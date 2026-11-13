# Power BI model — Shree Car Care, lakh-scale data

Sample data only. 120,000 bookings, 15,000 customers, 3 branches, Jan 2024–Dec 2025.
No `.pbix` here — Power BI Desktop is not available in this workspace. Build it from
this doc in under 2 hours. All file paths are relative to the project root.

## Files to load

| File | Rows | Role |
|---|---|---|
| data/large_bookings.csv | 120,000 | Fact |
| data/large_customers.csv | 15,000 | Dimension |
| data/large_services.csv | 12 | Dimension |
| data/large_expenses.csv | 2,400 | Fact |
| data/large_staff.csv | 24 | Dimension |
| output/summary_monthly_by_branch.csv | 72 | Check totals against this |

## Star schema

```
dim_date (build in Power BI: Calendar table, 2024-01-01 to 2025-12-31)
    1 ---- *  fact_bookings
    1 ---- *  fact_expenses
dim_customer (customer_id)  1 ---- *  fact_bookings
dim_service  (service_id)   1 ---- *  fact_bookings
dim_staff    (staff_id)     1 ---- *  fact_bookings
dim_branch   (branch, from a small table: Anand / Vallabh Vidyanagar / Ahmedabad)
```

Relationships, all single direction, fact on the many side:
- fact_bookings[booking_date] → dim_date[Date]
- fact_bookings[customer_id] → dim_customer[customer_id]
- fact_bookings[service_id] → dim_service[service_id]
- fact_bookings[staff_id] → dim_staff[staff_id]
- fact_expenses[expense_date] → dim_date[Date]
- Branch is a text column on both fact tables; use a dim_branch table if you
  want branch slicers to filter both facts at once, otherwise filter each fact
  separately and say so on the page.

Cleaning in Power Query (do it once, document it):
- booking_date / expense_date → Date type, no time.
- amount_inr → Whole Number. Cancelled / No-show rows have amount 0 — keep them,
  do not delete them, because cancellation rate is a KPI.
- phone: leave blanks blank. Do not fill with 99999 numbers.
- service_name: keep as in the file; the generator already standardised it.

## DAX measures

Put all measures in a separate Measures table. Do not scatter them in visuals.

```dax
Total Revenue = SUM(fact_bookings[amount_inr])
Total Bookings = COUNTROWS(fact_bookings)
Completed Bookings = CALCULATE(COUNTROWS(fact_bookings), fact_bookings[status] = "Completed")
Cancellation % = DIVIDE(
    CALCULATE(COUNTROWS(fact_bookings), fact_bookings[status] = "Cancelled"),
    [Total Bookings])
No-show % = DIVIDE(
    CALCULATE(COUNTROWS(fact_bookings), fact_bookings[status] = "No-show"),
    [Total Bookings])
Avg Bill = DIVIDE([Total Revenue], [Completed Bookings])
Total Expenses = SUM(fact_expenses[amount_inr])
Net Cash = [Total Revenue] - [Total Expenses]
Repeat Customers = COUNTROWS(FILTER(
    SUMMARIZE(fact_bookings, dim_customer[customer_id], "n", COUNTROWS(fact_bookings)),
    [n] >= 2))
Repeat % = DIVIDE([Repeat Customers], DISTINCTCOUNT(fact_bookings[customer_id]))

Revenue PY = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(dim_date[Date]))
YoY Growth % = DIVIDE([Total Revenue] - [Revenue PY], [Revenue PY])
Revenue YTD = TOTALYTD([Total Revenue], dim_date[Date])
Revenue MTD = TOTALMTD([Total Revenue], dim_date[Date])
```

Expected results (check against output/kpis.txt after you build it):
- Total Revenue: Rs 214,524,819 — Completed only, because cancelled/no-show are Rs 0
- Total Bookings: 120,000 — Completed 111,592, Cancelled 4,818 (4.01%), No-show 3,590 (2.99%)
- Avg Bill: Rs 1,922.40
- Total Expenses: Rs 28,837,815 — Net Cash: Rs 185,687,004
- YoY growth 2025 vs 2024: 0.70% — the chain is flat year-on-year in this sample,
  which is itself a finding: growth came from Oct-Nov festive months, not from
  a rising trend. Say that on the page, do not smooth it away.
- Repeat %: 99.7% of customers who booked have 2+ bookings. This is a direct
  result of 120,000 bookings across 15,000 customers (about 8 each). Report it
  with that note, not as a claim about a real business.

## 5 pages

**1. Owner overview**
KPIs: revenue, bookings, avg bill, cancellation %, net cash, YoY growth.
Monthly revenue trend (line), revenue by branch (bar), top 5 services.
One-line takeaway at the top, e.g. "Oct-Nov are your best months; June-July are the weakest."

**2. Branch comparison**
Revenue, bookings and avg bill by branch, side by side. Monthly trend per branch
(small multiples or three lines). Ahmedabad is the largest branch in this sample,
Vallabh Vidyanagar the smallest — check it in output/summary_by_branch.csv.

**3. Services**
Revenue and bookings by service and by category. Note the skew: coating and PPF
are a small share of bookings but a large share of revenue; wash is the volume driver.

**4. Customers**
Repeat %, top 20 customers by revenue (output/top_customers.csv), bookings by
source (Walk-in / Instagram / Referral / Google), customers by home branch.
Do not show phone numbers on a shared report.

**5. Cash & expenses**
Revenue vs expenses by month, expenses by category, payment split (UPI / Cash / Card),
net cash by month. Expenses are lumpy — rent and salary are fixed monthly, consumables
vary — so show the monthly table, not just a total.

## Performance notes for lakh-scale data

- Use **Import mode**, not DirectQuery, for 120k rows. It is fast enough and
  lets you use all DAX.
- Build a proper dim_date table. Do not use the booking_date column directly
  in time-intelligence measures.
- Keep the model thin: drop the phone column from the report view if you do
  not need it, and do not import the notes column (there is none in these CSVs —
  that is deliberate, keep it that way).
- Avoid row-level visuals: do not put 120,000 rows in a table visual. Aggregate
  first, then show the top 20 / top 50.
- Use measures, not calculated columns, for revenue, rates and growth.
  A calculated column on 120k rows is fine, but a measure is cheaper and
  responds to slicers.
- If the file gets slow, use aggregations: a monthly summary table
  (output/summary_monthly_by_branch.csv) as an aggregation table for the
  overview page, with detail only on drill-through.
- Refresh: the CSVs are static sample data. In a real client build, replace
  them with the client's export and re-run the same Power Query steps.

## Build order

1. Load the 5 CSVs, set types, build dim_date.
2. Set relationships as above, check the model view.
3. Write the measures in the Measures table, check each against output/kpis.txt.
4. Build page 1, get the layout right, copy the style to pages 2–5.
5. Add slicers: date range, branch, service category, payment mode.
6. Test: filter to Oct 2025, check totals; filter to one branch, check all
   visuals update; check YoY on the overview page.
7. Export a PDF and take screenshots for the portfolio.
