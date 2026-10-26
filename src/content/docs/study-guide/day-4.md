---
title: Study Guide - Day 4
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 4: SQL Fundamentals & Data Warehousing"
sidebar:
  order: 40
---

Study Guide - Day 4 (source: notes/Training 4.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences. The syllabus's CI/CD headers for this day were not covered in class, so this guide covers what was: SQL and data warehousing.

# Part 1: Quick Summary

**PostgreSQL Peer Authentication.** On Ubuntu/Debian, local connections use `peer`: Postgres trusts your OS username. Create a role and a database with the same name as your Linux user (`sudo -u postgres createuser --createdb $USER`, `createdb --owner=$USER $USER`) and plain `psql` connects with no `-U`, `-d` or password. Linux users, Postgres roles and databases are three separate namespaces. Don't give a dev role `SUPERUSER`.

**Primary and Foreign Keys.** A primary key uniquely identifies each row and is never `NULL`. A foreign key in a child table references a parent's primary key; it can repeat and can be `NULL`. **Referential integrity** blocks FK values with no parent and (by default) deleting a referenced parent, unless `ON DELETE CASCADE`/`SET NULL`. A **composite key** spans several columns (`order_id + product_id`). PK/FK pairs are what joins match on.

**Data Types.** `INTEGER`, `SMALLINT`, `BIGINT`; `SERIAL`/`BIGSERIAL` auto-increment (Postgres); `DECIMAL(p,s)`/`NUMERIC` exact, always for money; `FLOAT`/`DOUBLE PRECISION` approximate; `CHAR(n)` fixed and padded, `VARCHAR(n)` variable with a max (Postgres errors on overflow), `TEXT` unbounded; `DATE`, `TIME`, `TIMESTAMP`, `TIMESTAMPTZ` (stored as UTC, prefer it across time zones); `BOOLEAN`. Columns are nullable unless `NOT NULL`; PKs are always `NOT NULL`. Engines differ (MySQL uses `AUTO_INCREMENT`).

**INSERT and SELECT.** Multi-row `INSERT INTO t VALUES (...), (...);` in column order. Select named columns and filter with `WHERE`. Single quotes for values, double quotes for identifiers (`"Engineering"` is read as a column). A missing `;` leaves psql waiting (`dbname-#`). `\c db` only works after `CREATE DATABASE`.

**GROUP BY and HAVING.** `GROUP BY` collapses rows into one per group for `COUNT`, `AVG`, `SUM`, `MIN`, `MAX`. `WHERE` filters rows before grouping; `HAVING` filters groups after. Every non-aggregated selected column must be in `GROUP BY`. An `INNER JOIN` drops groups with no matches; use `LEFT JOIN` to keep them.

**Subqueries, CTEs, Window Functions.** Subquery = nested inline query. CTE = named result set with `WITH name AS (...)`, readable top to bottom and reusable in the same query. Window function = `AGG() OVER (PARTITION BY ... ORDER BY ...)`, computes per row without collapsing rows.

**Nth Highest per Group (interview question).** Rank inside a CTE or subquery, then filter in the outer query: `WITH r AS (SELECT ..., RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rank FROM employees_demo) SELECT * FROM r WHERE rank = 3;`. You can't filter a window function in the same `WHERE`, because `WHERE` runs before window functions are computed. Ties: `RANK()` shares ranks and leaves gaps, `DENSE_RANK()` shares ranks with no gaps, `ROW_NUMBER()` is always unique (one row per group).

**Indexes and EXPLAIN ANALYZE.** An index (B-tree by default) is a separate ordered structure that maps values to rows. `EXPLAIN` shows the planned execution; `EXPLAIN ANALYZE` runs it and reports real times. Demo: `Seq Scan` before, `CREATE INDEX idx_t_col ON t(col);`, `Index Scan` after (use a big table, e.g. 1M rows from `generate_series`). The planner may still pick a Seq Scan on a small table: an index doesn't force its use. An index only helps queries on its columns. Composite index `(a, b)` helps filters starting with `a`, not `b` alone. Costs: disk space and slower `INSERT`/`UPDATE`/`DELETE`. Check with `\d table`; remove with `DROP INDEX`.

**Data Warehouse.** A database built for analysis, not running the app. Application DB = "what is happening now" (OLTP, narrow row lookups); warehouse = "what happened over time" (OLAP, big scans and aggregations). Data flows from app DBs, SaaS, events, files and APIs through ETL/ELT into the warehouse, then to BI (Power BI, Tableau, Python).

**Star Schema in Postgres.** A separate `warehouse` schema with a central **fact** table (measurable events: IDs plus quantity, price, revenue) surrounded by **dimensions** (descriptive: customer, product, date, employee). Analysts join fact to dimensions and `GROUP BY` year/month/category. A primitive ETL: `pd.read_sql` (extract) → `merge` + calculated column (transform) → `to_sql` (load).

**Why Not Just Postgres.** Postgres handles tens of millions of rows fine. At billions of rows, analytical queries read most of the table, so indexes don't help. Specialized platforms are built for huge scans.

**Redshift, Snowflake, Databricks.** **Redshift** (AWS) = columnar storage: each column stored together, so `SUM(price)` reads only `price`, and columns compress well. **Snowflake** = separated storage and compute: one copy of data, independent virtual warehouses per team that scale or suspend. **Databricks** = the lakehouse: data in object storage (S3/ADLS/GCS) as Parquet/Delta, processed by distributed Spark for SQL, ETL and ML.

---

# Part 2: Cheat Sheet

## psql Setup
- `sudo -u postgres createuser --createdb $USER` · `sudo -u postgres createdb --owner=$USER $USER` · `psql`
- `psql` defaults to `-U $USER -d $USER` · peer auth = OS username · no `SUPERUSER`

## Keys
- PK: unique, never NULL, auto-indexed · FK: references parent PK, can repeat, can be NULL
- Referential integrity · `ON DELETE CASCADE` / `SET NULL` · composite key

## Data Types
- Money → `DECIMAL(p,s)` never `FLOAT` · `VARCHAR(n)` common · `TEXT` unbounded
- `TIMESTAMPTZ` across time zones · `SERIAL`/`BIGSERIAL` surrogate keys

## SQL Gotchas
- `'value'` single quotes · `"identifier"` double quotes
- Missing `;` → `dbname-#` prompt · `CREATE DATABASE` before `\c`

## GROUP BY
- `WHERE` (rows, before) vs `HAVING` (groups, after)
- Non-aggregated select columns must be in `GROUP BY` · `LEFT JOIN` keeps empty groups

## Subquery vs CTE vs Window
- Subquery inline · CTE `WITH x AS (...)` reusable · Window `OVER (PARTITION BY ... ORDER BY ...)` keeps all rows

## Nth Highest per Group
- Window in CTE → filter outside (`WHERE` runs before windows)
- `RANK` gaps · `DENSE_RANK` no gaps · `ROW_NUMBER` unique

## Indexes
- `EXPLAIN ANALYZE` → `CREATE INDEX idx_t_c ON t(c);` → compare → `\d t` → `DROP INDEX`
- Seq Scan vs Index Scan · planner decides by cost · B-tree default
- Composite `(a, b)`: leading column matters · costs: space + slower writes

## Warehouse
- OLTP app DB (now) vs OLAP warehouse (over time)
- Sources → ETL/ELT → warehouse → BI
- Star schema: fact (measures + IDs) + dimensions (descriptions)
- Pandas ETL: `read_sql` → `merge` → `to_sql`

## Platforms
- Postgres = general relational · Redshift = columnar AWS warehouse
- Snowflake = storage separate from compute · Databricks = lakehouse on object storage + Spark

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: How do you set up Postgres so you can just type psql with no flags?
A: Create a Postgres role and a database with the same name as your Linux user. Local connections use peer authentication, which trusts your OS username, so psql connects as that role to that database with no password.

Q: What's the difference between a primary key and a foreign key?
A: A primary key uniquely identifies each row in its own table and can't be null. A foreign key is a column that points at another table's primary key. It can repeat and can be null.

Q: What is referential integrity?
A: The database refuses a foreign key value that doesn't exist in the parent table, and by default refuses to delete a parent row that's still referenced. It keeps related tables consistent.

Q: What's a composite key?
A: A primary key made of more than one column, used when no single column is unique, like order ID plus product ID in an order lines table.

Q: What data type do you use for money and why?
A: DECIMAL or NUMERIC, because they're exact. Floating point types can introduce rounding errors.

Q: TIMESTAMP or TIMESTAMPTZ?
A: TIMESTAMPTZ for anything that crosses time zones. It's stored as UTC and converted to the session's time zone when read. Plain TIMESTAMP has no time zone awareness.

Q: Why does WHERE department_name = "Engineering" fail in Postgres?
A: Double quotes mean an identifier, so Postgres looks for a column named Engineering. String values need single quotes.

Q: What's the difference between WHERE and HAVING?
A: WHERE filters individual rows before grouping. HAVING filters groups after aggregation, so it's where conditions on aggregates like AVG(salary) go.

Q: What's the difference between a subquery, a CTE and a window function?
A: A subquery is a nested query inline. A CTE is a named result set defined with WITH, easier to read and reusable in the same query. A window function computes an aggregate for each row over a partition without collapsing rows like GROUP BY does.

Q: How do you find the third highest salary in each department?
A: Use a CTE that adds RANK or DENSE_RANK over a partition by department ordered by salary descending, then select from the CTE where the rank equals 3.

Q: Why can't you filter on the window function in the same query's WHERE?
A: WHERE runs before window functions are calculated, so the rank doesn't exist yet. You need an outer query level, a CTE or subquery.

Q: How do RANK, DENSE_RANK and ROW_NUMBER differ?
A: RANK gives ties the same rank and then skips numbers. DENSE_RANK gives ties the same rank with no gaps. ROW_NUMBER gives every row a unique number, so you get exactly one row per group.

Q: What does an index do?
A: It's a separate sorted structure, a B-tree by default, that lets the database jump straight to matching rows instead of scanning the whole table.

Q: How would you show that an index helps?
A: Run EXPLAIN ANALYZE on the query and see a Seq Scan, create the index, run it again and see an Index Scan with a lower execution time. Use a large table so the difference is real.

Q: If you create an index, will Postgres always use it?
A: No. The planner picks the cheapest plan it estimates. On a small table, or a filter matching many rows, a sequential scan can be cheaper.

Q: Why does column order matter in a composite index?
A: A B-tree on (category, price) is sorted by category first, so it helps filters on category, or category and price, but not much for price alone.

Q: Why not index every column?
A: Each index takes disk space and has to be updated on every insert, update and delete. Index columns used often to find, join or sort data when the benefit is worth the cost.

Q: What is a data warehouse?
A: A database designed for analyzing data over time rather than running the application. The app database answers what's happening now; the warehouse answers what happened and what we can learn.

Q: What's in a fact table versus a dimension table?
A: A fact table holds measurable events, mostly IDs and numbers like quantity and revenue. Dimension tables hold the descriptions, like customer name, product category or the date's month and year.

Q: Why isn't Postgres enough at very large scale?
A: An analytical query over billions of rows has to read most of the table, so indexes don't help. Platforms built for analytics use columnar storage and distributed compute for those big scans.

Q: Why does columnar storage help analytics?
A: Each column is stored together, so a query like SUM(price) reads only the price column instead of every full row. Columns of similar values also compress very well.

Q: What's special about Snowflake's architecture?
A: Storage is separated from compute. All teams share one copy of the data, and each team gets its own virtual warehouse that can be scaled up or suspended independently.

Q: What's a lakehouse?
A: Data lives cheaply in cloud object storage in formats like Parquet and Delta, and distributed engines like Spark run SQL, ETL and ML directly on it. Databricks popularized it.
