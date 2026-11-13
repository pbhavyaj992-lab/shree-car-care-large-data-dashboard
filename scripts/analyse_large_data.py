#!/usr/bin/env python3
"""Analyse the lakh-scale Shree Car Care data. Run from the project root:
    python3 scripts/analyse_large_data.py
Reads data/*.csv, writes output/*.csv and output/kpis.txt
Uses pandas if available, otherwise plain csv (pandas is expected here)."""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT = ROOT / "data", ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)

b = pd.read_csv(DATA / "large_bookings.csv", parse_dates=["booking_date"])
c = pd.read_csv(DATA / "large_customers.csv")
s = pd.read_csv(DATA / "large_services.csv")
e = pd.read_csv(DATA / "large_expenses.csv", parse_dates=["expense_date"])
comp = b[b["status"] == "Completed"]

# --- monthly by branch ---
b["month"] = b["booking_date"].dt.to_period("M").astype(str)
monthly = (b.groupby(["month", "branch"])
           .agg(bookings=("booking_id", "count"),
                completed=("status", lambda x: (x == "Completed").sum()),
                revenue=("amount_inr", "sum"))
           .reset_index())
exp_m = e.assign(month=e["expense_date"].dt.to_period("M").astype(str))
exp_m = exp_m.groupby(["month", "branch"])["amount_inr"].sum().rename("expenses").reset_index()
monthly = monthly.merge(exp_m, on=["month", "branch"], how="left").fillna({"expenses": 0})
monthly["net_cash"] = monthly["revenue"] - monthly["expenses"]
monthly = monthly.sort_values(["month", "branch"])
monthly.to_csv(OUT / "summary_monthly_by_branch.csv", index=False)

# --- by service ---
by_svc = (comp.groupby(["service_id", "service_name"])
          .agg(bookings=("booking_id", "count"), revenue=("amount_inr", "sum"))
          .reset_index())
by_svc = by_svc.merge(s[["service_id", "category", "base_price_inr"]], on="service_id")
by_svc["avg_bill"] = (by_svc["revenue"] / by_svc["bookings"]).round(2)
by_svc = by_svc.sort_values("revenue", ascending=False)
by_svc.to_csv(OUT / "summary_by_service.csv", index=False)

# --- by branch, top customers, payment ---
by_branch = (comp.groupby("branch")
             .agg(bookings=("booking_id", "count"), revenue=("amount_inr", "sum"))
             .reset_index())
by_branch.to_csv(OUT / "summary_by_branch.csv", index=False)

top = (comp.groupby("customer_id")
       .agg(bookings=("booking_id", "count"), revenue=("amount_inr", "sum"))
       .sort_values("revenue", ascending=False).head(20).reset_index())
top = top.merge(c[["customer_id", "customer_name", "home_branch"]], on="customer_id")
top.to_csv(OUT / "top_customers.csv", index=False)

pay = comp["payment_mode"].value_counts().rename_axis("payment_mode").reset_index(name="bookings")
pay["revenue"] = comp.groupby("payment_mode")["amount_inr"].sum().values
pay.to_csv(OUT / "payment_split.csv", index=False)

# --- KPIs ---
total_rev = int(comp["amount_inr"].sum())
total_exp = int(e["amount_inr"].sum())
n_cust = b["customer_id"].nunique()
repeat = int((b.groupby("customer_id").size() >= 2).sum())
kpis = [
    f"Total bookings: {len(b):,}",
    f"Completed: {(b['status'] == 'Completed').sum():,}  Cancelled: {(b['status'] == 'Cancelled').sum():,}  No-show: {(b['status'] == 'No-show').sum():,}",
    f"Cancellation rate: {(b['status'] == 'Cancelled').mean() * 100:.2f}%",
    f"No-show rate: {(b['status'] == 'No-show').mean() * 100:.2f}%",
    f"Total revenue (completed only): Rs {total_rev:,}",
    f"Total expenses: Rs {total_exp:,}",
    f"Net cash (revenue - expenses): Rs {total_rev - total_exp:,}",
    f"Average bill (completed): Rs {comp['amount_inr'].mean():.2f}",
    f"Distinct customers booked: {n_cust:,}",
    f"Repeat customers (2+ bookings): {repeat:,} ({repeat / n_cust * 100:.1f}% of customers who booked)",
    f"Date range: {b['booking_date'].min().date()} to {b['booking_date'].max().date()}",
    f"Revenue 2024: Rs {int(comp[comp['booking_date'].dt.year == 2024]['amount_inr'].sum()):,}",
    f"Revenue 2025: Rs {int(comp[comp['booking_date'].dt.year == 2025]['amount_inr'].sum()):,}",
    f"YoY revenue growth 2025 vs 2024: {(comp[comp['booking_date'].dt.year == 2025]['amount_inr'].sum() / comp[comp['booking_date'].dt.year == 2024]['amount_inr'].sum() - 1) * 100:.2f}%",
]
(OUT / "kpis.txt").write_text("\n".join(kpis) + "\n", encoding="utf-8")
print("\n".join(kpis))
print("\nWrote output/*.csv and output/kpis.txt")
