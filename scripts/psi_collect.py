#!/usr/bin/env python3
"""Pull Lighthouse + CrUX data from the PageSpeed Insights API and append to the raw CSV.

Same Lighthouse engine PSI's web UI uses, same Google-hosted hardware, no browser session needed.
Usage: PSI_API_KEY=... python scripts/psi_collect.py [--runs 3] [--site-version v1]
Runs weekly; rows carry run_week (ISO, YYYY-Www) and run_month. Monthly medians pool all runs in the month.
Keyless calls work but are rate-limited; get a free key at console.cloud.google.com (PageSpeed Insights API).
"""
import argparse, csv, datetime as dt, json, os, statistics, sys, time, urllib.parse, urllib.request

PAGES = {
    "home": "https://www.primaryarms.com/",
    "category": "https://www.primaryarms.com/ar-15/rifles",
    "product": "https://www.primaryarms.com/primary-arms-plx-htx-1-enclosed-reflex-sight-acss-vulcan-dot-reticle",
}
RAW = os.path.join("data", "lighthouse_raw.csv")
MONTHLY = os.path.join("data", "lighthouse_monthly.csv")
API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
CATS = ["performance", "accessibility", "best-practices", "seo"]
LAB = {"fcp_s": ("first-contentful-paint", 1000), "lcp_s": ("largest-contentful-paint", 1000),
       "tbt_ms": ("total-blocking-time", 1), "cls": ("cumulative-layout-shift", 1),
       "speed_index_s": ("speed-index", 1000)}
MED_COLS = ["performance", "accessibility", "best_practices", "seo", "fcp_s", "lcp_s", "tbt_ms", "cls", "speed_index_s"]


def iso_week(d):
    y, w, _ = dt.date.fromisoformat(d).isocalendar()
    return f"{y}-W{w:02d}"


def ensure_columns(path):
    """Migrate a raw CSV written before run_week existed: add the column, backfill from run_date."""
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    if not rows or "run_week" in rows[0]:
        return
    hdr = rows[0]
    i = hdr.index("run_date") + 1
    hdr.insert(i, "run_week")
    for r in rows[1:]:
        r.insert(i, iso_week(r[0]) if r and r[0] else "")
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    print("migrated raw CSV: added run_week")


def fetch(url, strategy, key):
    q = [("url", url), ("strategy", strategy)] + [("category", c) for c in CATS]
    if key:
        q.append(("key", key))
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(q), headers={"User-Agent": "pa-lighthouse-tracker"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 3:
                wait = 30 * (attempt + 1)
                print(f"    {e.code} on attempt {attempt + 1}, retrying in {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            raise


def field_block(data):
    exp = data.get("loadingExperience") or {}
    scope, src = "none", exp
    if exp.get("metrics"):
        scope = "url"
    elif (data.get("originLoadingExperience") or {}).get("metrics"):
        scope, src = "origin", data["originLoadingExperience"]
    m = src.get("metrics", {})
    cat = src.get("overall_category")
    status = {"FAST": "pass", "AVERAGE": "fail", "SLOW": "fail"}.get(cat, "") if scope != "none" else ""
    p = lambda k, d=1: (m.get(k, {}).get("percentile") / d) if m.get(k) else ""
    return scope, status, p("LARGEST_CONTENTFUL_PAINT_MS"), p("INTERACTION_TO_NEXT_PAINT"), p("CUMULATIVE_LAYOUT_SHIFT_SCORE", 100)


def row_from(data, page_key, url, device, run_index, today, site_version):
    lh = data["lighthouseResult"]
    cats, audits = lh["categories"], lh["audits"]
    score = lambda c: round(cats[c]["score"] * 100) if cats.get(c, {}).get("score") is not None else ""
    lab = {k: round(audits[a]["numericValue"] / d, 3) if audits.get(a, {}).get("numericValue") is not None else "" for k, (a, d) in LAB.items()}
    scope, status, flcp, finp, fcls = field_block(data)
    notes = ""
    final = lh.get("finalUrl", "")
    if final.rstrip("/") != url.rstrip("/"):
        notes = "wrong_page redirected_to " + final.replace(",", " ")
    return {
        "run_date": today, "run_week": iso_week(today), "run_month": today[:7], "run_index": run_index, "page_key": page_key, "url": url,
        "device": device, "source": "psi_api", "site_version": site_version,
        "performance": score("performance"), "accessibility": score("accessibility"),
        "best_practices": score("best-practices"), "seo": score("seo"), **lab,
        "field_scope": scope, "field_cwv_status": status, "field_lcp_ms": flcp, "field_inp_ms": finp, "field_cls": fcls,
        "lighthouse_version": lh.get("lighthouseVersion", ""),
        "chrome_version": (lh.get("environment") or {}).get("hostUserAgent", "").split("Chrome/")[-1].split(" ")[0],
        "notes": notes,
    }


def append(path, rows):
    with open(path, newline="") as f:
        header = next(csv.reader(f))
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        for r in rows:
            w.writerow({k: r.get(k, "") for k in header})


def rebuild_monthly():
    with open(RAW, newline="") as f:
        raw = list(csv.DictReader(f))
    with open(MONTHLY, newline="") as f:
        header = next(csv.reader(f))
    groups = {}
    for r in raw:
        groups.setdefault((r["run_month"], r["page_key"], r["device"]), []).append(r)
    out = []
    for (month, page, device), rows in sorted(groups.items()):
        good = [r for r in rows if r["performance"] != ""]
        if not good:
            good = rows
        m = {"run_month": month, "run_date": max(r["run_date"] for r in rows), "page_key": page,
             "url": rows[0]["url"], "device": device, "source": rows[0]["source"],
             "site_version": rows[0]["site_version"], "runs": len(good)}
        for c in MED_COLS:
            vals = [float(r[c]) for r in good if r[c] not in ("", None)]
            m[c] = round(statistics.median(vals), 3) if vals else ""
            if c in MED_COLS[:4] and m[c] != "":
                m[c] = int(m[c])
        for c in ["field_scope", "field_cwv_status", "field_lcp_ms", "field_inp_ms", "field_cls"]:
            m[c] = next((r[c] for r in rows if r[c]), "")
        m["notes"] = " | ".join(sorted({r["notes"] for r in rows if r["notes"]}))
        out.append(m)
    with open(MONTHLY, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for m in out:
            w.writerow({k: m.get(k, "") for k in header})


def rebuild_dashboard():
    """Inject the monthly CSV into dashboard.html so the repo always holds a current dashboard."""
    path = "dashboard.html"
    if not os.path.exists(path):
        return
    html = open(path, encoding="utf-8").read()
    start_tag = '<script id="csv-data" type="text/csv">'
    a = html.find(start_tag)
    b = html.find("</script>", a)
    if a < 0 or b < 0:
        print("dashboard.html has no csv-data block; skipped", file=sys.stderr)
        return
    csv_text = open(RAW, encoding="utf-8").read().strip()
    html = html[: a + len(start_tag)] + "\n" + csv_text + "\n" + html[b:]
    open(path, "w", encoding="utf-8").write(html)
    print("dashboard.html rebuilt")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--site-version", default="v1")
    a = ap.parse_args()
    key = os.environ.get("PSI_API_KEY", "").strip()
    if not key:
        sys.exit("PSI_API_KEY is empty. Add it as a repo secret (Settings > Secrets and variables > Actions) with that exact name.")
    print(f"using API key ending in ...{key[-4:]}")
    today = dt.date.today().isoformat()
    ensure_columns(RAW)
    rows = []
    for i in range(1, a.runs + 1):
        for page_key, url in PAGES.items():
            for device in ("mobile", "desktop"):
                try:
                    data = fetch(url, device, key)
                    rows.append(row_from(data, page_key, url, device, i, today, a.site_version))
                    print(f"ok  run{i} {page_key} {device} perf={rows[-1]['performance']}")
                except Exception as e:  # noqa: BLE001
                    print(f"ERR run{i} {page_key} {device}: {e}", file=sys.stderr)
                    rows.append({"run_date": today, "run_week": iso_week(today), "run_month": today[:7], "run_index": i, "page_key": page_key,
                                 "url": url, "device": device, "source": "psi_api", "site_version": a.site_version,
                                 "notes": "psi_error " + str(e).replace(",", " ")[:80]})
                time.sleep(5)
    append(RAW, rows)
    rebuild_monthly()
    rebuild_dashboard()
    print(f"appended {len(rows)} rows; monthly rebuilt")


if __name__ == "__main__":
    main()
