# Costs and free-tier usage

**Target:** domain registration only. Every other service on a free tier.
**Rule:** any spend needs owner approval. Log it in `docs/decisions.md`.

Limits last checked: **2026-10-07** (re-check quarterly; providers change them).

## Recurring costs

| Item | Cost | Notes |
|---|---|---|
| `indiaincharts.com` | ~₹900–1,200/yr (estimate) | Cloudflare Registrar sells .com at cost |
| `indiaincharts.in` | ~₹600–1,000/yr (estimate) | Cloudflare Registrar may not support .in; use another registrar, point DNS to Cloudflare |

## Free tiers in use

| Service | Free allowance | What could exceed it | Current usage |
|---|---|---|---|
| Cloudflare Pages | Unlimited bandwidth; 500 builds/month; **20,000 files per deployment**; 25 MiB per file | File count as pages grow | — |
| Cloudflare R2 | 10 GB storage; 1M Class A (write) + 10M Class B (read) ops/month; zero egress | Raw snapshots accumulating; uncached image reads | — |
| Cloudflare Workers (only if option C) | 100,000 requests/day; 10 ms CPU/request | Traffic spikes without caching | not used |
| Cloudflare Access | Up to 50 users | — | — |
| Cloudflare Web Analytics, Email Routing, Bulk Redirects | Free | — | — |
| GitHub Actions | Public repo: unlimited. Private: 2,000 min/month, 500 MB artifacts | Full rebuilds, infographic rendering | — |
| Google Search Console, Bing Webmaster Tools, Keyword Planner | Free | — | — |
| AdSense consent tool (EEA/UK) | Free (Google's own CMP) | — | — |
| Pagefind, Dependabot, secret scanning | Free | — | — |
| Off-platform backup | Google Drive 15 GB / external disk | Snapshot growth | — |

## Risks to the zero-cost target

- **R2 needs a payment card on file**, and there is no hard spending cap. Set Cloudflare usage notifications; check the R2 dashboard monthly.
- **Snapshot growth:** store a raw snapshot only when the content hash changes; compress (zstd/gzip); archive old snapshots to the offline backup.
- **Infographic rendering time:** regenerate only when the page's data hash changes.
- **No LLM API calls in the pipeline** (see decisions, 2026-10-07).

## Paid-upgrade trigger

Consider **Workers Paid ($5/month)** only when:
- deploy file count > ~15,000, or
- Worker requests > ~100,000/day.

Otherwise, stay free.

## Monthly usage log

| Month | Pages files | R2 storage | R2 Class A / B | Actions minutes | Notes |
|---|---|---|---|---|---|
| 2026-10 | 0 | 0 | 0 / 0 | 0 | Phase 0, no deployments |
