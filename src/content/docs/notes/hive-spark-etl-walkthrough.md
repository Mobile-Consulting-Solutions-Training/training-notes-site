---
title: Hive + Spark ETL Walkthrough
description: Hands-on runbook for migrating the Postgres medallion warehouse to Hive and building the Source to Bronze to Silver to Gold ETL pipeline with Spark.
---

# Hive + Spark ETL Walkthrough: Medallion Migration + First Real ETL Pipeline

Source: instructor's (Evan Flint's) lesson-plan article for `Training 8.md`'s Hive session, adapted to the real `ajackson` Postgres warehouse from `Training 5.md`. See `Training 8.md` for the conceptual notes (what Tez/Beeline/HiveServer2 are, etc.) - this file is the hands-on runbook.

**The two-part goal:**

```text
PART 1 — MIGRATION
PostgreSQL Bronze/Silver/Gold  --export-->  files  --load-->  Hive Bronze/Silver/Gold

PART 2 — FIRST REAL ETL PIPELINE
New Fake Sales -> Spark -> Hive Bronze -> (Spark clean/validate) -> Hive Silver
                                        -> (Spark dimensional transformation) -> Hive Gold.fact_sales
```

Why two parts: Part 1 is a straight *migration* (already-correct data moving between systems, no transformation logic). Part 2 is the first *actual ETL pipeline* (new raw data flowing through real cleaning + dimensional-modeling logic). Keeping them separate avoids blurring "Spark reads a CSV and writes to Hive" into one vague idea.

**Target shape (both systems, once done):**

```text
bronze.sales
silver.sales
gold.dim_customer, gold.dim_date, gold.dim_department, gold.dim_employee,
gold.dim_office, gold.dim_product, gold.fact_payment, gold.fact_sales
```

---

## Status

- [x] Postgres `warehouse_practice.bronze.sales` / `.silver.sales` built (2,803 rows each - see `Training 8.md`)
- [x] Postgres `warehouse_practice.gold` has all 8 tables (fixed `fact_payment` schema + added `dim_department`)
- [x] Hive running locally:
  ```bash
  docker run -d \
    --name hive-server \
    -p 10000:10000 \
    -p 10002:10002 \
    -e SERVICE_NAME=hiveserver2 \
    apache/hive:4.0.1
  ```
  Connect with:
  ```bash
  docker exec -it hive-server beeline -u 'jdbc:hive2://localhost:10000/default'
  ```
  *(Note: the earlier `apache/hive:standalone-metastore-nightly` pull was the wrong image for this - that one only runs the metastore service, not full HiveServer2. `apache/hive:4.0.1` is the correct one; it bundles HiveServer2 + an embedded Derby metastore + Hadoop + Tez.)*
- [x] **All 9 tables migrated Postgres -> Hive using PySpark** (`bronze.sales`, `silver.sales`, all 8 `gold.*` tables) - see "Part 1B" below for the full story, including two real bugs hit and fixed. All row counts verified matching, plus spot-checked actual content (not just counts):

  | Table | Rows | Status |
  |---|---|---|
  | `bronze.sales` | 2,803 | OK |
  | `silver.sales` | 2,803 | OK |
  | `gold.dim_customer` | 122 | OK |
  | `gold.dim_date` | 817 | OK |
  | `gold.dim_department` | 4 | OK |
  | `gold.dim_employee` | 23 | OK |
  | `gold.dim_office` | 23 | OK |
  | `gold.dim_product` | 111 | OK (embedded-comma risk in `product_description` confirmed handled correctly) |
  | `gold.fact_payment` | 273 | OK |
  | `gold.fact_sales` | 2,996 | OK |

  Scripts: `hive-spark-etl/spark/postgres_to_hive.py` (bronze.sales, the original single-table version with the bug writeup) and `hive-spark-etl/spark/migrate_remaining_to_hive.py` (generalized loop for the remaining 9 tables, using Hive's native `\001` delimiter to sidestep the comma-in-text risk).
- [x] Part 1 - Export/migrate all Postgres tables to Hive (done via PySpark instead of `\COPY`, functionally equivalent)
- [x] Part 1 - Create Hive databases + tables, load data
- [x] Part 1 - Validate migration (row counts) - see table above; also spot-checked actual row content, not just counts
- [x] Part 2 - Generate messy `new_sales.csv` (27 rows) - see "Part 2 — Actually Run (Results)" below
- [x] Part 2 - Spark: Source -> Bronze (27 rows)
- [x] Part 2 - Spark: Bronze -> Silver (16 rows survived cleaning)
- [x] Part 2 - Spark: Silver -> Gold (13 rows passed dimension lookups)
- [x] Part 2 - Trace one `sale_id` end-to-end + one bad record - both confirmed for real (20001 clean / 20003 rejected)

---

## Part 1 — Migrate the Existing Postgres Warehouse to Hive

No Spark yet - just `\COPY` + Hive DDL. Establish the existing warehouse in Hive before introducing any transformation logic.

**Suggested local project layout:**
```text
hive-spark-etl/
├── docker-compose.yml        (optional - can also just use the docker run command above)
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
└── spark/
    ├── bronze_to_silver.py
    └── silver_to_gold.py
```

```bash
mkdir -p data/bronze data/silver data/gold
```

### Step 1 - Export Bronze and Silver

From `psql` (`docker exec -it ajackson psql -U ajackson -d warehouse_practice`):
```sql
\COPY bronze.sales TO '/tmp/bronze_sales.csv' CSV HEADER;
\COPY silver.sales TO '/tmp/silver_sales.csv' CSV HEADER;
```
Then copy those out of the container and into the project's `data/` folders:
```bash
docker cp ajackson:/tmp/bronze_sales.csv data/bronze/sales.csv
docker cp ajackson:/tmp/silver_sales.csv data/silver/sales.csv
```

### Step 2 - Export Gold (all 8 tables)

```sql
\COPY gold.dim_customer TO '/tmp/dim_customer.csv' CSV HEADER;
\COPY gold.dim_date TO '/tmp/dim_date.csv' CSV HEADER;
\COPY gold.dim_department TO '/tmp/dim_department.csv' CSV HEADER;
\COPY gold.dim_employee TO '/tmp/dim_employee.csv' CSV HEADER;
\COPY gold.dim_office TO '/tmp/dim_office.csv' CSV HEADER;
\COPY gold.dim_product TO '/tmp/dim_product.csv' CSV HEADER;
\COPY gold.fact_payment TO '/tmp/fact_payment.csv' CSV HEADER;
\COPY gold.fact_sales TO '/tmp/fact_sales.csv' CSV HEADER;
```
```bash
for t in dim_customer dim_date dim_department dim_employee dim_office dim_product fact_payment fact_sales; do
  docker cp ajackson:/tmp/${t}.csv data/gold/${t}.csv
done
```

Final layout:
```text
data/
├── bronze/sales.csv
├── silver/sales.csv
└── gold/
    ├── dim_customer.csv
    ├── dim_date.csv
    ├── dim_department.csv
    ├── dim_employee.csv
    ├── dim_office.csv
    ├── dim_product.csv
    ├── fact_payment.csv
    └── fact_sales.csv
```

### Step 3 - Get the exported CSVs into the Hive container

Hive needs to `LOAD DATA` from a path *inside* its own container:
```bash
docker cp data/bronze/sales.csv hive-server:/tmp/bronze_sales.csv
docker cp data/silver/sales.csv hive-server:/tmp/silver_sales.csv
for t in dim_customer dim_date dim_department dim_employee dim_office dim_product fact_payment fact_sales; do
  docker cp data/gold/${t}.csv hive-server:/tmp/${t}.csv
done
```

### Step 4 - Create the three Hive databases

Inside Beeline:
```sql
CREATE DATABASE IF NOT EXISTS bronze;
CREATE DATABASE IF NOT EXISTS silver;
CREATE DATABASE IF NOT EXISTS gold;

SHOW DATABASES;
```
Postgres calls this level a **schema**; Hive traditionally calls it a **database** - same concept, different name.

```text
Postgres                 Hive
bronze.sales      →      bronze.sales
silver.sales      →      silver.sales
gold.dim_customer →      gold.dim_customer
gold.fact_sales   →      gold.fact_sales
```
Worth pointing out: Medallion Architecture isn't inherently tied to Databricks or Delta Lake - it's just Bronze/Silver/Gold as an organizing principle, which works the same way here in plain Hive.

### Step 5 - Type mapping (Postgres -> Hive)

| Postgres | Hive |
|---|---|
| `INTEGER` | `INT` |
| `BIGINT` | `BIGINT` |
| `NUMERIC(10,2)` | `DECIMAL(10,2)` |
| `VARCHAR` | `STRING` |
| `TEXT` | `STRING` |
| `DATE` | `DATE` |
| `TIMESTAMP` | `TIMESTAMP` |
| `BOOLEAN` | `BOOLEAN` |

### Step 6 - Create the Hive tables + load the CSVs

```sql
-- BRONZE
CREATE TABLE bronze.sales (
    sale_id INT,
    customer_id INT,
    product_id STRING,
    quantity INT,
    unit_price DECIMAL(12,2),
    sale_timestamp TIMESTAMP
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
TBLPROPERTIES ("skip.header.line.count"="1");

LOAD DATA LOCAL INPATH '/tmp/bronze_sales.csv' INTO TABLE bronze.sales;

-- SILVER (same shape as bronze for this dataset)
CREATE TABLE silver.sales (
    sale_id INT,
    customer_id INT,
    product_id STRING,
    quantity INT,
    unit_price DECIMAL(12,2),
    sale_timestamp TIMESTAMP
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
TBLPROPERTIES ("skip.header.line.count"="1");

LOAD DATA LOCAL INPATH '/tmp/silver_sales.csv' INTO TABLE silver.sales;

-- GOLD
CREATE TABLE gold.dim_customer (
    id INT,
    company STRING,
    last_name STRING,
    first_name STRING,
    phone STRING,
    address STRING,
    city_and_state STRING,
    postal_code STRING,
    country STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
TBLPROPERTIES ("skip.header.line.count"="1");
LOAD DATA LOCAL INPATH '/tmp/dim_customer.csv' INTO TABLE gold.dim_customer;

CREATE TABLE gold.dim_date (
    date_key INT,
    full_date DATE,
    year INT,
    quarter INT,
    month INT,
    month_name STRING,
    day INT,
    day_of_week INT,
    day_name STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
TBLPROPERTIES ("skip.header.line.count"="1");
LOAD DATA LOCAL INPATH '/tmp/dim_date.csv' INTO TABLE gold.dim_date;

CREATE TABLE gold.dim_department (
    department_id INT,
    department_name STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
TBLPROPERTIES ("skip.header.line.count"="1");
LOAD DATA LOCAL INPATH '/tmp/dim_department.csv' INTO TABLE gold.dim_department;

CREATE TABLE gold.dim_employee (
    id INT,
    last_name STRING,
    first_name STRING,
    badge_code STRING,
    email STRING,
    class STRING,
    seniority INT,
    job_title STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
TBLPROPERTIES ("skip.header.line.count"="1");
LOAD DATA LOCAL INPATH '/tmp/dim_employee.csv' INTO TABLE gold.dim_employee;

CREATE TABLE gold.dim_office (
    id INT,
    city STRING,
    phone STRING,
    address_1 STRING,
    address_2 STRING,
    state_or_region STRING,
    country STRING,
    post_code STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
TBLPROPERTIES ("skip.header.line.count"="1");
LOAD DATA LOCAL INPATH '/tmp/dim_office.csv' INTO TABLE gold.dim_office;

CREATE TABLE gold.dim_product (
    product_number STRING,
    product_name STRING,
    product_category STRING,
    product_scale STRING,
    product_manufacturer STRING,
    product_description STRING,
    length DECIMAL(12,2),
    width DECIMAL(12,2),
    height DECIMAL(12,2)
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
TBLPROPERTIES ("skip.header.line.count"="1");
LOAD DATA LOCAL INPATH '/tmp/dim_product.csv' INTO TABLE gold.dim_product;

CREATE TABLE gold.fact_payment (
    order_number INT,
    payment_id STRING,
    payment_date DATE,
    amount DECIMAL(12,2),
    payment_date_key INT
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
TBLPROPERTIES ("skip.header.line.count"="1");
LOAD DATA LOCAL INPATH '/tmp/fact_payment.csv' INTO TABLE gold.fact_payment;

CREATE TABLE gold.fact_sales (
    order_number INT,
    product_number STRING,
    quantity INT,
    price DECIMAL(12,2),
    order_line_number INT,
    sales_amount DECIMAL(12,2),
    order_date_key INT
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
TBLPROPERTIES ("skip.header.line.count"="1");
LOAD DATA LOCAL INPATH '/tmp/fact_sales.csv' INTO TABLE gold.fact_sales;
```

*(`LOAD DATA LOCAL INPATH` reads from the Hive container's own local filesystem, not HDFS - matches the `/tmp/*.csv` paths copied in via `docker cp` above.)*

Verify:
```sql
SHOW TABLES IN bronze;
SHOW TABLES IN silver;
SHOW TABLES IN gold;
```
Expected:
```text
bronze: sales
silver: sales
gold: dim_customer, dim_date, dim_department, dim_employee, dim_office, dim_product, fact_payment, fact_sales
```

**At this point: this is a migration, not an ETL pipeline.** Existing, already-correct data moved from Postgres into Hive - no transformation logic has run yet. That distinction matters for Part 2.

---

## Part 1B — Alternative: Migrating with PySpark Instead of `\COPY`

The steps above use plain Postgres `\COPY` + Hive `LOAD DATA`, no Spark involved. As a hands-on exercise, `bronze.sales` was also migrated using **PySpark** instead - script at `hive-spark-etl/spark/postgres_to_hive.py`. Two real bugs were hit and fixed along the way, both worth knowing about.

**The approach:** Spark reads from Postgres via JDBC (works great - Postgres is one of Spark's officially supported JDBC dialects), then hands off to Hive's native `LOAD DATA` for the actual load, rather than trying to write directly to Hive via JDBC.

**Bug 1 - Spark can't write to Hive via JDBC directly.** The first attempt used `df.write.format("jdbc")` pointed at Hive's JDBC endpoint (`jdbc:hive2://localhost:10000/default`), the same way you'd write to any other JDBC target. It failed:
```text
AnalysisException: [COLUMN_NOT_DEFINED_IN_TABLE] "INT" column `sale_id` is not defined in table
`bronze`.`sales`, defined table columns are: `sale_id`, `customer_id`, ...
```
Confusing, since `sale_id` is obviously one of the listed columns. **Root cause:** Spark's JDBC data source only ships dialects (identifier-quoting + type-mapping rules) for Postgres, MySQL, Oracle, SQL Server, DB2, Derby, and Teradata - not Hive. Without a registered dialect, Spark's pre-write schema-validation step quotes identifiers with double quotes (`"sale_id"`, ANSI-SQL style), but Hive's own dialect expects backticks (`` `sale_id` ``) - so the quoted name Spark generates never matches what Hive reports back, and the write fails before any data moves. **This is a real, general limitation** - Spark JDBC writes to Hive are unreliable for this reason, not something fixable with a connection option.

**Fix:** keep Spark's JDBC *read* from Postgres (that direction works fine), write the result to a local CSV, `docker cp` it into the `hive-server` container, then use Hive's own `LOAD DATA LOCAL INPATH` (the same mechanism Part 1 above uses) to actually load it.

**Bug 2 - the Hive table needs an explicit row format, or `LOAD DATA` silently loads garbage.** The first `bronze.sales` table was created without a `ROW FORMAT DELIMITED FIELDS TERMINATED BY ','` clause. Hive's default row format (`LazySimpleSerDe`) uses `\001` (Ctrl-A) as its field delimiter, not a comma - so loading a comma-separated CSV against that default silently produced **every column as NULL**, even though `SELECT COUNT(*)` reported the correct row count (2,803). The row count alone made it *look* like it worked - only checking actual row content revealed the problem. Fixed by dropping and recreating the table with the explicit `ROW FORMAT DELIMITED FIELDS TERMINATED BY ','` clause (matching what Part 1's DDL already specifies above).

**Bug 3 (smaller) - timestamp format mismatch.** Even after fixing the delimiter, `sale_timestamp` still came through `NULL` while every other column was correct. Spark's default CSV timestamp output is ISO 8601 (`2003-01-06T00:00:00.000-05:00`), but Hive's default `TIMESTAMP` parser expects `yyyy-MM-dd HH:mm:ss` (space-separated, no `T`, no timezone offset). Fixed with `date_format("sale_timestamp", "yyyy-MM-dd HH:mm:ss")` before writing the CSV.

**Result, fully verified (not just row count - actual data spot-checked column by column):**
```text
+----------------+--------------------+-------------------+-----------------+-------------------+------------------------+
| sales.sale_id  | sales.customer_id  | sales.product_id  | sales.quantity  | sales.unit_price  |  sales.sale_timestamp  |
+----------------+--------------------+-------------------+-----------------+-------------------+------------------------+
| 1              | NULL               | S24_3969          | 49              | 35.29             | 2003-01-06 00:00:00.0  |
| 2              | NULL               | S18_2248          | 50              | 55.09             | 2003-01-06 00:00:00.0  |
...
```
2,803 rows, matching Postgres exactly - `customer_id` is correctly `NULL` throughout (per the earlier decision that historical orders have no real customer link, not a bug).

**Lesson worth remembering:** a matching row count is necessary but **not sufficient** evidence a load worked - Bug 2 above produced the exact right row count (2,803) while every single value was `NULL`. Always spot-check actual row content after a load, not just `COUNT(*)`.

### Extending to All 9 Tables

With the pattern proven on `bronze.sales`, the same approach was generalized into a loop (`hive-spark-etl/spark/migrate_remaining_to_hive.py`) to migrate `silver.sales` and all 8 `gold` tables in one run - looping over a list of `(postgres_table, hive_database, hive_table, hive_column_defs)` tuples, creating each Hive database/table, reading from Postgres, and loading via the same CSV -> `docker cp` -> `LOAD DATA` path.

**One more bug caught before running it at scale:** `gold.dim_product.product_description` is free text, and 76 of its 111 rows contain literal commas (e.g. *"This replica features working kickstand, front suspension, gear-shift lever..."*). Hive's `ROW FORMAT DELIMITED` is a raw delimiter split, not a real CSV parser - it has no concept of a quoted field protecting an embedded delimiter. Loading that column with a comma-delimited file would have silently shifted every subsequent column in those 76 rows by however many extra commas each description contained - the same *"looks fine, is actually wrong"* failure mode as Bug 2, just triggered by data content instead of a missing table clause.

**Fix:** switched the field delimiter from `,` to `\u0001` (Ctrl-A) - Hive's own *default* delimiter, chosen historically for exactly this reason (it essentially never appears in real-world text). This has a nice side effect: since `\001` is already Hive's default, the `CREATE TABLE` statements for these 9 tables don't need a `ROW FORMAT DELIMITED FIELDS TERMINATED BY ...` clause at all - only `bronze.sales`'s original table (created before this lesson was learned) explicitly specifies `,`.

**Full verified results** (row counts matched Postgres exactly on every table, plus manual spot-checks - `dim_product`'s embedded-comma row was confirmed to load with all 6 checked columns intact and correctly aligned, and `silver.sales`'s timestamps came through correctly formatted):

| Table | Rows |
|---|---|
| `bronze.sales` | 2,803 |
| `silver.sales` | 2,803 |
| `gold.dim_customer` | 122 |
| `gold.dim_date` | 817 |
| `gold.dim_department` | 4 |
| `gold.dim_employee` | 23 |
| `gold.dim_office` | 23 |
| `gold.dim_product` | 111 |
| `gold.fact_payment` | 273 |
| `gold.fact_sales` | 2,996 |

All three Hive databases (`bronze`, `silver`, `gold`) now exist with the full target shape from the top of this document.

---

## Part 2 — Validate the Migration

Run the same counts against both systems:
```sql
SELECT COUNT(*) FROM bronze.sales;
SELECT COUNT(*) FROM silver.sales;
SELECT COUNT(*) FROM gold.fact_sales;
SELECT COUNT(*) FROM gold.fact_payment;
SELECT COUNT(*) FROM gold.dim_customer;
SELECT COUNT(*) FROM gold.dim_product;
```
(Postgres via `psql`, Hive via Beeline.) Matching counts on both sides is the first evidence the migration succeeded - a basic data-quality/validation check, same principle as verifying a pipeline actually worked rather than assuming it did.

---

## Part 3 — The Actual ETL Pipeline (Everything Below This Line Is ETL, Not Migration)

Pretend the business keeps operating after the migration - new sales occur. Generate `new_sales.csv` (~50-100 rows), **deliberately not clean**:

```csv
sale_id,customer_id,product_id,quantity,unit_price,sale_timestamp
10001,103,501,2,29.99,2026-09-22 09:14:00
10002,105,504,1,119.99,2026-09-22 09:18:00
10003,107,502,-3,14.50,2026-09-22 09:25:00
10004,,503,2,44.99,2026-09-22 09:31:00
10005,109,99999,1,25.00,2026-09-22 09:45:00
```
Include: normal sales, duplicate `sale_id`s, negative quantity, missing customer, unknown product, bad/NULL timestamps.

### Source → Bronze (Spark)

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("SalesETL")
    .enableHiveSupport()
    .getOrCreate()
)

raw = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv("/data/incoming/new_sales.csv")
)

raw.show()
raw.printSchema()
```

**"Should Bronze contain clean data?"** No - Bronze represents the source as faithfully as practical.

```python
raw.write.mode("append").insertInto("bronze.sales")
```
```sql
SELECT * FROM bronze.sales;
```

### Bronze → Silver (Spark)

```python
bronze = spark.table("bronze.sales")

from pyspark.sql.functions import col, to_timestamp, current_timestamp

silver = (
    bronze
    .dropDuplicates(["sale_id"])
    .filter(col("customer_id").isNotNull())
    .filter(col("product_id").isNotNull())
    .filter(col("quantity") > 0)
    .filter(col("unit_price") > 0)
    .withColumn("sale_timestamp", to_timestamp("sale_timestamp"))
    .withColumn("total_amount", col("quantity") * col("unit_price"))
    .withColumn("processed_at", current_timestamp())
)

silver.show()
print("Bronze:", bronze.count())
print("Silver:", silver.count())
```
Expect something like `Bronze: 100` / `Silver: 93` - **"Where did seven records go?"** is the natural follow-up question; this is where data-quality rules get introduced concretely instead of abstractly.

```python
silver.write.mode("append").insertInto("silver.sales")
```

### Silver → Gold (Spark) - Dimension Lookups + Surrogate Keys

For this pipeline: `silver.sales` + `gold.dim_customer` + `gold.dim_product` + `gold.dim_date` -> `gold.fact_sales`.

```python
silver = spark.table("silver.sales")
customers = spark.table("gold.dim_customer")
products = spark.table("gold.dim_product")
dates = spark.table("gold.dim_date")
```

**The business-key vs. surrogate-key idea from `Training 5.md`'s DWH lesson, made concrete:** an incoming `customer_id = 103` should resolve to whatever `gold.dim_customer`'s own key is; likewise `product_id` should resolve through `gold.dim_product`.

**Adapted to this warehouse's actual column names** (per the schema check above - the article's generic `customer_key`/`product_key` don't exist here, the real PKs are `dim_customer.id` and `dim_product.product_number`; `product_id` in `silver.sales` actually holds `product_number`-shaped values):

```python
fact_data = (
    silver
    .join(customers, silver.customer_id == customers.id, "left")
    .join(products, silver.product_id == products.product_number, "left")
    .join(dates, to_date(silver.sale_timestamp) == dates.full_date, "left")
)

fact_rows = fact_data.select(
    silver.sale_id,
    products.product_number,
    silver.quantity,
    silver.unit_price.alias("price"),
    silver.total_amount.alias("sales_amount"),
    dates.date_key.alias("order_date_key")
)

fact_rows.show()
```
*(Note: `gold.fact_sales`'s real columns are `order_number`, `product_number`, `quantity`, `price`, `order_line_number`, `sales_amount`, `order_date_key` - not a generic `customer_key`/`product_key` pair, since `fact_sales` was never linked to `dim_customer` in the first place, per `Training 5.md`'s homework Q1. This `fact_rows` selection reflects that real shape rather than the article's generic example - adjust before the actual `insertInto` if the class wants new sales to carry a customer link forward for the first time.)*

### Load Gold

```python
fact_rows.write.mode("append").insertInto("gold.fact_sales")
```
```sql
SELECT COUNT(*) FROM gold.fact_sales;
SELECT * FROM gold.fact_sales ORDER BY sale_timestamp DESC LIMIT 20;
```

---

## Part 4 — The Full Pipeline, Visually

```text
                 SOURCE SYSTEM
               new_sales.csv
                     │
                     │ Spark ingestion
                     ▼
              ┌─────────────┐
              │   BRONZE    │
              │    sales    │
              └──────┬──────┘
                     │ Spark
                     ├─ remove duplicates
                     ├─ reject invalid quantities
                     ├─ handle NULLs
                     ├─ convert types
                     └─ calculate amounts
                     ▼
              ┌─────────────┐
              │   SILVER    │
              │    sales    │
              └──────┬──────┘
                     │ Spark
                     ├──── gold.dim_customer
                     ├──── gold.dim_product
                     └──── gold.dim_date
                     ▼
              ┌─────────────┐
              │    GOLD     │
              │ fact_sales  │
              └─────────────┘
```

**Why raw fake data goes through Bronze -> Silver -> Gold, not straight to Gold:** it makes the layer purposes concrete instead of abstract.

| Layer | Purpose |
|---|---|
| Bronze | What did the source give us? |
| Silver | What data do we trust? |
| Gold | How does the business want to analyze it? |

---

## Part 5 — Trace One Transaction End-to-End

Pick one clean `sale_id` (e.g. `10001`) and one intentionally-bad one, and trace both through every layer:

```sql
SELECT * FROM bronze.sales WHERE sale_id = 10001;
SELECT * FROM silver.sales WHERE sale_id = 10001;
SELECT * FROM gold.fact_sales WHERE sale_id = 10001;
```

The bad record (e.g. `sale_id = 10003`, negative quantity) should exist in **Bronze only** - not in Silver, not in Gold. That single comparison demonstrates *why* Medallion Architecture exists far more intuitively than a slide explaining Bronze/Silver/Gold in the abstract.

---

## Part 2 — Actually Run (Results)

Script: `hive-spark-etl/spark/new_sales_etl.py`. Data: `hive-spark-etl/data/incoming/new_sales.csv` (27 rows, deliberately messy - duplicates, negative quantity, missing customer, unknown product, a malformed timestamp).

**Two design decisions made before running:**
1. **`gold.fact_sales` schema kept exactly as-is** (no `customer_key` added) - decided via explicit choice, matching the table's existing real limitation (never linked to `dim_customer`, per `Training 5.md` homework Q1). Only the `product_number` dimension lookup is demonstrated.
2. **`gold.dim_date` extended** to cover `2026-09-22` (every fake sale's date) in both Postgres and Hive, before running Silver -> Gold - it only covered `2003-01-06` to `2005-04-01` (generated from historical order dates). This is the exact scenario `Training 5.md` homework Q10 already covers: extend the date dimension before loading data that falls outside its range, rather than silently dropping/guessing.

**Two new bugs hit and fixed while building this (beyond the three already documented for Part 1):**

- **`to_timestamp()` throws instead of returning `NULL` on bad input.** The malformed `BAD_TIMESTAMP` value crashed the job with `SparkDateTimeException: [CAST_INVALID_INPUT]` - different from the article's assumption (older Spark silently nulled invalid casts). This Spark version (4.2.0) has ANSI SQL mode on by default. Fixed by using **`try_to_timestamp()`** instead, which tolerates bad input and returns `NULL` - the row then correctly fails the *date* dimension lookup downstream instead of crashing the job outright.
- **Per-table delimiter mismatch.** `bronze.sales` (created in Part 1) uses an *explicit* comma delimiter; every other table (`silver.sales`, all 8 `gold` tables, created later via `migrate_remaining_to_hive.py`) uses Hive's `\u0001` default. A shared `load_via_hive()` helper that assumed one delimiter for all tables silently loaded `bronze.sales` with every column `NULL` (same failure mode as Part 1's original delimiter bug) while reporting success. Fixed with a small per-table delimiter lookup (`{("bronze", "sales"): ","}`, default `\u0001` otherwise).

**Verified results:**

| Stage | Count | What happened |
|---|---|---|
| Source (raw CSV) | 27 | Read as-is |
| Bronze | 27 | Loaded unfixed - Bronze represents the source faithfully |
| Silver | 16 | 11 rejected: 2 exact duplicates (dedup), 9 rows failing `customer_id`/`product_id IS NOT NULL` or `quantity`/`unit_price > 0` |
| Gold (`fact_sales`) | 13 | 3 more rejected at the dimension-lookup stage: `sale_id` 20005 and 20020 referenced unknown `product_number`s (`S99_9999`, `S99_0000`); `sale_id` 20011's timestamp failed to parse (`try_to_timestamp` -> `NULL`), which then failed the *date* dimension lookup, not a data-quality filter |

**Trace exercise, run for real:**
- `sale_id = 20001` (clean): present in Bronze, Silver, and Gold (`order_number = 20001`, `sales_amount = 59.98`, `order_date_key = 20260922`) - full round-trip confirmed.
- `sale_id = 20003` (negative quantity, `-3`): present in Bronze only - `0` matches in both Silver and Gold. Exactly the demonstration Part 5 describes.

---

## Suggested Time Budget (~3-4 hours)

| Time | Activity |
|---|---|
| 30 min | Architecture review: Postgres vs Hive, schemas/databases, Bronze/Silver/Gold, OLTP vs DWH |
| 45 min | Migration: `\COPY`, Docker-mounted files, Hive databases/tables, load CSVs |
| 20 min | Validation: counts and sample queries between Postgres and Hive |
| 10 min | Break |
| 30 min | Source → Bronze: generate fake transactions, ingest with Spark |
| 35 min | Bronze → Silver: validation, deduplication, casting, derived columns |
| 45 min | Silver → Gold: dimension lookups, surrogate keys, loading `fact_sales` |
| 15 min | Verification: query Gold, trace one transaction Bronze → Silver → Gold |
