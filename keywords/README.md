# Keywords

Quarterly loop (CLAUDE.md §8): generate candidates → owner gets search volumes from Google Keyword Planner → we score and pick the first cluster.

## This round: `2026-10/`

- `candidates-all.csv`: every candidate with its topic, page type, indicator, place, data source and `data_status` (`ready` = we have the data and the licence; `licence_check` = data exists but the source still needs a licence record).
- `planner-upload-01.txt`, `planner-upload-02.txt`: the same keywords, one per line, at most 700 per file. **These are the files to upload.**

Regenerate with `python keywords/generate_candidates.py 2026-10`.

## Owner steps (about 15 minutes)

1. Go to **ads.google.com** → Tools → Planning → **Keyword Planner**. (A free Google Ads account is enough; you can skip creating a campaign. Without ad spend, volumes show as ranges like "1K–10K". That's fine.)
2. Choose **"Get search volume and forecasts"**.
3. Click **"Upload a file"** and choose `planner-upload-01.txt`.
4. Before submitting, set:
   - **Location:** India
   - **Language:** English
   - **Search network:** Google
   - **Date range:** last 12 months
5. Open the **"Historical metrics"** tab (not Forecasts) → **Download keyword ideas** → **CSV**.
6. Repeat steps 2–5 for `planner-upload-02.txt`.
7. Save both downloads in `keywords/2026-10/planner-export/` (any file names). If you're unsure where, just tell me where you saved them.

If Planner rejects a file or shows fewer keywords than uploaded, tell me the number it accepted and I'll split the files smaller.

## What happens next

We import the exports, score `priority = demand × winnability × data quality` (winnability from checking who ranks on page one, plus the boosts and penalties in CLAUDE.md §8), group by topic, and propose the first cluster of 50–100 pages for approval.
