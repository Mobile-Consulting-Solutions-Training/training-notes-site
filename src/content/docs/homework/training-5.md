---
title: Training 5 Homework
description: "Data warehousing: facts/dimensions, grain, surrogate keys, SCD types, star vs. snowflake, and a bronze-to-gold load walkthrough"
---

## Homework

# Data Warehousing Homework — 10 Questions

**Setup used for verification:** the star schema built earlier in `warehouse_practice` (see [Training 5](/training-notes-site/notes/training-5/)'s "Worked Example: Converting `bd_sql_training` into a Star Schema") was moved into a `gold` schema (`gold.fact_sales`, `gold.dim_product`, `gold.dim_date`, `gold.dim_customer`, `gold.dim_employee`, `gold.dim_office`) so the SQL below runs against real, live tables rather than being purely descriptive.

---

## 1. Facts and Dimensions

A **fact table** stores measurable events - numeric measures (quantity, price, revenue) plus Foreign Keys pointing out to the dimensions that describe each event. A **dimension table** stores descriptive, mostly-text context about those events (who, what, where, when) and is what a fact table's Foreign Keys reference. The fact table answers "what happened and how much," while dimension tables answer "who/what/where was involved."

From our warehouse:
- **Fact table:** `gold.fact_sales`
- **Dimension tables:** `gold.dim_product`, `gold.dim_date` (also `gold.dim_customer`, `gold.dim_employee`, `gold.dim_office` exist, though currently unlinked to the fact table since the source data never captured which customer/employee made each sale)

---

## 2. Grain

The grain of `gold.fact_sales` is **one row per product line item on an order** - i.e., one row for each distinct product sold within a single order (`order_number` + `product_number` together identify a row).

**Why deciding grain first matters:** every measure and every Foreign Key in a fact table only makes sense relative to its grain. If the grain isn't nailed down before designing the table, you get ambiguous or double-counted results - e.g., trying to add an "order-level shipping cost" measure to a line-item-grain fact table would either repeat that cost once per line item (over-counting it in a `SUM`) or require an awkward workaround. Every fact table should have exactly one clearly stated grain, and every dimension/measure added later must respect it.

---

## 3. Querying a Star Schema

```sql
SELECT
    p.product_category,
    d.year,
    SUM(f.sales_amount) AS total_sales
FROM gold.fact_sales f
JOIN gold.dim_product p ON f.product_number = p.product_number
JOIN gold.dim_date d ON f.order_date_key = d.date_key
GROUP BY p.product_category, d.year
ORDER BY d.year, total_sales DESC;
```

**Verified output (first few rows, run against `warehouse_practice`):**
```
product_category | year | total_sales
------------------+------+-------------
Classic Cars      | 2003 |  1374832.22
Vintage Cars      | 2003 |   619161.48
Trucks and Buses  | 2003 |   376657.12
Motorcycles       | 2003 |   348909.24
...
Classic Cars      | 2004 |  1763136.73
...
```

---

## 4. Surrogate Keys

A **surrogate key** is an artificial, warehouse-generated identifier (typically an auto-incrementing integer, e.g. `product_key`) assigned to a dimension row - used *instead of* the natural/business key the source system already provides (e.g. `product_number`).

**One reason to use a surrogate key even when a natural key exists:** it enables tracking history (SCD Type 2, see Q6) - a natural key like `product_number` can only exist once per real-world product, so there's no way to have two rows both legitimately represent "this product, at two different points in time." A surrogate key lets each historical version get its own row/key while all of them still share the same underlying `product_number`.

---

## 5. SCD Type 1

Under **SCD Type 1**, the change is handled by **overwriting the existing row in place** - the `product_category` value on that product's row in `dim_product` is updated directly from `Electronics` to `Computer Electronics`.

```sql
UPDATE dim_product
SET product_category = 'Computer Electronics'
WHERE product_number = '<the product in question>';
```

**What happens to the old value:** it's gone - **no history is kept**. Any report re-run after this update, even one covering past dates, will show `Computer Electronics` for that product retroactively, since there's only ever one row and it's been overwritten. This is appropriate when the old value was simply wrong (a correction), not when the business genuinely wants to preserve what was true at different points in time.

---

## 6. SCD Type 2

Under **SCD Type 2**, the customer's move isn't an overwrite - a **new row is inserted** for that customer with the updated city (`Miami`), while the **old row is kept** and marked as no longer current. Both rows share the same natural/business key (`customer_id`) but have different surrogate keys.

**Additional columns needed on `dim_customer`:**
```sql
ALTER TABLE dim_customer ADD COLUMN effective_date DATE;
ALTER TABLE dim_customer ADD COLUMN end_date DATE;
ALTER TABLE dim_customer ADD COLUMN is_current BOOLEAN;
```
- `effective_date` / `end_date` - the date range during which that row's version of the customer's data was true
- `is_current` - a quick flag for "give me the customer's current state" without having to reason about date ranges

**How the report still shows New York for past years:** a `fact_sales` row for an old sale was linked (at load time) to the surrogate key of the *New York* version of that customer row. That link never changes - it's baked into the fact row - so joining old fact rows to `dim_customer` always resolves back to the New York version, even after a new "Miami" row has been added for the customer's current state.

---

## 7. Star vs. Snowflake Schema

A **star schema** keeps every dimension table flat/denormalized - each dimension connects directly to the fact table via a single Foreign Key, giving the fewest possible joins per query. A **snowflake schema** normalizes some dimensions further, splitting them into multiple related sub-tables - those sub-tables connect to *other dimension tables* instead of connecting to the fact table directly, reducing redundancy at the cost of more joins per query.

**Example - normalizing `gold.dim_product` into a snowflake shape:**

`dim_product` currently holds `product_number`, `product_name`, `product_category`, `product_scale`, `product_manufacturer`, `product_description`, `length`, `width`, `height` all flattened into one table - meaning `product_category` and `product_manufacturer` repeat across every product that shares them. To snowflake this:

```sql
CREATE TABLE dim_product_category (
    category_key SERIAL PRIMARY KEY,
    product_category VARCHAR(100) UNIQUE
);

CREATE TABLE dim_manufacturer (
    manufacturer_key SERIAL PRIMARY KEY,
    product_manufacturer VARCHAR(255) UNIQUE
);

ALTER TABLE dim_product
    ADD COLUMN category_key INTEGER REFERENCES dim_product_category(category_key),
    ADD COLUMN manufacturer_key INTEGER REFERENCES dim_manufacturer(manufacturer_key);
-- drop the now-redundant text columns, populate the two new sub-tables and FKs
```
Now `dim_product` connects out to `dim_product_category` and `dim_manufacturer` instead of repeating that text on every row - the classic star-to-snowflake trade-off (less redundancy, more joins to get a product's full descriptive text).

---

## 8. Medallion Architecture

| Layer | Purpose | Example from our PostgreSQL/Pandas exercise |
|---|---|---|
| **Bronze** | Raw dumping ground - land data as-is, with little to no cleaning or rules | The raw `customers`/`employees`/`offices`/`orders`/`orderdetails`/`payments`/`products` CSVs loaded straight into `bd_sql_training`, including the still-present data-quality bug where `orderdetails.product_category` actually held quantity data, not a real category |
| **Silver** | Cleaned, conformed data - fix data quality issues, apply a common structure across sources | Renaming raw tables into their proper roles and fixing the mislabeled `product_category`/`quantity` columns during the `warehouse_practice` conversion (see [Training 5](/training-notes-site/notes/training-5/)'s Worked Example) |
| **Gold** | Business-ready data, shaped for direct analytical use | The finished `gold.fact_sales`/`gold.dim_product`/`gold.dim_date` star schema, verified with the real category-and-year revenue query in Q3 above |

---

## 9. Bronze → Silver with Pandas

```python
import pandas as pd

bronze = pd.DataFrame({
    "transaction_id": ["T101", "T102", "T103", "T104"],
    "category":       ["electronics", "ELECTRONICS", "Furniture", "electronics"],
    "quantity":       [2, 3, -2, 1],
    "unit_price":     [50.00, 75.00, 200.00, "INVALID"],
})

silver = bronze.copy()

# Standardize category (case-insensitive, trimmed)
silver["category"] = silver["category"].str.strip().str.title()

# Convert quantity/unit_price to numeric, invalid values -> NaN
silver["quantity"] = pd.to_numeric(silver["quantity"], errors="coerce")
silver["unit_price"] = pd.to_numeric(silver["unit_price"], errors="coerce")

# Remove rows where quantity or price is invalid (NaN)
silver = silver.dropna(subset=["quantity", "unit_price"])

# Remove rows where quantity is 0 or negative
silver = silver[silver["quantity"] > 0]

# Derived measure
silver["sales_amount"] = silver["quantity"] * silver["unit_price"]
```

**Verified result** (run against the exact sample data given):
```
  transaction_id     category  quantity  unit_price  sales_amount
0           T101  Electronics       2        50.0         100.0
1           T102  Electronics       3        75.0         225.0
```
- `T101`/`T102` survive - category standardized to `Electronics` regardless of original casing.
- `T103` dropped - negative quantity (`-2`).
- `T104` dropped - `unit_price = "INVALID"` becomes `NaN` after `pd.to_numeric(..., errors="coerce")`, then removed by the `dropna`.

---

## 10. Silver → Gold Warehouse Load

Loading the new Silver record (`T500`, `Laptop`, `Electronics`, 2 units @ $900.00, `sales_amount = 1800.00`) into the Gold star schema:

1. **Look up or add the product dimension member.** Check `gold.dim_product` for a row matching the incoming product (by its natural key, e.g. `product_number`/product name `Laptop`). If it already exists, reuse its surrogate key. If it doesn't exist yet, insert a new `dim_product` row (this is effectively an SCD Type 1 or Type 2 "new member" insert, not a change to an existing member) and get back the newly generated surrogate key.

2. **Look up the appropriate date in `dim_date`.** Convert `transaction_date = 2026-09-15` into the date dimension's key format (e.g. `20260915`) and look up the matching row in `gold.dim_date` to get its `date_key`. If `dim_date` was pre-populated for a fixed date range and this date falls outside it, the date dimension needs to be extended first (this is a common real-world gap when a date range was generated once and the warehouse keeps receiving new data past that range).

3. **Resolve the appropriate keys.** Now that both lookups are done, the load process has the surrogate `product_key` (from step 1) and `date_key` (from step 2) needed to build the fact row. If any other dimensions (customer, employee) are part of this fact table's grain, the same lookup-or-add pattern would apply to them too.

4. **Construct the `fact_sales` record.** Insert a new row into `gold.fact_sales` with: the resolved `product_key`/`date_key` (Foreign Keys), plus the measures directly from the Silver record - `quantity = 2`, `price = 900.00`, `sales_amount = 1800.00`.

5. **If required Gold-schema information is missing from the incoming batch:** don't silently drop or guess it. Standard options, in order of preference:
   - Reject/quarantine the record into a dead-letter/error table for manual review, if the missing piece is essential (e.g. no way to resolve the date at all).
   - Load it with an explicit "Unknown"/placeholder dimension member (a common pattern: a `dim_product` row with `product_key = -1` reserved for "unknown product") so the fact table doesn't get an orphaned or NULL Foreign Key, while still flagging that the record was incomplete.
   - Log/alert on the gap so it gets investigated and fixed at the source, rather than silently accepting bad data into Gold - directly related to the error-handling and data-quality-validation concepts from `Training 0.md`.
