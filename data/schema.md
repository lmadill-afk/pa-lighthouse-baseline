CSV schemas
lighthouse_raw.csv — one row per run
column	type	notes
run_date	YYYY-MM-DD	
run_month	YYYY-MM	derived from run_date
run_index	1–3	which of the month's runs
page_key	home / category / product	
url	string	must match TRACKER_CONFIG.md
device	mobile / desktop	
source	psi_ui / psi_api	never devtools
site_version	v1 / v2	v2 after new site launch
performance, accessibility, best_practices, seo	int 0–100	lab scores
fcp_s, lcp_s, speed_index_s	float, seconds	lab
tbt_ms	int, ms	lab
cls	float	lab
field_scope	url / origin / none	which CrUX dataset PSI showed
field_cwv_status	pass / fail / blank	CrUX assessment
field_lcp_ms, field_inp_ms	int, ms	CrUX p75
field_cls	float	CrUX p75
lighthouse_version, chrome_version	string	as shown in report
notes	string, no commas	product_unavailable / psi_error / wrong_page / free text
lighthouse_monthly.csv — one row per page × device × month
Same columns minus run_index, lighthouse_version, chrome_version; plus `runs` (count of raw rows aggregated). All numeric lab columns are the median of that month's raw rows. Field columns carry the first non-empty raw value.
