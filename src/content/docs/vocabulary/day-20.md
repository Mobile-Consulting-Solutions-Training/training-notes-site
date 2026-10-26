---
title: Day 20 Vocabulary
description: Glossary of terms and definitions from the Training 20 study guide.
sidebar:
  order: 20
---

Vocabulary — Study Guide Day 20

## Access
- **Access key** — An ID + secret pair that lets programs like the CLI act as your IAM user.
- **Access key ID** — The username-like half of an access key.
- **Secret access key** — The password-like half, shown only once at creation.
- **aws configure** — CLI command that saves keys, default region and output format.
- **Named profile** — A separately stored set of CLI credentials, chosen with `--profile`.
- **aws sts get-caller-identity** — Shows which identity the CLI is using.
- **CloudWatch log group** — Container for a service's logs, e.g. `/aws/lambda/<function>`.
- **Log stream** — One sequence of log events inside a log group.

## Loading
- **Full load** — Reloading all data every run.
- **Incremental loading** — Regularly loading only new data in small batches.
- **Job bookmark** — Glue feature that remembers which input files a job already processed.

## AWS Glue
- **AWS Glue** — Serverless data integration service that runs Spark ETL jobs plus its own ETL toolkit.
- **Glue job** — A configured Spark (or Python) script run by Glue.
- **glueetl** — The Glue job type for Spark ETL.
- **Glue execution role** — Role trusting `glue.amazonaws.com` that the job runs as.
- **AWSGlueServiceRole** — AWS-managed policy with basic Glue permissions.
- **Worker type (G.1X, G.2X...)** — Size of each Glue worker; G.1X = 1 DPU.
- **DPU (Data Processing Unit)** — Glue's compute unit: 4 vCPU and 16 GB memory.
- **TempDir** — S3 path where Glue writes temporary/staging files.
- **GlueContext** — Glue's wrapper around SparkContext, giving access to Glue features.
- **DynamicFrame** — Glue's flexible-schema version of a DataFrame, for messy or nested data.
- **Glue Data Catalog** — AWS's managed metastore of table definitions.
- **Crawler** — Glue component that scans data and creates catalog tables.
- **Glue connection** — Stored JDBC URL, credentials and network placement for reaching a data store.

## IAM Details
- **Implicit deny** — Denial because no statement allows the action, without any Deny statement.
- **Explicit deny** — Denial by a Deny statement, which overrides any Allow.
- **Overwrite mode** — Spark write that deletes existing output first (needs DeleteObject).
- **Append mode** — Spark write that only adds new files.

## Redshift Serverless
- **Redshift Serverless** — AWS's data warehouse without managing clusters.
- **Namespace** — The storage side: databases, schemas, tables, users, associated IAM roles.
- **Workgroup** — The compute side: RPUs, network settings and endpoint.
- **RPU (Redshift Processing Unit)** — Redshift Serverless's compute unit.
- **Price-performance target** — Workgroup setting letting Redshift scale compute automatically.
- **Base capacity** — Workgroup setting fixing the starting number of RPUs.
- **dev** — The default Redshift database.
- **Query editor v2** — Browser-based SQL editor for Redshift.
- **Federated user** — Logging into Redshift with your IAM identity instead of a database password.
- **COPY** — Redshift command for bulk-loading data from S3.

## Networking and Credentials
- **Ingress** — Network traffic coming into a system.
- **Egress** — Network traffic going out of a system.
- **Security group** — Firewall rules attached to a resource.
- **JDBC URL** — Connection string for a database, e.g. `jdbc:redshift://<endpoint>:5439/dev`.
- **Secrets Manager** — AWS service that stores credentials encrypted for services to read at runtime.
- **CloudTrail** — AWS service recording every API call, useful to see exactly what was denied.
- **NAT Gateway** — Lets resources in private subnets reach the internet outbound.
- **S3 endpoint** — Private route from a VPC to S3 (covered in Training 21).
