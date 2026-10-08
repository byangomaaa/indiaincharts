"""Generate keyword candidates for Google Keyword Planner (CLAUDE.md §8, step 1-2).

Only topics we have (or can get) data for — see docs/data-inventory.md.

Usage: python keywords/generate_candidates.py [YYYY-MM]
Outputs in keywords/<YYYY-MM>/:
  candidates-all.csv            keyword + topic, page type, indicator, geo, source, data status
  planner-upload-NN.txt         one keyword per line, <= 700 per file (upload these to Keyword Planner)
"""
import csv
import os
import re
import sys
from datetime import date

RUN = sys.argv[1] if len(sys.argv) > 1 else date.today().strftime("%Y-%m")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), RUN)
BATCH = 700

STATES = [
    "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", "goa", "gujarat",
    "haryana", "himachal pradesh", "jharkhand", "karnataka", "kerala", "madhya pradesh",
    "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", "odisha", "punjab", "rajasthan",
    "sikkim", "tamil nadu", "telangana", "tripura", "uttar pradesh", "uttarakhand", "west bengal",
]
UTS = [
    "delhi", "jammu and kashmir", "ladakh", "puducherry", "chandigarh",
    "andaman and nicobar islands", "lakshadweep", "dadra and nagar haveli and daman and diu",
]
GEOS = STATES + UTS
BIG = [  # larger states/UTs for lower-priority patterns
    "andhra pradesh", "assam", "bihar", "chhattisgarh", "gujarat", "haryana", "jharkhand",
    "karnataka", "kerala", "madhya pradesh", "maharashtra", "odisha", "punjab", "rajasthan",
    "tamil nadu", "telangana", "uttar pradesh", "west bengal", "delhi",
]
METROS = ["delhi", "mumbai", "kolkata", "chennai"]
CITIES = METROS + ["bengaluru", "hyderabad", "ahmedabad", "pune", "lucknow", "jaipur",
                   "patna", "bhopal", "chandigarh", "bhubaneswar", "guwahati"]
COUNTRIES = [
    "usa", "china", "uae", "saudi arabia", "russia", "singapore", "netherlands", "uk",
    "germany", "hong kong", "bangladesh", "japan", "south korea", "indonesia", "australia",
    "iraq", "malaysia", "nepal", "france", "italy", "switzerland", "south africa", "brazil",
    "vietnam", "thailand", "sri lanka", "canada", "qatar", "belgium", "turkey",
]
CROPS = ["rice", "wheat", "maize", "sugarcane", "cotton", "pulses", "gram", "tur dal",
         "groundnut", "soybean", "mustard", "potato", "onion", "tea", "coffee", "jute"]
FOOD = ["onion", "tomato", "potato", "rice", "wheat", "atta", "tur dal", "milk", "sugar", "mustard oil"]
YEAR = date.today().year
MONTH = date.today().strftime("%B").lower()

rows = []


def add(keyword, topic, page_type, indicator, geo, source, status="ready"):
    kw = re.sub(r"\s+", " ", keyword.lower()).strip()
    rows.append(dict(keyword=kw, topic=topic, page_type=page_type, indicator=indicator,
                     geo=geo, source=source, data_status=status))


# --- Labour (MoSPI PLFS) ---
for g in GEOS:
    add(f"unemployment rate in {g}", "labour", "metric", "unemployment-rate", g, "MoSPI PLFS")
    add(f"{g} unemployment rate", "labour", "metric", "unemployment-rate", g, "MoSPI PLFS")
for g in BIG:
    add(f"youth unemployment rate {g}", "labour", "metric", "youth-unemployment-rate", g, "MoSPI PLFS")
    add(f"female labour force participation rate {g}", "labour", "metric", "female-lfpr", g, "MoSPI PLFS")
    add(f"average salary in {g}", "labour", "metric", "regular-wage-earnings", g, "MoSPI PLFS")
for k in ["unemployment rate in india", f"unemployment rate in india {YEAR}", "india unemployment rate",
          "states with highest unemployment rate", "state wise unemployment rate in india",
          "youth unemployment rate india", "female unemployment rate india", "urban unemployment rate india",
          "rural unemployment rate india", "labour force participation rate india",
          "female labour force participation rate india", "worker population ratio india",
          "plfs monthly bulletin", "plfs quarterly bulletin", "plfs annual report",
          f"unemployment rate {MONTH} {YEAR}", "unemployment rate by education india",
          "graduate unemployment rate india", "average salary in india", "average monthly wage india"]:
    add(k, "labour", "national/ranking/release", "", "india", "MoSPI PLFS")

# --- Prices (MoSPI CPI, WPI) + tools ---
for k in ["inflation rate in india", f"inflation rate in india {YEAR}", "cpi inflation india",
          "retail inflation india", f"cpi inflation {MONTH} {YEAR}", f"retail inflation {MONTH} {YEAR}",
          "food inflation india", "core inflation india", "rural inflation india", "urban inflation india",
          "wpi inflation india", f"wpi inflation {MONTH} {YEAR}", "wholesale inflation india",
          "cpi new base year 2024", "state wise inflation india", "states with highest inflation",
          "inflation calculator india", "inflation calculator rupee", "value of rupee over time",
          "value of 1 rupee in 1990", "value of 100 rupees in 2000", "rupee value calculator",
          "purchasing power of rupee", "cpi index india", "consumer price index india"]:
    add(k, "prices", "national/release/tool", "", "india", "MoSPI CPI/WPI")
for g in BIG:
    add(f"inflation rate in {g}", "prices", "metric", "cpi-inflation", g, "MoSPI CPI")

# --- State economy (MoSPI NAS) ---
for g in GEOS:
    add(f"gdp of {g}", "economy", "metric", "gsdp", g, "MoSPI NAS")
    add(f"{g} gdp", "economy", "metric", "gsdp", g, "MoSPI NAS")
    add(f"per capita income of {g}", "economy", "metric", "per-capita-nsdp", g, "MoSPI NAS")
for g in BIG:
    add(f"{g} gdp growth rate", "economy", "metric", "gsdp-growth", g, "MoSPI NAS")
for k in ["gdp of india", f"india gdp {YEAR}", "india gdp growth rate", f"gdp growth rate {YEAR}",
          "gdp growth rate india quarterly", "richest state in india", "states by gdp india",
          "state wise gdp of india", "per capita income of india", "state wise per capita income india",
          "highest per capita income state in india", "lowest per capita income state in india",
          "gsdp ranking of states", "gdp new base year 2022-23", "gva india"]:
    add(k, "economy", "national/ranking/release", "", "india", "MoSPI NAS")
for a, b in [("maharashtra", "gujarat"), ("maharashtra", "tamil nadu"), ("gujarat", "tamil nadu"),
             ("karnataka", "tamil nadu"), ("uttar pradesh", "bihar"), ("kerala", "tamil nadu"),
             ("karnataka", "maharashtra"), ("telangana", "andhra pradesh"), ("punjab", "haryana"),
             ("delhi", "mumbai")]:
    add(f"{a} vs {b} gdp", "economy", "comparison", "gsdp", f"{a}|{b}", "MoSPI NAS")
    add(f"{a} vs {b} per capita income", "economy", "comparison", "per-capita-nsdp", f"{a}|{b}", "MoSPI NAS")

# --- School education (MoSPI UDISE+) ---
for g in GEOS:
    add(f"number of schools in {g}", "education", "metric", "schools", g, "MoSPI UDISE+")
for g in BIG:
    add(f"pupil teacher ratio {g}", "education", "metric", "ptr", g, "MoSPI UDISE+")
    add(f"school dropout rate {g}", "education", "metric", "dropout-rate", g, "MoSPI UDISE+")
    add(f"number of teachers in {g}", "education", "metric", "teachers", g, "MoSPI UDISE+")
for k in ["number of schools in india", "number of government schools in india", "school enrolment india",
          "pupil teacher ratio india", "school dropout rate india", "single teacher schools india",
          "schools with internet india", "udise plus data", "number of colleges in india",
          "number of universities in india", "gross enrolment ratio higher education india",
          "state wise literacy rate india", "literacy rate of india"]:
    add(k, "education", "national/ranking", "", "india", "MoSPI UDISE+/AISHE/NSS")

# --- Renewables (MoSPI MNRE) ---
for g in BIG:
    add(f"solar power capacity {g}", "energy", "metric", "solar-capacity", g, "MoSPI MNRE")
    add(f"renewable energy capacity {g}", "energy", "metric", "re-capacity", g, "MoSPI MNRE")
for k in ["solar power capacity india", "renewable energy capacity india", "state wise solar capacity india",
          "state wise renewable energy capacity", "largest solar state in india", "wind power capacity india",
          "state wise wind power capacity", "rooftop solar capacity india", "installed renewable capacity india"]:
    add(k, "energy", "national/ranking", "", "india", "MoSPI MNRE")

# --- Fuel (PPAC) ---
for c in METROS:
    add(f"petrol price today {c}", "fuel", "metric", "petrol-rsp", c, "PPAC")
    add(f"diesel price today {c}", "fuel", "metric", "diesel-rsp", c, "PPAC")
    add(f"petrol price history {c}", "fuel", "trend", "petrol-rsp", c, "PPAC")
for g in GEOS:
    add(f"vat on petrol in {g}", "fuel", "metric", "vat-petrol", g, "PPAC")
for g in BIG:
    add(f"petrol consumption in {g}", "fuel", "metric", "ms-consumption", g, "PPAC")
    add(f"number of petrol pumps in {g}", "fuel", "metric", "retail-outlets", g, "PPAC")
    add(f"lpg connections in {g}", "fuel", "metric", "lpg-active-customers", g, "PPAC")
for k in ["state wise vat on petrol", "state wise vat on diesel", "petrol price state wise",
          "cheapest petrol state in india", "petrol consumption in india", "diesel consumption in india",
          "state wise petrol consumption", "number of petrol pumps in india", "lpg connections in india",
          "ujjwala yojana connections state wise", "cng stations in india", "png connections india",
          "petrol price breakup india", "tax on petrol in india", "india crude oil import",
          "india crude oil production"]:
    add(k, "fuel", "national/ranking", "", "india", "PPAC")

# --- Trade (TradeStat / RBI) ---
for c in COUNTRIES:
    add(f"india exports to {c}", "trade", "metric", "exports-by-country", c, "DGCI&S TradeStat")
    add(f"india imports from {c}", "trade", "metric", "imports-by-country", c, "DGCI&S TradeStat")
    add(f"india {c} trade", "trade", "metric", "total-trade-by-country", c, "DGCI&S TradeStat")
for k in ["india top exports", "india top imports", "india exports", f"india exports {YEAR}",
          "india trade deficit", "india largest trading partner", "india top export destinations",
          "india merchandise exports", "india exports by country", "india imports by country",
          "india forex reserves", "rupee dollar exchange rate history"]:
    add(k, "trade", "national/ranking", "", "india", "DGCI&S TradeStat / RBI (MoSPI)")

# --- Population & health (MoSPI GENDER/NFHS; Census 2011 licence check pending) ---
for g in GEOS:
    add(f"population of {g}", "population", "metric", "population", g, "Census 2011 / projections", "licence_check")
    add(f"sex ratio of {g}", "population", "metric", "sex-ratio", g, "Census 2011 / MoSPI GENDER", "licence_check")
    add(f"literacy rate of {g}", "population", "metric", "literacy-rate", g, "Census 2011 / MoSPI NSS", "licence_check")
for g in BIG:
    add(f"anaemia in women {g}", "health", "metric", "anaemia-women", g, "MoSPI NFHS")
    add(f"child stunting {g}", "health", "metric", "stunting", g, "MoSPI NFHS")
    add(f"institutional delivery rate {g}", "health", "metric", "institutional-births", g, "MoSPI NFHS")
for k in ["population of india", "state wise population of india", "most populated state in india",
          "sex ratio of india", "state wise sex ratio india", "highest sex ratio state in india",
          "literacy rate state wise", "highest literacy rate state in india", "nfhs 5 state wise data",
          "anaemia in india nfhs 5", "child stunting india"]:
    add(k, "population/health", "national/ranking", "", "india", "Census 2011 / MoSPI", "licence_check")

# --- Agriculture (UPAg / data.gov.in; licence check pending) ---
for crop in CROPS:
    add(f"{crop} production in india", "agriculture", "national", f"{crop}-production", "india", "UPAg / data.gov.in", "licence_check")
    add(f"largest {crop} producing state in india", "agriculture", "ranking", f"{crop}-production", "india", "UPAg / data.gov.in", "licence_check")
    add(f"state wise {crop} production", "agriculture", "ranking", f"{crop}-production", "india", "UPAg / data.gov.in", "licence_check")
for crop in ["rice", "wheat", "sugarcane", "cotton"]:
    for g in BIG:
        add(f"{crop} production in {g}", "agriculture", "metric", f"{crop}-production", g, "UPAg / data.gov.in", "licence_check")

# --- Food prices (PMC / Agmarknet; licence check pending) ---
for f in FOOD:
    add(f"{f} price today", "food-prices", "national", f"{f}-retail-price", "india", "DoCA PMC / Agmarknet", "licence_check")
    for c in CITIES:
        add(f"{f} price today in {c}", "food-prices", "metric", f"{f}-retail-price", c, "DoCA PMC / Agmarknet", "licence_check")

# --- Road safety, vehicles, electricity, tax (various; licence checks pending except GODL copies) ---
for g in BIG:
    add(f"road accidents in {g}", "road-safety", "metric", "road-accidents", g, "MoRTH", "licence_check")
    add(f"number of vehicles in {g}", "vehicles", "metric", "registered-vehicles", g, "Vahan / data.gov.in", "licence_check")
    add(f"electric vehicles in {g}", "vehicles", "metric", "ev-registrations", g, "Vahan", "licence_check")
    add(f"per capita electricity consumption {g}", "energy", "metric", "per-capita-power", g, "CEA / data.gov.in", "licence_check")
    add(f"gst collection {g}", "tax", "metric", "gst-collection", g, "data.gov.in (GODL)")
for k in ["road accidents in india", "road accident deaths india", "state wise road accidents india",
          "number of vehicles in india", "state wise vehicle registration", "ev sales state wise india",
          "per capita electricity consumption india", "state wise per capita electricity consumption",
          "electricity tariff state wise", "gst collection india", "state wise gst collection",
          "monthly consumption expenditure india", "mpce state wise", "time use survey india"]:
    status = "ready" if any(w in k for w in ("gst", "mpce", "consumption expenditure", "time use")) else "licence_check"
    add(k, "misc", "national/ranking", "", "india", "various", status)

# --- Write ---
seen, uniq = set(), []
for r in rows:
    if r["keyword"] in seen or len(r["keyword"]) > 80 or re.search(r"[^a-z0-9 \-]", r["keyword"]):
        continue
    seen.add(r["keyword"])
    uniq.append(r)

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "candidates-all.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(uniq[0].keys()))
    w.writeheader()
    w.writerows(uniq)
for i in range(0, len(uniq), BATCH):
    with open(os.path.join(OUT, f"planner-upload-{i // BATCH + 1:02d}.txt"), "w") as fh:
        fh.write("\n".join(r["keyword"] for r in uniq[i:i + BATCH]) + "\n")

from collections import Counter
print(f"{len(uniq)} keywords -> {OUT}")
print("by topic:", dict(Counter(r["topic"] for r in uniq)))
print("by status:", dict(Counter(r["data_status"] for r in uniq)))
