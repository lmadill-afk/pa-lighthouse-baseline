# Lighthouse Baseline Tracker

Weekly-sampled, monthly-reported Lighthouse + CrUX baseline for three primaryarms.com pages, collected by GitHub Actions from the PageSpeed Insights API.

## In this repo
| path | purpose |
|---|---|
| `.github/workflows/psi-weekly.yml` | Cron Mondays 14:00 UTC. Also runnable manually. |
| `scripts/psi_collect.py` | Fetches PSI, appends raw CSV, rebuilds monthly medians, injects raw CSV into `dashboard.html`. |
| `data/lighthouse_raw.csv` | Every run. Append-only. |
| `data/lighthouse_monthly.csv` | Median per page × device × month (pools ~12 weekly runs). |
| `data/SCHEMA.md` | Column definitions. |
| `TRACKER_CONFIG.md` | Pages, cadence, thresholds, known-changes log, new-site URL map. Edit this, not the script. |
| `dashboard.html` | Self-contained dashboard with weekly/monthly toggle, regenerated every run. Open in a browser or serve via GitHub Pages. |

## In the Claude Project (not the repo)
- `PROJECT_RULES.md` → custom instructions. Commands: `Status`, `Monthly`, `Dashboard`, `Trend`, `Check`.
- `CHROME_SHORTCUT_PROMPT.md` → fallback manual collector, only if the Action fails.

## Setup
1. Repo secret `PSI_API_KEY` (PageSpeed Insights API key, API-restricted).
2. Settings → Actions → General → Workflow permissions → Read and write.
3. Actions → Run workflow once to seed the baseline.
