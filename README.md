# Lighthouse Baseline Tracker — package contents

| file | purpose |
|---|---|
| `PROJECT_RULES.md` | Paste into the Claude Project's custom instructions. Evergreen. |
| `TRACKER_CONFIG.md` | Monthly-editable: URLs, cadence, thresholds, known-changes log, new-site URL map. Upload to Project knowledge; re-upload when edited. |
| `CHROME_SHORTCUT_PROMPT.md` | Save as a Claude in Chrome shortcut (`/lighthouse-monthly`) and schedule monthly. Manual collection path. |
| `scripts/psi_collect.py` + `.github/workflows/psi-monthly.yml` | Automated collection path via PageSpeed Insights API. Drop into a private repo (pattern matches `pa-search-snapshots`). Needs a `PSI_API_KEY` repo secret. |
| `data/lighthouse_raw.csv` | Every run. Append-only. |
| `data/lighthouse_monthly.csv` | Median per page × device × month. Dashboard source. |
| `data/SCHEMA.md` | Column definitions. |
| `dashboard.html` | Self-contained. Paste `lighthouse_monthly.csv` into the `csv-data` block, or use the Load CSV button. |

## Monthly loop (Chrome path)
1. Shortcut fires → paste its CSV block into the Project.
2. Project validates, appends raw, rebuilds monthly, refreshes dashboard, writes 5-line summary.
3. Re-upload the two CSVs and dashboard to Project knowledge (replace old versions).

## Monthly loop (API path)
1. Action runs on the 1st and commits both CSVs.
2. Paste `lighthouse_monthly.csv` into the Project (or connect the repo) for the summary + dashboard refresh.
