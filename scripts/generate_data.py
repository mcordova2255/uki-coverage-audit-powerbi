"""
Generates the four coverage tables used by UKI_Coverage_Audit.pbix.

Every row is synthetic. Names, companies, territories and amounts are
invented so the model can be shown outside the organisation it was
designed for. The generator is seeded, so running it again produces
the same files.

Headline totals the model is built to land on:
    Accounts   400 rows, 170 with a defect (42.5 percent)
    Total TAM  10,613,100   TAM at risk 2,968,000 (28.0 percent)
    Reps       12 rows, net TAM correction -210,700, net quota correction -50,500
    Movements  48 rows, corrections -1,038,700, reforecast +828,000
    Cases      260 rows, 163 open, 97 closed or implemented, 96 stalled

Run:  python scripts/generate_data.py
"""
import csv, random, datetime as dt, os

random.seed(2026)
OUT = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- Reps
# opening TAM, corrections, reforecast per rep. closing = opening + both.
REPS = [
    ("R01", "Aisha Khan",    "Inside", "Inside Sales Rep",  595400,  -56400,  35000),
    ("R02", "Chloe Evans",   "Field",  "Field Sales Rep",   541400,  -66500,  77900),
    ("R03", "Daniel Brooks", "Field",  "Field Sales Rep",  2028600, -223800,  98000),
    ("R04", "Hannah Cole",   "Inside", "Inside Sales Rep",  557400,  -52700,  44900),
    ("R05", "Jamie Patel",   "Field",  "Field Sales Rep",   778900, -107300, 159500),
    ("R06", "Laura Bennett", "Field",  "Field Sales Rep",  1188900, -116600,  86900),
    ("R07", "Marcus Flynn",  "Inside", "Inside Sales Rep",  556100,  -31500,   4800),
    ("R08", "Megan Walsh",   "Inside", "Inside Sales Rep",  748400,  -68200,  12800),
    ("R09", "Oliver Grant",  "Inside", "Inside Sales Rep",  590600,  -45000,  97000),
    ("R10", "Priya Shah",    "Field",  "Field Sales Rep",  1366100, -100000, -24300),
    ("R11", "Ryan Cooper",   "Inside", "Inside Sales Rep",  623000,  -55900,  86400),
    ("R12", "Sophie Reed",   "Field",  "Field Sales Rep",  1038300, -114800, 149100),
]
assert sum(r[4] for r in REPS) == 10_613_100
assert sum(r[5] for r in REPS) == -1_038_700
assert sum(r[6] for r in REPS) == 828_000

rep_rows = []
quota_deltas = []
for rid, name, team, role, tam, corr, refc in REPS:
    delta = corr + refc
    cq = int(round(tam * 0.32, -2))
    qd = int(round(delta * 0.24, -2))
    quota_deltas.append(qd)
    rep_rows.append([rid, name, team, role, tam, tam + delta, delta,
                     round(delta / tam, 4), cq, cq + qd, qd,
                     "Decrease" if delta < 0 else "Increase"])
# force net quota correction to exactly -50,500 on the largest rep
fix = -50_500 - sum(quota_deltas)
rep_rows[2][10] += fix; rep_rows[2][9] += fix
assert sum(r[10] for r in rep_rows) == -50_500
assert sum(r[6] for r in rep_rows) == -210_700

with open(f"{OUT}/rep_impact.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rep_id", "rep_name", "team", "role_type", "current_tam",
                "corrected_tam", "tam_delta", "tam_delta_pct", "current_quota",
                "corrected_quota", "quota_delta", "direction"])
    w.writerows(rep_rows)

# ---------------------------------------------------------------- Movements
REASONS = ["Wrong parent", "Closed entity", "Duplicate"]
mov_rows = []
for rid, name, team, role, tam, corr, refc in REPS:
    parts = [random.random() for _ in REASONS]
    s = sum(parts)
    amts = [int(round(corr * p / s, -2)) for p in parts]
    amts[-1] = corr - sum(amts[:-1])
    for reason, a in zip(REASONS, amts):
        mov_rows.append([name, "Correction", reason, a])
    mov_rows.append([name, "Reforecast", "Headcount change in filings", refc])
assert len(mov_rows) == 48
assert sum(r[3] for r in mov_rows) == -210_700
with open(f"{OUT}/tam_movements.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rep_name", "movement_type", "movement_reason", "amount"])
    w.writerows(mov_rows)

# ---------------------------------------------------------------- Accounts
VERTICALS = {  # vertical: (clean, defect)
    "Financial & Retail": (93, 67),
    "Education":          (66, 53),
    "Public Sector":      (71, 50),
}
ISSUE_COUNTS = [("Duplicate Ownership", 38), ("Wrong Parent", 26),
                ("Orphan Account", 24), ("Territory Misalignment", 21),
                ("Active Bid Misaligned", 17), ("Closed Entity", 17),
                ("Missing Organization", 14), ("Wrong Segment", 13)]
assert sum(c for _, c in ISSUE_COUNTS) == 170
assert sum(a + b for a, b in VERTICALS.values()) == 400

# the ten largest at-risk accounts, fixed so the page reads the same way
TOP = [
    ("Sterling Leasing", "Sterling Retail Group plc", "Financial & Retail", "Strategic", "Duplicate Ownership", "High", 92200),
    ("Cavendish Stores", "Cavendish Commerce Group plc", "Financial & Retail", "Strategic", "Duplicate Ownership", "High", 91000),
    ("Regent Payments", "Regent Retail Holdings", "Financial & Retail", "Strategic", "Closed Entity", "High", 77400),
    ("Summit Online Retail", "Summit Retail Holdings", "Financial & Retail", "Strategic", "Duplicate Ownership", "High", 73400),
    ("Hollowell Wealth", "Hollowell Retail Holdings", "Financial & Retail", "Strategic", "Duplicate Ownership", "High", 63900),
    ("Saxon Leasing", "Saxon Banking Group", "Financial & Retail", "Strategic", "Closed Entity", "High", 57300),
    ("Westfield Asset Management", "Westfield Retail Holdings", "Financial & Retail", "Strategic", "Missing Organization", "Medium", 55600),
    ("Bristol Card Services", "Bristol Banking Group", "Financial & Retail", "Strategic", "Wrong Segment", "Medium", 53300),
    ("Pinnacle Housing", "Pinnacle Government Services", "Public Sector", "Enterprise", "Duplicate Ownership", "High", 48700),
    ("Thornbury Nursery Group", "Thornbury Education Holdings", "Education", "Enterprise", "Closed Entity", "High", 47400),
]

FIRST = ["Sterling", "Cavendish", "Regent", "Summit", "Hollowell", "Saxon", "Westfield",
         "Bristol", "Pinnacle", "Thornbury", "Albion", "Beacon", "Carlton", "Dorset",
         "Elmwood", "Fairview", "Granite", "Harbour", "Ironside", "Juniper", "Kestrel",
         "Lancaster", "Meridian", "Norfolk", "Oakridge", "Pembroke", "Quayside", "Redwood",
         "Severn", "Tamar", "Ulster", "Vale", "Wessex", "Yarrow", "Ashford", "Brook",
         "Clyde", "Dunmore", "Eden", "Forth"]
NOUN = {
    "Financial & Retail": (["Leasing", "Stores", "Payments", "Wealth", "Card Services", "Insurance",
                            "Retail", "Capital", "Lending", "Brokers", "Outlets", "Trading"],
                           ["Retail Group plc", "Banking Group", "Retail Holdings", "Financial Group",
                            "Commerce Group plc", "Capital Partners"]),
    "Education":          (["Academy Trust", "College", "Nursery Group", "School", "Learning Trust",
                            "Sixth Form", "Training", "Institute"],
                           ["Education Holdings", "Academies Trust", "Learning Group", "Education Trust"]),
    "Public Sector":      (["Housing", "Council Services", "Health Partnership", "Transport",
                            "Water", "Fire Service", "Community Trust", "Library Service"],
                           ["Government Services", "Public Services Group", "Civic Partnership",
                            "Regional Authority"]),
}
REGIONS = [("United Kingdom", "London"), ("United Kingdom", "South East"), ("United Kingdom", "Midlands"),
           ("United Kingdom", "North"), ("United Kingdom", "Scotland"), ("United Kingdom", "Wales"),
           ("Ireland", "Dublin"), ("Ireland", "Munster")]
TERR = [(f"T{i:03d}", f"{r[1]} {k}") for i, (r, k) in enumerate(
    [(r, k) for r in REGIONS for k in ("Core", "Growth", "Named", "Emerging", "Install")], start=1)]
SEGMENTS = ["Strategic", "Enterprise", "Corporate", "Mid-Market"]
BANDS = ["50-249", "250-999", "1,000-4,999", "5,000+"]
SEVERITY_BY_ISSUE = {
    "Duplicate Ownership": ["High", "High", "Medium"],
    "Wrong Parent": ["High", "Medium", "Medium"],
    "Orphan Account": ["Medium", "Medium", "Low"],
    "Territory Misalignment": ["High", "Medium", "Low"],
    "Active Bid Misaligned": ["High", "High", "High"],
    "Closed Entity": ["High", "Medium"],
    "Missing Organization": ["Medium", "Low"],
    "Wrong Segment": ["Medium", "Low", "Low"],
}

# issue pool for the 160 non-fixed defects
issue_pool = []
for issue, n in ISSUE_COUNTS:
    issue_pool += [issue] * n
for t in TOP:
    issue_pool.remove(t[4])
random.shuffle(issue_pool)

# build 400 skeleton rows: vertical + health
skel = []
for v, (clean, defect) in VERTICALS.items():
    skel += [(v, "Clean")] * clean + [(v, "Defect")] * defect
# fixed TOP rows take defect slots in their vertical
for t in TOP:
    skel.remove((t[2], "Defect"))
random.shuffle(skel)

accounts = []
used = set()
def mkname(v):
    for _ in range(1000):
        a = random.choice(FIRST); b = random.choice(NOUN[v][0])
        n = f"{a} {b}"
        if n not in used:
            used.add(n); return n, f"{a} {random.choice(NOUN[v][1])}"
    raise RuntimeError

# 1. the ten fixed rows
for name, parent, v, seg, issue, sev, risk in TOP:
    used.add(name)
    accounts.append(dict(account_name=name, parent_company=parent, vertical=v, segment=seg,
                         health="Defect", issue_type=issue, issue_severity=sev, tam_at_risk=risk))
# 2. the rest
for v, h in skel:
    name, parent = mkname(v)
    row = dict(account_name=name, parent_company=parent, vertical=v,
               segment=random.choices(SEGMENTS, [1, 3, 4, 4])[0], health=h)
    if h == "Defect":
        issue = issue_pool.pop()
        row.update(issue_type=issue, issue_severity=random.choice(SEVERITY_BY_ISSUE[issue]),
                   tam_at_risk=random.randint(20, 460) * 100)
    else:
        row.update(issue_type="None", issue_severity="None", tam_at_risk=0)
    accounts.append(row)
assert len(accounts) == 400 and not issue_pool

# 3. scale the free at-risk amounts so the total is exactly 2,968,000
fixed = sum(t[6] for t in TOP)
free = [a for a in accounts if a["health"] == "Defect" and a["account_name"] not in {t[0] for t in TOP}]
target = 2_968_000 - fixed
cur = sum(a["tam_at_risk"] for a in free)
for a in free:
    a["tam_at_risk"] = int(max(1000, round(a["tam_at_risk"] * target / cur, -2)))
diff = target - sum(a["tam_at_risk"] for a in free)
free[0]["tam_at_risk"] += diff
assert sum(a["tam_at_risk"] for a in accounts) == 2_968_000
assert max(a["tam_at_risk"] for a in free) < 47_400

# 4. assign reps in proportion to their opening TAM, then size estimated_tam
#    so each rep's accounts sum exactly to that rep's opening TAM
rep_tam = {r[1]: r[4] for r in REPS}
total_tam = sum(rep_tam.values())
random.shuffle(accounts)
counts = {n: max(12, round(400 * t / total_tam)) for n, t in rep_tam.items()}
while sum(counts.values()) > 400:
    counts[max(counts, key=counts.get)] -= 1
while sum(counts.values()) < 400:
    counts[min(counts, key=counts.get)] += 1
i = 0
for name, n in counts.items():
    for a in accounts[i:i + n]:
        a["rep_name"] = name
    i += n
for name, t in rep_tam.items():
    mine = [a for a in accounts if a["rep_name"] == name]
    # weight: at-risk accounts need headroom above their at-risk amount
    base = [a["tam_at_risk"] / 0.6 + random.randint(60, 400) * 100 for a in mine]
    s = sum(base)
    for a, b in zip(mine, base):
        a["estimated_tam"] = int(max(a["tam_at_risk"], round(b * t / s, -2)))
    diff = t - sum(a["estimated_tam"] for a in mine)
    big = max(mine, key=lambda a: a["estimated_tam"])
    big["estimated_tam"] += diff
    assert sum(a["estimated_tam"] for a in mine) == t
    assert all(a["estimated_tam"] >= a["tam_at_risk"] for a in mine)
assert sum(a["estimated_tam"] for a in accounts) == 10_613_100

# 5. remaining attributes
accounts.sort(key=lambda a: (-a["tam_at_risk"], a["account_name"]))
for k, a in enumerate(accounts, start=1):
    a["account_id"] = f"A{k:04d}"
    country, region = random.choice(REGIONS)
    tid, tname = random.choice([t for t in TERR if t[1].startswith(region)])
    a.update(country=country, region=region, territory_id=tid, territory_name=tname,
             employee_band=random.choices(BANDS, [4, 4, 2, 1])[0],
             active_bid="No",
             hierarchy_status=("Verified" if a["health"] == "Clean"
                               else random.choice(["Unverified", "Pending", "Verified"])),
             resolution_status=("Not required" if a["health"] == "Clean"
                                else random.choice(["Open", "In progress", "Resolved"])),
             severity_rank={"High": 3, "Medium": 2, "Low": 1, "None": 0}[a["issue_severity"]])
# active bids: 119 accounts in total, 48 of them on defective records, 21 of those High severity.
# These match the companion Python capstone and the Tableau build so the three tell one story.
defect_high = [a for a in accounts if a["health"] == "Defect" and a["issue_severity"] == "High"]
defect_rest = [a for a in accounts if a["health"] == "Defect" and a["issue_severity"] != "High"]
clean_all   = [a for a in accounts if a["health"] == "Clean"]
for a in random.sample(defect_high, 21) + random.sample(defect_rest, 27) + random.sample(clean_all, 71):
    a["active_bid"] = "Yes"
assert sum(a["active_bid"] == "Yes" for a in accounts) == 119
assert sum(a["active_bid"] == "Yes" and a["health"] == "Defect" for a in accounts) == 48
assert sum(a["active_bid"] == "Yes" and a["issue_severity"] == "High" for a in accounts) == 21

cols = ["account_id", "account_name", "parent_company", "vertical", "segment", "country", "region",
        "territory_id", "territory_name", "rep_name", "employee_band", "estimated_tam", "health",
        "issue_type", "issue_severity", "severity_rank", "tam_at_risk", "active_bid",
        "hierarchy_status", "resolution_status"]
with open(f"{OUT}/coverage_accounts.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(accounts)

# ---------------------------------------------------------------- Cases
defects = [a for a in accounts if a["health"] == "Defect"]
TEAMS = ["Business Analyst", "Master Data", "Sales Operations", "Market Approver"]
status_pool = (["Submitted"] * 60 + ["Approved"] * 55 + ["Delayed"] * 48
               + ["Implemented"] * 62 + ["Closed"] * 35)
assert len(status_pool) == 260
random.shuffle(status_pool)
open_idx = [i for i, s in enumerate(status_pool) if s in ("Submitted", "Approved", "Delayed")]
assert len(open_idx) == 163
stalled_idx = set(random.sample(open_idx, 96))
case_accounts = defects + random.sample(defects, 90)        # 260 cases over 170 accounts
random.shuffle(case_accounts)
asof = dt.date(2026, 9, 25)
cases = []
for i, (a, status) in enumerate(zip(case_accounts, status_pool), start=1):
    if status in ("Submitted", "Approved", "Delayed"):
        days = random.randint(31, 140) if i - 1 in stalled_idx else random.randint(1, 30)
    else:
        days = random.randint(5, 90)
    opened = asof - dt.timedelta(days=days)
    cases.append([f"C{i:04d}", a["account_id"], a["vertical"], a["issue_type"],
                  random.choice(TEAMS), status,
                  "Stalled" if i - 1 in stalled_idx else "Moving", days,
                  opened.isoformat(), opened.replace(day=1).isoformat()])
with open(f"{OUT}/case_flow.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["case_id", "account_id", "vertical", "issue_type", "owning_team",
                "implementation_status", "is_stalled", "days_open", "date_opened", "month_opened"])
    w.writerows(cases)

print("accounts", len(accounts), "defects", len(defects),
      "TAM", sum(a["estimated_tam"] for a in accounts),
      "at risk", sum(a["tam_at_risk"] for a in accounts))
print("cases", len(cases), "open", len(open_idx), "stalled", len(stalled_idx))
print("reps", len(rep_rows), "net TAM", sum(r[6] for r in rep_rows), "net quota", sum(r[10] for r in rep_rows))
print("movements", len(mov_rows), "net", sum(r[3] for r in mov_rows))
