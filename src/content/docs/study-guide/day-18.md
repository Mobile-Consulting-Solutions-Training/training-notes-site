---
title: Study Guide - Day 18
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 18: AWS Cloud Fundamentals"
sidebar:
  order: 180
---

Study Guide - Day 18 (source: notes/Training 18.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Why Cloud.** On-premises means buying servers, staff, power and space, and weeks to set up. Cloud charges a service fee and is cheaper overall, with minutes to provision and easy scaling. Everything in cloud still takes time to provision.

**Regions and AZs.** A Region is a geographic area of AWS data centers (`us-east-1` = N. Virginia, `us-east-2` = Ohio); each has several isolated **Availability Zones**. Choose by latency, cost and data-residency law. One account can use every Region, but moving Regions is a migration, not a setting. The console shows one Region at a time.

**IAM.** Who can do what on which resources. **User** (person or app, long-term credentials), **group** (shared permissions), **role** (temporary credentials a service or user **assumes**), **policy** (JSON allow/deny). To grant yourself permissions: IAM roles and policies. Least privilege; roles over access keys.

**S3.** Object store; each bucket has its own simulated filesystem (keys with prefixes). Evan's "discrete unit" = the **bucket** (what you configure: Region, policies, versioning, lifecycle); AWS's fundamental stored entity = the **object** (key, data up to 5 TB, metadata, version ID). Objects can't be edited in place. Lakehouse convention: Bronze, Silver and Gold in separate buckets. **Glacier** = cheaper long-term storage tiers with slower retrieval; lifecycle rules move data there.

**EC2 and EBS.** EC2 = rentable virtual machines; choose AMI, instance type (t, m, r, c, g/p), key pair, network, storage. GPU instances need a **quota increase**. Servers have no GUI: command line only. **EBS** = persistent disk for an instance; survives stop/start; snapshots to S3. Instance store is ephemeral. EFS = shared network file system. Running instances and volumes bill even when idle.

**VPC.** A private isolated network: subnets (public/private), Internet Gateway, NAT Gateway, route tables, security groups. IAM answers "are you allowed?"; VPC answers "can you even reach it?" Put databases and clusters in private subnets; reach S3 via a VPC endpoint.

**EMR.** Managed Hadoop/Spark/Hive/Flink/Trino clusters built from EC2 instances (primary, core, task nodes), ready in 10-20 minutes. Hadoop is the software; EMR runs it for you, usually with S3 instead of HDFS (storage separate from compute). Transient vs long-running clusters; EMR Serverless. Access the cluster over SSH. **Spark Connect** (introduced 3.4, headline in 4.0) = thin client sends plans to a remote Spark server.

**Serverless.** Servers exist, you just don't manage them; pay only while work runs. S3, Lambda, Glue, Athena are serverless; EMR on EC2 isn't. If it runs constantly, serverless can cost more.

**EventBridge and Lambda.** EventBridge = event bus: events → rules → targets, plus schedules. S3 must have "Send notifications to EventBridge" enabled (S3 can also invoke Lambda directly). **Lambda** runs a function per event (`lambda_handler(event, context)`), billed per ms, max 15 minutes and 10 GB; cold vs warm starts; good for small files, not monitoring.

**Glue.** Serverless Spark with its own UI (Glue Studio), **DynamicFrames**, Data Catalog, crawlers, job bookmarks and triggers. Sized in **DPUs** (1 DPU = 4 vCPU, 16 GB; G.1X, G.2X). Billed per DPU-hour while running; data volume affects cost indirectly; no idle cost. **EMR vs Glue:** EMR for always-on, always-processing work; Glue for occasional data so you don't pay between arrivals.

**Redshift.** AWS's premier data warehouse: columnar, **MPP** (leader node, compute nodes, slices), distribution styles, sort keys, Spectrum. Went from provisioned clusters (~30 min setup, billed by uptime) to also offering **Serverless** (RPU-hours while queries run plus storage per GB-month). Load with the **`COPY`** command from S3 in parallel (many files, a prefix, Parquet; errors in `STL_LOAD_ERRORS`). **BigQuery** = first serverless warehouse (billed per TB scanned or slots). MPP = one query split across many shared-nothing nodes; data movement is the slow part.

**RDS.** Managed relational (OLTP) databases: PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, Db2, Aurora. EC2 runs the app, EBS holds OS and code, RDS holds the app's data. Under the hood an AWS-managed EC2 instance (no SSH). Backups, Multi-AZ, read replicas. In pipelines RDS is the **source** (extract from a read replica or via CDC); Redshift is the **destination**.

**Athena, Crawler, Data Catalog.** **Athena** = serverless SQL query engine (Trino) over S3 files using schema on read; stores no tables; billed per TB scanned; needs a query result location. **Glue Crawler** infers a schema and writes it, but stores nothing. **Glue Data Catalog** stores the schema long term, based on the Hive metastore, shared by Athena, Glue, EMR and Spectrum. Remember both halves.

**DynamoDB and SageMaker.** DynamoDB = serverless NoSQL key-value/document database (partition key, optional sort key, GSIs/LSIs), single-digit-ms lookups. SageMaker = managed ML platform and the easiest route to cloud GPUs.

**Interview Notes.** Round 1 is often a vendor reading set questions: "How do you ingest into Redshift?" → COPY; "What is Glacier?"; crawler vs catalog. Expect Glue questions if you list an AWS project. Reference pipelines: S3 → EMR → Redshift (classic); S3 Bronze → Glue → Silver → Glue → Gold (S3 or Redshift Serverless), then Athena, Redshift, RDS/DynamoDB by consumer.

---

# Part 2: Cheat Sheet

## Basics
- Region (`us-east-1` N. Virginia, `us-east-2` Ohio) · AZ · check the Region selector
- IAM: user · group · role (assumed, temporary) · policy (JSON) · least privilege
- VPC: subnets, IGW, NAT, route tables, security groups · IAM = allowed? VPC = reachable?

## Storage
- S3 bucket (configure) vs object (stored) · separate buckets per layer · Glacier tiers
- EBS = instance disk, persists on stop · instance store = ephemeral · EFS = shared

## Compute
- EC2 families t/m/r/c/g-p · GPU quota · CLI only
- EMR = managed Hadoop on EC2, S3 instead of HDFS · transient clusters · SSH access
- Lambda: event → function, 15 min / 10 GB, cold vs warm
- Glue: serverless Spark · DynamicFrame · DPU = 4 vCPU/16 GB · DPU-hours
- EMR (always on) vs Glue (occasional)

## Warehouses and Databases
- Redshift: columnar MPP · `COPY` from S3 · provisioned vs Serverless (RPUs) · Spectrum
- BigQuery: first serverless warehouse · per TB scanned
- RDS: OLTP source · engines incl. Aurora · read replicas, Multi-AZ
- DynamoDB: serverless key-value · partition + sort key · GSI/LSI

## Schema on Read
- Crawler finds schema · Data Catalog stores it · Athena queries S3 with it
- Hive: HDFS / metastore / HiveQL ↔ AWS: S3 / Glue Catalog / Athena

## Pipelines
- Classic: S3 → EMR → Redshift
- Serverless: S3 Bronze → Glue → Silver → Glue → Gold → Athena / Redshift / RDS

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What's the difference between a Region and an Availability Zone?
A: A Region is a geographic area like N. Virginia. Each Region has several Availability Zones, which are separate data centers with their own power and networking, so one can fail without taking the others down.

Q: How do you choose a Region?
A: By latency to your users, by cost, and by data-residency laws, like EU data having to stay in the EU.

Q: If you wanted to grant yourself certain permissions, which service would you use?
A: IAM, by attaching policies to your user, a group you're in, or a role you assume.

Q: What's the difference between a user and a role in IAM?
A: A user is a person or app with long-term credentials. A role has no password; a service or user assumes it to get temporary credentials, which is safer for anything running inside AWS.

Q: What is the discrete unit in S3?
A: The bucket, which is what you create and configure: Region, permissions, versioning. Inside it, data is stored as objects, each identified by a key.

Q: Why put Bronze, Silver and Gold in separate buckets?
A: Permissions and lifecycle rules are simpler and safer at the bucket level, a mistake in one layer can't wipe out another, and costs can be tracked per layer.

Q: What is S3 Glacier?
A: A set of cheaper S3 storage tiers for long-term data you rarely read. Retrieval is slower and costs extra.

Q: What is EBS?
A: Persistent block storage attached to an EC2 instance, like its hard drive. It's how you keep things on an instance across stops and starts.

Q: What's the difference between IAM and a VPC?
A: IAM controls who can perform which actions. A VPC controls which network traffic can reach a resource at all.

Q: What's the difference between Hadoop and EMR?
A: Hadoop is the open-source software. EMR is AWS's managed service that runs Hadoop and Spark on EC2 for you, usually with S3 instead of HDFS so the cluster can be shut down.

Q: What does serverless mean?
A: There are still servers, but you never manage them. The provider supplies compute when your work runs, and you pay only for that time.

Q: What is EventBridge?
A: An event bus that fires actions when things happen in AWS, like starting a Glue job when a file arrives in S3. It can also run things on a schedule.

Q: What is AWS Glue?
A: Serverless Spark with its own UI and its own DynamicFrame style of programming, plus the Data Catalog. Instead of nodes, you size it in DPUs.

Q: What is a DPU and how does Glue charge?
A: A DPU is a serverless unit of compute, 4 vCPUs and 16 GB of memory. Glue bills DPU-hours per second while the job runs, so more data costs more indirectly through longer runs or more DPUs.

Q: When do you use EMR versus Glue?
A: EMR when the compute is busy all the time and you want control. Glue when data arrives occasionally and you don't want to pay for idle time in between.

Q: How do you ingest data into Redshift?
A: With the COPY command, which loads files from S3 in parallel across all the slices. Split the data into multiple files for speed.

Q: How did Redshift change with Serverless?
A: Provisioned clusters took about 30 minutes to set up and billed for uptime. Serverless is ready almost immediately and bills for compute only while queries run, plus storage.

Q: What is MPP?
A: Massively parallel processing: one query is split across many nodes that each work on their own data at the same time, and the results are combined. Moving data between nodes is the slow part.

Q: What's the difference between RDS and Redshift?
A: RDS is a row-based OLTP database for an application's many small reads and writes, and it's usually a pipeline source. Redshift is a columnar OLAP warehouse for big analytical queries, usually the destination.

Q: What is Athena?
A: A serverless SQL query engine that queries files in S3 directly using schema on read. It stores no data; the table schemas come from the Glue Data Catalog.

Q: What's the difference between the Glue Crawler and the Glue Data Catalog?
A: The crawler scans files and figures out the schema in the moment, but stores nothing. The Data Catalog stores the schema long term so Athena, Glue and EMR can use it.

Q: What is DynamoDB?
A: A serverless NoSQL key-value and document database. Items are looked up by partition key, optionally with a sort key, with very fast single-digit-millisecond reads at any scale.

Q: Describe a modern serverless lakehouse pipeline on AWS.
A: Data lands in a Bronze S3 bucket, Glue cleans it into Silver and then builds Gold, stored in S3 or Redshift Serverless. Athena handles ad-hoc queries, Redshift serves dashboards, and RDS or DynamoDB serve applications.
