---
title: "Training 34 - GCP Intro, Beam and Storage Transfer"
description: "GCP compared with AWS and Azure, Apache Beam and Dataflow basics, BigQuery, and an S3-to-GCS migration with Storage Transfer Service."
sidebar:
  order: 34
---

Teacher: Evan Flint

Syllabus Day 35 (per file numbering; Wed Oct 28, 2026). The roadmap had a **Presentation** day for today (trainee presentations and an architecture review), but Evan skipped it and started **GCP day 1** instead (roughly roadmap Day 36: Cloud Storage, BigQuery, plus a preview of Dataflow from Day 37). Presentations moved to next week (see below).

Source: class notes.

**Code note:** the code below is written from the class demo plus standard Apache Beam / gcloud / AWS syntax. It is not an exact copy of Evan's code.

---

# Capstone presentations: dates and requirements

> **Capstone presentations are next week.** At the start of class Evan told the students they have "another week" to finish, make edits, and practice. On Thursday (Training 35) the plan became: **practice run on Monday, Nov 2**, then **real presentations on Friday, Nov 6**. See Training 35 for details.

| Item | What Evan said |
|---|---|
| Timing | About one more week of work. Use it to finish the pipeline, fix things, and practice the narrative |
| Single cloud is fine | "You don't need to force it to be multi cloud if you have a complete presentable pipeline that's mainly in Azure Databricks" |
| Minimum shape | An **ingestion job** into cloud object storage (e.g. ADLS Gen2), processing up through the **lakehouse layers** (Bronze → Silver → Gold), then a **visualization** connected to the Gold data |
| Visualization | Use a tool **other than** Databricks' built-in charts if you can (e.g. Looker Studio / Google Data Studio, Power BI, Streamlit). Databricks visualizations "are fine, but they're pretty basic", and connecting another service shows you can serve the data |
| Live demo backup | A student backed up all his notebook code locally in case his Databricks workspace has to be rebuilt before the live demo. Good idea given the recent Azure problems |
| Homework | Read about **GCP Storage Transfer Service (STS)** and the general GCP services from the lecture, and keep working on the capstone |

---

# Today at a glance

| # | What happened |
|---|---|
| 1 | Capstone check-in round (earthquake map + charts, theme-park wait-time Streamlit dashboard, a Databricks VM-capacity region move, Power BI) |
| 2 | Why GCP now: fewer interviews than AWS/Azure, but bench candidates panic when a GCP interview comes up |
| 3 | Lecture: GCP is "the exact same thing, except with a couple of Google flourishes". Service map: GCS, Dataflow (Apache Beam), Dataproc, BigQuery, STS, Cloud Run functions, Composer, Looker Studio, Cloud SQL |
| 4 | First look at Apache Beam pipeline syntax (`|` pipe steps). Student questions about Cloud Run jobs, enabling APIs, Firestore |
| 5 | Break |
| 6 | Demo: new GCP project, but **billing never finished enabling**. Local Beam demo while waiting: `map` vs `flatMap`, Bronze → Silver locally |
| 7 | Break |
| 8 | Plan B: local Beam job loads Bronze JSON into **local Postgres**, then try **AWS DMS** Postgres → S3. Blocked: no IAM permission to create a DMS endpoint |
| 9 | Break. Cause found: the GCP billing problem was a **quota** issue on the new project |
| 10 | Switched to an older project with billing on. **STS** transfer from S3 to GCS: permission errors, then success |
| 11 | Profile narratives: Databricks + Snowflake in one project, Spark/Kafka in an AWS context, a PayPal Hadoop → BigQuery migration story |
| 12 | Final Q&A: multi-cloud not required, bronze/silver/gold vs raw/curated/semantic |

---

# Why GCP, and how it compares

Q. Why is GCP in the course now?

A. (Evan) "For the longest time in our training classes, we just taught AWS, and then it was just AWS and Azure. And now it's finally AWS, Azure and GCP." There's less time for it because "AWS and Azure definitely have the lion's share of the interview opportunities". But "every once in a while… somebody on bench will get a GCP focused interview", and they panic because they only studied AWS or Azure. Today's goal is to prevent that.

Expanded: you don't need GCP depth unless your profile uses it. You do need to be able to **map every GCP service to the AWS/Azure one you already know**, and to explain what makes BigQuery and Dataflow different.

---

Q. How is GCP different from AWS and Azure?

A. (Teacher's definition) "GCP is basically just the exact same thing, except with a couple of Google flourishes."

Expanded: the flourishes Evan named:

| GCP convenience | What it means |
|---|---|
| Easy sign-up | If you have a Gmail address you already have a Google account, so creating a GCP account is a smaller step |
| GCS console | It's a little easier to look at your data. You can preview some files (e.g. images) right in the console |
| One-click authorization buttons | Some services have buttons that grant the permissions you need. "Not a silver bullet": sometimes you still need extra IAM or command-line steps |
| Overall auth | "Comparatively easier to get authentication done in GCP than it is in AWS or Azure" (today's demo made this ironic) |
| Google AI integration | Gemini can talk natively to other Google services, because Google runs those services. A student mentioned Gemini is good at exact transcripts of YouTube videos |

The thing Evan called **more complicated** on GCP is **Cloud Dataflow**, because it uses Apache Beam instead of plain Spark.

---

# The GCP service map

Q. Which GCP services matter for a data pipeline?

A. (Evan, lecture) For an ELT lakehouse on GCP: ingest into **GCS** (by migration with **STS** or incrementally with **Cloud Run functions** scheduled by **Composer**), process Bronze → Silver → Gold with **Dataflow** or **Dataproc**, warehouse in **BigQuery**, and visualize with **Looker Studio**.

```
Source (S3 / on-prem / API)
   │  Storage Transfer Service (migration)   or   Cloud Run functions (incremental, scheduled by Cloud Composer)
   ▼
GCS Bronze bucket (raw)
   │  Cloud Dataflow (Apache Beam)   or   Dataproc / Managed Service for Apache Spark
   ▼
GCS Silver  →  Gold (BigQuery tables, star schema)
   ▼
Looker Studio dashboard
```

| Role | GCP | AWS | Azure |
|---|---|---|---|
| Object storage (landing / lake) | **Cloud Storage (GCS)** | S3 | ADLS Gen2 |
| Bulk migration / copy | **Storage Transfer Service (STS)** | DMS (database-aware), DataSync | ADF copy activity, Azure DMS |
| Serverless functions | **Cloud Run functions** (formerly Cloud Functions) | Lambda | Azure Functions |
| Container deployment | **Cloud Run** | ECS | Container Apps / ACI |
| VMs | **Compute Engine** (Evan said App Engine; see note) | EC2 | Azure VMs |
| Managed Airflow | **Cloud Composer** | MWAA | ADF Managed Airflow |
| Data processing (Beam) | **Cloud Dataflow** | Glue (closest role) | Databricks / Synapse notebook |
| Spark / Hadoop | **Dataproc** (serverless now branded "Managed Service for Apache Spark") | EMR / EMR Serverless | HDInsight / Databricks |
| Serverless data warehouse | **BigQuery** | Redshift (Serverless), Athena | Synapse |
| Relational DB | **Cloud SQL** | RDS | Azure SQL |
| BI | **Looker Studio** (formerly Google Data Studio) | QuickSight | Power BI |
| NoSQL (app-facing) | **Firestore** | DynamoDB | Cosmos DB |
| IAM | **IAM** | IAM | Entra ID + RBAC |

Note: Evan compared "Google App Engine" to EC2. Strictly, **Compute Engine** is GCP's VM service (the EC2 equivalent); **App Engine** is a managed app-hosting platform, closer to Elastic Beanstalk. Use Compute Engine in interviews.

---

Q. What is Cloud Dataflow?

A. (Teacher's definition) "It is yet another one of the data processing services. So you can compare it to AWS Glue… a Databricks or Synapse notebook. Not the full Databricks or Synapse platform, but like a notebook within them." Its "main processing framework is Apache Beam."

Expanded: Dataflow is Google's fully managed, autoscaling runner for Beam pipelines. It handles **batch and streaming** with the same code. Evan started it a day early because "it looms so large in the GCP space".

---

Q. What is Apache Beam?

A. (Teacher's definition) "Beam basically is a way of writing a data processing job… Beam actually doesn't have its own inbuilt data processor. What it does is it connects to some other data processor and it provides the code interface that we use in order to write that process." He's mostly seen it used for **ETL**, though it could do ELT.

Expanded: Beam = one **programming model** (the name comes from **B**atch + str**eam**), many **runners**. You write the pipeline once and choose where it runs:

| Runner | Where the pipeline runs |
|---|---|
| `DirectRunner` | Your laptop (testing) |
| `DataflowRunner` | Google Cloud Dataflow (managed) |
| `SparkRunner` | A Spark cluster (on-prem or cloud) |
| `FlinkRunner` | A Flink cluster |

So Beam on-prem is possible (on Spark or a Hadoop stack), but in practice "the most likely use case for Apache Beam is going to be Cloud Dataflow."

| Beam term | Meaning | Spark analogy |
|---|---|---|
| `Pipeline` | The whole job (a DAG of steps) | The Spark application |
| `PCollection` | A distributed dataset flowing between steps | RDD / DataFrame |
| `PTransform` | One step (`Map`, `Filter`, `ParDo`, …) | A transformation |
| `ParDo` / `DoFn` | "Parallel do": a custom per-element function, can emit 0..n outputs | `mapPartitions` / UDF |
| `CombinePerKey` | Aggregate values per key | `reduceByKey` / `combineByKey` |
| `GroupByKey` | Group values by key | `groupByKey` |
| Runner | The engine that executes | The cluster manager / Spark itself |

---

Q. What does Beam code look like?

A. (Evan) After the plain Python boilerplate, "with `beam.Pipeline() as pipeline`… every one of the different lines that is a new job starts with the pipe symbol." The pipe is **Shift + backslash**, and "in traditional computer symbolism, the pipe symbol means take something from one place and put it in another place." Each step "is on one or maybe two lines of code… This is the central reason why people actually use Beam."

```python
# from the article Evan shared (not exact)
import json
import apache_beam as beam

def parse_json(line):
    return json.loads(line)

def is_valid(rec):
    return rec.get("station_id") is not None and rec.get("capacity", 0) > 0

def calc_utilization(rec):
    rec["utilization"] = rec["num_bikes_available"] / rec["capacity"]
    return rec

with beam.Pipeline() as pipeline:
    (pipeline
     | "ReadJSON"          >> beam.io.ReadFromText("input/*.json")
     | "ParseJSON"         >> beam.Map(parse_json)
     | "Validate"          >> beam.Filter(is_valid)
     | "CalcUtilization"   >> beam.Map(calc_utilization)
     | "KeyByStation"      >> beam.Map(lambda r: (r["station_id"], r["utilization"]))
     | "Aggregate"         >> beam.CombinePerKey(max)
     | "FormatResult"      >> beam.Map(lambda kv: {"station_id": kv[0], "max_util": kv[1]})
     | "SerializeJSON"     >> beam.Map(json.dumps)
     | "WriteOutput"       >> beam.io.WriteToText("output/results", file_name_suffix=".json"))
```

Expanded: read it top to bottom like a recipe. `"Label" >> transform` gives each step a name, and those names become the boxes in the Dataflow job graph. Validation is a `Filter`, "as we've seen in recent examples of ELT code". `CombinePerKey` is "like a `combineByKey` in Spark RDD". Evan's point: it's "just another style of writing the same kind of logic", so don't let the syntax scare you in an interview.

---

Q. What is the difference between `map` and `flatMap`? (Evan: "a common interview question, or at least a fairly common one")

A. (Teacher's definition) "With map, it's a one-to-one transformation with all objects, no matter what data type they are. With flat map, on the other hand, it does what we call removing internal groupings. So if you have a list of lists, all of the items in the sub-lists of the list will just get brought to the very top."

```python
# from the class demo (not exact)
import apache_beam as beam

data = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]

with beam.Pipeline() as p:
    (p | "Create" >> beam.Create(data)
       | "Map"    >> beam.Map(lambda xs: [x * 2 for x in xs])
       | "Print"  >> beam.Map(print))
# [2, 4, 6]
# [8, 10]
# [12, 14, 16, 18]          -> 3 output elements (one per input list)

with beam.Pipeline() as p:
    (p | "Create"  >> beam.Create(data)
       | "FlatMap" >> beam.FlatMap(lambda xs: [x * 2 for x in xs])
       | "Print"   >> beam.Map(print))
# 2, 4, 6, 8, 10, 12, 14, 16, 18   -> 9 output elements (nesting removed)
```

| | `Map` | `FlatMap` |
|---|---|---|
| Outputs per input | Exactly 1 | 0, 1 or many |
| Function returns | One value | An iterable, which gets flattened |
| Typical use | Convert / clean each record | Explode a nested array (e.g. one snapshot file → many station rows) |
| Spark equivalent | `map` / `withColumn` | `flatMap` / `explode` |

---

# BigQuery (intro)

Q. What is BigQuery?

A. (Teacher's definition) "The first serverless SQL warehouse." Back in 2019 "there was only one that was serverless. And that was BigQuery." Instead of "provisioning a big, expensive, unresponsive cluster", Google made "a serverless data warehouse, you can still use SQL to query it, and you are charged based on the data that you're querying, rather than on the data that you're storing."

Expanded: storage in BigQuery is cheap (about the same as a GCS bucket); **queries** are where the bill grows, because on-demand pricing charges by **bytes scanned**. Evan was careful with queries since he demoed on his personal account. Evan credits features like this for GCP's rise: in 2019 "it was considered a waste of time to even learn Azure", and AWS dominated.

| Cost lever | Why it matters in BigQuery |
|---|---|
| `SELECT` only the columns you need | Columnar storage: fewer columns = fewer bytes billed |
| Partitioned tables (e.g. by date) | Filters on the partition column skip whole partitions |
| Clustered tables | Sorts data by columns so filters read fewer blocks |
| Preview / dry run | The console shows "This query will process X MB" before you run it |
| `LIMIT` | Does **not** reduce bytes scanned on a normal table |

---

# Ingestion: STS and Cloud Run functions

Q. What is Storage Transfer Service?

A. (Teacher's definition) "Google Cloud Storage Transfer Service… which is like AWS DMS. Or you can sort of compare it to an Azure Data Factory copy activity."

Expanded: later in the demo Evan found out the comparison only goes so far. **DMS is database-aware**: it connects to a database (e.g. Postgres) and replicates tables. **STS moves files/objects** between storage systems (S3, Azure Blob, HTTP lists, on-prem file systems through agents) into GCS. It can't read from Postgres. "So this means that STS works on different logic fundamentally than DMS."

| | AWS DMS | GCP STS | GCP Database Migration Service |
|---|---|---|---|
| Moves | Database tables (full load + CDC) | Files / objects | Database tables (to Cloud SQL / AlloyDB) |
| Typical source | Postgres, MySQL, Oracle, SQL Server | S3, Azure Blob, URL lists, POSIX file systems | MySQL, Postgres, SQL Server, Oracle |
| Typical target | RDS, Redshift, **S3** | **GCS** | Cloud SQL / AlloyDB |
| Needs a replication instance / agent? | Replication instance | Agents only for on-prem / S3-compatible sources | Managed |

Interview tip: if your profile is a migration **into GCP from S3 or Hadoop files**, the tool is **STS**. GCP also has a **BigQuery Data Transfer Service** for scheduled loads into BigQuery (a student remembered that one), and Google's open-source **Data Validation Tool (DVT)** for checking row counts after a migration.

---

Q. How do you do incremental ingestion?

A. (Evan) The same way as on AWS: "ingest data incrementally with scheduled serverless functions… Google Cloud Functions. So that's like AWS Lambda or Azure Functions." Schedule them with **Cloud Composer**, "basically managed Airflow", the equivalent of **MWAA** on AWS. (A student guessed Step Functions; Evan: "step functions isn't managed airflow. Step functions is a completely different AWS specific thing.")

---

Q. Why did my Cloud Run job need a Dockerfile? (a student working on a GCP capstone)

A. (Evan) Cloud Functions are now called **Cloud Run functions**, and **Cloud Run** is "Google Cloud's equivalent of AWS ECS. So it's basically a container deployment service." If GCP now requires your function in a container, "that actually is a significant architectural difference between GCP and AWS. It didn't used to be like that."

Uploading a zip of your code is the normal professional pattern on AWS too. In his Lambda demo he packaged a dependency with pip into a zip, put it on S3, and pointed Lambda at it. "Most people writing Lambda functions have some kind of dependency… so the method of packaging them in zip files… has just kind of become the common professional standard."

Expanded:

| GCP option | What you deploy | AWS equivalent |
|---|---|---|
| Cloud Run **functions** | Source code (GCP builds the container for you behind the scenes) | Lambda (zip) |
| Cloud Run **services** | A container that serves HTTP requests | ECS / App Runner |
| Cloud Run **jobs** | A container that runs to completion (batch tasks) | ECS task / AWS Batch |

---

Q. Do we need to enable APIs? Some ask for subscriptions. (a student)

A. (Evan) Yes. "There are APIs that need to be activated, but it's made a little bit more streamlined than any others." Every service (BigQuery, Dataflow, Storage Transfer, …) has an API that must be **enabled per project** before you can use it, and billing must be on. "That is just the nature of working on the cloud. It's never going to go away."

```bash
# standard gcloud syntax
gcloud services list --enabled
gcloud services enable storage.googleapis.com bigquery.googleapis.com \
    dataflow.googleapis.com storagetransfer.googleapis.com
```

---

Q. Does Firestore count as big data? (a student with an Android background)

A. (Evan) "Insofar as Firestore is a database, it absolutely can be used in big data." But it's "more designed for customer-facing applications than it is for back-end stuff". It's NoSQL and JSON-document based, "at least somewhat similar to DynamoDB". GCP "has all the Google stuff". Evan's own example: to auto-post videos to YouTube he had to register a GCP app and apply for API access, and then he gets a **quota**, "so you can't just upload 50 hours of content on your first day".

---

# The gcloud CLI

Q. What CLI commands did Evan show?

A. (Evan, demo) Check the SDK version, which account is logged in, and switch projects. When you set a project you may see "Your active project does not match the quota project in your local application default credentials file". That warning matters (see the billing story below).

```bash
# from the class demo (not exact)
gcloud --version
gcloud auth list                                   # which Google account is active
gcloud config get-value project                    # current project
gcloud projects list                               # all your projects
gcloud config set project <PROJECT_ID>
gcloud auth application-default set-quota-project <PROJECT_ID>   # fixes the quota-project warning
gcloud billing projects describe <PROJECT_ID>      # billingEnabled: true/false
bq ls                                              # BigQuery has its own CLI: bq
```

| Tool | Use |
|---|---|
| `gcloud` | Main CLI (projects, IAM, services, Dataflow, STS) |
| `gcloud storage` (or older `gsutil`) | GCS buckets and objects |
| `bq` | BigQuery datasets, tables, queries |

---

# Demo, part 1: the billing wall

Q. What went wrong at the start?

A. (Evan) He created a new project (`example-elt-lakehouse-pipeline`, no organization) and went to GCS. GCS said he couldn't use it until billing was enabled. He linked a billing account, but it stayed stuck. The CLI showed `billingAccountName: null` and `billingEnabled: false` for **over an hour and a half**. Enabling APIs failed with "Billing is not found. Billing must be enabled." (A student said his own fresh account took 20–30 minutes.)

During a break he found the cause: **billing on the new project was blocked by a quota**. Raising it needs a form and Google's approval, which takes about two days and may not be granted for an educational demo. So he **abandoned the new project** and switched to an older project (`my-dataflow-demo-…`) that already had billing.

Expanded: lessons for your own GCP work:

| Lesson | Detail |
|---|---|
| Set up accounts before you need them | Evan: "This is something that I definitely should have arranged beforehand" |
| Billing accounts can only be linked to a limited number of projects | New projects may hit a billing **quota**. Reuse a project that already works, or request the increase early |
| Check with the CLI | `gcloud billing projects describe <id>` shows `billingEnabled` |
| Cloud work is like this | "This is the joy of working in the cloud" |

---

# Demo, part 2: local Apache Beam while waiting

Q. What did he run locally?

A. (Evan, demo) He synced some Citi Bike Bronze JSON from S3 to his laptop (`aws s3 sync`, then cancelled because he didn't need all of it), and ran an AI-written Beam script, `test.py`, with the **DirectRunner**. It declared a Silver schema with **PyArrow** types (`pa.string()`, `pa.timestamp()`, `pa.int64()`) instead of Spark types, and had `parse_snapshot`, `valid_station` and `to_silver` functions.

First run: "No stations found" over and over, because the script expected a different file layout. After he gave the AI a snapshot of the real data, it wrote Silver output (at least for the GBFS discovery feed).

```python
# from the class demo (not exact)
import argparse, json
import apache_beam as beam
from apache_beam.io import fileio
import pyarrow as pa

SILVER_SCHEMA = pa.schema([
    ("station_id", pa.string()),
    ("num_bikes_available", pa.int64()),
    ("num_docks_available", pa.int64()),
    ("snapshot_ts", pa.timestamp("s")),
])

def parse_snapshot(readable_file):
    doc = json.loads(readable_file.read_utf8())
    for st in doc.get("data", {}).get("stations", []):
        yield {**st, "last_updated": doc.get("last_updated")}

def valid_station(rec):
    return rec.get("station_id") is not None

def to_silver(rec):
    return {
        "station_id": str(rec["station_id"]),
        "num_bikes_available": int(rec.get("num_bikes_available", 0)),
        "num_docks_available": int(rec.get("num_docks_available", 0)),
        "snapshot_ts": rec.get("last_updated"),
    }

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with beam.Pipeline() as p:   # DirectRunner by default = runs on your laptop
        (p
         | "Match"   >> fileio.MatchFiles(args.input)
         | "Read"    >> fileio.ReadMatches()
         | "Parse"   >> beam.FlatMap(parse_snapshot)     # one file -> many stations
         | "Valid"   >> beam.Filter(valid_station)
         | "Silver"  >> beam.Map(to_silver)
         | "Write"   >> beam.io.WriteToParquet(args.output, SILVER_SCHEMA))

if __name__ == "__main__":
    run()
```

Expanded: note `FlatMap(parse_snapshot)` is exactly the `map` vs `flatMap` case: one Bronze snapshot file in, ~2,500 station records out.

---

# Demo, part 3: Beam → local Postgres, then AWS DMS (blocked)

Q. What was Plan B?

A. (Evan) He wanted to teach migration services anyway. "One of the things that I didn't manage to cover when I was doing AWS… is AWS DMS." Since ADF had already copied S3 → Azure, he wanted to "complete the trifecta" with DMS. Taking data from Azure SQL would have meant reprovisioning it, so he went **local Postgres → DMS → S3** instead.

Steps:

| # | Step | Result |
|---|---|---|
| 1 | Created S3 bucket `citibike-nyc-dms-demo` (public access not blocked; the data is public anyway) | OK |
| 2 | In `psql`: `CREATE DATABASE citibike`, then a `citibike_bronze` table (id, source_file, feed_type, ingested_at, payload `JSONB`) | OK |
| 3 | AI-written Beam job `beam_bronze_to_postgres.py` loads Bronze JSON into Postgres | `psycopg2` failed to build. Fixed by installing `libpq-dev` and `build-essential` (C headers), then fixing the Postgres user/password env vars |
| 4 | `SELECT * FROM citibike_bronze` | Looked blank/garbled: printing a big `JSONB` payload for every row floods the terminal. Data was there (**1,427** Bronze records) |
| 5 | DMS: no RDS needed since the target is S3. Create IAM role + policy, create a **target endpoint** (engine: Amazon S3, role ARN, not bucket ARN) | Console showed no S3 option; CLI said his user **isn't authorized to create the endpoint**. `attach-user-policy` also denied. Hard blocker, and the company admin couldn't help that day |

```sql
-- from the class demo (not exact)
CREATE DATABASE citibike;
\c citibike
CREATE TABLE IF NOT EXISTS citibike_bronze (
    id           BIGSERIAL PRIMARY KEY,
    source_file  TEXT UNIQUE NOT NULL,
    feed_type    TEXT,
    ingested_at  TIMESTAMPTZ DEFAULT now(),
    payload      JSONB
);
-- check without dumping the huge JSON payloads:
SELECT feed_type, COUNT(*) FROM citibike_bronze GROUP BY feed_type;
```

```python
# from the class demo (not exact)
import argparse, json, os, pathlib
import apache_beam as beam
import psycopg2

def read_bronze_json(path):
    p = pathlib.Path(path)
    yield {"source_file": str(p), "feed_type": p.parent.name, "payload": p.read_text()}

class WriteBronzeToPostgres(beam.DoFn):
    def setup(self):
        self.conn = psycopg2.connect(dbname="citibike", user=os.environ["PGUSER"],
                                     password=os.environ["PGPASSWORD"], host="localhost")
    def process(self, batch):
        with self.conn.cursor() as cur:
            for r in batch:
                cur.execute("""
                    INSERT INTO citibike_bronze (source_file, feed_type, payload)
                    VALUES (%s, %s, %s::jsonb)
                    ON CONFLICT (source_file) DO UPDATE
                    SET feed_type = EXCLUDED.feed_type,
                        payload   = EXCLUDED.payload
                """, (r["source_file"], r["feed_type"], r["payload"]))
        self.conn.commit()
    def teardown(self):
        self.conn.close()

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bronze-root", default="data/bronze")
    args, beam_args = parser.parse_known_args()
    files = [str(f) for f in pathlib.Path(args.bronze_root).rglob("*.json")]
    with beam.Pipeline(argv=beam_args) as p:
        (p
         | "CreateFileList" >> beam.Create(files)
         | "ReadJSON"       >> beam.FlatMap(read_bronze_json)
         | "Batch"          >> beam.BatchElements(min_batch_size=50, max_batch_size=500)
         | "WritePostgres"  >> beam.ParDo(WriteBronzeToPostgres()))

if __name__ == "__main__":
    run()
```

Expanded: things Evan explained or wondered about in this code:

| Piece | Meaning |
|---|---|
| `argparse` | Adds command-line options: `python beam_bronze_to_postgres.py --bronze-root data/bronze`. `parser.add_argument("--bronze-root")` is "like writing it out" |
| `ParDo` | "Parse and do", Evan's reading. Officially **parallel do**: run a custom `DoFn` on every element |
| `BatchElements` | Groups records into chunks so each DB round trip inserts many rows |
| `ON CONFLICT (source_file) DO UPDATE` | An **upsert**. Re-running the job updates rows instead of duplicating them (idempotent) |
| `EXCLUDED` | Evan couldn't see where it was defined. It's a Postgres built-in: the row you **tried** to insert. `SET payload = EXCLUDED.payload` means "take the new value" |
| `psycopg2` build error | The non-binary package compiles C code and needs `libpq-dev`. `pip install psycopg2-binary` avoids it |

---

# Demo, part 4: STS from S3 to GCS (it finally worked)

Q. How did the STS transfer go?

A. (Evan, demo) In the working project he created a GCS bucket `citibike-bronze`, set the project and application-default credentials (now `billingEnabled: true`), and enabled the Storage Transfer API. Then:

| # | Step | Outcome |
|---|---|---|
| 1 | STS → Create transfer job. First tried **"S3-compatible"** source | Needs an **agent pool** ("agents are containerized applications that move data to and from POSIX file systems or from S3 compatible storage"). Went back |
| 2 | Source type **Amazon S3** (not S3-compatible), batch mode, bucket `citibike-nyc-pipeline`, auth by **IAM role for identity federation**, destination `citibike-bronze`, run once now | **Access denied**: he had reused the DMS role ARN |
| 3 | Created a proper IAM role in AWS that trusts Google's STS service account (federated identity, subject ID), plus S3 read permissions | 403s on the GCP side until the quota project was set; then a 200 |
| 4 | Created the job again | Queued and ran (2.68 of 4.24 GB copied) but **permission denied** errors, and nothing showed in the bucket |
| 5 | The AWS policy was too narrow (only the bronze prefix). Re-ran with a less restrictive policy | **Success**: deeply nested JSON files in GCS |

Evan: "After all that, we have finally got our S3 data migrated into GCS… That was a real mess, but of course it's instructive… It's going to be a source of frustration when migrating from one cloud platform to another."

```bash
# standard gcloud syntax for the same job
gcloud transfer jobs create s3://citibike-nyc-pipeline gs://citibike-bronze \
    --source-creds-file=aws-role.json        # {"roleArn": "arn:aws:iam::<acct>:role/<sts-role>"}
gcloud transfer jobs list
gcloud transfer operations list --job-names=<JOB_NAME>
gcloud storage ls -r gs://citibike-bronze/ | head
```

Expanded: STS cross-cloud auth in plain words:

| Piece | Where | Purpose |
|---|---|---|
| Google STS service account (`project-<num>@storage-transfer-service.iam.gserviceaccount.com`) | GCP | The identity that does the copy |
| Its **subject ID** | GCP → used in AWS | Goes in the AWS role's trust policy (`accounts.google.com:sub`) |
| AWS IAM role with a **web identity** trust | AWS | Lets Google assume it, no access keys needed |
| S3 policy on that role: `s3:ListBucket`, `s3:GetObject` on the **whole path you copy** | AWS | Too narrow a prefix = "permission denied" with a partial job |
| `roles/storage.objectAdmin` (or similar) for the STS service account on the bucket | GCP | Lets STS write into GCS |

---

# Migration vs transformation

Q. What does a migration tool do?

A. (Evan, from Training 35's follow-up) "At the end of the day, what you are doing with a migration tool is that you are taking data from one place and you are making a copy of it in another place and that copy is expected to be complete and correct and unmodified. So there is no transformation step if you are using STS or DMS." Transform afterwards, in a separate step.

---

# Profile narratives

Q. Can one project use both Databricks and Snowflake? (feedback to a student)

A. (Evan) "There's no reason to do your processing in Databricks and your reporting in Snowflake. Databricks is perfectly capable of doing reporting." The only convincing stories: your team used Databricks and **another team / business unit** used Snowflake, or a **joint project with another company** that used Snowflake. Otherwise drop Snowflake from the narrative. (The student's newest profile no longer lists it.)

---

Q. How do you talk about Spark and Kafka in a cloud project?

A. (Evan) "If you just straight mention Spark and Kafka, the implication is that you're using those on prem." If the project used **AWS Secrets Manager**, it's a Databricks-on-AWS project, so adapt everything to AWS:

| Plain tool | Say this on AWS | Note |
|---|---|---|
| Spark | **PySpark on EMR Serverless** (or Glue) | If the profile specifically says Spark, EMR Serverless |
| Kafka | **Amazon MSK** | "MSK is actual Kafka just running as a managed service". Kinesis is the other option |
| On-prem migration source | On-prem Kafka / Flink is fine | When the story is a migration **from** an on-prem cluster |

---

Q. What tool would a Hadoop → BigQuery migration use? (feedback to a student with a PayPal profile)

A. (Evan) The source was **Hive**, which makes sense. The answer he wanted was the tool from today: **STS**. "DMS is the AWS service. In GCP, we've been trying to wrestle with STS, storage transfer service… Azure also has Azure DMS, but on GCP, it's called STS." Everyone with the PayPal GCP migration project should review the working STS section (Demo, part 4 above), because "its transfer from S3 into GCS is going to be important for your profile."

Expanded: a typical Hive → BigQuery story: copy Hive's underlying files (ORC/Parquet) from HDFS to GCS (STS with agents, or `DistCp`), load them into BigQuery (`bq load` or the BigQuery Data Transfer Service), validate row counts (Data Validation Tool), and move Spark jobs to **Dataproc**.

---

Q. Bronze/Silver/Gold or Raw/Curated/Semantic? (a student's playbook used the second set)

A. (Evan) "Bronze, silver, and gold are the most common terms that you hear even in interviews." First-round interviewers are often non-technical and have a checklist that says bronze/silver/gold, so they may not connect the other names. "Bronze, silver, and gold are perfectly proper terms. There's nothing informal about them." A sharp technical second-round interviewer will know raw/curated/semantic means the same thing.

| Medallion | Alternative names | Contents |
|---|---|---|
| Bronze | Raw, landing | Data exactly as ingested |
| Silver | Curated, cleansed, conformed | Flattened, typed, validated, deduplicated |
| Gold | Semantic, presentation, consumption | Star schema or business-question tables |

---

# Interview-ready from today

| Question | Your one-line answer |
|---|---|
| What is Cloud Dataflow? | GCP's fully managed, autoscaling service for running Apache Beam pipelines, batch or streaming. Same role as Glue or a Databricks notebook |
| What is Apache Beam? | A unified programming model for batch and streaming. You write the pipeline once and pick a runner (Direct, Dataflow, Spark, Flink) |
| Dataflow vs Dataproc? | Dataflow = serverless Beam. Dataproc = managed Spark/Hadoop clusters (plus serverless Spark). Choose Dataproc to reuse existing Spark code |
| What is BigQuery and why was it special? | The first serverless SQL data warehouse: no cluster, cheap storage, billed by bytes queried |
| `map` vs `flatMap`? | Map is one-to-one; flatMap returns 0..n outputs per input and flattens nested collections |
| S3 → GCS migration tool? | Storage Transfer Service (STS). DMS is AWS and database-aware; STS moves objects |
| GCP equivalents of Lambda / ECS / MWAA / RDS? | Cloud Run functions / Cloud Run / Cloud Composer / Cloud SQL |
| Should a migration transform data? | No. A migration makes a complete, unmodified copy; transform afterwards in a separate step |
| Medallion layer names? | Bronze/Silver/Gold (most common), also Raw/Curated/Semantic |

---

# Still to add

- Cloud Dataflow on GCP (not just local Beam), the BigQuery star schema, and Looker Studio: done in **Training 35**.
- AWS DMS demo: blocked by permissions today. Evan said "we can find a way to do a DMS job somewhere in the following week."
- Homework: read about **STS** and the general GCP services above; keep working on your capstone.
