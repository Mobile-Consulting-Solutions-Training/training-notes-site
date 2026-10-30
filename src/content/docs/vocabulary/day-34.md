---
title: Day 34 Vocabulary
description: Glossary of terms and definitions from the Training 34 notes.
sidebar:
  order: 34
---

Vocabulary — Study Guide Day 34

Source: notes/Training 34.md

## Capstone
- **Capstone practice run** — A rehearsal of the final project presentation, set for Monday, Nov 2.
- **Capstone presentation** — The final project presentation, set for Friday, Nov 6.
- **Live demo backup** — A local copy of your pipeline code kept in case a cloud workspace has to be rebuilt before the demo.

## GCP Platform
- **GCP (Google Cloud Platform)** — Google's public cloud, the third major cloud alongside AWS and Azure.
- **Project (GCP)** — The GCP container for resources, billing and permissions, similar to an AWS account.
- **Billing account** — The GCP payment account linked to projects; a project can't use most services until billing is enabled.
- **Billing quota** — A limit on how many projects a billing account can be linked to; raising it needs a request and approval.
- **API enablement** — Turning on a service's API for a project before you can use that service.
- **gcloud** — Google Cloud's main command-line tool.
- **bq** — The BigQuery command-line tool.
- **Application Default Credentials (ADC)** — The local credentials file that client libraries use to authenticate to GCP.
- **Quota project** — The project that API usage made with your ADC credentials is billed and counted against.
- **IAM (GCP)** — GCP's identity and access management for roles and permissions.

## GCP Services
- **Cloud Storage (GCS)** — GCP's object storage, the equivalent of S3 and ADLS.
- **Storage Transfer Service (STS)** — GCP's managed service for copying files and objects from S3, Azure Blob, URLs or file systems into Cloud Storage.
- **Agent pool (STS)** — Containerized agents that STS needs to move data from POSIX file systems or S3-compatible storage.
- **BigQuery Data Transfer Service** — A GCP service for scheduled loads from SaaS apps and other sources into BigQuery.
- **Database Migration Service (GCP)** — GCP's database-aware migration service into Cloud SQL or AlloyDB.
- **Cloud Run functions** — GCP's serverless function service (formerly Cloud Functions), the equivalent of Lambda.
- **Cloud Run** — GCP's container deployment service, comparable to ECS.
- **Cloud Run job** — A container on Cloud Run that runs to completion, for batch tasks.
- **Compute Engine** — GCP's virtual machine service, the equivalent of EC2.
- **App Engine** — GCP's managed app-hosting platform, closer to Elastic Beanstalk than EC2.
- **Cloud Composer** — GCP's managed Apache Airflow, the equivalent of MWAA.
- **Cloud Dataflow** — GCP's fully managed, autoscaling service for running Apache Beam pipelines.
- **Dataproc** — GCP's managed Spark and Hadoop service.
- **Managed Service for Apache Spark** — The newer branding of Dataproc Serverless, comparable to EMR Serverless.
- **BigQuery** — GCP's serverless data warehouse, the first serverless SQL warehouse, billed mainly by data scanned.
- **Cloud SQL** — GCP's managed relational database service, the equivalent of RDS.
- **Looker Studio** — Google's dashboard tool, formerly Google Data Studio.
- **Looker** — Google's enterprise BI platform, bought by Google around 2019–2020.
- **Firestore** — GCP's NoSQL document database for customer-facing apps, similar to DynamoDB.
- **Gemini** — Google's AI model family, which integrates natively with Google services.

## Apache Beam
- **Apache Beam** — A unified programming model for batch and streaming pipelines that runs on a separate execution engine.
- **Runner** — The engine that executes a Beam pipeline, such as Direct, Dataflow, Spark or Flink.
- **DirectRunner** — The Beam runner that executes a pipeline on your own machine.
- **DataflowRunner** — The Beam runner that submits a pipeline to Cloud Dataflow.
- **Pipeline (Beam)** — The whole Beam job, a graph of steps.
- **PCollection** — A distributed dataset flowing between Beam steps.
- **PTransform** — One processing step in a Beam pipeline.
- **Pipe operator (`|`)** — Beam syntax that applies the next transform to the previous step's output.
- **Step label (`"Name" >>`)** — The name given to a Beam step, shown in the job graph.
- **Map** — A one-to-one transform producing exactly one output per input.
- **FlatMap** — A transform producing zero or more outputs per input and flattening nested collections.
- **Filter** — A transform that keeps only elements passing a condition, used for validation.
- **ParDo** — "Parallel do": applies a custom DoFn to every element.
- **DoFn** — A user-defined Beam function class with setup, process and teardown methods.
- **CombinePerKey** — A transform that aggregates values for each key, like Spark's combineByKey.
- **BatchElements** — A transform that groups elements into batches, e.g. for bulk database inserts.
- **ReadFromText / WriteToText** — Beam I/O transforms for reading and writing text files.
- **fileio.MatchFiles / ReadMatches** — Beam transforms that find files by pattern and open them.
- **PyArrow schema** — A column schema defined with Apache Arrow types, used for Parquet output.
- **argparse** — Python's module for defining command-line options for a script.

## Databases and Migration
- **AWS DMS (Database Migration Service)** — AWS's database-aware service that replicates tables from a source database to a target.
- **Replication instance** — The DMS compute that performs the migration.
- **DMS endpoint** — A DMS source or target connection definition, such as Postgres or S3.
- **Full load** — Copying all existing data in one go during a migration.
- **CDC (Change Data Capture)** — Replicating ongoing inserts, updates and deletes after the initial load.
- **Migration** — Making a complete, correct and unmodified copy of data in a new location.
- **JSONB** — Postgres's binary JSON column type.
- **Upsert** — Insert a row, or update it if the key already exists.
- **ON CONFLICT DO UPDATE** — Postgres syntax for an upsert.
- **EXCLUDED** — The Postgres pseudo-table holding the row you tried to insert in an upsert.
- **psycopg2** — The Python driver for Postgres.
- **libpq-dev** — The Postgres client development headers needed to build psycopg2 from source.
- **Idempotent** — A job that gives the same result when run more than once.

## Cross-Cloud Auth
- **Web identity federation** — Letting an outside identity, like Google's STS service account, assume an AWS IAM role without access keys.
- **Subject ID** — The unique ID of a Google service account used in an AWS role's trust policy.
- **Trust policy** — The part of an AWS IAM role that says who may assume it.
- **Implicit deny** — Denial because no policy allows an action, as opposed to an explicit deny statement.

## Narratives
- **Amazon MSK** — AWS's managed Apache Kafka service.
- **EMR Serverless** — AWS's serverless service for running Spark jobs.
- **Raw / Curated / Semantic** — Alternative names for the Bronze / Silver / Gold layers.
- **Hive → BigQuery migration** — Moving Hive's data files from HDFS to GCS and loading them into BigQuery.
