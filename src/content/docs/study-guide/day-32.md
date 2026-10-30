---
title: Study Guide - Day 32
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 32: Microsoft Fabric Lakehouse"
sidebar:
  order: 320
---

Study Guide - Day 32 (source: notes/Training 32.md)

Note: built for verbal-quiz prep. The flashcards (Part 3) are phrased the way a quiz question would be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Class Admin.** Final-project check-ins. **Looker** is worth learning because it comes up in interviews and Streamlit doesn't. For the project: Power BI if you can get it, otherwise Looker, otherwise Streamlit (free). Scheduling is "the most forgivable thing to have not implemented"; what matters is the full pipeline from ingestion to visualization and the **how and why** of the data. The presentation date is likely this week.

**What Fabric Is.** Microsoft's all-in-one SaaS data platform. "The only significant difference between Microsoft Fabric and Microsoft Azure is OneLake." Everything else (ADF, Spark notebooks, SQL, Power BI, Functions) is the same Azure tech packaged in one UI, competing with Talend, Pentaho and Informatica. Every Fabric item has a plain-Azure equivalent.

**OneLake.** Three layers: **Blob Storage** (flat object storage) → **ADLS Gen2** (Blob + hierarchical namespace) → **OneLake** (ADLS + a **unified namespace**, catalog and governance, like Snowflake's unified-platform features). One OneLake per organization. Mostly worth it for large organizations with very varied sources, not small projects.

**Fabric Capacity.** The paid compute pool that every Fabric workload uses. About **$8,400/month** for the size shown, so students won't each get one. Evan's capacity had been cancelled, and creating one failed with "all administrators must belong to the same tenant". Creating a copy job later started a **free trial capacity** automatically.

**UI Tour.** Workspaces · OneLake catalog (Govern, Secure) · Monitor (job runs) · Real-Time hub (Kafka/Event Hubs sources, Fabric events, alerts, **event schema registry**) · Workloads (tutorials) · **Deployment pipelines** (CI/CD) · Functions (≈ Lambda) · Power BI switch. Fabric doesn't have its own Event Hubs equivalent; "Fabric events" are events about your environment.

**Schema Registry.** Stores every version of a stream's schema, so consumers apply the right schema to each message. Used for **schema evolution**.

**Interview Rule.** Fabric is all-in-one, so a Fabric narrative shouldn't also use Snowflake or a separate Databricks for the same project. External **sources** are fine. Fabric interview questions are mostly "tell me about your Fabric experience", which prompts a profile narrative.

**Hospital Scenario.** Synthetic data (real medical data isn't public). Hospital A = Parquet in ADLS, B = CSV in S3, C = table in **Azure SQL**.

**Azure SQL Queries.** Portal **Query editor (preview)** is fastest. VS Code **MS SQL** extension: connect, open a `.sql` file, then Command Palette → *MS SQL: Execute Query*. **`SELECT TOP 20`** is T-SQL's version of `LIMIT 20`, and `LIMIT` errors in T-SQL. Conditional count: `SUM(CASE WHEN discharge_date IS NULL THEN 1 ELSE 0 END)` gave 201 of 10,150 still admitted. Hide passwords and keys when screen sharing.

**ADLS vs S3.** ADLS Gen2 has a real **hierarchical namespace** (actual folders, atomic renames, ACLs). S3 folders are just key prefixes.

**ADF to Bronze.** One pipeline with three Copy activities (ADLS Parquet, S3 CSV, Azure SQL) into bronze sinks. Monitor shows rows, data read/written, duration and throughput.

**Fabric Copy Jobs.** New item → Copy job → source Azure SQL → destination: new **Lakehouse** → full copy → **Tables** (Delta) → auto column mapping → run. **One source per copy job.** Files go to the lakehouse **Files** area. ADLS (invalid credentials) and S3 (`s3://` rejected, HTTPS URL then empty) failed on **authentication**, so the demo used Hospital C only.

**Notebook.** New item → Notebook → add the lakehouse. Bronze → silver: select/cast/alias, clean the diagnosis code, `source_hospital`, `dropDuplicates(encounter_id)`, null filter, keep `discharge_date IS NULL OR discharge_date >= admit_date`. Enrich with a **window** per patient ordered by admit date: `lag` previous discharge → days since discharge → **30-day readmission** flag, length of stay. Gold: per hospital (only 1 row), per diagnosis, per month.

**Power BI in Fabric.** Lakehouse → **New semantic model** (three gold tables) → **New report**. Click empty canvas before choosing a visual. Tick fields in the Data pane. Bar chart of diagnosis × encounters (J18.9 highest), line chart of encounters by month. Save.

**Narrative Coaching.** Turn real work into a data story by finding the data the real system produced. Example: EV charging telemetry → Kinesis → Spark Structured Streaming (EMR, later Databricks) → Delta bronze → predictive maintenance.

---

# Part 2: Cheat Sheet

## Project
- End-to-end + how/why > scheduling · Power BI → Looker → Streamlit

## Fabric
- All-in-one SaaS on OneLake · items in workspaces · capacity ≈ $8.4k/mo, trial available
- Copy job ≈ ADF · Notebook ≈ Databricks · Semantic model/report ≈ Power BI · Functions ≈ Lambda · Deployment pipelines = CI/CD

## Storage Stack
- Blob (flat) → ADLS Gen2 (hierarchical) → OneLake (unified namespace + governance)

## Real-Time Hub
- Sources: Kafka, Event Hubs, samples · Fabric/Azure/business events · alerts · schema registry

## SQL
- T-SQL `TOP n` = `LIMIT n` · Oracle `FETCH FIRST n ROWS ONLY` · conditional count with `SUM(CASE ...)`

## Copy Jobs
- One source each · relational → Tables (Delta) · files → Files · auth is the usual blocker

## Notebook
- select/cast/alias → dedup → validate → Delta `saveAsTable`
- Window: `partitionBy(patient).orderBy(admit)` + `lag` → readmit 30d

## Power BI
- Lakehouse → New semantic model → New report · Direct Lake by default

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What is Microsoft Fabric?
A: Microsoft's all-in-one SaaS analytics platform. It packages Data Factory, Spark notebooks, warehousing, real-time analytics and Power BI into one UI, on top of one shared storage layer called OneLake.

Q: What's the main difference between Fabric and plain Azure?
A: OneLake. The compute services are basically the same Azure ones; Fabric bundles them in one interface on shared storage, while in Azure each service is separate and you wire them together.

Q: Explain the layers under OneLake.
A: Blob Storage is flat object storage. ADLS Gen2 adds a hierarchical namespace. OneLake sits on ADLS and adds a tenant-wide unified namespace, a catalog and governance.

Q: What does unified namespace mean?
A: You can work with data from many buckets and workspaces as one environment, instead of managing each storage account separately.

Q: When is a unified platform like OneLake worth it?
A: For large organizations with many teams and very varied sources. For a small project or business, plain storage and a Spark or DuckDB engine is enough.

Q: What is a Fabric capacity?
A: The pool of paid compute that all Fabric workloads run on. It's expensive, around eighty-four hundred dollars a month for the size shown, so you pause it or use a trial.

Q: What is a schema registry for?
A: Storing every version of a stream's message schema, so consumers can apply the right schema to each message and schema changes can be checked for compatibility.

Q: Can you mention Snowflake in a Fabric project story?
A: Not as part of the same pipeline. Fabric is all-in-one, so processing, storage and BI should all be in Fabric. External sources feeding it are fine.

Q: How is TOP different from LIMIT?
A: They do the same thing. TOP is the Microsoft T-SQL dialect, used in SQL Server, Azure SQL and Synapse; LIMIT is used in Postgres, MySQL, Spark SQL and others, and doesn't work in T-SQL.

Q: How do you count rows matching a condition next to the total?
A: Use COUNT star for the total and SUM of CASE WHEN condition THEN 1 ELSE 0 END for the matching rows.

Q: What's the real difference between ADLS Gen2 and S3?
A: ADLS Gen2 has a hierarchical namespace with real directories, so folder renames are atomic and you can set ACLs on folders. S3 is flat, and its folders are just key prefixes.

Q: How many sources can a Fabric copy job have?
A: One. You create a separate copy job for each source.

Q: Where does a copy job put relational data versus files in a lakehouse?
A: Relational data goes into Tables as Delta tables; raw files go into the Files area, ideally a subfolder per source.

Q: Why did the ADLS and S3 copy jobs fail?
A: Authentication. ADLS needed a valid key, SAS token or service principal, and the S3 connector rejected the s3 URI and wanted the HTTPS bucket URL plus working IAM keys.

Q: What does the discharge-date filter in silver do?
A: It keeps rows where the patient hasn't been discharged yet or the discharge is on or after admission, and drops impossible rows where discharge comes before admission.

Q: How do you compute a 30-day readmission?
A: Use a window partitioned by patient and ordered by admit date, use lag to get the previous discharge date, take the days between that and the new admission, and flag it if it's 30 or less.

Q: What is a semantic model?
A: Power BI's data model: tables, relationships and measures that reports are built on. In Fabric you create one from the lakehouse's gold tables.

Q: What are common Fabric interview questions?
A: Mostly "do you have Fabric experience?", which leads into your profile narrative. Be ready to tell the story: sources, Data Factory into OneLake, Spark notebooks bronze to gold, Power BI on Direct Lake.

Q: How do you turn a non-data job into a data-engineering narrative?
A: Find the data the real system produced, like charging-station telemetry, and build a coherent pipeline around it: a stream like Kinesis, Spark Structured Streaming, a Delta bronze layer and a business use case like predictive maintenance.
