# Data inventory (Phase 0)

Part A: MoSPI eSankhyiki API · Part B: PPAC, TradeStat (DGCI&S), data.gov.in, NDAP

# Part A — MoSPI eSankhyiki

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
- RBI DBIE (not yet inventoried).

---

# Part B — Other sources (checked 2026-10-07)

## B1. PPAC (ppac.gov.in) ✅ strong state-level source

**Access:** each data page links to a current **Excel file** under `/uploads/page-images/` (file names change with each update), and some pages show HTML tables loaded by AJAX. Daily metro fuel prices come as a **PDF**. robots.txt: none (the URL returns a 404 page). The scraper finds the current file link on each page, downloads it, and validates the header layout before parsing.

| Dataset (file) | Geography | Periods | Frequency | Page ideas |
|---|---|---|---|---|
| State-wise sales/consumption of petroleum products — all products, MS (petrol), HSD (diesel), LPG and more, one sheet each (`Statewise_Sales-POL_Consumption_Final.xlsx`) | States/UTs + regional totals | **FY 2008-09 → 2025-26** (18 yrs) | Annual | ⭐ "petrol consumption by state", diesel/LPG rankings, per-capita (with population) |
| Retail outlets (petrol pumps) by state (`Statewise_Retail_Outlets.xls`) | States | 1 Apr 2012 → 1 Apr 2026 (15 yrs) | Annual | "number of petrol pumps in {state}", ranking |
| LPG distributors by state | States | 2001 → Aug 2026 (26 yrs) | Annual | ranking, trend |
| Active domestic LPG customers (lakh) | States | Latest snapshot (Aug 2026) | Monthly/quarterly update | "LPG connections in {state}" |
| PMUY (Ujjwala) connections | States | Latest snapshot (Aug 2026) | Periodic | Ujjwala by state ranking |
| VAT/sales tax on petrol, diesel, SKO, domestic LPG (`PP_3_SalesTax_*.xls`) | States/UTs | Current rates (posted 12 Aug 2026) | On change | ⭐ "VAT on petrol in {state}", "why petrol costs more in X" |
| Retail prices of petrol/diesel in 4 metros (PDF) | Delhi, Mumbai, Kolkata, Chennai | Daily since 16 Jun 2017 | Daily | ⭐ "petrol price today in Delhi" (high demand, hard SERP), price trend |
| Contribution of petroleum sector to exchequer (₹ crore) | Centre & states | FY 2014-15 → Q1 2026-27 (P) | Annual | tax-take charts |
| CGD: CNG stations and PNG connections (domestic/commercial/industrial) | States | Snapshots (latest 31 Jul 2026) | Periodic | CNG stations by state |
| Installed refinery capacity ('000 MT) | Refinery, state | 1 Apr 2026 | Annual | refinery map/ranking |
| Crude production, product production, imports/exports, natural gas (HTML tables / PDFs) | National | Monthly | Monthly | release pages |

**Licence:** reuse free with accurate reproduction and prominent credit (`licences/ppac.md`). ⚠ **International crude/petrol/diesel prices** on PPAC are likely third-party (e.g. Platts) and are **excluded** unless a table states PPAC ownership.

## B2. TradeStat (DGCI&S / Dept of Commerce) ✅ usable (owner decision)

**Access:** `tradestat.commerce.gov.in` — Laravel forms; each query is a POST with a session cookie + CSRF `_token`. **No login, no CAPTCHA.** robots.txt: `Disallow:` (empty, i.e. everything allowed). `trade-analytics.commerce.gov.in` also allows all and publishes a sitemap.

| Database | Contents | Periods |
|---|---|---|
| **EIDB** (annual) | Exports/imports by commodity (HS 2/4/6/8-digit) and by country (251 countries); commodity × country; region-wise; totals | FY 2021-22 → 2025-26 offered in the year dropdown (each report shows 5 years) |
| **MEIDB** (monthly) | Same, monthly | Monthly |
| FTPA, FTSPCC | Commodity-group and principal-commodity views | — |

Units: US$ million, ₹ crore, quantity (8-digit only). HS code mapping changed in April 2024 (codes dropped or re-allocated, units changed), so this is a series-break note for commodity pages.

**Site disclaimer (verbatim):** *"The data refrenced in the system do not have any legal sanctity and is for general refrence only. The user may like to verify official publications for DGCI&S, Kolkata for any further refrence."* Data source: DGCI&S, Kolkata. (Evidence: `licences/evidence/2026-10-07/tradestat-home-with-disclaimer.html`.)

⚠ **Data-quality finding on the first test query.** For India → USA, the site returned exports of **US$155,030 million in 2023-24** (+97.4%, 35.5% share of India's exports), followed by −44.2% in 2024-25. India's total exports in the same table are ~US$437 bn, and exports to the USA should be roughly half that figure. This is a **source error**. → Trade pages need: (1) jump checks (>±40% YoY flagged), (2) reconciliation of country totals against India's total, and (3) cross-checking against RBI trade data in the MoSPI API before publishing.

## B3. data.gov.in (OGD Platform) — rich but uneven; API currently down

**Access status (2026-10-08):**
- `api.data.gov.in` **refuses TCP connections** (port 443) from this Mac *and* from GitHub Actions runners. The service appears to be **down for everyone**, not just blocking us. The owner's API key is stored locally (`.env`, git-ignored) and as the GitHub secret `DATA_GOV_IN_API_KEY`.
- `www.data.gov.in` (website, including its internal `/backend/` JSON) returns **HTTP 403 Access Denied** (Akamai bot protection) to automated clients. We **do not work around this** (§3: never bypass protections).
- **Until the API returns:** data.gov.in datasets enter through **manual upload** (`pipeline/manual/data-gov-in/`, with the metadata note). The owner downloads the CSV from the dataset page in a browser. In Phase 1, a small scheduled job will re-test the API weekly and tell us when it's back.

**What the catalogue is like (fresh look).** About 230k resources, of three very different kinds:

| Kind | Example | Value to us |
|---|---|---|
| **Recurring catalogues**: same table refreshed on a schedule | District-wise crop production; PMC daily retail prices; mandi prices; HMIS monthly | ⭐ **High**: trends, release-style pages, district depth |
| **Census/survey reference tables** | Census 2011 PCA (district, sub-district, village); NFHS-5 district factsheets; district rainfall normals | ⭐ **High** for district profiles (old but authoritative; label the year) |
| **One-off Parliament-answer tables**: "State/UT-wise … as on 29-01-2025", "from 2019-20 to 2023-24" | JJM tap connections; per-capita power; GST by year; EVs on Vahan | ⚠ **Medium–low**: snapshots, inconsistent definitions, may never update. Use only as dated facts, never as live series. |

**Shortlist by theme** (state = S, district = D):

| Theme | Dataset(s) | Geo | Period | Why it matters |
|---|---|---|---|---|
| **Agriculture** | *District-wise, season-wise crop production statistics* (MoA&FW): area (ha) and production (t) by crop × season × year | **D** | 1997 → recent | ⭐ Deepest district time series on the portal. "rice production in {district}", top districts by crop, state crop rankings |
| **Prices (food)** | *Daily/weekly retail and wholesale prices* (Dept of Consumer Affairs PMC): rice, wheat, atta, dals, milk, onion, potato, tomato, oils, sugar, gur… from **~75 market centres** | City/centre | Daily | ⭐ "onion price today in {city}", price trend pages. High search demand |
| **Prices (mandi)** | *Current daily price of various commodities from various markets (Mandi)* (AGMARKNET) | Market → D/S | Daily | ⭐ "tomato mandi rate {district}". Huge long tail; needs careful page-count control (§6.4 near-duplicates) |
| **Population** | *Census 2011 Primary Census Abstract* (India/states; district; village/town per state); *district-wise rural/urban population by sex* | **D** (down to village) | 2011 | ⭐ Base for every district profile: population, sex ratio, literacy, SC/ST, workers. Also the **denominator** for per-capita rates everywhere |
| **Population** | Technical Group population projections (state, age, sex) | S | 2011–2036 | Per-capita denominators for current years (label as projections) |
| **Health** | *NFHS-5 district factsheets* (2019-21); *NFHS-5 state factsheets* | **D**, S | 2019-21 (+ NFHS-4) | ⭐ District health, nutrition, sanitation, women's indicators |
| **Health** | *HMIS item-wise monthly report, all states and districts* | **D** (some sub-district) | Monthly | Institutional deliveries, immunisation, disease cases. ⚠ Administrative data; needs strong caveats |
| **Weather** | *Area-weighted monthly/seasonal/annual rainfall, 36 met subdivisions* (1951→); *District rainfall normals 1951-2000* | Subdivision, **D** (normals) | Monthly, since 1951 | Monsoon pages: "rainfall in {state} this year vs normal" |
| **Roads** | Road accidents, deaths and injuries by state/UT and city, by mode, cause and road type (MoRTH) | S, city | Annual (to 2023) | ⭐ High-interest; ⚠ **sensitive**: per-lakh-population and per-10k-vehicle rates, neutral tone |
| **Vehicles** | Registered motor vehicles by state and category; per 1,000 population; EVs on Vahan | S | 2001–2011 series + dated snapshots | Vehicle ownership rankings; EV adoption (snapshots) |
| **Energy** | Per-capita power consumption by state; average electricity tariff by state | S | Recent years (snapshots) | "per capita electricity consumption by state" |
| **Tax** | GST collection (year-wise, state-wise in places) | S | 2019-20 → 2024-25 | GST by state (check completeness) |
| **Water & schemes** | Jal Jeevan Mission tap connections; MGNREGA district "at a glance" | S, **D** | Snapshots | Scheme coverage pages. ⚠ Check for official dashboards with fuller series |
| **Tourism** | Domestic and foreign tourist visits by state | S | Annual | "most visited state in India" |

**Licence:** all GODL ✅ (`licences/data-gov-in.md`). Credit the **contributing ministry** (shown on each dataset page) plus data.gov.in, using the GODL attribution template.

**Fit with MoSPI:** data.gov.in is where the **district** depth comes from (crop production, Census 2011 PCA, NFHS-5 district, HMIS). MoSPI provides the **state and national time series**. Together they make district profile hubs feasible in Phase 3 without NDAP.

## B4. NDAP (ndap.niti.gov.in) — later phase

robots.txt allows all. Search results suggest NDAP uses NDSAP/GODL-style terms (commercial use with attribution), but this was **not verified on the site** (it's a JavaScript app). Licence check is required before use (CLAUDE.md §3). It's strong for district data and a candidate for district pages.

## B5. Original sources behind data.gov.in (checked 2026-10-09)

Most data.gov.in tables are copies of what ministries publish on their own portals, which are often fresher. Reachability was tested with our honest user agent. **"Reachable" is not "licensed":** each needs a `docs/licences/<source>.md` record before use.

| Data | Original source | Reachable | robots.txt / notes |
|---|---|---|---|
| Mandi (wholesale) prices | Agmarknet — agmarknet.gov.in | ✅ | Disallows only `/signin`, `/forgotpassword` |
| Crop production (district × crop × season) | UPAg — upag.gov.in; DES — data.desagri.gov.in | ✅ / ❌ timeout | UPAg allows all |
| Daily retail prices, ~75 centres | Dept of Consumer Affairs PMC — fcainfoweb.nic.in | ✅ | ASP.NET report forms |
| Census 2011 (state → village) | censusindia.gov.in | ✅ | Excel downloads |
| NFHS-5 district factsheets | IIPS — rchiips.org | ❌ timeout | Copy on data.gov.in; state level in MoSPI NFHS |
| HMIS (monthly district health) | hmis.mohfw.gov.in | ✅ | |
| Rainfall | IMD — mausam.imd.gov.in | ✅ | |
| Road accidents | MoRTH "Road Accidents in India" — morth.nic.in | ✅ | PDF/Excel annexes; sensitive topic |
| Vehicle registrations, EVs | Vahan dashboard — vahan.parivahan.gov.in | ✅ | Live; far fresher than data.gov.in snapshots |
| Tap water connections | Jal Jeevan Mission — ejalshakti.gov.in | ✅ | Live, to village level |
| MGNREGA | nrega.nic.in | ✅ | District/block reports |
| Electricity | CEA — cea.nic.in | ✅ | General Review (annual), monthly reports |
| Banking, state finances | RBI — rbi.org.in (Handbook of Statistics on Indian States); DBIE — dbie.rbi.org.in | ✅ / ❌ timeout | |
| School education (district) | UDISE+ — udiseplus.gov.in | ✅ | State level already via MoSPI |
| Many of the above, harmonised | NDAP — ndap.niti.gov.in | ✅ | robots allows all; licence to verify |
| Official place codes | LGD — lgdirectory.gov.in | ✅ | **Required** master list (§5) |
| Official India boundaries | Survey of India — surveyofindia.gov.in | ✅ | Required for maps (§7) |

**Approach:** original portals are primary; data.gov.in (GODL, the clearest licence) is the fallback when an original is down or awkward. Licence checks to do before the first cluster: **LGD, Census 2011, Agmarknet, Vahan** (plus any other the cluster needs). Many originals are form-based dashboards: scrapable within §3 rules (no logins or CAPTCHAs), each with its own validation checks.

## B6. What this changes

- **Topics now covered for the first cluster** (beyond MoSPI): **fuel** (state consumption, VAT, petrol pumps, LPG/Ujjwala, metro prices) and **trade** (country and commodity, with validation).
- **Topics added from data.gov.in:** agriculture (district crop production), food prices (daily retail by city, mandi), population (Census 2011), road safety, vehicles, rainfall.
- **District pages:** feasible from data.gov.in (crop production, Census 2011 PCA, NFHS-5 district, HMIS) via manual download while the API is down. NDAP stays a later addition.
