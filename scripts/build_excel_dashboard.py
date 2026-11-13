#!/usr/bin/env python3
"""Build Shree_Car_Care_Large_Dashboard.xlsx from output/*.csv
Run: python3 scripts/build_excel_dashboard.py
KPIs on Dashboard are formulas pointing at the summary sheets, not pasted values.
Charts link to the summary tables. Design: plain, readable, no gradients."""
import pandas as pd
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
OUT, EXCEL = ROOT / "output", ROOT / "excel"
EXCEL.mkdir(parents=True, exist_ok=True)

monthly = pd.read_csv(OUT / "summary_monthly_by_branch.csv")
by_svc = pd.read_csv(OUT / "summary_by_service.csv")
by_branch = pd.read_csv(OUT / "summary_by_branch.csv")
top = pd.read_csv(OUT / "top_customers.csv")
pay = pd.read_csv(OUT / "payment_split.csv")

# Monthly pivot: one row per month, revenue per branch
piv = monthly.pivot(index="month", columns="branch", values="revenue").reset_index()
piv["Total Revenue"] = piv[["Ahmedabad", "Anand", "Vallabh Vidyanagar"]].sum(axis=1)
book_m = monthly.groupby("month")["bookings"].sum().rename("Bookings")
exp_m = monthly.groupby("month")["expenses"].sum().rename("Expenses")
piv = piv.merge(book_m, on="month").merge(exp_m, on="month")
piv["Net Cash"] = piv["Total Revenue"] - piv["Expenses"]

wb = Workbook()
NAVY = "1F3864"; LIGHT = "D9E2F3"; GREY = "F2F2F2"
title_font = Font(name="Calibri", size=16, bold=True, color=NAVY)
head_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
head_fill = PatternFill("solid", fgColor=NAVY)
thin = Side(style="thin", color="BFBFBF")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

def write_table(ws, df, start_row=1):
    for j, col in enumerate(df.columns, 1):
        c = ws.cell(row=start_row, column=j, value=col)
        c.font, c.fill, c.border = head_font, head_fill, border
    for i, row in enumerate(df.itertuples(index=False), start_row + 1):
        for j, v in enumerate(row, 1):
            c = ws.cell(row=i, column=j, value=v)
            c.border = border
            if isinstance(v, (int, float)) and j > 1:
                c.number_format = '#,##0'
    for j, col in enumerate(df.columns, 1):
        ws.column_dimensions[get_column_letter(j)].width = max(14, min(28, len(str(col)) + 4))

# --- Monthly sheet ---
ws = wb.active; ws.title = "Monthly"
write_table(ws, piv)
n_m = len(piv) + 1  # last data row
ws.cell(row=n_m + 2, column=1, value="Total").font = Font(bold=True)
for col in range(2, len(piv.columns) + 1):
    letter = get_column_letter(col)
    ws.cell(row=n_m + 2, column=col, value=f"=SUM({letter}2:{letter}{n_m})").font = Font(bold=True)
    ws.cell(row=n_m + 2, column=col).number_format = '#,##0'

# --- By Service ---
ws2 = wb.create_sheet("By Service")
write_table(ws2, by_svc[["service_name", "category", "bookings", "revenue", "avg_bill"]])
n_s = len(by_svc) + 1
ws2.cell(row=n_s + 2, column=1, value="Total").font = Font(bold=True)
ws2.cell(row=n_s + 2, column=3, value=f"=SUM(C2:C{n_s})").font = Font(bold=True)
ws2.cell(row=n_s + 2, column=4, value=f"=SUM(D2:D{n_s})").font = Font(bold=True)

# --- By Branch ---
ws3 = wb.create_sheet("By Branch")
write_table(ws3, by_branch)
ws3.cell(row=5, column=1, value="Total").font = Font(bold=True)
ws3.cell(row=5, column=2, value="=SUM(B2:B4)").font = Font(bold=True)
ws3.cell(row=5, column=3, value="=SUM(C2:C4)").font = Font(bold=True)

# --- Top Customers ---
ws4 = wb.create_sheet("Top Customers")
write_table(ws4, top[["customer_id", "customer_name", "home_branch", "bookings", "revenue"]])

# --- Payment ---
ws5 = wb.create_sheet("Payment")
write_table(ws5, pay)

# --- Dashboard (insert first) ---
dash = wb.create_sheet("Dashboard", 0)
dash["A1"] = "Shree Car Care — Large Data Dashboard"
dash["A1"].font = title_font
dash["A2"] = "3 branches: Anand, Vallabh Vidyanagar, Ahmedabad  |  Jan 2024 – Dec 2025  |  Sample data, 120,000 bookings"
dash["A2"].font = Font(size=11, italic=True, color="595959")
dash["A4"] = "KPI"
dash["B4"] = "Value"
for c in ("A4", "B4"):
    dash[c].font, dash[c].fill = head_font, head_fill
# Monthly totals row is n_m+2 on Monthly sheet; revenue col E, bookings col F, expenses col G
kpis = [
    ("Total bookings", f"='Monthly'!F{n_m + 2}"),
    ("Total revenue (Rs)", f"='Monthly'!E{n_m + 2}"),
    ("Total expenses (Rs)", f"='Monthly'!G{n_m + 2}"),
    ("Net cash (Rs)", "=B6-B7"),
    ("Average bill (Rs)", "=B6/B10"),  # total revenue / completed bookings
    ("Completed bookings", "='By Service'!C15"),  # By Service total row is 15
]
# Fix average bill: use total revenue / completed bookings from By Service total (row 14 = total row)
for i, (label, formula) in enumerate(kpis):
    r = 5 + i
    dash.cell(row=r, column=1, value=label).font = Font(bold=True)
    c = dash.cell(row=r, column=2, value=formula)
    c.number_format = '#,##0.00' if "bill" in label.lower() else '#,##0'
dash["A11"] = "Note: Average bill = total revenue / completed bookings (111,592). Revenue, expenses and net cash are formulas from the Monthly sheet, so they update if you change the summary tables."
dash["A11"].font = Font(size=10, italic=True, color="595959")
dash["A11"].alignment = Alignment(wrap_text=True, vertical="top")
dash.merge_cells("A11:B11")
dash.column_dimensions["A"].width = 28
dash.column_dimensions["B"].width = 22
dash["A13"] = "Monthly total revenue — see Monthly sheet for the table"
dash["A13"].font = Font(bold=True)

# Charts on Dashboard, linked to Monthly / By Service
lc = LineChart(); lc.title = "Monthly total revenue (Rs)"; lc.style = 2
lc.y_axis.title, lc.x_axis.title = "Revenue", "Month"
lc.add_data(Reference(ws, min_col=5, min_row=1, max_row=n_m), titles_from_data=True)
lc.set_categories(Reference(ws, min_col=1, min_row=2, max_row=n_m))
lc.width, lc.height = 24, 9
dash.add_chart(lc, "A15")

bc = BarChart(); bc.type = "col"; bc.title = "Revenue by service"; bc.style = 10
bc.y_axis.title = "Revenue (Rs)"
bc.add_data(Reference(ws2, min_col=4, min_row=1, max_row=n_s), titles_from_data=True)
bc.set_categories(Reference(ws2, min_col=1, min_row=2, max_row=n_s))
bc.width, bc.height = 24, 9
dash.add_chart(bc, "A32")

# --- Data notes ---
ws6 = wb.create_sheet("Data notes")
notes = [
    ["What this is", "Sample data for a fictional 3-branch detailing chain, Shree Car Care. All names, phones and plates are made up."],
    ["Size", "120,000 bookings, 15,000 customers, 12 services, 2,400 expenses, 24 staff, Jan 2024-Dec 2025."],
    ["How it was made", "scripts/generate_large_data.py, seed 42, stdlib only. Re-run it to regenerate the same data."],
    ["Seasonality", "Oct-Nov festive months are busier, Jun-Jul monsoon months are quieter. Ahmedabad is the largest branch."],
    ["Repeat customers", "99.7% of customers who booked have 2+ bookings. That is a direct result of 120,000 bookings across 15,000 customers (about 8 each) - it is not a claim about a real business."],
    ["Revenue skew", "Coating and PPF are a small share of bookings but a large share of revenue, because they cost Rs 10,000-25,000. Wash is the volume driver."],
    ["What is not here", "No .pbix file - build that in Power BI Desktop using powerbi/docs/powerbi_large_model.md. No real customer data."],
    ["Formulas", "Dashboard KPIs are Excel formulas from the Monthly and By Service sheets, not pasted values."],
]
for i, (a, b) in enumerate(notes, 1):
    ws6.cell(row=i, column=1, value=a).font = Font(bold=True)
    ws6.cell(row=i, column=2, value=b).alignment = Alignment(wrap_text=True, vertical="top")
ws6.column_dimensions["A"].width = 22
ws6.column_dimensions["B"].width = 110

wb.save(EXCEL / "Shree_Car_Care_Large_Dashboard.xlsx")
print(f"Saved excel/Shree_Car_Care_Large_Dashboard.xlsx, {len(wb.sheetnames)} sheets: {wb.sheetnames}")
print(f"Monthly rows: {len(piv)}, total revenue check: {piv['Total Revenue'].sum():,}")
