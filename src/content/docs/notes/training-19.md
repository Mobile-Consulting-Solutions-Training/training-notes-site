---
title: "Training 19 - AWS Batch Pipelines"
description: "Batch pipelines on AWS: EMR Serverless, a Streamlit app on ECS/Fargate, QuickSight, and Citi Bike GBFS ingestion to S3 Bronze."
sidebar:
  order: 19
---

Teacher: Evan Flint

Syllabus Day 20 (per file numbering; Oct 7) - topic: AWS batch pipelines (S3 + EMR Serverless); more filled in as class goes. The class has been running about one day ahead of the syllabus, so today continues the AWS material (`Course Roadmap.md` lists EC2 + Lambda for Day 21, AWS Glue for Day 22, and EMR for Day 23).

---

# Batch Pipelines on AWS

Q. What does a batch pipeline look like on AWS?

A. (Teacher's definition) Batch pipeline: ingest into S3. Process it with a Spark job on EMR Serverless. Output to a Data Warehouse on Redshift Serverless. Streamlit app for visualization hosted on ECS/Fargate.

**Expanded:** A **batch** pipeline processes data in chunks on a schedule or when a file arrives (e.g. last night's sales), as opposed to **streaming**, which processes each event as it happens (Kafka/Kinesis, Training 13–15). On AWS the standard batch shape has four steps:

1. **Ingest into S3.** Raw files land in a Bronze bucket (uploaded by a source system, copied by a script, delivered by another service). S3 is the landing zone because it's cheap, durable and readable by every other AWS service.
2. **Process with Spark on EMR Serverless.** A Spark job reads the raw files from S3, cleans and transforms them, and writes the results back to S3 (Silver/Gold), usually as Parquet.
3. **Output to a data warehouse on Redshift Serverless.** The cleaned, modeled data (fact and dimension tables) is loaded into Redshift, where analysts and BI dashboards query it with SQL.
4. **Visualize with a Streamlit app hosted on ECS/Fargate.** A small Python web app queries Redshift and shows charts and tables to business users in a browser.

Every step is **serverless**, so you never manage a server. Steps 1–3 bill nothing between nightly runs except storage; the Streamlit app is the exception, since a website has to stay up (see below). This is the "modern" version of Evan's classic pipeline from Training 18 (S3 → EMR cluster → provisioned Redshift).

```
Source system ──▶ S3 (Bronze, raw files) ──▶ Spark job on EMR Serverless ──▶ S3 (Silver/Gold, Parquet)
                                                                               │
                                                                    COPY       ▼
                                                     Redshift Serverless (data warehouse) ──▶ Streamlit app on ECS/Fargate (dashboards)
```

| Step | AWS service | What happens | Bills while idle? |
|---|---|---|---|
| Ingest | **S3** | Raw data lands as files, unchanged | Storage only |
| Trigger (optional) | **EventBridge** or a schedule | Starts the job when a file arrives or at a set time | No |
| Process | **EMR Serverless** (Spark) | Read from S3 → transform → write back to S3 | No |
| Load | **Redshift `COPY`** | Bulk-loads the processed Parquet from S3 into warehouse tables | — |
| Warehouse | **Redshift Serverless** | Star-schema tables; analysts run SQL, BI tools connect | Storage only (compute in RPUs only while queries run) |
| Visualize | **Streamlit on ECS/Fargate** | Web dashboard that queries Redshift | **Yes**: the container runs (and bills) while the site is up |

### Getting the Spark output into Redshift

| Option | How | When |
|---|---|---|
| **Spark writes Parquet to S3, then `COPY`** (most common) | The job writes to `s3://company-gold/...`; a `COPY` command (run by a scheduler, Step Functions, or the Redshift Data API) loads it | Default choice: fast parallel load, and the files in S3 double as a backup and an Athena-queryable copy |
| **Spark writes straight to Redshift** | The Spark-Redshift connector (`df.write.format("io.github.spark_redshift_community.spark.redshift")`). Under the hood it stages files in S3 and runs `COPY` for you | Fewer steps in the pipeline; needs the connector JAR and a temp S3 dir |
| **Don't load; query in place** | **Redshift Spectrum** external tables over the S3 Parquet (schemas from the Glue Data Catalog) | Huge or rarely queried data you don't want to copy |

```sql
-- Load the night's output into the warehouse
COPY analytics.fact_sales
FROM 's3://company-gold/fact_sales/sale_date=2026-10-07/'
IAM_ROLE '<redshift-role-arn>'
FORMAT AS PARQUET;
```

**Why a warehouse at the end instead of just Athena:** Athena is pay-per-scan and great for occasional questions. When dashboards hit the same tables all day, a warehouse (data stored in Redshift's own optimized columnar format, with caching, sort keys and concurrency handling) is faster and more predictable. Redshift **Serverless** keeps the same pay-while-working idea as the rest of the pipeline.

---

## EMR Serverless

Q. What is EMR Serverless?

A. (Expanded; no teacher's definition yet) EMR Serverless runs Spark (or Hive) jobs **without creating a cluster**. You submit a job, AWS spins up the compute it needs, runs the job, and releases it. You pay only for the vCPU, memory and storage used **while the job runs**.

**Expanded:** It's the answer to the EMR problem from Training 18: a regular EMR cluster is built from EC2 instances and bills the whole time it's on, even when idle. EMR Serverless keeps EMR's open-source Spark (your normal `spark-submit`-style PySpark script, no Glue-specific code) but bills like Glue, only while working. That's why it fits a batch pipeline where data arrives once a night.

**How you use it:**
1. **Create an application.** This is a reusable container for jobs: you pick the EMR release (Spark version) and the type (Spark or Hive). It costs nothing while idle.
2. **Upload your script** to S3 (e.g. `s3://company-code/jobs/clean_sales.py`).
3. **Start a job run.** Point it at the script, its arguments and an IAM **execution role** that lets the job read and write the right buckets.

```bash
aws emr-serverless start-job-run \
  --application-id <application-id> \
  --execution-role-arn <job-role-arn> \
  --job-driver '{
    "sparkSubmit": {
      "entryPoint": "s3://company-code/jobs/clean_sales.py",
      "entryPointArguments": ["s3://company-bronze/sales/", "s3://company-silver/sales/"]
    }
  }'
```

The script itself is plain PySpark, the same as on your laptop or an EMR cluster:

```python
import sys
from pyspark.sql import SparkSession, functions as F

src, dst = sys.argv[1], sys.argv[2]
spark = SparkSession.builder.appName("clean_sales").getOrCreate()

df = spark.read.option("header", True).csv(src)
clean = (df.dropDuplicates(["sale_id"])
           .withColumn("amount", F.col("amount").cast("decimal(10,2)"))
           .withColumn("sale_date", F.to_date("sale_date")))
clean.write.mode("overwrite").partitionBy("sale_date").parquet(dst)
```

| | EMR on EC2 (cluster) | **EMR Serverless** | Glue |
|---|---|---|---|
| Cluster to manage | Yes: EC2 nodes you size and shut down | **No** | No |
| Bills while idle | Yes | **No**: only while a job runs | No |
| Code | Open-source Spark | **Open-source Spark** (same scripts as EMR) | Spark plus Glue extras (`GlueContext`, `DynamicFrame`) |
| Startup time | 10–20 min to create a cluster; jobs then start instantly | Seconds to a couple of minutes per job (less with **pre-initialized capacity**) | About a minute per job |
| Control / tuning | Full (instance types, any tool, SSH) | Spark settings only; no SSH | Limited to what Glue exposes |
| Best for | Constant, heavy, always-busy work | Occasional Spark batch jobs where you want plain open-source Spark | Occasional ETL, especially with the Data Catalog, crawlers and Glue Studio |

**Why this blurs Training 18's EMR-vs-Glue rule:** the "traditional" rule was *EMR = always on, Glue = occasional*. EMR Serverless is EMR that's also pay-per-job, so for an occasional batch job the choice between EMR Serverless and Glue comes down to preference: plain portable Spark (EMR Serverless) or Glue's built-in catalog and visual tooling (Glue).

---

## Streamlit App on ECS/Fargate (Visualization Layer)

Q. How is the visualization layer of the batch pipeline hosted?

A. (Teacher's definition) Streamlit app for visualization hosted on ECS/Fargate.

**Expanded:** Three pieces work together here:

| Piece | What it is | Analogy |
|---|---|---|
| **Streamlit** | An open-source Python library that turns a Python script into an interactive web app (charts, tables, filters, dropdowns) with no HTML/JavaScript | The dashboard itself |
| **ECS (Elastic Container Service)** | AWS's service for **running Docker containers**: it starts them, restarts them if they crash, and keeps the right number running | The manager that keeps the app running |
| **Fargate** | The **serverless engine** for ECS: AWS supplies the machine the container runs on, so there's no EC2 instance to manage | Renting just the space the container needs, instead of a whole computer |

So "Streamlit on ECS/Fargate" means: **package the Streamlit app as a Docker container, and let AWS run it without you managing any server.**

### How it fits together

```
Business user's browser
        │  https
        ▼
Application Load Balancer (public URL)
        │
        ▼
ECS service ──runs──▶ Fargate task (Docker container: streamlit run app.py, port 8501)
                                  │  SQL (redshift_connector or the Redshift Data API)
                                  ▼
                       Redshift Serverless (fact_sales, dim_* tables)
```

### Deploy steps

1. **Write the app** (`app.py`), e.g. a chart of daily sales from Redshift.
2. **Containerize it** with a `Dockerfile`.
3. **Push the image to ECR** (Elastic Container Registry, AWS's private Docker Hub).
4. **Create an ECS task definition:** which image, how much CPU/memory, port 8501, environment variables, and the **task IAM role** (permission to query Redshift / read the secret).
5. **Create an ECS service** on a cluster with **launch type Fargate**. It keeps 1+ copies (tasks) running and puts them behind a **load balancer**.
6. Open the load balancer's URL in a browser.

```python
# app.py
import streamlit as st
import redshift_connector, pandas as pd, os

conn = redshift_connector.connect(
    host=os.environ["REDSHIFT_HOST"], database="dev",
    user=os.environ["REDSHIFT_USER"], password=os.environ["REDSHIFT_PASSWORD"],  # from Secrets Manager, never hard-coded
)
df = pd.read_sql("SELECT sale_date, SUM(amount) AS revenue FROM analytics.fact_sales GROUP BY 1 ORDER BY 1", conn)

st.title("Daily Sales")
st.line_chart(df, x="sale_date", y="revenue")
st.dataframe(df)
```

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt     # streamlit, pandas, redshift_connector
COPY app.py .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### ECS vocabulary

| Term | Meaning |
|---|---|
| **Cluster** | A logical group that ECS tasks/services run in (with Fargate, there are no machines in it to manage) |
| **Task definition** | The recipe: image, CPU, memory, ports, env vars, IAM role. Like a `docker run` command written down |
| **Task** | One running copy of a task definition (one or more containers) |
| **Service** | Keeps N tasks running, replaces failed ones, connects them to a load balancer |
| **Launch type** | **Fargate** (serverless) or **EC2** (you supply and manage the EC2 instances) |
| **ECR** | Where the Docker image is stored |

### Fargate vs the other ways to run this app

| | EC2 | **ECS on Fargate** | ECS on EC2 | Lambda |
|---|---|---|---|---|
| You manage a server | Yes | **No** | Yes (the instances) | No |
| Runs a Docker container | If you install Docker | **Yes** | Yes | Only as a short function |
| Good for a long-running web app | Yes | **Yes** | Yes | **No**: 15-min limit, no persistent connections (Streamlit uses WebSockets) |
| Bills | While the instance is on | **Per second for the vCPU/memory the task reserves, while it runs** | While the instances are on | Per request |

**Important cost difference from the rest of the pipeline:** EMR Serverless and Redshift Serverless bill only while working. A Fargate task serving a website bills **the whole time it's running**, because a website has to be up to answer visitors. "Serverless" here means *no server to manage*, not *free when idle*. (You can scale the service to 0 tasks overnight to save money.)

**Why not just a BI tool?** AWS's own BI service is **QuickSight** (next section), and Tableau/Power BI also connect to Redshift. Streamlit is chosen when you want a **custom, code-based** dashboard in Python, version-controlled with the rest of the pipeline, with no per-user BI licenses.

---

## Alternative Visualization Tool: Amazon QuickSight

Q. What's the alternative to a Streamlit app for visualization?

A. (Teacher's definition) Alternative visual tool: AWS QuickSight. QuickSight is a competitor to Tableau and Power BI. Those are called business intelligence tools - basically for data visualization.

**Expanded:** QuickSight is AWS's own **managed, serverless BI (business intelligence) service**, AWS's answer to Tableau and Power BI. You connect it to a data source (Redshift, Athena, S3, RDS and others), then build dashboards by dragging and dropping in the browser. There's no code, no container and no server. Users sign in and view or interact with the dashboards.

**Expanded (how it works):**
- **Data source:** a connection, e.g. to Redshift Serverless or Athena.
- **Dataset:** the tables/query you'll chart. It can query the source live (**direct query**) or import a copy into **SPICE**, QuickSight's in-memory engine, for fast dashboards.
- **Analysis:** where an author builds visuals (bar and line charts, KPIs, maps, pivot tables) and filters.
- **Dashboard:** the published, read-only version shared with viewers. It can also be embedded in other apps.
- **Pricing:** per user (authors cost more than readers), not per server. Readers can be pay-per-session.
- **Extras:** ML insights (anomaly detection, forecasting) and natural-language questions ("Q", now part of its generative-AI features).

**Naming note:** in late 2025 AWS folded QuickSight into a broader product called **Amazon Quick Suite** (the BI part is now "Quick Sight"). Most docs, job posts and interviewers still say QuickSight.

### BI (Business Intelligence) Tools

Q. What are business intelligence (BI) tools?

A. (Teacher's definition) Business intelligence tools - basically for data visualization. (QuickSight, Tableau and Power BI.)

**Expanded:** BI tools sit at the **very end** of the data pipeline. They connect to the warehouse (or lake), let people build charts, dashboards and reports without writing much or any code, and share them across the company so business users can make decisions from the data. Everything a data engineer builds upstream (ingestion, Spark cleaning, the star schema in Redshift) exists so these dashboards show correct, fresh numbers. That's why the **Gold layer** and **star schemas** are shaped the way they are: they're designed to be easy for BI tools to query.

| BI tool | Made by | Notes |
|---|---|---|
| **QuickSight** (Quick Sight) | AWS | Serverless, per-user pricing, connects natively to Redshift, Athena and S3 |
| **Tableau** | Salesforce | Long-time market leader for rich, interactive visual analysis |
| **Power BI** | Microsoft | Very common in companies on Microsoft 365 / Azure; integrates with Fabric (covered later in the course) |
| **Looker** | Google | GCP's BI tool; defines metrics in a modeling layer (LookML) |
| Superset / Metabase | Open source | Free, self-hosted alternatives |
| *Streamlit* | Open source (Snowflake) | **Not a BI tool**: a Python framework for building custom data apps. Used when you want code-level control |

**Where BI fits in the pipeline:**

```
Sources ─▶ S3 (lake) ─▶ Spark (EMR Serverless / Glue) ─▶ Redshift (warehouse) ─▶ BI tool (QuickSight / Tableau / Power BI)
                                                                                     └▶ dashboards for business users
```

### Streamlit on ECS/Fargate vs QuickSight

| | Streamlit on ECS/Fargate | **QuickSight** |
|---|---|---|
| What it is | A custom Python web app you build and host | A managed BI service; dashboards built in the browser |
| Code needed | Yes (Python, Dockerfile, ECS setup) | **No**: drag and drop |
| Who builds it | Data engineers / developers | Analysts and business users too |
| Hosting | You deploy a container on ECS/Fargate behind a load balancer | **Nothing to host**; AWS runs it |
| Flexibility | Anything Python can do (custom logic, ML models, forms/inputs) | Limited to QuickSight's visuals and features |
| Pricing | Fargate vCPU/memory while the app runs, plus the load balancer | **Per user** (or per session) |
| Users and access | You build login yourself (or put it behind a VPN or Cognito) | Built in: users, groups, row-level security |
| Version control | The app is code in Git | Dashboards live in QuickSight (can be exported as definitions) |
| Best for | Custom data apps, prototypes, ML demos, internal tools | Standard business dashboards for many non-technical users |

**Interview one-liner:** "For standard dashboards for business users I'd use QuickSight, since it's managed with no infrastructure and built-in sharing and security. If we need a custom, code-driven data app, I'd build it in Streamlit and run it as a container on ECS Fargate."

---

# ECS (Elastic Container Service)

Q. What is ECS?

A. (Teacher's definition) ECS: Elastic Container Service. The containers that it's talking about are Docker containers.

**Expanded:** ECS is AWS's managed service for **running Docker containers**. You tell it *which* container image to run, *how much* CPU/memory it gets and *how many copies* to keep running. ECS then starts them, restarts any that crash, spreads them across machines and connects them to a load balancer. It's the AWS equivalent of running `docker run` / `docker compose up` yourself, but at production scale and self-healing.

**Containers refresher (from using Docker in class):** a container packages an app **plus everything it needs** (Python version, libraries, config) into one image, so it runs the same on a laptop, a server or AWS. "It works on my machine" stops being a problem. An EC2 instance is a whole virtual computer; a container is a much lighter, isolated process that shares the host's operating system.

| | EC2 instance (VM) | Container (on ECS) |
|---|---|---|
| What you get | A whole virtual computer with its own OS | One packaged app sharing the host's OS kernel |
| Starts in | Minutes | Seconds |
| You maintain | The OS: patches, installs, updates | Just the image (your app and its dependencies) |
| Packaging | AMI | Docker image (stored in **ECR**) |

**ECS has two ways to supply the machines (launch types):**

| Launch type | Who provides the compute | You manage | Pick it when |
|---|---|---|---|
| **Fargate** | AWS (serverless) | Nothing but the container | Default choice; you don't want to manage servers |
| **EC2** | EC2 instances in your account that join the ECS cluster | Those instances (size, patching, scaling) | You need special hardware (e.g. GPUs), or have steady load where reserved instances are cheaper |

(ECS vocabulary — cluster, task definition, task, service, ECR — is in the table in the Streamlit section above.)

**ECS vs the other AWS container services:**

| Service | What it is | When |
|---|---|---|
| **ECS** | AWS's own, simpler container orchestrator | Most AWS-only teams; easiest path to running containers |
| **EKS (Elastic Kubernetes Service)** | Managed **Kubernetes** (the open-source standard orchestrator, Day 43 in the syllabus) | Teams already on Kubernetes, or that need to run the same setup across clouds |
| **Fargate** | Not a separate service you use alone: the serverless compute engine **under** ECS or EKS | When you don't want to manage the nodes |
| **ECR (Elastic Container Registry)** | Private storage for Docker images (like Docker Hub) | Always; ECS/EKS pull images from here |
| **App Runner** | Even simpler: give it an image or repo and it gives back a URL | Small web apps when you don't want to configure ECS at all |

**Where data engineers use ECS:**
- **Hosting data apps and dashboards:** the Streamlit app in today's pipeline.
- **Running containerized batch jobs:** a Python ETL script packaged as a container, started on a schedule by EventBridge. It has no 15-minute limit like Lambda, and it's lighter than Spark when the data is small.
- **Running pipeline tooling:** e.g. Airflow (Day 27), API services, or a small Kafka consumer, all as long-running ECS services.

---

## Fargate

Q. What is Fargate?

A. (Teacher's definition) Fargate is basically serverless ECS. Effectively what it means is that the container is hosted and available to be accessed by the public - but if no one is accessing it, then there is no cost to you.

**Expanded:** With plain ECS (EC2 launch type) you still have to run a fleet of EC2 instances for your containers to live on, then size, patch and scale them. With **Fargate**, you only describe the container (image, CPU, memory) and AWS finds a machine to run it on. You never see or manage that machine. It's the same idea as the rest of today's "serverless" services: the servers exist, but they're AWS's problem.

| | ECS on EC2 | **ECS on Fargate** |
|---|---|---|
| Machines | Your EC2 instances, registered to the cluster | AWS's; invisible to you |
| You size | Instances (and pack containers onto them) | Each task's vCPU and memory (e.g. 0.5 vCPU / 1 GB) |
| Patching / OS updates | You | AWS |
| Scaling | Scale the tasks **and** the instances underneath | Scale the tasks only |
| Billing | For the instances while they're on, even if half-empty | Per second for the vCPU/memory each task reserves while it runs |
| GPUs / special hardware | Yes | No |
| SSH into the host | Yes | No |

**"Serverless" doesn't mean "pay only when used" here.** Fargate bills **while the task is running**, not per request. A Streamlit dashboard that's up 24/7 bills 24/7, unlike EMR Serverless or Redshift Serverless, which stop billing between jobs or queries. What makes Fargate serverless is that there's **no server to manage**.

**Accuracy note (cost when idle):** Evan said that if no one is accessing the container, there's no cost. That isn't how Fargate bills. Fargate charges **per second for the vCPU and memory of each running task** (from when the image starts downloading until the task stops, with a 1-minute minimum), whether or not anyone visits. A task with no traffic still costs money. A public app also usually sits behind an **Application Load Balancer**, which bills hourly too. What *is* true: there's no server for you to pay for or manage on top, and you can make idle cost zero by **scaling the service to 0 tasks** (manually or on a schedule, e.g. overnight).

| If you want... | Use | Idle cost |
|---|---|---|
| A container that's always reachable | ECS on Fargate (1+ tasks running) | Pays for the running tasks + load balancer |
| Zero cost when idle (Evan's description) | **Lambda** (with a Function URL or API Gateway), or Fargate scaled to 0 on a schedule | Truly ~$0 with Lambda; $0 with Fargate only while scaled to 0 (the app is offline then) |
| Something in between | **App Runner** | Low: it bills only memory while idle, and full vCPU + memory while handling requests |

In an interview: "Fargate is serverless in the sense that I don't manage servers. I pay for the task's vCPU and memory while it runs, so for spiky traffic I'd use autoscaling, or Lambda if it truly needs to scale to zero."

**Accuracy note:** Fargate also runs containers for **EKS** (Kubernetes), not only ECS. "Serverless ECS" is how it's used most of the time, though.

---

# Class Project Data Source: Citi Bike GBFS Feed

Q. What data will the batch pipeline use?

A. (Teacher's definition) "View the data feed we will use": Evan's script reads the Citi Bike **GBFS** feed (`https://gbfs.citibikenyc.com/gbfs/gbfs.json`) and inspects three of its feeds: `station_information`, `station_status` and `system_information`.

**Expanded:** **GBFS (General Bikeshare Feed Specification)** is an open standard that bike and scooter share systems use to publish real-time data as public JSON files over HTTP. No API key is needed. Citi Bike (NYC, operated by Lyft) publishes one. It's a good pipeline source because it's free, live, updates every minute, and has real data-quality problems to clean.

Runnable copy: `class-demos/training-19-evan-citibike/explore_gbfs.py` (indentation and `#` comments restored from the paste; the code is unchanged). It uses only the Python standard library: `python3 explore_gbfs.py`.

### How GBFS is organized

`gbfs.json` is a **discovery document**: it doesn't hold the data, just a list of the other feeds and their URLs. That's why the script reads it first, then follows the links. This "index file, then follow the URLs" pattern is common in public APIs, and it means you never hard-code feed URLs. (They currently redirect to `gbfs.lyft.com/gbfs/1.1/bkn/en/...`.)

```
gbfs.json (discovery) ──lists──▶ system_information.json
                                 station_information.json
                                 station_status.json
                                 ...(9 more feeds)
```

| Feed | What it holds | Changes | In pipeline terms |
|---|---|---|---|
| **`station_information`** | Each station's ID, name, lat/lon, capacity, region, payment methods | Rarely (new or moved stations) | **Dimension** (`dim_station`) |
| **`station_status`** | Each station's *current* bikes available, e-bikes, docks free, broken bikes/docks, renting/returning flags, `last_reported` | Every ~minute | **Fact** (`fact_station_status`, one row per station per snapshot) |
| **`system_information`** | The system itself: name (Citi Bike), operator (Lyft), start date (2013-05-01), timezone, URLs | Almost never | Reference / metadata |

Other feeds in the discovery doc (not used yet): `ebikes_at_stations`, `free_bike_status`, `system_hours`, `system_calendar`, `system_regions`, `system_pricing_plans`, `system_alerts`, `gbfs_versions`.

### What the script does, step by step

| Step | Code | Purpose |
|---|---|---|
| `get_json(url)` | `urllib.request.urlopen(url, timeout=30)` → `json.loads` | Download one URL and parse the JSON into Python dicts/lists. The timeout stops it hanging forever |
| 1 | `gbfs["data"]["en"]["feeds"]` | Read the discovery doc; the feed list is under the English (`en`) language key |
| 2 | Loop, keep names in `WANTED_FEEDS` | Build `{feed_name: url}` for the 3 feeds we want (a **set** makes the `in` check fast) |
| 3 | `datasets[name] = get_json(url)` | Download each wanted feed |
| 4–6 | `json.dumps(..., indent=2)` on the first 3 records | **Profile** the data: look at the real fields before designing tables |
| 7 | Set comprehensions + set difference (`status_ids - info_ids`) | **Validation**: does every status record have matching station metadata, and vice versa? Then print the UTC snapshot time |

### What a run showed (Oct 7, 18:31 UTC)

- **2,520 stations** in both `station_information` and `station_status`, with **0 mismatched IDs** in either direction, so the join key (`station_id`) lines up.
- Every feed has `last_updated` (Unix epoch seconds) and **`ttl: 60`**: the data is refreshed every 60 seconds, so polling more often than once a minute is pointless.

Sample `station_status` record:

```json
{
  "station_id": "1860189650739626488",
  "num_bikes_available": 0,
  "num_bikes_disabled": 13,
  "num_docks_available": 8,
  "is_installed": 1,
  "is_renting": 0,
  "is_returning": 0,
  "last_reported": 1791315217,
  "num_ebikes_available": 0
}
```

**Data-quality issues already visible (things the Spark cleaning step will need to handle):**

| Issue | Example | Cleaning idea |
|---|---|---|
| **Fake timestamps** | `"last_reported": 86400`, which is Jan 2, 1970: a placeholder meaning "never reported" | Treat values before ~2013 (the system's start date) as `NULL` |
| **Uninstalled stations** | `is_installed: 0`, everything 0 | Filter out, or flag as inactive |
| **`capacity: 0`** in station info | Stations whose capacity shows as 0 | Don't divide by capacity without checking; derive it from bikes + docks if needed |
| **Mixed ID formats** | UUIDs (`66db2a71-...`) and long numbers (`1860189650739626488`) | Keep `station_id` as a **string**, never cast to int |
| **Epoch times** | `last_reported`, `last_updated` are Unix seconds | Convert with `from_unixtime` / `to_timestamp` to UTC timestamps |
| **Optional fields** | Some records have `num_scooters_available`, others don't | Define an explicit schema; missing → `NULL` |

### How this feeds the batch pipeline

`station_status` is a **current snapshot only**: the API doesn't keep history. To analyze over time (e.g. "which stations run out of bikes at 8am?"), the pipeline has to **save a snapshot on a schedule** and build the history itself:

```
Every N minutes (EventBridge schedule → Lambda or ECS task)
   └─▶ download the feeds ──▶ S3 Bronze: raw JSON, partitioned by snapshot time
                                 e.g. s3://citibike-bronze/station_status/dt=2026-10-07/hour=18/1831.json
Nightly: Spark on EMR Serverless
   └─▶ flatten JSON, convert epoch → timestamp, clean, dedupe ──▶ S3 Silver (Parquet)
   └─▶ build dim_station + fact_station_status ──▶ COPY ──▶ Redshift Serverless
   └─▶ Streamlit on ECS/Fargate (or QuickSight) dashboards: availability by station and hour, empty/full stations
```

---

## Ingestion Script: GBFS → S3 Bronze

Q. How does the Citi Bike data get into S3?

A. (Teacher's code) Evan's ingestion script downloads the discovery document and the three wanted feeds, then writes each one **as raw JSON** to the `citi-bike-nyc` bucket under `bronze/citibike/<dataset>/year=/month=/day=/hour=/`, using `boto3` with the `company` AWS profile in `us-east-2`.

**Expanded:** This is **step 1 of the batch pipeline (ingest into S3)** in code. It doesn't clean or change anything; it lands the data exactly as received, which is what Bronze is for. Cleaning comes later in Spark.

Runnable copy: `class-demos/training-19-evan-citibike/ingest_to_s3.py` (indentation, `#` comment lines and the `if __name__ == "__main__":` guard restored from the paste; the logic is unchanged). It needs `pip install boto3` and an AWS profile named `company`. You don't have AWS access yet, so it can't run until you do.

### What each part does

| Section | Code | Why |
|---|---|---|
| **Config** | `BUCKET`, `AWS_PROFILE`, `AWS_REGION`, `WANTED_FEEDS` at the top | Settings in one place, not buried in the logic |
| **HTTP** | `urllib.request.Request(url, headers={"User-Agent": ...})` | Same `get_json` as the explore script, plus a **User-Agent** header that identifies the caller. Some public APIs block or throttle requests without one |
| **AWS session** | `boto3.Session(profile_name="company", region_name="us-east-2")` → `session.client("s3")` | **boto3** is the AWS SDK for Python. A **profile** is a named set of credentials in `~/.aws/credentials` (made with `aws configure --profile company`). `us-east-2` = **Ohio** |
| **S3 write** | `s3.put_object(Bucket=..., Key=..., Body=..., ContentType="application/json")` | Uploads one object. `Body` must be bytes, hence `.encode("utf-8")` |
| **Compact JSON** | `json.dumps(data, separators=(",", ":"))` | Removes the spaces after `,` and `:`, so files are smaller (cheaper storage, less to scan) |
| **Snapshot time** | `datetime.now(timezone.utc)`, taken **once** in `main()` | Every file from one run shares the same timestamp, so the four files can be matched up later. **UTC** avoids daylight-saving problems |
| **Fail fast** | `missing = WANTED_FEEDS - set(feed_urls)` → `raise RuntimeError` | If Citi Bike renames or removes a feed, the run fails loudly instead of quietly saving incomplete data |
| **Save the discovery doc too** | `write_json_to_s3("gbfs_discovery", discovery, ...)` | Keeps a record of which feed URLs and versions were used for each snapshot (lineage) |
| **Summary** | `len(uploaded) + 1` | The `+1` counts the discovery file, which isn't in the `uploaded` list |

### The S3 key layout (Hive-style partitions)

```
s3://citi-bike-nyc/bronze/citibike/station_status/year=2026/month=10/day=07/hour=18/station_status_20261007T183145Z.json
                   └─layer─┘└source┘└─dataset───┘└──────── partitions (key=value) ────────┘└──── file named by snapshot time ───┘
```

| Part | Why it's designed this way |
|---|---|
| `bronze/` prefix | The medallion layer. (Here it's a prefix in one bucket; Training 18's recommendation was a separate bucket per layer. Both work, but separate buckets make permissions simpler) |
| `citibike/<dataset>/` | One folder per feed, so each becomes its own table |
| `year=2026/month=10/...` | **Hive-style partitions** (`key=value`), the same idea as Hive partitioning in Training 8. The Glue Crawler turns them into partition columns automatically, and Athena/Spark can **skip** folders that don't match a `WHERE year=2026 AND month=10` filter (partition pruning), so queries scan less and cost less |
| `%Y%m%dT%H%M%SZ` filename | ISO-8601 basic format in UTC (`Z` = UTC). Files sort in time order, and two runs never overwrite each other |

### Moving it to AWS (the next step)

On a laptop the script authenticates with a **profile**. Running in AWS (Lambda or an ECS task on a schedule), it should use an **IAM role** instead, with no profile and no stored keys:

```python
s3 = boto3.client("s3")   # picks up the Lambda/ECS role's temporary credentials automatically
```

| | Laptop | Lambda / ECS task |
|---|---|---|
| Credentials | `~/.aws/credentials` profile (`company`) | The function's or task's **IAM role** (temporary credentials) |
| Code change | `boto3.Session(profile_name=...)` | `boto3.client("s3")`; drop `profile_name` |
| Scheduling | Run by hand or cron | **EventBridge schedule**, e.g. every 5 minutes (the feed's `ttl` is 60 s, so every minute is the fastest that makes sense) |
| Permission needed | Whatever the profile's user has | A least-privilege policy: `s3:PutObject` on `arn:aws:s3:::citi-bike-nyc/bronze/citibike/*` |

**Size check:** at 4 files per run, every 5 minutes is about 1,150 files a day. That's fine for S3, but lots of small files slow Spark down. That's a reason the nightly Spark job **compacts** them into a few larger Parquet files in Silver.

---
