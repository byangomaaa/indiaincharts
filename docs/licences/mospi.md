# Licence record — MoSPI (eSankhyiki API / MCP)

| Field | Value |
|---|---|
| Source | Ministry of Statistics and Programme Implementation (MoSPI), Government of India |
| Access | `api.mospi.gov.in` (REST), `mcp.mospi.gov.in` (MCP, discovery only), portal `esankhyiki.mospi.gov.in` |
| Date checked | 2026-10-07 |
| Checked by | Claude Code (Phase 0) — **owner to confirm** |
| Evidence | `evidence/2026-10-07/esankhyiki-llms.txt`, `esankhyiki-ard.json`, `mospi-nas-publication-copyright-notice.pdf`, `godl-india-gazette-2017-02-13.pdf` (SHA-256 in `SHA256SUMS`) |
| Status | ✅ **Usable with credit — owner decision 2026-10-07.** No explicit API licence found; attribution on every surface is mandatory. |

## What we found

1. **eSankhyiki portal, `llms.txt` and ARD manifest** (machine-readable files MoSPI publishes for AI/agents): require **attribution** — preserve dataset name, indicator, value, unit, reference period, source, publication/update info, and link to the original source. They state **no licence and no restriction on commercial use**.
2. **The MCP server code** (`github.com/nso-india/esankhyiki-mcp`) is MIT-licensed. That covers the **code only**, not the data.
3. **Older MoSPI print publications** (e.g. National Accounts Statistics) carry: *"All rights are reserved. No part of this publication can be reproduced **for sale** in any form or by any means … without prior permission in writing from the Director General, Central Statistical Organisation."* This targets reselling the publication. We don't sell data or publications, but an ad-funded site is commercial, so the notice is a caution.
4. **GODL-India** (Gazette, 13 Feb 2017) grants a worldwide, royalty-free licence for "all lawful commercial and non-commercial purposes" for shareable, non-sensitive data generated with public funds by Government of India agencies, as published under NDSAP. MoSPI publishes many datasets on data.gov.in under GODL. Whether GODL automatically covers the eSankhyiki **API** is not stated anywhere we could find.

## Assessment

- CLAUDE.md's "commercial use allowed with credit" is **plausible but not documented** for the API. Risk is low (aggregate official statistics, credited, not resold, no endorsement implied), but per §1 "accuracy over volume" and §2 "ask before irreversible", we should **get it in writing** before the public launch.
- **Owner decision (2026-10-07):** the owner is confident the data may be used with credit and accepts the residual risk. No launch gate. The email below is optional, for written confirmation if ever wanted.

## Credit line (use everywhere)

> Source: Ministry of Statistics and Programme Implementation (MoSPI), eSankhyiki — {Dataset name}, {indicator}, {reference period}, released {dd Mon yyyy}. {source URL}. Visualised by IndiaInCharts. Not endorsed by MoSPI.

Never use the MoSPI logo, the State Emblem, or wording like "official" in our branding.

## Permission-request email (optional)

**To:** MoSPI eSankhyiki / data dissemination contact (find the current address on esankhyiki.mospi.gov.in → Contact, or mospi.gov.in → Contact Us)
**Subject:** Request to confirm reuse terms for eSankhyiki API data (attributed, free public website)

> Dear Sir/Madam,
>
> I am building IndiaInCharts (indiaincharts.com), a free public website that presents published aggregate statistics from the eSankhyiki API as charts, tables and short factual summaries, so that citizens, students and journalists can find and understand them easily.
>
> Every page will credit MoSPI and eSankhyiki with the dataset name, reference period, release date and a link to the original source, and will state that the site is not endorsed by MoSPI. We will use published aggregate data only (no unit-level data), will not resell data, and will not use the Ministry's name, logo or emblem in our branding. The site will be free to use and supported by display advertising.
>
> Could you please confirm that this use is permitted, and whether the eSankhyiki API data is covered by the Government Open Data License – India (GODL), or let me know of any conditions we should follow?
>
> Thank you for making these statistics openly available.
>
> Regards,
> Prasenjit Sharma
> IndiaInCharts

Record the reply (date, sender, text) in this file and save it under `evidence/`.
