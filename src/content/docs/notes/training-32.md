---
title: "Training 32 - Microsoft Fabric Lakehouse"
description: "Fabric and OneLake, a hospital scenario through ADF and copy jobs, a bronze-silver-gold Fabric notebook and a Power BI report."
sidebar:
  order: 32
---

Teacher: Evan Flint

Syllabus Day 33 (per file numbering; Mon Oct 26, 2026). The roadmap had **Microsoft Fabric (Day 2)** for today: Direct Lake, mirroring, governance and hands-on work. Since Training 31 covered Synapse instead of Fabric Day 1, today was effectively the **first Fabric day**: a UI tour, then a hands-on bronze → silver → gold → Power BI demo inside Fabric. Direct Lake and mirroring came the next day (Training 33).

Source: class notes.

**Code note:** the code below is written from the class demo plus standard Fabric / PySpark / T-SQL syntax. It is not an exact copy of Evan's code.

---

# Today at a glance

| # | What happened |
|---|---|
| 1 | Final-project check-ins. Looker vs Streamlit for visualization. Presentation date still being set (probably this week) |
| 2 | Fabric admission: Evan's Fabric capacity had been cancelled, so the live demo would be limited |
| 3 | Concept: what Fabric is, and the **OneLake** hierarchy (Blob → ADLS Gen2 → OneLake) |
| 4 | Fabric capacity pricing check (about $8,400/month) |
| 5 | Tour of the Fabric UI: workspaces, OneLake catalog, Govern, Secure, Monitor, Real-Time hub, workloads, deployment pipelines, functions, apps |
| 6 | Interview tip: Fabric is all-in-one, so don't mix it with Snowflake or external Databricks in a narrative |
| 7 | Break |
| 8 | The hospital scenario: three hospitals' data in three places (ADLS Parquet, S3 CSV, Azure SQL) |
| 9 | Querying Azure SQL: portal query editor, then the MS SQL extension in VS Code. `SELECT TOP` vs `LIMIT` |
| 10 | ADLS hierarchical namespace vs S3 "folders" (student question) |
| 11 | Break |
| 12 | ADF pipeline with three copy activities into a bronze layer |
| 13 | Fabric copy jobs: Azure SQL worked; ADLS and S3 failed on authentication |
| 14 | Break |
| 15 | Fabric notebook: bronze → silver → three gold Delta tables |
| 16 | Semantic model + Power BI report inside Fabric (bar chart + line chart) |
| 17 | Fabric interview questions. Profile narrative coaching |

---

# Class admin and project check-ins

Q. Should we learn Looker or stick with Streamlit for visualization? (student question)

A. (Evan) "Probably Looker would be a good thing to learn ... Streamlit's never talked about in interviews, but Looker sometimes is. So Looker is actually going to be a more valuable skill for you to learn for interviews." He might add Looker to his own live demos.

Expanded: the dashboard tool you name in an interview signals what kind of shop you've worked in. Streamlit is great for quick demos, but hiring managers recognize the BI tools.

| Tool | Cost | Interview value | Notes |
|---|---|---|---|
| **Power BI** | Free desktop / paid Pro | High (Microsoft shops) | Comes built into Fabric |
| **Looker** (Google) | Paid, part of GCP | Comes up in interviews | Uses LookML modelling layer |
| **Streamlit** | Free, open source | Rarely asked about | Python code, fastest to build |

Evan's order for the final project: use **Power BI** if you can get access, otherwise try **Looker**, and if neither works, **Streamlit** is always free.

---

Q. Is it normal that a whole ingestion run cost only three cents? (student question)

A. (Evan) "Those are the kinds of surprises we like. Never feel like it's a bad thing that it's not charging you too much money." Set up cost alerts, then check after the weekend.

---

Q. Do we need automatic scheduling in the final project? (student question)

A. (Evan) "If you have time to set up scheduling, then yes ... But if you don't have time to implement it, it's the most forgivable thing to have not implemented. What we want is the full pipeline to be able to be demonstrated from ingestion to visualization ... What I'm hoping to see is the construction of the pipeline and the how and why of the data."

Expanded: what matters most in the presentation:

| Priority | Item |
|---|---|
| Must have | End-to-end flow: ingestion → bronze → silver → gold → visualization |
| Must have | The **how and why** of each step and data decision |
| Nice to have | Automation / scheduling |
| OK | Multi-cloud (e.g. a student who lost Redshift access moved to Azure + Databricks + Lakeflow). Evan called multi-cloud "aggressive" but encouraged it |

Other notes from the check-ins:
- The presentation date depends on the head of training and interviews confirming. It will probably be this week, so start now if you haven't.
- Several students are using Terraform plus the CLI for AWS infrastructure, and APIs with both live (streaming) and CSV data.
- If your own laptop misbehaves with your slide tool, joining from two devices (one presenting, one talking) is fine as long as it works.

---

# What Microsoft Fabric is

Q. What is Microsoft Fabric, compared to plain Azure?

A. (Teacher's definition) "Really the only significant difference between Microsoft Fabric and Microsoft Azure is OneLake, which is based on ADLS, but has some additional features ... putting it on par with the unified data platform type features that Snowflake has. Other than that basic change to the way that storage buckets are managed, everything else is pretty much exactly the same as you would be able to find within regular Azure." It "takes all of those Azure services and packages them all together in a ... business-to-business product, which is designed to be a full and complete data pipeline, which can compete with the likes of Talend and Pentaho and Informatica."

Expanded: Fabric is Microsoft's SaaS "all-in-one" analytics platform. Instead of creating a storage account, a Data Factory, a Databricks workspace and a Power BI workspace separately and wiring them together, you open one web UI and create **items** (lakehouse, notebook, copy job, pipeline, semantic model, report) inside a **workspace**. All items share one storage layer, OneLake.

| Fabric item / experience | Plain-Azure equivalent |
|---|---|
| OneLake / Lakehouse | ADLS Gen2 storage account |
| Copy job / Data pipeline | Azure Data Factory |
| Notebook / Spark job | Databricks (or Synapse Spark) notebook |
| Warehouse / SQL endpoint | Synapse dedicated / serverless SQL, Azure SQL |
| Eventstream / Eventhouse | Event Hubs + Azure Data Explorer |
| Semantic model / Report | Power BI |
| Functions | Azure Functions (≈ AWS Lambda) |
| Deployment pipelines | Azure DevOps / GitHub CI/CD |

Evan's takeaway: "every single thing that we're doing in Fabric, we can do with an equivalent Azure service." The difference is that in Azure "every service is explicitly separate from each other," while Fabric combines them "into a singular user interface."

---

Q. What is OneLake, and how does it relate to Blob Storage and ADLS?

A. (Teacher's definition) "OneLake is basically going to be a management layer on top of Azure Data Lake Service ... You've got blob storage at the bottom as the foundational technology. Then on top of that, you've got ADLS Gen 2, which is basically blob storage plus a hierarchical namespace. And then on top of that, you get OneLake, which includes unified data platform type features ... probably the most important one is the unified namespace."

Expanded: think of it as three layers stacked on each other:

| Layer | What it adds |
|---|---|
| **Azure Blob Storage** | Cheap object storage. Flat namespace |
| **ADLS Gen2** | Blob + **hierarchical namespace** (real folders, POSIX-style permissions, fast renames) |
| **OneLake** | ADLS Gen2 + **unified namespace** across the whole tenant, a catalog, governance and security, shortcuts to other storage, Delta as the default table format |

**Unified namespace** = "you can have multiple buckets, and you can work with data from any of those buckets within a single environment." There's one OneLake per organization, so every workspace's lakehouse lives under the same logical lake.

---

Q. When does OneLake / a unified platform actually make sense?

A. (Evan) "It's mostly a benefit for large organizations that have extremely varied data sources. It's not really something that most people would think to want to use in just a small demo project or even a small business project." For his own small business he doesn't see a reason to use OneLake or Snowflake. His example of where it fits: a platform reading data from all the hospitals in the United States.

| Situation | Unified platform worth it? |
|---|---|
| Small demo / small business | No. Plain storage + Databricks or DuckDB is enough |
| Growing business, a few sources | Maybe |
| Large enterprise, many teams, very varied sources | Yes. Central catalog, governance and one namespace pay off |

---

Q. Why couldn't Evan do a full live Fabric demo?

A. (Evan) His Fabric capacity had been cancelled shortly before class. Trying to create a new one failed with "All administrators must belong to the same tenant" (Bad Request). The pricing page also showed why access is restricted:

| Setting in the "Create Fabric capacity" form | Value / note |
|---|---|
| Resource group | Same as any Azure resource |
| Capacity name | e.g. `demofabriccapacity` |
| Capacity overage protection | Covers spikes. Not needed for a demo, so turn it off |
| Estimated cost | **about $8,409.60 / month** |

"Obviously, we would not want to keep this thing running all of the time because it is most definitely not cheap." Later in class, creating a copy job made Fabric automatically give him a **free trial capacity**, which let the demo go ahead.

Expanded: a **Fabric capacity** (F SKU) is the pool of compute you pay for. Every Fabric workload (Spark, SQL, Power BI, pipelines) draws on it. With no capacity you can browse the UI but can't run anything. Capacities can be **paused** to stop billing. Students won't each get one because of cost.

---

# Tour of the Fabric UI

Q. What are the main areas of the Fabric UI?

A. (Evan) "Just like in Databricks, you have the concept of workspaces." He walked through each left-sidebar section.

Expanded:

| Area | What it's for | What Evan noticed |
|---|---|---|
| **Workspaces** | Containers for items (lakehouses, notebooks, pipelines, reports) | Old "Energy Company Simulation" workspace held a diagram of a simple pipeline: 2 sources → bronze → silver → gold → visualization + ML (logic only, nodes not configured). New "Hospital Analytics" workspace for today |
| **Copilot** | AI assistant for Power BI | Errored. Needs a paid tier |
| **OneLake catalog** | Browse and manage all data items across the tenant | Feels like ADLS "with that extra governance layer". Item types include semantic models, **Cosmos DB** (Azure's proprietary NoSQL database), custom stream connectors, event schema sets, eventhouses, graph models |
| **Govern** (in catalog) | Insights and recommended actions: domains, subdomains, workspaces, items | "Remove unused items" suggestion |
| **Secure** | Who has admin and access rights | Evan and an infrastructure manager are both admins |
| **Monitor** | Job runs view, filter by time and item type (pipeline, notebook, dbt, Airflow, semantic model, etc.) | "Probably going to look a little bit more like Databricks jobs" |
| **Real-Time hub** | View streaming data, connect sources, set alerts | Sources include **Kafka**, **Azure Event Hubs**, sample stock-market data. Plus Fabric/Azure/business **events** and an **event schema registry** |
| **Workloads** | Packaged tutorials and sample items per workload | Data engineering workload: lakehouse, sample lakehouse, notebook, environment, Spark job, data functions, API for GraphQL, Snowflake database |
| **Deployment pipelines** | CI/CD: promote items dev → test → prod | "I didn't realize that Fabric did CI/CD, but here it is" |
| **Functions** | Serverless code | A port of Azure Functions, so "something like AWS Lambda" |
| **Apps** | Apps installable within Power BI | Rarely needed |
| **Power BI switch** | Jump to the Power BI experience (bottom left) | Same account, same items |

---

Q. What are "Fabric events" in the Real-Time hub? Does Fabric have its own streaming service?

A. (Evan) They are events generated **inside** your Fabric environment, so you can watch and alert on what's happening. "It's not like Fabric has its own native application that is equivalent to Event Hubs." Categories he saw: anomaly detection, capacity overview, capacity operation, **job events**, **OneLake events**, workspace item events. Job events even list their schemas, which "Kafka definitely isn't as forthright with you on."

| Real-Time hub tab | Contents |
|---|---|
| Streaming data | Streams already flowing into Fabric |
| Connect data sources | Kafka, Event Hubs, sample data, other connectors |
| Business events | Any event in your Fabric environment you can access |
| Fabric events | Job / OneLake / workspace item / capacity events |
| Azure events | Events from Azure services (e.g. Blob Storage) |
| Event schema registry | Stored schemas for streams |

---

Q. What is a schema registry, and why is it useful?

A. (Teacher's definition) "Schema registries are going to be useful when we're working with evolving data that is streaming. So if we want to set up schema evolution, a schema registry is a convenient place to do that ... A schema registry is going to be a place to store all of the different schemas that we are working with for our streaming job so that we can apply the proper one to the proper data."

Expanded: in streaming, producers may change their message format over time. A schema registry stores each schema **version**, and messages carry a schema ID. That way consumers know exactly how to read each message, and the registry can reject changes that would break consumers.

| Concept | Meaning |
|---|---|
| Schema | Field names + types for a message |
| Schema version | A new version is registered when the producer's format changes |
| Compatibility rules | Backward / forward / full: which changes are allowed |
| Examples | Confluent Schema Registry (Kafka), Azure Schema Registry (Event Hubs), AWS Glue Schema Registry, Fabric event schema sets |

---

Q. Can a Fabric project use Snowflake or external Databricks too? (student question: "So if I'm talking about Fabric, only talk about Fabric, nothing else?")

A. (Evan) "Fabric is an all-in-one solution. And so you don't want to tell a story about having used both it and Snowflake or both it and some kind of external Databricks or something like that in any kind of a project ... Pretty much Fabric and the sources that you are working with outside of it ... If your company is using Fabric for data operations, then yes, all of the data operations that you talk about should be within Fabric."

Expanded:

| In a Fabric narrative | OK? |
|---|---|
| External **sources** (APIs, on-prem SQL, S3, Kafka/Event Hubs) feeding into Fabric | Yes |
| Processing, storage, warehousing and BI all inside Fabric | Yes |
| Fabric **and** Snowflake as the warehouse for the same project | No: overlapping, unrealistic |
| Fabric **and** a separate Databricks workspace for the same pipeline | No |

---

Q. The Fabric UI looks like a hybrid of Azure and AWS. Was that a design goal? (student question)

A. (Evan) "It's certainly not trying to integrate with AWS. It's still very much a Microsoft product. But they've probably taken some design notes from the AWS people and the GCP people." Fabric is new (he estimated 2021-2022; it was announced in 2023), while AWS dates to 2006. Demand for Fabric spiked from January to March of this year and then subsided, "but every once in a while, there is still a Fabric-centric interview," which is why it's in the course.

---

# The hospital scenario and its data sources

Q. What scenario did the demo use?

A. (Evan) Ingesting data from several hospitals that each store patient encounters differently. The data is **synthetic**: "There is no hospital data available on the Internet for a very good reason. Obviously, nobody wants their medical records to be public information ... You have to be an organization that's certified by the organizations that manage those records."

Expanded: the three sources were deliberately in three different systems and formats, which is the classic multi-source ingestion problem:

| Hospital | Source system | Format | Location |
|---|---|---|---|
| Hospital A | ADLS Gen2 | Parquet | `hospital-a/encounters.parquet` |
| Hospital B | AWS S3 | CSV | `encounters/hospital_b_encounters.csv` (10,151 lines incl. header) |
| Hospital C | **Azure SQL Database** | Relational table | `dbo.patient_encounters` (10,150 rows) |

Evan also used Claude Code to pre-build the resources and a small **federated query** demo: a FastAPI/uvicorn app with DuckDB + pandas (`federated_query.py`) reading all three sources "in place, without copying anything." All three had near-identical columns because the data was generated.

---

# Querying Azure SQL Database

Q. How do you run queries against an Azure SQL Database?

A. (Evan) Two ways worked in class: the **Query editor (preview)** in the Azure portal, and the **MS SQL extension in VS Code**. "Azure Portal is the fastest."

Expanded:

| Option | Steps | Notes |
|---|---|---|
| Portal query editor | SQL databases → your DB → **Query editor (preview)** → sign in (SQL auth or Entra ID) → New query | Fastest. The firewall may need your client IP added |
| VS Code MS SQL extension | Install "SQL Server (mssql)" → Add connection (server `<name>.database.windows.net`, DB, SQL login) → Test → Connect | Open a `.sql` file, then **Ctrl/Cmd+Shift+P → "MS SQL: Execute Query"** (or Ctrl/Cmd+Shift+E in a .sql editor tab) |
| SSMS / Azure Data Studio | Classic Windows tools | Not used in class |
| CLI | `sqlcmd -S <server> -d <db> -U <user>` | Scriptable |

Gotcha seen in class: in the portal, the database appeared under **SQL databases**, not under the **SQL servers** listing Evan first checked. Double-clicking a table in VS Code ran a "select top 1000" style preview automatically.

Security habit: Evan stopped screen sharing whenever he printed a password or access key. Never show secrets on a shared screen or in screenshots.

---

Q. What's the difference between `SELECT TOP 20` and `LIMIT 20`?

A. (Teacher's definition) "This is syntax in SQL that will only ever work in a Microsoft version of SQL ... For the purposes of doing interviews, `SELECT TOP 20 *` is the same as `SELECT * FROM table LIMIT 20`. TOP 20 is just a Microsoft convention that works within Microsoft databases. Oracle also has some of those conventions where it's got its own ... dialect of SQL."

Expanded: T-SQL (SQL Server / Azure SQL / Synapse / Fabric Warehouse) does **not** support `LIMIT`, which is why `LIMIT 20` gave "Incorrect syntax near '20'" in class.

| Dialect | First N rows |
|---|---|
| T-SQL (SQL Server, Azure SQL, Synapse, Fabric) | `SELECT TOP 20 * FROM t;` or `ORDER BY ... OFFSET 0 ROWS FETCH NEXT 20 ROWS ONLY` |
| PostgreSQL, MySQL, SQLite, DuckDB, Spark SQL, Snowflake | `SELECT * FROM t LIMIT 20;` |
| Oracle 12c+ | `SELECT * FROM t FETCH FIRST 20 ROWS ONLY;` (older: `WHERE ROWNUM <= 20`) |

"MySQL and Postgres ... are a whole lot more similar to each other than they are to the Microsoft and Oracle ones."

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

`SUM(CASE WHEN ... THEN 1 ELSE 0 END)` is the standard pattern for **conditional counting**: count only the rows meeting a condition, alongside the total.

---

Q. This looks very similar to what we did on S3. What's the real difference between ADLS and S3? (student question)

A. (Evan) The UI differences are "just because they're different companies with different products. But they are fundamentally doing the same thing." The key difference is the **hierarchical namespace**: "the data that is contained within an ADLS container is actually formatted with these directories and files in it, just like it is on the local file system of your computer. Whereas while AWS S3 appears to have a folder and file structure, that's just an abstraction that it creates in order to make it easier for you to browse it ... With ADLS Gen 2, these are actual folders that contain actual files."

| | AWS S3 | ADLS Gen2 |
|---|---|---|
| Namespace | Flat: keys like `a/b/c.csv`; "folders" are just prefixes | Hierarchical: real directories |
| Rename / move a folder | Copy + delete every object (slow for big folders) | Single atomic metadata operation |
| Permissions | Bucket / prefix policies (IAM) | POSIX-style ACLs on folders and files + RBAC |
| Container term | Bucket | Container (file system) inside a storage account |
| URI | `s3://bucket/key` | `abfss://container@account.dfs.core.windows.net/path` |

---

# Ingesting to bronze with Azure Data Factory

Q. What was the plan for the rest of class?

A. (Evan) Simulate a Fabric-style pipeline, using Fabric where possible and plain Azure where not:

| # | Stage | Tool |
|---|---|---|
| 1 | Combine all three sources into one **bronze** layer | Azure Data Factory (then Fabric copy jobs) |
| 2 | Normalize bronze → **silver** | Notebook (Databricks / Fabric Spark) |
| 3 | Build **gold** | Same notebook. "Databricks is perfectly fine for hosting a gold layer" even without a Synapse/Redshift-style SQL UI |
| 4 | Dashboard | Power BI (inside Fabric) |

---

Q. How was the ADF pipeline set up?

A. (Evan) A separate pipeline (`PL_ingest_hospitals` / "hospital demo") inside the existing data factory from the Citi Bike lessons, with **three Copy activities**:

| Copy activity | Source dataset | Sink dataset |
|---|---|---|
| Copy Hospital A (ADLS) | ADLS Parquet | `DS_Lakehouse_Bronze_Parquet` |
| Copy Hospital B (S3) | S3 CSV (Amazon S3 linked service) | `DS_Lakehouse_Bronze_CSV` |
| Copy Hospital C (Azure SQL) | `DS_Hospital_C_Source` (table) | `DS_Lakehouse_Bronze_Parquet` |

So the Parquet outputs share one sink type, while the CSV "will remain separated in the bronze layer for the time being."

Expanded: one data factory can hold many pipelines, and it's normal to reuse it across projects. Run with **Add trigger → Trigger now**, then watch in **Monitor**. Each activity run shows the activity run ID, source → sink, **data read/written, rows copied, copy duration and throughput**. Those are "essential things for when you're monitoring a long-running job." The run succeeded. The output files already existed because Claude Code had already done a test run before class.

Bronze layout after ingestion:

```
bronze-hospital/
├── hospital-a/   encounters.parquet
├── hospital-b/   encounters.csv
└── hospital-c/   dbo.patient_encounters.parquet
```

---

# Ingesting into Fabric: copy jobs and the lakehouse

Q. How do you ingest into Fabric?

A. (Evan) In the workspace: **New item → Copy job**. The first time, Fabric automatically started a **free trial capacity**. "When I was doing the last step ... Fabric just automatically signed me up. So now I can do demos within it."

Expanded: steps that worked for the Azure SQL source:

| # | Step |
|---|---|
| 1 | Workspace (Hospital Analytics) → **New item → Copy job** |
| 2 | Choose data source: **Azure SQL Database** → enter the server, DB and SQL auth → select `dbo.patient_encounters` (schema preview shown) |
| 3 | Destination: **New Fabric item → Lakehouse** named `hospital_lakehouse` (lakehouse schemas enabled) → Create and connect |
| 4 | Copy mode: **Full copy** (suggested for a one-off) |
| 5 | Destination type: **Tables** (a relational source becomes a **Delta table**) |
| 6 | Map to destination: Fabric auto-generates the column mapping (same names, source types → Fabric types) |
| 7 | **Save + Run** |

Lessons learned:
- **One data source per copy job.** For three sources, create three copy jobs (go back to the workspace → New item → Copy job each time). Don't try to add a second source inside the first job's settings.
- Relational sources → lakehouse **Tables** (Delta). File sources → lakehouse **Files**, in a subfolder per source under `bronze/`.

| Lakehouse area | Holds | Queryable via SQL endpoint? |
|---|---|---|
| **Tables** | Managed Delta tables | Yes |
| **Files** | Raw files of any format (CSV, JSON, Parquet) | Not directly. Load with Spark first |

---

Q. Why did the ADLS and S3 copy jobs fail?

A. (Evan) Authentication. "I hate authentication so much."

| Source | Error | Likely cause / fix |
|---|---|---|
| ADLS Gen2 | Invalid credentials | Needs an account key, **SAS token**, organizational account, or **service principal** (tenant ID + client ID + secret) that the user can access. Cross-tenant setup in the training account blocked the org-account route |
| Amazon S3 | "`s3://` scheme isn't supported" even though the example text showed an S3 URI | The connector wants the **HTTPS** bucket URL (`https://<bucket>.s3.<region>.amazonaws.com`). After switching, access was granted but no objects showed, probably because of the bucket region or IAM policy |

Evan's decision with one hour left: "abandon the S3 and ADLS ingestion pipelines because they are both giving us completely unreasonable authentication errors," and finish end to end with Hospital C only.

Expanded: authentication is the most common blocker when connecting clouds. Before class or a demo, check that you have, for each source:

| Source | Credential you need |
|---|---|
| ADLS Gen2 | Account key / SAS / service principal with **Storage Blob Data Reader** (or Contributor) |
| S3 | IAM access key + secret with `s3:ListBucket` + `s3:GetObject` on that bucket |
| Azure SQL | SQL login, or Entra ID user added as a DB user; firewall rule for the client |

---

# Bronze → silver → gold in a Fabric notebook

Q. How do you create a notebook and attach the lakehouse?

A. (Evan) Opening the lakehouse only offered "New Spark SQL query," so instead: **Workspace → New item → Notebook** (`hospital_notebook`), then in the Explorer pane **Add data items → From OneLake catalog → hospital_lakehouse**. The first cell listed the tables to prove access (namespace, tableName, isTemporary).

Expanded: a Fabric notebook is a Spark notebook like Databricks, with `spark` already defined. "The fact that it was Databricks was kind of obscured from us, but the format of that should have been familiar." (Fabric runs its own Spark runtime, not Databricks, but the PySpark code is the same.)

```python
# Cell 1 - confirm the lakehouse is attached
spark.sql("SHOW TABLES").show()

# Cell 2 - read bronze into a DataFrame
bronze = spark.read.table("hospital_lakehouse.dbo.patient_encounters")
display(bronze)
```

---

Q. What did the bronze → silver transformation do?

A. (Evan) "We're going to declare a silver data frame defined as bronze dot select each of the columns. When necessary, we cast it. We always give it an alias." Then: clean the diagnosis code, add a source-hospital column, drop duplicates on encounter ID, filter out nulls, and run a date validity check.

```python
from pyspark.sql import functions as F

silver = (
    bronze.select(
        F.col("encounter_id").cast("string").alias("encounter_id"),
        F.col("patient_id").cast("string").alias("patient_id"),
        F.col("admit_date").cast("date").alias("admit_date"),
        F.col("discharge_date").cast("date").alias("discharge_date"),
        F.upper(F.trim(F.col("diagnosis_code"))).alias("diagnosis_code"),
    )
    .withColumn("source_hospital", F.lit("hospital_c"))
    .dropDuplicates(["encounter_id"])
    .filter(F.col("encounter_id").isNotNull() & F.col("patient_id").isNotNull())
    # keep rows still admitted (no discharge yet) OR with a logical date order
    .filter(F.col("discharge_date").isNull() | (F.col("discharge_date") >= F.col("admit_date")))
)

print(bronze.count(), silver.count())   # silver slightly smaller, as expected

silver.write.format("delta").mode("overwrite").saveAsTable("silver_patient_encounters")
```

Expanded: about the validity filter. Evan first questioned it, but it **keeps** good rows rather than removing them. A discharge date on or after the admit date is valid, and a null discharge date means the patient is still in hospital. Rows where discharge is **before** admit are impossible and get dropped.

| Silver step | Purpose |
|---|---|
| `select` + `cast` + `alias` | Enforce types and consistent names |
| Clean `diagnosis_code` | Standardize codes (trim, uppercase) |
| `source_hospital` literal | Lineage: which hospital a row came from (needed once A and B are unioned in) |
| `dropDuplicates(["encounter_id"])` | One row per encounter |
| Null filter | Drop rows missing keys |
| Date validity filter | Drop impossible records |
| `saveAsTable` (Delta) | Shows up under **Tables** after refreshing the Explorer |

---

Q. How was silver enriched and turned into gold?

A. (Evan) A **window** partitioned by patient and ordered by admit date and encounter ID adds previous-discharge, days-since-discharge, a **30-day readmission** flag and length of stay. That enriched frame then feeds three gold tables.

```python
from pyspark.sql.window import Window

w = Window.partitionBy("patient_id").orderBy("admit_date", "encounter_id")

enriched = (
    spark.read.table("silver_patient_encounters")
    .withColumn("prev_discharge", F.lag("discharge_date").over(w))
    .withColumn("days_since_discharge", F.datediff("admit_date", "prev_discharge"))
    .withColumn("readmitted_30d",
                F.when(F.col("days_since_discharge").between(0, 30), 1).otherwise(0))
    .withColumn("length_of_stay_days", F.datediff("discharge_date", "admit_date"))
)

# Gold 1 - one row per hospital
gold_hospital = (enriched.groupBy("source_hospital").agg(
    F.count("*").alias("total_encounters"),
    F.countDistinct("patient_id").alias("unique_patients"),
    F.sum("readmitted_30d").alias("readmissions_30d"),
    F.round(F.sum("readmitted_30d") / F.count("*") * 100, 2).alias("readmission_rate_pct"),
    F.round(F.avg("length_of_stay_days"), 2).alias("avg_length_of_stay_days")))
gold_hospital.write.format("delta").mode("overwrite").saveAsTable("gold_hospital_metrics")

# Gold 2 - one row per diagnosis (main Power BI dataset)
gold_diagnosis = (enriched.filter(F.col("diagnosis_code").isNotNull())
    .groupBy("diagnosis_code").agg(
        F.count("*").alias("total_encounters"),
        F.sum("readmitted_30d").alias("readmissions_30d"),
        F.round(F.sum("readmitted_30d") / F.count("*") * 100, 2).alias("readmission_rate_pct"),
        F.round(F.avg("length_of_stay_days"), 2).alias("avg_length_of_stay_days")))
gold_diagnosis.write.format("delta").mode("overwrite").saveAsTable("gold_diagnosis_metrics")

# Gold 3 - one row per admit month
gold_monthly = (enriched.withColumn("admit_month", F.date_trunc("month", "admit_date"))
    .groupBy("admit_month").agg(
        F.count("*").alias("total_encounters"),
        F.sum("readmitted_30d").alias("readmissions_30d")))
gold_monthly.write.format("delta").mode("overwrite").saveAsTable("gold_monthly_metrics")
```

Expanded:

| Gold table | Grain | Result in class |
|---|---|---|
| `gold_hospital_metrics` | One row per hospital | **One row** only, since only Hospital C was ingested. A cross-hospital comparison needs A and B |
| `gold_diagnosis_metrics` | One row per diagnosis code | About 10 codes. Good for a bar chart |
| `gold_monthly_metrics` | One row per month | May → December trend. Good for a line chart |

Window functions used:

| Function | Meaning here |
|---|---|
| `Window.partitionBy("patient_id")` | Compute separately for each patient |
| `.orderBy("admit_date", ...)` | In visit order |
| `F.lag(col)` | Value from the patient's **previous** encounter |
| `F.datediff(end, start)` | Days between two dates |

**30-day readmission** is a standard hospital quality metric: a patient re-admitted within 30 days of a discharge. It's a classic interview example of window functions.

---

# Power BI inside Fabric

Q. How do you build a Power BI report from lakehouse gold tables?

A. (Evan) Open the lakehouse → **New semantic model** → name it (`hospital_analytics_model`) → pick the three gold tables → Confirm. Then from the semantic model: **New report**.

Expanded:

| Term | Meaning |
|---|---|
| **Semantic model** | Power BI's data model (formerly "dataset"): tables, relationships, measures. Reports sit on top of it |
| **Report** | The canvas of visuals |
| **Direct Lake** | Storage mode where Power BI reads the Delta/Parquet files in OneLake directly, with no import copy and no live SQL queries. It turned out (Training 33) to be the default for lakehouse semantic models |

Building visuals (Copilot wasn't available, so it was done by hand):

| # | Step |
|---|---|
| 1 | Click on empty canvas, then pick a visual from the **Visualizations** pane. If a visual is selected, clicking another visual type **changes** it instead of adding a new one |
| 2 | Add fields by **ticking them in the Data pane** (or dragging onto the Y-axis / X-axis wells) |
| 3 | Clustered bar chart: Y-axis = `gold_diagnosis_metrics.diagnosis_code`, X-axis = `total_encounters`, Tooltip = `readmission_rate_pct` |
| 4 | Format pane: colors, data labels. Sort via the visual's "..." menu → Sort by total encounters, descending |
| 5 | Line chart: X-axis = `gold_monthly_metrics.admit_month`, Y-axis = `total_encounters` |
| 6 | Resize the visuals to share the page. **Save** the report (e.g. "Hospital C Analytics") |

Findings: diagnosis code **J18.9** (pneumonia, unspecified) had the most encounters. Monthly encounters started in May and fell toward December (the data is fake, so don't read too much into it).

Recap of what was built in Fabric: free trial capacity → copy job (Azure SQL → lakehouse Delta table) → Spark notebook bronze → silver → three gold tables → semantic model → Power BI report.

---

# Interview angle

Q. What are common Fabric interview questions? (student question)

A. (Evan) "The extent of Fabric interview questions is more to do with your profile narrative than it is anything else. So if your profile says that you've got Fabric experience, then you should be able to tell the story of what you did in Fabric." He has never heard Fabric come up in a first-round quiz "aside from just to ask, do you have Fabric experience in order to prompt a profile narrative."

Expanded: a Fabric story skeleton built from today's demo:

| Part | What to say |
|---|---|
| Sources | Data from several systems (on-prem / Azure SQL, files in ADLS, S3, streams) |
| Ingestion | Data Factory pipelines / copy jobs into a OneLake lakehouse (bronze) |
| Processing | Spark notebooks: bronze → silver (types, dedup, validation) → gold aggregates |
| Serving | Semantic model in **Direct Lake** mode, Power BI reports |
| Platform | Workspaces, OneLake catalog for governance, deployment pipelines for CI/CD |

Since Fabric capacity is too expensive to give every student, practice with the **equivalent Azure services** (ADF, Databricks, Power BI). "I don't think that it's a huge disadvantage for you guys not to have access to Fabric, because everything is possible just within Azure."

---

Q. How do you turn a real non-data job into a data-engineering narrative? (student question, about mobile-app work on EV charging features)

A. (Evan) Find the **data the real system produced** and build a coherent pipeline around it. EV charging stations "are distributed throughout the country and they are a rich source of data." The station sends frequent updates: transaction, wattage delivered and charge time remaining. That suggests:

| Stage | Narrative |
|---|---|
| Producer | A Kinesis producer on or behind the stations emits telemetry |
| Stream | **Kinesis Data Streams** |
| Processing | **Spark Structured Streaming**, first on AWS **EMR**, later **migrated to Databricks** ("EMR and Databricks are fundamentally kind of for the same thing") |
| Landing | Bronze layer of a **Delta Lake** lakehouse |
| Use case | **Predictive maintenance**: early notice that a part will fail, so maintenance is scheduled before an outage |

"Any kind of hardware like that is going to be generating quite a lot of data just all the time based on its operation ... It really, really lends itself to Kinesis as a technology." Any notification or data the real system handled "should be captured, stored and organized" in the story.

Also from the training staff: everyone did well on the first profile narratives and elevator pitches. Start on the **second** narrative, which should have more technical (SME) input, not just soft skills. Sessions with subject-matter experts are being scheduled.

---

# Key terms from today

| Term | Meaning |
|---|---|
| Microsoft Fabric | Microsoft's all-in-one SaaS data platform that bundles ADF, Spark, warehouse, real-time and Power BI on OneLake |
| Fabric capacity | Paid compute pool (F SKU) that all Fabric workloads draw on. About $8.4k/month for the size shown. Has a free trial |
| OneLake | Tenant-wide logical data lake on ADLS Gen2, with a unified namespace and governance |
| Unified namespace | Work with data from many buckets/workspaces as one environment |
| Hierarchical namespace | ADLS Gen2 feature: real directories, unlike S3's key prefixes |
| Workspace | Container for Fabric items |
| Lakehouse | Fabric item with Tables (Delta) and Files areas plus a SQL endpoint |
| Copy job | Fabric item that copies one source to a destination (ADF-style) |
| Real-Time hub | Fabric area for streams, event sources, Fabric events and alerts |
| Schema registry | Store of versioned message schemas for streaming / schema evolution |
| Deployment pipeline | Fabric CI/CD between dev/test/prod |
| Cosmos DB | Azure's proprietary NoSQL database |
| T-SQL `TOP` | Microsoft's version of `LIMIT` |
| Semantic model | Power BI data model (tables + measures) behind reports |
| Direct Lake | Power BI mode that reads OneLake Delta files directly |
| 30-day readmission | Patient re-admitted within 30 days of discharge. A window-function metric |
