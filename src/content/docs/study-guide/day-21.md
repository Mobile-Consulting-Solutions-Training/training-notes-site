---
title: Study Guide - Day 21
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 21: Cloud Networking for Glue and Redshift"
sidebar:
  order: 210
---

Study Guide - Day 21 (source: notes/Training 21.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Cloud Networking.** Glue and Redshift sit inside a **VPC** (private network) and subnet; S3 sits outside ("globally available, designed for availability"). Services that talk to each other belong in the same VPC. A VPC is mainly a security concept: one controlled point of entry. **Subnets** group and isolate services. Evan's terms: VPC, subnet, route table (where traffic goes), Internet Gateway (internet route for public resources), NAT Gateway (outbound-only for private subnets), VPC endpoint (private connectivity to AWS services without the internet), security group (stateful virtual firewall). Corrections: opening SSH to your IP is a security group rule, and `ssh hostname` resolving to an IP is name resolution, not NAT.

**Yesterday's Error Decoded.** "Could not find S3 endpoint or NAT gateway for subnet" = the Glue connection put the job inside Redshift's private subnet, which had no route to S3. Fix: an **S3 Gateway Endpoint** (free, added to the subnet's route table). Gateway endpoints exist only for S3 and DynamoDB; interface endpoints cover other services and cost money.

**Authentication vs Authorization.** Authentication = checking you are who you say you are and may access the system. Authorization = what you may do once in. The next Glue error (PutObject denied on the TempDir) was authorization; fixed with `aws iam put-role-policy`, verified with `aws iam simulate-principal-policy`. Then the job succeeded and `public.citibike_station_snapshot` had data. Networking → authorization → success: a new error is often progress.

**Student Permissions Added.** `scheduler:*` + PassRole to `scheduler.amazonaws.com` (EventBridge); `sqlworkbench:*` (Query editor v2 is its own IAM prefix); `tag:*` (editor lists workgroups via tag:GetResources); `secretsmanager:*`. Still no role creation. **Secrets Manager** stores credentials securely for services to read at runtime; it comes up in interviews. In real jobs access takes weeks: be exact about what you need and ask for everything at once.

**Two Permission Layers in Redshift.** IAM decides whether you can reach the workgroup and editor; database `GRANT`s decide which database user can read a table. Connected to Evan's workgroup as a federated user → `permission denied for relation` (needs the owner's `GRANT`). Solution: your own workgroup and namespace with an admin user.

**Data Checks Before Modeling.** Profile: `COUNT(*)`, `COUNT(DISTINCT station_id)`, `MIN/MAX(snapshot_ts)` → 100 rows, 97 stations, Oct 7–8. Duplicates: `GROUP BY station_id, snapshot_ts HAVING COUNT(*) > 1` → none. **WHERE** filters rows before aggregation; **HAVING** filters after aggregation. Query editor's **Limit 100** caps display only. Copy-paste syntax errors fixed by cutting and re-pasting.

**The Gold Star Schema.** Schema `gold`: `dim_station` (station_id VARCHAR PK, station_name, capacity), `dim_date` (date_key YYYYMMDD integer, calendar_date, year/month/day numbers, day_of_week), `fact_station_snapshot` (station_id, date_key, snapshot_ts, bikes/ebikes/docks available, utilization_pct, is_empty, is_full, is_operational; DISTKEY/SORTKEY). Dimensions created first (facts reference them). Redshift keys are informational only, not enforced. No `DESCRIBE` in Redshift (use `information_schema.columns`). **DISTKEY** = which node a row lives on; **SORTKEY** = storage order.

**Loading Gold with ELT SQL.** `TRUNCATE` then `INSERT ... SELECT` (rerunnable). **DELETE** removes chosen rows (row by row), **TRUNCATE** removes all rows (fast, structure stays), **DROP** removes the table. `dim_station` via `QUALIFY ROW_NUMBER() OVER (PARTITION BY station_id ORDER BY snapshot_ts DESC) = 1` (latest record per key) → 97 rows. **QUALIFY** filters window-function results like WHERE filters rows and HAVING filters groups. `dim_date` via `SELECT DISTINCT` + `EXTRACT` → 2 rows. Fact → 100 rows; capacity moved to the dimension; `date_key` = `CAST(TO_CHAR(ts,'YYYYMMDD') AS INT)`. This is ELT (transform inside the warehouse).

**Validation.** Row counts with `UNION ALL` (100/97/2); orphaned facts with `LEFT JOIN ... WHERE dim.key IS NULL` (0); duplicate facts with `GROUP BY ... HAVING COUNT(*) > 1` (0). Why: make sure nothing is wrong before doing anything more advanced.

**Why a Star Schema.** Evan: "a dimensional data model is basically the gold standard for how to organize analytical data." Central measurements in the fact table; descriptive information that expands on them in dimension tables; analysis by joining. Fuller answer: declared grain, no repeated descriptions, logic defined once, simple and fast queries, consistent answers, managed history.

**Analytical Queries.** (1) Most bikes available: `AVG(bikes_available)` by station with `HAVING COUNT(*) >= 2` → 3 stations (Queens ×2, Washington Heights). (2) Most often empty: `SUM(CASE WHEN is_empty THEN 1 ELSE 0 END)`, `100.0 * x / NULLIF(COUNT(*),0)`. (3) By hour: `EXTRACT(HOUR FROM snapshot_ts)`; hours 18–20 are UTC = 2–4 PM EDT. (4) Operational problems: conditional % on `is_operational`. (5) By day: 20 avg bikes Wed vs 15 Thu. Too little data: percentages only 0 or 100. **CASE WHEN** = SQL's if-statement. Query editor's 3-session limit: close tabs or comment out with Cmd+/.

**SQL Patterns and Stored Procedures.** Factory pattern ≈ stored procedure (saved callable SQL steps); observer ≈ triggers/CDC; MERGE/upsert and the star schema are SQL patterns too.

**Big Picture.** Data engineers also analyze (Power BI, Tableau, QuickSight) and feed ML/AI. "Full stack AI": DevOps (Terraform next week) → pipelines → analysis → ML/GenAI → MLOps (MLflow). Understand how the steps fit together; look up details.

**Weekend Homework.** Rebuild the full pipeline on your side: Lambda ingestion → S3, EMR or Glue Bronze → Silver, Silver → Gold in Redshift, a star schema, analytical queries answering natural-language questions. Run the ingestion over the weekend to collect more data.

---

# Part 2: Cheat Sheet

## Networking
- **VPC** (private network) · **subnet** (slice, one AZ) · **route table** (where traffic goes)
- **IGW** (public, two-way) · **NAT** (private → out only, paid) · **VPC endpoint** (private to AWS services)
- **Gateway endpoint** = S3/DynamoDB, route table, free · **Interface endpoint** = ENI, paid
- **Security group** = stateful, per resource, allow-only · **NACL** = stateless, per subnet, allow + deny
- **ENI** = virtual network card (how Glue joins a subnet)
- Error "no S3 endpoint or NAT gateway" → add an **S3 gateway endpoint**

## AuthN / AuthZ
- Authentication = who you are (invalid token, wrong password)
- Authorization = what you may do (AccessDenied) → policy fix → `simulate-principal-policy`

## Redshift Permission Layers
- IAM: reach editor/workgroup (`sqlworkbench:*`, `tag:*`, `redshift-serverless:*`)
- Database: `GRANT SELECT ON table TO user/PUBLIC` (owner only)

## SQL Clauses
- WHERE (rows) → GROUP BY → HAVING (groups) → window functions → QUALIFY (window results)
- DELETE (chosen rows) · TRUNCATE (all rows, fast) · DROP (table)
- SELECT DISTINCT (identical rows) vs `ROW_NUMBER() ... = 1` (dup by key)
- UNION (dedup) vs UNION ALL (keep all)
- No DESCRIBE in Redshift → `information_schema.columns`

## Gold Model
- `gold.dim_station` (97) · `gold.dim_date` (2) · `gold.fact_station_snapshot` (100)
- Grain: station × snapshot · capacity → dimension · `date_key` YYYYMMDD integer
- Dims before facts · keys not enforced · DISTKEY (location) / SORTKEY (order)

## Validation
- Counts (UNION ALL) · orphans (LEFT JOIN … IS NULL) · duplicates (GROUP BY … HAVING > 1)

## Analytics Patterns
- `AVG` semi-additive measures over time (not SUM)
- Conditional count `SUM(CASE WHEN … THEN 1 ELSE 0 END)` · safe % `100.0 * x / NULLIF(n,0)`
- `EXTRACT(HOUR …)` is UTC → `CONVERT_TIMEZONE('UTC','America/New_York', ts)`
- Small samples → 0%/100% · compare absolute numbers with percentages

## Reusable SQL
- View (saved query) · materialized view (stored results) · stored procedure (`CALL`) · UDF (function)

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: Why are Glue and Redshift in the same VPC in Evan's diagram, while S3 is outside?
A: Services that talk to each other should share a private network so traffic stays local and secure. S3 is a globally available object store designed for availability, so it normally isn't inside your VPC.

Q: What caused "Could not find S3 endpoint or NAT gateway for subnet" and how is it fixed?
A: The Glue connection made the job run inside Redshift's private subnet, which had no route to S3. You fix it by adding an S3 gateway endpoint to that subnet's route table.

Q: What's the difference between an Internet Gateway and a NAT Gateway?
A: An Internet Gateway gives public resources two-way internet access. A NAT Gateway lets private resources make outbound connections without being reachable from outside, and it costs money.

Q: What's the difference between a gateway endpoint and an interface endpoint?
A: Gateway endpoints exist only for S3 and DynamoDB, work through the route table and are free. Interface endpoints cover most other services, create a network interface in your subnet and are billed.

Q: What's the difference between authentication and authorization?
A: Authentication checks who you are, like credentials or tokens. Authorization decides what you're allowed to do once you're in, like IAM policies.

Q: Why did students need sqlworkbench permissions when they already had Redshift Serverless access?
A: Redshift Query editor v2 is a separate service with its own IAM prefix, sqlworkbench, so redshift-serverless permissions don't cover it.

Q: What is AWS Secrets Manager?
A: A service that stores credentials like database passwords encrypted in one place, so services read them at runtime instead of having them in code. It supports rotation and audit logging.

Q: You can open the query editor but get "permission denied for relation." What's going on?
A: IAM got you in, but inside the database your user hasn't been granted access to that table. The table's owner has to run a GRANT.

Q: What's the difference between WHERE and HAVING?
A: WHERE filters individual rows before any aggregation. HAVING filters groups after a GROUP BY, so it can use aggregates like COUNT.

Q: What does QUALIFY do?
A: It filters on the result of a window function, the way WHERE filters rows and HAVING filters groups. For example, keeping only rows where ROW_NUMBER equals one.

Q: What's the difference between DELETE, TRUNCATE and DROP?
A: DELETE removes specific rows one by one and can use a WHERE. TRUNCATE quickly removes all rows but keeps the table. DROP removes the table itself.

Q: Why create dimension tables before the fact table?
A: The fact table references the dimensions through foreign keys, so the dimensions need to exist and be populated first.

Q: Why did dim_station have 97 rows but the fact table 100?
A: Different grains. The dimension is one row per station; the fact is one row per station per snapshot, and three stations had two snapshots.

Q: Name the three validation checks Evan ran and why.
A: Row counts per table, orphaned facts with a left join where the dimension key is null, and duplicate facts with group by having count greater than one. They make sure the Gold data is correct before analysis, since Redshift doesn't enforce keys.

Q: Why is a star schema used for analytics?
A: It's the gold standard for analytical data. Measurements sit in a central fact table at a declared grain, descriptions sit in dimension tables, so descriptions aren't repeated, business logic is defined once, and every question is a simple fact-plus-joins query.

Q: What does CASE WHEN do and how did Evan use it?
A: It's SQL's if-statement. He used SUM of CASE WHEN is_empty THEN 1 ELSE 0 END to count how often each station was empty, then turned it into a percentage.

Q: What does NULLIF do in a percentage calculation?
A: NULLIF of the count and zero returns null when the count is zero, so dividing gives null instead of a division-by-zero error.

Q: Evan's hourly query showed hours 18 to 20. What do they mean?
A: The timestamps are UTC, so those are 2 to 4 PM New York time, not evening hours.

Q: What's the closest SQL equivalent to the factory design pattern?
A: A stored procedure: saved, named SQL logic you call instead of rewriting the same queries.

Q: What is this weekend's homework?
A: Rebuild the full pipeline on your side: Lambda ingestion into S3, EMR or Glue from Bronze to Silver, Silver to Gold in Redshift as a star schema, and analytical queries, while letting the ingestion run over the weekend to collect more data.
