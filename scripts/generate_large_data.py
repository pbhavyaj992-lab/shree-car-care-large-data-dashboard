#!/usr/bin/env python3
"""
Generate lakh-scale sample data for Shree Car Care - 3 branches.
Sample data only. Fictional business, no real customers.

Run:  python3 scripts/generate_large_data.py
Seed 42, stdlib only, deterministic - run it twice, same output.
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)
random.seed(SEED)

FIRST = ["Aarav", "Vivaan", "Aditya", "Arjun", "Sai", "Reyansh", "Krishna", "Ishaan",
         "Rohan", "Kabir", "Ananya", "Diya", "Aadhya", "Myra", "Sara", "Ira",
         "Priya", "Anika", "Navya", "Riya", "Aryan", "Dhruv", "Kavya", "Meera",
         "Nikhil", "Karan", "Vikram", "Suresh", "Ramesh", "Mahesh", "Jignesh",
         "Bhavesh", "Hardik", "Ketan", "Nilesh", "Parth", "Jay", "Yash", "Dev",
         "Amit", "Sanjay", "Rajesh", "Mohan", "Anil", "Sunil", "Prakash", "Ashok",
         "Kiran", "Seema", "Rekha", "Geeta", "Sunita", "Kavita", "Nita", "Rita",
         "Hetal", "Kinjal", "Bhavna", "Falguni", "Jinal", "Mitali", "Pooja", "Neha",
         "Rahul", "Sagar", "Manish", "Chirag", "Tejas", "Viral", "Nirav", "Pratik"]
LAST = ["Patel", "Shah", "Desai", "Mehta", "Joshi", "Trivedi", "Dave", "Bhatt",
        "Panchal", "Solanki", "Thakor", "Chauhan", "Rathod", "Parmar", "Vaghela",
        "Nayak", "Modi", "Soni", "Agarwal", "Gupta", "Sharma", "Verma", "Singh",
        "Chaudhary", "Raval", "Oza", "Pandya", "Kapadia", "Mistry", "Darji"]

BRANCHES = [
    ("AN", "Anand", 1.00),
    ("VV", "Vallabh Vidyanagar", 0.90),
    ("AH", "Ahmedabad", 1.25),
]

SERVICES = [
    ("S01", "Basic Car Wash", "Wash", 299, 30),
    ("S02", "Premium Car Wash", "Wash", 499, 45),
    ("S03", "Foam Wash", "Wash", 399, 35),
    ("S04", "Interior Detailing", "Detailing", 1499, 120),
    ("S05", "Exterior Detailing", "Detailing", 1799, 150),
    ("S06", "Full Detailing", "Detailing", 3499, 240),
    ("S07", "Ceramic Coating", "Coating", 9999, 360),
    ("S08", "Ceramic Coating Pro", "Coating", 14999, 480),
    ("S09", "Paint Protection Film", "PPF", 24999, 480),
    ("S10", "PPF Partial", "PPF", 12999, 300),
    ("S11", "Exterior Polish", "Polish", 999, 90),
    ("S12", "Headlight Restoration", "Polish", 799, 60),
]
SERVICE_WEIGHTS = [22, 18, 15, 9, 7, 5, 4, 2, 1, 1, 10, 6]  # sums to 100

STAFF_ROLES = ["Manager", "Supervisor", "Detailer", "Detailer", "Washer", "Washer"]

# Month factor: festive Oct-Nov high, monsoon Jun-Jul low
MONTH_FACTOR = {1: 1.0, 2: 0.95, 3: 1.1, 4: 1.05, 5: 1.0, 6: 0.75,
                7: 0.8, 8: 0.9, 9: 1.0, 10: 1.35, 11: 1.3, 12: 1.15}

def phone():
    if random.random() < 0.05:
        return ""
    return random.choice(["9", "8", "7"]) + "".join(random.choices("0123456789", k=9))

def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"{path.name}: {len(rows)} rows")

# --- services ---
write_csv(DATA / "large_services.csv",
          ["service_id", "service_name", "category", "base_price_inr", "duration_min"],
          SERVICES)

# --- staff: 8 per branch ---
staff_rows, staff_by_branch = [], {}
sid = 1
for code, branch, _ in BRANCHES:
    staff_by_branch[branch] = []
    for i in range(8):
        name = f"{random.choice(FIRST)} {random.choice(LAST)}"
        role = "Manager" if i == 0 else STAFF_ROLES[i % len(STAFF_ROLES)]
        staff_id = f"ST{sid:03d}"
        sid += 1
        staff_rows.append([staff_id, name, branch, role, "2023-04-01" if i == 0 else f"202{random.randint(3,5)}-{random.randint(1,12):02d}-15"])
        staff_by_branch[branch].append(staff_id)
write_csv(DATA / "large_staff.csv",
          ["staff_id", "staff_name", "branch", "role", "join_date"], staff_rows)

# --- customers: 15,000 ---
cust_rows, cust_branch = [], []
for i in range(1, 15001):
    cid = f"C{i:05d}"
    branch = random.choices([b for _, b, _ in BRANCHES],
                            weights=[w for _, _, w in BRANCHES])[0]
    cust_branch.append(branch)
    cust_rows.append([
        cid, f"{random.choice(FIRST)} {random.choice(LAST)}", branch,
        random.choices(["Walk-in", "Instagram", "Referral", "Google"],
                       weights=[40, 30, 18, 12])[0],
        phone(),
        f"202{random.randint(3,5)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
    ])
write_csv(DATA / "large_customers.csv",
          ["customer_id", "customer_name", "home_branch", "source", "phone", "first_visit_date"],
          cust_rows)

# --- bookings: 120,000 over 2024-01-01 to 2025-12-31 ---
# Build a weighted date list so festive months are busier.
start = date(2024, 1, 1)
days = [(start + timedelta(days=d)) for d in range(731)]  # 2024 leap year
date_weights = [MONTH_FACTOR[d.month] for d in days]

booking_rows = []
for i in range(1, 120001):
    d = random.choices(days, weights=date_weights)[0]
    branch = random.choices([b for _, b, _ in BRANCHES],
                            weights=[w for _, _, w in BRANCHES])[0]
    svc = random.choices(SERVICES, weights=SERVICE_WEIGHTS)[0]
    service_id, service_name, category, price, _dur = svc
    cust_idx = random.randrange(15000)
    status = random.choices(["Completed", "Cancelled", "No-show"],
                            weights=[93, 4, 3])[0]
    if status == "Completed":
        amount = price
        if random.random() < 0.10:  # add-on
            amount += random.choice([199, 299, 499])
        payment = random.choices(["UPI", "Cash", "Card"], weights=[45, 35, 20])[0]
    else:
        amount, payment = 0, ""
    booking_rows.append([
        f"B{i:06d}", d.isoformat(), branch,
        f"C{cust_idx + 1:05d}", service_id, service_name,
        random.choice(staff_by_branch[branch]), status, amount, payment,
    ])
write_csv(DATA / "large_bookings.csv",
          ["booking_id", "booking_date", "branch", "customer_id", "service_id",
           "service_name", "staff_id", "status", "amount_inr", "payment_mode"],
          booking_rows)

# --- expenses: 2,400 rows, ~33 per branch-month ---
exp_rows, eid = [], 1
rent = {"Anand": 45000, "Vallabh Vidyanagar": 40000, "Ahmedabad": 65000}
for y in (2024, 2025):
    for m in range(1, 13):
        for _, branch, _ in BRANCHES:
            exp_rows.append([f"E{eid:05d}", f"{y}-{m:02d}-01", branch, "Rent", rent[branch]]); eid += 1
            exp_rows.append([f"E{eid:05d}", f"{y}-{m:02d}-05", branch, "Salary", random.randint(180000, 240000)]); eid += 1
            exp_rows.append([f"E{eid:05d}", f"{y}-{m:02d}-10", branch, "Utilities", random.randint(8000, 15000)]); eid += 1
            exp_rows.append([f"E{eid:05d}", f"{y}-{m:02d}-15", branch, "Marketing", random.randint(5000, 20000)]); eid += 1
            for _ in range(random.randint(24, 30)):  # consumables etc.
                cat = random.choices(["Consumables", "Consumables", "Consumables", "Maintenance"],
                                     weights=[70, 0, 0, 30])[0] if False else random.choice(
                    ["Consumables", "Consumables", "Consumables", "Maintenance"])
                exp_rows.append([f"E{eid:05d}", f"{y}-{m:02d}-{random.randint(1,28):02d}",
                                 branch, cat, random.randint(500, 8000)]); eid += 1
# Trim / pad to exactly 2400 for a clean spec
exp_rows = exp_rows[:2400]
while len(exp_rows) < 2400:
    exp_rows.append([f"E{eid:05d}", "2025-12-20", "Anand", "Consumables", random.randint(500, 3000)]); eid += 1
write_csv(DATA / "large_expenses.csv",
          ["expense_id", "expense_date", "branch", "category", "amount_inr"], exp_rows)

print("Done. Totals are checked in analyse_large_data.py")
