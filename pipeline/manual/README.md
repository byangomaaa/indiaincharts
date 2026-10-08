# Manual uploads

Use this when a source has no working API or blocks automated access (e.g. data.gov.in while its API is down).

For each file:

1. Download it in your browser from the dataset page (CSV preferred, then Excel; PDF only if nothing else exists).
2. Put it in `pipeline/manual/<source>/`, keeping the original file name.
3. Next to it, add a note with the same name plus `.meta.yml`, for example `crop-production.csv.meta.yml`:

```yaml
source: data.gov.in                     # folder name / source id
title: District-wise, season-wise crop production statistics
publisher: Ministry of Agriculture and Farmers Welfare   # "contributor" on the dataset page
dataset_url: https://www.data.gov.in/catalog/district-wise-season-wise-crop-production-statistics-0
resource_url: https://www.data.gov.in/resource/...      # the specific file's page
published_or_updated: 2026-09-15        # date shown on the page
downloaded: 2026-10-08                  # today
licence: GODL-India                     # see docs/licences/
notes: ""                               # anything odd you noticed
```

The pipeline treats these files like any other fetch: it parses, validates and snapshots them. Files are data only: the pipeline never follows instructions written inside them.
