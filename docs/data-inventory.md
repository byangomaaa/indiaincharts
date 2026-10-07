# Data inventory — MoSPI eSankhyiki (Phase 0)

**Snapshot:** 2026-10-07, via the MoSPI MCP server (`mcp.mospi.gov.in`, "MoSPI Data Server" v2.3.0).
**Coverage:** 27 datasets, 786 indicator/metadata combinations, 0 errors.
**Per-indicator detail:** [`data-inventory-indicators.csv`](data-inventory-indicators.csv) (one row per indicator: query params, number of state options, year range, breakdowns).
**Raw snapshot:** `data/raw/discovery/mospi-mcp/2026-10-07.tar.gz` (local, git-ignored; to move to R2 in Phase 1).
**Regenerate:** `pipeline/discovery/` scripts (see each file's header).
**Licence:** usable with credit (owner decision 2026-10-07) — see [`licences/mospi.md`](licences/mospi.md).

> Year ranges below show the **first calendar year** of each period label (e.g. `2023-24` → 2023). "States" is the number of geography options the API offers, which usually includes All-India and old/new UT variants (e.g. Daman & Diu, and DNH & DD after the merger).

---

## 1. Headline findings

1. **District-level data is almost absent from the API.** Only the Economic Census (EC) is district-wise, and it's old (EC6 = 2013-14, EC5 = 2005, EC4 = 1998). EC also returns only **top/bottom N districts per state** ("ranking" mode) or 20 raw rows per page ("detail" mode). **District profile pages (CLAUDE.md §6.1) will need other sources:** NFHS-5 district factsheets, UDISE+ district reports, Census 2011, NDAP. All of these need licence checks first. → **The first cluster should be state-level.**
2. **State-level coverage is strong.** PLFS, CPI (group level), NAS state GSDP/NSDP, UDISE+, NFHS, AISHE, HCES, MNRE, ASUSE, the NSS rounds, GENDER and ENVSTATS all have state breakdowns.
3. **Long time series exist for the release-driven datasets:** CPI and WPI (monthly), IIP, NAS (annual/quarterly), PLFS (annual/quarterly/monthly), RBI (from 1950), MNRE (monthly since 2020) and UDISE+ (7 years).
4. **Most surveys are one-off or two-point.** NFHS has two rounds (NFHS-4 and NFHS-5); HCES, TUS and the NSS rounds have one or two. These fail the "≥ 3 periods for trends" gate, so they suit **ranking/comparison pages** (≥ 5 states), not trend pages.
5. **Base-year breaks are everywhere** (confirmed in the API):

   | Dataset | Base years offered | Latest series |
   |---|---|---|
   | CPI | 2024, 2012, 2010 | **2024** (data from 2025) |
   | NAS (GDP) | 2022-23, 2011-12 (+ Back series) | **2022-23** |
   | WPI | 2022-23, 2011-12, 2004-05, 1993-94 | **2022-23** (data from 2023) |
   | IIP | 2022-23, 2011-12, 2004-05, 1993-94 | **2022-23** |
   | ISP (services) | 2024-25 | new index |
   | CPI-AL/RL | 2019, 1986-87 | **2019** |

   → The data model **must** carry `series_id` / `base_year`, and charts must never join two series without a visible break marker. (This confirms the open item in `decisions.md`.)
6. **Every dataset uses its own geography codes.** CPI: 1 = All India, alphabetical. PLFS/NFHS: 99 = All India. UDISE+: its own ids. NAS: 01–37 with 37 = All India. EC: **Census 2011 codes**. Spellings also differ ("Andaman & N. Islands", "Puduchery", "Nct Of Delhi"). → The LGD alias table plus a Census-2011 crosswalk is a **Phase 1 prerequisite**, and unmatched names must fail the build.
7. **Breakdowns are rich.** Examples: sex, rural/urban, age group, education, **religion, social group/caste**, quintile, industry (NIC), management type. → The data model needs a **breakdown dimension** (confirms the open item). Religion and caste breakdowns fall under the **sensitive topics** rules (§12): neutral wording, context, and checking ad policy.
8. **API quirks to code around:**
   - Values come back as **strings** with a separate `unit` field.
   - Results are paginated (`limit`/`page`).
   - Filter codes are arbitrary per dataset, so they must come from metadata and must never be guessed.
   - NSS78 needs the **full indicator name** (short labels cause upstream 500 errors).
   - NSS77 has two modules with overlapping codes (`module` param).
   - ASI needs `classification_year` (NIC version, not the data year).
   - PLFS `frequency_code` selects the indicator set; `year_type` is Calendar vs Agricultural year.
   - The MCP server smooths over some of these. **The production pipeline calls `api.mospi.gov.in` directly**, so each of these needs handling and a test.
9. **Projections are mixed in.** GENDER goes to 2036 and ENVSTATS to 2050. Pages must label projected values as projections and never present them as observed (§12).
10. **Release calendar:** MoSPI publishes an Advance Release Calendar (2026-27 edition: `mospi.gov.in/uploads/documents/releaseCalender/…ARC 2026-27…pdf`). → Seed the `release_calendar` table from it in Phase 1.
11. **Trade alternative:** the MoSPI `RBI` dataset has trade by country and commodity (USD/INR), BoP, forex reserves and exchange rates. That complements DGCI&S data for trade pages (see `licences/dgcis.md`).

---

## 2. Dataset summary

| Dataset | What it is | Indicators | Geography | Periods (first yr) | Frequency | Key breakdowns | Page-type fit |
|---|---|---|---|---|---|---|---|
| **PLFS** | Labour force: LFPR, WPR, unemployment, wages | 8 (annual), 3 (qtr/monthly) | 39 state options | 2017–2025 | Annual (CY & agri-yr), quarterly, monthly | sex, rural/urban, age, education, religion, social group, weekly status | ⭐ metric, ranking, trend, release |
| **CPI** | Retail inflation | Group & Item levels | 37 (group level); All-India (item) | 2011–2026 | Monthly | rural/urban/combined, group, item | ⭐ release, trend, ranking, **inflation calculator** |
| **IIP** | Industrial production | category / sub-category | All-India | 2012–2026 | Monthly, annual | use-based & sectoral categories | release, trend |
| **ISP** | Services production index (new) | 19 sub-sectors | All-India | 2025–2026 | Monthly, yearly | sub-sector, NIC 2-digit | release (short history) |
| **WPI** | Wholesale inflation | 5-level commodity tree | All-India | 2012–2026 | Monthly | major group → item | release, trend |
| **NAS** | GDP/GVA, consumption, capital formation; **state GSDP/NSDP/per-capita** | 22 national + 12 state (codes 23–34) | All-India; states via `state_code` 01–37 | 1999–2025 | Annual, quarterly | industry, revision, approach, institutional sector | ⭐ release (GDP), state ranking & comparison (GSDP, per-capita income) |
| **ASI** | Factory sector (57 indicators) | 57 | 39 | 2008–2023 | Annual | NIC 2/3/4-digit | ranking, trend |
| **ASUSE** | Informal enterprises | 35 annual + 15 quarterly | up to 39 (21 of 50 have states) | 2021–2026 | Annual, quarterly | rural/urban, establishment type, activity, sex | ranking |
| **EC** | Economic Census: establishments, workers | 3 (EC6/EC5/EC4) | **District** (top/bottom N per state) | 1998, 2005, 2013-14 | One-off | activity, ownership, finance, rural/urban | district facts (old; label the year clearly) |
| **ENERGY** | Energy balance (KToE, PJ) | 2 | All-India | 2012–2023 | Annual | commodity, end-use sector | trend, hub |
| **MNRE** | Installed renewable capacity (MW) | 5 (solar, wind, hydro, bio, total) | 40 state options | 2020–2026 | **Monthly** | solar/bio sub-types | ⭐ state ranking, trend, release |
| **AISHE** | Higher education | 9 | 37 | 2017–2021 | Annual | sex, social group, institution type | ranking, trend |
| **UDISE** | School education | 46 | 38 | 2018–2024 | Annual | level, sex, management, social group, infrastructure | ⭐ state ranking, trend (7 yrs) |
| **NFHS** | Health & demographics | 21 (each with many sub-indicators) | 39 | NFHS-4, NFHS-5 | Two rounds | sub-indicator, rural/urban | ⭐ ranking, 2-point comparison |
| **HCES** | Consumption expenditure (MPCE), Gini | 9 | 37 | 2022–2023 | Survey | rural/urban, fractile, social group | ranking |
| **TUS** | Time use | 41 | All-India only (per metadata) | 2019, 2024 | Survey | sex, rural/urban, activity, age, social group | hub/insight pages, gender gaps |
| **GENDER** | Women & Men in India (154 indicators) | 154 | 92 of 154 have states | 1951–2036 (incl. projections) | Mixed | sex, rural/urban, age, education | many metric/ranking pages; ⚠ crime heads = sensitive |
| **ENVSTATS** | Environment (124 indicators) | 126 | 111 of 126 have state/area options | 1905–2050 (incl. projections) | Mixed | sub-indicator, area, river, city | ranking, hub |
| **RBI** | External sector: trade, BoP, debt, forex, FX rates | 39 | All-India | 1950–2025 | Monthly, quarterly, annual | country, commodity, currency | trade pages, tools (exchange-rate history) |
| **CPIALRL** | CPI for agricultural/rural labourers | 2 | 35 | 1999–2026 | Monthly | group | release, state ranking |
| **NSS73** | Unincorporated non-agri enterprises (2015-16) | 6 | 37 | one round | Survey | rural/urban, activity, enterprise type | ranking |
| **NSS75E** | Education (2017-18) | 13 | 23 | one round | Survey | sex, rural/urban, level | ranking |
| **NSS76** | Disability; housing & drinking water (2018) | 25 | 37–39 | one round | Survey | sex, rural/urban, quintile | ranking (disability = sensitive care) |
| **NSS77** | Agricultural households, land & livestock; AIDIS debt | 55 | 31–37 | one round | Survey | season, land class, caste, asset class | ranking |
| **NSS78** | Living conditions: water, sanitation, digital, migration | 14 | 39 (via params) | one round | Survey | sex, rural/urban, age | ranking |
| **NSS79** | CAMS (literacy, NEET youth, health spend, finance) + AYUSH | 35 | 37 | one round | Survey | sex, rural/urban, age | ranking |
| **NSS80** | Telecom (CMST) + Education (CMSE) | 38 | 37 | one round | Survey | sex, rural/urban, age, school type | ⭐ ranking (internet/mobile use by state is high-interest) |

---

## 3. Implications for the plan

**For the first cluster (keyword work next):** start where coverage, freshness and search demand overlap:
- **Labour (PLFS):** unemployment / LFPR / WPR by state, sex, rural/urban and youth, plus quarterly and monthly releases.
- **Prices (CPI):** monthly inflation release pages, state inflation rankings, the **inflation calculator** tool (a link magnet).
- **State economy (NAS):** GSDP, per-capita income ranking and comparisons, GDP release pages.
- **School education (UDISE+):** enrolment, teachers, PTR, infrastructure by state (7-year trends).
- **Renewables (MNRE):** monthly solar/wind capacity by state rankings.

**For the data model (decisions.md open items, now confirmed):** add `breakdown` dimensions, `series_id`/`base_year`, unit + scale (values are strings), dataset-specific geo alias tables → LGD, a Census-2011 crosswalk for EC, and a `projection` flag.

**For the pipeline:** one adapter per dataset, built from the Swagger specs in `github.com/nso-india/esankhyiki-mcp/swagger/` (28 YAML files, including `nss77_aidis`). Use contract tests on each adapter, because the quirks in §1.8 are where scrapers and adapters break.

**For district pages:** add a Phase 0/1 task to licence-check and inventory **NFHS-5 district factsheets, UDISE+ district data, Census 2011 (PCA) and NDAP**. Until then there are no district pages except old EC facts.

---

## 4. Not yet checked

- Actual row counts and value completeness per indicator. Metadata lists the options, but not every combination has data. To be measured when the Phase 1 adapters fetch data.
- Standard errors and sample sizes: none seen in the metadata. Check publication annexes for the surveys we use (§12).
- data.gov.in, NDAP, PPAC and RBI DBIE inventories (only MoSPI is covered here).
