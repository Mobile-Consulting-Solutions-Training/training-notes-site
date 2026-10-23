---
title: "Training 16 - Snowflake Dynamic Tables"
description: "Snowflake Dynamic Tables and TARGET_LAG, plus CLI environment terms (REPL, TUI)."
sidebar:
  order: 16
---

Teacher: Evan Flint

Syllabus Day 17 (per file numbering) - topic: Snowflake Dynamic Tables, plus CLI environment terminology (REPL/TUI).

# Snowflake Dynamic Tables

Teacher's framing: a very simple sales summary is probably the clearest classroom demonstration because students can actually see the behavioral difference between a regular table, a view, and a dynamic table.

## Setup: daily sales totals

Source table:

```sql
CREATE TABLE sales (
    sale_id INTEGER,
    product VARCHAR,
    amount NUMBER(10,2)
);

INSERT INTO sales VALUES
    (1, 'Laptop', 1200),
    (2, 'Phone', 800),
    (3, 'Laptop', 1000);
```

Business wants a table containing total sales by product.

## Regular Table

```sql
CREATE TABLE sales_summary AS
SELECT
    product,
    SUM(amount) AS total_sales
FROM sales
GROUP BY product;
```

```sql
SELECT * FROM sales_summary;
```
```
Laptop   2200
Phone     800
```

Now add another sale:
```sql
INSERT INTO sales VALUES
    (4, 'Phone', 500);
```

The important demonstration - compare source vs. summary:
```sql
SELECT * FROM sales;
SELECT * FROM sales_summary;
```

The source has changed (`Phone` -> 1300), but `sales_summary` still says `Phone` -> 800.

**Why:** a regular table is just stored data. Snowflake has no inherent knowledge that `sales_summary` was intended to stay synchronized with `sales`. You'd have to re-run the transformation manually:
```sql
CREATE OR REPLACE TABLE sales_summary AS
SELECT
    product,
    SUM(amount) AS total_sales
FROM sales
GROUP BY product;
```
or build a scheduled task/dbt/Airflow pipeline to maintain it.

## Dynamic Table - the same scenario

```sql
CREATE OR REPLACE DYNAMIC TABLE sales_summary_dynamic
    TARGET_LAG = '1 minute'
    WAREHOUSE = COMPUTE_WH
AS
SELECT
    product,
    SUM(amount) AS total_sales
FROM sales
GROUP BY product;
```

Initially:
```
Laptop   2200
Phone     1300
```

Add another transaction, and **don't touch the dynamic table at all**:
```sql
INSERT INTO sales VALUES
    (5, 'Laptop', 500);
```

After Snowflake refreshes it (per `TARGET_LAG`):
```sql
SELECT * FROM sales_summary_dynamic;
```
```
Laptop   2700
Phone     1300
```

That's the "aha" moment - nobody touched `sales_summary_dynamic`, it updated itself.

## Real-World Example: Bronze -> Silver via a Dynamic Table (teacher's terminal)

A more realistic Dynamic Table than the toy `sales_summary` example above - this one does actual Bronze-to-Silver cleaning, filtering, and deduplication, all declaratively, continuously maintained by Snowflake rather than run as a one-time script:

```sql
CREATE OR REPLACE DYNAMIC TABLE DE_CLASS.SILVER.SALES
    TARGET_LAG = '1 minute'
    WAREHOUSE = DE_WH
AS
SELECT
    TRANSACTION_ID,
    TRANSACTION_DATE,
    INITCAP(TRIM(CUSTOMER_NAME)) AS CUSTOMER_NAME,
    INITCAP(TRIM(PRODUCT)) AS PRODUCT,
    UPPER(TRIM(CATEGORY)) AS CATEGORY,
    QUANTITY,
    UNIT_PRICE,
    ROUND(QUANTITY * UNIT_PRICE, 2) AS TOTAL_AMOUNT,
    UPPER(TRIM(COUNTRY)) AS COUNTRY
FROM DE_CLASS.RAW.SALES
WHERE QUANTITY > 0
  AND UNIT_PRICE > 0
  AND REGEXP_LIKE(TRANSACTION_ID, '^T[0-9]+$')
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY TRANSACTION_ID
    ORDER BY TRANSACTION_DATE
) = 1;
```

Expanded, piece by piece:

| Clause | What it's doing |
|---|---|
| `INITCAP(TRIM(CUSTOMER_NAME))` / `INITCAP(TRIM(PRODUCT))` | Trims whitespace, then title-cases free-text fields (`"  john smith "` -> `"John Smith"`) |
| `UPPER(TRIM(CATEGORY))` / `UPPER(TRIM(COUNTRY))` | Trims whitespace, then upper-cases fields meant to be standardized codes/labels rather than display names |
| `ROUND(QUANTITY * UNIT_PRICE, 2) AS TOTAL_AMOUNT` | A derived measure computed directly in the query - Bronze only has quantity/unit price, Silver adds the computed total |
| `WHERE QUANTITY > 0 AND UNIT_PRICE > 0` | Drops obviously-invalid rows (zero/negative quantity or price) |
| `REGEXP_LIKE(TRANSACTION_ID, '^T[0-9]+$')` | Drops rows whose `TRANSACTION_ID` doesn't match the expected format (a `T` followed by digits, start to end) - filters out malformed/corrupted source IDs |
| `QUALIFY ROW_NUMBER() OVER (PARTITION BY TRANSACTION_ID ORDER BY TRANSACTION_DATE) = 1` | Deduplicates - if the same `TRANSACTION_ID` appears more than once in Bronze, only the earliest one (by `TRANSACTION_DATE`) survives into Silver |

**Why this matters as a Dynamic Table and not just a one-time query:** every one of these cleaning/filtering/dedup steps re-runs automatically as new rows land in `DE_CLASS.RAW.SALES` - new Bronze data that's malformed, duplicated, or has inconsistent casing gets cleaned into Silver within the `TARGET_LAG` window, with zero manual re-run and no separate orchestration (Airflow/dbt/scheduled task) needed to keep Silver in sync with Bronze. This is the medallion architecture's Bronze->Silver step (per `Training 5.md`) implemented as a *continuously self-maintaining* table instead of a batch job.

**`QUALIFY` note:** `QUALIFY` filters on the result of a window function (`ROW_NUMBER()` here) the same way `WHERE` filters on regular columns - it's what makes "keep only the first row per `TRANSACTION_ID`" expressible in a single query, without a subquery/CTE wrapping the window function just to filter on it afterward.

## Side-by-Side Diagram (teacher's board drawing)

```text
REGULAR TABLE                     DYNAMIC TABLE

SALES                             SALES
  │                                 │
  │ CREATE TABLE AS                 │ defined query
  ▼                                 ▼
SALES_SUMMARY                     SALES_SUMMARY
  │                                 │
  │                                 │
new sales arrive                  new sales arrive
  │                                 │
  ▼                                 ▼
Nothing happens                  Snowflake refreshes it
  │
Need ETL/SQL to
update summary
```

## The Conceptual Distinction

Teacher's definition: "A regular table stores data. A dynamic table stores the result of a query that Snowflake continually maintains according to a freshness target."

## "Why not just use a view?"

Teacher's three-way comparison:

```text
Regular table
→ result is physically stored
→ doesn't automatically update

View
→ doesn't store the result
→ recalculates when queried

Dynamic table
→ result is physically materialized
→ Snowflake refreshes it automatically
```

| | Stores result? | Stays current? |
|---|---|---|
| **Regular table** | Yes, physically stored | No - frozen at creation/last manual refresh |
| **View** | No - recalculates every query | Yes, but at the cost of recomputing from scratch each time it's queried |
| **Dynamic table** | Yes, physically materialized | Yes - Snowflake automatically refreshes it to meet the declared `TARGET_LAG` |

Expanded: this three-way framing is what actually makes Dynamic Tables click - they're not just "another ETL feature," they're the answer to "I want a view's automatic freshness, but a table's physical/pre-computed performance, without hand-rolling a refresh pipeline myself." `TARGET_LAG` is the key new concept: it's a declared freshness *target* (e.g. `'1 minute'`), not a guarantee of instant updates - Snowflake decides how/when to refresh the underlying query to try to meet that target, trading off compute cost against staleness, which is also why a `WAREHOUSE` has to be specified (something has to actually run the refresh).

---

# CLI Environment Terminology

## REPL

Teacher's definition: "REPL - a CLI environment that's designed for working with a programming language." "REPL stands for Read-Eval-Print-Loop."

Expanded: a REPL reads one expression you type, evaluates it immediately, prints the result, then loops back to read the next one - literally Read, Eval, Print, Loop. `python3` (bare, no script argument), the Scala `sbt console`, and `psql`'s own interactive prompt are all REPLs - each one is specifically for writing and immediately running code/queries in that particular language, one expression at a time, rather than running a whole program file at once.

## TUI

Teacher's definition: "TUI - Terminal User Interface - a CLI environment that's designed for interacting with a program through the CLI."

Expanded: a TUI is a full, often visually-structured interface (menus, panels, keyboard navigation) rendered entirely in text inside a terminal - not line-by-line like a REPL, but closer to a graphical app's layout, just built from text characters instead of pixels. `beeline` and `htop`-style tools are examples of this general category - the distinction from a REPL is purpose: a REPL is for interactively running code in a language, a TUI is for interacting with a specific program's own interface (menus, navigation, live-updating views) without ever leaving the terminal.

| | REPL | TUI |
|---|---|---|
| Purpose | Interactively run code in a programming language | Interact with a specific program's own interface |
| Interaction style | Type an expression, see its result, repeat | Navigate a text-rendered interface (menus, panels, keys) |
| Examples | `python3`, `sbt console`, `psql` prompt | `htop`, text-based dashboards/navigators |

---

# AWS IAM Policy Example - S3 Bucket Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowBucketInspection",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation",
        "s3:GetBucketVersioning"
      ],
      "Resource": "arn:aws:s3:::company-data"
    },
    {
      "Sid": "AllowReadWriteObjects",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::company-data/*"
    },
    {
      "Sid": "ExplicitlyDenyDeletion",
      "Effect": "Deny",
      "Action": [
        "s3:DeleteObject",
        "s3:DeleteObjectVersion"
      ],
      "Resource": "arn:aws:s3:::company-data/*"
    },
    {
      "Sid": "ExplicitlyDenyBucketAdministration",
      "Effect": "Deny",
      "Action": [
        "s3:DeleteBucket",
        "s3:PutBucketPolicy",
        "s3:PutBucketVersioning"
      ],
      "Resource": "arn:aws:s3:::company-data"
    }
  ]
}
```

Expanded - walking through each statement's role and why they're split this way:

| `Sid` | Effect | What it covers | Resource scope |
|---|---|---|---|
| `AllowBucketInspection` | Allow | Listing bucket contents, checking bucket location/versioning config | The **bucket itself** (`...:::company-data`, no trailing `/*`) |
| `AllowReadWriteObjects` | Allow | Reading and writing individual objects | **Objects inside** the bucket (`...:::company-data/*`, with the `/*`) |
| `ExplicitlyDenyDeletion` | Deny | Deleting objects or object versions | Objects inside the bucket |
| `ExplicitlyDenyBucketAdministration` | Deny | Deleting the bucket itself, changing its policy, changing its versioning config | The bucket itself |

**Why the bucket-level and object-level actions are split into separate statements with different `Resource` values:** S3 permissions distinguish between actions *on the bucket as a container* (`s3:ListBucket`, `s3:DeleteBucket`, etc. - these use the bare bucket ARN) and actions *on the objects inside it* (`s3:GetObject`, `s3:DeleteObject`, etc. - these need the `/*` suffix to apply to every object key within the bucket). Mixing them under one `Resource` value wouldn't work correctly - a bucket-level action checked against an object-level ARN (or vice versa) simply won't match.

**Why this is a genuinely useful pattern, not just a style choice:** this policy grants broad read/write access (list, inspect, get, put) while specifically carving out and blocking the destructive subset of actions (delete object, delete bucket, change bucket policy, change versioning) - a "read/write but not delete/administer" permission shape. This relies on a core IAM evaluation rule: **an explicit `Deny` always wins over an `Allow`**, no matter where either statement appears or what other policies might grant that same principal. So even if some other attached policy elsewhere granted `s3:DeleteObject`, these two `Deny` statements would still block it for this bucket - that's exactly why they're written as explicit denies rather than simply *omitting* delete/admin actions from the Allow list (omission only prevents access if no other policy grants it; an explicit Deny prevents it unconditionally).

---

# Time Travel

Q. What is Time Travel in data engineering?

A. The ability to query data *as it existed at a previous point in time* - not just a table's current state, but a version from minutes, hours, or days ago - without needing a separate backup or manually-taken snapshot.

**In Snowflake specifically** (directly relevant to today's Dynamic Tables coverage): every table automatically retains historical versions of its data for a configurable retention period (default 1 day, up to 90 days on Enterprise+), queryable via:

```sql
-- As of a specific timestamp
SELECT * FROM sales_summary_dynamic
  AT (TIMESTAMP => '2026-10-02 10:00:00');

-- As of N seconds ago
SELECT * FROM sales_summary_dynamic
  AT (OFFSET => -60*60);  -- 1 hour ago

-- Right before a specific change (by query ID)
SELECT * FROM sales_summary_dynamic
  BEFORE (STATEMENT => '<query_id>');

-- Restore an accidentally dropped/corrupted table entirely
UNDROP TABLE sales_summary_dynamic;
```

**Why it matters, practically:**
- Recovering from a bad `DELETE`/`UPDATE`, or an accidentally dropped table, without restoring from a backup
- Auditing - "what did this table actually look like before yesterday's pipeline ran?"
- Reproducing a report exactly as it appeared at a past point, for debugging or compliance

**Not Snowflake-exclusive:** the same underlying idea is behind Delta Lake's and Apache Iceberg's own time travel features (`Training 13.md`'s OTF coverage) - both keep a log of every change to a table and let you query (or roll back to) any prior snapshot by timestamp or version number. Snowflake just makes it a built-in table feature with zero setup, where Delta/Iceberg require the table format itself to be managing that versioned log.
