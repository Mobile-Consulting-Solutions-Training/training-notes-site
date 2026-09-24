---
title: Training 8 - Spark Partitioning, Salting & Hive Setup
description: repartition() vs. salting for handling data skew, then adding Hive to the local Docker environment and the medallion-migration ETL lesson plan.
---

Teacher: Evan Flint

Syllabus Day 9 (per file numbering) - actual coverage: deeper Spark performance tuning, continuing directly from `Training 7.md`'s Data Skew/Salting coverage (this session opened with a clarification on yesterday's homework's salting question). Note: this continues the pacing drift already visible in `Training 6.md`/`Training 7.md` - this session's content still lines up with the roadmap's Spark-focused territory rather than its own nominal Day 9 slot ("Hive + Spark Intro").

# `repartition()` vs. Salting: What Each One Actually Controls

Q. Does salting mean getting an exact, evenly-controlled number of rows per partition?

A. (Teacher's definition) No. Salting is not about getting an exact number of rows per partition. It is specifically a technique for dealing with data skew.

Expanded: this corrects a natural assumption coming out of `Training 7.md`'s Salting section - salting isn't a general-purpose tool for precisely controlling partition sizes, it's a targeted fix for one specific problem (a single key dominating a partition). The distinction the rest of this session draws out is between three related-but-different things: `df.repartition(n)` (no key), `df.repartition(n, "key")` (hash-partitioned by a key), and salting a skewed key on top of a key-based repartition.

---

## 1. `repartition(n)` (No Key) - Distribute the Data

```python
df2 = df.repartition(10)
```

Spark shuffles the data into 10 partitions, generally trying to distribute it reasonably evenly. With 100 million rows, you'd typically end up with roughly:

```text
Partition 0    ~10M
Partition 1    ~10M
Partition 2    ~10M
...
Partition 9    ~10M
```

This is useful when you just want **parallelism** - splitting work across more tasks/executors - with no requirement that rows sharing a particular value end up together. But often Spark *does* need records with the same key to be together (for a `groupBy()` or `join()`, per `Training 7.md`'s Narrow vs Wide Dependencies section) - that's where the next problem starts.

---

## 2. Partitioning by a Key Can Create Skew

```python
df.repartition(10, "customer_id")
```

Spark **hashes** `customer_id` to determine which partition each row goes to. Every row sharing the same key value gets the same hash, so they all land in the same partition - no exceptions. Suppose the data looks like:

| `customer_id` | rows |
|---|---|
| 100 | 70,000,000 |
| 101 | 3,000,000 |
| 102 | 3,000,000 |
| 103 | 3,000,000 |
| ... | ... |

Since every row where `customer_id = 100` hashes identically, all 70 million of them are forced into the same partition:

```text
Partition 0     5M
Partition 1     4M
Partition 2     6M
Partition 3    73M   <-- problem
Partition 4     3M
...
```

**Increasing the partition count does not fix this:**

```python
df.repartition(1000, "customer_id")
```

All 70 million rows for `customer_id = 100` still hash to exactly one partition, no matter how many total partitions exist. This is the direct, concrete mechanism behind `Training 7.md`'s Data Skew section - the "root cause: data not partitioned properly" and "uneven key distribution during a shuffle" points now have their precise explanation: hash partitioning guarantees same-key rows co-locate, so a single dominant key value simply *cannot* be split across partitions by `repartition(n, key)` alone, regardless of `n`.

**This is exactly the key reason salting exists.**

---

## 3. Salting Artificially Splits the Hot Key

Instead of:

```text
customer_id
100
100
100
100
100
100
```

...you create something like:

```text
customer_id    salt
100             0
100             3
100             1
100             4
100             2
100             0
```

Now partition using **both** columns:

```python
df.repartition(10, "customer_id", "salt")
```

Spark is now effectively hashing the *combination* `(100, 0)`, `(100, 1)`, `(100, 2)`, `(100, 3)`, `(100, 4)` instead of just `100` - so the 70 million rows for that one customer can be spread across up to 5 different partitions (one per distinct salt value used), rather than being forced into a single one. This is the mechanical detail underneath `Training 7.md`'s Salting subsection - the salt column doesn't change *what* determines a partition (it's still a hash), it changes *what gets hashed*, breaking the hot key's total dominance over a single hash bucket.

---

## The Important Distinction

Think of `repartition()` as answering: **"How many buckets should Spark create?"**

Salting answers a different question: **"How do I stop one extremely common key from all being forced into the same bucket?"**

| Goal | Tool | Example |
|---|---|---|
| Just need N reasonably equal partitions, no key involved | `repartition(n)` alone | `df.repartition(100)` |
| Need rows grouped by key, keys are reasonably evenly distributed | `repartition(n, key)` | `df.repartition(10, "customer_id")` |
| Need rows grouped by key, but one key massively dominates | `repartition(n, key, salt)` | `df.repartition(10, "customer_id", "salt")` |

If you simply need 100 reasonably equal partitions with no key requirement, `df.repartition(100)` is enough - no salting needed. Salting specifically matters when doing something **key-based** - `df.groupBy("customer_id").agg(...)` or `orders.join(customers, "customer_id")` - and one particular key represents an enormous percentage of the data.

---

## Caveat: Salting Changes How the Follow-Up Operation Must Work

**For `groupBy()`:** salting usually requires a **two-stage aggregation** - first aggregate by `(key, salt)`, then aggregate *again* by the original key alone. This extra step is necessary precisely because salting deliberately splits what logically belongs to one group (e.g. all of `customer_id = 100`'s rows) across multiple salted sub-groups - the first aggregation produces partial results per `(key, salt)` pair, and the second aggregation recombines those partial results back into the single correct total per real key.

**For joins:** you typically salt the large/skewed side of the join, and correspondingly **duplicate the matching rows from the smaller side across the salt values** used. Since the large side's rows for the hot key are now spread across multiple salted partitions, the small side's matching rows need a copy present in *each* of those same salted partitions, or the join would miss matches that ended up split apart by the salting.

| Operation | Extra step salting requires |
|---|---|
| `groupBy()` + aggregation | Two-stage aggregation: aggregate by `(key, salt)` first, then re-aggregate by the original key alone |
| `join()` | Duplicate the small/non-skewed side's matching rows across every salt value used, so each salted partition of the large side still has something to match against |

---

# Adding Hive to the Local Docker Environment

*(Hands-on setup, run step by step in the terminal - each step is logged here for reference. Builds on the existing `ajackson` Postgres container from `Training 5.md`'s warehouse work.)*

## Step 1 - Pull the Hive Standalone Metastore Image

```bash
docker pull apache/hive:standalone-metastore-nightly
```

**What this does:** downloads the Apache Hive **Standalone Metastore** Docker image from Docker Hub onto the local machine - it doesn't start or configure anything yet, it just fetches the image layers so a container can be created from it later. `docker pull` alone never runs a container; that's a separate `docker run` step still to come.

**Why the Standalone Metastore specifically (not "full Hive"):** the Hive Metastore is the actual piece most relevant to this course's Spark integration - it's the catalog service that tracks table schemas/locations (already referenced in `Training 0.md`'s Hive coverage: "a 'Hive Metastore' tracking table schemas/locations"). Running just the metastore as its own standalone service is the common pattern for letting Spark (and other engines) share one central catalog, without needing to run Hive's full query-execution engine (HiveServer2/HiveQL-on-MapReduce) alongside it.

**Verify it worked:**
```bash
docker images | grep hive
```
Should show `apache/hive` with the `standalone-metastore-nightly` tag now present locally.

---

## The Lesson Plan: Medallion Migration + First Real ETL Pipeline

The instructor's own article lays out today's actual goal as two parts, building directly on the `ajackson` Postgres warehouse from `Training 5.md`:

```text
PART 1 — MIGRATION
PostgreSQL Bronze/Silver/Gold  --export-->  files  --load-->  Hive Bronze/Silver/Gold

PART 2 — FIRST REAL ETL PIPELINE
New Fake Sales -> Spark -> Hive Bronze -> (Spark clean/validate) -> Hive Silver
                                        -> (Spark dimensional transformation) -> Hive Gold.fact_sales
```

**Why this two-part structure matters:** it deliberately separates *migrating* an existing warehouse (moving already-correct data from one system to another, no transformation logic involved) from *actually building an ETL pipeline* (new raw data flowing through cleaning and dimensional-modeling logic) - "Spark reads a CSV and writes to Hive" alone would blur that distinction. Part 1 gives students a working baseline in Hive; Part 2 is the first pipeline that actually *does* something to data as it moves.

**Target Postgres shape (per the article, corrected from an earlier - wrong - assumption that bronze/silver would each hold copies of every source table):**

```text
Postgres (warehouse_practice)
├── bronze.sales   <- one table: raw incoming sales transactions, unfixed
├── silver.sales    <- one table: cleaned/validated version of bronze.sales
└── gold
    ├── dim_customer
    ├── dim_date
    ├── dim_department
    ├── dim_employee
    ├── dim_office
    ├── dim_product
    ├── fact_payment
    └── fact_sales
```

**Gold schema was fixed to match this shape** (previously missing two of the eight tables):
```sql
-- fact_payment had been left behind in the public schema instead of gold
ALTER TABLE public.fact_payment SET SCHEMA gold;

-- dim_department didn't exist at all yet - sourced from bd_sql_training.departments
CREATE TABLE gold.dim_department (
    department_id INTEGER PRIMARY KEY,
    department_name VARCHAR(50)
);
INSERT INTO gold.dim_department (department_id, department_name) VALUES
    (1, 'Engineering'), (2, 'Sales'), (3, 'Finance'), (4, 'Marketing');
```
Note: `gold.dim_department` isn't linked to `gold.dim_employee` via a Foreign Key - the main `employees`/`dim_employee` table never captured a `department_id` (only the separate `employees_demo` table in `bd_sql_training` did). This is the same "dimension exists but is currently unlinked to the fact table" situation already documented for `dim_customer`/`dim_office` in `Training 5.md`'s homework Q1.

**`bronze.sales` / `silver.sales` built:**

Since the existing historical data lives in `gold.fact_sales` (already cleaned back in `Training 5.md`'s conversion) plus `public.orders`, and `orders` never captured a customer link at all - not even in the raw `bd_sql_training` source - `bronze.sales` was derived from those two rather than invented from scratch, with `customer_id` left `NULL` for every historical row (an honest gap, not a guessed value - same principle as `Training 5.md`'s homework Q10 on missing Gold-schema information):

```sql
CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE bronze.sales (
    sale_id INTEGER PRIMARY KEY,
    customer_id INTEGER,       -- NULL for all historical rows - orders never captured this
    product_id VARCHAR(50),    -- actually dim_product's product_number business key
    quantity INTEGER,
    unit_price NUMERIC(12,2),
    sale_timestamp TIMESTAMP
);

INSERT INTO bronze.sales (sale_id, customer_id, product_id, quantity, unit_price, sale_timestamp)
SELECT
    ROW_NUMBER() OVER (ORDER BY f.order_number, f.order_line_number) AS sale_id,
    NULL::INTEGER AS customer_id,
    f.product_number AS product_id,
    f.quantity,
    f.price AS unit_price,
    o.order_date::TIMESTAMP AS sale_timestamp
FROM gold.fact_sales f
JOIN public.orders o ON f.order_number = o.order_number;
```
2,803 rows loaded. `silver.sales` was then just a straight copy of `bronze.sales` (`CREATE TABLE silver.sales AS SELECT * FROM bronze.sales`) - there was nothing left to clean, since this historical backfill was sourced from already-cleaned `gold` data. **Worth remembering:** this makes today's `bronze`/`silver` historical backfill an exception, not the norm - it's only this clean because it was derived from `gold`. The article's Part 2 (`new_sales.csv` -> Spark -> Bronze -> Silver) is where Bronze will actually hold deliberately messy, unfixed data for the first time, and Silver's cleaning logic will have real work to do (dedup, null-filtering, type casting - see the dropDuplicates/filter chain in the article's Part 7).

**Naming note:** `bronze.sales.product_id` and `silver.sales.product_id` are populated with `gold.dim_product.product_number` values (e.g. `S18_3482`) - the column is named `product_id` to match the article's flat schema, but the actual business key it holds is `product_number`, matching every other table in this warehouse. Keep this in mind during the Part 9/10 dimension-lookup join later - the join key is `product_number`-shaped data even though the column is called `product_id`.

---

**Still to do, per the article's own sequence:**
1. ~~Build `bronze.sales` / `silver.sales` in Postgres~~ - done above.
2. ~~Stand up Hive itself~~ - done: `apache/hive:4.0.1` running as container `hive-server` (the earlier `standalone-metastore-nightly` pull was the wrong image - that only runs the metastore, not full HiveServer2).
3. Migrate Postgres's Bronze/Silver/Gold to Hive via `\COPY` -> CSV files -> Hive `LOAD DATA`.
4. Validate the migration with row-count comparisons between Postgres and Hive.
5. Build the actual Spark ETL pipeline: generate a deliberately messy `new_sales.csv`, then Spark Source -> Bronze -> Silver (clean/validate/dedupe) -> Gold (dimension lookups, surrogate keys, `fact_sales` load).
6. Trace one `sale_id` end-to-end through Bronze -> Silver -> Gold, and one intentionally-bad record that only survives in Bronze, as the closing demonstration of *why* Medallion Architecture exists.

**Full hands-on runbook for steps 3-6: `notes/hive-spark-etl-walkthrough.md`** - a dedicated step-by-step document (SQL/Python code adapted to this warehouse's actual column names, e.g. `dim_customer.id` and `dim_product.product_number` instead of the article's generic `customer_key`/`product_key`), separate from this file's narrative notes - same pattern as `notes/sql-training-walkthrough.md`.

---

## Gotcha: Spark Can't Write to Hive via a Plain JDBC Connection

Q. Can Spark's generic JDBC data source (`df.write.format("jdbc")`) write directly to Hive, the same way it writes to Postgres?

Expanded (hands-on discovery, from migrating `bronze.sales` with PySpark - full writeup in `hive-spark-etl-walkthrough.md`'s "Part 1B"): no - not reliably. Spark's JDBC data source only ships dialects (identifier-quoting and type-mapping rules) for a specific list of databases - Postgres, MySQL, Oracle, SQL Server, DB2, Derby, Teradata. **Hive isn't on that list.** Without a registered Hive dialect, Spark's pre-write schema-validation step quotes column names with double quotes (`"sale_id"`, ANSI-SQL style) when checking them against the target table - but Hive's own SQL dialect expects backticks (`` `sale_id` ``) for quoted identifiers instead. The mismatch means Spark never recognizes the target table's columns as matching, producing a confusing `[COLUMN_NOT_DEFINED_IN_TABLE]` error that names a column which is clearly right there in the table definition.

**The working pattern instead:** use Spark for what it's actually good at and has full dialect support for (reading/transforming via JDBC from something like Postgres), then hand off to the target system's own native bulk-load mechanism - for Hive, that's `LOAD DATA LOCAL INPATH`, the same command `Training 8.md`'s Part 1 migration already uses.

| Direction | Works via plain Spark JDBC? |
|---|---|
| Spark reads from Postgres (`spark.read.format("jdbc")`) | Yes - Postgres has an official Spark dialect |
| Spark writes to Postgres (`df.write.format("jdbc")`) | Yes - same reason |
| Spark reads from Hive | Not attempted here, but same dialect gap applies |
| Spark writes to Hive via plain JDBC | **No** - no Hive dialect registered in Spark; use `LOAD DATA` instead |

**Second gotcha layered on top of this:** even once you're loading via Hive's native `LOAD DATA`, the target table needs an explicit `ROW FORMAT DELIMITED FIELDS TERMINATED BY ','` clause - Hive's *default* row format uses `\001` (Ctrl-A) as its field delimiter, not a comma. Loading a comma-separated CSV against a table missing that clause doesn't error at all - it silently loads every column as `NULL`, while `SELECT COUNT(*)` still reports the correct row count. **A matching row count alone is not sufficient evidence a load worked** - always spot-check actual row values after a load, not just the count.

**Third gotcha: comma-delimited files break on free-text columns.** Migrating `gold.dim_product` (76 of 111 rows have literal commas inside `product_description`, e.g. *"...working kickstand, front suspension..."*) revealed why comma is a bad delimiter choice in the first place: Hive's `ROW FORMAT DELIMITED` is a raw split on the delimiter character, with **no quoted-field support** - unlike a real CSV parser, it has no way to know a comma inside a text field isn't a column boundary. Every embedded comma would silently shift all later columns in that row. Fixed by using `\u0001` (Ctrl-A) as the field delimiter instead - which happens to be Hive's own default, chosen historically for exactly this reason (it essentially never occurs in real text) - meaning the `CREATE TABLE` doesn't even need a `ROW FORMAT` clause when using it.

**Fourth gotcha: `to_timestamp()` throws instead of returning `NULL` on bad input, under ANSI SQL mode.** Building the Part 2 ETL pipeline (`new_sales_etl.py`, full writeup in `hive-spark-etl-walkthrough.md`), a deliberately malformed timestamp value crashed the job with `SparkDateTimeException: [CAST_INVALID_INPUT]`, instead of silently becoming `NULL` the way the lesson article assumed. This Spark version (4.2.0) runs with **ANSI SQL mode on by default** - invalid casts raise an exception rather than nulling out. Fixed with **`try_to_timestamp()`** instead of `to_timestamp()`, which tolerates unparseable input and returns `NULL` - letting that row continue through the pipeline and get correctly rejected later, at the date-dimension-lookup stage, instead of crashing the whole job. Worth remembering as a general Spark-version gotcha: don't assume older tutorials' cast-failure behavior carries over to a current Spark version without checking.

**Fifth gotcha: a shared "load into Hive" helper needs a per-table delimiter, not one delimiter for every table.** `bronze.sales` (created in Part 1) explicitly uses a comma delimiter; every table created afterward (`silver.sales`, all 8 `gold` tables) uses Hive's `\u0001` default instead (per the third gotcha above). A single reusable `load_via_hive()` function that assumed one fixed delimiter for every table silently loaded `bronze.sales` with every column `NULL` - same failure signature as the second gotcha, just triggered by inconsistency across tables within one project rather than a single missing clause. **Lesson: when a project's tables don't all share the same format for a historical reason, generalize the tooling to look up the right format per table - don't assume uniformity.**

---
