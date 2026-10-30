---
title: "Code: SQL"
description: "Every SQL example from the notes: Postgres, Hive, Redshift, Snowflake, Databricks and Synapse, grouped by training day."
sidebar:
  order: 8
---

Every SQL example from the notes: Postgres, Hive, Redshift, Snowflake, Databricks and Synapse, grouped by training day. Each example is titled with the question it answers in the notes; the day heading links to the full notes for context. Use the copy button on any block.
**82 examples.**


Code marked "from the class demo (not exact)" in the notes was rewritten from the demo, so check names and paths before running it.

## Training 4: SQL Fundamentals & Data Warehousing

[Open the Training 4 notes](/training-notes-site/notes/training-4/)

### How do you insert multiple rows at once, and how do you filter/select specific columns?

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

### How do you use GROUP BY with the departments/employees_demo tables?

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

### What's the difference between a subquery, a CTE, and a window function?

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

### (Common interview question, per Evan Flint) Write a query to find out what the third highest salary per department is in an employee table.

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

```sql
-- This does NOT work:
SELECT employee_name, department_id, salary,
       RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rank
FROM employees_demo
WHERE rank = 3;
```

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

```sql
SELECT *
FROM (
    SELECT employee_name, department_id, salary,
           DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS salary_rank
    FROM employees_demo
) AS ranked
WHERE salary_rank = 3;
```

### How would you demonstrate the purpose and effect of an index in a live classroom setting, and how do you read the resulting query plan?

```sql
EXPLAIN ANALYZE
SELECT *
FROM orderdetails
WHERE product_number = 'S18_1749';
```

```sql
EXPLAIN ANALYZE
SELECT *
FROM orderdetails
WHERE product_number = 'S18_1749';
```

```sql
CREATE TABLE index_demo AS
SELECT
    i AS id,
    'employee_' || i AS employee_name,
    (random() * 100000)::INTEGER AS salary
FROM generate_series(1, 1000000) AS i;
```

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

### How would you build a small data warehouse (star schema) in PostgreSQL?

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

### Why not just use PostgreSQL as the data warehouse?

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

## Training 5: Data Warehouse Concepts

[Open the Training 5 notes](/training-notes-site/notes/training-5/)

### What does it actually look like to convert the class's operational tables into a warehouse-style star schema?

```sql
-- Dimensions
ALTER TABLE customers RENAME TO dim_customer;
ALTER TABLE employees RENAME TO dim_employee;
ALTER TABLE offices RENAME TO dim_office;
ALTER TABLE products RENAME TO dim_product;

-- Facts
ALTER TABLE orderdetails RENAME TO fact_sales;
ALTER TABLE payments RENAME TO fact_payment;
```

```sql
ALTER TABLE fact_sales RENAME COLUMN quantity TO order_line_number;
ALTER TABLE fact_sales RENAME COLUMN product_category TO quantity;
ALTER TABLE fact_sales ALTER COLUMN quantity TYPE INTEGER USING quantity::INTEGER;
ALTER TABLE fact_sales ADD COLUMN sales_amount NUMERIC(12,2);
UPDATE fact_sales SET sales_amount = price * quantity;
```

```sql
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INTEGER, quarter INTEGER, month INTEGER, month_name VARCHAR(20),
    day INTEGER, day_of_week INTEGER, day_name VARCHAR(20)
);

INSERT INTO dim_date
SELECT TO_CHAR(d, 'YYYYMMDD')::INTEGER, d::DATE,
       EXTRACT(YEAR FROM d)::INTEGER, EXTRACT(QUARTER FROM d)::INTEGER,
       EXTRACT(MONTH FROM d)::INTEGER, TO_CHAR(d, 'FMMonth'),
       EXTRACT(DAY FROM d)::INTEGER, EXTRACT(ISODOW FROM d)::INTEGER, TO_CHAR(d, 'FMDay')
FROM generate_series(
    (SELECT MIN(order_date) FROM orders),
    (SELECT MAX(order_date) FROM orders),
    INTERVAL '1 day'
) d;

ALTER TABLE fact_sales ADD COLUMN order_date_key INTEGER;
UPDATE fact_sales f SET order_date_key = d.date_key
FROM orders o JOIN dim_date d ON o.order_date = d.full_date
WHERE f.order_number = o.order_number;
```

```sql
SELECT p.product_category, SUM(f.sales_amount) AS total_revenue
FROM fact_sales f
JOIN dim_product p ON f.product_number = p.product_number
GROUP BY p.product_category
ORDER BY total_revenue DESC;
```

### What is the difference between SCD Type 1 and SCD Type 2?

```sql
-- Type 1: just overwrite
UPDATE dim_customer
SET city = 'Austin'
WHERE customer_id = 42;   -- no record that the city was ever anything else

-- Type 2: insert a new row, close out the old one
ALTER TABLE dim_customer ADD COLUMN effective_date DATE;
ALTER TABLE dim_customer ADD COLUMN end_date DATE;
ALTER TABLE dim_customer ADD COLUMN is_current BOOLEAN;

UPDATE dim_customer
SET end_date = CURRENT_DATE, is_current = FALSE
WHERE customer_id = 42 AND is_current = TRUE;

INSERT INTO dim_customer (customer_key, customer_id, city, effective_date, end_date, is_current)
VALUES (DEFAULT, 42, 'Austin', CURRENT_DATE, NULL, TRUE);
```

### Which window functions besides ranking should I know?

```sql
SELECT order_date, revenue,
       revenue - LAG(revenue) OVER (ORDER BY order_date)            AS change_vs_prev_day,
       SUM(revenue) OVER (ORDER BY order_date
                          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
       AVG(revenue) OVER (ORDER BY order_date
                          ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)  AS moving_avg_7d
FROM daily_sales;
```

### How do you find and delete duplicate rows?

```sql
-- Find
SELECT email, COUNT(*) FROM customers GROUP BY email HAVING COUNT(*) > 1;

-- Delete all but one copy (Postgres)
DELETE FROM customers
WHERE ctid IN (
    SELECT ctid FROM (
        SELECT ctid, ROW_NUMBER() OVER (PARTITION BY email ORDER BY customer_id) AS rn
        FROM customers
    ) AS d
    WHERE rn > 1
);
```

## Training 8: Spark Partitioning, Salting & Hive Setup

[Open the Training 8 notes](/training-notes-site/notes/training-8/)

### The Lesson Plan: Medallion Migration + First Real ETL Pipeline

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

### How do partitioned Hive tables work in practice, and what does MSCK REPAIR TABLE do?

```sql
CREATE TABLE silver.sales (sale_id INT, amount DECIMAL(12,2))
PARTITIONED BY (sale_date STRING)
STORED AS PARQUET;

-- Dynamic partition insert: partition value comes from the data
SET hive.exec.dynamic.partition.mode=nonstrict;
INSERT INTO silver.sales PARTITION (sale_date)
SELECT sale_id, amount, sale_date FROM bronze.sales;

-- Files were added to storage outside Hive: register them
MSCK REPAIR TABLE silver.sales;                                  -- scan and add all missing partitions
ALTER TABLE silver.sales ADD PARTITION (sale_date='2026-10-01');  -- add one explicitly
```

## Training 15: Cloud Platforms and Snowflake

[Open the Training 15 notes](/training-notes-site/notes/training-15/)

### What is a semantic view?

```sql
CREATE SEMANTIC VIEW sales_analysis
  TABLES (
    sales     AS gold.fact_sales   PRIMARY KEY (sale_id),
    customers AS gold.dim_customer PRIMARY KEY (id)
  )
  RELATIONSHIPS (
    sales (customer_id) REFERENCES customers
  )
  FACTS (
    sales.line_amount AS quantity * unit_price
  )
  DIMENSIONS (
    customers.region AS region
  )
  METRICS (
    sales.total_revenue AS SUM(sales.line_amount)
  );
```

```sql
SELECT * FROM SEMANTIC_VIEW(
  sales_analysis
  DIMENSIONS customers.region
  METRICS sales.total_revenue
);
```

### What is dbt?

```sql
-- models/silver/silver_sales.sql
SELECT sale_id, customer_id, product_id, quantity, unit_price,
       quantity * unit_price AS line_amount
FROM {{ ref('bronze_sales') }}
WHERE sale_id IS NOT NULL
```

## Training 16: Snowflake Dynamic Tables

[Open the Training 16 notes](/training-notes-site/notes/training-16/)

### Setup: daily sales totals

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

### Regular Table

```sql
CREATE TABLE sales_summary AS
SELECT
    product,
    SUM(amount) AS total_sales
FROM sales
GROUP BY product;
```

```sql
CREATE OR REPLACE TABLE sales_summary AS
SELECT
    product,
    SUM(amount) AS total_sales
FROM sales
GROUP BY product;
```

### Dynamic Table - the same scenario

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

### Real-World Example: Bronze -> Silver via a Dynamic Table (teacher's terminal)

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

### What is Time Travel in data engineering?

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

### How do you load data into Snowflake?

```sql
CREATE FILE FORMAT pq TYPE = PARQUET;
CREATE STAGE market_stage FILE_FORMAT = pq;          -- internal stage
COPY INTO raw.market_ticks
  FROM @market_stage
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;          -- already-loaded files are skipped (load metadata kept 64 days)
```

## Training 17: dbt with Snowflake

[Open the Training 17 notes](/training-notes-site/notes/training-17/)

### How does Snowflake RBAC work?

```sql
CREATE ROLE transformer;
GRANT ROLE transformer TO ROLE SYSADMIN;                  -- keep the hierarchy intact
GRANT USAGE ON WAREHOUSE de_wh TO ROLE transformer;
GRANT USAGE ON DATABASE de_class TO ROLE transformer;
GRANT USAGE, CREATE TABLE, CREATE VIEW ON SCHEMA de_class.dbt_dev TO ROLE transformer;
GRANT SELECT ON FUTURE TABLES IN SCHEMA de_class.raw TO ROLE transformer;   -- tables created later too
```

### How do you secure PII in Snowflake?

```sql
CREATE MASKING POLICY email_mask AS (val STRING) RETURNS STRING ->
  CASE WHEN CURRENT_ROLE() IN ('PII_READER') THEN val ELSE '***MASKED***' END;
ALTER TABLE customers MODIFY COLUMN email SET MASKING POLICY email_mask;

CREATE ROW ACCESS POLICY region_rap AS (region STRING) RETURNS BOOLEAN ->
  CURRENT_ROLE() = 'ADMIN' OR region = 'US';             -- often a lookup to a mapping table
ALTER TABLE sales ADD ROW ACCESS POLICY region_rap ON (region);
```

## Training 18: AWS Cloud Fundamentals

[Open the Training 18 notes](/training-notes-site/notes/training-18/)

### How do you ingest data into Redshift?

```sql
COPY sales.orders
FROM 's3://company-gold/orders/'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftS3ReadRole'
FORMAT AS PARQUET;
```

## Training 19: AWS Batch Pipelines

[Open the Training 19 notes](/training-notes-site/notes/training-19/)

### Getting the Spark output into Redshift

```sql
-- Load the night's output into the warehouse
COPY analytics.fact_sales
FROM 's3://company-gold/fact_sales/sale_date=2026-10-07/'
IAM_ROLE '<redshift-role-arn>'
FORMAT AS PARQUET;
```

## Training 21: Cloud Networking for Glue and Redshift

[Open the Training 21 notes](/training-notes-site/notes/training-21/)

### Building the star schema

```sql
SELECT COUNT(*)                   AS total_rows,
       COUNT(DISTINCT station_id) AS stations,
       MIN(snapshot_ts)           AS earliest_snapshot,
       MAX(snapshot_ts)           AS latest_snapshot
FROM public.citibike_station_snapshot;
```

### Data checks before modeling

```sql
SELECT station_id, snapshot_ts, COUNT(*) AS occurrences
FROM public.citibike_station_snapshot
GROUP BY station_id, snapshot_ts
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;
```

### Creating the Gold schema and tables

```sql
CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS gold.dim_station (
    station_id   VARCHAR(64) PRIMARY KEY,   -- a string, not an integer
    station_name VARCHAR(500),
    capacity     BIGINT
)
DISTSTYLE ALL;                              -- small dimension: full copy on every node

CREATE TABLE IF NOT EXISTS gold.dim_date (
    date_key      INTEGER PRIMARY KEY,      -- YYYYMMDD, e.g. 20261008
    calendar_date DATE,
    year_number   INTEGER,
    month_number  INTEGER,
    day_number    INTEGER,
    day_of_week   INTEGER                   -- 0 = Sunday ... 6 = Saturday
)
DISTSTYLE ALL;

CREATE TABLE IF NOT EXISTS gold.fact_station_snapshot (
    station_id       VARCHAR(64),
    date_key         INTEGER,
    snapshot_ts      TIMESTAMP,
    bikes_available  BIGINT,
    ebikes_available BIGINT,
    docks_available  BIGINT,
    utilization_pct  DOUBLE PRECISION,
    is_empty         BOOLEAN,
    is_full          BOOLEAN,
    is_operational   BOOLEAN
)
DISTKEY (station_id) SORTKEY (snapshot_ts);
```

### Why didn't DESCRIBE TABLE gold.dim_date work?

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'gold' AND table_name = 'dim_date';
-- or
SELECT * FROM pg_table_def WHERE schemaname = 'gold' AND tablename = 'dim_date';  -- needs schema on search_path
```

### How do you upsert (incrementally load) into Redshift?

```sql
-- 1. Stage the new batch
CREATE TEMP TABLE stage (LIKE gold.fact_station_snapshot);
COPY stage FROM 's3://<bucket>/silver/station_status/batch=<id>/'
IAM_ROLE '<redshift-role-arn>' FORMAT AS PARQUET;

-- 2a. MERGE (supported in Redshift since 2023)
MERGE INTO gold.fact_station_snapshot
USING stage s
ON gold.fact_station_snapshot.station_id = s.station_id
   AND gold.fact_station_snapshot.snapshot_ts = s.snapshot_ts
WHEN MATCHED THEN UPDATE SET bikes_available = s.bikes_available,
                             docks_available = s.docks_available
WHEN NOT MATCHED THEN INSERT VALUES (s.station_id, s.date_key, s.snapshot_ts,
    s.bikes_available, s.ebikes_available, s.docks_available,
    s.utilization_pct, s.is_empty, s.is_full, s.is_operational);

-- 2b. Older equivalent: delete + insert in one transaction
BEGIN;
DELETE FROM gold.fact_station_snapshot USING stage s
WHERE gold.fact_station_snapshot.station_id = s.station_id
  AND gold.fact_station_snapshot.snapshot_ts = s.snapshot_ts;
INSERT INTO gold.fact_station_snapshot SELECT * FROM stage;
COMMIT;
```

### Populating dim_station: one row per station

```sql
TRUNCATE TABLE gold.dim_station;

INSERT INTO gold.dim_station (station_id, station_name, capacity)
SELECT station_id, station_name, capacity
FROM public.citibike_station_snapshot
WHERE station_id IS NOT NULL              -- a row without a station ID is invalid
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY station_id
    ORDER BY snapshot_ts DESC, station_name DESC, capacity DESC
) = 1;                                    -- keep only the newest row per station
```

### What does QUALIFY do?

```sql
SELECT station_id, station_name, capacity
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY station_id ORDER BY snapshot_ts DESC) AS rn
    FROM public.citibike_station_snapshot
    WHERE station_id IS NOT NULL
) t
WHERE rn = 1;
```

### Populating dim_date

```sql
TRUNCATE TABLE gold.dim_date;

INSERT INTO gold.dim_date (date_key, calendar_date, year_number, month_number, day_number, day_of_week)
SELECT DISTINCT
    CAST(TO_CHAR(snapshot_ts, 'YYYYMMDD') AS INT) AS date_key,      -- e.g. 20261008
    CAST(snapshot_ts AS DATE)                    AS calendar_date,
    EXTRACT(YEAR  FROM snapshot_ts)              AS year_number,
    EXTRACT(MONTH FROM snapshot_ts)              AS month_number,
    EXTRACT(DAY   FROM snapshot_ts)              AS day_number,
    EXTRACT(DOW   FROM snapshot_ts)              AS day_of_week     -- 0 = Sunday ... 6 = Saturday
FROM public.citibike_station_snapshot
WHERE snapshot_ts IS NOT NULL;
```

### Validating the star schema

```sql
SELECT 'dim_station' AS table_name, COUNT(*) AS row_count FROM gold.dim_station
UNION ALL
SELECT 'dim_date', COUNT(*) FROM gold.dim_date
UNION ALL
SELECT 'fact_station_snapshot', COUNT(*) FROM gold.fact_station_snapshot;
```

```sql
SELECT COUNT(*) AS orphaned_facts
FROM gold.fact_station_snapshot f
LEFT JOIN gold.dim_station s ON f.station_id = s.station_id
WHERE s.station_id IS NULL;
```

```sql
SELECT station_id, snapshot_ts, COUNT(*)
FROM gold.fact_station_snapshot
GROUP BY station_id, snapshot_ts
HAVING COUNT(*) > 1;
```

### Query 1: Which stations have the most bikes available?

```sql
SELECT s.station_name,
       s.capacity,
       ROUND(AVG(f.bikes_available), 0) AS avg_bikes_available,
       ROUND(AVG(f.utilization_pct), 0) AS avg_utilization_pct,
       COUNT(*)                         AS observations
FROM gold.fact_station_snapshot f
JOIN gold.dim_station s ON f.station_id = s.station_id
GROUP BY s.station_id, s.station_name, s.capacity
HAVING COUNT(*) >= 2
ORDER BY avg_bikes_available DESC
LIMIT 15;
```

### Query 2: Which stations are most frequently empty?

```sql
SELECT s.station_name,
       COUNT(*)                                                           AS observations,
       SUM(CASE WHEN f.is_empty THEN 1 ELSE 0 END)                        AS empty_observations,
       ROUND(100.0 * SUM(CASE WHEN f.is_empty THEN 1 ELSE 0 END)
             / NULLIF(COUNT(*), 0), 1)                                    AS pct_observations_empty
FROM gold.fact_station_snapshot f
JOIN gold.dim_station s ON f.station_id = s.station_id
GROUP BY s.station_id, s.station_name
ORDER BY pct_observations_empty DESC;
```

### What is CASE WHEN?

```sql
CASE
    WHEN condition_1 THEN result_1      -- like: if
    WHEN condition_2 THEN result_2      -- like: elif
    ELSE default_result                  -- like: else (NULL if omitted)
END
```

### Query 3: How does bike availability change by hour?

```sql
SELECT EXTRACT(HOUR FROM f.snapshot_ts)   AS hour_utc,
       ROUND(AVG(f.bikes_available), 0)   AS avg_bikes,
       ROUND(AVG(f.utilization_pct), 0)   AS avg_utilization,
       COUNT(*)                           AS observations
FROM gold.fact_station_snapshot f
GROUP BY EXTRACT(HOUR FROM f.snapshot_ts)
ORDER BY hour_utc;
```

### Query 4: Which stations may have operational problems?

```sql
SELECT s.station_name,
       COUNT(*)                                                     AS observations,
       SUM(CASE WHEN f.is_operational = FALSE THEN 1 ELSE 0 END)    AS non_operational_observations,
       ROUND(100.0 * SUM(CASE WHEN f.is_operational = FALSE THEN 1 ELSE 0 END)
             / NULLIF(COUNT(*), 0), 1)                              AS pct_non_operational
FROM gold.fact_station_snapshot f
JOIN gold.dim_station s ON f.station_id = s.station_id
GROUP BY s.station_id, s.station_name
-- HAVING COUNT(*) >= 2      (removed: not enough data)
ORDER BY pct_non_operational DESC
LIMIT 20;
```

### What is a stored procedure?

```sql
CREATE OR REPLACE PROCEDURE gold.refresh_dim_station()
AS $$
BEGIN
    TRUNCATE TABLE gold.dim_station;
    INSERT INTO gold.dim_station (station_id, station_name, capacity)
    SELECT station_id, station_name, capacity
    FROM public.citibike_station_snapshot
    WHERE station_id IS NOT NULL
    QUALIFY ROW_NUMBER() OVER (PARTITION BY station_id ORDER BY snapshot_ts DESC) = 1;
END;
$$ LANGUAGE plpgsql;

CALL gold.refresh_dim_station();
```

## Training 24: Incremental Pipelines

[Open the Training 24 notes](/training-notes-site/notes/training-24/)

### What does the stored procedure's load SQL actually look like?

```sql
CREATE OR REPLACE PROCEDURE public.sp_process_citibike_batch(p_batch_id IN VARCHAR)
AS $$
BEGIN
    -- 1. New observations into the canonical table (one row per business key)
    INSERT INTO public.citibike_station_snapshot (station_id, snapshot_ts, bikes_available, docks_available /* , ... */)
    SELECT station_id, snapshot_ts, bikes_available, docks_available /* , ... */
    FROM (
        SELECT *
        FROM public.citibike_station_snapshot_landing
        WHERE batch_id = p_batch_id
          AND station_id IS NOT NULL AND snapshot_ts IS NOT NULL
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY station_id, snapshot_ts
            ORDER BY station_name DESC NULLS LAST, capacity DESC NULLS LAST
        ) = 1
    ) src
    WHERE NOT EXISTS (
        SELECT 1 FROM public.citibike_station_snapshot tgt
        WHERE tgt.station_id = src.station_id AND tgt.snapshot_ts = src.snapshot_ts
    );

    -- 2. Missing dates into gold.dim_date      (same NOT EXISTS pattern)
    -- 3. Missing stations into gold.dim_station (latest row per station via QUALIFY)
    -- 4. Missing fact rows into gold.fact_station_snapshot (NOT EXISTS on station_id + snapshot_ts)
END;
$$ LANGUAGE plpgsql;
```

```sql
CREATE TEMP TABLE batch_src AS
SELECT *
FROM public.citibike_station_snapshot_landing_v2
WHERE batch_id = '<batch_id>'
QUALIFY ROW_NUMBER() OVER (PARTITION BY station_id, snapshot_ts ORDER BY station_name DESC NULLS LAST) = 1;

MERGE INTO public.citibike_station_snapshot_v2
USING batch_src AS src
ON  public.citibike_station_snapshot_v2.station_id  = src.station_id
AND public.citibike_station_snapshot_v2.snapshot_ts = src.snapshot_ts
WHEN MATCHED THEN UPDATE SET
     bikes_available = src.bikes_available,
     docks_available = src.docks_available
WHEN NOT MATCHED THEN INSERT (station_id, snapshot_ts, bikes_available, docks_available)
     VALUES (src.station_id, src.snapshot_ts, src.bikes_available, src.docks_available);
```

## Training 25: AI on the Pipeline

[Open the Training 25 notes](/training-notes-site/notes/training-25/)

### Debugging the generated SQL (the most useful part for homework)

```sql
SELECT ds.station_id, ds.station_name, fss.bikes_available
FROM gold.fact_station_snapshot AS fss
JOIN gold.dim_station AS ds ON fss.station_id = ds.station_id
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY fss.station_id
    ORDER BY fss.snapshot_timestamp DESC
) = 1
ORDER BY fss.bikes_available DESC
LIMIT 20;
```

## Training 28: ADF and Databricks Medallion

[Open the Training 28 notes](/training-notes-site/notes/training-28/)

### How did Evan validate Silver?

```sql
SELECT 'bronze' AS layer, COUNT(*) AS row_count FROM <catalog>.bronze.station_status
UNION ALL
SELECT 'silver', COUNT(*) FROM <catalog>.silver.station_history;

DESCRIBE HISTORY <catalog>.silver.station_history;
```

### What was the Gold query?

```sql
SELECT hour, stations_reporting, total_bikes_available,
       total_docks_available, avg_bikes_per_station
FROM <catalog>.gold.hourly_network_availability
ORDER BY total_bikes_available ASC
LIMIT 5;
```

## Training 29: Elasticsearch, ELK and Lakeflow

[Open the Training 29 notes](/training-notes-site/notes/training-29/)

### How do you upsert into Delta, and do SCD Type 2?

```sql
MERGE INTO silver.stations AS t
USING updates AS s
ON t.station_id = s.station_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

### What is time travel?

```sql
DESCRIBE HISTORY silver.stations;                         -- versions, operations, who, when
SELECT * FROM silver.stations VERSION AS OF 12;
SELECT * FROM silver.stations TIMESTAMP AS OF '2026-10-20';
RESTORE TABLE silver.stations TO VERSION AS OF 12;         -- roll back a bad load
```

## Training 30: Delta Lake, Auto Loader and MLflow

[Open the Training 30 notes](/training-notes-site/notes/training-30/)

### How did the Delta demo go? (step by step)

```sql
-- from the class demo (not exact)
%sql
CREATE OR REPLACE TABLE <catalog>.default.delta_demo
USING DELTA
AS
SELECT '001' AS station_id, 10 AS bikes_available
UNION ALL
SELECT '002' AS station_id, 15 AS bikes_available;

DESCRIBE HISTORY <catalog>.default.delta_demo;

UPDATE <catalog>.default.delta_demo
SET bikes_available = 4
WHERE station_id = '001';

-- Time travel by version
SELECT * FROM <catalog>.default.delta_demo VERSION AS OF 0 ORDER BY station_id;

-- The "production mistake": no WHERE clause
UPDATE <catalog>.default.delta_demo SET bikes_available = 0;

-- Recover
RESTORE TABLE <catalog>.default.delta_demo TO VERSION AS OF 1;
```

### What does the MERGE syntax look like?

```sql
-- from the class demo (not exact)
MERGE INTO <catalog>.default.delta_demo AS target
USING (
  SELECT '001' AS station_id, 20 AS bikes_available
  UNION ALL
  SELECT '003' AS station_id, 8 AS bikes_available
) AS source
ON target.station_id = source.station_id
WHEN MATCHED THEN
  UPDATE SET target.bikes_available = source.bikes_available
WHEN NOT MATCHED THEN
  INSERT (station_id, bikes_available)
  VALUES (source.station_id, source.bikes_available);
```

### What did the CDC-style merge do?

```sql
-- from the class demo (not exact)
MERGE INTO <catalog>.default.delta_demo AS target
USING (
  SELECT '001' AS station_id, 12   AS bikes_available, 'UPDATE' AS op
  UNION ALL
  SELECT '002' AS station_id, NULL AS bikes_available, 'DELETE' AS op
  UNION ALL
  SELECT '004' AS station_id, 6    AS bikes_available, 'INSERT' AS op
) AS source
ON target.station_id = source.station_id
WHEN MATCHED AND source.op = 'DELETE' THEN DELETE
WHEN MATCHED THEN UPDATE SET target.bikes_available = source.bikes_available
WHEN NOT MATCHED AND source.op <> 'DELETE' THEN
  INSERT (station_id, bikes_available) VALUES (source.station_id, source.bikes_available);
```

## Training 31: Azure Synapse and Event Hubs

[Open the Training 31 notes](/training-notes-site/notes/training-31/)

### What was the first test query?

```sql
-- from the class demo (not exact)
SELECT @@VERSION       AS sql_version,
       DB_NAME()       AS current_database,
       GETUTCDATE()    AS current_utc_time;
```

### Why couldn't Synapse just read the Bronze JSON?

```sql
-- from the class demo (not exact): the "simplest way" to see JSON in serverless SQL
SELECT TOP 10 doc
FROM OPENROWSET(
        BULK 'https://<storageaccount>.dfs.core.windows.net/bronze/<path>/*.json',
        FORMAT = 'CSV',
        FIELDTERMINATOR = '0x0b',
        FIELDQUOTE      = '0x0b',
        ROWTERMINATOR   = '0x0b'
     ) WITH (doc NVARCHAR(MAX)) AS r;

-- parse it (what the AI's JSON_QUERY version was going for)
SELECT s.station_id, s.num_bikes_available, s.num_docks_available
FROM OPENROWSET(... same as above ...) WITH (doc NVARCHAR(MAX)) AS r
CROSS APPLY OPENJSON(r.doc, '$.data.stations')
     WITH (station_id          VARCHAR(50) '$.station_id',
           num_bikes_available INT         '$.num_bikes_available',
           num_docks_available INT         '$.num_docks_available') AS s;
```

### How did he query the Parquet?

```sql
-- from the class demo (not exact)
USE citibike_analytics;

SELECT TOP 100 *
FROM OPENROWSET(
        BULK 'https://<storageaccount>.dfs.core.windows.net/bronze/silver/station_status/*.parquet',
        FORMAT = 'PARQUET'
     ) AS silver;
```

### What analytics did he run?

```sql
-- from the class demo (not exact)
SELECT TOP 20
       station_id,
       AVG(CAST(num_bikes_available AS FLOAT)) AS avg_bikes_available,
       MAX(num_bikes_available)                AS max_bikes,
       COUNT(*)                                AS observation_count
FROM OPENROWSET(BULK '<silver path>/*.parquet', FORMAT = 'PARQUET') AS s
GROUP BY station_id
ORDER BY avg_bikes_available DESC;
```

```sql
-- from the class demo (not exact)
SELECT snapshot_time,
       COUNT(DISTINCT station_id)  AS active_stations,
       SUM(num_bikes_available)    AS total_bikes,
       SUM(num_docks_available)    AS total_docks
FROM OPENROWSET(BULK '<silver path>/*.parquet', FORMAT = 'PARQUET') AS s
GROUP BY snapshot_time
ORDER BY snapshot_time;
```

### What did he do with views?

```sql
-- from the class demo (not exact)
CREATE OR ALTER VIEW dbo.v_station_availability AS
SELECT station_id, snapshot_time, num_bikes_available, num_docks_available
FROM OPENROWSET(BULK '<silver path>/*.parquet', FORMAT = 'PARQUET') AS s;
GO

SELECT TOP 100 * FROM dbo.v_station_availability;
```

```sql
-- from the class demo (not exact): a CETAS Gold table (needs an external data source + file format defined first)
CREATE EXTERNAL TABLE gold_hourly_availability
WITH (LOCATION = 'gold/hourly_availability/', DATA_SOURCE = citibike_adls, FILE_FORMAT = parquet_format)
AS
SELECT DATEADD(hour, DATEDIFF(hour, 0, snapshot_time), 0) AS snapshot_hour,
       COUNT(DISTINCT station_id) AS stations_reporting,
       SUM(num_bikes_available)   AS total_bikes,
       SUM(num_docks_available)   AS total_docks
FROM dbo.v_station_availability
GROUP BY DATEADD(hour, DATEDIFF(hour, 0, snapshot_time), 0);
```

## Training 32: Microsoft Fabric Lakehouse

[Open the Training 32 notes](/training-notes-site/notes/training-32/)

### What's the difference between SELECT TOP 20 and LIMIT 20?

```sql
-- T-SQL (Azure SQL)
SELECT TOP 20 * FROM dbo.patient_encounters;

-- Data quality check: encounters still missing a discharge date
SELECT
    COUNT(*) AS total_encounters,
    SUM(CASE WHEN discharge_date IS NULL THEN 1 ELSE 0 END) AS missing_discharge_dates
FROM dbo.patient_encounters;
-- Result in class: 10,150 total, 201 missing → 201 patients admitted but not yet discharged
```

## Training 34: GCP Intro, Beam and Storage Transfer

[Open the Training 34 notes](/training-notes-site/notes/training-34/)

### What was Plan B?

```sql
-- from the class demo (not exact)
CREATE DATABASE citibike;
\c citibike
CREATE TABLE IF NOT EXISTS citibike_bronze (
    id           BIGSERIAL PRIMARY KEY,
    source_file  TEXT UNIQUE NOT NULL,
    feed_type    TEXT,
    ingested_at  TIMESTAMPTZ DEFAULT now(),
    payload      JSONB
);
-- check without dumping the huge JSON payloads:
SELECT feed_type, COUNT(*) FROM citibike_bronze GROUP BY feed_type;
```

## Training 35: Dataflow, BigQuery and Looker Studio

[Open the Training 35 notes](/training-notes-site/notes/training-35/)

### How did he create the star schema?

```sql
-- from the class demo (not exact)
CREATE SCHEMA IF NOT EXISTS citibike;     -- a BigQuery "dataset" (bq mk --dataset also works)

CREATE TABLE IF NOT EXISTS citibike.dim_station (
  station_id     STRING NOT NULL,
  station_name   STRING,
  latitude       FLOAT64,
  longitude      FLOAT64,
  capacity       INT64,
  last_updated   TIMESTAMP
);

CREATE TABLE IF NOT EXISTS citibike.fact_station_snapshot (
  station_id           STRING NOT NULL,
  snapshot_ts          TIMESTAMP,
  bikes_available      INT64,
  docks_available      INT64,
  is_renting           BOOL,
  is_returning         BOOL
)
PARTITION BY DATE(snapshot_ts)
CLUSTER BY station_id;
```

### What did the data look like?

```sql
-- from the class demo (not exact)
SELECT COUNT(DISTINCT snapshot_ts)   AS snapshots,
       COUNT(*)                      AS rows_loaded,
       COUNT(DISTINCT station_id)    AS unique_stations,
       MIN(snapshot_ts)              AS first_snapshot,
       MAX(snapshot_ts)              AS last_snapshot,
       SUM(bikes_available)          AS total_bikes_observed
FROM citibike.fact_station_snapshot;
```

### How did he build the dashboard view?

```sql
-- from the class demo (not exact)
CREATE OR REPLACE VIEW citibike.v_station_latest AS
WITH latest AS (
  SELECT *
  FROM citibike.fact_station_snapshot
  WHERE TRUE
  QUALIFY ROW_NUMBER() OVER (PARTITION BY station_id ORDER BY snapshot_ts DESC) = 1
)
SELECT f.station_id,
       d.station_name,
       d.latitude,
       d.longitude,
       d.capacity,
       f.snapshot_ts,
       f.bikes_available,
       f.docks_available,
       ROUND(SAFE_DIVIDE(f.bikes_available, d.capacity) * 100, 1) AS availability_pct
FROM latest f
JOIN citibike.dim_station d USING (station_id);

SELECT * FROM citibike.v_station_latest LIMIT 20;
```

### What analytics queries did he run?

```sql
-- from the class demo (not exact)
SELECT CASE WHEN capacity < 20 THEN 'small'
            WHEN capacity < 40 THEN 'medium'
            ELSE 'large' END            AS size_class,
       COUNT(*)                         AS stations,
       ROUND(AVG(availability_pct), 1)  AS avg_availability_pct
FROM citibike.v_station_latest
GROUP BY size_class
ORDER BY stations DESC;
```

### How did he get the map to work?

```sql
-- from the class demo (not exact)
CREATE OR REPLACE VIEW citibike.v_station_map AS
SELECT station_id,
       station_name,
       bikes_available,
       availability_pct,
       CONCAT(CAST(latitude AS STRING), ',', CAST(longitude AS STRING)) AS map_coordinates
FROM citibike.v_station_latest;
```
