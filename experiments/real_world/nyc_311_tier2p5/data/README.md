# Data notes

This demo includes a small `sample_311.csv` so the scripts run without downloads.

For real runs, place your exported CSV at:

`data/raw/nyc_311.csv`

Expected columns (minimum):
- `created_date` (timestamp)
- `closed_date` (timestamp; may be empty)
- `agency` (string)
- `complaint_type` (string)

Extra columns are allowed and ignored.

