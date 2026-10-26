---
title: Day 16 Vocabulary
description: Glossary of terms and definitions from the Training 16 notes.
sidebar:
  order: 16
---

Vocabulary — Study Guide Day 16

Source: notes/Training 16.md

## Snowflake Dynamic Tables
- **Regular table** — A table that physically stores data and does not update automatically when its source changes.
- **CREATE TABLE AS (CTAS)** — Creates a table from a query's result at that moment.
- **CREATE OR REPLACE** — Recreates an object, replacing any existing one with the same name.
- **Dynamic table** — A table that stores the result of a query that Snowflake continually maintains according to a freshness target.
- **CREATE DYNAMIC TABLE** — Snowflake command that defines a dynamic table with a query, `TARGET_LAG` and `WAREHOUSE`.
- **TARGET_LAG** — A declared freshness target for how far a dynamic table may fall behind its source; a target, not a guarantee of instant updates.
- **WAREHOUSE (dynamic table)** — The virtual warehouse whose compute runs a dynamic table's refreshes.
- **Refresh** — Snowflake re-running a dynamic table's query to bring its result up to date.
- **View** — A saved query that stores no result and recalculates every time it is queried.
- **Materialized** — Physically stored as precomputed data rather than computed at query time.
- **Freshness** — How current a table's data is relative to its source.
- **Orchestration** — Scheduling and coordinating pipeline steps, e.g. with Airflow, dbt or scheduled tasks.
- **Scheduled task** — A job that re-runs SQL on a schedule to keep a table updated.

## Bronze to Silver Cleaning in SQL
- **Medallion architecture** — Layering data as Bronze (raw), Silver (cleaned) and Gold (business-ready).
- **Bronze layer** — The raw, as-landed data layer.
- **Silver layer** — The cleaned, filtered and deduplicated data layer.
- **TRIM** — Removes leading and trailing whitespace from a string.
- **INITCAP** — Title-cases a string, capitalizing the first letter of each word.
- **UPPER** — Converts a string to upper case.
- **ROUND** — Rounds a number to a given number of decimal places.
- **Derived measure** — A value computed in the query from other columns, such as `QUANTITY * UNIT_PRICE`.
- **REGEXP_LIKE** — Returns true when a string matches a regular expression pattern.
- **Regular expression (regex)** — A pattern language for matching text, e.g. `^T[0-9]+$`.
- **Deduplication** — Keeping only one row per duplicated key.
- **Window function** — A function computed over rows related to the current row, defined with `OVER`.
- **ROW_NUMBER()** — Window function that numbers rows within each partition in a given order.
- **PARTITION BY** — Splits rows into groups for a window function.
- **ORDER BY (window)** — Sets the row order within each window partition.
- **QUALIFY** — Filters on the result of a window function the way `WHERE` filters regular columns.
- **WHERE** — Filters rows on regular column conditions.
- **CTE (Common Table Expression)** — A named subquery defined with `WITH`.

## CLI Environment Terminology
- **CLI (Command-Line Interface)** — A text interface where you type commands in a terminal.
- **REPL (Read-Eval-Print-Loop)** — A CLI environment designed for working with a programming language, running one expression at a time.
- **TUI (Terminal User Interface)** — A CLI environment designed for interacting with a program through a text-rendered interface of menus, panels and keys.
- **sbt console** — Scala's interactive REPL launched through sbt.
- **psql** — PostgreSQL's interactive command-line client.
- **beeline** — Hive's command-line client.
- **htop** — A terminal process monitor with a text-based interactive interface.

## AWS IAM Policies for S3
- **IAM (Identity and Access Management)** — AWS service that controls who can do what on which resources.
- **IAM policy** — A JSON document of statements that allow or deny actions on resources.
- **Version (policy)** — The policy language version, `2012-10-17`.
- **Statement** — One rule in a policy combining effect, actions and resources.
- **Sid (Statement ID)** — An optional label naming a policy statement.
- **Effect** — Whether a statement `Allow`s or `Deny`s its actions.
- **Action** — The API operations a statement covers, such as `s3:GetObject`.
- **Resource** — The ARN(s) a statement applies to.
- **ARN (Amazon Resource Name)** — A unique identifier for an AWS resource.
- **Principal** — The user, role or service a policy applies to.
- **Bucket-level action** — An S3 action on the bucket as a container, matched against the bare bucket ARN.
- **Object-level action** — An S3 action on objects inside a bucket, matched against the bucket ARN with `/*`.
- **s3:ListBucket** — Permission to list a bucket's contents.
- **s3:GetBucketLocation** — Permission to read a bucket's region.
- **s3:GetBucketVersioning** — Permission to read a bucket's versioning setting.
- **s3:GetObject** — Permission to read an object.
- **s3:PutObject** — Permission to write an object.
- **s3:DeleteObject** — Permission to delete an object.
- **s3:DeleteObjectVersion** — Permission to delete a specific object version.
- **s3:DeleteBucket** — Permission to delete the bucket itself.
- **s3:PutBucketPolicy** — Permission to change a bucket's policy.
- **s3:PutBucketVersioning** — Permission to change a bucket's versioning setting.
- **Bucket versioning** — S3 setting that keeps prior versions of overwritten or deleted objects.
- **Explicit Deny** — A `Deny` statement, which always overrides any `Allow` from any policy.
- **Implicit deny** — Access is refused by default when no policy allows it, but another policy could still grant it.

## Time Travel
- **Time Travel** — The ability to query data as it existed at a previous point in time without a separate backup.
- **Retention period** — How long Snowflake keeps historical table versions (default 1 day, up to 90 on Enterprise+).
- **AT (TIMESTAMP => ...)** — Queries a table as of a specific timestamp.
- **AT (OFFSET => ...)** — Queries a table as of a number of seconds ago.
- **BEFORE (STATEMENT => ...)** — Queries a table as it was right before a given query ID ran.
- **Query ID** — The unique identifier Snowflake assigns to each executed statement.
- **UNDROP TABLE** — Restores a dropped table within its retention period.
- **Snapshot** — A stored version of a table at a point in time.
- **Delta Lake** — Open table format that keeps a transaction log enabling time travel.
- **Apache Iceberg** — Open table format with snapshot-based time travel.
- **OTF (Open Table Format)** — A table format, like Delta or Iceberg, that adds transactions and versioning over files in object storage.
