---
title: Study Guide - Day 16
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 16: Snowflake Dynamic Tables"
sidebar:
  order: 160
---

Study Guide - Day 16 (source: notes/Training 16.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Regular Table Demo.** `CREATE TABLE sales_summary AS SELECT product, SUM(amount) ... GROUP BY product`. Insert a new sale and the summary doesn't change: a regular table is just stored data, and Snowflake doesn't know it should stay in sync. You'd have to re-run it or build a Task/dbt/Airflow job.

**Dynamic Table Demo.** `CREATE OR REPLACE DYNAMIC TABLE sales_summary_dynamic TARGET_LAG = '1 minute' WAREHOUSE = COMPUTE_WH AS SELECT ...`. Insert a new sale, don't touch the dynamic table, and after the refresh it shows the new total. A **warehouse** is required because something has to run the refresh.

**Bronze → Silver as a Dynamic Table.** Evan's `DE_CLASS.SILVER.SALES` reads `DE_CLASS.RAW.SALES` and continuously: trims and title-cases names (`INITCAP(TRIM(...))`), upper-cases codes (`UPPER(TRIM(...))`), adds `ROUND(QUANTITY * UNIT_PRICE, 2) AS TOTAL_AMOUNT`, drops invalid rows (`QUANTITY > 0 AND UNIT_PRICE > 0`, `REGEXP_LIKE(TRANSACTION_ID, '^T[0-9]+$')`), and deduplicates with `QUALIFY ROW_NUMBER() OVER (PARTITION BY TRANSACTION_ID ORDER BY TRANSACTION_DATE) = 1`. **`QUALIFY`** filters on a window function result without a subquery. The medallion Bronze → Silver step runs itself, with no orchestration.

**Table vs View vs Dynamic Table.** "A regular table stores data. A dynamic table stores the result of a query that Snowflake continually maintains according to a freshness target." Regular table: stored, not updated. View: not stored, recalculated on every query. Dynamic table: stored and refreshed automatically. **`TARGET_LAG`** is a freshness target, not a guarantee.

**REPL and TUI.** **REPL** (Read-Eval-Print-Loop) = a CLI environment for working with a programming language: `python3`, `sbt console`, `psql`. **TUI** (Terminal User Interface) = a CLI environment for interacting with a program through text menus and panels: `htop`.

**IAM Policy Example.** A "read/write but don't delete or administer" S3 policy: Allow `ListBucket`, `GetBucketLocation`, `GetBucketVersioning` on the **bucket ARN** (`arn:aws:s3:::company-data`); Allow `GetObject`, `PutObject` on the **object ARN** (`.../*`); explicit **Deny** on deleting objects and versions, and on `DeleteBucket`, `PutBucketPolicy`, `PutBucketVersioning`. Bucket and object actions need different resources. **An explicit Deny always beats an Allow**, even from another policy, whereas leaving an action out only works if nothing else grants it.

**Time Travel.** Query data as it existed earlier, with no backup: `AT (TIMESTAMP => ...)`, `AT (OFFSET => -3600)`, `BEFORE (STATEMENT => '<query_id>')`, and `UNDROP TABLE`. Snowflake default retention is 1 day, up to 90 on Enterprise. Uses: recovering from a bad DELETE, auditing, reproducing old reports. Delta Lake and Iceberg offer the same idea through their transaction logs.

---

# Part 2: Cheat Sheet

## Dynamic Tables
- `CREATE DYNAMIC TABLE t TARGET_LAG = '1 minute' WAREHOUSE = wh AS SELECT ...`
- Needs a warehouse · lag = target, not guarantee
- Regular table (stored, stale) · View (not stored, live) · Dynamic (stored, auto-refreshed)

## Silver Cleaning SQL
- `INITCAP(TRIM(x))` names · `UPPER(TRIM(x))` codes · derived `ROUND(q*p, 2)`
- `WHERE q > 0 AND p > 0` · `REGEXP_LIKE(id, '^T[0-9]+$')`
- `QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY date) = 1` → dedupe

## CLI Terms
- REPL = language prompt (`python3`, `psql`) · TUI = program interface in text (`htop`)

## IAM
- Bucket ARN `arn:aws:s3:::b` for bucket actions · object ARN `arn:aws:s3:::b/*` for object actions
- Explicit Deny > Allow

## Time Travel
- `AT (TIMESTAMP => ...)` · `AT (OFFSET => -n)` · `BEFORE (STATEMENT => id)` · `UNDROP TABLE`
- Default 1 day, up to 90 · also Delta / Iceberg

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: Why doesn't a table created with CREATE TABLE AS update when the source changes?
A: A regular table is just stored data. Snowflake doesn't know it was meant to stay in sync with the source, so you have to rerun the query or schedule a pipeline.

Q: What's a dynamic table?
A: A table that stores the result of a query, which Snowflake keeps refreshed automatically to meet a freshness target you set with TARGET_LAG.

Q: Why does a dynamic table need a warehouse?
A: Something has to run the refreshes. The warehouse is the compute that executes the query each time Snowflake updates the table.

Q: What's the difference between a regular table, a view and a dynamic table?
A: A regular table stores its result but doesn't update. A view stores nothing and recalculates on every query. A dynamic table stores its result and Snowflake refreshes it automatically.

Q: Is TARGET_LAG a guarantee?
A: No, it's a target. Snowflake schedules refreshes to try to stay within it, trading compute cost against freshness.

Q: How did Evan's Silver dynamic table clean the data?
A: It trimmed and standardized the text fields, calculated the total amount, dropped rows with bad quantities, prices or transaction IDs, and kept only the first row for each transaction ID to remove duplicates.

Q: What does QUALIFY do?
A: It filters on the result of a window function, like keeping only rows where ROW_NUMBER equals 1, without wrapping the query in a subquery.

Q: What's the difference between a REPL and a TUI?
A: A REPL is for running code in a language one expression at a time, like the python prompt or psql. A TUI is a text-based interface for using a specific program, like htop.

Q: Why does an S3 policy need separate statements for the bucket and its objects?
A: Bucket actions like ListBucket apply to the bucket ARN, while object actions like GetObject apply to the objects, written with slash-star. A mismatched resource simply won't match.

Q: Why use an explicit Deny instead of just leaving delete out of the Allow?
A: An explicit Deny always wins, even if another policy grants delete. Leaving it out only blocks delete if nothing else allows it.

Q: What is time travel in Snowflake?
A: Querying a table as it was at an earlier point, by timestamp, offset or before a specific statement, within the retention period. UNDROP can even restore a dropped table.

Q: When would you use time travel?
A: To recover from a bad delete or update, to audit what a table looked like before a pipeline ran, or to reproduce an old report.
