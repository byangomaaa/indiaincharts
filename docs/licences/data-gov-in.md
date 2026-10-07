# Licence record — data.gov.in (Open Government Data Platform India)

| Field | Value |
|---|---|
| Licence | Government Open Data License – India (GODL-India) |
| Licence URL | https://data.gov.in/government-open-data-license-india |
| Legal text | Gazette of India, Extraordinary, Part I Sec 1, No. 42, 13 Feb 2017 (MeitY notification No. 8(2)/2013-EG-I, dated 10 Feb 2017) |
| Date checked | 2026-10-07 |
| Evidence | `evidence/2026-10-07/godl-india-gazette-2017-02-13.pdf` |
| Status | ✅ **Commercial use permitted with attribution.** Check each dataset page shows GODL before use. |

## Key terms (quoted from the Gazette, §3–7)

- **Grant (§3):** "worldwide, royalty-free, non-exclusive license to use, adapt, publish (either in original, or in adapted and/or derivative forms), translate, display, add value, and create derivative works (including products and services), for all lawful commercial and non-commercial purposes".
- **Attribution (§4a):** "acknowledge the provider, source, and license of data by explicitly publishing the attribution statement, including the DOI … or the URL … or the URI of the data concerned."
- **Multiple data (§4b):** may link to a separate page listing all attribution statements → our per-page "Source & method" section plus a site-wide `/sources/` page.
- **Non-endorsement (§4c):** "must not indicate or suggest in any manner that the data provider(s) endorses their use and/or the user."
- **No warranty (§4d)** and **no guarantee of continued updates (§4e)**.
- **Exemptions (§6):** personal information; non-shareable/sensitive data; "names, crests, logos and other official symbols of the data provider(s)"; data under other IP rights; military insignia; identity documents; RTI §8 data.
- **Termination (§7):** rights end automatically on non-compliance; reinstated if cured within 30 days.
- **Disputes / law (§8–9):** arbitrator appointed by the Union Law Secretary; Indian law.

## Attribution template (§5)

> "[Name of Data Provider], [Year of Publication], [Name of Data], [Name of Data Repository/Website], [Version Number and/or Date of Publication (dd/mm)], [DOI / URL / URI]. Published under [Name of License]: [URL of License]."

Our form:

> Source: {Provider}, {year}, {dataset}, Open Government Data Platform India, {dd/mm}, {dataset URL}. Published under Government Open Data License – India: https://data.gov.in/government-open-data-license-india. Visualised by IndiaInCharts. Not endorsed by {Provider}.

## Notes

- API needs a key → store only in CI secrets / local `.env`.
- The website blocked an automated fetch of the licence page (HTTP 403 to one tool); the Gazette PDF downloaded fine. Respect rate limits.
