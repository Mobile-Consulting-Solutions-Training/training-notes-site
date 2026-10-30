---
title: "Training 35 - Dataflow, BigQuery and Looker Studio"
description: "Dataflow jobs from Bronze to a BigQuery star schema, a latest-snapshot view, and a Looker Studio dashboard."
sidebar:
  order: 35
---

Teacher: Evan Flint

Syllabus Day 36 (per file numbering; Thu Oct 29, 2026). Partly matched the roadmap: Day 36 is **GCP: BigQuery + Pub/Sub**. Evan taught **GCS, Cloud Dataflow (Beam), BigQuery (star schema, views) and Looker Studio**. Pub/Sub was **not** covered, and the Dataflow part is really roadmap Day 37 content.

Source: class notes.

**Code note:** the code below is written from the class demo plus standard Apache Beam / BigQuery / gcloud syntax. It is not an exact copy of Evan's code.

---

# Capstone presentations: dates

> **Practice run: Monday, Nov 2.** **Final capstone presentations: Friday, Nov 6.**
>
> A student asked for a chance to run projects past Evan before the presentations next week. Evan checked the syllabus (tomorrow is ML fundamentals + MLflow; days 44–45 are flexible extension and marketing) and agreed: "On Monday, do a practice run. And then on Friday, we can do the real thing."

| Item | Detail |
|---|---|
| Monday Nov 2 | Practice run. Bring your project to "a presentable point", or at least have what you want to share ready |
| Friday Nov 6 | The real presentations |
| Requirements (from Training 34) | Ingestion into object storage → Bronze/Silver/Gold processing → visualization with a tool beyond the built-in Databricks charts. Single cloud is fine |
| Interview tip on dashboards | Interviewers ask about Looker/BI "every once in a while", but not deeply. They care more about BigQuery and Dataflow |

---

# Today at a glance

| # | What happened |
|---|---|
| 1 | Check-ins. Using AI on top of a pipeline (SQL query → prompt vs. RAG). Presentation practice day agreed (Monday) |
| 2 | Aerospike and Couchbase in some profiles: Evan says remove them |
| 3 | Break (early) |
| 4 | Demo: Dataflow **Bronze → Silver** (`bronze_to_silver.py`), test with DirectRunner, then run on **DataflowRunner** |
| 5 | Every cloud is the same pipeline with different tool names |
| 6 | Break |
| 7 | BigQuery: create `dim_station` + `fact_station_snapshot`. Dataflow **Silver → Gold** writes to BigQuery (bug fix, then success). Station status Bronze → Silver → fact table. Q&A on job graph steps and branching |
| 8 | Key-value logic (`CombinePerKey`), latest-snapshot view with `QUALIFY ROW_NUMBER()`, analytics queries |
| 9 | Break |
| 10 | Looker Studio dashboard: 3 scorecards and a bubble map (after a geo-field struggle) |
| 11 | Cleanup with an AI agent. Narrative Q&A: migrations don't transform; streaming risk-assessment story; company-internal tools |

---

# Using AI on top of a pipeline

Q. How should a data app feed new data to an AI model? (a student)

A. (Evan) "In a data app, in most cases, what I would actually recommend is just doing a SQL query and feeding the results to the AI via a prompt… You should really only do the vector database RAG thing if you need to persistently ask the AI about a particular subject." Example: when a new batch lands, programmatically run a SQL query and put the results in a prompt like "generate a new visualization using this data".

| Approach | When |
|---|---|
| SQL query → results in the prompt | Structured data, one-off questions or generated charts. Simple, cheap, exact |
| RAG (embeddings + vector DB) | Lots of unstructured text you keep asking about over time |

---

# Aerospike and Couchbase in profiles

Q. Why are Aerospike and Couchbase in my profile? (two students)

A. (Evan) Both are **NoSQL document databases** (Aerospike also mentions graph and vector). They got in through the generated **skills list**, which "escaped my manual removal because there are no bullet points in the project that say anything about those". "There's no reason why you would use both of those in the same project." His advice: **remove both** from the profile. "I found out what Aerospike is just now, right? So obviously there is zero demand in the job market for it." He updated the affected profiles and sent them to the program coordinator.

Expanded: a student's AI search suggested **Bigtable** (GCP's wide-column NoSQL for low-latency lookups) or **Firebase** instead. Evan: Firebase is fine, but it's built for customer-facing apps; for analytics you'd ingest from it into BigQuery.

| GCP NoSQL | Type | Use |
|---|---|---|
| **Bigtable** | Wide-column (like HBase) | Very high-throughput, low-latency key lookups (fraud features, time series) |
| **Firestore / Firebase** | Document (JSON) | Mobile/web app back ends |
| **Memorystore** | In-memory (Redis) | Caching |

---

# Demo plan

Q. What was the plan?

A. (Evan) Starting from the S3 data migrated into GCS yesterday with STS ("do remember that name since it's the migration tool that I have most extensively demonstrated"): one **Dataflow** job moves Bronze → Silver in GCS, another Dataflow job moves Silver → Gold in **BigQuery**, organize a **star schema** there, and visualize in **Looker Studio**. He had verified all GCP permissions before class.

```
GCS bronze (raw GBFS JSON, from STS)
  │  Dataflow job 1: bronze_to_silver.py         (station_information)
  │  Dataflow job 3: bronze_status_to_silver.py  (station_status)
  ▼
GCS silver (JSON Lines)
  │  Dataflow job 2: silver_to_gold.py           → BigQuery dim_station
  │  Dataflow job 4: silver_status_to_gold.py    → BigQuery fact_station_snapshot
  ▼
BigQuery citibike dataset: dim_station, fact_station_snapshot, v_station_latest, v_station_map
  ▼
Looker Studio: scorecards + bubble map
```

---

# Dataflow setup: service account and permissions

Q. What setup did Dataflow need?

A. (Evan, demo) Environment variables for the **project number** and the default **Compute Engine service account** (the Dataflow workers run as it), and checking it has `roles/dataflow.worker` and `roles/storage.objectAdmin`.

```bash
# from the class demo (not exact)
export PROJECT_ID=<your-project-id>
export REGION=us-central1
export BUCKET=<your-bucket>
export PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
export WORKER_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
echo $PROJECT_NUMBER $WORKER_SA

gcloud services enable dataflow.googleapis.com bigquery.googleapis.com storage.googleapis.com

# check / grant the worker roles
gcloud projects get-iam-policy "$PROJECT_ID" \
  --flatten="bindings[].members" --filter="bindings.members:$WORKER_SA" \
  --format="table(bindings.role)"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$WORKER_SA" --role="roles/dataflow.worker"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$WORKER_SA" --role="roles/storage.objectAdmin"
```

| Role | Why |
|---|---|
| `roles/dataflow.worker` | Lets the worker VMs run Dataflow work items |
| `roles/storage.objectAdmin` | Read Bronze, write Silver, use temp/staging folders in GCS |
| `roles/bigquery.dataEditor` (+ `jobUser`) | Needed when the job writes to BigQuery |

---

# Dataflow job 1: Bronze → Silver

Q. What does `bronze_to_silver.py` do?

A. (Evan, demo) "Just a regular Beam script." Parse each Bronze document inside a `try/except`, pull `data.stations`, and for each station get the ID, latitude and longitude. "If any of these are None… continue", meaning "go back to the beginning of the for loop" for the next station. Then `yield` a dictionary with basic type conversions. The pipeline reads the input, `FlatMap`s the stations out, `Map`s each row to a JSON string, and writes Silver.

```python
# from the class demo (not exact)
import argparse, json, logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

def extract_stations(line):
    try:
        doc = json.loads(line)
    except json.JSONDecodeError:
        return                                    # invalid document: skip it
    stations = doc.get("data", {}).get("stations", [])
    for st in stations:
        sid, lat, lon = st.get("station_id"), st.get("lat"), st.get("lon")
        if sid is None or lat is None or lon is None:
            continue                              # skip to the next station
        yield {
            "station_id": str(sid),
            "name": st.get("name"),
            "lat": float(lat),
            "lon": float(lon),
            "capacity": int(st.get("capacity") or 0),
            "last_updated": doc.get("last_updated"),
        }

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    known_args, pipeline_args = parser.parse_known_args()
    options = PipelineOptions(pipeline_args)      # --runner, --project, --region, ... go here

    with beam.Pipeline(options=options) as p:
        (p
         | "ReadBronzeJSON"     >> beam.io.ReadFromText(known_args.input)
         | "ExtractStations"    >> beam.FlatMap(extract_stations)
         | "ToJSON"             >> beam.Map(json.dumps)
         | "WriteSilverJSONL"   >> beam.io.WriteToText(known_args.output,
                                                       file_name_suffix=".jsonl",
                                                       num_shards=1))

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()
```

Expanded: `parse_known_args()` (Evan wasn't sure what "known args" means) splits the command line in two: **known_args** are the options you declared (`--input`, `--output`); **pipeline_args** are everything else (`--runner`, `--project`, `--region`, …), which get passed to Beam's `PipelineOptions`. That's how one script runs locally or on Dataflow without code changes.

---

Q. Is Beam its own engine?

A. (Evan) "Beam is going to connect to cloud Dataflow's execution engine in order to execute this code. We don't actually know what the execution engine exactly is because it's not public knowledge… it's effectively based on Spark… you should not consider Beam to be its own execution engine; you should consider it to be an API."

Expanded: correct that Beam is an API, not an engine. But Dataflow's engine is **not Spark**: it's Google's own service, descended from Google's internal FlumeJava and MillWheel systems (the Dataflow paper that Beam came from). Beam can *also* run on Spark via the SparkRunner. In an interview: "Beam is the SDK; Dataflow is Google's managed runner."

---

Q. How do you test locally, then run in the cloud?

A. (Evan, demo) Download one sample Bronze file with `gcloud storage cp`, run the script with `--runner DirectRunner` ("the way that Beam can actually execute its code on my own local machine"), then switch to `--runner DataflowRunner`. The local run hit dependency problems first (an `AttributeError` about the array API and a NumPy 2.x incompatibility; fixed by pinning versions and reinstalling pandas). Testing locally first means a failure "costs me $0 and 0 cents".

```bash
# from the class demo (not exact)
SAMPLE_URI=$(gcloud storage ls -r "gs://$BUCKET/bronze/**station_information*.json" | head -1)
gcloud storage cp "$SAMPLE_URI" /tmp/citibike_sample.json
mkdir -p /tmp/citibike_silver

python bronze_to_silver.py \
  --input /tmp/citibike_sample.json \
  --output /tmp/citibike_silver/stations \
  --runner DirectRunner

python bronze_to_silver.py \
  --input "gs://$BUCKET/bronze/**station_information*.json" \
  --output "gs://$BUCKET/silver/station_information/stations" \
  --runner DataflowRunner \
  --project "$PROJECT_ID" --region "$REGION" \
  --temp_location "gs://$BUCKET/dataflow/temp" \
  --staging_location "gs://$BUCKET/dataflow/staging" \
  --job_name citibike-bronze-to-silver \
  --worker_machine_type e2-standard-2 \
  --num_workers 1 --max_num_workers 2 \
  --save_main_session
```

| Flag | Meaning |
|---|---|
| `--runner DataflowRunner` | Submit to Cloud Dataflow instead of running locally |
| `--temp_location` / `--staging_location` | GCS folders for temp files and the uploaded code/packages |
| `--worker_machine_type e2-standard-2` | Compute Engine VM type for the workers (2 vCPU) |
| `--num_workers` / `--max_num_workers` | Starting workers and the autoscaling ceiling (also a cost cap) |
| `--save_main_session` | Pickles global imports/variables so worker VMs can use them (Evan wasn't sure; this is what it does) |

---

Q. What did the job look like in the console?

A. (Evan, demo) Dataflow → Jobs showed `citibike-bronze-to-silver` with a graph: **ReadBronzeJSON** (green when done) → **ExtractStations** → **StandardizeRecords** → **WriteSilverJSONL**. It looked stuck at first ("stage may be stuck or running slowly"), then jumped from 0 to 100%. Each job took **about 4–5 minutes** (mostly worker startup). Silver showed up in GCS (station information ~532 KB of JSON plus station snapshots). The job was "Done".

---

# The big picture: same pipeline, different names

Q. So the pipeline is the same as before? (a student)

A. (Teacher's definition) "These are just different tools to do the same thing… In every single situation, what we are doing is we are building out a pipeline where we ingest into some kind of object storage and we use some kind of data processing technology to move the data up the same series of layers. And then at the top layer, it's probably a data warehouse. And that's where we power our analytics and link any kind of visualization and AI tool to."

| Platform | Ingest into | Process with | Gold / warehouse | Visualize |
|---|---|---|---|---|
| On-prem | HDFS | Spark | Hive | (any BI tool) |
| AWS | S3 | Glue or EMR | Redshift | QuickSight / Streamlit |
| Azure | ADLS (via ADF) | Databricks or Synapse | Databricks or Synapse | Power BI |
| GCP | GCS (via STS) | Dataproc or Dataflow | BigQuery | Looker Studio |

Expanded: Evan's framing of the layers: Bronze "to preserve your initial data", Silver "to analyze that bronze data and make it workable", Gold "to either make it into a star schema or make it into task-specific tables that are supposed to answer specific business questions". And the reason it matters: "it is those analytics and how they help drive the decision making process of the business that makes data engineers valuable." The demo is "deliberately simplified for the purposes of education"; real Silver/Gold logic depends on the business case.

---

# BigQuery: the Gold layer

Q. Why is BigQuery so important for interviews?

A. (Evan) "BigQuery is the technology that gets asked about on GCP more than any other." But "it's just another data warehouse, just like Redshift, just like Synapse, just like Hive… BigQuery made a lot of waves when it was first released because it was the first serverless data warehouse… Everybody does it these days. But because of the hype that BigQuery got, it still looms large in people's minds."

| BigQuery term | Meaning | Other platforms |
|---|---|---|
| Project | Billing + permission container | AWS account / Azure subscription |
| Dataset | Group of tables in a location | Schema / database |
| Table / View | As usual | As usual |
| Slot | Unit of query compute | Redshift RPU |
| On-demand pricing | Pay per TB scanned | Athena, Synapse serverless |

---

Q. How did he create the star schema?

A. (Evan, demo) Opened BigQuery from the console search ("just literally go here and type BigQuery"; he also enabled the Gemini-in-BigQuery API when prompted). The AI pointed out that `dim_station` can be filled right away, but "we cannot build a meaningful availability fact table from station metadata alone", so station **status** also had to be processed. He chose to "keep the data authentic". Two `CREATE TABLE IF NOT EXISTS` statements in the SQL editor: `dim_station` and `fact_station_snapshot`, "just like we had in Redshift".

```sql
-- from the class demo (not exact)
CREATE SCHEMA IF NOT EXISTS citibike;     -- a BigQuery "dataset" (bq mk --dataset also works)

CREATE TABLE IF NOT EXISTS citibike.dim_station (
  station_id     STRING NOT NULL,
  station_name   STRING,
  latitude       FLOAT64,
  longitude      FLOAT64,
  capacity       INT64,
  last_updated   TIMESTAMP
);

CREATE TABLE IF NOT EXISTS citibike.fact_station_snapshot (
  station_id           STRING NOT NULL,
  snapshot_ts          TIMESTAMP,
  bikes_available      INT64,
  docks_available      INT64,
  is_renting           BOOL,
  is_returning         BOOL
)
PARTITION BY DATE(snapshot_ts)
CLUSTER BY station_id;
```

Expanded: `PARTITION BY` and `CLUSTER BY` are the BigQuery cost levers from the roadmap. Filters on `snapshot_ts` skip whole daily partitions, and clustering by `station_id` reads fewer blocks for per-station queries. Fewer bytes scanned = a smaller bill.

---

# Dataflow job 2: Silver → Gold (BigQuery)

Q. What does `silver_to_gold.py` do?

A. (Evan, demo) Defines the BigQuery schema, a `parse_station` function (builds a row with proper data types, run by `Map` on every element), and `newest_station(a, b)`, which "returns A if A's last updated is greater than B's, else B", so it keeps the most recently updated record. Pipeline: read Silver → parse → filter out `None` → **key by station** → **CombinePerKey(newest_station)** → **drop keys** with `beam.Values()` → `WriteToBigQuery`.

```python
# from the class demo (not exact)
import argparse, json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

SCHEMA = ("station_id:STRING,station_name:STRING,latitude:FLOAT,"
          "longitude:FLOAT,capacity:INTEGER,last_updated:TIMESTAMP")

def parse_station(line):
    try:
        r = json.loads(line)
        return {
            "station_id": str(r["station_id"]),
            "station_name": r.get("name"),
            "latitude": float(r["lat"]),
            "longitude": float(r["lon"]),
            "capacity": int(r.get("capacity") or 0),
            "last_updated": r.get("last_updated"),
        }
    except (KeyError, ValueError, TypeError):
        return None

def newest_station(records):
    # CombinePerKey passes an iterable of values for one key
    return max(records, key=lambda r: r.get("last_updated") or 0)

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--table", required=True)        # project:citibike.dim_station
    known, beam_args = parser.parse_known_args()

    with beam.Pipeline(options=PipelineOptions(beam_args)) as p:
        (p
         | "ReadSilver"        >> beam.io.ReadFromText(known.input)
         | "ParseRecords"      >> beam.Map(parse_station)
         | "RemoveInvalid"     >> beam.Filter(lambda x: x is not None)
         | "KeyByStation"      >> beam.Map(lambda x: (x["station_id"], x))
         | "LatestPerStation"  >> beam.CombinePerKey(newest_station)
         | "RemoveKeys"        >> beam.Values()
         | "WriteToBigQuery"   >> beam.io.WriteToBigQuery(
                known.table,
                schema=SCHEMA,
                method=beam.io.WriteToBigQuery.Method.FILE_LOADS,
                create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
                write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE))

if __name__ == "__main__":
    run()
```

| Write option | Meaning |
|---|---|
| `Method.FILE_LOADS` | Stage files in GCS, then run a BigQuery **load job** (cheap, batch). Alternatives: streaming inserts, Storage Write API |
| `CREATE_NEVER` | Table must already exist (we created it in SQL) |
| `WRITE_TRUNCATE` | Replace the table's contents each run (idempotent full refresh). `WRITE_APPEND` adds rows |

**The bug:** the first Dataflow run failed at stage 5 (LatestPerStation): `newest_station() missing 1 required positional argument: 'b'`. The two-argument `newest_station(a, b)` form doesn't fit how `CombinePerKey` calls a plain function (it passes **one iterable** of values). The AI's fix (plus an indentation fix) was a one-argument version like the one above, or wrapping the pairwise version: `lambda vals: functools.reduce(newest_station, vals)`. He **tested locally first**, then resubmitted, which creates a **new** job rather than restarting the failed one.

Cost check: the Dataflow job's **Cost** tab showed **$0.00** (about 0.0037 vCPU-hours). Job metrics showed one worker scaling up briefly and back down, which helps when troubleshooting.

---

Q. Why add a key and then remove it? (a student)

A. (Teacher's definition) "It's because we're using the combine per key method… anything that's got per key in it is going to be designed to operate on key and value type data… after we finish using combine per key, we remove the keys because we don't need them anymore."

Expanded: Evan tied it back to older tools. In the **Spark RDD API** (before DataFrames) you had `groupByKey`, `reduceByKey`, `combineByKey`; "any kind of ByKey method assumes that you are going to have a collection which has exactly two values in it, and it will treat the first of those values as a key." Kafka messages also come as key + value. "This is a method that has been going on in data engineering for many, many years."

| Step | Data shape |
|---|---|
| After `ParseRecords` | `{station_id: "72", ...}` (many per station) |
| After `KeyByStation` | `("72", {...})` tuples |
| After `CombinePerKey` | `("72", {newest record})` (one per station) |
| After `Values()` | `{newest record}` (ready for BigQuery) |

Small correction: Evan said the Kafka key is "basically Kafka's offset". The **offset** is a separate field (the message's position in the partition). The **key** is set by the producer and decides which partition the message goes to.

---

Q. Is every pipe step its own stage in the Dataflow graph? Should we combine steps? (a student)

A. (Evan) "It's a one to one between the pipeline that we define in code and the stages that we have in Dataflow." Keep the individual steps: "This is essentially a directed acyclical graph, just like in Spark execution and just like in Airflow… we cannot go back and revisit this step." There's "no real reason to combine the steps". Spark groups narrow transformations with lazy evaluation; Evan didn't think Beam does.

Expanded: Dataflow actually does something similar: its optimizer **fuses** consecutive steps (like Spark stages) so they run together on the same worker. The graph still shows your named steps, which is why clear labels help monitoring and debugging.

---

Q. Can a Beam pipeline branch? (a student thinking of per-market kill switches)

A. (Evan) It can, "but it's not super considered a good idea". A valid case: the same Silver data goes to BigQuery **and** to a NoSQL database for a customer-facing app, with different transforms. But "if it's me doing it, then I would want a dedicated pipeline for the data warehouse and a separate dedicated pipeline for the NoSQL database". Reason: **modularity**. If one target must be decommissioned, two jobs means turning off one schedule; one combined job means "rewrite the code and submit a pull request and get it approved and take it through the stages of productionizing the code".

For the kill-switch case: don't put the switch in Silver → Gold. Turn the source off **at or before Bronze ingestion**, and design downstream steps so they keep working if that source's Bronze data isn't there.

Expanded: in Beam, branching is just applying two transforms to the same PCollection; bad records are usually routed with **tagged outputs** (a "dead-letter" output) so they don't block the main path.

---

# Station status: Bronze → Silver → fact table

Q. How was the fact table filled?

A. (Evan, demo) The first `SELECT * FROM fact_station_snapshot` returned no data: the job had only filled `dim_station`. Station status hadn't been moved to Silver yet, so two more Dataflow jobs:

| Job | Does |
|---|---|
| `bronze_status_to_silver.py` | Read the status docs, get a timestamp string, for each station get the ID, bikes available and docks available, serialize to JSON, write Silver |
| `silver_status_to_gold.py` | Read Silver, map to the BigQuery schema, key by (station, snapshot), deduplicate with `CombinePerKey`, `Values()`, write to `fact_station_snapshot` |

Silver validation counted **17,633** status records. The Gold job took about 4 minutes.

```bash
# from the class demo (not exact): validate Silver from the CLI
gcloud storage ls "gs://$BUCKET/silver/station_status/"
gcloud storage cat "gs://$BUCKET/silver/station_status/*.jsonl" | head -5
gcloud storage cat "gs://$BUCKET/silver/station_status/*.jsonl" | wc -l
gcloud dataflow jobs list --region "$REGION"
```

Note: run these in the terminal that has your environment variables. In a new terminal, `$BUCKET` is empty and the commands look "malformed".

---

# BigQuery analytics and views

Q. What did the data look like?

A. (Evan, demo) Summary query: **2 snapshots, 17,149 rows, 2,519 unique stations**, first snapshot in **1970**, last in 2026, **235,884** total bikes observed. "Same data that we saw in Redshift. Same data that we saw in Synapse… Databricks… Fabric."

```sql
-- from the class demo (not exact)
SELECT COUNT(DISTINCT snapshot_ts)   AS snapshots,
       COUNT(*)                      AS rows_loaded,
       COUNT(DISTINCT station_id)    AS unique_stations,
       MIN(snapshot_ts)              AS first_snapshot,
       MAX(snapshot_ts)              AS last_snapshot,
       SUM(bikes_available)          AS total_bikes_observed
FROM citibike.fact_station_snapshot;
```

Expanded: a first snapshot in **1970** means a timestamp of `0` (or null converted to epoch zero), i.e. a record with a missing `last_reported`. A Silver/Gold check should reject or null those. Same family of anomaly as the "1 station snapshot" in Training 31.

---

Q. How did he build the dashboard view?

A. (Evan, demo) A **view** `v_station_latest`: take each station's newest snapshot with `QUALIFY ROW_NUMBER() OVER (PARTITION BY station_id ORDER BY snapshot_ts DESC) = 1`, join to `dim_station` for name, coordinates and capacity, and compute a rounded availability percent. "This is using ELT logic by having CREATE OR REPLACE VIEW AS SELECT."

```sql
-- from the class demo (not exact)
CREATE OR REPLACE VIEW citibike.v_station_latest AS
WITH latest AS (
  SELECT *
  FROM citibike.fact_station_snapshot
  WHERE TRUE
  QUALIFY ROW_NUMBER() OVER (PARTITION BY station_id ORDER BY snapshot_ts DESC) = 1
)
SELECT f.station_id,
       d.station_name,
       d.latitude,
       d.longitude,
       d.capacity,
       f.snapshot_ts,
       f.bikes_available,
       f.docks_available,
       ROUND(SAFE_DIVIDE(f.bikes_available, d.capacity) * 100, 1) AS availability_pct
FROM latest f
JOIN citibike.dim_station d USING (station_id);

SELECT * FROM citibike.v_station_latest LIMIT 20;
```

Expanded: Evan read `QUALIFY` as making sure "we only got valid data". What it really does: **filter on a window function**, the way `HAVING` filters on an aggregate. Without it you'd need a subquery (`WHERE rn = 1`). BigQuery, Snowflake and Databricks support it; Postgres and SQL Server don't.

| Clause | Filters on |
|---|---|
| `WHERE` | Raw row values |
| `HAVING` | Aggregates after `GROUP BY` |
| `QUALIFY` | Window function results (e.g. `ROW_NUMBER() = 1` for "latest per key") |

---

Q. What analytics queries did he run?

A. (Evan, demo)

| Query | Result |
|---|---|
| Stations with the lowest availability (`ORDER BY bikes_available ASC`) | First 20 all had zero bikes |
| Hourly availability trend (`GROUP BY` hour) | Zero bikes and docks for every hour, jumping from 1970 to May 2026. Evan: "the results of this query don't seem to be what we're expected… I didn't write the query" |
| Availability by capacity size (`CASE` → small/medium/large) | Station counts and average availability per size class. Worked fine |

```sql
-- from the class demo (not exact)
SELECT CASE WHEN capacity < 20 THEN 'small'
            WHEN capacity < 40 THEN 'medium'
            ELSE 'large' END            AS size_class,
       COUNT(*)                         AS stations,
       ROUND(AVG(availability_pct), 1)  AS avg_availability_pct
FROM citibike.v_station_latest
GROUP BY size_class
ORDER BY stations DESC;
```

Expanded: the hourly query failing is the 1970 problem again. With only 2 real snapshots and some epoch-zero rows, "per hour" has almost nothing to show. Good lesson: check your timestamps before building time-series charts.

---

# Looker Studio dashboard

Q. How do you connect Looker Studio to BigQuery?

A. (Evan, demo) Go to `datastudio.google.com` (now **lookerstudio.google.com**), same Google account. **Create → Blank report → Add data → BigQuery** → project → `citibike` dataset → `v_station_latest` → Add. The fields from the view appear in the Data panel.

Then **three KPI scorecards** (Add a chart → Scorecard):

| Scorecard | Metric | Aggregation |
|---|---|---|
| Total stations | `station_id` | Count distinct (record count also works) |
| Available bikes | `bikes_available` | Sum (display name renamed to "Available bikes") |
| Average availability | `availability_pct` | Average |

A student helped: in the Setup panel, **dimensions** only let you change the name; **metrics** have the aggregation options. Click the small aggregation label (e.g. "SUM") on the **left** of a metric chip to change aggregation or display name; clicking the name itself changes which field it uses. You can select several charts and move them together.

---

Q. How did he get the map to work?

A. (Evan, demo) "For reliable geographic plotting, create a geographic point in BigQuery rather than relying on Looker Studio." First try: a view `v_station_map` with `ST_GEOGPOINT(longitude, latitude) AS station_location`, added as a second data source, then **Google Maps → Bubble map**. It said **"Invalid dimension"** and wouldn't let him pick anything. Fix:

| # | Step |
|---|---|
| 1 | Replace the view with a **text** field `CONCAT(CAST(latitude AS STRING), ',', CAST(longitude AS STRING)) AS map_coordinates` |
| 2 | Resource → **Manage added data sources** → Edit → **Refresh fields** → Apply (Looker caches the old schema; a student once spent 1.5 hours on stale fields) |
| 3 | Change `map_coordinates` type from Text to **Geo → Latitude, Longitude** |
| 4 | Still "invalid metric", so he **deleted the chart and added a new bubble map**. "Sometimes just starting again from the beginning is exactly what you need to do" |
| 5 | Location = `map_coordinates`, Size = `bikes_available`, Color metric = `availability_pct`, Tooltip = `station_name` |

```sql
-- from the class demo (not exact)
CREATE OR REPLACE VIEW citibike.v_station_map AS
SELECT station_id,
       station_name,
       bikes_available,
       availability_pct,
       CONCAT(CAST(latitude AS STRING), ',', CAST(longitude AS STRING)) AS map_coordinates
FROM citibike.v_station_latest;
```

Result: circles sized by bikes available and shaded by availability: "the darker they are, the more available the bikes are in that area" (e.g. 22% light, 100% dark).

Expanded: Looker Studio's Latitude,Longitude field type expects text like `"40.75,-73.99"`, which is why the `CONCAT` version worked. And Evan's view on BI tools: Looker "does the same thing as Power BI… Tableau… Streamlit… Plotly… Seaborn… But because it's a Google product, it connects very seamlessly to BigQuery."

| Looker | What it is |
|---|---|
| **Looker Studio** (formerly Data Studio) | Free, self-service dashboards (what Evan used) |
| **Looker** (core) | Enterprise BI platform with the LookML modeling layer. Google bought Looker in 2019–2020 |

---

# Cleanup

Q. How did he avoid surprise charges?

A. (Evan) He asked an AI coding agent with gcloud access to survey the project and make sure nothing that costs money was left running. "The stuff that we did for our AWS demonstration cost well over a hundred dollars… There are plenty of things that you can do in the cloud that are surprisingly expensive, like in the thousands of dollars… Don't leave it running."

| Resource | Leaves a cost? |
|---|---|
| Finished Dataflow batch jobs | No (workers shut down), but check none are stuck "Running" |
| Streaming Dataflow jobs | Yes, until you drain/cancel them |
| GCS buckets / BigQuery storage | Small storage cost; delete if not needed |
| BigQuery queries | Per TB scanned each time |

---

# Narratives and interview Q&A

Q. Is there a set sequence for an STS migration? Does the data change? (a student)

A. (Evan) STS took over yesterday only because of authentication problems. "What you are doing with a migration tool is that you are taking data from one place and you are making a copy of it in another place and that copy is expected to be complete and correct and unmodified. So there is no transformation step if you are using STS or DMS." Same schema, same row count; "it should ideally be a perfect copy. After you have copied it, you can then apply transformations to it in a separate step." Some migration tools need a SQL source (DMS), others need object storage (STS), but the job is the same. He now has DMS permission but chose to build the pipeline instead.

---

Q. Is a real-time risk-assessment stream a data engineer's job? (a student with a buy-now-pay-later story)

A. (Evan) Computing the decision is a cross-team effort (finance/risk, data scientists, app developers), probably with **machine learning**. "Working on the actual program that makes the calculation… is outside the purview of the data engineer." Likely architecture: the public form → HTTP → a dedicated evaluation server → its result goes to a **producer** (Kafka / Kinesis / Event Hubs) → broker → consumer → Bronze. "Once it is consumed and put into our bronze layer, then it is well and truly within our analytics pipeline." It's streaming because it's time-sensitive: the user wants "that spinny thing to go away". Your job is that the decision data is stored, queryable, reportable and available to compliance, "and that we don't lose any of the information… between when it starts and when it finishes."

| Owned by | Part |
|---|---|
| Web/app developers | The application form |
| Finance/risk + data scientists + software engineers | The approval algorithm (K-nearest neighbors, regression, …) |
| **Data engineers** | Making input data available, and getting decisions + context into the pipeline (stream) and the warehouse (batch) |

---

Q. How much do we need to know about company-internal tools (e.g. PayPal's Gimel, a data-access layer)? (a student)

A. (Evan) "You need to know what they basically are and what they basically do." If asked technical follow-ups: "We ingest the data from it… as far as I was concerned, it's a black box." "That's a completely reasonable perspective to have as a data engineer."

---

Q. Do I need to learn Beam deeply?

A. (Evan) "You should get familiar with Beam if you're going to be talking about GCP in your profile narratives." Otherwise, no: Beam is basically only used in Dataflow. "Focus your data processing stuff on Spark and Databricks, and maybe Snowflake."

---

# Interview-ready from today

| Question | Your one-line answer |
|---|---|
| How do you run a Beam pipeline on GCP? | Same script, `--runner DataflowRunner` plus project, region, temp/staging GCS locations and worker settings. Test first with DirectRunner |
| What runs Dataflow workers and what do they need? | Compute Engine VMs as the default compute service account, with `dataflow.worker`, storage and BigQuery roles |
| How do you write from Beam to BigQuery? | `WriteToBigQuery` with a schema, a method (file loads / streaming / Storage Write API), and create/write dispositions |
| Why key, CombinePerKey, then Values? | Per-key operations need (key, value) pairs; drop the key after the aggregation |
| How do you get the latest row per key in BigQuery? | `QUALIFY ROW_NUMBER() OVER (PARTITION BY key ORDER BY ts DESC) = 1` |
| How do you cut BigQuery cost? | Partition and cluster tables, select only needed columns, check bytes before running |
| Should one pipeline feed both a warehouse and a NoSQL store? | Usually two dedicated pipelines, for modularity and easy decommissioning |
| Is the risk-scoring model the data engineer's job? | No. DE makes inputs available and lands decisions in the stream/warehouse; the model belongs to data science/finance/app teams |
| Pipeline on every cloud? | Ingest to object storage → process Bronze/Silver/Gold → warehouse → BI/AI |

---

# Still to add

- **Pub/Sub** (roadmap Day 36) wasn't covered. Expect it, or skip if the schedule moves on.
- Tomorrow (Fri Oct 30): **ML fundamentals and MLflow** per Evan.
- Homework: Evan generated a short homework at the end of class and posted it in the chat and Teams (GCP review; keep working on the capstone and narratives).
- **Monday Nov 2: presentation practice run. Friday Nov 6: final presentations.**
