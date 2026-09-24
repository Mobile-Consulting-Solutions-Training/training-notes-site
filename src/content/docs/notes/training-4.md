---
title: Training 4 - SQL Fundamentals & Data Warehousing
description: PostgreSQL keys, data types, joins, CTEs, window functions, and indexing/query plans, followed by data warehousing concepts and a Redshift/Snowflake/Databricks comparison; the syllabus's CI/CD headers went uncovered this session.
---

Teacher: Evan Flint

Syllabus Day 5: CI/CD for Data Eng.
Coverage: Build/test/deploy flow, pipeline YAML, PR validation, environments, secrets, rollback and patterns.

## Video Resources

## References

# CI/CD Fundamentals

# Pipeline YAML & Build/Test/Deploy Flow

# PR Validation

# Environments

# Secrets Management

# Rollback & Recovery Patterns

---

# Databases & SQL Providers

## PostgreSQL Local Dev Setup (Peer Authentication)

Q. On a typical Ubuntu/Debian PostgreSQL installation, what is the cleanest way to set up local access so a Linux user can just run `psql` with no flags?

A. (Teacher's definition) On a typical Ubuntu/Debian PostgreSQL installation, the cleanest setup is to create a PostgreSQL role with the same name as the Linux user. PostgreSQL's default local authentication commonly uses `peer`, so your OS username becomes your database identity.

Suppose the Linux user is `evan`.

1. Enter PostgreSQL as the admin:
```bash
sudo -u postgres psql
```

2. Create a PostgreSQL user matching the Linux username. Inside `psql`:
```sql
CREATE USER evan;
```
If the user should be allowed to create databases:
```sql
ALTER USER evan CREATEDB;
```
You generally do not want to give the user `SUPERUSER` for normal development.

3. Create a database owned by that user. A useful convention is to also create a database with the same name:
```sql
CREATE DATABASE evan OWNER evan;
```
Then exit:
```
\q
```

4. Now simply run, from the normal Linux shell:
```bash
psql
```
It should connect automatically:
```
evan@machine:~$ psql
psql (16.x)
Type "help" for help.

evan=>
```

This works because plain `psql` effectively defaults to:
```bash
psql -U "$USER" -d "$USER"
```
So if all three names match - Linux user `evan`, PostgreSQL role `evan`, PostgreSQL DB `evan` - then `psql` requires no `-U`, `-d`, or password.

**Quick version (shell one-liners):**
```bash
sudo -u postgres createuser --createdb $USER
sudo -u postgres createdb --owner=$USER $USER
psql
```

Expanded: This is a convenience setup for a single-developer dev machine, not a production pattern. The key concept being taught is that **Linux users, PostgreSQL roles, and PostgreSQL databases are three separate, independent namespaces** - nothing forces them to share a name. `peer` authentication (PostgreSQL's default for local Unix-socket connections on Debian/Ubuntu) works by checking the OS-level username of the process calling `psql` against a matching PostgreSQL role name, with no password prompt at all. When you deliberately name the role and the database after your Linux username, every default `psql` invokes without flags lines up automatically: it connects as a role named after your OS user, to a database named after your OS user, authenticated by the OS session itself. Skip any one of the three matches and you're back to typing `-U`, `-d`, or a password every time.

| Identity | Example value | Where it lives |
|---|---|---|
| Linux user | `evan` | OS-level user account (`whoami`) |
| PostgreSQL role | `evan` | Created with `CREATE USER` / `createuser`; PostgreSQL's login + permissions identity |
| PostgreSQL database | `evan` | Created with `CREATE DATABASE` / `createdb`; the actual data container the role connects to |

**Why not just give the dev user `SUPERUSER`?** Even on a personal dev box, keeping the working role as a plain (optionally `CREATEDB`) user rather than `SUPERUSER` mirrors real production discipline - app/dev roles shouldn't have unrestricted access to bypass all permission checks, catalog changes, and row-level security, so practicing with a scoped role builds the right habit early.

---

## Primary Keys & Foreign Keys

Q. What is a Primary Key? What is a Foreign Key?

A. A **Primary Key (PK)** is the column (or set of columns) that uniquely identifies every row in a table - no two rows can share the same value, and it can never be `NULL`. A **Foreign Key (FK)** is a column in one table that references the Primary Key of another table, creating a link between the two.

Expanded: The Primary Key is a table's own unique identity - the database enforces uniqueness and non-null automatically the moment a column is declared `PRIMARY KEY`, and most databases auto-index it for fast lookups. A Foreign Key doesn't identify rows in its own table; instead it points *outward* at another table's Primary Key, which is how relational databases represent relationships (e.g. an `orders` table pointing at a `customers` table) without duplicating that other table's data everywhere. This PK/FK pairing is the mechanical basis of a `JOIN` - the database matches rows by comparing a FK value in one table against the PK value it references in another.

| | Primary Key | Foreign Key |
|---|---|---|
| Purpose | Uniquely identifies each row in its own table | Links a row to a row in another (or the same) table |
| Uniqueness | Must be unique across the table | Can repeat many times (many rows can reference the same parent row) |
| Nullability | Never `NULL` | Can be `NULL` (means "no relationship" for that row) |
| Where it lives | Defined on the table it identifies | Defined on the "child"/referencing table, pointing at the "parent" table's PK |
| Example | `customers.customer_id` | `orders.customer_id` referencing `customers.customer_id` |

**Referential integrity:** the database won't let you insert a Foreign Key value that doesn't exist in the referenced table's Primary Key (and by default won't let you delete a parent row that's still referenced, unless the FK is defined with `ON DELETE CASCADE`/`SET NULL`). This is what keeps related tables consistent with each other rather than silently drifting apart.

**Composite key note:** a Primary Key can span multiple columns (e.g. `order_id + product_id` in an order-line-items table) when no single column is unique on its own - this is called a composite/compound key.

---

## SQL Data Types & Rules

Q. What are the main SQL data types, and what rules govern each?

A. Every column must be declared with a data type, which controls what values it can hold, how much storage it uses, and what operations are valid on it. The core categories are numeric, character/string, date/time, and boolean.

| Category | Type | Rule |
|---|---|---|
| Numeric (whole) | `INTEGER` / `INT` | Whole numbers only, no decimals; range roughly -2.1B to 2.1B (4 bytes) |
| Numeric (whole) | `SMALLINT` | Whole numbers, smaller range (-32,768 to 32,767); use for small bounded values (e.g. a percentage) |
| Numeric (whole) | `BIGINT` | Whole numbers, very large range; use for IDs that could exceed `INTEGER`'s ceiling (e.g. high-volume auto-incrementing keys) |
| Numeric (auto-increment) | `SERIAL` / `BIGSERIAL` (Postgres) | Same storage as `INTEGER`/`BIGINT`, but auto-generates the next sequential value on insert - common for surrogate Primary Keys |
| Numeric (exact decimal) | `DECIMAL(p,s)` / `NUMERIC(p,s)` | Exact, no rounding error; `p` = total digits, `s` = digits after the decimal point. `DECIMAL(10,2)` = up to 10 digits total, 2 after the decimal (max value 99999999.99). **Rule: always use this for money** - never floating point |
| Numeric (approximate) | `FLOAT` / `REAL` / `DOUBLE PRECISION` | Approximate binary floating point - fast, but can introduce rounding error; fine for scientific/measurement data, never for currency |
| String (fixed) | `CHAR(n)` | Fixed-length; always stores exactly `n` characters, padding shorter values with trailing spaces. Rare in practice - wastes space for variable-length data |
| String (variable) | `VARCHAR(n)` | Variable-length up to a max of `n` characters; the most common string type. Rule: inserting a value longer than `n` raises an error (Postgres) or silently truncates (some engines/modes - always check) |
| String (unbounded) | `TEXT` | Variable-length with no practical max length. Use when length is genuinely unbounded/unpredictable (e.g. a comment body) |
| Date/Time | `DATE` | Calendar date only (`YYYY-MM-DD`), no time component |
| Date/Time | `TIME` | Time of day only, no date |
| Date/Time | `TIMESTAMP` | Date + time, no timezone awareness - stored/interpreted as-is |
| Date/Time | `TIMESTAMPTZ` (`TIMESTAMP WITH TIME ZONE`, Postgres) | Date + time, normalized to UTC internally and converted to the querying session's timezone on read. **Rule: prefer this over plain `TIMESTAMP` for anything that crosses timezones** |
| Boolean | `BOOLEAN` | Only `TRUE`/`FALSE` (or `NULL`) - Postgres also accepts shorthand like `'t'`/`'f'`, `1`/`0` on input but always stores/displays as `TRUE`/`FALSE` |

**Nullability rule that cuts across every type:** any column is nullable by default unless declared `NOT NULL` - a Primary Key column is the one exception, which is always implicitly `NOT NULL`.

**Cross-engine note:** exact type names/behavior vary - e.g. MySQL has no native `SERIAL` keyword (uses `AUTO_INCREMENT` instead) and MySQL's `VARCHAR` overflow behavior differs from Postgres's hard error depending on SQL mode. Always check the specific engine's docs rather than assuming Postgres syntax is universal.

---

## INSERT & SELECT Basics

Q. How do you insert multiple rows at once, and how do you filter/select specific columns?

A. `INSERT INTO <table> VALUES (...), (...), ...;` inserts multiple rows in one statement - values must be listed in the same order as the table's columns. `SELECT <col1>, <col2> FROM <table> WHERE <condition>;` returns only the requested columns, filtered to rows matching the condition.

```sql
INSERT INTO departments VALUES
(1, 'Engineering'),
(2, 'Sales'),
(3, 'Finance'),
(4, 'Marketing');

INSERT INTO employees_demo VALUES
(101, 'Alice Johnson', 1, 95000.00, '2022-03-15', TRUE),
(102, 'Bob Smith', 2, 72000.00, '2023-07-01', TRUE),
(103, 'Carol Williams', 1, 105000.00, '2020-11-20', TRUE);

SELECT employee_name, salary FROM employees_demo WHERE salary > 80000;
```

Expanded: `SELECT *` returns every column; naming specific columns (`SELECT employee_name, salary FROM ...`) returns only those, in the order listed - useful once a table has many columns and you only need a few. `WHERE` filters *rows* (evaluated before the result set is returned), the same way a Pandas boolean mask filters a DataFrame (from `Training 2.md`).

**Rule - quoting matters:** string/text/date literals must use **single quotes** (`'Engineering'`, `'2022-03-15'`). Double quotes (`"Engineering"`) are reserved for quoting *identifiers* (table/column names with special characters or forced case) - using them around a value causes Postgres to look for a column named `Engineering`, producing `ERROR: column "Engineering" does not exist`.

**Gotcha - the missing semicolon:** every SQL statement must end in `;`. If you forget it, `psql`'s prompt changes from `dbname=#` to `dbname-#` to show it's still waiting for more input - it will treat the next line(s) you type (even a `\dt` meta-command) as a continuation of the same unfinished statement rather than running them, which is why a stray `\dt` on the next line can throw a `syntax error at or near "/"`. Finishing with `;` on its own line clears this.

**Gotcha - `\c` requires the database to already exist:** running `\c bd_sql_training;` before `CREATE DATABASE bd_sql_training;` has run will fail with `database "bd_sql_training" does not exist` and keep the previous connection open. Order matters: `CREATE DATABASE` first, then `\c` into it.

---

## GROUP BY & Aggregation

Q. How do you use `GROUP BY` with the `departments`/`employees_demo` tables?

A. `GROUP BY` collapses rows sharing the same value in the grouped column(s) into a single output row, letting you apply an aggregate function (`COUNT`, `AVG`, `SUM`, `MIN`, `MAX`) across each group.

```sql
-- Count employees per department (no join needed)
SELECT department_id, COUNT(*) AS employee_count
FROM employees_demo
GROUP BY department_id;

-- Average salary per department, with department names (JOIN + GROUP BY)
SELECT d.department_name, AVG(e.salary) AS avg_salary
FROM employees_demo e
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name;

-- Filter on the aggregate itself with HAVING (WHERE can't - it runs before grouping)
SELECT d.department_name, AVG(e.salary) AS avg_salary
FROM employees_demo e
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name
HAVING AVG(e.salary) > 80000;
```

Expanded: `WHERE` filters individual rows *before* grouping happens; `HAVING` filters *groups* after aggregation - this is why `HAVING AVG(e.salary) > 80000` works but `WHERE AVG(e.salary) > 80000` throws an error (the aggregate doesn't exist yet at the point `WHERE` runs). A department with zero matching employees (e.g. Marketing, if unreferenced) won't appear in an `INNER JOIN` result at all - it would need a `LEFT JOIN` to still show up with a `NULL`/zero aggregate.

**Rule:** every non-aggregated column in the `SELECT` list must also appear in `GROUP BY`, or Postgres raises an error - you can't select a raw column alongside an aggregate unless it's part of what you're grouping by.

---

## Subqueries, CTEs & Window Functions

Q. What's the difference between a subquery, a CTE, and a window function?

A. All three let you build a query on top of another query's result, but they behave differently: a **subquery** is a nested query used inline; a **CTE** (`WITH ... AS`) is a named, reusable temporary result set defined before the main query; a **window function** computes an aggregate per row *without* collapsing rows, unlike `GROUP BY`.

```sql
-- Subquery: employees earning above the company-wide average
SELECT employee_name, salary
FROM employees_demo
WHERE salary > (SELECT AVG(salary) FROM employees_demo);

-- CTE: same idea as a GROUP BY subquery, but named and readable top-to-bottom
WITH dept_avgs AS (
    SELECT department_id, AVG(salary) AS avg_salary
    FROM employees_demo
    GROUP BY department_id
)
SELECT d.department_name, da.avg_salary
FROM dept_avgs da
JOIN departments d ON d.department_id = da.department_id
WHERE da.avg_salary > 80000;

-- Window function: rank employees by salary within their own department,
-- without collapsing rows the way GROUP BY would
SELECT employee_name, department_id, salary,
       RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS salary_rank
FROM employees_demo;

-- Window function: attach each department's average salary to every row
SELECT employee_name, department_id, salary,
       AVG(salary) OVER (PARTITION BY department_id) AS dept_avg_salary
FROM employees_demo;
```

Expanded: a subquery nested in `WHERE`/`FROM` is evaluated first and its result substituted in, but stacking several nested subqueries gets hard to read. A CTE solves this readability problem - `WITH dept_avgs AS (...)` names the inner query's result so the outer query reads like plain English, and the same CTE can be referenced more than once in the outer query if needed. A window function is fundamentally different from both: `GROUP BY` (and by extension most subquery/CTE aggregate patterns) produces one row *per group*; `OVER (PARTITION BY ...)` produces one row *per original row*, with the aggregate value computed across that row's partition and attached alongside its own columns - nothing gets collapsed away.

| | Subquery | CTE | Window Function |
|---|---|---|---|
| Structure | Nested inline in `WHERE`/`FROM`/`SELECT` | Named block defined with `WITH ... AS` before the main query | `<aggregate>() OVER (PARTITION BY ... ORDER BY ...)` in `SELECT` |
| Row count in output | Depends on outer query | Depends on outer query | Same as the original table - no rows collapsed |
| Reusable in same query? | No - must repeat the subquery | Yes - can reference the CTE name multiple times | N/A (per-row, not a separate result set) |
| Typical use | One-off filtering against a computed value | Multi-step logic that's easier to read broken into named stages | Rankings, running totals, per-row comparisons against a group |

---

## Nth-Highest-Per-Group: RANK / DENSE_RANK / ROW_NUMBER (Common Interview Question)

Q. (Common interview question, per Evan Flint) Write a query to find out what the third highest salary per department is in an employee table.

A. (Teacher's definition) Yes. These are good examples for showing students that a CTE can replace the subquery you're using to filter the results of a window function.

**Subquery approach:**
```sql
SELECT *
FROM (
    SELECT
        employee_name,
        department_id,
        salary,
        RANK() OVER (
            PARTITION BY department_id
            ORDER BY salary DESC
        )
    FROM employees_demo
)
WHERE rank = 3;
```

**Equivalent CTE approach:**
```sql
WITH ranked_employees AS (
    SELECT
        employee_name,
        department_id,
        salary,
        RANK() OVER (
            PARTITION BY department_id
            ORDER BY salary DESC
        ) AS rank
    FROM employees_demo
)
SELECT *
FROM ranked_employees
WHERE rank = 3;
```

Same pattern with `DENSE_RANK()` and `ROW_NUMBER()`:
```sql
WITH ranked_employees AS (
    SELECT employee_name, department_id, salary,
           DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dense_rank
    FROM employees_demo
)
SELECT * FROM ranked_employees WHERE dense_rank = 3;

WITH numbered_employees AS (
    SELECT employee_name, department_id, salary,
           ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS row_number
    FROM employees_demo
)
SELECT * FROM numbered_employees WHERE row_number = 3;
```

**Why the CTE (or subquery) is necessary - a single-level query doesn't work:**
```sql
-- This does NOT work:
SELECT employee_name, department_id, salary,
       RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rank
FROM employees_demo
WHERE rank = 3;
```
That fails because logically the `WHERE` filtering happens *before* the window function result is available - `WHERE` operates on raw table rows, while window functions are computed as part of producing the output row. So you need another query level:
```
employees_demo
      |
window function
      |
ranked_employees CTE
      |
WHERE rank = 3
      |
final result
```
The CTE becomes much more useful than the equivalent subquery once you start chaining multiple transformations together, since it avoids deeply nested subqueries.

**Live classroom run** (against a larger seeded `sample_database`, so results include ties across more employees than the small `employees_demo` example above):
```sql
sample_database=# SELECT * FROM (SELECT employee_name, department_id, salary, RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) FROM employees_demo) WHERE rank=3;
  employee_name  | department_id |  salary  | rank
------------------+---------------+----------+------
 Susan White      |             2 | 75000.00 |    3
 James Rodriguez  |             2 | 75000.00 |    3
(2 rows)

sample_database=# SELECT * FROM (SELECT employee_name, department_id, salary, DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) FROM employees_demo) WHERE dense_rank=3;
   employee_name   | department_id |  salary   | dense_rank
--------------------+---------------+-----------+------------
 Alice Johnson      |             1 |  95000.00 |          3
 Ted Jones          |             1 |  95000.00 |          3
 Michael Anderson   |             1 |  95000.00 |          3
 Susan White        |             2 |  75000.00 |          3
 James Rodriguez    |             2 |  75000.00 |          3
 Joseph Harris      |             3 |  88000.00 |          3
 David Brown        |             3 |  88000.00 |          3
 Matthew King       |             4 |  98000.00 |          3
(8 rows)

sample_database=# SELECT * FROM (SELECT employee_name, department_id, salary, ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) FROM employees_demo) WHERE row_number=3;
  employee_name  | department_id |   salary   | row_number
------------------+---------------+------------+------------
 Carol Williams   |             1 |  105000.00 |          3
 Susan White      |             2 |   75000.00 |          3
 Karen Clark      |             3 |   92000.00 |          3
 Sandra Wright    |             4 |  102000.00 |          3
(4 rows)
```

Expanded: this is the standard interview question that tests whether you understand ranking window functions and the ordering-of-operations gotcha above. All three functions rank rows within each `PARTITION BY department_id` group, ordered by `salary DESC`, but they disagree on how to handle ties:

| Function | Tie handling | On ties, rank 3 returns... |
|---|---|---|
| `RANK()` | Tied rows share the same rank; the *next* rank skips ahead by the number of ties (gaps appear) | Every row tied at that rank position (here: 2 rows tied at rank 3 in dept 2) |
| `DENSE_RANK()` | Tied rows share the same rank; the next rank is always +1, no gaps | Every row tied at that rank position, across every department where a tie lands on rank 3 (here: 8 rows total) |
| `ROW_NUMBER()` | Every row gets a unique, sequential number regardless of ties (order among tied values is arbitrary unless a tiebreaker is added to `ORDER BY`) | Exactly one row per department (here: exactly 4 rows, one per department) |

**Naming gotcha:** an unaliased window function column takes on the bare function name as its output column header (`rank`, `dense_rank`, `row_number`) - which is why the classroom queries above could filter with `WHERE rank = 3` in the outer query even without writing `AS rank` explicitly. Aliasing explicitly (as done in the CTE versions) is still the clearer habit, especially once a query has more than one window function in play.

---

## Indexing & Query Plans (EXPLAIN ANALYZE)

Q. How would you demonstrate the purpose and effect of an index in a live classroom setting, and how do you read the resulting query plan?

A. (Teacher's definition) For a final classroom demonstration, I'd show the query before the index, create the index, then run the same query again. This makes the purpose of indexing concrete.

**1. Start with a query.** Using `orderdetails`:
```sql
SELECT *
FROM orderdetails
WHERE product_number = 'S18_1749';
```
It works without an index. The point of the index is performance, not functionality. Now inspect the plan:
```sql
EXPLAIN ANALYZE
SELECT *
FROM orderdetails
WHERE product_number = 'S18_1749';
```
Depending on the size of your dataset, you may see `Seq Scan on orderdetails`. A Sequential Scan means PostgreSQL is scanning the table looking for matching rows.

**2. Create an index.** Syntax:
```sql
CREATE INDEX index_name
ON table_name(column_name);
```
For this query:
```sql
CREATE INDEX idx_orderdetails_product_number
ON orderdetails(product_number);
```
That's it. The index now exists. See the indexes on a table with `\d orderdetails`:
```
Indexes:
    "orderdetails_pkey" PRIMARY KEY, btree (order_number, product_number)
    "idx_orderdetails_product_number" btree (product_number)
```
PostgreSQL uses B-tree by default.

**3. Run the same query again.**
```sql
EXPLAIN ANALYZE
SELECT *
FROM orderdetails
WHERE product_number = 'S18_1749';
```
With a sufficiently large/selective table, PostgreSQL may now choose something like `Index Scan using idx_orderdetails_product_number on orderdetails`.

So conceptually:
```
WITHOUT INDEX                          WITH INDEX

orderdetails                           Index
+--------+                                │
| row 1  | <- check                       ├── S10...
| row 2  | <- check                       ├── S12...
| row 3  | <- check                       ├── S18_1749 -----> matching table rows
| row 4  | <- check                       ├── S18...
| ...    |                                └── S24...
| row N  | <- check
+--------+

Sequential Scan                        Index Scan
```
The index provides PostgreSQL with a data structure designed to locate the desired values efficiently rather than simply examining the entire table.

**4. PostgreSQL may still use a Seq Scan** - worth demonstrating deliberately. Running the same `EXPLAIN ANALYZE` again might still show `Seq Scan`. That's not an error - the classroom dataset is relatively small, and PostgreSQL's optimizer can decide "this table is tiny, reading the whole thing is cheaper than going through the index." **Important interview point: creating an index does not force PostgreSQL to use it** - the query planner chooses whichever plan it estimates will be cheaper.

**5. A better demonstration with a larger table.** If the dataset is too small to show the difference, create a large temporary table:
```sql
CREATE TABLE index_demo AS
SELECT
    i AS id,
    'employee_' || i AS employee_name,
    (random() * 100000)::INTEGER AS salary
FROM generate_series(1, 1000000) AS i;
```
Now there's one million rows. Run:
```sql
EXPLAIN ANALYZE
SELECT * FROM index_demo WHERE id = 543210;
```
You should see a sequential scan, since `CREATE TABLE AS` didn't create an index (`Seq Scan on index_demo`). Now:
```sql
CREATE INDEX idx_index_demo_id
ON index_demo(id);
```
Run exactly the same query again - now you should see `Index Scan using idx_index_demo_id on index_demo`. You can also compare the `Execution Time` between the two plans - a much more convincing classroom demonstration.

**6. Indexes help some queries but not others.** The index on `id` benefits `WHERE id = 543210`, but a query filtering on `salary` (`WHERE salary = 75000`) has no index to use yet, and will show `Seq Scan` until you also run:
```sql
CREATE INDEX idx_index_demo_salary
ON index_demo(salary);
```
After that, PostgreSQL has an indexed access path available for that column too.

**7. Composite indexes** span multiple columns:
```sql
CREATE INDEX idx_orderdetails_category_price
ON orderdetails(product_category, price);
```
Useful for queries like:
```sql
SELECT * FROM orderdetails
WHERE product_category = 'Classic Cars' AND price > 100;
```
**Interview topic: column order matters in composite B-tree indexes.** An index on `(product_category, price)` is naturally suited to queries beginning with conditions on `product_category` - either alone, or combined with `price`. It is generally less useful for a query filtering *only* on the second column (`WHERE price > 100`).

**8. Indexes aren't free.** They improve many reads (`SELECT`/`WHERE`/`JOIN`/`ORDER BY`), but cost more disk space, and every `INSERT`/`UPDATE`/`DELETE` must also update or remove the corresponding index entries. The rule isn't "index every column" - it's **index columns that are frequently used to locate, join, or order data when the performance benefit justifies the write/storage cost.**

Clean up a demo table when done: `DROP TABLE index_demo;`

**Memorize this sequence for interview prep:**
```sql
-- 1. Identify a slow/important query
EXPLAIN ANALYZE
SELECT * FROM my_table WHERE some_column = 'value';

-- 2. Create an appropriate index
CREATE INDEX idx_my_table_some_column
ON my_table(some_column);

-- 3. Compare the plan
EXPLAIN ANALYZE
SELECT * FROM my_table WHERE some_column = 'value';

-- 4. Verify indexes
\d my_table

-- 5. Remove an unnecessary index
DROP INDEX idx_my_table_some_column;
```
That connects indexing and query plans rather than teaching indexes as an isolated SQL command.

Expanded: an index is a separate, ordered data structure (B-tree by default in Postgres) that maps column values to the physical rows containing them, so the database can jump straight to matching rows instead of reading every row in the table (a Sequential Scan). `EXPLAIN` shows the query planner's *chosen* execution plan without running the query; `EXPLAIN ANALYZE` actually executes it and reports real timing alongside the plan - always prefer `ANALYZE` when you want true performance numbers rather than just estimates. The planner's choice between `Seq Scan` and `Index Scan` is a cost-based decision, not a guarantee - on small tables a full scan is often genuinely cheaper than the overhead of traversing an index, which is why table size/selectivity matters for the demonstration to be convincing.

| Scan type | When PostgreSQL picks it | Cost characteristic |
|---|---|---|
| `Seq Scan` | Small tables, or queries matching a large fraction of rows | Reads every row once, in physical order - no extra structure to maintain/traverse |
| `Index Scan` | Larger tables with a selective filter (few matching rows) matched to an existing index | Traverses the B-tree to find matches, then fetches only those rows - overhead pays off only when it skips enough rows to matter |

| Index cost | Trade-off |
|---|---|
| Disk space | Each index is a separate structure stored alongside the table |
| `INSERT` | Every new row also adds an entry to each index on that table |
| `UPDATE` | Any indexed column that changes value requires the index entry to be updated |
| `DELETE` | Index entries for deleted rows must also be removed |

---

# Data Warehousing & Modern Analytical Platforms

## What is a Data Warehouse?

Q. What is a Data Warehouse?

A. (Teacher's definition) A data warehouse is a database designed primarily for analyzing data rather than running day-to-day applications.

A useful distinction for beginners is:
- **Application database:** "What is happening right now?"
- **Data warehouse:** "What has happened over time, and what can we learn from it?"

Imagine an online store. Its application database might contain: `customers`, `orders`, `order_details`, `products`, `payments`. The application needs to do things like:
```sql
SELECT *
FROM orders
WHERE order_number = 10401;
```
That's a small, targeted query. An analyst might instead ask: *"For each product category, what was our monthly revenue for the last three years, compared with the previous month and previous year?"* That could require millions or billions of rows to be joined, aggregated, sorted, and scanned. That's the kind of workload a data warehouse is built for.

Expanded: the core distinction is **OLTP vs. OLAP** (covered earlier in `Training 0.md`) - an application database is optimized for fast, narrow, single-row reads/writes (OLTP), while a warehouse is optimized for scanning and aggregating huge volumes of historical data across many rows at once (OLAP). This is why the SQL skills covered throughout this training (joins, aggregations, CTEs, window functions, indexing and query plans) matter so much to data engineers - analytical workloads use them constantly.

## Where Warehouse Data Comes From

Data typically flows in from many systems into a central analytical repository:
```
PostgreSQL application DB --+
                            |
Salesforce -----------------+
                            |
Website / mobile events ----+--> ETL / ELT --> DATA WAREHOUSE --> BI / Analytics
                            |
CSV / Excel files ----------+
                            |
APIs ------------------------+
```
Inside the warehouse, a typical structure looks like:
```
                    +----------------------+
                    |    DATA WAREHOUSE    |
                    |                      |
                    |  fact_sales          |
                    |  dim_customer        |
                    |  dim_product         |
                    |  dim_date            |
                    +-----------+----------+
                                |
               +----------------+----------------+
               v                v                v
           Power BI          Tableau          Python
```

## Building a Small Data Warehouse in PostgreSQL

PostgreSQL absolutely can be used as a data warehouse - in fact, it's an excellent way to teach the concepts before introducing specialized platforms.

Given operational tables (`customers`, `orders`, `orderdetails`, `products`, `payments`, `employees`), rather than letting analysts work directly against those operational tables, create a separate warehouse schema:
```sql
CREATE SCHEMA warehouse;
```
A common design for the analytical tables inside it is a **star schema**:
```
                    dim_customer
                         |
                         |
dim_date -------- fact_sales -------- dim_product
                         |
                         |
                    dim_employee
```
The center contains **facts**: measurable events. The surrounding tables contain **dimensions**: descriptive information about those events.

**Fact tables** contain things that happened and things that can be measured:
```sql
CREATE TABLE warehouse.fact_sales (
    sale_id BIGSERIAL PRIMARY KEY,
    order_number INT,
    customer_id INT,
    product_id INT,
    employee_id INT,
    date_id INT,

    quantity INT,
    unit_price NUMERIC(10,2),
    revenue NUMERIC(12,2)
);
```
A row might look like:

| order | customer | product | date | quantity | price | revenue |
|---|---|---|---|---|---|---|
| 10401 | 381 | 27 | 20260916 | 4 | 25.00 | 100.00 |

Notice that this table contains lots of numbers and IDs - that's characteristic of a fact table.

**Dimension tables** describe the facts:
```sql
CREATE TABLE warehouse.dim_customer (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100)
);

CREATE TABLE warehouse.dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(200),
    product_category VARCHAR(100),
    product_line VARCHAR(100)
);

CREATE TABLE warehouse.dim_date (
    date_id INT PRIMARY KEY,
    full_date DATE,
    year INT,
    quarter INT,
    month INT,
    month_name VARCHAR(20),
    day_of_week VARCHAR(20)
);
```
Now analysts can write very intuitive queries:
```sql
SELECT
    d.year,
    d.month,
    p.product_category,
    SUM(f.revenue) AS revenue
FROM warehouse.fact_sales f
JOIN warehouse.dim_date d
    ON f.date_id = d.date_id
JOIN warehouse.dim_product p
    ON f.product_id = p.product_id
GROUP BY
    d.year,
    d.month,
    p.product_category
ORDER BY
    d.year,
    d.month,
    revenue DESC;
```
That's fundamentally what a warehouse is about: organizing historical data so analytical questions are easy and efficient to answer.

## How Data Gets Into It (a Primitive ETL Pipeline)

A simple Python/Pandas pipeline for feeding a warehouse:
```
Postgres operational tables
          |
          | Extract
          v
       Pandas
          |
          | Transform
          v
Clean / aggregate / validate
          |
          | Load
          v
Postgres warehouse tables
```
```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://student:password@localhost/sample_database"
)

orders = pd.read_sql("SELECT * FROM orders", engine)
order_details = pd.read_sql("SELECT * FROM orderdetails", engine)

sales = order_details.merge(orders, on="order_number")

sales["revenue"] = (
    sales["quantity_ordered"] *
    sales["price_each"]
)

sales.to_sql(
    "fact_sales",
    engine,
    schema="warehouse",
    if_exists="append",
    index=False
)
```
That's a primitive ETL pipeline feeding a data warehouse - extract via `pd.read_sql`, transform via a Pandas `merge` + calculated column, load via `to_sql`. See `Training 2.md` for the underlying Pandas concepts (`merge`, DataFrame column math).

## So Why Not Just Use PostgreSQL?

For a small company, you sometimes can - PostgreSQL is mature, reliable, inexpensive, and extremely capable. A warehouse containing 1 million, 10 million, or even 50 million rows may work perfectly well in PostgreSQL with good schema design, indexes, partitioning, sufficient hardware, and well-written queries.

The problem becomes apparent as the analytical workload grows. Imagine:
```sql
SELECT
    country,
    product_category,
    DATE_TRUNC('month', order_date),
    SUM(revenue)
FROM enormous_sales_table
GROUP BY
    country,
    product_category,
    DATE_TRUNC('month', order_date);
```
Suppose `enormous_sales_table` contains 20 billion rows. An index isn't necessarily going to save you here, because you aren't asking for a handful of records - you actually want to process a huge portion of the table. That's fundamentally different from:
```sql
SELECT * FROM customers WHERE customer_id = 12345;
```
PostgreSQL is traditionally optimized around general-purpose relational/transactional workloads, while modern analytical systems make architectural choices specifically for enormous scans and aggregations.

## Redshift (Columnar Storage)

Amazon Redshift is AWS's cloud data warehouse. One of the big differences is that Redshift uses a **column-oriented architecture**.

Consider this table:

| customer | country | product | quantity | price |
|---|---|---|---|---|
| Alice | USA | Laptop | 1 | 1200 |
| Bob | Canada | Mouse | 4 | 25 |
| Carol | USA | Monitor | 2 | 300 |

Traditional **row-oriented** storage conceptually stores each full row together:
```
Alice, USA, Laptop, 1, 1200
Bob, Canada, Mouse, 4, 25
Carol, USA, Monitor, 2, 300
```
**Column-oriented** storage instead groups each column together:
```
customer: Alice, Bob, Carol
country:  USA, Canada, USA
product:  Laptop, Mouse, Monitor
quantity: 1, 4, 2
price:    1200, 25, 300
```
Now consider:
```sql
SELECT SUM(price) FROM sales;
```
The analytical engine mostly cares about the `price` column - it doesn't necessarily need to read all the other columns. Across billions of rows, that's enormously valuable. Columnar data also tends to compress extremely well, further reducing how much data must be read.

## Snowflake (Separated Storage & Compute)

Snowflake made another architectural idea extremely popular: **separating storage from compute**.
```
                 STORAGE
              All company data
                     |
        +------------+------------+
        |            |            |
        v            v            v
   Warehouse A   Warehouse B   Warehouse C

   Analysts      Data Eng.       Finance
   compute       compute         compute
```
The data doesn't have to live on the same machine that's executing the query - you can scale compute separately. If finance needs huge computational resources at month end, you can increase its compute without rebuilding the entire storage architecture. When nobody needs that compute, it can be reduced or suspended. This architecture is extremely attractive in cloud environments.

## Databricks (The Lakehouse)

Databricks comes from a somewhat different lineage - its roots are closely associated with Apache Spark and large-scale distributed data processing. Instead of thinking only "database -> warehouse," Databricks helped popularize the modern **lakehouse** approach:
```
             Object Storage
          S3 / ADLS / GCS
                  |
                  v
             Delta Lake
                  |
       +----------+-----------+
       v          v           v
      SQL       Spark         ML
 Analytics       ETL          AI
```
Data can live cheaply in cloud object storage using formats such as Parquet and Delta. Then distributed compute processes it:
```python
df = spark.read.format("delta").load("/sales")

result = (
    df.groupBy("country")
      .sum("revenue")
)
```
Instead of one PostgreSQL server doing all the work, Spark can distribute processing across many workers:
```
                   Query
                     |
          +----------+----------+
          |                     |
       Worker 1              Worker 2
    rows 1-500M            rows 500M-1B
          |                     |
          +----------+----------+
                     |
                   Result
```
Real systems are considerably more sophisticated, but that's the basic idea students should understand.

## PostgreSQL vs Redshift vs Snowflake vs Databricks

| System | Best mental model |
|---|---|
| PostgreSQL | General-purpose relational database |
| Redshift | AWS distributed analytical warehouse |
| Snowflake | Cloud-native analytical data platform with separated storage/compute |
| Databricks | Lakehouse platform combining data engineering, SQL analytics, ML and AI |

The important point isn't that PostgreSQL is bad for analytics - it isn't. It's that eventually the requirements change. You go from *"Store our company's sales data"* to *"Scan 8 TB of sales data, join it against customer and advertising data, calculate 30 metrics, and let 200 analysts do this simultaneously."* At that point, specialized analytical architecture becomes much more attractive.

## A Good Progression for Students

The technologies covered actually form a natural progression:
```
PostgreSQL
    |
SQL fundamentals
    |
Joins / Aggregations
    |
CTEs / Window Functions
    |
Indexes / Query Plans
    |
Dimensional Modeling
    |
Fact + Dimension Tables
    |
ETL / ELT
    |
Data Warehouse
    |
Distributed / Cloud Warehouses
    |
Redshift / Snowflake
    |
Spark / Databricks / Lakehouse
```
The underlying problem remains remarkably consistent: take data from different places, organize it reliably, and make large amounts of it easy and fast to analyze. The newer platforms largely exist because doing that for terabytes or petabytes of data, many simultaneous users, and modern ML/AI workloads requires architectural capabilities that a conventional single PostgreSQL deployment wasn't primarily designed to provide.