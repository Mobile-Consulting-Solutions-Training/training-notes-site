---
title: "Walkthrough - Training 18: AWS Cloud Fundamentals"
description: "Every core AWS service introduced as the answer to a problem in one running story, with a self-check."
sidebar:
  order: 180
---

Source material: [Training 18 notes](/training-notes-site/notes/training-18/).

**How to use this:** read it top to bottom once. Each AWS service shows up as the *answer to a problem* in one running story, instead of as a list of definitions. Then do the self-check at the end without looking back. If an answer doesn't come, reread just that step.

---

## The one-paragraph version

A company has data files arriving. It needs somewhere to **keep** them (S3), someone to decide **who's allowed** to touch them (IAM), something to **clean** them with Spark (EMR if the work never stops, Glue if it's occasional), a way to **start** that cleaning automatically when a file arrives (EventBridge), and a way for analysts to **ask questions in SQL** (Athena for files, Redshift for a real warehouse). Apps that serve customers keep their data in **RDS** or **DynamoDB**. Everything else in today's class is detail on those pieces.

---

## You already know most of this

Almost every AWS service today is something you've already used on your laptop, but rented and managed by Amazon. Keep this table in mind; it's the biggest shortcut in the whole class.

| You used this before | Class | AWS version | What changes |
|---|---|---|---|
| Your laptop / a VM | Training 1 | **EC2** | It runs in Amazon's data center; you rent it by the hour |
| Your laptop's hard drive | — | **EBS** | A virtual disk you plug into an EC2 instance |
| HDFS (where Hadoop keeps files) | Training 7 | **S3** | Not a file system; a giant bucket of objects reached over the internet |
| Your Hadoop/Spark cluster | Training 7–9 | **EMR** | Amazon builds the cluster out of EC2 instances in ~15 minutes |
| `spark-submit` a job | Training 8–9 | **Glue** | Same Spark, but no cluster at all; you just hand over the script |
| Hive Metastore (table schemas) | Training 8 | **Glue Data Catalog** | Same idea, managed by AWS |
| Hive (SQL over files) | Training 8 | **Athena** | Same idea: SQL over files, no database underneath |
| Snowflake (a warehouse) | Training 16–17 | **Redshift** | AWS's own data warehouse |
| Postgres in Docker | Training 5 | **RDS** | Amazon runs the Postgres server for you |
| MongoDB (NoSQL) | Training 14 | **DynamoDB** | AWS's own NoSQL database |
| Kafka | Training 13 | **Kinesis** | AWS's managed streaming service (only mentioned today) |
| A cron job that runs a script | Training 1 | **EventBridge + Lambda** | Triggered by events (a file arriving), not just by time |

If you get lost later, come back here and ask "which thing I already know is this the AWS version of?"

---

## The story: ShopCo's sales files

ShopCo sells products online. Every evening its point-of-sale system drops a CSV of the day's sales. Management wants three things:

1. **Keep every file forever** (auditors may ask).
2. **Clean the data** (duplicates, bad dates, wrong types) with Spark.
3. **Let analysts query it with SQL.**

We'll build ShopCo's platform one problem at a time.

---

## Step 1: "Where in the world does this run?" → Regions

**Problem:** AWS has data centers all over the world. Which one do you use?

**Answer: a Region**, a geographic area with several data centers. Examples: `us-east-1` (N. Virginia), `us-east-2` (Ohio), `eu-central-1` (Frankfurt), `sa-east-1` (São Paulo).

**How you pick:**
- **Closest to your customers:** less distance, faster responses.
- **Laws:** EU customer data often must stay in the EU.
- **Price and services:** both vary by Region.

**The thing Evan stressed:** your resources *physically live* in that Region. Switching Regions isn't a setting you flip; it's moving everything (a migration). One AWS account can use any Region, though, so you don't need a new account when you move countries.

ShopCo is in the US, so it picks `us-east-1`.

---

## Step 2: "Who is allowed to do what?" → IAM

**Problem:** many people and programs will touch ShopCo's data. The intern shouldn't be able to delete the raw files, and the cleaning job shouldn't be able to read the HR database.

**Answer: IAM (Identity and Access Management)**, the permission system for the whole AWS account.

Think of an office building:

| IAM piece | Office analogy | What it actually is |
|---|---|---|
| **User** | An employee with an ID badge | A person (or app) with permanent login credentials |
| **Group** | A department ("Data Engineers") | A set of users who share the same permissions |
| **Policy** | The rulebook listing which doors a badge opens | A JSON document: "allow `s3:GetObject` on bucket X" |
| **Role** | A **visitor badge** you check out, use, and hand back | Permissions with no owner; whoever **assumes** it gets temporary access |

**Policies are the actual permissions.** Users, groups and roles are just *who* the policies get attached to.

**Why roles matter in data engineering:** programs use roles, not users. ShopCo's Glue job will **assume** a role whose policy says "read the Bronze bucket, write the Silver bucket." No passwords are stored in the code.

**Evan's version:** "a role is a packet of policies." That's a fine mental model, but in an interview say a role is **assumed** to get **temporary credentials**.

**Least privilege:** give each identity only what it needs. Evan's example: data engineers get Redshift, web engineers get the web server, and neither gets the other's.

What a policy looks like (you don't need to memorize it, just recognize it):

```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject"],
  "Resource": "arn:aws:s3:::shopco-bronze/*"
}
```

Read it as: *allow* reading objects in the `shopco-bronze` bucket.

---

## Step 3: "Where do the files live?" → S3

**Problem:** ShopCo needs somewhere to keep every CSV forever, cheaply, that every other service can read.

**Answer: S3 (Simple Storage Service)**, AWS's **object storage**.

**What "object storage" means:** S3 isn't a hard drive or a folder tree. It's a gigantic coat check:
- You hand over a file (the **object**) and get a ticket (its **key**, e.g. `sales/2026-10-06.csv`).
- Coats are grouped into separate cloakrooms (**buckets**).
- You can't "open" a file inside S3 and edit one line. You upload a whole new version.
- Anything with permission can reach it over the internet (HTTP), from anywhere.

| Term | Meaning |
|---|---|
| **Bucket** | The container; the discrete unit of S3 (Evan's quiz answer). Globally unique name, lives in one Region |
| **Object** | One file plus its metadata |
| **Key** | The object's full name, e.g. `sales/2026/10/06.csv`. The "folders" are fake, just part of the name |
| **Glacier** | A cheaper S3 tier for data you rarely read; slow to get back |

**Why it's the center of everything:** S3 accepts any file in any format, without forcing a structure first. That's what made data lakes possible, and today's lakehouses still sit on it.

### Medallion architecture with three buckets

You saw Bronze/Silver/Gold in Training 6 and 8 (Hive). On AWS, Evan's rule is **one bucket per layer**:

```
shopco-bronze          shopco-silver               shopco-gold
raw CSVs, exactly  ─▶  cleaned, deduped,       ─▶  business-ready:
as they arrived        correct types, Parquet      daily sales by region,
(never edited)                                     top products...
```

**Why separate buckets:** permissions are simple ("ingestion can only write Bronze; analysts can only read Gold"), a mistake in one layer can't wipe another, and you can set rules per layer (e.g. move Bronze files older than 90 days to Glacier).

ShopCo now has requirement 1 covered: the raw files sit in `shopco-bronze` permanently.

---

## Step 4: "I need an actual computer" → EC2, EBS, VPC

Not every job needs this, but you need to know the basic building blocks because everything else is built on them.

### EC2 = a rented computer

**EC2 (Elastic Compute Cloud)** is a virtual machine in Amazon's data center. Evan: "just a computer that is on their system." When you launch one you pick:
- **AMI:** the operating system (Amazon Linux, Ubuntu...)
- **Instance type:** how big. `t3.micro` = 2 vCPUs, 1 GB RAM (free tier); large types go to hundreds of vCPUs
- **Key pair:** the SSH key you log in with (exactly like `ssh jackserver`)
- **Network and storage:** next two sections

Servers have **no desktop**, only the command line. That's why the course started with Linux.

### EBS = its hard drive

**Problem:** compute and storage are separate in the cloud. Where does the instance keep its OS, code and data?

**Answer: EBS (Elastic Block Store)**, a virtual hard drive you attach to an EC2 instance. Evan: "The EBS volume is the storage. The EC2 instance is the compute." Like a USB drive: you can unplug it from one instance and plug it into another.

**The S3 vs EBS question (it's on the homework):**

| | EBS | S3 |
|---|---|---|
| Is like | The hard drive inside your laptop | A shared online drive (Dropbox-ish) |
| Attached to | **One** EC2 instance | Nothing; anyone with permission reaches it over the network |
| Good for | The OS, installed apps, a database's files | Data files, data lakes, backups, sharing between services |
| Can it run an OS or database? | Yes | No |
| Cost | Higher per GB | Much cheaper per GB |

**Correction to class:** Evan said EC2 is ephemeral and everything is gone at shutdown. Today most instances boot from EBS, so a **stop** keeps the data. What's lost is the instance's temporary local disk (the instance store), and the root disk when you **terminate** (delete) the instance.

### VPC = the private network around it

**VPC (Virtual Private Cloud)** is your own private, fenced-off network inside AWS. You decide which machines can be reached from the internet (a web server) and which can't (a database in a private subnet that only the app servers can talk to).

Evan compared it to a VPN. Close: a **VPC is the private network**; a **VPN is an encrypted tunnel into a network**. Companies often use a VPN to connect their office to their VPC.

### Why GPUs need special permission

New accounts get **zero quota** for GPU instances, so you have to ask AWS and say what it's for. The main reasons are that GPUs are scarce and expensive, AWS wants to block crypto mining, and it stops beginners from accidentally running up huge bills. (A GPU is a chip specialized in matrix multiplication, the math behind AI and graphics.)

---

## Step 5: "I need *lots* of computers running Spark" → EMR

**Problem:** cleaning ShopCo's data needs Spark. In Training 7–9 you saw what a Hadoop cluster takes: several machines, networking, passwordless SSH, installing Hadoop, HDFS and YARN...

**Answer: EMR (Elastic MapReduce)**. Evan: "Essentially what AWS EMR is, is a Hadoop cluster." You fill in a form, and **10–20 minutes** later you have a working cluster with Spark installed.

**Key fact for interviews:** an EMR cluster is **made of EC2 instances**. Each node is an EC2 instance ("a node is a computer, and an EC2 instance is a computer"):

```
EMR cluster
├── Primary node (EC2)  ← you SSH in here, like the master/NameNode
├── Core node (EC2)     ← runs tasks + stores HDFS data
├── Core node (EC2)
└── Task node (EC2)     ← optional extra compute only
```

**The catch:** a cluster bills for **every minute it's on**, busy or idle. If ShopCo's file arrives once a night and takes 15 minutes, an always-on EMR cluster sits idle (and bills) for the other 23¾ hours.

**When EMR is right:** work that keeps the cluster busy all day. Examples: a constant stream of data, huge batch jobs every few hours, or a team moving its existing Hadoop/Spark jobs to the cloud and wanting full control over the cluster.

---

## Step 6: "I don't want to babysit computers" → serverless (Glue, Lambda, EventBridge)

### What "serverless" really means

Evan: calling something serverless is like calling it "computerless." Code can't run without a computer. **Serverless means there *are* servers, but AWS runs them and you never see them.** You hand over code or data and it just runs.

**The money rule (this explains half the class):**

```
Provisioned (EC2, EMR, provisioned Redshift):  you pay while it's ON, busy or idle
Serverless (Lambda, Glue, Athena, Redshift Serverless, S3): you pay only while it's WORKING
```

So:
- **Work happens occasionally** → serverless is cheaper (no idle bill).
- **Work never stops** → provisioned is usually cheaper (serverless costs more per unit of work).

### Glue = Spark without a cluster

**AWS Glue** runs your Spark script serverlessly. Evan: "a heavily modified version of Apache Spark, running as a serverless service." No cluster to create, size or shut down.

Instead of choosing nodes, you choose **DPUs (Data Processing Units)**:
- **1 DPU = 4 vCPUs + 16 GB RAM**, a "pretend node."
- You're billed **DPUs × minutes the job runs** (DPU-hours, billed per second).
- 10 DPUs for 6 minutes = 1 DPU-hour. Nothing running = $0.

| | EMR | Glue |
|---|---|---|
| You manage | The cluster (EC2 nodes) | Nothing; just the script |
| You size it in | Instance types × node count | DPUs (workers) |
| Bills while idle? | **Yes** | **No** |
| Cheaper per unit of work? | Yes | No (you pay for convenience) |
| Pick it when | Compute is busy **all the time** | Data arrives **occasionally** |

**Homework Workload A/B:** continuous data all day → **EMR**. One nightly file, 15 minutes of Spark → **Glue**.

A Glue script looks like the Spark you know, plus a little wrapper:

```python
from awsglue.context import GlueContext
from pyspark.context import SparkContext

glueContext = GlueContext(SparkContext())   # Glue's wrapper
spark = glueContext.spark_session           # a normal SparkSession

df = spark.read.option("header", "true").csv("s3://shopco-bronze/sales/")
# ...the same withColumn / filter / dropDuplicates you already wrote in Training 8-9...
df.write.mode("overwrite").parquet("s3://shopco-silver/sales/")
```

Glue also has **Glue Studio**, a drag-and-drop editor (source → transforms → target) that writes the script for you.

### Lambda = one small function

**Lambda** runs a single function when something happens. It's the most "classic" serverless service and costs fractions of a cent per run.

```python
def lambda_handler(event, context):   # always this name by default
    # event = a JSON dict describing what triggered it (e.g. which file arrived)
    ...
```

**Limits:** 15 minutes max and up to 10 GB of memory, so it's for **small** files (e.g. Pandas on a 1,000-line CSV). Big data → Glue.

**Cold vs warm:** the first call loads the function into memory (a slower **cold start**). For a while after that it stays loaded (**warm**) and responds faster.

### EventBridge = the doorbell

**Problem:** who notices that ShopCo's file arrived and starts the job?

**Answer: EventBridge**, an event router. Something happens (an "Object Created" event in S3), a **rule** matches it ("bucket = shopco-bronze, prefix = sales/"), and it starts a **target** (the Glue job, or a Lambda).

```
CSV lands in shopco-bronze ──event──▶ EventBridge rule ──▶ starts Glue job
```

It's like the cron job from Training 1, but triggered by *something happening* instead of only by the clock. (It can do schedules too.)

**Interview gotcha from class:** S3 can also trigger Lambda **directly** (S3 Event Notifications) without EventBridge. Both are valid. EventBridge adds filtering and many more targets.

ShopCo now has requirement 2 covered: the file arrives → EventBridge → Glue cleans it → Parquet lands in `shopco-silver`.

---

## Step 7: "Analysts want SQL on those files" → Crawler, Data Catalog, Athena

This is the part Evan said students mix up most. Go slow here.

### The key idea: schema-on-read

A Parquet or CSV file in S3 is just bytes. To query it with SQL, something has to know *"this file has columns `order_id INT, amount DECIMAL...`, it's CSV, and it lives at this S3 path."*

- **Schema-on-write** (Postgres, Training 5): data must fit the table *before* it goes in.
- **Schema-on-read** (Hive, Training 8; Athena): files go in as-is, and the table structure is applied **when you query**.

You already did this in Hive: `CREATE EXTERNAL TABLE ... LOCATION '/path'`. The files stayed put; Hive just remembered how to read them.

### The three pieces (and the one-line job of each)

| Piece | One-line job | Stores data? | Hive equivalent |
|---|---|---|---|
| **Glue Crawler** | **Figures out** the schema by scanning the files | No, nothing | You writing `CREATE TABLE` by hand |
| **Glue Data Catalog** | **Remembers** the schema long-term | Only metadata (no data) | **Hive Metastore** |
| **Athena** | **Runs SQL** against the files using that schema | No; data stays in S3 | Hive / HiveQL |

Evan's memory trick: **"The Glue Crawler is what gets your schema in the moment. The Glue Data Catalog is what stores your schema over the long term."**

### Follow one file through

```
1. orders.csv lands at s3://company-bronze/orders/orders.csv
        │
2. Glue Crawler scans s3://company-bronze/orders/
        │   "CSV with header; columns order_id INT, customer_id INT, order_date DATE, amount DOUBLE"
        ▼
3. Glue Data Catalog now has a table: bronze.orders → (columns, CSV, location s3://company-bronze/orders/)
        │
4. Analyst in Athena:  SELECT customer_id, SUM(amount) FROM bronze.orders GROUP BY customer_id;
        │   Athena asks the Catalog how to read it, reads the CSV straight from S3, returns the result
        ▼
   Results (Athena also writes a copy of the results to an S3 output location)
```

**Two things that trip people up:**
- The databases you see in Athena aren't "Athena's." They show up **because they're in the Glue Data Catalog**.
- Athena charges per **amount of data scanned**, so Parquet and date partitions (which let it skip files) make queries cheaper.

ShopCo now has requirement 3: analysts query `silver.sales` and `gold.daily_sales` in Athena.

---

## Step 8: "We need a real warehouse for heavy dashboards" → Redshift

Athena is great for occasional questions. If ShopCo's BI team runs big dashboards all day, they want a proper **data warehouse**.

**Redshift** is AWS's data warehouse, the AWS counterpart of Snowflake (Training 16–17). It's **OLAP** (analytics), uses star/snowflake schemas, and runs SQL.

### MPP: why warehouses are fast

**MPP (Massively Parallel Processing):** the data is split across many nodes, each with its own CPU, memory and disk. A query is cut into pieces that all run **at the same time**, then a leader node combines the results.

Analogy: counting the words in a 1,000-page book alone takes all day. Give 100 people 10 pages each and it takes minutes. Evan's point is that MPP is that idea at huge scale: many clusters of nodes wired together until it's "basically indistinguishable from a supercomputer."

### COPY: how data gets in

Never `INSERT` big data row by row. Use **`COPY`**, which loads files from S3 **in parallel** across all nodes:

```sql
COPY gold.daily_sales
FROM 's3://shopco-gold/daily_sales/'
IAM_ROLE '<redshift-role-arn>'
FORMAT AS PARQUET;
```

Same idea as Snowflake's `COPY INTO` from a stage.

### Provisioned vs Serverless (same money rule as Step 6)

| | Provisioned Redshift | Redshift Serverless |
|---|---|---|
| Setup | Pick nodes, wait ~30 min | Ready almost immediately |
| Pay for compute | Every hour it's up, idle or not | Only while queries run (RPUs) |
| Best for | Constant heavy use | Spiky or occasional use |

**Why Redshift went serverless:** Google's **BigQuery** was the first serverless data warehouse, and companies liked not paying for something "you can never really turn off." AWS answered with Redshift Serverless. **What they have in common:** no cluster to manage, storage and compute billed separately, automatic scaling, columnar storage with MPP underneath, standard SQL, and both can query files in object storage.

---

## Step 9: "Our website needs a database" → RDS (and DynamoDB)

This is a different world from Steps 5–8. It's the **app** side, not analytics.

**OLTP vs OLAP:**

| | OLTP (transactions) | OLAP (analytics) |
|---|---|---|
| Example | A store register, the checkout button | "Total sales by region last quarter" |
| Query shape | Tiny, fast, many per second | Huge scans, a few at a time |
| AWS service | **RDS**, **DynamoDB** | **Redshift**, **Athena** |

### RDS = someone else runs your Postgres

**RDS (Relational Database Service):** you pick an engine and AWS runs the database server: backups, patching, failover and replicas. Evan: underneath, "RDS is just an EC2 instance" with a database installed and managed for you.

**Engines:** PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, IBM Db2, and **Aurora** (Amazon's own engine, in MySQL- and PostgreSQL-compatible editions).

**Why the app doesn't keep data on its own EC2 instance:** apps have always had one machine for code and another for data. That's why your Python code in class opened a **connection** and a **cursor**: the database is a separate server. If the app server dies or you add five more app servers, the data is safe and shared. Evan's flight-search example:

```
Users ──▶ EC2 (the app's code)  +  EBS (its disk: code, dependencies)
                 │
                 ▼
               RDS  (prices, bookings: fast OLTP database)
```

### DynamoDB = AWS's NoSQL

**DynamoDB:** serverless NoSQL, **key-value/document**, very fast lookups by key at any scale (shopping carts, sessions). Like MongoDB from Training 14. (Evan called it column-family; it isn't. That's Cassandra and HBase.)

---

## Step 10: AI and GPUs → SageMaker

**SageMaker** (now "SageMaker AI") is AWS's managed **machine learning** platform: notebooks, **training** models, and **deploying** them to answer predictions. GPUs make the training and serving fast.

**Glue vs SageMaker:** Glue *prepares data* (ETL), and its output is clean tables. SageMaker *learns from data* (ML), and its output is a model. They're often used together: Glue cleans the data in S3, then SageMaker trains on it.

Evan's angle: SageMaker may be the easiest way to get GPU compute without an EC2 GPU quota request.

---

## The whole picture

```
                          IAM: roles + policies on every arrow below
                          VPC: private network around anything with a server

Source files ─▶ S3 Bronze ─event─▶ EventBridge ─▶ Glue (Spark) ─▶ S3 Silver ─▶ Glue ─▶ S3 Gold
                (kept forever;                    or EMR if the                                │
                 old → Glacier)                   work never stops                              │
                                                                                                │
                Glue Crawler ─▶ Glue Data Catalog ─▶ Athena  (ad-hoc SQL on files)   ◀─────────┤
                                                                                                │
                                                     Redshift  (heavy BI, loaded with COPY) ◀───┘

App side:   Users ─▶ EC2 + EBS (app) ─▶ RDS / DynamoDB (OLTP)
ML side:    S3 data ─▶ SageMaker (train + deploy models on GPUs)
```

Evan's two pipeline shapes:
- **Classic:** S3 → **EMR** → **Redshift**
- **Modern serverless lakehouse:** S3 Bronze → **Glue** → S3 Silver → **Glue** → Gold (S3 or Redshift Serverless) → **Athena**/Redshift

---

## Pairs people mix up

| These two... | ...differ like this |
|---|---|
| **Bucket vs object** | The cloakroom vs one coat. Bucket = container (the "discrete unit"); object = a file in it |
| **User vs role** | Your permanent badge vs a visitor badge you check out (temporary credentials) |
| **Policy vs role** | The rulebook (the permissions) vs who carries the rulebook |
| **EBS vs S3** | A disk plugged into one machine vs shared storage reached over the network |
| **EBS vs EFS** | One machine's disk vs a shared network folder many machines mount at once |
| **VPC vs VPN** | The private network vs an encrypted tunnel into a network |
| **EMR vs Glue** | Your own Spark cluster (pay while on) vs Spark with no cluster (pay while running) |
| **Lambda vs Glue** | A small function (15-minute limit, small data) vs Spark jobs for big data |
| **Crawler vs Data Catalog** | Figures out the schema (now) vs stores the schema (long-term) |
| **Athena vs Redshift** | SQL directly on S3 files, no storage vs a real warehouse that holds the data |
| **RDS vs Redshift** | OLTP for apps vs OLAP for analytics |
| **RDS vs DynamoDB** | Relational SQL with joins vs NoSQL key lookups, serverless |
| **Provisioned vs serverless** | Pay while on vs pay while working |

---

## Self-check

Answer out loud first, then open the answer.

<details><summary>1. Name the service: "SQL over files in S3 without loading them anywhere."</summary>

**Athena.** It uses schemas from the Glue Data Catalog and stores nothing itself.
</details>

<details><summary>2. A job runs 20 minutes every night. EMR or Glue, and why?</summary>

**Glue.** An always-on EMR cluster would bill for the ~23 idle hours; Glue bills only for the 20 minutes.
</details>

<details><summary>3. What is an EMR cluster made of?</summary>

**EC2 instances.** Each node is one EC2 instance (one primary, core nodes, optional task nodes).
</details>

<details><summary>4. What does 1 DPU equal?</summary>

**4 vCPUs + 16 GB RAM.** Glue bills DPUs × run time (DPU-hours).
</details>

<details><summary>5. Where is a table's schema stored for Athena? What created it?</summary>

**Stored** in the Glue Data Catalog. **Created** by a Glue Crawler (or a `CREATE EXTERNAL TABLE` in Athena).
</details>

<details><summary>6. What's the Hive equivalent of the Glue Data Catalog? Of S3? Of Athena?</summary>

Hive Metastore; HDFS; Hive itself (the SQL engine).
</details>

<details><summary>7. Why does Redshift load data with COPY instead of INSERT?</summary>

`COPY` loads many S3 files **in parallel** across every node (MPP), so it's far faster than row-by-row inserts.
</details>

<details><summary>8. A file lands in S3 and processing should start automatically. Which service notices it?</summary>

**EventBridge** (a rule matching the S3 "Object Created" event). S3 Event Notifications can also invoke Lambda directly.
</details>

<details><summary>9. The app server is replaced every week. Why keep its data in RDS?</summary>

The data lives on a separate, managed database server, so it survives the app server being replaced, can be shared by several app servers, and gets automatic backups and failover.
</details>

<details><summary>10. Your Glue job needs to read the Bronze bucket. How does it get permission without a password in the code?</summary>

It **assumes an IAM role** whose policy allows `s3:GetObject` on the Bronze bucket and gets temporary credentials.
</details>

<details><summary>11. What's the one money rule behind EMR vs Glue and provisioned vs serverless Redshift?</summary>

Provisioned bills while it's **on**; serverless bills while it's **working**. Always busy → provisioned. Occasional → serverless.
</details>

<details><summary>12. What is "the discrete unit" of S3 according to Evan?</summary>

The **bucket**.
</details>

---

## If an interviewer says "walk me through a data pipeline on AWS"

> "Raw files land in an S3 Bronze bucket. An EventBridge rule picks up the object-created event and starts a Glue job, which is serverless Spark. It cleans and dedupes the data and writes partitioned Parquet to a Silver bucket, then aggregates into Gold. A Glue Crawler registers the tables in the Glue Data Catalog, so analysts can query them in Athena, or for heavy BI we `COPY` Gold into Redshift Serverless. Each job runs under an IAM role with least-privilege access to only the buckets it needs. If the workload were constant instead of occasional, I'd run the Spark on EMR instead of Glue, since a busy cluster is cheaper than serverless."
