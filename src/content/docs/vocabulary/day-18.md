---
title: Day 18 Vocabulary
description: Glossary of terms and definitions from the Training 18 notes.
sidebar:
  order: 18
---

Vocabulary — Study Guide Day 18

Source: notes/Training 18.md

## Cloud Basics and Regions
- **On-premises** — Running your own physical servers in your office, with your own staff, power, space and maintenance.
- **Cloud computing** — Renting provider-managed compute and storage for a service fee, provisioned in minutes and scaled with clicks.
- **Provisioning** — Creating and setting up a cloud resource so it is ready to use.
- **POC (Proof of Concept)** — A small trial build to show something works.
- **Region** — A separate geographic area where AWS runs data centers, e.g. `us-east-1` (N. Virginia) or `us-east-2` (Ohio).
- **Availability Zone (AZ)** — An isolated data center (or group) inside a Region with its own power and networking.
- **High availability** — Staying up through a failure, e.g. by spreading resources across AZs.
- **Latency** — Delay in data reaching a user, lower when the Region is closer.
- **Data residency** — Laws requiring data to stay in a particular geography.
- **Region migration** — Moving resources to another Region, since they physically live in one Region's data centers.
- **Oracle Cloud** — Oracle's public cloud, a distant fourth behind AWS, Azure and GCP.

## IAM
- **IAM (Identity and Access Management)** — The AWS service that provides authentication and controls who can do what on which resources.
- **Authentication** — Verifying who you are.
- **IAM user** — An identity representing a person (or AI/app) using the system, with long-term credentials.
- **IAM group** — A collection of users sharing the same permissions.
- **IAM role** — An identity with temporary credentials that a user, service or app assumes; a "packet of policies."
- **Assume a role** — Taking on a role to receive its temporary credentials.
- **IAM policy** — A JSON document determining which actions a user is or isn't allowed to perform on which resources.
- **AWS managed policy** — A ready-made AWS policy such as `AmazonS3ReadOnlyAccess`.
- **Custom policy** — A policy you write yourself in JSON.
- **AdministratorAccess** — AWS managed policy granting full access.
- **IAMUserChangePassword** — Policy letting a user change only their own password.
- **AccessDenied** — Error returned when no policy allows the requested action.
- **Least privilege** — Giving each identity only the permissions it actually needs.
- **Access keys** — Long-lived programmatic credentials that can leak, unlike expiring role credentials.
- **MFA (Multi-Factor Authentication)** — A second login factor beyond the password.
- **Root user** — The account owner identity tied to the account's email.
- **Tags** — Optional labels that help organize and find resources.
- **Governance** — Organizing who may access which systems, e.g. data engineers vs web engineers.

## S3
- **S3 (Simple Storage Service)** — AWS's object store, where each bucket has its own simulated file system.
- **Object store** — Storage that saves data as whole objects under keys in buckets, with no real folders.
- **Simulated file system** — Folders shown in S3 that are really just key prefixes.
- **Bucket** — The discrete unit of S3: the globally uniquely named container you create and configure in one Region.
- **Object** — The fundamental stored entity in S3: data plus metadata under a key, read and replaced as a whole.
- **Key** — An object's unique name inside a bucket, its "path."
- **Key prefix** — The leading part of a key that the console displays as a folder.
- **Object metadata** — System and custom name-value pairs describing an object.
- **Version ID** — Identifier of a specific object version when bucket versioning is on.
- **Byte-range GET** — Reading only part of an object, used by Spark and Athena to read parts of Parquet files.
- **Bucket policy** — Permissions set on a bucket.
- **Lifecycle rule** — A bucket rule that automatically moves or deletes objects, e.g. to Glacier after 90 days.
- **Data lake** — Cheap object storage holding raw files of any format.
- **Lakehouse** — A data lake with a table layer (Delta, Iceberg, Hudi) adding warehouse features like ACID and schema enforcement.
- **Medallion buckets** — Putting Bronze, Silver and Gold in separate buckets for simpler permissions, lifecycle and cost tracking.
- **ACID (Atomicity, Consistency, Isolation, Durability)** — Guarantees that transactions are reliable.
- **Storage class** — An S3 tier trading storage price against retrieval speed and cost.
- **S3 Standard** — Default S3 class with immediate access for active data.
- **S3 Standard-IA (Infrequent Access)** — Immediate-access class with a retrieval fee for occasionally read data.
- **S3 Glacier** — Long-term storage at a lower price, just a different tier of S3.
- **Glacier Instant Retrieval** — Glacier class with millisecond retrieval.
- **Glacier Flexible Retrieval** — Glacier class with minutes-to-hours retrieval, for backups.
- **Glacier Deep Archive** — Cheapest Glacier class, with retrieval up to ~12–48 hours.
- **File system** — Storage organized as files in real directories mounted by an OS.
- **Block storage** — Raw blocks attached as a disk to one machine.

## EC2 and EBS
- **EC2 (Elastic Compute Cloud)** — AWS's rentable virtual machines ("instances"), a virtual computer in an AWS data center.
- **Instance** — One EC2 virtual machine.
- **Elastic** — Able to start, stop, resize or add capacity whenever you want, paying only while running.
- **AMI (Amazon Machine Image)** — The operating system image an instance boots from.
- **Instance type** — The CPU/memory/GPU size of an instance, e.g. `t3.micro`.
- **Instance family** — The letter in an instance type, e.g. `t` burstable, `m` balanced, `r` memory, `c` compute, `g`/`p` GPU.
- **Instance generation** — The number in an instance type; T3 is newer hardware than T2.
- **Burstable** — Instance class giving cheap baseline CPU that can burst briefly.
- **vCPU (virtual CPU)** — A virtual processor core assigned to an instance.
- **Free tier** — AWS's free usage allowance for eligible small resources such as `t3.micro`.
- **Key pair** — The key you create, download and pass to SSH into an instance.
- **SSH (Secure Shell)** — Encrypted command-line login to a remote machine, the only way to work with server OSes with no GUI.
- **Service Quotas** — AWS console/limits on resources; GPU instance quotas start at 0 vCPUs on new accounts.
- **Quota increase request** — Asking AWS to raise a service quota, e.g. for GPU instances.
- **GPU (Graphics Processing Unit)** — A chip specialized for fast parallel matrix multiplication, used for AI and graphics.
- **Matrix multiplication** — The core math of AI models that GPUs accelerate.
- **Tokenizer** — Converts text into numbers a model can process.
- **VRAM (Video RAM)** — Memory on the video card that determines how large a model you can load.
- **Crypto mining** — Main abuse AWS guards against by restricting GPU quotas.
- **EBS (Elastic Block Store)** — The way to get persistent storage on an EC2 instance: a network-attached virtual disk.
- **EBS volume** — One EBS disk, existing separately from the instance.
- **Root volume** — The EBS volume an instance boots from; survives stop/start but is deleted on terminate by default.
- **Delete on termination** — Setting that deletes the root volume when the instance is terminated.
- **Instance store** — A fast but ephemeral disk on the host that is wiped when the instance stops or terminates.
- **Ephemeral** — Temporary; lost when the resource stops.
- **Stop vs terminate** — Stopping pauses an instance (EBS kept); terminating deletes it.
- **EBS snapshot** — A point-in-time backup of a volume stored in S3 behind the scenes.
- **EFS (Elastic File System)** — A shared network file system that many EC2 instances can mount at once.
- **Elastic Beanstalk** — A non-deprecated web developer's tool that deploys and auto-scales web apps on EC2.

## VPC
- **VPC (Virtual Private Cloud)** — A basic cloud security concept: your own isolated private network inside AWS that you add resources to.
- **VPN (Virtual Private Network)** — An encrypted connection (tunnel) into a network, whereas a VPC is the network itself.
- **AWS Site-to-Site VPN** — Connects a company's office network to its VPC.
- **CIDR block** — The IP address range of a VPC or subnet, e.g. `10.0.0.0/16`.
- **Default VPC** — The VPC AWS creates in every Region for each account.
- **Subnet** — A slice of a VPC's IP range inside one Availability Zone.
- **Public subnet** — A subnet with a route to an Internet Gateway.
- **Private subnet** — A subnet with no direct route from the internet.
- **Internet Gateway** — The VPC's door to the public internet.
- **NAT Gateway** — Lets private-subnet resources reach out to the internet without being reachable in.
- **Route table** — Rules for where a subnet's traffic goes.
- **Security group** — A firewall on an individual resource.
- **VPC endpoint** — Lets private resources reach services like S3 without going over the internet.
- **Bastion host** — A public machine used as a gateway for SSH into private resources.
- **Load balancer** — Distributes incoming traffic across servers.

## EMR and Hadoop
- **EMR (Elastic MapReduce)** — AWS's managed service running Hadoop, Spark, Hive, Flink and Trino clusters built out of EC2 instances.
- **Hadoop** — Open-source framework of HDFS, YARN and MapReduce; the software that EMR runs.
- **HDFS (Hadoop Distributed File System)** — Hadoop's distributed storage layer.
- **YARN (Yet Another Resource Negotiator)** — Hadoop's resource manager.
- **MapReduce** — Hadoop's original processing engine, which EMR is named after.
- **Node** — A computer in a cluster; an EC2 instance is a node.
- **Primary (master) node** — EMR node that manages the cluster and schedules work.
- **Core node** — EMR node that runs tasks and stores HDFS data.
- **Task node** — Optional EMR node that runs tasks only, safe to add or remove.
- **Spot instance** — Cheap spare EC2 capacity that AWS can reclaim.
- **Transient cluster** — A cluster started for a job and terminated automatically when it finishes.
- **Long-running cluster** — A cluster kept up for interactive or constant work.
- **EMR on EC2** — EMR option where you manage cluster size, instance types and scaling.
- **EMR Serverless** — EMR option where you submit jobs and AWS provides compute, billing only while jobs run.
- **EMR managed scaling** — Automatic resizing of an EMR cluster between minimum and maximum sizes.
- **Release / application bundle** — The set of preinstalled applications chosen when creating an EMR cluster.
- **Bootstrap script** — A startup script that installs extra software on cluster nodes.
- **JupyterEnterpriseGateway** — EMR application letting Jupyter notebooks run kernels on the cluster.
- **Livy** — REST service for submitting Spark jobs to a cluster.
- **Presto / Trino** — Distributed SQL query engines still offered on EMR; Athena is built on them.
- **spark-submit** — Command that submits a Spark application to a cluster.
- **Databricks on AWS** — Third-party managed Spark platform with notebooks, Delta Lake and Unity Catalog.
- **Passwordless SSH (RSA keys)** — Key-based login between nodes needed when building Hadoop by hand.

## Spark Connect
- **Spark Connect** — Client-server functionality where a thin client sends Spark query plans over gRPC to a remote Spark server; introduced in Spark 3.4 and prominent in Spark 4.0.
- **Client-server** — Architecture where a client sends requests and a server processes them.
- **gRPC** — A remote procedure call protocol used by Spark Connect.
- **AQE (Adaptive Query Execution)** — Spark 3 feature that re-optimizes query plans at runtime.
- **SparkSession** — Spark's unified entry point, introduced in Spark 2.0.
- **REST API** — A web API where an app sends HTTP requests to a server.

## Serverless, EventBridge and Lambda
- **Serverless** — Servers still exist but you never see or manage them; you pay only for what you use.
- **Cold start** — Extra delay when a serverless function isn't in memory and must load first.
- **Warm (hot)** — A serverless function kept in memory after a call so later calls are faster.
- **Economies of scale** — Lower cost per unit from huge shared data centers, enabling serverless.
- **EventBridge** — An AWS serverless event bus that fires events when things happen, e.g. a file arriving in S3.
- **Event** — A JSON object describing something that happened, sent from one place to another.
- **Event bus** — The channel events flow through.
- **Rule (EventBridge)** — A pattern or schedule matching events.
- **Target (EventBridge)** — What runs when a rule matches, e.g. a Glue job or Lambda function.
- **Event-driven pipeline** — A pipeline that runs automatically when data arrives, with no polling.
- **Send notifications to Amazon EventBridge** — Bucket setting required before S3 sends events to EventBridge.
- **S3 Event Notifications** — S3 feature that can invoke Lambda directly when an object is created.
- **AWS Lambda** — Serverless service running a single function in response to an event, billed per request and millisecond.
- **lambda_handler(event, context)** — The default Lambda entry-point function.
- **Lambda limits** — 15-minute max run time and up to 10 GB memory, so Lambda suits small data.
- **SNS (Simple Notification Service)** — AWS messaging/alert service usable as an EventBridge target.
- **Step Functions** — AWS workflow orchestration service usable as an EventBridge target.

## AWS Glue
- **AWS Glue** — Basically serverless Spark, with its own UI and programming style, sized in DPUs instead of nodes.
- **Glue Studio** — Glue's visual interface for building and monitoring jobs with source, transform and target nodes.
- **Glue ETL job** — A PySpark or Scala script Glue runs serverlessly.
- **DynamicFrame** — Glue's version of a Spark DataFrame that handles messy, changing schemas.
- **toDF() / DynamicFrame.fromDF()** — Convert between DynamicFrames and Spark DataFrames.
- **GlueContext** — Glue object that wraps a SparkContext and provides a SparkSession.
- **Job bookmarks** — Remember already-processed data so the next run picks up only new files.
- **Glue triggers / workflows** — Start Glue jobs on a schedule, on demand, or after another job.
- **Incremental processing** — Processing only data that is new since the last run.
- **DPU (Data Processing Unit)** — A serverless abstraction of the nodes in a Hadoop-based system; one DPU = 4 vCPUs and 16 GB.
- **Worker type** — Glue's worker size, e.g. G.1X (1 DPU) or G.2X (2 DPUs).
- **DPU-hour** — Glue's billing unit: DPUs × run time, charged per second with a 1-minute minimum.
- **Interactive sessions** — Glue's notebook-style sessions, billed separately.
- **EMR vs Glue rule** — Use EMR for always-on, constantly processing work and Glue for occasional data to avoid paying for idle time.

## Redshift and Warehousing
- **Amazon Redshift** — AWS's premier columnar MPP data warehouse service.
- **Columnar storage** — Storing data by column with compression so analytical queries read less.
- **Leader node** — Redshift node that plans queries and combines results.
- **Compute nodes** — Redshift nodes that store data and run query pieces in parallel.
- **Slices** — Portions of a compute node that each process part of the data.
- **Distribution style (KEY, EVEN, ALL, AUTO)** — How table rows are spread across nodes.
- **Distribution key** — Column that places rows joined together on the same node.
- **Sort key (Redshift)** — The order rows are stored in, letting Redshift skip non-matching blocks.
- **Redistribution** — Moving rows between nodes for a join, Redshift's equivalent of a shuffle.
- **COPY** — The command used to ingest data into Redshift, loading S3 files in parallel.
- **IAM_ROLE (COPY)** — The role Redshift uses to read S3 during `COPY`.
- **STL_LOAD_ERRORS / SYS_LOAD_ERROR_DETAIL** — System tables showing which row and column caused a load error.
- **Redshift Spectrum** — Queries S3 files directly using the Glue Data Catalog without loading them.
- **Provisioned Redshift** — Original cluster model, ~30 minutes to set up and billed per node-hour while up.
- **Redshift Serverless** — Redshift option (GA 2022) billed per RPU-hour while queries run plus storage per GB-month.
- **RPU (Redshift Processing Unit)** — Redshift Serverless's unit of compute.
- **Workgroup** — The Redshift Serverless (or Athena) container for compute and settings.
- **RA3 nodes** — Newer Redshift node type with storage separated from compute.
- **Google BigQuery** — The first serverless data warehouse offered as a service, billed by data scanned or reserved slots.
- **Slots** — BigQuery's reserved units of compute capacity.
- **Star schema** — A fact table surrounded by dimension tables.
- **Snowflake schema** — A star schema with normalized, multi-level dimension tables.
- **MPP (Massively Parallel Processing)** — Splitting one query across many nodes working on their own data at once, then combining results.
- **Shared-nothing architecture** — Each node has its own CPU, memory and disk.
- **Scale up vs scale out** — A bigger machine vs more machines.
- **Shuffle** — Moving data across the network between nodes, the slow part of distributed processing.
- **Teradata** — A traditional MPP data warehouse vendor.
- **Azure Synapse** — Azure's MPP analytics warehouse.

## RDS and Databases
- **RDS (Relational Database Service)** — A managed cloud database server, under the hood an AWS-managed EC2 instance.
- **Database engine** — The database software RDS runs: PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, IBM Db2 or Aurora.
- **Aurora** — Amazon's cloud-built relational engine with MySQL- and PostgreSQL-compatible editions over AWS's own replicated storage.
- **RDS Custom** — RDS option for Oracle and SQL Server that gives OS access.
- **Instance class** — RDS instance size following EC2 naming, e.g. `db.m6g.large`.
- **Automated backups** — Daily snapshots plus transaction logs for point-in-time restore.
- **Point-in-time restore** — Restoring a database to any moment within the retention period.
- **Multi-AZ** — A standby copy in another AZ that RDS fails over to automatically.
- **Failover** — Automatic switch to a standby when the primary fails.
- **Read replica** — A read-only copy that takes query load off the primary.
- **Separation of concerns** — Keeping app servers and the database server separate so each can scale and be secured independently.
- **Connection / cursor** — Database client objects: a connection to the server and a cursor to pass SQL through it.
- **OLTP (Online Transaction Processing)** — Fast, real-time transactional databases serving applications, like RDS.
- **OLAP (Online Analytical Processing)** — Analytics-oriented systems such as Redshift, BigQuery, Snowflake and Delta Lake.
- **CDC (Change Data Capture)** — Extracting row-level changes from a database, e.g. with AWS DMS or Debezium.
- **AWS DMS (Database Migration Service)** — AWS service for migrating and replicating database data, including CDC.
- **Debezium** — Open-source CDC tool that streams database changes to Kafka.
- **DocumentDB** — AWS's MongoDB-compatible database.
- **DBeaver** — Graphical database client tool.
- **JDBC (Java Database Connectivity)** — Standard Java API for connecting to databases.

## DynamoDB
- **DynamoDB** — AWS's serverless NoSQL key-value and document database with single-digit-millisecond access.
- **NoSQL** — Non-relational databases with flexible schemas.
- **Item / attribute** — DynamoDB's row and field, where items can have different attributes.
- **Partition key** — Required key deciding which partition stores an item.
- **Sort key (DynamoDB)** — Optional key ordering items that share a partition key.
- **GSI (Global Secondary Index)** — An alternate partition/sort key to query by (default quota 20 per table).
- **LSI (Local Secondary Index)** — Same partition key with a different sort key (up to 5 per table).
- **Capacity modes** — On-demand (pay per request) or provisioned (set read/write capacity).
- **PartiQL** — SQL-like query option for DynamoDB.
- **Column-family database** — Database storing data by column families, like Cassandra and HBase (not DynamoDB).
- **Clustered index** — The single index defining a table's physical row order; other indexes can be many.
- **Vector index** — Index storing AI embeddings for similarity search.

## Athena and the Glue Data Catalog
- **Athena** — A serverless SQL query engine (Presto/Trino-based) that queries S3 files in place using schema on read, storing no tables itself.
- **Query engine** — Software that queries data stored elsewhere without being a full database.
- **External table** — A table definition pointing at files in an external location such as S3.
- **Schema on read** — Data stored as-is with the schema applied at query time.
- **Schema on write** — Schema defined first, with data validated when loaded.
- **Query result output location** — The S3 location (or managed query results) where Athena writes results, required before queries run.
- **Athena managed query results** — Workgroup option where Athena stores query results for you.
- **Glue Crawler** — Scans S3 files, infers or lets you specify the schema, and writes it to the Data Catalog without storing it.
- **Custom classifier** — Crawler rule for formats default inference gets wrong.
- **CREATE EXTERNAL TABLE** — DDL defining an external table in the Data Catalog without a crawler.
- **Glue Data Catalog** — Metadata store based on the Hive metastore that stores schemas long-term for schema on read.
- **Hive Metastore** — Hive's schema store, which the Glue Data Catalog is compatible with.
- **Schema evolution** — Handling a schema that changes over time.
- **Partition (Hive-style)** — Folder-based data split such as `year=2026/month=10/`.

## SageMaker and Other Services
- **SageMaker** — AWS's managed ML platform and the best shot at cloud GPU compute without a quota request.
- **SageMaker Studio Lab** — Free SageMaker environment that can give GPU access.
- **Kinesis** — AWS's managed streaming service, very close to Kafka.

## Interview Process
- **Vendor screening (Round 1)** — Technical screen by a staffing company asking basic facts from a list with set answers.
- **Client round (Round 2)** — Interview with the hiring company where the decision is ideally made.
