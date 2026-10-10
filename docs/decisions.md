# Decisions log

Newest first. Each entry: date, decision, reason, status. Owner approval required for anything marked **pending**.

---

## 2026-10-10 — Data storage: start without R2? (pending owner)

**Proposal:** Phase 1 runs without R2. Processed data (small, e.g. state GDP = 1,740 rows ≈ 100 KB) lives in the repo as compressed CSV/Parquet; raw snapshots are attached to dated GitHub Releases (free, public like the data itself); infographics and CSV downloads ship inside the Pages build. Move images/CSVs to R2 behind Cloudflare cache when the deploy approaches the file limit (see hosting decision, 2026-10-07).

**Reason:** zero cost, no payment card, no usage limits to watch at our current size. R2 free tier estimates (if used): pipeline writes ≈ 1–10k/month of 1M; storage ≈ 3 GB in year one of 10 GB; visitor reads are the only real risk and are avoided by serving R2 through Cloudflare's cache on our own domain.

**Alternative:** set up R2 from the start, as CLAUDE.md §4 currently assumes.

**Immediate need either way:** raw snapshots exist only on the owner's Mac (`data/raw/`, git-ignored). Give them a backed-up home.

**Status:** pending owner. If accepted, update CLAUDE.md §4 (Storage, Infographics) to match.

## 2026-10-10 — Visuals: interactive charts and videos (proposed)

**Proposal:**
- Single-metric pages: static SVG charts built at build time (fast, crawlable), plus at most one small interactive chart.
- Ranking/topic pages (e.g. "State-wise GDP of India"): showcase interactive charts ported from the owner's Claude dashboard "India state GDP" (bar race, heatmap, income-vs-growth scatter, indexed trend). d3 modules only (~25 KB), lazy-loaded on scroll, with a static fallback in the HTML.
- Phase 2: Remotion videos (bar race first) for YouTube Shorts / Reels / LinkedIn / X, rendered on GitHub Actions (not Remotion Lambda), posted natively; only thumbnails on the site.

**Cost:** ₹0. Remotion is free for individuals and companies up to 3 people (paid from 4+; licence changes expected in Remotion 5.0 — re-check then). Real costs are build time (~2–3 days per chart set or video style) and owner review per video.

**Status:** proposed — owner to confirm.

## 2026-10-10 — Prototype page template "GDP of {state}" (under review)

**What:** `site/prototype/build_gsdp_page.py` generates the single-metric page for any state from MoSPI NAS state data, following §6.2 (direct answer, metric cards, infographic, SVG trend + ranking charts, sortable table, computed summary with number-match check, source & method, related questions, JSON-LD, reserved ad slots, light/dark + toggle). Published for review as a private artifact: https://claude.ai/artifact/UVyyL1s643NpJhCAsF9rQF

**Open question:** desktop side space — option 1 (right sidebar: "On this page" menu, sticky 300×600 ad, related links) recommended; alternatives: wider charts, both, or leave narrow.

**Status:** pending owner feedback.

## 2026-10-09 — First cluster: state economy (pending owner)

**Proposal:** ~80 pages — 36 × "GDP of {state}", 36 × "per capita income of {state}", ~5 rankings (richest state, state-wise GDP, highest/lowest per-capita income, state-wise per-capita income), ~4 comparisons with demand — plus the inflation calculator tool.

**Reason:** strongest demand that is both data-ready and licensed (5K–50K searches/month per big state; rankings up to 50K); page one is mostly news, PDFs, paywalled and thin sites (winnable); StatisticsTimes is the main direct competitor. Population/literacy have more demand but need current figures (MoSPI projections / NSS) — candidate second cluster.

**Status:** pending owner.

## 2026-10-09 — Data findings to design around

- **State GSDP is only on the 2011-12 base.** National GDP moved to 2022-23; state series on the new base are not yet published. Pages must say so and never mix the two.
- **Haryana is missing** from MoSPI's state series (30 states/UTs report). A Haryana page needs another source; "combined" totals and shares must say they cover reporting states only.
- **Latest year is partial:** 2025-26 has 15 of 30 states. Ranks use the latest complete year (2024-25).
- **MoSPI API paging:** `limit` above ~100 returns HTTP 400; page through results.
- **data.gov.in API down** (connection refused from local and GitHub Actions, 2026-10-08/09); website blocks bots. Manual downloads until it returns; the `datagovindia` wrapper uses the same API.
- **TradeStat source error** (India→USA exports 2023-24); trade series need jump and reconciliation checks.

**Status:** recorded.

## 2026-10-07 — MoSPI and DGCI&S data: usable with credit (owner decision)

**Decision:** The owner has assessed that MoSPI (eSankhyiki API) data and DGCI&S foreign-trade data may be used on the site, including in production, **provided every use is credited** (page, chart, infographic, embed, CSV). No launch gate on written permission. The earlier DGCI&S restriction (no full tables / CSV downloads) is lifted.

**Reason:** Owner's judgement. Research on 2026-10-07 found no explicit API licence for MoSPI (attribution-only guidance; older publications reserve reproduction "for sale") and a copyright reservation on DGCI&S sites; the owner accepts this residual risk.

**Mitigations kept:** full attribution on every surface; non-endorsement statement; no government names/logos/emblems in branding; aggregate data only; accuracy checks. The permission emails in `docs/licences/` remain available if the owner ever wants written confirmation. If a provider objects, we comply promptly and log it in the corrections log.

**Status:** accepted (owner, 2026-10-07).

## 2026-10-07 — First cluster is state-level; district pages need other sources

**Decision:** The first cluster targets state- and national-level pages. District pages are deferred until district sources (NFHS-5 district factsheets, UDISE+ district, Census 2011, NDAP) are licence-checked and inventoried.

**Reason:** The MoSPI API has almost no district data. Only the Economic Census has it (latest 2013-14), and only as top/bottom-N rankings per state. See `docs/data-inventory.md`.

**Status:** accepted (owner, 2026-10-07).

## 2026-10-07 — Hosting: HTML on Cloudflare Pages, images/CSVs on R2 (option B)

**Decision:** Page HTML is deployed to Cloudflare Pages. Infographic PNGs, CSV downloads and chart-data JSON are served from R2 under **versioned, immutable keys** (e.g. `/img/{page-id}/{data-hash}-1200x675.png`). Use a single shared embed page that loads chart data, not one embed HTML per chart.

**Reason:** Free plan caps a deployment at 20,000 files (paid: 100,000). Bundling everything (~5 files/page) caps us near 4,000 pages; moving assets to R2 raises that to roughly 8–10k pages. The quality gate should keep year-one indexable pages well under that.

**Escape hatch:** When the deploy approaches ~15,000 files, either (C) serve pages from R2 via a Worker (unlimited pages, more code, 100k requests/day free) or (D) Workers Paid at $5/month (100k files). URLs do not change either way.

**Status:** accepted.

## 2026-10-07 — Preview and `pages.dev` URLs locked down

**Decision:** All four:
1. Canonical tag on every page → `https://indiaincharts.com/...`
2. Bulk Redirect `indiaincharts.pages.dev/*` → `indiaincharts.com/*` (301)
3. Cloudflare Access (email one-time PIN) on all preview deployments
4. `X-Robots-Tag: noindex` on every host except `indiaincharts.com`

Plus a CI test that requests the `pages.dev` host and fails unless it redirects.

**Reason:** Preview and production `pages.dev` URLs are public by default. Risks: duplicate content splitting ranking signals, and unreviewed numbers being screenshotted and shared.

**Status:** accepted.

## 2026-10-07 — No LLM API calls in the pipeline

**Decision:** Summaries are generated deterministically from computed facts. Any wording polish happens in Claude Code sessions (owner's subscription) and is committed as a reviewed template change, never as a per-page API call at build time. The number-match test still applies.

**Reason:** Per-page API calls are a recurring cost that breaks the "domain only" target, and add non-determinism to builds.

**Status:** accepted.

## 2026-10-07 — Keyword priority favours queries Google can't answer in a box

**Decision:** In `priority = demand × winnability × data quality`, winnability gets a boost for: district-level queries, rankings, comparisons, multi-year time series, and tools. Headline single national numbers (already answered by Google or owned by news on release day) get a penalty.

**Reason:** New domain with no authority; zero-click answer boxes and news Top Stories capture headline queries. Tables, rankings and district data are where existing answers are weak.

**Status:** accepted.

## 2026-10-07 — Free-tier watch and first paid trigger

**Decision:** Track usage in `docs/costs.md`. The first paid item, if ever needed, is Workers Paid ($5/month), considered only when deploy file count > ~15,000 or Worker traffic > ~100k requests/day. Any spend still needs owner approval.

**Status:** accepted.

## 2026-10-07 — Repo visibility: public vs private

**Decision:** **public** code repository, hosted under the owner's separate project GitHub account (not the personal account).

**Reason:** Public repos get unlimited GitHub Actions minutes (private: 2,000/month). Code isn't secret; data licences permit redistribution with credit. Secrets stay in CI secrets either way. Caveats: DGCI&S trade data (no redistribution until permission) must never be committed to the repo; preview URLs in PR comments become visible (mitigated by Cloudflare Access).

**Status:** accepted (owner, 2026-10-07).

---

## Open items to decide later (not yet decisions)

- Data model additions: breakdown dimensions, series/base year, unit scale, Census-2011↔LGD crosswalk, sample size / SE fields.
- Number and date formatting conventions (lakh/crore, Indian digit grouping, FY `2024-25`, rounding).
- Tooling: uv + ruff + pytest (pipeline); pnpm + vitest + prettier (site); satori + resvg for infographics.
- Quality-gate thresholds per page type.
- Slim CLAUDE.md into rules + pointers to `docs/`.
