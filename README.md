# Shree Car Care — Large Data Dashboard

I built this to show I can work with lakh-scale data, not just a small sample file.

The business is fictional — Shree Car Care, a detailing chain with 3 branches:
Anand, Vallabh Vidyanagar, and Ahmedabad. All the data is sample data I made
up for this project. No real customers, no real business, no invented results.

## How big is it

- **120,000 bookings**, Jan 2024 to Dec 2025 (2 years)
- **14,996 distinct customers booked** (15,000 customers in the file, 4 never booked)
- **12 services**, **24 staff**, **2,400 expenses**
- Total revenue (completed bookings only): **Rs 21,45,24,819**
- Total expenses: **Rs 2,88,37,815**
- Net cash: **Rs 18,56,87,004**

The headline numbers are in `output/kpis.txt`. I checked them three ways —
from the generator, from the analysis script, and from the Excel workbook —
they match.

A few things that are true about this data, and worth saying plainly:
- Cancellation is 4.01%, no-show is 2.99% — I set those in the generator on purpose.
- Oct-Nov are the busiest months (festive season), June-July are the quietest (monsoon).
- Ahmedabad is the biggest branch, Vallabh Vidyanagar the smallest.
- Coating and PPF are a small share of bookings but a big share of revenue,
  because they cost Rs 10,000-25,000. Wash is the volume driver.
- Repeat customers are 99.7%. That sounds too high until you do the maths:
  120,000 bookings across 15,000 customers is about 8 bookings each, so
  almost everyone comes back. It is a property of this sample, not a claim
  about a real business.
- Year-on-year revenue growth is only 0.70%. The chain is flat in this sample.
  I left that in, instead of making the data look like a success story.

## What is in here

```
large-data-dashboard/
  README.md
  scripts/
    generate_large_data.py      # makes all the CSVs, seed 42, stdlib only
    analyse_large_data.py       # pandas, writes the output/ summaries
    build_excel_dashboard.py    # openpyxl, builds the Excel workbook
  data/
    large_bookings_2024.csv     # 60,251 rows (split by year on GitHub)
    large_bookings_2025.csv     # 59,749 rows (split by year on GitHub)
    large_customers.csv         # 15,000 rows
    large_services.csv          # 12 rows
    large_expenses.csv          # 2,400 rows
    large_staff.csv             # 24 rows
  output/
    summary_monthly_by_branch.csv
    summary_by_service.csv
    summary_by_branch.csv
    top_customers.csv
    payment_split.csv
    kpis.txt
  excel/
    Shree_Car_Care_Large_Dashboard.xlsx
  powerbi/
    docs/powerbi_large_model.md # star schema, DAX, 5 pages, performance notes
```

## How to re-run it

```bash
cd large-data-dashboard
python3 scripts/generate_large_data.py
python3 scripts/analyse_large_data.py
python3 scripts/build_excel_dashboard.py
```

The generator needs only the Python standard library. The analysis script
uses pandas, the Excel builder uses openpyxl. Run the generator twice and
you get the same files both times — seed 42, deterministic.

## How to open the Excel dashboard

Open `excel/Shree_Car_Care_Large_Dashboard.xlsx`.

- **Dashboard** — KPIs, monthly revenue line chart, revenue by service chart.
  The KPIs are Excel formulas from the Monthly and By Service sheets, not
  pasted values, so they update if you change the summary tables.
- **Monthly** — one row per month, revenue by branch, bookings, expenses, net cash.
- **By Service** — bookings and revenue by service.
- **By Branch** — the 3 branches side by side.
- **Top Customers** — top 20 by revenue.
- **Payment** — UPI / Cash / Card split.
- **Data notes** — what the data is, and what is not in here.

## How to build the Power BI version

There is no `.pbix` in this repo — I do not have Power BI Desktop here.
Follow `powerbi/docs/powerbi_large_model.md`: load the 5 CSVs, set up the
star schema, write the DAX measures in a Measures table, and build the
5 pages (Owner overview, Branch comparison, Services, Customers, Cash & expenses).
Check every measure against `output/kpis.txt` as you go. It also has
performance notes for 120k rows — import mode, a proper date table, and
no row-level visuals.

## What I would do next for a real client

Replace the sample CSVs with the client's real export, keep the same
columns, and re-run the same scripts. The cleaning rules are in the
generator and analysis scripts, so the work is repeatable, not a one-off
dashboard I made by hand.

## Note on the bookings file on GitHub

Locally this project has one file, `data/large_bookings.csv` (120,000 rows).
GitHub's upload limit for a single file push meant it is stored here split by
year instead: `data/large_bookings_2024.csv` (60,251 rows) and
`data/large_bookings_2025.csv` (59,749 rows). Together they are the same
120,000 rows, same columns, same order. To rebuild the single file, stack the
two files and keep one header row.

The Excel workbook is now in `excel/Shree_Car_Care_Large_Dashboard.xlsx`.
