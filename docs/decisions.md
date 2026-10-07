# Decisions log

Newest first. Each entry: date, decision, reason, status. Owner approval required for anything marked **pending**.

---

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
