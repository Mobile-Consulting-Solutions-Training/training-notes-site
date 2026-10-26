---
title: "Training 31 - Azure Synapse and Event Hubs"
description: "Azure Synapse Analytics over Databricks Silver Parquet, a small-business on-prem analytics design, and a preview of Event Hubs."
sidebar:
  order: 31
---

Teacher: Evan Flint

Syllabus Day 32 (per file numbering; Fri Oct 23, 2026). The roadmap had Microsoft Fabric for today, but Evan taught the **Synapse + Event Hubs** day (roadmap Day 34) instead.

Source: class notes.

**Code note:** the code below is written from the class demo plus standard Synapse syntax. It is not an exact copy of Evan's code.

---

# Today at a glance

| # | What happened |
|---|---|
| 1 | Plan for the day: Synapse (Evan admits he's not deeply hands-on with it) and Event Hubs (Kafka syntax, quick). Feedback on profile narratives: "a very good foundation", no serious complaints, will tighten over the coming classes |
| 2 | AWS permissions revoked for students, and possibly for Evan too. He has asked the company admin |
| 3 | A student's GCP free-trial tips |
| 4 | Break |
| 5 | Evan's own analytics pipeline design (on-prem: MinIO, DuckDB, Iceberg, Lakekeeper, Streamlit) |
| 6 | Creating a Synapse workspace: the cost check, MPP review, a failed deploy in East US 2, redeploy in Brazil South |
| 7 | Break |
| 8 | Synapse Studio. First serverless query. JSON doesn't work directly. `CREATE DATABASE` because of the `master` error |
| 9 | Databricks notebook: Bronze JSON → flattened, validated Silver **Parquet** |
| 10 | Back in Synapse: query the Parquet, analytics queries, `CREATE VIEW` |

---

# Class admin and heads-ups

Q. What happened with AWS access?

A. (Evan) Students have lost AWS permissions, and Evan may have lost his own admin rights too. "There has been some degree of organizational complaint about the amount of spending that's been going on in the cloud." He may no longer be able to grant permissions himself, so requests now go through the company administrator.

Expanded: what this means for you:

| Situation | What to do |
|---|---|
| You hit `AccessDenied` on something that used to work | It's probably the org-wide permission removal, not something you did. Note the exact error and request ID |
| You need a permission | Ask Evan. He'll pass it to the company admin, so expect a delay |
| Cloud spend | The company is watching costs. Stop or delete anything you don't need, such as Glue jobs, Redshift, EMR and Synapse dedicated pools |

---

Q. What about GCP for personal projects? (from another student)

A. (Student tip) The GCP free trial gives **$300 of credit**, but signing up also takes a **$30 payment** on top of the credit card. It's refunded if you close the account. Their first step was setting up a **budget alert**. GCP can also **forecast** spend and email you when the forecast will exceed your threshold. Their other advice: test locally first before running anything that costs compute.

---

Q. How did Evan rate the profile narratives?

A. (Evan) All of them were "actually really, really" good. Everyone already knows how to look and sound professional in an interview, there were "no serious complaints", and over the coming classes the work is to "gradually tighten them up" and make sure all the details are worked out. "We're already starting on a very good foundation."

---

# Evan's real-world design: small-business analytics on-prem

Q. What problem is Evan solving?

A. (Evan) His media and store business posts videos on **Facebook, Instagram, X, YouTube and Threads** (three of those are Meta). To see how videos are doing he has to check five sites. He wants **one analytics page**. Later he also wants to join social media stats with **store sales**, to see which videos lead to which purchases and why some items don't sell.

Expanded: this is a textbook **multi-source analytics** problem. Several sources with different APIs and permissions feed one model, which feeds one dashboard. Note the practical constraint he raised: some APIs (X in particular) charge a lot for analytics access, so **data availability depends on what the business can afford**. That's a real-world requirement, not a technical one.

---

Q. What's the most important design lesson he took from it?

A. (Teacher's definition) "The best analytics platform is not necessarily the most functional and not necessarily the cheapest. It is the one that provides what the business needs in the way the business needs it."

Expanded: he compared his plan with **Microsoft Fabric** and decided there's "no way you can justify the expense". He already owns the compute and storage (a 5-node on-prem cluster with ~16 TB), so a cloud platform would be paying twice. This is a good interview answer to "how do you choose a platform?": start from the business need, the data size, the budget and the existing infrastructure, not from the most popular tool.

| His cluster node | Role |
|---|---|
| Laptop | Control node |
| Admin node | Logged into from the laptop to manage everything |
| 2 worker nodes | Mostly video exports |
| GX10 ("the big boy") | AI video, image, sound, lip sync |

---

Q. What does his pipeline look like?

A. (Evan) A properly structured **ELT** pipeline. Separate periodic **batch ingestion jobs** per source (each social network plus his own web server) write to a **Bronze layer in MinIO**. Periodic incremental jobs go Bronze → Silver → Gold, and a **Streamlit dashboard** reads Gold. DuckDB is the query engine, Iceberg is the table format, and Lakekeeper is the Iceberg catalog.

```
Facebook / Instagram / Threads (Meta APIs)  ┐
X API                                       │  one batch ingestion job per source
YouTube API                                 │
His VPS (website / store, 1984 in Iceland)  ┘
        │
        ▼
MinIO (on-prem object storage) ── Bronze → Silver → Gold  (incremental, scheduled)
        │        tables in Apache Iceberg format, tracked by Lakekeeper (REST catalog)
        ▼
DuckDB (OLAP SQL engine)
        ▼
Streamlit dashboard: which platform performs best, which drives website traffic,
                     and later which content drives sales
```

Cloud equivalent, to compare against what you already know:

| Layer | Evan's on-prem stack | AWS | Azure |
|---|---|---|---|
| Object storage (lake) | **MinIO** | S3 | ADLS Gen2 |
| Table format | **Apache Iceberg** | Iceberg / Delta on S3 | Delta Lake |
| Catalog | **Lakekeeper** (Iceberg REST catalog) | Glue Data Catalog | Unity Catalog |
| SQL / OLAP engine | **DuckDB** | Athena / Redshift | Synapse serverless SQL / Databricks SQL |
| Dashboard | **Streamlit** | QuickSight | Power BI |
| Server | VPS (1984, Iceland) | EC2 | Azure VM |

---

Q. What is a VPS?

A. (Teacher's definition) VPS stands for **virtual private server**. "When I say VPS, what I'm talking about is EC2 instance, except not on AWS. It's just a computer in the cloud", which you hook up to DNS to host a website.

Expanded: his business website runs on one VPS from the provider **1984** (Iceland). The domain is registered with DNS through **Cloudflare**. He picked Iceland originally for legal reasons that don't apply to this project, so he may move the deployment to the US or Europe, depending on where his customers are. That's the same **data residency** idea that came up later with Synapse.

---

Q. What is MinIO?

A. (Teacher's definition) "MinIO is basically locally hosted object storage. So it's sort of like if you wanted to have storage that is in the style of ADLS, but you want to host it on your own local machine."

Expanded: MinIO speaks the **S3 API**, so anything that can read S3 (Spark, DuckDB, boto3, Iceberg) can read MinIO by changing the endpoint URL. Evan chose it over "the old school Hadoop route" (HDFS + Hive in Docker), which he called "a little bit outdated these days". Object storage plus an open table format is the modern replacement for HDFS + Hive.

| | HDFS + Hive (old way) | MinIO + Iceberg (modern on-prem) |
|---|---|---|
| Storage | HDFS blocks across DataNodes | Objects in buckets (S3 API) |
| Table metadata | Hive Metastore | Iceberg metadata + a catalog (e.g. Lakekeeper) |
| Engines | Hive, Spark | DuckDB, Spark, Trino, anything that speaks S3 + Iceberg |
| Cloud equivalent | EMR with HDFS | S3 / ADLS |

---

Q. What is DuckDB?

A. (Teacher's definition) DuckDB is "an OLAP SQL query engine", a "reasonable way to implement OLAP type analytical databases in a local environment. So no cloud hosting, no nothing."

Expanded: DuckDB is an **in-process** analytical database, the SQLite of analytics. There's no server to run: it's a library inside your Python program (or a single CLI binary). It's columnar and vectorized, so `GROUP BY` and aggregations over millions of rows are fast on one machine, and it can query **Parquet, CSV and JSON files directly**, including from S3 or MinIO.

Evan's open question was why DuckDB isn't as capable "out of the box" as Redshift or Hive. Here's the likely answer. DuckDB alone is just an **engine**: it reads files, but it doesn't manage a shared, versioned set of tables that many jobs write to over time. **Iceberg** adds the table layer (schema, snapshots, ACID commits, time travel, partition evolution), and a **catalog** tells every engine where each table's current state is. Redshift bundles all three (storage, tables, engine) into one product.

| | DuckDB | Redshift / Synapse dedicated |
|---|---|---|
| Runs as | A library or CLI on one machine | A managed MPP cluster |
| Scale | One node (very fast up to ~100s of GB) | Many nodes, TB–PB |
| Cost | Free, open source | Pay per node-hour or per query |
| Tables | Its own file, or external files (+ Iceberg via an extension) | Managed tables |

---

Q. What is Lakekeeper, and why would Iceberg need a REST catalog?

A. (Evan) Lakekeeper's website calls it "a user friendly Apache Iceberg REST catalog". He said he wasn't sure why Iceberg needs REST functionality, but AI recommended it for a fully on-prem pipeline, and he plans to learn it this weekend.

Expanded: an Iceberg table is a set of data files plus metadata files. Every write creates a new metadata file, so something has to hold the single answer to "what is the **current** metadata file for table X?" That something is the **catalog**. It also makes commits atomic, so two writers can't overwrite each other's changes.

The **REST catalog** is Iceberg's standard HTTP API for that job. Any engine that speaks it (DuckDB, Spark, Trino, Flink, PyIceberg) can share the same tables without each needing a special connector. Lakekeeper is an open-source server that implements that API, and it can also handle access control. It plays the role Glue Data Catalog plays on AWS and Unity Catalog plays on Databricks.

```
DuckDB ─┐                        ┌─▶ "orders is at metadata v42" ─┐
Spark  ─┼─ HTTP (Iceberg REST) ─▶ Lakekeeper (catalog)            ├─▶ MinIO: data + metadata files
Trino  ─┘                        └────────────────────────────────┘
```

| Iceberg piece | Job |
|---|---|
| Data files | The rows (usually Parquet) |
| Metadata files | Schema, partitions, list of snapshots |
| Catalog (Lakekeeper / Glue / Unity) | Points to the current metadata file, makes commits atomic |

---

# Azure Synapse Analytics

Q. Where does Synapse fit, and how did Evan frame it?

A. (Teacher's definition) "Synapse is kind of considered in some projects as the older way of doing things and moving everything into Databricks as the newer way. But Synapse is still an available product. It still is used in some tech stacks. And in some cases, you use Databricks and Synapse together in order to do complex pipeline operations." Later: Synapse "basically is the **Azure equivalent of Redshift**."

Expanded: Synapse is Azure's analytics workspace. It's one place with SQL warehousing, Spark, and pipelines (pipelines are ADF built in). Microsoft now steers new projects to **Microsoft Fabric**, but lots of existing companies still run Synapse, so it comes up in Azure interviews.

| Synapse part | What it is | Closest AWS service |
|---|---|---|
| **Serverless SQL pool** (built-in) | Query files in ADLS with T-SQL. Pay per TB scanned. Nothing to provision | Athena / Redshift Spectrum |
| **Dedicated SQL pool** | Provisioned MPP warehouse (formerly Azure SQL Data Warehouse) | Redshift (provisioned) |
| **Apache Spark pool** | Managed Spark for notebooks | EMR / Glue |
| **Pipelines** | ADF inside Synapse | Glue workflows / Step Functions |
| **Synapse Studio** | The web UI for all of the above | Console + Query Editor |

---

Q. Serverless SQL pool vs. dedicated SQL pool?

A. (Teacher's definition) "For Synapse we have one **serverless SQL** warehouse, which is obviously by the name you can tell that it's serverless. And then there's the **dedicated SQL pool**, which is the name of basically an **MPP cluster** for Synapse." The AI cost check flagged the dedicated pool as **high risk**: "That is for professional applications that have serious budgets."

Expanded:

| | Serverless SQL pool | Dedicated SQL pool |
|---|---|---|
| Provisioning | None. Every workspace gets a built-in one | You create it and pick a size (DWU, Data Warehouse Units) |
| Data lives | In files in ADLS (Parquet, CSV, Delta); queried in place | Loaded into the pool's own distributed tables |
| Billing | **Per TB of data processed** (~$5/TB) | **Per hour while running**, even if idle. Pause it to stop compute charges |
| Best for | Exploration, ad-hoc queries, logical views over the lake, cheap class demos | Large, steady, high-performance warehouse workloads |
| Materialized views | ❌ Not supported | ✅ Supported |
| Class risk | Low (Evan used only this) | High. Don't create one |

---

Q. How is serverless SQL billed, and why does it matter?

A. (Teacher's definition) "Notice how it's not per terabyte stored. This is per terabyte **processed**. So we could only have one gigabyte of data stored. But if we were to query that whole data set 1000 times, then that would bring us up to the scale of one terabyte having been processed. And so that would come to $5." Also: "one query does cost something… And pennies add up."

Expanded: the bill counts **bytes your queries read**, not bytes you store. It's the same model as Athena and BigQuery on-demand. The AI's class estimate was 20 students × 20 queries × 1 GB ≈ 400 GB ≈ **$2**. The AI also mentioned a **hard serverless SQL processing limit** (a cost-control setting with daily, weekly and monthly TB caps). Evan didn't set it today.

How to keep it cheap (same tricks as Athena):

| Do | Why |
|---|---|
| Query **Parquet**, not JSON or CSV | Columnar: only the columns you select are read, and it's compressed |
| Select only the columns you need (avoid `SELECT *`) | Less data scanned |
| Partition folders and filter on them | Skips whole folders |
| Create views over aggregated data | Smaller result sets for repeat use |
| Set the processing limit (Manage → SQL pools → Built-in → cost control) | A hard cap on spend |

Storage is billed separately, by the storage account.

---

Q. What is MPP? (review: **common interview question**)

A. (Teacher's definition) "When we talk about MPP, we're not talking about a query engine. We're talking about an **architectural system**… MPP is the kind of architecture that allows you to make the greatest use of parallel computing with existing computer technology." His picture: a mainframe cabinet with slots, each slot a **node**, forming a cluster (10 nodes is plenty for most medium and many large companies). Connect cabinets together so all the nodes can work with each other, keep extending across a data center floor, and you have a large MPP cluster, which at the top end is a **supercomputer**. "All modern data warehouses that are hosted on the cloud are based on MPP architecture": **Redshift, Snowflake, Databricks, Azure Synapse.**

Interview advice from Evan: "If an interviewer asks you to define what MPP is, then you should be able to do that **without looking it up**." Leave out the supercomputer part, since interviewers don't care about it.

A student's answer, which Evan accepted as the right direction: MPP stands for **Massively Parallel Processing**. The data and the query are split into smaller parts that are processed on different **nodes**. ("Nodes" is the word to use in cluster talk, not "servers", even though every node is a server.)

Expanded: full notes are in Training 18 ("What is MPP?"). A version to say out loud in an interview:

> "MPP, massively parallel processing, is a shared-nothing architecture. The data is distributed across many nodes, each with its own CPU, memory and storage. A leader node splits a query into pieces, every node works on its own slice of the data in parallel, and the leader combines the partial results. You scale by adding nodes. Redshift, Snowflake, Synapse dedicated pools and Databricks all use it. The expensive part is moving data between nodes, which is why distribution keys matter."

---

Q. How do you create a Synapse workspace? (what Evan clicked)

A. (Evan, demo) Portal → **Azure Synapse Analytics → Create**:

| Field | What Evan did | Notes |
|---|---|---|
| Resource group | Same resource group as everything else | Keep class resources together for cleanup |
| Managed resource group | Accidentally typed the workspace name here at first, then fixed it | Azure fills this in itself. Leave it blank |
| Workspace name | `synapse-citibike-teacher` (an AI suggestion) | Students: use your own name as the prefix |
| Region | Default was Australia East. Tried **East US 2** (failed, per the error message), then **Brazil South** (succeeded) | See the failure below |
| Data Lake Storage Gen2 | **Use the existing storage account** (the class ADLS) | This is the workspace's **primary storage** |
| File system (container) | Created a **new** one called `synapse` | Synapse's own workspace files go here, not into bronze or silver |
| Cost check | ~$5 per TB processed (serverless) | Asked AI about risks first. Use serverless only |

Then **Create**. Afterwards: Resource group → the workspace → **Open Synapse Studio**.

---

Q. Why did the first deployment fail?

A. (Evan) Error: "**East US 2 is currently not accepting the creation of new Azure SQL database servers** for the subscription in question." That's why the portal had suggested Australia. He redeployed in **Brazil South**, and it succeeded after about 10 minutes.

Expanded: it's an Azure **regional capacity or subscription restriction**, not a mistake in your settings. Behind the scenes, a Synapse workspace creates a SQL server resource, so a region that blocks new SQL servers blocks Synapse. Fixes: pick another region, or ask an admin to request quota. Interview angle: "Deployment fails in one region" → check capacity and quotas, pick a region near the data, and document it.

---

Q. Why is it a problem to have the data in East US and the warehouse in Brazil?

A. (Teacher's definition) "It is definitely not a good idea for a production pipeline for us to have our ADLS data located in the eastern United States and our data warehouse located in Brazil or Australia… That's a very long physical distance for the data to have to travel." And: "The data crosses national borders… Different countries have different laws relating to data. If you have a data pipeline that exists in multiple countries, you need to ensure that the data being stored in each country is compliant with the local laws there."

Expanded: there are two separate problems:

| Problem | Effect |
|---|---|
| **Latency and cost** | Every query pulls data across continents. It's slower, and **cross-region data transfer (egress) is billed** |
| **Data residency / sovereignty** | Laws say where certain data (especially personal data) may be stored or processed |

Laws Evan mentioned. These come up in interviews, more often on the UK side, but also with US companies that do business in Europe:

| Law | Where | Key point |
|---|---|---|
| **GDPR** (General Data Protection Regulation) | EU (servers in Germany, France, Italy, …) | Strict rules on personal data. Consent, right to be forgotten, limits on moving data out of the EU |
| **CCPA / CPRA** (California Consumer Privacy Act, amended by the California Privacy Rights Act) | California | Widely seen as the strictest in the US (other state laws such as Virginia's and Colorado's, and sector laws such as HIPAA, also apply). Evan: "In practice most companies just make the entire country's data California compliant." (He couldn't recall the name in class; this is it) |
| **LGPD** (Lei Geral de Proteção de Dados) | Brazil | Brazil's GDPR-style law. Evan said he's not familiar with it |

Public NYC Citi Bike data has no personal data, so it's fine here. With customer data, region choice is a compliance decision.

---

Q. What's in Synapse Studio?

A. (Evan, demo) Front-page shortcuts: **Ingest, Explore and analyze, Visualize**. Sidebar hubs: **Home, Data, Develop, Integrate, Monitor, Manage**.

| Hub | Use |
|---|---|
| Home | Shortcuts |
| **Data** | Browse **Linked** storage (the ADLS Gen2 account and its containers, e.g. bronze) and workspace databases |
| **Develop** | **SQL scripts**, notebooks, data flows. Evan first opened a script from Data by mistake, discarded it, and went to **Develop → SQL script** |
| Integrate | Pipelines (ADF inside Synapse) |
| Monitor | Run history for pipelines, SQL requests and Spark |
| Manage | SQL pools, Spark pools, linked services, access control, **cost control** |

He also saw an **RPC error** at one point. It didn't stop anything.

---

Q. What was the first test query?

A. (Evan, demo) A smoke test, to prove the serverless pool can run anything. The result came back immediately: the SQL version, current database `master`, and the current UTC time.

```sql
-- from the class demo (not exact)
SELECT @@VERSION       AS sql_version,
       DB_NAME()       AS current_database,
       GETUTCDATE()    AS current_utc_time;
```

---

Q. Why couldn't Synapse just read the Bronze JSON?

A. (Teacher's definition) "Azure Synapse's SQL engine is an OLAP SQL database, and so it's not natively configured to read JSON data because JSON is formatted completely differently from SQL." "Synapse requires Parquet, because both Synapse and Parquet require structured data… not semi-structured data." "Semi-structured data is simply not going to ever work in a SQL environment. You always need to flatten it in order to convert it to SQL."

What happened, in order:

| Try | Result |
|---|---|
| AI's sample `OPENROWSET(... FORMAT = 'PARQUET')` on the copied ADLS URL | Wrong: the Bronze files are JSON. Every folder he checked (station information, station status, the autoloader class demo) was JSON |
| Changed it to `FORMAT = 'JSON'` | `Incorrect syntax near format`. **Serverless SQL does not support `FORMAT = 'JSON'`** |
| AI's `JSON_VALUE` / `JSON_QUERY(... '$.data.stations')` version | "Stored procedures cannot be stored in a master database". A **misleading** error. The real cause: queries were running in **`master`** |
| `CREATE DATABASE citibike_analytics;` then `USE citibike_analytics;` | ✅ Both ran |
| The "simplest possible" JSON read, using `FORMAT = 'CSV'` | ✅ One column holding the whole JSON document. "Not nothing", but not usable as a table |
| Decision | Go to Databricks, flatten Bronze into **Silver Parquet**, then query that |

Expanded: a refinement to Evan's explanation. Synapse serverless **can** query JSON, just not with a `JSON` format option. The documented trick is to read each file as one big "CSV" text column with field and row terminators that never occur (`0x0b`), then parse it with `JSON_VALUE` / `OPENJSON`. So "never works" is too strong. But his conclusion is the right production answer: **flatten semi-structured data once, in Silver, as Parquet**. Every downstream query is then simpler, faster and cheaper (columnar, with only the needed columns scanned).

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

| Synapse serverless `OPENROWSET` FORMAT | Supported? |
|---|---|
| `'PARQUET'` | ✅ Best |
| `'DELTA'` | ✅ |
| `'CSV'` | ✅ (also the JSON workaround) |
| `'JSON'` | ❌ "Incorrect syntax near format" |

---

Q. Why the `master` database error, and why `CREATE DATABASE`?

A. (Evan / AI) The error said stored procedures can't be stored in `master`, even though he wasn't creating one. AI: "Query against the master database as shown in use database. So create a database for your exercises." Evan: "The error message is misleading."

Expanded: every serverless pool starts in `master`, a system database. You **can't create your own objects there** (views, external tables, credentials, procedures), and some functions fail with confusing messages. The habit: **create a database first and `USE` it**. In Synapse Studio you can also choose the database in the "Use database" dropdown above the script.

```sql
CREATE DATABASE citibike_analytics;
GO
USE citibike_analytics;
```

---

# Databricks: Bronze JSON → Silver Parquet (for Synapse)

Q. What did the Databricks notebook do?

A. (Evan, demo) A notebook (renamed from "New notebook" to something like *Citibike to Silver*), built step by step from ChatGPT. It did "the same thing as that first Glue job" from the AWS module: read Bronze, flatten, validate, deduplicate, and write **Silver as Parquet** so Synapse can query it.

| Step | What it did | Evan's comment |
|---|---|---|
| 1. Confirm access | `spark.read` the Bronze JSON in ADLS and `display` it | Databricks can still see the data. The output "looks quite a bit different" from what the AI expected; probably just the query type |
| 2. Look at the schema | `bronze.printSchema()` | Columns are nested: `data` → `stations` → `element` → fields. `last_updated`, `ttl` and `version` sit at the same level as `data`. "Practically unreadable" |
| 3. Flatten | `withColumn("station", F.explode(...stations))`, then `select` each field with `cast` + `alias` | "ELT syntax." The result is neat SQL-style columns |
| 4. Validate | Filters: `IS NOT NULL`, counts `>= 0` | "You can consider this to basically be `DLT.expect` or **Great Expectations** style of validations" |
| 5. Deduplicate | `dropDuplicates(...)` | "Another basically validation step" |
| 6. Add a column | `withColumn("snapshot_date", ...)` | |
| 7. Compare counts | Bronze rows vs Silver rows | Silver had **about 8,000 fewer rows** than Bronze, the invalid ones. Bronze was "full of zeros", Silver hardly any |
| 8. Sanity-check | A `groupBy` summary | |
| 9. Write | `silver.coalesce(4).write.mode("overwrite").parquet(path)` | It wrote into a `silver/station_status` folder **inside the bronze container**. "That's weird… let's just ignore that." Production would use its own silver container |
| 10. Verify | Read the Parquet back in Databricks | Then verify in Synapse |

```python
# written from the class demo (not exact). Field names match the Citi Bike GBFS feed.
from pyspark.sql import functions as F

bronze_path = "abfss://bronze@<storageaccount>.dfs.core.windows.net/<station_status_path>/"
silver_path = "abfss://bronze@<storageaccount>.dfs.core.windows.net/silver/station_status/"  # Evan's demo location

bronze = spark.read.json(bronze_path)
bronze.printSchema()                      # data -> stations -> element -> fields; last_updated, ttl, version

flat = (bronze
        .withColumn("station", F.explode("data.stations"))
        .select(
            F.col("station.station_id").cast("string").alias("station_id"),
            F.col("station.num_bikes_available").cast("int").alias("num_bikes_available"),
            F.col("station.num_docks_available").cast("int").alias("num_docks_available"),
            F.col("station.is_renting").cast("int").alias("is_renting"),
            F.col("station.is_returning").cast("int").alias("is_returning"),
            F.to_timestamp(F.from_unixtime("station.last_reported")).alias("last_reported"),
            F.to_timestamp(F.from_unixtime("last_updated")).alias("snapshot_time"),
        ))

silver = (flat
          .filter(F.col("station_id").isNotNull())
          .filter(F.col("num_bikes_available") >= 0)
          .filter(F.col("num_docks_available") >= 0)
          .dropDuplicates(["station_id", "snapshot_time"])
          .withColumn("snapshot_date", F.to_date("snapshot_time")))

print("bronze station rows:", flat.count(), " silver rows:", silver.count())

silver.coalesce(4).write.mode("overwrite").parquet(silver_path)
spark.read.parquet(silver_path).display()
```

Expanded: this is the same Silver pattern you built in Glue (Training 19–26) and in Databricks (Training 28–29). The only new reason for it is **the consumer**: Synapse serverless SQL wants Parquet. `coalesce(4)` means 4 output files, so Synapse reads a few medium files instead of many tiny ones. The **small-files problem** makes queries slower.

---

Q. Why must semi-structured data be flattened for SQL? (Evan's explanation to a student)

A. (Teacher's definition) "To work with SQL, everything's got to be at the same top level. If it's not all at the same top level, then we can't get these nice even rows where everything that's important is at the same schema level and everything has a corresponding column full of row data." Parquet "is going to have the exact same SQL type formatting."

A student had it backwards, thinking he converted to Parquet and then had to keep JSON. Evan: "I had to do the exact opposite. I had to take the JSON data that was in bronze and turn it into Parquet."

The full data path:

```
Citi Bike GBFS API (JSON)
  → AWS: ingestion into S3 (Bronze, raw JSON)
  → ADF copy S3 → ADLS Gen2 (Bronze, still raw JSON)
  → Databricks notebook: explode + flatten → validate → dedupe → Silver PARQUET (ADLS)
  → Synapse serverless SQL: OPENROWSET(FORMAT='PARQUET') → analytics queries → views
```

| | JSON (Bronze) | Parquet (Silver) |
|---|---|---|
| Structure | Semi-structured, nested | Structured: rows, columns, schema |
| Storage | Row-based text | Columnar, compressed binary |
| SQL engines | Need parsing (`OPENJSON`) | Read natively |
| Scan cost | Whole file read | Only the selected columns |

---

# Back in Synapse: querying Silver Parquet

Q. How did he query the Parquet?

A. (Evan, demo) He copied the Silver folder URL with a wildcard `*.parquet`, assumed the wildcard would work, and it did. He got "all of these columns exactly the same as they've been in Redshift and Databricks and everywhere else, but now we can see them in Synapse."

```sql
-- from the class demo (not exact)
USE citibike_analytics;

SELECT TOP 100 *
FROM OPENROWSET(
        BULK 'https://<storageaccount>.dfs.core.windows.net/bronze/silver/station_status/*.parquet',
        FORMAT = 'PARQUET'
     ) AS silver;
```

`OPENROWSET(BULK ...)` reads files in the lake as if they were a table. Nothing is loaded or copied. That's what "serverless" means here.

---

Q. What analytics did he run?

A. (Evan, demo) "Same kind of analytics that we did in Redshift."

**1. Stations with the most bikes available.** Took about 20 seconds (serverless startup plus the scan). He first thought it wasn't ordered, then saw the `ORDER BY` on average bikes available. It didn't select the station name or location ("whatever").

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

**2. Total network availability per snapshot.**

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

**A data anomaly showed up.** One snapshot had **1 active station** compared with **2,518** in the others, and most rows were from 10/16. Evan: "That must be an anomaly in the data. We would want to take a look at this", but he didn't dig in.

Expanded: this is the kind of thing a Gold-layer **row-count / completeness check** should catch. Likely causes are a partial or truncated snapshot file, or one station's `last_reported` time being used as the snapshot time. Your own pipeline had ~2,519 stations per snapshot, so you know what "normal" looks like. It makes a good interview story: *"A snapshot showed 1 station instead of ~2,500. I added a completeness check that flags any snapshot below a threshold."*

---

Q. What did he do with views?

A. (Evan, demo) `CREATE OR ALTER VIEW` over the Silver Parquet, then a simple `SELECT` from it.

```sql
-- from the class demo (not exact)
CREATE OR ALTER VIEW dbo.v_station_availability AS
SELECT station_id, snapshot_time, num_bikes_available, num_docks_available
FROM OPENROWSET(BULK '<silver path>/*.parquet', FORMAT = 'PARQUET') AS s;
GO

SELECT TOP 100 * FROM dbo.v_station_availability;
```

His definition: "A view is going to be the results of a query, which you can then query the view itself." He wasn't satisfied ("looks like just a subset of the rows or the columns in the original"), so he asked AI for a view "that is going to actually tell us something and which can be queried faster". The AI produced "a complex query" that he was starting to copy into the SQL editor.

Evan also said: "If we log out and then log back in, this view will be destroyed because views are tied to a session. If we wanted to keep this data around… what we would need to do is create a materialized view."

Expanded: a correction (the same one as in Training 29). In Synapse serverless, `CREATE VIEW` is **saved in the database** (`citibike_analytics`). It is **not** session-scoped and survives logout. That's exactly why the `master` problem mattered: views need a real database to live in. What's true is that a view stores **no data**, so every `SELECT` re-scans the Parquet and is **billed again**. Also, **serverless SQL pools don't support materialized views**; those exist only in **dedicated SQL pools** (and in Databricks). In serverless, the way to "keep results" is **CETAS** (`CREATE EXTERNAL TABLE AS SELECT`), which writes the query result as new Parquet files in ADLS, effectively a Gold table.

| Object in Synapse serverless | Stores data? | Survives logout? | Each query costs |
|---|---|---|---|
| View (`CREATE VIEW`) | ❌ | ✅ (saved in the database) | Re-scans the source files |
| External table | ❌ (points at files) | ✅ | Scans those files |
| **CETAS** (`CREATE EXTERNAL TABLE AS SELECT`) | ✅ Writes new Parquet | ✅ | Scans only the smaller result |
| Materialized view | — | — | ❌ Not available in serverless (dedicated pools only) |

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

---

# Event Hubs (preview, from the start of class)

Q. What did Evan say about Event Hubs so far?

A. (Teacher's definition) "Setting up an Event Hubs pipeline is actually quite simple and you've already been over most of it. When we covered Kafka, the syntax for working with Event Hubs is literally Kafka syntax. So if you've got existing Kafka producers and consumers, then pretty much we can just change the end point and you've got an Event Hubs pipeline."

Expanded: Event Hubs is Azure's managed event-streaming service. Its role matches Kinesis Data Streams, and it can speak the **Kafka protocol** on port **9093**. "Change the endpoint" means changing the connection config, not the code:

| Kafka setting | Value for Event Hubs |
|---|---|
| `bootstrap.servers` | `<namespace>.servicebus.windows.net:9093` |
| `security.protocol` | `SASL_SSL` |
| `sasl.mechanism` | `PLAIN` |
| `sasl.jaas.config` username | the literal string `$ConnectionString` |
| password | the namespace connection string (a **secret**: keep it in Key Vault or a secret scope, never in code or chat) |

Setup gotcha: the Kafka endpoint needs the **Standard tier or higher**. The Basic tier doesn't support Kafka.

| Kafka | Event Hubs | Kinesis |
|---|---|---|
| Cluster | Namespace | (account / region) |
| Topic | Event hub | Stream |
| Partition | Partition | Shard |
| Consumer group | Consumer group | Consumer / enhanced fan-out |
| Offset | Offset / sequence number | Sequence number |

---

# Interview-ready from today

| Question | Your one-line answer |
|---|---|
| What is MPP? | Massively parallel processing: a shared-nothing architecture where data is spread across nodes, each node processes its slice in parallel, and a leader combines results. It's what Redshift, Snowflake, Synapse and Databricks use |
| What's the Azure equivalent of Redshift? | Azure Synapse (dedicated SQL pool for provisioned MPP; serverless SQL pool is closer to Athena / Spectrum) |
| Serverless vs dedicated SQL pool? | Serverless: query files in ADLS, pay per TB processed, nothing to manage. Dedicated: a provisioned MPP warehouse, billed per hour, must be paused |
| How do you keep serverless query costs down? | Parquet, select only the columns you need, partition pruning, smaller Gold tables (CETAS), and a cost-control limit |
| Why convert JSON to Parquet before the warehouse? | SQL engines want flat, typed columns. Parquet is columnar and compressed, so queries are simpler, faster and cheaper |
| What's a VPS? | A virtual private server, a VM in the cloud (like EC2) from any provider |
| GDPR / CCPA? | EU and California data-privacy laws. They affect where personal data is stored and how it's handled (data residency) |
| How do you pick an analytics platform? | Start from the business need, data size, budget and existing infrastructure. "The best platform is the one that provides what the business needs in the way the business needs it" |
| What is MinIO / DuckDB / Iceberg? | MinIO: S3-compatible on-prem object storage. DuckDB: in-process OLAP SQL engine. Iceberg: an open table format (ACID, snapshots) that needs a catalog |

---

# Still to add

- ~~The rest of the Synapse **view** section~~: covered step by step in the Training 31 walkthrough, Part 4 (station-health view, the 55 inactive stations, cleaned views), plus Part 5 (Synapse Spark pool + charts), Part 6 (Power BI attempt) and Part 7 (cleanup).
- **Event Hubs** live demo: not done today (only the verbal preview). Expect it next class.
- Homework / announcements from the end of class: **read up on Synapse**, and the main weekend homework is to **keep working on your presentations**, ideally ready to present Monday (the date isn't final; Evan is checking with the program coordinator). AWS permissions are still revoked company-wide; if you're blocked, you may switch your project to Azure (or try Redshift Spectrum if you still have Redshift access).
