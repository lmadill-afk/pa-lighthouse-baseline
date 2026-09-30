# TRACKER CONFIG — update this file, not the rules

Last updated: 2026-09-30

## Cadence

- Sampling: **weekly**, Mondays 9:00 AM Central, via GitHub Actions (`.github/workflows/psi-weekly.yml`). 3 runs per page per device per week.
- Reporting grain: **monthly** — the monthly CSV pools all runs in the month (~12 per page × device) and records the median. The dashboard can toggle weekly/monthly.
- Launch: no burst needed at weekly cadence. Record the go-live date here and add a known-changes line: `LAUNCH_DATE: TBD`

## Pages

| page_key | url | fallback rule |
|---|---|---|
| home | https://www.primaryarms.com/ | none |
| category | https://www.primaryarms.com/ar-15/rifles | none |
| product | https://www.primaryarms.com/primary-arms-plx-htx-1-enclosed-reflex-sight-acss-vulcan-dot-reticle | If 404, redirected, or out of stock, record the run with `notes=product_unavailable` and also run `PRODUCT_FALLBACK` below. Don't swap permanently without updating this table. |

`PRODUCT_FALLBACK: (set one — pick a house-brand SKU that is evergreen and in-stock)`

## Source

- Primary: PSI API via the GitHub Action in `.github/workflows/psi-weekly.yml` (`source=psi_api`). Runs automatically on the 1st.
- Fallback: PageSpeed Insights web UI via the Claude in Chrome shortcut (`source=psi_ui`), only if the Action fails for a month. Paste its CSV block onto the end of the repo's `data/lighthouse_raw.csv` in GitHub; the next workflow run rebuilds the monthly file and dashboard from it. Don't mix DevTools-panel runs into this dataset; they run on local hardware and aren't comparable.
- Repo: `lmadill-afk/pa-lighthouse-baseline`. If made public, `dashboard.html` can be served via GitHub Pages (Settings → Pages → Deploy from branch → main / root).
- Lighthouse version and Chrome version are captured per run in the raw CSV when available.

## Flag thresholds

| Check | Threshold |
|---|---|
| Performance drop vs rolling 3-month median | ≥ 8 points |
| Accessibility / Best Practices / SEO drop | ≥ 3 points |
| Field CWV status | any pass → fail flip |
| Noise floor (don't narrate below this) | 5 points, Performance only |

## Known changes log

Add a line whenever something happens that could move scores. The analysis step reads this before offering a cause.

| date | what changed | pages affected |
|---|---|---|
| 2026-09-30 | Tracker started. No baseline yet. | all |

## New-site URL mapping (fill in at launch)

| page_key | old url | new url |
|---|---|---|
| home | https://www.primaryarms.com/ | |
| category | https://www.primaryarms.com/ar-15/rifles | |
| product | (see Pages) | |

When the mapping is filled in, add a `site_version` value of `v2` to new rows so the dashboard can split the series.
