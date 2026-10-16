---
title: "Training 18 - AWS Cloud Fundamentals"
description: "AWS regions, IAM, S3, EC2, VPC, EMR, serverless, Redshift, RDS, Athena, and SageMaker."
---

Teacher: Evan Flint

Syllabus Day 19 (per file numbering) - topic: Cloud (AWS): Regions, IAM, S3, EC2, SageMaker. Class is running about one day ahead of the syllabus: dbt (listed for Day 19) was covered in Training 17, and this class covers the AWS material listed for Days 20-21 in `Course Roadmap.md`.

---

# Video Resources (Review: Snowflake, Kafka, Flink)

Shared during this class. They cover earlier topics: Snowflake (Training 15-16), Kafka (Training 12-14), Flink (Training 13-14).

| Topic | Title | Channel | Link |
|---|---|---|---|
| Snowflake | Introduction to the Snowflake Data Cloud | Snowflake Inc. | https://www.youtube.com/watch?v=MEFlT3dc3uc |
| Snowflake | Getting Started - Architecture & Key Concepts | Snowflake Developers | https://www.youtube.com/watch?v=GtVwChmxdpw |
| Snowflake | What Is Snowflake - Breaking Down What Snowflake Is, How Snowflake Credits Work And More | Seattle Data Guy | https://www.youtube.com/watch?v=GuM6dQGRFyQ |
| Snowflake | Databricks vs Snowflake vs Fabric: Which One Should You Learn? | Data with Baraa | https://www.youtube.com/watch?v=yPGEQ8vtuOw |
| Snowflake | Ontology on Snowflake: How to Make AI Actually Understand Your Data (Summit 2026) | Snowflake Developers | https://www.youtube.com/watch?v=Ooan6cErKCM |
| Snowpark | Snowflake 101: What is Snowpark? | Snowflake Developers | https://www.youtube.com/watch?v=ZzfCsmKoVQY |
| Snowpark | How to Build Python Data Engineering Pipelines with Snowpark | Snowflake Developers | https://www.youtube.com/watch?v=yTUneS1WXao |
| Snowpark | What Is Snowpark \| Learn Everything About Snowflake Snowpark (playlist) | Data Engineering Simplified | https://www.youtube.com/watch?v=-awSPRW9AOY&list=PLba2xJ7yxHB4yPg3pUrobdzeMxk4mP24S |
| Kafka | What is Apache Kafka®? | Confluent | https://www.youtube.com/watch?v=06iRM1Ghr1k |
| Kafka | Apache Kafka: What it is and where it's going. | Confluent Developer | https://www.youtube.com/watch?v=9CrlA0Wasvk |
| Kafka | Kafka Tutorial for Beginners \| Everything you need to get started | TechWorld with Nana | https://www.youtube.com/watch?v=QkdkLdMBuL0&t=56s |
| Kafka | Apache Kafka Fundamentals course, starting at 1. Introduction (playlist) | Confluent | https://www.youtube.com/watch?v=-DyWhcX3Dpc&list=PLa7VYi0yPIH2PelhRHoFR5iQgflg-y6JA |
| Kafka | Kafka Explained \| Producer, Consumer, Topics & Consumer Groups (short) | The Curious Coder | https://www.youtube.com/shorts/7E8IEF4WaIs |
| Flink | What is Apache Flink®? | Confluent | https://www.youtube.com/watch?v=PVoc5tRr6to |
| Flink | Apache Flink: What it is and how it works. | Confluent Developer | https://www.youtube.com/watch?v=X1bhZZgAlCI |
| Flink | Apache Flink 101, starting at Introduction (playlist) | Confluent | https://www.youtube.com/watch?v=3cg5dABA6mo&list=PLa7VYi0yPIH1UdmQcnUr8lvjbUV8JriK0 |

---

# Cloud Fundamentals (AWS)

## AWS Services Covered Today

| Service | Full name | What it is | Data engineering use |
|---|---|---|---|
| **Regions** | - | Geographic areas where AWS runs data centers | Where your data and compute physically live |
| **IAM** | Identity and Access Management | Who can do what in your AWS account | Giving pipelines and people only the access they need |
| **S3** | Simple Storage Service | Object store | The storage layer of the data lake / lakehouse |
| **EC2** | Elastic Compute Cloud | Rentable virtual machines | Running Spark, Kafka, Airflow, or any server you'd run yourself |
| **EBS** | Elastic Block Store | Persistent disk volumes attached to EC2 instances | Keeping data, installed software, and databases on an EC2 instance across restarts |
| **VPC** | Virtual Private Cloud | Your own isolated private network inside AWS | Keeping databases, clusters and EC2 instances off the public internet |
| **EMR** | Elastic MapReduce | Managed big data clusters (Spark, Hive, Hadoop, Flink) on EC2 | Running Spark jobs over S3 data without setting up the cluster yourself |
| **EventBridge** | - | Event bus that triggers actions when something happens in AWS | Starting a pipeline when a file lands in S3 |
| **Glue** | AWS Glue | Serverless Spark, plus a data catalog | ETL jobs without managing a cluster; sized in DPUs |
| **Redshift** | Amazon Redshift | AWS's data warehouse | The Gold layer that BI tools and analysts query with SQL |
| **RDS** | Relational Database Service | Managed relational (OLTP) databases: PostgreSQL, MySQL, etc. | The application database that pipelines extract data *from* |
| **Athena** | Amazon Athena | Serverless SQL queries directly over files in S3 (schema on read) | Ad-hoc SQL on the data lake without loading it anywhere |
| **SageMaker** | - | Managed machine learning platform | Training/serving ML models; easiest path to cloud GPU compute |

---

## Regions

Q. What is an AWS Region?

A. (Teacher's definition) *(Evan named the topic; definition not captured yet.)*

**Expanded:** A Region is a separate geographic area where AWS has data centers, for example `us-east-1` (N. Virginia) or `eu-west-1` (Ireland). Each Region is split into multiple **Availability Zones (AZs)**: physically separate data centers with their own power and networking, so one failing doesn't take down the others. Most resources you create (EC2 instances, databases) belong to one Region. S3 bucket names are global, but each bucket's data is stored in the one Region you pick.

| Concept | Meaning | Why it matters |
|---|---|---|
| **Region** | A geographic area (e.g. `us-east-1`) | Latency (closer to users is faster), cost (prices differ by Region), and data-residency laws (e.g. EU data must stay in the EU) |
| **Availability Zone** | An isolated data center (or group) inside a Region (e.g. `us-east-1a`) | High availability: spreading across AZs survives a single data-center outage |

**Gotcha:** if a resource you just made "disappeared" in the console, check the Region selector in the top-right corner. The console shows one Region at a time.

---

# IAM (Identity and Access Management)

Q. What is IAM?

A. (Teacher's definition) Identity and Access Management.

**Expanded:** IAM is the AWS service that controls **who** (identity) can do **what** (actions) on **which resources**. Every request to AWS, whether from the console, the CLI, or code like a Spark job, is checked against IAM. By default, a new identity can do nothing until a policy allows it.

| Building block | What it is | Example |
|---|---|---|
| **User** | A person or application with long-term credentials (password and/or access keys) | `alex` logging into the console |
| **Group** | A collection of users that share the same permissions | `data-engineers` group |
| **Role** | An identity with temporary credentials that is *assumed* by a service or user, with no password of its own | An EC2 instance or Glue job assuming a role to read S3 |
| **Policy** | A JSON document listing allowed or denied actions on resources | "Allow `s3:GetObject` on `arn:aws:s3:::my-bronze-bucket/*`" |

Q. If you wanted to grant yourself certain permissions, which AWS service would you use?

A. (Teacher's answer, from the class review quiz) **IAM**, and within it, **roles and policies** (plus users). "The majority of all discussions surrounding IAM is going to be about users, roles, or policies."

In practice: attach a policy to your IAM user (or to a group you're in, or a role you assume) that allows the actions you need.

**Expanded:** You can only change your own permissions if you already have IAM permissions to do so, for example as the account's admin. Otherwise an administrator has to grant them. In practice, permissions usually go on a **group** (e.g. `data-engineers`) rather than directly on a user, so everyone doing the same job gets the same access.

| Step (in the IAM console) | What you do |
|---|---|
| 1. Open **IAM → Users** (or **Groups** / **Roles**) | Pick the identity that needs the permission |
| 2. **Add permissions → Attach policies** | Choose an **AWS managed policy** (e.g. `AmazonS3ReadOnlyAccess`) or create your own **custom policy** |
| 3. For a custom policy, write the JSON | List the allowed actions and the resources they apply to (see the example below) |
| 4. Save, then test | Try the action. An `AccessDenied` error means the policy doesn't cover it yet |

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::company-bronze/*"
    }
  ]
}
```

This allows reading and writing objects in the `company-bronze` bucket and nothing else, which is least privilege in practice. (A fuller S3 policy example from an earlier class is in `Training 16.md`, under "AWS IAM Policy Example - S3 Bucket Permissions.")

**Least privilege:** give each identity only the permissions it actually needs. A pipeline that only reads Bronze and writes Silver should not have access to delete Gold.

**Roles vs access keys:** prefer roles for anything running inside AWS. Access keys are long-lived and can leak (committed to GitHub, for example). Role credentials expire automatically.

---

# S3 (Simple Storage Service)

Q. What is S3?

A. (Teacher's definition) S3 is an object store. We work with S3 buckets. Each bucket has its own simulated file system.

**Expanded:** An object store saves data as whole **objects** (a file plus its metadata) under a **key**, inside a container called a **bucket**. There are no real folders. A key like `bronze/orders/2026-10-06/orders.parquet` only *looks* like a path. The console shows `/` as folders, which is the "simulated file system." You can't edit part of an object; you replace the whole thing. In return you get nearly unlimited, cheap, very durable storage that any compute engine (Spark, Snowflake, Athena, Glue) can read.

| | Object store (S3) | File system (your laptop, HDFS) | Block storage (EBS disk on EC2) |
|---|---|---|---|
| Unit of storage | Object (data + metadata) under a key | File inside directories | Raw blocks, attached to one machine |
| Folders | Simulated (key prefixes) | Real directories | Real (once formatted with a file system) |
| Edit in place | No, rewrite the whole object | Yes | Yes |
| Scale | Practically unlimited | Limited by disks/cluster | Limited by volume size |
| Accessed by | HTTP API, from anywhere with permission | The OS mounting it | One EC2 instance at a time |
| Typical use | Data lakes, backups, raw files | Local work, Hadoop clusters | OS disk, databases on a VM |

---

## The Discrete Unit in S3: Bucket vs Object

Q. What is the discrete unit in S3?

A. (Teacher's definition) The bucket.

**Expanded:** Which answer is right depends on what "unit" means, so know both:

| If the question means... | Answer | Why |
|---|---|---|
| The unit you **manage and configure** S3 by | **Bucket** (Evan's answer) | Region, permissions (bucket policies), versioning, lifecycle rules, encryption and cost tracking are all set per bucket. That's why Evan puts Bronze, Silver and Gold in separate buckets. |
| The unit of **data you store** | **Object** (AWS documentation's wording: objects are "the fundamental entities stored in Amazon S3") | Each file you upload is one object, read, written and replaced as a whole |

In class, answer **bucket**. In an interview, mentioning both shows you understand the distinction: "The bucket is the unit you create and configure: region, access policies, versioning. Inside it, data is stored as objects, each identified by a key."

**Buckets in more detail:**
- Bucket names are **globally unique** across all AWS accounts (no one else can have `company-bronze`).
- A bucket lives in one Region, chosen when you create it.
- Buckets can't be nested. "Folders" inside a bucket are just key prefixes (the simulated file system).

**Objects in more detail:** Everything stored in S3 is an object. S3 reads, writes, versions, permissions and bills each object as one indivisible unit. You can't append to an object or change a few bytes inside it. To change it, you upload a whole new version under the same key. You *can* read part of an object with a byte-range GET, which is how Spark and Athena read only the columns or row groups they need from a large Parquet file.

| Part of an object | What it is | Example |
|---|---|---|
| **Key** | The object's unique name inside the bucket (the "path") | `bronze/orders/2026-10-06/orders.parquet` |
| **Value (data)** | The bytes themselves, from 0 bytes up to **5 TB** | The Parquet file contents |
| **Metadata** | Name-value pairs describing the object: system ones (size, content type, last modified) plus your own custom ones | `Content-Type: application/octet-stream`, `x-amz-meta-source: crm` |
| **Version ID** | Identifies a specific version when bucket versioning is on | `3HL4kqtJlcpXroDTDmJ...` |

**Bucket → key → object:** a bucket holds objects, and each key in that bucket points to exactly one object. The full address is `s3://bucket-name/key`.

**Why it matters for data engineering:** because objects can't be edited in place, "updating" a table stored in S3 means writing new files. That's why table formats like Delta and Iceberg (Training 13) track which files make up the current version of a table, rather than modifying files directly.

---

## S3 in the Lakehouse

Q. How are S3 buckets organized for a data lakehouse?

A. (Teacher's definition) Generally when building a data lakehouse, we want to put bronze in one bucket, silver in another, and gold in a third. Object stores were the basis of data lakes when they first came around, and they are still today the basis of the lakehouse architecture.

**Expanded:** A data lake is cheap object storage holding raw files of any format. A **lakehouse** adds a table layer on top (Delta, Iceberg, Hudi from Training 13) so the same files can be queried with warehouse features like ACID transactions and schema enforcement. The storage underneath is still S3. Using one bucket per medallion layer keeps them separate for permissions, lifecycle rules and cost tracking.

| Bucket | Holds | Typical IAM access | Typical lifecycle |
|---|---|---|---|
| `company-bronze` | Raw data exactly as ingested | Ingestion jobs write; transform jobs read | Keep long-term (can rebuild everything from it); move old data to cheaper storage classes |
| `company-silver` | Cleaned, deduplicated, typed data | Transform jobs write; analysts may read | Rebuildable from Bronze |
| `company-gold` | Business-level aggregates | Gold jobs write; BI tools and analysts read | Kept current; heavily queried |

**Why separate buckets instead of one bucket with folders:** permissions are simpler to write and harder to get wrong at the bucket level, a mistake in one layer can't wipe out another, and versioning, lifecycle and cost reports can be set per layer.

---

# EC2 (Elastic Compute Cloud)

Q. What is EC2?

A. (Teacher's definition) Elastic Compute Cloud. To get a GPU on an EC2 instance requires you to request an increase in your GPU quota.

**Expanded:** EC2 rents you virtual machines ("instances") by the second. You choose the **instance type** (CPU, memory, GPU), the operating system image (**AMI**), and the storage, and you manage everything on it yourself. "Elastic" means you can start, stop, resize or add instances whenever you want and pay only while they run.

New AWS accounts have **service quotas** for GPU instance families (e.g. `G` and `P` types) set to **0 vCPUs** by default, so launching one fails until you submit a quota-increase request in the **Service Quotas** console and AWS approves it. This limits surprise bills and abuse.

| Instance family | Optimized for | Data engineering example |
|---|---|---|
| `t` (e.g. `t3.micro`) | Cheap, burstable general use | Small test server, free-tier practice |
| `m` | Balanced CPU/memory | General-purpose app or Airflow server |
| `r` | Memory | Spark executors with large in-memory data |
| `c` | Compute (CPU) | CPU-heavy transformations |
| `g` / `p` | **GPU** (needs a quota increase) | ML training/inference, GPU-accelerated processing |

**Cost gotcha:** a running instance bills even when idle. Stop or terminate instances when you're done.

---

## EBS (Elastic Block Store)

Q. What is EBS?

A. (Teacher's definition) Elastic Block Store. The way to get persistent storage on an EC2 instance. In other words, if you want to keep things on your EC2 instance permanently, you need an EBS volume.

**Expanded:** An EBS volume is a network-attached virtual hard drive for an EC2 instance. It exists separately from the instance itself, so its data survives when the instance is stopped and started again. Some instance types also come with an **instance store**, a disk physically on the host machine. It's fast, but it's **ephemeral**: everything on it is wiped when the instance stops or terminates. Most instances today boot from an EBS **root volume**, and you can attach extra EBS volumes for data.

| | EBS volume | Instance store | S3 |
|---|---|---|---|
| Type | Block storage (a disk) | Block storage (a disk) | Object storage |
| Survives instance **stop** | Yes | **No** | Not attached to an instance at all |
| Survives instance **terminate** | Root volume: deleted by default (configurable). Extra volumes: kept by default | No | Yes |
| Attached to | One instance at a time (in the same Availability Zone) | Only the host it's on | Accessed by anything with permission |
| Typical use | OS disk, databases, software installed on the VM | Temporary scratch space, caches, Spark shuffle files | Data lake files, backups |

**Snapshots:** an EBS snapshot is a point-in-time backup of a volume, stored in S3 behind the scenes. You can restore it to a new volume, including in another Availability Zone.

**Cost gotcha:** EBS volumes bill for the storage you provisioned even while the instance is stopped. A stopped instance still costs money for its disks, and volumes left behind after a terminate keep billing until you delete them.

**EBS vs S3 for data engineering:** EBS is a disk for one machine. S3 is shared storage that many machines (Spark clusters, Snowflake, Athena) can read at once. Pipeline data belongs in S3. EBS is for whatever the instance itself needs to run.

---

# VPC (Virtual Private Cloud)

Q. What is a VPC?

A. (Teacher's definition) Virtual Private Cloud - a basic cloud security concept. Basically you create a VPC and add resources, such as EC2 instances, to that VPC. The VPC is isolated from other cloud resources.

**Expanded:** A VPC is your own private network inside AWS, with its own IP address range (e.g. `10.0.0.0/16`). Resources you launch into it, such as EC2 instances, databases (RDS) or EMR clusters, can talk to each other, but nothing outside can reach them unless you explicitly open a path. It's the cloud version of a company's internal office network. Every AWS account comes with a **default VPC** in each Region, which is why EC2 instances launch into one even if you never created it.

| Component | What it does | Analogy |
|---|---|---|
| **VPC** | The isolated private network, defined by an IP range | The office building |
| **Subnet** | A slice of the VPC's IP range, inside one Availability Zone | A floor of the building |
| **Public subnet** | Has a route to an **Internet Gateway**, so resources can be reached from the internet | Lobby (open to visitors) |
| **Private subnet** | No direct route from the internet | Back offices (staff only) |
| **Internet Gateway** | The VPC's door to the public internet | Front door |
| **NAT Gateway** | Lets private-subnet resources reach *out* to the internet (e.g. download packages) without being reachable *in* | One-way exit door |
| **Route table** | Rules for where network traffic from a subnet goes | Signs in the hallways |
| **Security group** | Firewall on an individual resource (e.g. "allow port 22 only from my IP") | A lock on each office door |

**IAM vs VPC (two different layers of security):**

| | IAM | VPC |
|---|---|---|
| Controls | *Who* is allowed to perform *which actions* on AWS resources | *Which network traffic* can reach a resource |
| Example | "This Glue job may read the Bronze bucket" | "Only machines inside the VPC can connect to the database on port 5432" |
| Question it answers | "Are you allowed to do this?" | "Can you even reach it?" |

**Data engineering pattern:** databases and processing clusters go in **private subnets**, so they're never exposed to the internet. Only things that must be public (a load balancer, a bastion host for SSH) go in public subnets. S3 sits outside your VPC, so private resources reach it through a **VPC endpoint** instead of going over the internet.

---

# EMR (Elastic MapReduce)

Q. What is EMR?

A. (Teacher's definition) Elastic MapReduce. An EMR cluster is built out of EC2 instances.

**Expanded:** EMR is AWS's managed service for running big data frameworks such as **Spark, Hive, Hadoop, Presto/Trino and Flink** on a cluster. You say how many machines and of what type, and EMR launches EC2 instances with the software already installed and configured. It's how you run the kind of Spark jobs from earlier classes at scale on AWS, without building a Hadoop/Spark cluster by hand. The name comes from Hadoop **MapReduce**, the processing engine it originally ran; today Spark is the most common workload on it.

| Node type | Role | Spark equivalent |
|---|---|---|
| **Primary (master) node** | Manages the cluster and schedules work (runs YARN ResourceManager) | Where the driver usually runs |
| **Core nodes** | Run tasks **and** store data in the cluster's HDFS | Executors |
| **Task nodes** (optional) | Run tasks only, no HDFS storage, so they're safe to add and remove (often cheap **Spot** instances) | Extra executors |

How EMR ties together today's services:

| Service | Its role in an EMR pipeline |
|---|---|
| **EC2** | The machines the cluster runs on |
| **S3** | Where input and output data live (read with `s3://` paths). Data is kept in S3 rather than in the cluster's HDFS so the cluster can be shut down without losing anything |
| **EBS** | Disks attached to each node for the OS, logs and temporary data |
| **VPC** | The private network the cluster runs inside |
| **IAM** | Roles that let the cluster read and write S3 (and other services) |

Q. What's the difference between Hadoop and EMR?

A. **Hadoop is the software. EMR is an AWS service that runs that software (and Spark, Hive, Flink, etc.) for you.** They aren't competitors: EMR runs Hadoop.

**Expanded:** Hadoop is an open-source framework made of **HDFS** (distributed storage), **YARN** (resource manager) and **MapReduce** (processing engine). Running it yourself means buying or renting servers, installing and configuring Hadoop on each one, and handling failures, upgrades and scaling. EMR does all of that: you ask for a cluster and get one with Hadoop/YARN already running, usually with Spark on top. EMR also lets you store data in **S3 instead of HDFS**, so storage and compute are separated and the cluster can be shut down when it's idle.

| | Self-managed Hadoop (on-premises or your own VMs) | EMR |
|---|---|---|
| What it is | Open-source software | AWS managed service that runs Hadoop, Spark, Hive, Flink, Trino... |
| Hardware | You buy/rent and maintain servers | AWS launches EC2 instances for you |
| Setup | Install and configure every node by hand | Pick versions and apps; ready in minutes |
| Storage | HDFS on the cluster's own disks | Usually S3 (`s3://`), with HDFS available for temporary data |
| Storage and compute | Coupled: data lives on the cluster, so it must stay running | Separated: data in S3, cluster can be terminated |
| Scaling | Add physical/virtual machines manually | Resize or auto-scale; add Spot task nodes |
| Cost model | Pay for servers whether busy or idle | Pay per second while the cluster runs, plus an EMR fee on top of EC2 |
| Who handles failures/upgrades | Your team | Mostly AWS |
| Typical era | 2010s on-premises big data | Cloud; common when migrating old Hadoop workloads to AWS |

**Interview one-liner:** "Hadoop is the open-source framework (HDFS, YARN, MapReduce). EMR is AWS's managed version of it. It runs Hadoop and Spark on EC2 for you and usually swaps HDFS for S3, so you can separate storage from compute and only pay for the cluster while jobs run."

**Transient vs long-running clusters:** a common pattern is a **transient** cluster: start it, run the Spark job, write results to S3, and terminate it automatically. You pay only while the job runs. A **long-running** cluster stays up for interactive or constant work.

| Option | What you manage | Best for |
|---|---|---|
| **EMR on EC2** | Cluster size, instance types, scaling | Full control, long-running or very large workloads |
| **EMR Serverless** | Nothing about clusters; submit a job and AWS provides the compute | Occasional jobs, no cluster tuning |
| **AWS Glue** (Day 22 on the syllabus) | Even less; serverless Spark ETL with a built-in data catalog | Standard ETL jobs |
| **Databricks on AWS** | A third-party managed Spark platform | Teams that want notebooks, Delta Lake and Unity Catalog |

---

# Serverless

Q. What does serverless mean?

A. (Teacher's definition) Serverless. *(Evan named the topic; definition not captured yet.)*

**Expanded:** Serverless doesn't mean there are no servers. It means **you never see or manage them**. You don't choose instance types, patch operating systems, or keep machines running. You hand AWS your code or job, AWS provides the compute when it runs, and you pay only for what you use. It's the opposite end of the scale from EC2, where you manage the whole machine.

| | Server-based (EC2, EMR on EC2) | Serverless (Glue, Lambda, EMR Serverless, Athena) |
|---|---|---|
| You manage | Instance types, cluster size, OS, scaling, shutdown | Just your code/job and its settings |
| Billing | While machines are running, even if idle | Only while work is actually running |
| Scaling | You add or remove machines | AWS scales automatically |
| Startup | Machines already running = instant | Can have a short "cold start" delay |
| Control | Full | Limited to what the service exposes |
| Best for | Constant workloads, custom setups | Spiky or occasional workloads, event-driven pipelines |

---

## EventBridge

Q. What is EventBridge?

A. (Teacher's definition) An AWS service which can cause events to fire when things happen on the system. So for example, when a file arrives in S3.

**Expanded:** EventBridge is a serverless **event bus**. AWS services publish **events** ("an object was created in bucket X", "a Glue job failed", "an EC2 instance stopped"). You write **rules** that match certain events and send them to **targets** that do something in response. It can also run things on a **schedule** (cron-style), so it often replaces a cron job.

| Piece | What it is | Example |
|---|---|---|
| **Event** | A JSON message describing something that happened | `Object Created` in `company-bronze`, key `orders/2026-10-06.csv` |
| **Event bus** | The channel events flow through (each account has a default bus) | `default` |
| **Rule** | A pattern that matches certain events, or a schedule | "Any object created in `company-bronze` under `orders/`" |
| **Target** | What runs when a rule matches | Start a Glue job, invoke a Lambda function, start a Step Functions workflow, send an SNS alert |

**Event-driven pipeline example:**

```
File lands in S3 (Bronze bucket)
        ↓  event
EventBridge rule matches it
        ↓  target
Glue job cleans it → writes to the Silver bucket
```

No one has to run the job manually or poll the bucket. The pipeline runs the moment data arrives.

**Gotcha:** S3 doesn't send events to EventBridge by default. You have to turn on **"Send notifications to Amazon EventBridge"** in the bucket's properties.

---

## AWS Glue

Q. What is AWS Glue?

A. (Teacher's definition) Glue is basically serverless Spark. It has its own user interface. It has its own style of programming that is slightly different from Spark. Instead of worrying about nodes, in Glue what you think about is DPUs.

**Expanded:** Glue runs Spark ETL jobs without you creating or managing a cluster: you write the job, choose how much capacity it gets, and Glue provides the compute only while the job runs. Compared with EMR, you give up control (instance types, cluster configuration) in exchange for not managing anything. Glue also includes the **Glue Data Catalog**, a central list of your tables and schemas that Athena, EMR and Redshift Spectrum can all share.

Glue's "own style of programming" is mainly the **DynamicFrame**: Glue's version of a Spark DataFrame that handles messy, changing schemas better (for example, a column that's a string in some files and a number in others). You can convert back and forth with `toDF()` and `DynamicFrame.fromDF()`, and you can write plain PySpark inside a Glue job.

| Glue component | What it does |
|---|---|
| **Glue Studio** | The visual user interface for building and monitoring jobs (drag-and-drop, or a script editor) |
| **ETL jobs** | Spark (PySpark or Scala) scripts that Glue runs serverlessly |
| **Data Catalog** | Stores table definitions (schemas, S3 locations) so other services can query the data |
| **Crawlers** | Scan data in S3, infer the schema, and create or update Catalog tables automatically |
| **Job bookmarks** | Remember which data was already processed, so the next run only picks up new files (incremental processing) |
| **Triggers / workflows** | Start jobs on a schedule, on demand, or after another job finishes |

| | Spark on EMR | Glue |
|---|---|---|
| Infrastructure | You pick EC2 instance types and cluster size | Serverless: no cluster to see |
| Sizing unit | Nodes (EC2 instances) | **DPUs** |
| Programming | Standard Spark DataFrames | DynamicFrames + standard Spark |
| Startup | Cluster launch takes minutes (unless already running) | Usually faster, starts per job |
| Best for | Large, custom, long-running workloads | Standard ETL jobs, event-driven pipelines |

---

### DPU (Data Processing Unit)

Q. What is a DPU?

A. (Teacher's definition) A DPU is a data processing unit - it's a serverless abstraction of the nodes that are required in a regular hadoop-based Big Data processing system.

**Expanded:** Instead of choosing EC2 instances, you tell Glue how many DPUs a job gets. **One DPU = 4 vCPUs and 16 GB of memory.** In practice you pick a **worker type** and a **number of workers**, and Glue converts that into DPUs. Billing is per **DPU-hour**, charged per second while the job runs, so more DPUs finish the job faster but cost more per minute.

| Worker type | DPUs per worker | Typical use |
|---|---|---|
| **G.1X** | 1 DPU (4 vCPU, 16 GB) | Most standard ETL jobs |
| **G.2X** | 2 DPUs (8 vCPU, 32 GB) | Memory-heavy jobs (big joins, aggregations) |
| Larger types (G.4X, G.8X) | 4 / 8 DPUs | Very demanding jobs |

| Regular Hadoop/Spark cluster (EMR) | Glue |
|---|---|
| "I need 10 `r5.xlarge` nodes" | "I need 10 G.1X workers" (= 10 DPUs) |
| You pay for nodes while the cluster is up | You pay for DPU-hours while the job runs |

---

### How Glue Charges

Q. How does Glue charge?

A. (Teacher's definition) Glue charges by the amount of data that is processed, and the amount of time that it spends processing that data per DPU.

**Expanded:** AWS's actual billing formula is **number of DPUs × time the job runs**, measured in **DPU-hours** and charged per second (with a 1-minute minimum on current Glue versions). There's no separate per-GB charge for Glue ETL jobs. The amount of data still drives the bill indirectly: more data takes longer to process, or needs more DPUs, and either one means more DPU-hours.

| Cost driver | Effect on the bill |
|---|---|
| **Number of DPUs** (workers × worker size) | More DPUs = higher cost per minute, but the job may finish sooner |
| **Run time** | Billed per second while the job runs |
| **Data volume** | Indirect: more data → longer run or more DPUs → more DPU-hours |
| **Idle time** | **None**. No job running = no charge (unlike an EMR cluster left on) |
| Extras | Data Catalog storage/requests, crawler run time, and interactive sessions are billed separately |

**Example:** a job with 10 G.1X workers (10 DPUs) that runs for 6 minutes uses 10 × 0.1 h = **1 DPU-hour**. (Check the current per-DPU-hour price for your Region on the AWS Glue pricing page.)

---

### EMR vs Glue: When to Use Which

Q. When should you use EMR vs Glue?

A. (Teacher's definition) The traditional logic about when to use EMR vs when to use Glue is that you should use EMR if you need something that is always on, and always processing data in some way. You use Glue for data that will only arrive occasionally, and you don't want to pay in between when the data is arriving.

**Expanded:** The decision comes down to **how often the compute is busy**. An EMR cluster bills for every second it's running, whether or not it's doing work. That's efficient when it's always busy, but wasteful when it sits idle waiting for the next file. Glue bills only while a job runs, so occasional data costs nothing in between. Glue's per-unit compute price is higher, though, so for constant heavy workloads an always-on EMR cluster usually ends up cheaper.

| | EMR | Glue |
|---|---|---|
| Data arrival pattern | Continuous / constant (always processing) | Occasional (e.g. a file a few times a day) |
| Billing while idle | Yes, the cluster keeps billing | No |
| Price per unit of compute | Lower (EC2 rates + EMR fee; Spot instances can cut it further) | Higher (paying for convenience) |
| Control and tuning | Full: instance types, Spark configs, any open-source tool | Limited to what Glue exposes |
| Management effort | You size, scale and shut down the cluster | Almost none |
| Typical pairing | Long-running streaming or heavy daily batch | **EventBridge** trigger: file lands in S3 → Glue job runs |

**Why "traditional":** the line has blurred. EMR can now run **transient** clusters (start, run the job, terminate) and **EMR Serverless**, which bills only while jobs run. Glue can also run streaming jobs. The always-on vs occasional rule is still the standard starting point and interview answer.

**Interview one-liner:** "EMR when the compute is busy all the time and I want control over the cluster. Glue when data arrives occasionally and I don't want to pay for idle time between arrivals."

---

# AWS Redshift

Q. What is AWS Redshift?

A. (Teacher's definition) AWS Redshift is the premier Data Warehouse service on AWS.

**Expanded:** Redshift is AWS's managed **columnar, MPP (massively parallel processing)** data warehouse, built for running analytical SQL over large amounts of data. Data is stored by column, so a query that sums one column reads only that column. Queries are split across many nodes that work in parallel. In a lakehouse on AWS, Redshift usually sits at the end of the pipeline, serving the cleaned Gold data to dashboards and analysts. It's AWS's equivalent of Snowflake.

| Concept | What it means |
|---|---|
| **Leader node** | Receives SQL, builds the query plan, and combines the results |
| **Compute nodes** | Store data and run their part of each query in parallel |
| **Slices** | Each compute node is divided into slices; each slice processes a portion of the data |
| **Columnar storage** | Data stored by column with compression, so analytical queries read far less data |
| **Distribution style** (`KEY`, `EVEN`, `ALL`, `AUTO`) | How table rows are spread across nodes. Rows that are joined together should land on the same node to avoid moving data around |
| **Sort key** | The order rows are stored in, so Redshift can skip blocks that can't match a filter (similar to Snowflake's micro-partition pruning) |
| **`COPY` command** | The fast way to load data, in parallel, from S3 (CSV, Parquet, JSON...) |
| **Redshift Spectrum** | Query files directly in S3 (using the Glue Data Catalog) without loading them into Redshift |
| **Redshift Serverless** | No cluster to size; billed only for compute while queries run |

---

### Provisioned Redshift vs Redshift Serverless

Q. How did Redshift change from a cluster system to serverless?

A. (Teacher's definition) A few years ago Redshift went from an ordinary cluster type system where you had to provision it and wait for it to get set up (about 30 minutes), and which charged by uptime (usually at a high rate), to a serverless system. In Redshift Serverless, you don't have to pay for server uptime, you pay a monthly rate based on GB of data that are stored on the system, plus extra for queries.

**Expanded:** Redshift Serverless became generally available in 2022. **Provisioned clusters still exist**: serverless was added as an option, not a replacement. In Serverless, compute is measured in **RPUs (Redshift Processing Units)**. You're billed for RPU-hours, per second, only while queries are running; that's the "extra for queries." Storage is billed separately per GB-month; that's the "monthly rate based on GB." When nothing is running, compute costs nothing. It's the same idea as Glue's DPUs: a serverless unit of compute instead of nodes.

| | Provisioned Redshift (original) | Redshift Serverless |
|---|---|---|
| Setup | Choose node type and count, wait (~30 min) for the cluster | Create a workgroup; ready almost immediately |
| Compute billing | Per node-hour **while the cluster is up**, busy or idle | Per **RPU-hour** only while queries run |
| Storage billing | Included with nodes (or separate on RA3 nodes) | Separate, per GB-month |
| Scaling | Resize the cluster yourself | Automatic |
| Best for | Steady, heavy, predictable workloads | Spiky or occasional query loads, getting started |

This follows the same rule as **EMR vs Glue**: if something is busy all the time, a provisioned cluster can be cheaper. If it sits idle between uses, serverless avoids paying for idle time.

---

### Loading Data: the `COPY` Command

Q. How do you ingest data into Redshift?

A. (Teacher's definition) To ingest data into Redshift, you use the COPY command.

**Expanded:** `COPY` loads files from S3 (and a few other sources) into a Redshift table **in parallel**: every slice on every node loads a share of the files at once. That's why it's much faster than `INSERT` statements, which go through the leader node one batch at a time. Redshift reads S3 using an **IAM role** attached to it.

```sql
COPY sales.orders
FROM 's3://company-gold/orders/'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftS3ReadRole'
FORMAT AS PARQUET;
```

| `COPY` tip | Why |
|---|---|
| Split data into **multiple files** (ideally a multiple of the number of slices) | One big file can only be loaded by one slice; many files load in parallel |
| Point at a **prefix/folder**, not one file | Loads every file under it in one command |
| Use **compressed** or **columnar** files (gzip CSV, Parquet) | Less data to transfer from S3 |
| Check `STL_LOAD_ERRORS` (or `SYS_LOAD_ERROR_DETAIL`) when a load fails | Shows which row and column caused the error |

Same idea as Snowflake's `COPY INTO` from a stage (Training 15-16).

---

### Google BigQuery

Q. What is Google BigQuery?

A. (Teacher's definition) The first serverless data warehouse made available as a service.

**Expanded:** BigQuery is Google Cloud's data warehouse, launched around 2010-2011, well before Redshift Serverless (2022). From the start there was no cluster to create: you load data and run SQL, and Google provides the compute. It's billed either **on-demand** (per TB of data a query scans) or by **capacity** (reserved compute "slots"), plus storage. Because on-demand billing is by data scanned, `SELECT *` on a huge table is expensive. Selecting only the columns you need and partitioning tables directly lower the bill.

| | Redshift | BigQuery | Snowflake |
|---|---|---|---|
| Cloud | AWS | Google Cloud | AWS, Azure, GCP |
| Serverless | Option since 2022 (provisioned clusters still exist) | Serverless from the start | Not fully: you size virtual warehouses, but they start and stop automatically |
| Compute billing | Node-hours, or RPU-hours (Serverless) | Data scanned per query, or reserved slots | Credits per second while a warehouse runs |

GCP data engineering is on the syllabus for Week 8.

---

### MPP (Massively Parallel Processing)

Q. What is MPP?

A. **Massively Parallel Processing**: one query is split into pieces that run at the same time on many nodes, each working on its own slice of the data, and then the results are combined.

**Expanded:** In a single-server database, one machine does all the work for a query. In an MPP system, the data is spread across many nodes and each node has its own CPU, memory and disk. (This is called **shared-nothing** architecture.) When a query comes in, the leader breaks it into steps, every node runs those steps on its own data at the same time, and the leader combines the partial results. If each of 10 nodes holds a tenth of the data, the query can run close to 10 times faster.

Example: `SELECT region, SUM(sales) FROM orders GROUP BY region` on 1 billion rows across 4 nodes:

| Step | What happens |
|---|---|
| 1 | Leader node receives the SQL and plans it |
| 2 | Each node sums `sales` by `region` for **its own** ~250 million rows, all at once |
| 3 | Nodes send their small partial totals back |
| 4 | Leader adds the partials together and returns the final result |

**Data movement is the slow part.** If a join needs rows that live on different nodes, the data has to be sent across the network (a "shuffle" in Spark, "redistribution" in Redshift). That's why Redshift lets you choose a **distribution key**: rows that get joined together are stored on the same node.

| | Traditional database (e.g. single-server Postgres) | MPP warehouse |
|---|---|---|
| Machines per query | One | Many, in parallel |
| Scales by | Bigger machine (scale up) | More nodes (scale out) |
| Built for | Many small transactions (OLTP) | Large analytical queries (OLAP) |
| Examples | PostgreSQL, MySQL | **Redshift**, Snowflake, BigQuery, Azure Synapse, Teradata |

**Connection to Spark:** it's the same idea as Spark (driver plans the work, executors process partitions in parallel, shuffles are expensive). MPP warehouses apply it to SQL over data the warehouse stores itself, while Spark is a general processing engine over files.

---

**Redshift vs Snowflake:**

| | Redshift | Snowflake (Training 15-17) |
|---|---|---|
| Cloud | AWS only | AWS, Azure, GCP |
| Compute and storage | Originally coupled to the nodes. Separated on newer **RA3** node types and in Serverless | Separated from the start (virtual warehouses + central storage) |
| Tuning | More hands-on: distribution and sort keys, cluster sizing (largely automated today) | Mostly automatic |
| Loading from S3 | `COPY` | `COPY INTO` from a stage |
| AWS integration | Native: IAM, Glue Catalog, S3, Kinesis, SageMaker | Through integrations and storage stages |
| Billing | Per node-hour (provisioned) or per compute used (Serverless) | Credits per second while a warehouse runs |

**Where it fits in today's AWS services:**

```
S3 (Bronze) ──Glue / EMR──▶ S3 (Silver / Gold) ──COPY──▶ Redshift ──▶ BI dashboards
                                     └──── or query in place with Redshift Spectrum
```

On the syllabus, Redshift gets its own classes later (Days 23-24: architecture, `COPY`, distribution/sort strategies, optimization).

---

# RDS (Relational Database Service)

Q. What is RDS?

A. (Teacher's definition) Relational Database Service. RDS is a cloud database server.

Let's say you want to deploy a web app that uses a database on an EC2-based system. EC2 will provide the compute, but it's got no persistent storage. EBS is persistent storage, but it's not for larger volumes of data - EBS is better for storing the essential system files and dependencies that the application needs, as well as the application itself. RDS is the separate database server that is dedicated to storing and serving the data that is required by the application.

**Evan's web app example, as a table:**

| Piece | Job in the web app | Holds |
|---|---|---|
| **EC2** | Compute: runs the application code | Nothing permanent by itself |
| **EBS** | Persistent disk attached to the EC2 instance | The OS, system files, dependencies, and the application itself |
| **RDS** | Separate, dedicated database server | The application's **data**: users, orders, products... |

```
Users ──▶ EC2 (web app) ──SQL──▶ RDS (PostgreSQL / MySQL)
              │
             EBS (OS + app code + dependencies)
```

Under the hood, RDS is just an EC2 instance. It's an EC2 instance which by default allows you to install whatever database you want.

**What "under the hood" means:** this follows the same pattern as EMR ("an EMR cluster is built out of EC2 instances"). Many AWS services are EC2 machines with software and management added. RDS instance classes even follow EC2 naming, e.g. `db.m6g.large` ↔ `m6g.large`. The instance is AWS-managed, though: it doesn't appear in your EC2 console, and you can't SSH into it.

**"Whatever database you want," clarified:** you pick from RDS's **supported engines** (PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, IBM Db2, Aurora) and versions when you create the instance. You can't install an arbitrary database such as MongoDB or Cassandra, or add OS-level software. If you need that, run the database yourself on a plain EC2 instance with EBS, or use a different AWS service (e.g. DocumentDB for MongoDB-compatible workloads). **RDS Custom** (Oracle and SQL Server only) is the exception that gives OS access.

| | Database on plain EC2 (self-managed) | RDS |
|---|---|---|
| Underlying machine | EC2 instance you manage | EC2 instance AWS manages |
| Which database | Anything you can install | Supported engines only |
| OS / SSH access | Yes | No (except RDS Custom) |
| Backups, patching, failover, replicas | You build and run them | Built in |

**Why keep the data on a separate RDS server instead of a database installed on the EC2/EBS machine:** EBS volumes can technically be very large (up to tens of TB), so the reason isn't capacity. It's separation of concerns:
- The app servers can be replaced, scaled out to many EC2 instances, or redeployed without touching the data. All of them connect to the same RDS database.
- RDS adds what you'd otherwise build yourself: automated backups, point-in-time restore, Multi-AZ failover, read replicas and patching.
- The database can be sized and secured separately, for example in a private subnet that only the app servers can reach.

**Expanded:** RDS runs ordinary relational databases for you: **PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, IBM Db2**, and Amazon's own **Aurora** (compatible with MySQL and PostgreSQL). You choose the engine and size, and AWS handles installation, patching, backups, failover and storage. You still write normal SQL and connect with normal tools (`psql`, DBeaver, JDBC). These are **OLTP** databases: built for an application's many small reads and writes, not for big analytical queries.

| Feature | What it does |
|---|---|
| **Engines** | PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, IBM Db2, Aurora |
| **Automated backups** | Daily snapshots plus transaction logs, so you can restore to any point in time within the retention period |
| **Multi-AZ** | A standby copy in another Availability Zone; RDS fails over to it automatically if the primary goes down (high availability) |
| **Read replicas** | Read-only copies that take query load off the primary, e.g. reporting or extraction jobs |
| **Storage** | EBS-backed, can auto-grow |
| **Networking** | Lives inside your **VPC**, normally in a private subnet; access controlled by security groups |

**RDS vs Redshift (OLTP vs OLAP), a common interview question:**

| | RDS | Redshift |
|---|---|---|
| Type | Relational database (**OLTP**) | Data warehouse (**OLAP**) |
| Storage layout | Row-based | Columnar |
| Workload | Many small, fast reads/writes (one order, one customer) | Few big scans and aggregations over millions/billions of rows |
| Scales by | Bigger instance (scale up) + read replicas | More nodes (MPP, scale out) |
| Typical user | The application (website, app back end) | Analysts, BI dashboards |
| Role in a pipeline | **Source** | **Destination** |

**Where RDS fits in a data pipeline:** the application writes to RDS. Data engineers extract from it, ideally from a **read replica** so they don't slow the live application, and land the data in S3 Bronze. The extraction can be a full copy, incremental queries (`WHERE updated_at > last_run`), or **CDC (change data capture)** with a tool like AWS DMS or Debezium → Kafka.

```
App ──▶ RDS (PostgreSQL) ──extract / CDC──▶ S3 Bronze ──Glue / EMR──▶ Silver / Gold ──COPY──▶ Redshift
```

On the syllabus, RDS source patterns come up again on Day 24 (Redshift + Kinesis + RDS).

---

# Athena

Q. What is Athena?

A. (Teacher's definition) Athena uses schema on read technology, to read tables that are not located in it, because tables cannot actually be stored in Athena. In order to parse the data in an external table, that table must have a formal schema description, because this is SQL.

**Expanded:** Athena is a **serverless SQL query engine** (based on Presto/Trino) that queries files sitting in S3 (CSV, JSON, Parquet, ORC...) in place. Athena stores no data of its own: every table is an **external table** pointing at an S3 location. The files are just bytes, though, and SQL needs to know the column names and types. So every table needs a schema stored somewhere else, which is the **Glue Data Catalog**. Billing is **per TB of data scanned** (like BigQuery on-demand), so Parquet, compression and partitioning directly lower the cost.

| Schema on write (warehouse: Redshift, Snowflake, RDS) | Schema on read (Athena, Hive, Spark on files) |
|---|---|
| Schema defined first; data must match it when loaded | Data stored as-is; schema applied when you query it |
| Bad data rejected at load time | Bad data found at query time (shows up as errors or NULLs) |
| Data lives inside the system | Data stays in S3; system only holds the schema |
| Fast, optimized queries | Flexible: the same files can be read with different schemas |

(See also the data lake vs warehouse vs lakehouse comparison in `Training 0.md`.)

---

## Glue Crawler

Q. How do you create a schema for Athena to use?

A. (Teacher's definition) To create a schema for Athena to use, you will need to pass it through the Glue Crawler. The Crawler can either intuit a schema for you or you can use it to manually specify your schema. But the schema is NOT stored in the crawler, because the crawler cannot store data.

**Expanded:** A crawler is a job that scans an S3 location, samples the files, **infers** the format, columns, data types and partitions (e.g. `year=2026/month=10/` folders), and then **writes** a table definition into the Glue Data Catalog. It can run on demand or on a schedule, so newly added partitions and columns get picked up. The crawler only *creates* the schema; it doesn't keep it.

| Way to get a table into the Data Catalog | When to use it |
|---|---|
| **Glue Crawler** (infers the schema) | Many files, unknown or changing schemas, new partitions arriving regularly |
| **Crawler with custom classifiers** | The default inference gets the format wrong (unusual CSV, custom log format) |
| **`CREATE EXTERNAL TABLE` DDL in Athena** | You already know the schema and want exact control. This writes to the same Data Catalog without a crawler |
| **Add table manually in the Glue console** | Small, one-off tables |

**Gotcha:** crawler inference can guess wrong (e.g. a ZIP code read as an integer, losing leading zeros, or every column typed as `string` in headerless CSVs). Check the table definition after the first crawl.

---

## Glue Data Catalog

Q. Where is the schema stored?

A. (Teacher's definition) The schema is stored in the Glue Data Catalog. The Glue Data Catalog is based on the Hive metastore - it's a metadata store for implementing schema on read, just like in Hive.

**Expanded:** The Data Catalog stores **metadata only**: databases, tables, column names and types, file format, S3 location and partitions. The data itself stays in S3. Because it's compatible with the Hive Metastore (Training 8, 11), many services can share the same table definitions. Define a table once and query it from all of them.

| Piece | What it is | Stored where |
|---|---|---|
| The data | Files (Parquet, CSV...) | **S3** |
| The schema / table definition | Columns, types, format, location, partitions | **Glue Data Catalog** |
| The thing that creates schemas | Scans files and writes definitions | **Glue Crawler** (stores nothing) |
| The thing that queries | Runs SQL using the catalog's schema against the S3 files | **Athena** (stores nothing either) |

Services that read the Glue Data Catalog: **Athena, Glue ETL jobs, EMR** (Spark/Hive, configured to use it as the metastore), **Redshift Spectrum**, and Lake Formation (permissions).

```
S3 files ──scanned by──▶ Glue Crawler ──writes schema──▶ Glue Data Catalog
                                                              │
     Athena / Redshift Spectrum / EMR / Glue jobs ◀── read schema ──┘
                         └── read the actual data from S3
```

| Hive (on-premises, Training 8) | AWS equivalent |
|---|---|
| HDFS (where the files live) | S3 |
| Hive Metastore (schemas) | Glue Data Catalog |
| Hive / HiveQL engine (runs SQL) | Athena |

---

# SageMaker

Q. What is SageMaker?

A. (Teacher's definition) Our best shot at being able to access some level of GPU compute on the cloud without permission.

**Expanded:** SageMaker is AWS's managed machine learning platform: notebooks, training jobs, model hosting and pipelines. Because AWS manages the underlying machines, some SageMaker options (such as **SageMaker Studio Lab** or certain notebook instance types) can give access to GPU compute without first going through an EC2 GPU quota request. Quotas still exist in SageMaker, but some are not zero by default the way new-account EC2 GPU quotas are.

| | EC2 with a GPU | SageMaker |
|---|---|---|
| What you manage | Everything: OS, drivers, libraries, shutdown | Mostly just your code and data |
| GPU access on a new account | Blocked until a quota increase is approved | Often possible without a request |
| Best for | Full control, custom setups | ML experiments, training and deploying models |

---

# Industry / Interview Notes

- **Expect AWS vocabulary questions in round 1.** Evan described the usual data engineering interview process:

  | Round | Who | What to expect |
  |---|---|---|
  | **Round 0** | Vendor (staffing company) | Brief intro call |
  | **Round 1** | Vendor technical screening | Question after question on basic technical facts, often read by a non-technical person from a list with set answers. Answer in the expected terms |
  | (Sometimes a second vendor screen) | Vendor | "Always very frustrating" |
  | **Round 2** | The client | Ideally the hiring decision is made here, though some clients add a 3rd or 4th round |

- **Known round-1 questions from today:**
  - *How do you ingest data into Redshift?* → **The `COPY` command.** `COPY` isn't unique to Redshift, but this question comes up a lot specifically for Redshift.
  - *What is S3 Glacier?* → Long-term, low-cost storage tier of S3 ("every once in a while it is asked about in a job interview").
  - *Glue Crawler vs Glue Data Catalog* → The crawler *finds* the schema; the catalog *stores* it. Evan says many students remember only the crawler, which is "only remembering half."
- **Glue is common in interviews:** "If you have an AWS project on your profile, there is a high probability that you are going to be asked to talk about Glue."
- **Goal of today's class:** be able to talk fluently about building cloud architectures. The two reference pipelines Evan described are in the Agent Generated Notes below ("Putting It Together").
- **Cost discipline:** never leave cloud resources running when you're done. EC2-based services bill for uptime, not use. Evan closed an AWS account over charges that continued after a GPU quota increase.

---

# Agent Generated Notes (from Class Recording)

Source: `transcriptions/Training 18 – 2026-10-06 13-07-38/transcript.md` (3h53m, all lecture; the planned demos were mostly a console tour). Items below are things Evan said in class that weren't already in the notes above. Corrections are marked **Accuracy note** where something he said doesn't match how AWS currently works.

---

## Why Cloud at All? (On-Premises vs Cloud)

Teacher's explanation: before cloud, "you buy the actual physical server, you keep it in your office, and you maintain it." That means maintenance, configuration management, staff, electricity and rented space. "Cloud comes along in order to try and simplify that infrastructure away." The provider charges a service fee for the compute, and "in the long run and taking all things into account will come out cheaper, even if at the moment it seems expensive."

**Expanded:** Cloud services can look expensive to an individual learning them, but the comparison that matters to a business is the *total* cost of doing it yourself.

| On-premises (e.g. self-built Kafka cluster) | Cloud (e.g. AWS Kinesis) |
|---|---|
| Buy the servers up front | Pay a service fee for what you use |
| Pay staff to maintain hardware, patch, configure | AWS maintains the hardware |
| Pay for power, cooling, space | Included |
| Engineers write and run the infrastructure software | Hire an engineer who knows the managed service |
| Weeks to buy, set up and install | Minutes to provision (up to ~30 for the slowest services) |
| Hard to scale (buy/remove hardware) | Scale with a few clicks |

- **Kinesis** = AWS's managed streaming service, "basically something that's very close to Kafka." When doing a proof of concept (POC) with it, **strictly limit the messages you send**, or the bill will be uncomfortable.
- "Everything in cloud takes time to provision. That's one thing you're definitely going to find out."

---

## Regions: Evan's Explanation

- Regions are company-managed data centers around the world; the closer to the end customer, the faster data reaches them. This matters more as customers spread globally (China, India, Australia, South America).
- Data centers are "big gigantic warehouses" with enough compute to host the infrastructure of many large corporations at once.
- **You don't need a new account when you move countries.** One account can use any Region. Evan moved his resources from Frankfurt (living in Prague) to US West (Las Vegas area) to São Paulo (Brazil).
- **Changing Region isn't a setting, it's a migration.** Resources physically live in that Region's data center. A Frankfurt server is reachable from Virginia (it's the internet), but traffic crosses the Atlantic. For customers on both continents you'd run **two copies** of the infrastructure, one per Region, and pay for both.
- Examples he gave: US (N. Virginia, Ohio, Oregon, N. California), Europe (London, Dublin/Ireland, Frankfurt, Paris), South America (São Paulo, the only broadly available option there), Southeast Asia (usually Singapore), plus Australia and China.

**Accuracy note:** Evan said "US East 2, which is Northern Virginia." The Region codes are **`us-east-1` = N. Virginia** (AWS's largest Region) and **`us-east-2` = Ohio**. The California Region (`us-west-1`) is in Northern California, which he called San Francisco.

---

## IAM: Users, Roles and Policies (Evan's Model)

Teacher's definition: "IAM is the main [service] in any one of the cloud services that you provide authentication details. So it's also how you organize the permission structure of the organization." "The majority of all discussions surrounding IAM is going to be about users, roles, or policies."

| Term | Evan's definition |
|---|---|
| **User** | "Represent[s] a human being who is actually using the system, or possibly an AI that is using the system" |
| **Role** | "Basically a packet of policies" |
| **Policy** | "Determines what that user is allowed to do or not allowed to do"; written in **JSON** |
| Relationships | You can edit individual policies, attach policies to roles, and one user can have one or many roles |

- **Governance example:** data engineers get access to the machines they work on (e.g. the Redshift cluster) but not the production web server; web engineers get the web server but not Redshift, because "that's data engineer territory."
- **`AdministratorAccess` policy:** "the first thing that you want to give yourself" if you create an IAM user for yourself; it removes most permission problems. (In a real company you'd follow least privilege instead.)
- **`IAMUserChangePassword` policy:** lets a user change *their own* password, not other people's.
- **Tags** are optional labels that help organize and find resources.
- The console's security credentials page is where sign-in links, **access keys**, and **MFA** are set up. Evan's root user had MFA; his IAM user didn't.
- **Root user vs IAM user:** with a personal account you might sign in as the root user (the account's email). In a company account you sign in as an IAM user.

**Accuracy note (precise AWS terms):** in AWS, policies can be attached **directly to users, to groups, or to roles**. Users usually get permissions through **groups** (Evan's user was in a "full AWS admin" group). A **role** isn't permanently attached to a user; a user, service or application **assumes** it to get temporary credentials. Evan's "a role is a packet of policies" is a good mental model; "assumes a role" is the wording interviewers expect.

---

## S3: Extra Points from Class

- **S3 = Simple Storage Service**: "three S's, and that's why we call it S3." It "lives up to its name."
- **Store anything:** images, video, music, any file type, no formatting needed. Don't put images, music or video in a SQL database ("It's a really bad idea").
- **Old way vs lake:** ETL into a big, complicated data warehouse required data to be formatted *before* it arrived. An object store accepts data as-is, which is why object stores became the basis of data lakes and lakehouses.
- **Console tour:** click into a bucket to see "folders" (key prefixes), use **Upload** to add files, or create folders. The same can be done from the AWS CLI.
- **Evan's discrete-unit question, clarified:** he meant "a unit of storage that is separated from other units of storage... you can store a lot of objects in one of these units," i.e. the **bucket**, the container. (See "The Discrete Unit in S3" above.)

### S3 Glacier

Teacher's definition: "Glacier is basically long term storage at a lower price." It's "just a different tier of S3."

**Expanded:** Glacier storage classes are for data you must keep but rarely read: archives, compliance records, old raw data. Storage is much cheaper than S3 Standard, but reading data back can take minutes to hours (depending on the class) and costs extra per retrieval. **Lifecycle rules** can move objects automatically, e.g. Bronze files older than 90 days → Glacier.

| Storage class | Retrieval time | Use for |
|---|---|---|
| S3 Standard | Immediate | Active data (Silver/Gold, recent Bronze) |
| S3 Standard-IA (Infrequent Access) | Immediate, retrieval fee | Data read occasionally |
| Glacier Instant Retrieval | Milliseconds | Archives still read now and then |
| Glacier Flexible Retrieval | Minutes to hours | Backups |
| Glacier Deep Archive | Up to ~12-48 hours | Long-term compliance archives; cheapest |

---

## EC2: Extra Points from Class

Teacher's definition: "An EC2 instance is just a computer that is on their system. It's a virtual machine... a simulation of that thing that lives in an AWS data center." The name throws people off; it's just a virtual computer, which may be tiny, laptop-sized, or far bigger.

- Same idea as a VM on your laptop (you choose CPU, RAM and storage), except it runs on a data center with thousands of cores. A VM can never be more powerful than the physical machine it runs on.

**Launch-instance page tour:**

| Setting | What it is |
|---|---|
| **Name** | Label for the instance |
| **AMI (Amazon Machine Image)** | The operating system image: Amazon Linux (default), Ubuntu, Red Hat, SUSE, Debian, Windows, even macOS |
| **Instance type** | CPU/memory size, e.g. `t2.nano`, `t3.micro` up to very large types |
| **Key pair** | Create it, download it, and pass it when you SSH in. "Relatively easy compared to other forms of cloud authentication" |
| **Network settings** | VPC, subnet, allowed traffic (e.g. HTTP), CIDR blocks |
| **Storage** | EBS volumes |

- **Server OSes have no graphical interface.** On EC2 (or anything built on EC2) the **command line is the only way** to work with the machine. That's why Evan insists on learning the command line.
- **`t2.micro` vs `t3.micro`:** t2.micro = 1 vCPU, 1 GB; t3.micro = 2 vCPUs, 1 GB, and t3.micro is the **free-tier eligible** one in the console he showed. Larger examples: 32 vCPU / 128 GB, and 48 vCPU / 384 GB.
- The company training account has two stopped `t3.small` instances; training accounts use small instances because they're cheap.
- **Hosting a website on EC2:** run your app on localhost and expose a port, just as on a laptop. It won't auto-scale unless you configure it.

**Accuracy note:** Evan said the T2 vs T3 difference "depend[s] on what the relative amount of compute versus memory versus disk is." The number is the **generation** (T3 is newer hardware than T2); the letter is the **family** (T = burstable general purpose). The compute/memory balance is set by family and size (`micro`, `small`, `large`...).

### Elastic Beanstalk (student question)

Q. Is Elastic Beanstalk deprecated?

A. (Teacher's answer) "It is not deprecated. It's just that it's not really relevant to data engineering workloads. Elastic Beanstalk is more of a web developer's tool." It's designed to build a website that starts small and scales automatically as traffic grows.

**Expanded:** AWS has hundreds of services, and many are never used by data engineers. Beanstalk deploys and auto-scales web apps on EC2 for you. The data engineering services from today are S3, IAM, EC2/EBS, EMR, Glue, Lambda, EventBridge, Redshift, RDS, DynamoDB and Athena.

---

## EBS: Evan's Explanation

- "An EC2 instance is ephemeral... once you've shut it down, everything is gone." The EBS volume is the persistent storage you attach. "The EBS volume is the storage. The EC2 instance is the compute."
- **Analogy:** like a hot-pluggable hard drive or a USB stick holding your data. You can even run a whole Linux OS from a USB stick, which is analogous to attaching an EBS volume to an EC2 instance.

**Accuracy note:** this is true for **instance store** volumes and for **terminated** instances. Today most EC2 instances boot from an **EBS root volume** by default, so data on it **does survive a stop and start**. What's lost is instance-store data, and the root volume when the instance is *terminated* (its default "delete on termination" setting). See the EBS comparison table above.

**EFS (mentioned in the quiz):** Evan said EFS is "a slightly different thing" from EBS. **EFS (Elastic File System)** is a shared network file system that **many EC2 instances can mount at once**. EBS attaches to one instance at a time (in the same Availability Zone).

| | EBS | EFS | S3 |
|---|---|---|---|
| Type | Block storage (a disk) | Network file system | Object storage |
| Attached to | One EC2 instance | Many instances at once | Accessed over HTTP by anything with permission |
| Feels like | A local hard drive | A shared network folder | Buckets of objects |

---

## VPC: Evan's Analogy

Teacher's explanation: "When you hear VPC, some of you are thinking VPN. Very, very similar concepts. A VPC is basically the same thing as a VPN, except that it is exclusively with cloud services. So it's like a private network... it is insulated from other traffic that is out there, which could potentially pose a threat to it."

**Expanded:** the analogy works for the idea of a private network. Technically, a **VPN** is an encrypted *connection* (tunnel) into a network, and a **VPC** is the private *network itself*. They're often used together: companies connect their office network to their VPC with an **AWS Site-to-Site VPN**.

---

## GPUs: Why AI Needs Them, and Why AWS Restricts Them

Teacher's explanation:
- "A GPU is a chip. It's not storage." It's like a CPU, but specialized for **matrix multiplication**.
- An AI model turns your prompt into numbers (a **tokenizer**), multiplies them through layer after layer of numbers ("hundreds of millions of times"), and converts the result back into text. A GPU is good at AI because it does those multiplications extremely fast **in parallel**. The same reason makes GPUs good for graphics: a screen is a matrix of pixels whose color values must all be calculated quickly.
- A model *can* run on a CPU; a very light model might just take 20-30 minutes to answer.
- **VRAM** is RAM on the video card. It determines how large a model you can load and hold. For LLMs, "enough VRAM is enough VRAM"; for AI video generation, the more the better.
- **Why AWS makes you request GPU quota:** mainly to stop **crypto mining**, which would take capacity from AWS's main customers (corporations) and wears out GPUs. The quota request asks for your intended use, and crypto mining will be rejected.
- **Cost warning:** after getting a GPU quota increase, Evan kept getting charged for things he didn't want and ended up closing that account.

---

## EMR: Extra Points from Class

Teacher's definition: "Essentially what AWS EMR is, is a Hadoop cluster." (Hadoop's three parts: **HDFS, YARN, MapReduce**.) EMR adds a user interface and a serverless option on top.

- **Provisioning:** a ready-to-use cluster in about **10-20 minutes**, vs buying computers, networking them, setting up passwordless SSH (RSA keys) and installing Hadoop by hand.
- **Scaling:** EMR can scale up or down "pretty much at will." Scaling on-premises means adding or removing physical machines, which usually means shutting down.
- **EC2 instance = node.** Q (student): how do EC2 instances relate to nodes? A (Teacher): "An EC2 instance is a node, because a node is a computer, and an EC2 instance is a computer." Each node runs the Hadoop software (HDFS, MapReduce, YARN).
- **Not available in the web UI:** you can't use the cluster's services from the console. You get the primary node's address and SSH in with the cluster's **EC2 key pair**, the same authentication as EC2.

**Create-cluster page tour:**

| Setting | Notes from class |
|---|---|
| **Release / application bundle** | Modern bundles come with Spark installed. Evan saw Spark **4.0**, **JupyterEnterpriseGateway** and **Livy**, plus a **Spark Connect** endpoint. Old EMR clusters needed a startup (bootstrap) script to install Python and other tools |
| **Custom bundle** | Pick individual applications |
| **Instance types** | Node sizes from small (2 vCore, 1.7 GB) to very large (96-128 vCores) |
| **Cluster scaling** | Primary, core and task node groups; **EMR managed scaling** from a minimum (1 primary + 1 worker) up to many nodes |
| **Networking / security** | Same as EC2: VPC, subnet, security configuration, EC2 key pair |

**Accuracy note:** Evan said Presto seemed to be gone from the options ("nobody really uses it anymore"). Presto and its successor **Trino** are still offered in current EMR releases, under the custom application bundle. Trino in particular is widely used (Athena is built on it).

### Spark Connect (Spark 4.0)

Teacher's explanation: "Spark Connect basically is the big new feature in Spark 4." It's "just a client-server functionality to your Spark instance." A lightweight client (e.g. a laptop in Brazil) sends Spark commands to a powerful cluster somewhere else (e.g. in the US), which does the processing.

**Expanded:** before Spark Connect, the driver had to run near the cluster, and your code ran *inside* the driver. With Spark Connect, the client builds the DataFrame query plan and sends it over the network (gRPC) to a Spark server, which executes it and streams results back. The client is a thin library, so it works from notebooks, IDEs or small apps without a full Spark install.

| Spark version | Headline feature (per Evan) |
|---|---|
| Spark 2 | DataFrames (as the main API) |
| Spark 3 | Adaptive Query Execution (AQE) |
| Spark 4 | Spark Connect |

**Accuracy note:** Spark Connect was first released in **Spark 3.4** (2023) and became much more complete and prominent in Spark 4.0. DataFrames first appeared in Spark 1.3; Spark 2.0 unified DataFrames and Datasets and introduced `SparkSession`.

| Other client-server examples | Client | Server |
|---|---|---|
| Spark Connect | Laptop / notebook | Spark cluster |
| REST API | App making the request | API server processing it |
| Mobile app (student example) | Phone (client-side rendering) | Server (server-side rendering) |

---

## Serverless: Evan's Explanation

Teacher's explanation: "Saying that something is serverless is like saying it's computerless... You cannot run computer code without a computer." Student answer, confirmed as "absolutely right": you still have a server; you just don't manage it, the provider does.

- Data centers have huge numbers of computers, mostly connected in an **MPP** architecture. Thanks to these economies of scale, "a serverless service is a distributed application that runs across a large number of different computers," which allocates processing wherever it wants. You only see your code or data going in. "It's reducing infrastructure to being something more like a consumer application."
- **S3 is serverless:** no S3 server to provision or log into; you use it like a web application.
- **EMR is not serverless:** you provision a cluster and SSH into it.
- "Cloud services were originally basically just web-based versions of regular compute infrastructure. That's exactly what EC2 is. That's exactly what EMR is."
- **Serverless pricing trade-off:** a serverless service stops charging when it stops running. If it runs *all the time*, it quickly costs **more** than a provisioned instance left on. That's the business decision behind EMR vs Glue.

---

## AWS Lambda

Q. What is AWS Lambda?

A. (Teacher's definition) "The thing most people think of when they think serverless service is AWS Lambda."

**Expanded:** Lambda runs a single **function** in response to an **event**, with no server to manage. You're billed per request and per millisecond of run time, so tests cost "a fraction of a penny." Evan: "you would have to use Lambda quite a lot in order to spend a dollar on it," which makes it a cheap way to learn hands-on cloud work.

```python
import json

def lambda_handler(event, context):
    # event arrives as JSON (a Python dict); e.g. an S3 upload event
    bucket = event.get("bucket")
    key = event.get("key")
    ...
    return {"statusCode": 200, "body": json.dumps("done")}
```

| Lambda point from class | Details |
|---|---|
| **Handler** | Always `lambda_handler(event, context)` by default |
| **`event`** | A JSON object (handled as a Python dict) describing what triggered the function |
| **Console editor** | Write code in the browser with boilerplate provided. More advanced: build locally with dependencies and deploy |
| **Testing** | Test tab: create a test event with keys and values |
| **Flow** | Write → test → deploy → triggered by an event (another app calling it, or a schedule) |
| **Cold vs warm** | **Cold:** the function isn't in memory, so the first call is slower while it loads. **Warm ("hot"):** kept in memory for a while after a call, so later calls are faster. Unused functions are released from memory |
| **Not for monitoring** | Monitoring needs something always on and collecting data. Lambda is ephemeral: loaded, run, released |

**Evan's example pipeline (Lambda + EventBridge):** a few times a day, another company drops a 1,000-line CSV into your S3 bucket.

```
CSV lands in S3 (Bronze) ──event──▶ EventBridge ──▶ Lambda (imports Pandas)
                                                      │ reads the file, processes it
                                                      ▼
                                               S3 (Silver bucket)
```

He called this "fairly simplified." Lambda suits small data. Bigger data belongs in Glue (Spark), and Lambda has limits of **15 minutes** max run time and up to **10 GB** memory.

**What is an event?** "It's a JSON object with particular structure to it... It is a literal object that has data. It is a configuration, and it is sent from one place to another."

**Accuracy note:** Evan said "they may have set it up now where you don't need EventBridge... I've had interviewers get argumentative with me about whether you can actually fire an event when something just arrives." You can do both. **S3 Event Notifications** can trigger a Lambda function **directly** when an object is created (no EventBridge needed), and this has been possible for many years. Routing S3 events through **EventBridge** (once enabled on the bucket) adds filtering and many more target types. In an interview: "S3 can invoke Lambda directly through event notifications, or send events to EventBridge for more complex routing."

---

## AWS Glue: Extra Points from Class

- "A heavily modified version of Apache Spark, which is running as a serverless service."
- **The two central AWS processing services are EMR and Glue.** EMR runs regular Spark jobs with `spark-submit` and on-premises conventions ("a perfect clone... in a virtual computer"). Glue is "Amazon's own unique take on Spark."
- **Glue job code structure** (standard Glue boilerplate matching what Evan described in the `bank batch ETL` job; reconstructed from the audio, not read off the screen):

```python
import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext

sc = SparkContext()
glueContext = GlueContext(sc)          # GlueContext wraps a SparkContext
spark = glueContext.spark_session      # ...and gives back a normal SparkSession
job = Job(glueContext)

df = spark.read.option("header", "true").csv("s3://bucket/path/")   # regular Spark still works
```

- Evan noted the job was named "ETL" but the code (`spark.read`, many `withColumn` calls) "looks like ELT to me."
- **Visual editor (Glue Studio):** add **nodes**: a **source** (e.g. browse to an S3 bucket and choose a format), **transforms** (drop duplicates, drop null fields, filter) and a **target** (e.g. MongoDB), then set each node's options. Good for getting a visual understanding when starting out. In class the source failed with "failed to infer schema" on a random bucket.
- **Why serverless pricing beats EC2 for occasional data:** EC2-based compute is "charged by the amount of time that they are available for you to use... not based on how much you actually use them." Leave an instance on all night and you pay all night. Glue runs when triggered, returns the result, stops, and stops charging.

---

## Redshift: Extra Points from Class

- "You can think of Redshift as being the same kind of basic thing that Hive is, and sort of like Snowflake, except that Snowflake is a much more expansive platform." Redshift is "just simply a data warehouse," designed to store data in an analytical format using a **star schema** or **snowflake schema**.
- Provisioned Redshift clusters "insisted on an MPP architecture." In the console Evan only saw the **serverless dashboard**. Provisioned clusters still exist (see the Provisioned vs Serverless table above); the console just leads with Serverless now.

### MPP: Evan's Definition

Teacher's definition: "MPP stands for Massively Parallel Processing." A parallel cluster (like Hadoop) has a master node and worker nodes; "a massively parallel architecture is basically just one form factor beyond that, which is to connect multiple of those together for as big as you want to make the cluster... Eventually, you've got what is basically indistinguishable from a supercomputer." MPP is "the hardware architecture that drives the most powerful computers that we make today."

- **Why data warehouses use MPP:** not just for massive storage. *Querying* that much data needs massive compute. One node running a query over huge storage would take a very long time. MPP spreads the query processing across many nodes.
- Evan expects MPP to outlast even quantum computing: quantum chips would replace silicon chips *inside* an MPP architecture.
- A student's answer ("breaking tasks into smaller sub-tasks that run at the same time") was "regular distribution of data," not quite MPP. Evan's point is the **scale**: many clusters of nodes connected into one system.

### Why Redshift Went Serverless: BigQuery

- Redshift worked fine as a business "until Google Cloud Platform came on the market." **BigQuery** was GCP's flagship differentiator, started as an internal Google project, and was the first serverless data warehouse. Companies realized it beat "paying those ridiculous fees for something that you can never really turn off" and moved to it, so AWS made Redshift serverless too.
- **The big three clouds:** AWS, Azure, GCP. Oracle Cloud is "a distant fourth"; Apple is absent. Each has a cloud data warehouse. On AWS and GCP it's fully serverless; on Azure, **Databricks** offers a serverless SQL warehouse (Azure's own approach comes later in the course).

---

## RDS: Extra Points from Class

- **App server vs database server:** "As long as we have had applications that require access to data, there has basically been a system where one production machine runs the code and a different production machine is dedicated to storing the data." That's why database code creates a **connection** object, then a **cursor** to pass SQL into (as in the Python exercises): it assumes the database is a separate server.
- **Flight search engine example:** the app code runs on EC2, the code and dependencies live on EBS, and the constantly changing price data (plus history for a price-prediction ML model) lives in RDS, "a specialized database server that is there to be able to serve data quickly."
- RDS = "a fancy EC2 instance with some persistent stuff written into it," with a SQL distribution installed, storing data in an **OLTP** system for fast queries and responses.
- **Engines in the console:** Aurora (MySQL-compatible), Aurora (PostgreSQL-compatible), MySQL, PostgreSQL, MariaDB, Oracle, Microsoft SQL Server, **IBM Db2**. Which one depends "very much on the preferences of the team."

**Accuracy note:** Evan called Aurora "a clone of Postgres... optimized for speed and for running on AWS-specific hardware." Aurora is Amazon's own cloud-built relational engine, offered in **two compatible editions: MySQL and PostgreSQL**. Apps talk to it as if it were MySQL or Postgres, but the storage layer underneath is AWS's own (distributed, replicated six ways across three Availability Zones).

### OLTP vs OLAP (class Q&A)

Q (Evan): What is OLTP? A (student, accepted): transactional processing: fast, real-time transactions, like a store register. Evan: "Most businesses most of the time in customer-facing applications are using OLTP databases. Every single database you see here [in RDS] is an OLTP database."

Q (student): Is there any current use case for OLAP? A (Teacher): "Redshift. Redshift is an OLAP... data warehouse. BigQuery is also OLAP. Anything else that's a data warehouse is OLAP. So Delta Lake is OLAP. Snowflake is OLAP." OLAP use cases all involve **analytics**, not serving an application. An OLAP database behind a flight search site would make queries slow and drive customers away.

---

## DynamoDB

Q. What is DynamoDB?

A. (Teacher's definition) "DynamoDB is a serverless NoSQL database."

**Expanded:** DynamoDB is AWS's fully managed, serverless **key-value and document** database. Tables need a **partition key** (and optionally a sort key) but no fixed schema for the other attributes, so each item can have different fields. It delivers consistent single-digit-millisecond reads and writes at almost any scale, which suits customer-facing apps (shopping carts, sessions, user profiles, gaming leaderboards). Evan: "as far as I know, DynamoDB is the fastest of the cloud databases." He also pointed out that the training account has a lot of data in DynamoDB "because it's cheap to keep it there."

| Concept | What it is |
|---|---|
| **Table / item / attribute** | Like table / row / column, but items in the same table can have different attributes |
| **Partition key** | Required; decides which partition stores the item, so lookups by key are very fast |
| **Sort key** | Optional; orders items that share a partition key (e.g. all orders for one customer by date) |
| **Global Secondary Index (GSI)** | An alternate key to query by (different partition/sort key). Covered in Training 13 |
| **Local Secondary Index (LSI)** | Same partition key, different sort key |
| **Capacity modes** | On-demand (pay per request) or provisioned (set read/write capacity) |

| | RDS (relational) | DynamoDB (NoSQL) |
|---|---|---|
| Data model | Tables with a fixed schema, joins | Key-value / documents, flexible attributes, no joins |
| Query language | SQL | API calls by key (plus PartiQL, a SQL-like option) |
| Servers | Managed instance you size | Serverless |
| Scales by | Bigger instance + read replicas | Automatically, horizontally |
| Best for | Complex queries and relationships | Very fast lookups by key at huge scale |

**Accuracy notes:**
- Evan described DynamoDB as a "column family" database where "columns are all actually stored independently." DynamoDB is a **key-value / document** store. Items are stored together by partition key, not column by column. Column-family databases are **Cassandra** and **HBase**. (The console's grid view just *looks* like columns.)
- Evan said "in a regular SQL database, you can have one index per table." SQL databases can have **many indexes per table**. What's limited to one is the **clustered** index (the physical order of the rows, e.g. the primary key in MySQL or SQL Server). DynamoDB allows up to **20 GSIs** (default quota) and **5 LSIs** per table.
- Evan saw a **vector indexes** tab in the console. Vector indexes store AI embeddings for similarity search. Check the current DynamoDB documentation for how they work before relying on this, since it's newer than the rest of these notes.

---

## Athena: Extra Points from Class

- "Athena is basically an example of a piece of software which is not a full database, but it is a **query engine**." It doesn't store data; it queries data stored elsewhere using schema on read. "Athena costs almost nothing."
- **Live demo problem:** the `DESCRIBE TABLE` queries wouldn't run, and the console asked for a **query result output location**. Evan thought he'd need to enable **Athena managed query results** in the **workgroup** settings.

**Expanded on the demo error:** every Athena query writes its results to a location. Traditionally that's an **S3 bucket** you set in the workgroup or console settings (e.g. `s3://my-athena-results/`). Newer accounts can instead turn on **managed query results**, where Athena stores results for you. Until one is set, queries won't run. That's a first-time setup step, not a bug.

- **The databases listed in Athena aren't Athena's.** They're there because their schemas are in the **Glue Data Catalog**. "It is [their] presence in the Glue Data Catalog which makes it so that you can select it as a database."
- **Glue Crawler and schema evolution (advanced):** "The Glue Crawler can crawl each incremental piece of data that comes into your AWS system, and it can look to see if the schema has changed, and if the schema has changed, then it can change the processing downstream."
- **Common student mistake:** "they'll remember what the Glue Crawler is, but they won't remember what the Glue Data Catalog is... the Glue Data Catalog is what stores your schema over the long term. The Glue Crawler is what gets your schema in the moment."

---

## Putting It Together: AWS Data Pipelines (Evan's Wrap-Up)

**Classic AWS ETL pipeline:**

```
Data lands in S3 ──▶ EMR cluster processes it ──▶ Redshift
```

**Modern serverless lakehouse pipeline:**

```
S3 Bronze bucket ──Glue (serverless ELT)──▶ S3 Silver bucket ──Glue──▶ Gold layer
                                                                      (S3 bucket, or Redshift Serverless)
```

Then, depending on who needs the data:

| Consumer | AWS service |
|---|---|
| Quick ad-hoc analysis of a subset | **Athena** (schema from the Glue Data Catalog) |
| Analytics / BI dashboards | **Redshift (Serverless)** |
| Serving data to an application | **RDS** (relational) or **DynamoDB** (NoSQL) |
| The application itself | **EC2** (compute) + **EBS** (code, dependencies), reading from RDS |

Evan's goal: by interview time, be able to "talk fluently about building out cloud architectures" using exactly this vocabulary.

---

## Homework and Account Access

- **Homework:** a review/research assignment on today's vocabulary, so you can talk about these services fluently in job interviews. **No infrastructure needs to be provisioned on AWS.**
- **AWS access:** students don't have access to the company AWS account yet; Evan was following up with Ian. If company access isn't possible, the next homework may be to **create a personal AWS account** (free tier available, but a credit card is required). Evan wants to avoid that unless necessary.
- Evan's AWS CLI is tied to his personal account, so command-line demos with the company account are on hold until he gets credentials.
