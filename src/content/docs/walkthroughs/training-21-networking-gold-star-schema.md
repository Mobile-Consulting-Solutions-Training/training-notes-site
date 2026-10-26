---
title: "Walkthrough - Training 21: Networking, Gold Star Schema and Analytics"
description: "VPC networking for Glue to Redshift, the S3 Gateway Endpoint fix, the Gold star schema, validation and analytical queries."
sidebar:
  order: 210
---

Source material: [Training 21 notes](/training-notes-site/notes/training-21/) . Deep dive for the modeling part: [Deep Dive - Star Schema (Facts and Dimensions)](/training-notes-site/walkthroughs/star-schema-deep-dive/). 

**How to use this:** read it top to bottom once. It's the last stage of the pipeline: getting Silver into Redshift, shaping it into Gold, and finally asking it questions. Then do the self-check.

---

## The one-paragraph version

Yesterday's Glue → Redshift job died with a **networking** error. Today Evan explained why: Redshift lives in a private network (a **VPC**), so Glue had to join that network, and from inside it there was **no road to S3**. An **S3 Gateway Endpoint** builds that road. The next run hit an **authorization** error (the Glue role couldn't write its temporary files to S3), fixed with one more policy, and then **data landed in Redshift**. Students got the permissions they'd been missing (EventBridge Scheduler, the query editor, Secrets Manager). Evan reshaped the loaded table into a **star schema** in a `gold` schema (two dimensions and one fact), **validated** it (counts, orphans, duplicates), and ran **analytical queries** that answered real questions: where can I find a bike, which stations run empty. With only 100 rows it's a demo, so the weekend homework is to rebuild it yourself and let the ingestion run to collect more data.

---

## You already know most of this

| You did this before | Class | Today's version |
|---|---|---|
| Your home network behind a router | Life | A **VPC** with subnets and route tables |
| The server you SSH into (`jackserver`) | Training 1 / your setup | Resources in a subnet, reached through rules |
| `chmod` / file permissions | Training 1 | **Security groups** (who may connect) |
| IAM `AccessDenied` | Training 19–20 | **Authorization** errors, now from Glue's role |
| Star schema theory | Training 5 | Built for real: `gold.dim_station`, `gold.dim_date`, `gold.fact_station_snapshot` |
| `ROW_NUMBER()` window function | SQL classes | `QUALIFY ROW_NUMBER() ... = 1` to dedup |
| GROUP BY / HAVING | SQL classes | Validation and analytical queries |
| dbt tests (unique, relationships) | Training 17 | The same checks written by hand |

---

## Part 1: The networking problem (why yesterday failed)

### The diagram, as a story

Picture an office building (the **VPC**). Redshift works on one floor (a **subnet**). The building has no doors to the street unless you add them. S3 isn't in the building; it's a giant public warehouse across town.

1. To talk to Redshift, Glue has to **work on the same floor**. The **Glue connection** does that: it gives Glue a desk (an **ENI**, a virtual network card) in Redshift's subnet.
2. But Glue also has to fetch its **script** and the **Silver data** from S3, across town. From that floor there's **no way out**: no front door (Internet Gateway), no mail room (NAT Gateway).
3. Before starting, Glue checks for a way to reach S3, finds none, and refuses: **"Could not find S3 endpoint or NAT gateway for subnet."**
4. The fix is a **private tunnel** from the building straight to S3: an **S3 Gateway Endpoint**. It's free and never touches the public internet. It works by adding a line to the subnet's **route table**: "traffic for S3 → the endpoint."

### Evan's key points

- **S3 sits outside the VPC** because it's a global object store "designed for availability."
- **Services that talk to each other should be in the same VPC**, like having them on one local network instead of going out to the internet and back.
- **A VPC is mainly a security concept:** one controlled point of entry, secured to cloud standards. "The cloud forces you to practice strong security, as we're finding out firsthand."
- **Subnets** group services that talk to each other and isolate them from those that shouldn't.
- The error message was a *good* one: reason, subnet ID, VPC ID, error code, request ID, "everything a knowledgeable person, or more likely an AI, needs to diagnose it."

### The seven terms (Evan's list) in one table

| Term | Building analogy | One line |
|---|---|---|
| VPC | The building | Your isolated private network in AWS |
| Subnet | A floor | A slice of the VPC's IP range, in one Availability Zone |
| Route table | Hallway signs | Rules for where traffic goes |
| Internet Gateway | Front door to the street | Two-way internet access for public subnets |
| NAT Gateway | Mail room | Private resources can send out and get replies; nobody walks in. Costs money |
| VPC Endpoint | Private tunnel to an AWS service | Reach S3/DynamoDB (gateway, free) or other services (interface, paid) privately |
| Security Group | Guard at each office door | Stateful firewall on a resource; allow rules only |

**Two corrections to class examples:** opening SSH to your IP is a **security group** rule (not the route table), and `ssh morty-c137` resolving to an IP is **name resolution** (DNS/SSH config/Tailscale), not NAT.

---

## Part 2: The next error was progress

After the networking fix, the job got further and failed differently: the Glue role wasn't allowed to **write temporary files to S3** (the TempDir it stages data in before Redshift `COPY`s it). Evan's distinction:

| | Authentication | Authorization |
|---|---|---|
| Question | Who are you? | What may you do? |
| Today's example | Redshift username/password, invalid token | Glue role denied `s3:PutObject` on the TempDir |
| Fix | Fix the credentials | Add a policy |

He fixed it with an inline policy (`aws iam put-role-policy`) and **verified before rerunning** with `aws iam simulate-principal-policy` (asks IAM "would this be allowed?" without doing it). The rerun **succeeded**, and `SELECT * FROM public.citibike_station_snapshot` showed rows.

**The pattern of the whole two days:** networking error → authorization error → success. Each fix moved the job one step further. **A new, different error after a fix usually means progress.**

---

## Part 3: Permissions for students (and why it takes weeks at real jobs)

| Students hit | Evan added to the group policy |
|---|---|
| `scheduler:CreateSchedule` denied | `scheduler:*` + PassRole to `scheduler.amazonaws.com` |
| Query editor: `sqlworkbench:GetAccountInfo` | `sqlworkbench:*` (the editor is a separate service prefix) |
| Query editor can't list workgroups: `tag:GetResources` | `tag:*` |
| Query editor connection via Secrets Manager | `secretsmanager:*` |

Still not granted: creating roles/policies (`iam:CreateRole`). You can **attach** existing roles, not make new ones.

**Secrets Manager** (Evan: it comes up in interviews): stores credentials encrypted, once; services read them at runtime with permission; supports automatic rotation and auditing. Better than passwords in code or config.

**Why access takes weeks in real companies:** the person who can grant it is busy, often makes one change at a time, and each new blocker restarts the process. Lesson: when you ask, include the **exact action, resource and role** from the error, and figure out **everything** the job needs before asking.

### Your hands-on lesson: two layers of permission in Redshift

Connecting to Evan's workgroup gave `permission denied for relation citibike_station_snapshot`:

| Layer | Controls | You |
|---|---|---|
| IAM | Using the editor, connecting to the workgroup | ✅ Passed |
| Database (`GRANT`) | Which database user may read which table | ❌ The table belongs to Evan's admin user |

That's why you created **your own** workgroup (`<initials>-citibike-wg`, namespace `<initials>-citibike-ns`, admin user set up front). Tables you create there are yours.

---

## Part 4: Building Gold as a star schema

Evan's goal: "the full star schema in Redshift and the ability to ask it analytical queries that tell us something interesting... As of now, we haven't actually analyzed anything."

### Step 0: Profile before you model

```sql
SELECT COUNT(*), COUNT(DISTINCT station_id), MIN(snapshot_ts), MAX(snapshot_ts)
FROM public.citibike_station_snapshot;
```

**100 rows, 97 stations, Oct 7 6:28 PM → Oct 8 8:55 PM** (UTC). Then a duplicate check (`GROUP BY station_id, snapshot_ts HAVING COUNT(*) > 1`): 0 rows.

Along the way: **WHERE filters rows before grouping; HAVING filters groups after aggregation** (a common interview question).

### Step 1: Create the schema and tables (dimensions first)

```
                dim_station  (97 rows: station_id, station_name, capacity)
                     │
                     ▼
         fact_station_snapshot (100 rows: station_id, date_key, snapshot_ts,
                                bikes/ebikes/docks available, utilization_pct,
                                is_empty, is_full, is_operational; DISTKEY/SORTKEY)
                     ▲
                     │
                 dim_date  (2 rows: date_key 20261007/20261008, date parts, day_of_week)
```

- A separate **`gold` schema** keeps Gold apart from the raw loaded table in `public`.
- **Dimensions before facts:** the fact references them through foreign keys. In Redshift, keys are **informational only, not enforced**, so you have to check them yourself.
- `DESCRIBE TABLE` failed: **Redshift has no DESCRIBE**. Use `information_schema.columns` or the sidebar.
- **DISTKEY** decides which node a row lives on (join locality); **SORTKEY** decides storage order (skip blocks when filtering).
- Natural `station_id` used as the key "to keep the model deliberately simple" (no surrogate key yet).

### Step 2: Load each table with ELT SQL

| Table | Load | Key idea |
|---|---|---|
| `dim_station` | `TRUNCATE` + `INSERT ... SELECT ... QUALIFY ROW_NUMBER() OVER (PARTITION BY station_id ORDER BY snapshot_ts DESC) = 1` | **Latest record per key**: one row per station → 97 |
| `dim_date` | `TRUNCATE` + `INSERT ... SELECT DISTINCT` date parts with `EXTRACT`, `date_key = CAST(TO_CHAR(ts,'YYYYMMDD') AS INT)` | Identical rows collapse → 2 days |
| `fact_station_snapshot` | `TRUNCATE` + `INSERT ... SELECT` + `date_key` + dedup on `(station_id, snapshot_ts)` | One row per station per snapshot → 100; **capacity moved to the dimension** |

**Interview questions hidden in this step:**
- **DELETE vs TRUNCATE vs DROP:** delete chosen rows (slow, row by row) / empty the whole table fast (structure stays) / remove the table entirely.
- **QUALIFY:** filters window-function results, the way WHERE filters rows and HAVING filters groups.
- **SELECT DISTINCT vs QUALIFY:** identical rows vs duplicates by key where you pick which one survives.
- **ETL vs ELT:** this step is ELT: transform with SQL inside the warehouse after loading.

### Step 3: Validate

| Check | Query shape | Result |
|---|---|---|
| Row counts | `SELECT 'x', COUNT(*) ... UNION ALL ...` | 100 / 97 / 2 |
| Orphaned facts | `fact LEFT JOIN dim ... WHERE dim.key IS NULL` | 0 |
| Duplicate facts | `GROUP BY station_id, snapshot_ts HAVING COUNT(*) > 1` | 0 |

Why: "so that we can be sure nothing is wrong with the data before we do anything more advanced with it." Redshift won't enforce keys, and a successful insert only proves rows went in.

### Why a star at all? (Evan's question to the class)

> "It's a dimensional data model, which is basically the **gold standard for how to organize analytical data**. The most central information is stored in the fact table, at the center. Information that expands on the facts is in the dimension tables. Anything that relates the fact table to anything else, we achieve by joining."

The fuller answer (grain, no repeated descriptions, business logic defined once, simple and fast queries, consistent answers, managed history) is in the deep-dive file.

---

## Part 5: Asking the data questions

All five queries follow the same shape: **fact in the middle, join a dimension if you need descriptions, group, aggregate, order.**

| # | Question | Technique | What it said (100 rows) |
|---|---|---|---|
| 1 | Where am I most likely to find a bike? | `AVG(bikes_available)` by station, `HAVING COUNT(*) >= 2` | 78 Ave & Queens Blvd (~23 of 29), Arlington Ave & Warwick St, W 181 St & Fort Washington |
| 2 | Which stations are most often empty? | `SUM(CASE WHEN is_empty THEN 1 ELSE 0 END)`, `100.0 * ... / NULLIF(COUNT(*),0)` | Several at 100%, but each had only 1 observation |
| 3 | How does availability change by hour? | `EXTRACT(HOUR FROM snapshot_ts)` | ~48% → 55% over three hours |
| 4 | Which stations may have operational problems? | Same conditional % on `is_operational = false` | Only 0% or 100% (too little data) |
| 5 | How do days compare? | Group by `calendar_date`, `COUNT(DISTINCT station_id)` | Avg 20 bikes Wed vs 15 Thu |

**Three things to catch that class didn't fully cover:**
1. **Hours are UTC.** Hours 18–20 are **2–4 PM in New York**, not 6–8 PM. The "fewer riders after 8 PM" guess doesn't follow from this data. Convert with `CONVERT_TIMEZONE('UTC', 'America/New_York', snapshot_ts)`.
2. **`HAVING COUNT(*) >= 2` counts snapshots, not bikes.** It hides stations observed only once, so their averages aren't based on a single moment.
3. **Percentages need context.** With one observation, every percentage is 0% or 100%. And a 70-dock station (the one by the UN) shows low *utilization %* even with many bikes out. A classmate caught this: "Good catch." Always show counts and absolute numbers next to percentages.

**SQL "design patterns"** (a student question): Evan hadn't thought of SQL that way, but there are named ones. The factory pattern maps to **stored procedures** (saved, callable SQL steps), and the observer pattern to **triggers / CDC**, plus MERGE/upsert, latest-record-per-key, anti-join, conditional aggregation and the star schema itself.

---

## Part 6: The bigger picture Evan painted

- Data engineers often analyze data too (BI tools like Power BI, Tableau, QuickSight) and feed ML/AI. "Data engineering bleeds into all of its adjacent fields."
- **"Full stack AI":** DevOps (**Terraform** day next week) → pipelines (this week) → analysis → ML and generative AI → MLOps (**MLflow**, if time allows).
- On learning: nobody remembers it all. The achievable goal is to **understand conceptually what the steps are and how they fit together**, and look up the details.

---

## The whole pipeline, finished

```
EventBridge Scheduler (every 5 min)
        │  role: scheduler → lambda:InvokeFunction
        ▼
Lambda ingestion ──▶ S3 bronze/citibike/<feed>/year=/month=/day=/hour=/*.json
                                   │
                    EMR Serverless or Glue (Spark)
                                   ▼
                     S3 silver/ (Parquet, one row per station per snapshot)
                                   │
          Glue job + Glue connection (inside Redshift's VPC subnet)
          ├── reads S3 through the S3 Gateway Endpoint
          ├── stages files in TempDir (needs s3:PutObject)
          ▼
Redshift Serverless (namespace + workgroup)
   public.citibike_station_snapshot  ──ELT SQL──▶  gold.dim_station
                                                   gold.dim_date
                                                   gold.fact_station_snapshot
                                                          │
                                         validation + analytical queries
                                         (next: BI dashboard / Streamlit on Fargate)
```

---

## Pairs people mix up

| These two | The difference |
|---|---|
| Internet Gateway vs NAT Gateway | Two-way public access vs outbound-only for private subnets |
| Gateway endpoint vs interface endpoint | S3/DynamoDB via a route-table entry, free vs most services via an ENI, paid |
| Security group vs NACL | Stateful, per resource, allow-only vs stateless, per subnet, allow + deny |
| Authentication vs authorization | Who you are vs what you may do |
| IAM permission vs database GRANT | Reaching Redshift vs reading a table inside it |
| WHERE vs HAVING vs QUALIFY | Rows vs groups vs window-function results |
| DELETE vs TRUNCATE vs DROP | Chosen rows vs all rows vs the whole table |
| SELECT DISTINCT vs ROW_NUMBER dedup | Identical rows vs duplicates by key |
| Fact vs dimension | Measurements at a grain vs descriptive context |
| UNION vs UNION ALL | Removes duplicate rows vs keeps all |
| ETL vs ELT | Transform before loading vs inside the warehouse after loading |
| DISTKEY vs SORTKEY | Which node a row lives on vs order on disk |

---

## Self-check

<details><summary>1. Why did the Glue job need to be inside Redshift's VPC, and what broke once it was?</summary>

Redshift is in a private network, so Glue had to join it (via the Glue connection) to reach Redshift. From inside the private subnet there was no route to S3 for its script and data.
</details>

<details><summary>2. What fixed it and why that instead of a NAT Gateway?</summary>

An S3 Gateway Endpoint: a free private route to S3 added to the route table. A NAT Gateway also works but costs money and goes through the internet path.
</details>

<details><summary>3. The next error was s3:PutObject denied on the TempDir. Authentication or authorization? Why does Glue write there?</summary>

Authorization. Glue stages data as files in S3, then Redshift loads them with COPY.
</details>

<details><summary>4. You're connected to Evan's workgroup but get "permission denied for relation". Can an IAM change fix it?</summary>

No. It's a database-level permission. The table's owner must GRANT SELECT.
</details>

<details><summary>5. Why did dim_station get 97 rows but the fact table 100?</summary>

Different grains: one row per station vs one row per station per snapshot. Three stations had two snapshots.
</details>

<details><summary>6. What does QUALIFY ROW_NUMBER() OVER (PARTITION BY station_id ORDER BY snapshot_ts DESC) = 1 do?</summary>

Numbers each station's rows from newest to oldest and keeps only #1: the latest record per station.
</details>

<details><summary>7. Name the three validation checks and what each catches.</summary>

Row counts (missing or doubled data), orphaned facts via LEFT JOIN ... IS NULL (facts that would vanish from joined reports), duplicate facts via GROUP BY ... HAVING COUNT(*) > 1 (inflated totals).
</details>

<details><summary>8. Why did several stations show 100% empty?</summary>

Each had only one observation, so any percentage could only be 0% or 100%.
</details>

<details><summary>9. Query 3 showed hours 18, 19, 20. What New York times are those?</summary>

2, 3 and 4 PM EDT (UTC−4).
</details>

<details><summary>10. What's the closest SQL equivalent of the factory pattern?</summary>

A stored procedure: saved, named SQL steps you call instead of rewriting.
</details>

---

## If an interviewer says "walk me through loading your Silver data into a warehouse"

"Silver was Parquet in S3. I loaded it into Redshift Serverless with a Glue job writing through a Glue JDBC connection. Glue stages files in S3 and Redshift bulk-loads them with COPY. Because Redshift sits in a private VPC subnet, the Glue job runs inside that subnet, which meant adding an S3 gateway endpoint so it could still reach S3, and giving its role write access to the staging prefix. Then I modeled Gold as a star schema with ELT SQL in a separate schema: a station dimension deduplicated to the latest record per station with ROW_NUMBER and QUALIFY, a date dimension with an integer YYYYMMDD key, and a fact table at the grain of one row per station per five-minute snapshot. Since Redshift doesn't enforce primary or foreign keys, I validated every load with row counts, an anti-join for orphaned facts, and a duplicate check on the grain. Then I answered questions like which stations run empty most often, keeping in mind that availability is semi-additive and that hours were stored in UTC."
