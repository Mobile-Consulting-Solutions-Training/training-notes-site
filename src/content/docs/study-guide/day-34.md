---
title: Study Guide - Day 34
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 34: GCP Intro, Beam and Storage Transfer"
sidebar:
  order: 340
---

Study Guide - Day 34 (source: notes/Training 34.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Capstone Presentations.** About one more week of work. Plan set on Day 35: **practice run Monday Nov 2**, **real presentations Friday Nov 6**. Single cloud is fine. Minimum shape: ingestion into object storage → Bronze/Silver/Gold → a visualization, ideally with a tool beyond Databricks' built-in charts (Looker Studio, Power BI, Streamlit). Back up your code in case a workspace has to be rebuilt.

**Why GCP.** Fewer interviews than AWS and Azure, but bench candidates panic when a GCP interview appears. "GCP is basically just the exact same thing, except with a couple of Google flourishes": easy sign-up with a Google account, nicer GCS console, one-click authorization buttons (not a silver bullet), Gemini integrating natively with Google services.

**Service Map.** GCS = S3/ADLS. **STS** (Storage Transfer Service) = bulk object migration. **Cloud Run functions** (formerly Cloud Functions) = Lambda. **Cloud Run** = ECS (containers). **Cloud Composer** = managed Airflow (= MWAA, not Step Functions). **Dataflow** = Beam-based processing (role of Glue / a Databricks notebook). **Dataproc** = Spark/Hadoop (serverless now "Managed Service for Apache Spark", = EMR Serverless). **BigQuery** = serverless warehouse. **Cloud SQL** = RDS. **Looker Studio** (formerly Data Studio) = BI. **Firestore** = app-facing NoSQL, like DynamoDB. **Compute Engine** = EC2.

**Apache Beam.** A programming model, not an engine: "it connects to some other data processor and it provides the code interface". Name = Batch + strEAM. Runners: DirectRunner (laptop), DataflowRunner, SparkRunner, FlinkRunner. Code = `with beam.Pipeline() as p:` and steps chained with the pipe `|`, each labeled `"Name" >> transform`. Terms: Pipeline, PCollection, PTransform, `Map`, `FlatMap`, `Filter` (validation), `ParDo`/`DoFn` (parallel do), `CombinePerKey` (like `combineByKey`), `BatchElements`.

**map vs flatMap (interview).** Map is one-to-one. FlatMap returns 0..n per input and "removes internal groupings": a list of lists becomes one flat collection. Use FlatMap to explode one snapshot file into many station rows.

**BigQuery.** "The first serverless SQL warehouse." Cheap storage (like GCS); you pay mostly for **bytes scanned** by queries. Cut cost with column selection, partitioning, clustering, and checking the bytes estimate. `LIMIT` doesn't reduce bytes scanned. CLI is `bq`.

**APIs and the CLI.** Each service's API must be enabled per project, with billing on. `gcloud auth list`, `gcloud config set project`, `gcloud projects list`, `gcloud services enable`, `gcloud billing projects describe` (shows `billingEnabled`). Set the ADC **quota project** to avoid the mismatch warning.

**The Billing Wall.** A new project's billing stayed `false` for 1.5+ hours. Cause: a billing **quota** on new projects; increases need a form and ~2 days. Fix: use an existing project with billing. Set up accounts before you need them.

**Local Beam + Postgres.** While waiting: Bronze JSON synced from S3, a local Beam job (PyArrow schema, `FlatMap(parse_snapshot)`) wrote Silver; another loaded **1,427** Bronze records into local Postgres (`JSONB` payload, `ON CONFLICT ... DO UPDATE` upsert using `EXCLUDED`). `psycopg2` needed `libpq-dev` + `build-essential` (or use `psycopg2-binary`). Printing every JSONB payload floods the terminal.

**AWS DMS (blocked).** Plan: local Postgres → DMS → S3 (no RDS needed when the target is S3). Needed an IAM role, a target endpoint (role ARN, not bucket ARN). Blocked: user not authorized to create the endpoint or attach policies.

**STS vs DMS.** DMS is **database-aware** (tables, full load + CDC). STS moves **files/objects** (S3, Azure Blob, URL lists, POSIX via agents) into GCS and can't read Postgres. GCP's own Database Migration Service is the database one. BigQuery Data Transfer Service = scheduled loads into BigQuery.

**STS Demo.** Source type **Amazon S3** (not "S3-compatible", which needs an agent pool). Auth: AWS IAM role trusting Google's STS service account (subject ID, web identity federation). Errors: reused DMS role → access denied; 403s until quota project set; policy only on the bronze prefix → permission denied with nothing landed. Broader policy → success.

**Migration Rule.** A migration makes a complete, correct, **unmodified** copy (same schema and row count). Transform afterwards in a separate step.

**Narratives.** Databricks + Snowflake together only if another team or partner company used Snowflake. In an AWS project say **PySpark on EMR Serverless** (or Glue) and **Amazon MSK** instead of plain Spark/Kafka (plain implies on-prem; on-prem is fine when migrating *from* on-prem). Hive → BigQuery migration tool = **STS**. Use **bronze/silver/gold** in interviews (raw/curated/semantic is equivalent but first-round screeners may not know it).

---

# Part 2: Cheat Sheet

## GCP ↔ AWS ↔ Azure
- GCS ↔ S3 ↔ ADLS · STS ↔ DMS/DataSync ↔ ADF copy · Cloud Run functions ↔ Lambda ↔ Functions
- Cloud Run ↔ ECS · Composer ↔ MWAA · Dataflow ↔ Glue · Dataproc ↔ EMR · BigQuery ↔ Redshift ↔ Synapse
- Cloud SQL ↔ RDS ↔ Azure SQL · Looker Studio ↔ QuickSight ↔ Power BI · Firestore ↔ DynamoDB ↔ Cosmos DB

## Beam
- Pipeline · PCollection · PTransform · `|` chains steps · `"Label" >>` names them
- Map (1:1) · FlatMap (0..n, flattens) · Filter (validate) · ParDo/DoFn · CombinePerKey · BatchElements
- Runners: Direct · Dataflow · Spark · Flink

## BigQuery
- Serverless · billed by bytes scanned · partition + cluster · select columns · `bq` CLI

## gcloud
- `auth list` · `config set project` · `services enable` · `billing projects describe` · `auth application-default set-quota-project`

## Migration
- DMS = database-aware · STS = objects · migrations don't transform
- STS from S3: source "Amazon S3", IAM role with web identity trust, policy covers whole path

## Postgres Upsert
- `ON CONFLICT (key) DO UPDATE SET col = EXCLUDED.col` · `EXCLUDED` = the row you tried to insert

## Narratives
- Spark → EMR Serverless/Glue · Kafka → MSK · Databricks+Snowflake needs a reason · bronze/silver/gold

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: When are the capstone presentations?
A: A practice run on Monday, November 2, and the real presentations on Friday, November 6.

Q: What does the capstone need at minimum?
A: An ingestion job into cloud object storage, processing up through bronze, silver and gold, and a visualization connected to the gold data, ideally with a tool other than Databricks' built-in charts. It doesn't have to be multi-cloud.

Q: How is GCP different from AWS and Azure?
A: Mostly it isn't. It's the same set of services with a few Google conveniences, like easy sign-up with a Google account, a friendlier storage console, and one-click permission buttons.

Q: What is Cloud Dataflow?
A: GCP's fully managed, autoscaling data processing service that runs Apache Beam pipelines, batch or streaming. It fills the same role as Glue or a Databricks notebook.

Q: What is Apache Beam?
A: A unified programming model for batch and streaming. It has no engine of its own. You write the pipeline once and choose a runner, like the direct runner locally or the Dataflow runner on GCP.

Q: What does the pipe symbol mean in Beam code?
A: It applies the next transform to the data from the previous step, so each line is one step of the pipeline. The label before the double arrow names the step.

Q: What's the difference between map and flatMap?
A: Map gives exactly one output per input. FlatMap can give zero or many and flattens nested collections, so a list of lists becomes one flat list.

Q: What is Dataproc?
A: GCP's managed Spark and Hadoop service. Its serverless Spark option is like EMR Serverless.

Q: What made BigQuery special when it launched?
A: It was the first serverless data warehouse. There's no cluster to provision, storage is cheap, and you pay mainly for the data your queries scan.

Q: How do you reduce BigQuery costs?
A: Select only the columns you need, partition and cluster tables so filters skip data, and check the bytes estimate before running. LIMIT doesn't reduce the bytes scanned.

Q: What's the GCP equivalent of Lambda, ECS, MWAA and RDS?
A: Cloud Run functions, Cloud Run, Cloud Composer and Cloud SQL.

Q: What's the difference between AWS DMS and GCP Storage Transfer Service?
A: DMS is database-aware: it connects to a database and replicates tables. STS moves files and objects between storage systems into Cloud Storage, so it can't read straight from Postgres.

Q: Which tool would migrate S3 or Hadoop files into GCP?
A: Storage Transfer Service. For scheduled loads into BigQuery there's also the BigQuery Data Transfer Service.

Q: Should a migration transform the data?
A: No. A migration makes a complete, unmodified copy with the same schema and row count. You transform afterwards in a separate step.

Q: Why did the new GCP project's billing never enable?
A: Billing on new projects was blocked by a quota, and raising it takes a request and about two days. The fix was to use an existing project that already had billing.

Q: How does Storage Transfer Service get access to an S3 bucket without access keys?
A: You create an AWS IAM role that trusts Google's transfer service account through web identity federation, and give that role read access to the whole path you're copying.

Q: What does ON CONFLICT DO UPDATE do in Postgres?
A: It's an upsert. If the key already exists, it updates the row instead of inserting a duplicate, and EXCLUDED refers to the values you tried to insert.

Q: How should you describe Spark and Kafka in an AWS project narrative?
A: Say PySpark running on EMR Serverless or Glue, and Amazon MSK for Kafka. Plain Spark and Kafka suggest an on-prem setup.

Q: When does it make sense to use Databricks and Snowflake in the same project?
A: Only when another team, business unit or partner company uses Snowflake and your Databricks team has to work with them. Otherwise Databricks can do the reporting itself.

Q: Should you say bronze, silver, gold or raw, curated, semantic?
A: Bronze, silver and gold. They're the most common terms, and first-round interviewers often work from a checklist that uses them.
