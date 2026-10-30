---
title: "Training 33 - Fabric Direct Lake and Event Hubs Streaming"
description: "Direct Lake and DAX, a SQL mirroring attempt, and Event Hubs into a Fabric Eventstream, Eventhouse and Real-Time Dashboard."
sidebar:
  order: 33
---

Teacher: Evan Flint

Syllabus Day 34 (per file numbering; Tue Oct 27, 2026). The roadmap had **Synapse + Event Hubs** for today. Synapse was already taught in Training 31, so today was a **second Fabric day** (the roadmap's Day 33 topics: **Direct Lake** and **SQL mirroring**) plus the **Event Hubs** half of today's roadmap topic, connected into Fabric through an Eventstream. Partial match: the Event Hubs part matched; the rest was the Fabric Day 2 content that had been pushed back.

Source: class notes.

**Code note:** the code below is written from the class demo plus standard Fabric / DAX / KQL / Python SDK syntax. It is not an exact copy of Evan's code.

---

# Today at a glance

| # | What happened |
|---|---|
| 1 | **Direct Lake** semantic model: it turned out to be the default, so yesterday's model was already Direct Lake |
| 2 | **DAX** measures (`SUM`, `DIVIDE`) and a Direct Lake report with cards, a bar chart and a line chart |
| 3 | Attempt at **SQL mirroring**: the Azure SQL database had been deleted, so it was restored from a restore point (slow) |
| 4 | Early break while the restore deployed |
| 5 | Managed identity on the SQL logical server (portal → CLI → REST API) |
| 6 | Mirroring blocked: "cannot mirror a SQL database with the managed identity across tenants". Abandoned |
| 7 | **Azure Event Hubs**: namespace, event hub `patient-events`, shared access policies (Send / Listen) |
| 8 | Python producer + consumer with the `azure-eventhub` SDK. Data Explorer view of events |
| 9 | Student question: `while True` loops and graceful shutdown |
| 10 | Break |
| 11 | Fabric **Eventstream** with Event Hubs as the source |
| 12 | **Eventhouse** + **KQL database** destination. KQL queries, a time chart, a **Real-Time Dashboard** |
| 13 | Second destination: lakehouse **bronze** table. Notebook bronze → silver → unified table → three streaming gold tables |
| 14 | Semantic model + DAX measures for streaming gold. Start of a report |
| 15 | Interview prep: an SME session's narrative breakdown and "five questions" document. Next class: GCP or review |

---

# Direct Lake

Q. What is Direct Lake?

A. (Evan) In the semantic model's table properties, **Storage mode** gives two options, **Import** and **Direct Lake**. The model built yesterday "was already Direct Lake ... so we were unwittingly using it yesterday."

Expanded: Direct Lake is a Power BI storage mode only available in Fabric. The semantic model reads the **Delta/Parquet files in OneLake directly** into memory when a visual needs them. Nothing is copied into Power BI, and no SQL query runs against a database on each click.

| Storage mode | How data reaches the report | Freshness | Speed | Cost / limits |
|---|---|---|---|---|
| **Import** | Data is copied into the model on a scheduled refresh | As fresh as the last refresh | Very fast (in-memory) | Copy of data. Refresh time and model size limits |
| **DirectQuery** | Each visual sends a live SQL query to the source | Live | Slowest. Depends on the source | Load on the source DB |
| **Direct Lake** | Loads column data straight from OneLake Delta files | Near-live (picks up new Delta versions) | Close to Import | Fabric only. Falls back to DirectQuery if a table is too large or it's a SQL view |

Interview line: "Direct Lake gives you Import-mode speed with DirectQuery-style freshness, because Power BI reads the Delta files in OneLake directly instead of copying them."

Steps used in class:

| # | Step |
|---|---|
| 1 | Open `hospital_lakehouse` → **New semantic model** (button at the top of the lakehouse) |
| 2 | Name it `hospital_direct_lake_model`, workspace Hospital Analytics, select the three gold tables |
| 3 | **Open data model** → editing mode → **Model view** → select a table → Properties → **Storage mode = Direct Lake** |

---

# DAX measures

Q. What is DAX?

A. (Teacher's definition) "DAX is a language that we use to write queries within Power BI." The syntax "looks kind of like a combination of SQL with pandas syntax": `'table'[column]` references look like pandas, and the aggregations look like SQL.

Expanded: DAX (Data Analysis Expressions) is the formula language of Power BI, Analysis Services and Excel Power Pivot. A **measure** is a named calculation that is evaluated **at query time in the current filter context**. The same measure gives a total on a card and per-category values in a bar chart.

```dax
Total Encounters = SUM('gold_hospital_metrics'[total_encounters])

Readmission Rate =
DIVIDE(
    SUM('gold_diagnosis_metrics'[readmissions_30d]),
    SUM('gold_diagnosis_metrics'[total_encounters]),
    0
)
```

| DAX piece | Meaning |
|---|---|
| `'table'[column]` | Column reference |
| `SUM`, `AVERAGE`, `COUNTROWS`, `DISTINCTCOUNT` | Aggregations |
| `DIVIDE(a, b, alt)` | Safe division: returns `alt` (here 0) instead of a divide-by-zero error. Evan: it "must not be a division by zero because that would lead to a zero division error" |
| Measure vs calculated column | A measure is computed per visual/filter at query time. A calculated column is computed per row and stored |

How to add one: semantic model editor → select a table → **New measure** → type the formula → click the check mark. Gotcha from class: click **New measure each time**. If you edit the formula bar while an existing measure is selected, you just **rename/overwrite** that measure.

---

Q. How did the Direct Lake report go?

A. (Evan) From the model editor: **New report**. Visuals: **cards** for the two DAX measures (shrink them to compact tiles in the top left, "just big enough to easily contain the text"), plus a clustered bar chart (diagnosis × total encounters) and a line chart (admit month × total encounters). The results were "some boring charts": the readmission rate card showed 0 and the encounter card showed ~10K, because the data only covers one synthetic hospital.

| Visual | Use |
|---|---|
| **Card** | Single KPI number: total encounters, readmission rate, distinct diagnosis count |
| Clustered bar chart | Compare categories |
| Line chart | Trend over time |

Lesson: a report is only as interesting as the gold data. One hospital and fake data give flat charts.

---

# SQL mirroring (attempted)

Q. What is mirroring in Fabric?

A. (Teacher's definition) "SQL mirroring is just about making it so that the data in the SQL database is going to be continuously available in the Fabric environment without issues in the way."

Expanded: **Mirroring** continuously replicates an operational database into OneLake as Delta tables, in near real time, using **change data capture** under the hood. There are no pipelines to build or schedule. Sources include Azure SQL Database, Azure SQL Managed Instance, Azure Cosmos DB, Snowflake, PostgreSQL and others.

| | Copy job / ADF pipeline | Mirroring |
|---|---|---|
| How | Scheduled batch copy | Continuous replication (CDC) |
| Latency | Minutes to hours | Seconds to minutes |
| You build | Pipeline, schedule, incremental logic | Just point at the source |
| Output | Whatever the sink is | Read-only Delta tables in OneLake + SQL endpoint |
| Best for | Many source types, transformations on the way | Keeping an OLTP database's copy analytics-ready with no ETL |

Steps attempted: Fabric workspace → **New item → Mirrored Azure SQL Database** → server + database → authentication (SQL auth / organizational account).

---

Q. What went wrong with mirroring?

A. (Evan) A chain of blockers:

| # | Problem | Cause | Fix / outcome |
|---|---|---|---|
| 1 | "Login failed for user '<token-identified principal>'", then "Resource not found" | `hospital_c_db` had been **deleted** when resources were taken down after the previous class | **SQL server → Data management → Deleted databases → Restore** to a restore point from yesterday |
| 2 | Restore stayed "Deploying" through a break | "Restoring a deleted SQL database is more involved than provisioning a new one" | It finished just as Evan decided to change topic ("complaining always works") |
| 3 | Mirroring needs a **system-assigned managed identity** on the SQL logical server, but no Identity page was visible | He was looking at the database, not the **SQL server** ("SQL server databases" in the portal means SQL Server/Arc instances, not Azure SQL) | `az sql server update --identity-type SystemAssigned` returned a null principal ID. A **direct REST API update** finally set it |
| 4 | Invalid credentials with SQL auth and with an organizational account | Password problems | Password reset |
| 5 | "You cannot mirror a SQL database with the managed identity across tenants" | The SQL server's tenant and the Fabric tenant differ: "a hard architectural restriction, not another missing permission" | **Abandoned** for the day |

Expanded: things to remember:
- Azure SQL keeps **deleted databases restorable** for the retention period (point-in-time restore). Restoring is slower than creating a new one.
- **Managed identity** = an Azure-managed identity for a resource, so it can authenticate to other services without stored secrets. **System-assigned** identities live and die with the resource. **User-assigned** ones are standalone.
- **Tenant** = an organization's Microsoft Entra ID directory. Fabric and the source must be in the same tenant for mirroring. This is the same cross-tenant problem that blocked the Fabric capacity in Training 32.

```bash
# Enable a system-assigned managed identity on the Azure SQL logical server
az sql server update \
  --resource-group <rg> --name <sql-server-name> \
  --identity-type SystemAssigned

az sql server show -g <rg> -n <sql-server-name> --query identity
# expect: { "type": "SystemAssigned", "principalId": "<guid>", ... }
```

---

# Azure Event Hubs

Q. What is Azure Event Hubs?

A. (Evan) Azure's streaming broker. "We've all seen how Kafka works. We can see that Event Hubs works pretty much the same, except that you've got less junk to manage." He has connected to Event Hubs before using **regular Kafka syntax**. Today used the Event Hubs-specific Python package instead.

Expanded: Event Hubs is a fully managed, partitioned event ingestion service. No brokers or ZooKeeper to run. It has a Kafka-compatible endpoint, so Kafka clients work by changing configuration.

| Kafka | Event Hubs | AWS | GCP |
|---|---|---|---|
| Cluster | **Namespace** | Kinesis (account/region) | Pub/Sub (project) |
| Topic | **Event hub** | Kinesis stream | Topic |
| Partition | Partition | Shard | (managed) |
| Consumer group | Consumer group (`$Default`) | Consumer / KCL app | Subscription |
| Offset | Offset / sequence number | Sequence number | Ack |
| Retention | Message retention (1 day on Basic) | 24 h default | 7 days default |

---

Q. How was Event Hubs set up?

A. (Evan) Portal steps:

| # | Step | Values used |
|---|---|---|
| 1 | Create **Event Hubs namespace** | Same resource group, East US, **Basic** tier (cheapest). "All I really needed was the namespace name" |
| 2 | In the namespace → **+ Event Hub** | Name `patient-events`, 1 partition, retention 1 hour/1 day, capture disabled, cleanup policy **Delete** |
| 3 | Namespace → **Settings → Shared access policies** | `hospital-producer` = **Send** only, `hospital-consumer` = **Listen** only |
| 4 | Copy each policy's **primary connection string** | Store as environment variables, never in code |

Expanded: separate policies per role follow **least privilege**. The producer can only send and the consumer can only read, so a leaked consumer key can't inject data.

| Shared access claim | Allows |
|---|---|
| Send | Publish events |
| Listen | Read events |
| Manage | Send + Listen + manage entities |

---

Q. What did the producer and consumer look like?

A. (Evan) "Here's my favorite part, the stuff that we can do on prem." A local folder `hospital-events` with a virtual environment, `pip install azure-eventhub`, environment variables for the two connection strings, then `producer.py` and `consumer.py` in VS Code.

```bash
python3 -m venv venv
source venv/bin/activate          # forgetting this step caused "module not found" in class
pip install azure-eventhub

export EVENTHUB_SEND_CONNECTION_STRING='<hospital-producer primary connection string>'
export EVENTHUB_LISTEN_CONNECTION_STRING='<hospital-consumer primary connection string>'
export EVENTHUB_NAME='patient-events'
```

```python
# producer.py
import json, os, random, time, uuid
from datetime import datetime, timezone
from azure.eventhub import EventHubProducerClient, EventData

CONN = os.environ["EVENTHUB_SEND_CONNECTION_STRING"]
HUB = os.environ["EVENTHUB_NAME"]

def generate_event():
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": random.choice(["admission", "admission", "discharge", "transfer"]),
        "facility_id": random.choice(["hospital-a", "hospital-b", "hospital-c"]),
        "patient_id": f"P{random.randint(1, 5000):05d}",
        "diagnosis_code": random.choice(["J18.9", "I10", "E11.9", "N39.0", "I50.9"]),
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
    }

def main():
    producer = EventHubProducerClient.from_connection_string(CONN, eventhub_name=HUB)
    print("Producing events... Ctrl+C to stop")
    with producer:
        while True:                       # infinite loop: runs until stopped
            event = generate_event()
            batch = producer.create_batch()
            batch.add(EventData(json.dumps(event)))
            producer.send_batch(batch)
            print("sent", event["event_type"], event["facility_id"])
            time.sleep(2)                 # one event every 2 seconds

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Producer stopped.")
```

```python
# consumer.py
import json, os
from azure.eventhub import EventHubConsumerClient

CONN = os.environ["EVENTHUB_LISTEN_CONNECTION_STRING"]
HUB = os.environ["EVENTHUB_NAME"]

def on_event(partition_context, event):
    e = json.loads(event.body_as_str())
    print(partition_context.partition_id, e["event_type"], e["facility_id"], e["patient_id"])

consumer = EventHubConsumerClient.from_connection_string(
    CONN, consumer_group="$Default", eventhub_name=HUB)

try:
    with consumer:
        consumer.receive(on_event=on_event, starting_position="-1")  # "-1" = from the beginning
except KeyboardInterrupt:
    print("Consumer stopped.")
```

Expanded: what happened when run:

| Observation | Why |
|---|---|
| The consumer first printed a burst of many events, then one every 2 seconds | "Just like with Kafka, when you connect a new [consumer], it will ingest the backlog of data that was persisted first, and then it will start with the consumption of newly added data" |
| Events visible in the portal | Event hub → **Data Explorer** → partition → **View events**. Evan: "better than it was the last time that I used it" |
| Three parts of the pipeline | Producer (terminal 1), **broker** (Event Hubs), consumer (terminal 2) |

Evan stopped both scripts before the break "so that we're not streaming during the breaks."

---

Q. If a script runs `while True`, does it only stop when stopped externally? Can the code stop itself? (student question)

A. (Evan) "If you have a loop that says while true, then it is supposed to keep on working forever ... until either it is manually stopped or some kind of external problem stops it." In a mobile or web app you rarely want that, "but in the case of a streaming pipeline, having it always up and operational is a desirable property because that means that it's always there to consume the data. And you have no idea when the data is coming in." Stopping cleanly from code is a **graceful exit**: here the `try/except KeyboardInterrupt` catches **Ctrl+C** and prints "Producer stopped", and Kafka clients have explicit calls like `close()`.

Expanded: ways to shut down a streaming producer or consumer gracefully:

| Method | How |
|---|---|
| Ctrl+C / `KeyboardInterrupt` | `try: main() except KeyboardInterrupt: ...`. The `with` block closes the client |
| Signal handler | Catch `SIGTERM` (sent by Docker/Kubernetes/systemd) and set a `running = False` flag the loop checks |
| Stop condition | `while running and sent < max_events:` or a time limit |
| Explicit close | `producer.close()`, `consumer.close()`, Kafka `producer.flush()` then `close()` so buffered messages aren't lost |
| Commit / checkpoint before exit | Save consumer offsets (checkpoint store) so a restart resumes in the right place |
| Orchestrator | Stop the job or container from the platform (scheduled jobs save cost) |

Why it matters: a hard kill can lose buffered events, leave offsets uncommitted (causing reprocessing) or leave cloud resources running (cost).

---

# Connecting Event Hubs to Fabric

Q. How does streaming data get into Fabric?

A. (Evan) Workspace → **New item → Eventstream** → add **Azure Event Hubs** as the source → publish → add destinations. He left the preview **schema-aware eventstream** option disabled. It's relevant to schema evolution pipelines, "but we're trying to keep it simple here."

Expanded: steps that worked:

| # | Step | Detail |
|---|---|---|
| 1 | New item → **Eventstream** | `hospital_patient_events` |
| 2 | Add source → Connect data sources → **Azure Event Hubs** | "No connection found" → **Create new connection** |
| 3 | Connection settings | Namespace, event hub `patient-events`, auth = **Shared access key** using the **consumer** policy (`hospital-consumer` + its primary key): Fabric is a reader |
| 4 | Consumer group, data format JSON → Add | Schema registry not needed |
| 5 | Canvas shows Event Hub → (blank transform) → output with a data preview | The preview is a **snapshot**. Click refresh for new data |
| 6 | **Publish**, then switch to **Live view** | Edit mode vs Live mode |

| Fabric real-time item | Role | Azure equivalent |
|---|---|---|
| **Eventstream** | Ingest, route and lightly transform streams, no code | Event Hubs + Stream Analytics |
| **Eventhouse** | Container for real-time analytics databases | Azure Data Explorer cluster |
| **KQL database** | Time-series optimized store queried with KQL | Azure Data Explorer database |
| **KQL queryset** | Saved KQL queries | ADX query editor |
| **Real-Time Dashboard** | Auto-refreshing dashboard on KQL queries | ADX dashboards |

---

# Eventhouse, KQL and the Real-Time Dashboard

Q. How was the Eventhouse set up?

A. (Evan) Workspace → New item → **Eventhouse** (`hospital_real_time`). It comes with a default **KQL database** of the same name. Back in the eventstream (edit mode) → **Add destination → Eventhouse** → workspace, eventhouse, KQL database, destination table, input format **JSON** → save, connect the nodes, publish.

Gotcha: the KQL database showed **no tables** at first. The fix was **Get data → Existing eventstream** from the KQL database side, which created the `patient_events` table with live data.

---

Q. What is KQL and what queries were run?

A. Expanded: **KQL (Kusto Query Language)** is the read-only query language for Azure Data Explorer, Fabric Real-Time Intelligence, Log Analytics and Sentinel. A query starts with a table and **pipes** (`|`) the rows through operators, much like a Unix pipeline. Evan noticed it's "different syntax" from SQL. Names containing a dash need bracket-quote syntax, like `['patient-events']`; the typo of `_` for `-` caused the "take operator failed" error.

```kusto
patient_events
| take 10

patient_events
| count                                    // 81 events at that point in class

patient_events
| summarize event_count = count() by event_type
| order by event_count desc                // admission > discharge, transfer

patient_events
| where event_type == "admission"
| summarize admissions = count() by facility_id
| order by admissions desc

patient_events
| summarize events = count() by bin(todatetime(event_timestamp), 1m)
| render timechart                         // built-in chart in the query result
```

| SQL | KQL |
|---|---|
| `SELECT * FROM t LIMIT 10` | `t \| take 10` |
| `SELECT COUNT(*) FROM t` | `t \| count` |
| `WHERE x = 'a'` | `\| where x == "a"` |
| `GROUP BY` + aggregate | `\| summarize count() by col` |
| `ORDER BY c DESC` | `\| order by c desc` (or `sort by`) |
| Time bucketing | `bin(timestamp, 1m)` |
| (no equivalent) | `\| render timechart` draws a chart |

Real-Time Dashboard: from the time-series query → **Save to dashboard** (no existing dashboard) → **Generate real-time dashboard** → open it, add more tiles as needed, save. Tiles re-run their KQL on a refresh interval, so it updates as events stream in.

---

# Streaming into the lakehouse medallion

Q. How do you get the stream into the bronze layer so it can join silver?

A. (Evan) Add a **second destination** to the same eventstream: **Lakehouse** → `hospital_lakehouse`, new table `bronze_patient_events`, format JSON. First save failed with "The operation is missing input" until the destination node was **connected** to the stream on the canvas. Then the eventstream fanned out to two places:

```text
producer.py → Event Hubs (patient-events) → Fabric Eventstream ─┬→ Eventhouse / KQL DB (patient_events) → KQL queries → Real-Time Dashboard
                                                                 └→ Lakehouse table bronze_patient_events → notebook → silver → gold → Power BI
```

Expanded: this is the **hot path / cold path** pattern (a lambda-style architecture). The hot path (Eventhouse + KQL) gives second-level dashboards. The cold path (lakehouse Delta + Spark) gives cleaned, joined, historical analytics.

| Path | Store | Latency | Used for |
|---|---|---|---|
| Hot | Eventhouse (KQL) | Seconds | Live monitoring, alerts |
| Cold | Lakehouse (Delta) | Minutes (batch notebook) | Joins with batch data, gold tables, BI |

---

Q. What did the streaming notebook do?

A. (Evan) A new notebook, `streaming_notebook`. First error: "no default context exists": the lakehouse wasn't attached as **default**. In the Explorer, remove the wrong item (a warehouse, not a lakehouse), add `hospital_lakehouse`, then **"Set as default lakehouse"** from its menu. After that the schemas loaded.

```python
from pyspark.sql import functions as F

bronze_ev = spark.read.table("bronze_patient_events")

# Silver: typed, validated, deduped streaming events
silver_ev = (bronze_ev
    .withColumn("event_ts", F.to_timestamp("event_timestamp"))
    .withColumn("event_type", F.lower(F.trim("event_type")))
    .filter(F.col("event_id").isNotNull() & F.col("patient_id").isNotNull())
    .filter(F.col("event_type").isin("admission", "discharge", "transfer"))
    .dropDuplicates(["event_id"]))
silver_ev.write.format("delta").mode("overwrite").saveAsTable("silver_patient_events")

# Unified table: batch encounters + a per-patient summary of streaming events
event_summary = silver_ev.groupBy("patient_id").agg(F.count("*").alias("stream_event_count"))
unified = (spark.read.table("silver_patient_encounters")
    .join(event_summary, "patient_id", "left"))
unified.write.format("delta").mode("overwrite").saveAsTable("silver_unified_encounters")

display(spark.read.table("silver_unified_encounters").limit(10))
```

Gotcha: `SELECT TOP 10 *` threw a syntax error because a notebook cell is **PySpark**, not T-SQL. Use `display(df.limit(10))`, or a `%%sql` cell with Spark SQL `LIMIT`.

---

Q. What were the streaming gold tables?

A. (Evan) Three gold tables from the silver events: **facility**, **timeline** and **diagnosis**.

```python
is_adm = (F.col("event_type") == "admission").cast("int")
is_dis = (F.col("event_type") == "discharge").cast("int")
is_tra = (F.col("event_type") == "transfer").cast("int")

gold_facility = (silver_ev.groupBy("facility_id").agg(
        F.count("*").alias("total_events"),
        F.sum(is_adm).alias("admissions"),
        F.sum(is_dis).alias("discharges"),
        F.sum(is_tra).alias("transfers"))
    .withColumn("net_admissions", F.col("admissions") - F.col("discharges")))

gold_timeline = (silver_ev.groupBy(F.window("event_ts", "5 minutes")).agg(
        F.count("*").alias("events"),
        F.sum(is_adm).alias("admissions"),
        F.sum(is_dis).alias("discharges"),
        F.sum(is_tra).alias("transfers"))
    .select(F.col("window.start").alias("window_start"), "events",
            "admissions", "discharges", "transfers"))

gold_diag = silver_ev.groupBy("diagnosis_code").agg(F.count("*").alias("events"))

for name, df in [("gold_live_facility_metrics", gold_facility),
                 ("gold_live_timeline", gold_timeline),
                 ("gold_live_diagnosis", gold_diag)]:
    df.write.format("delta").mode("overwrite").saveAsTable(name)
print("All three streaming gold tables refreshed")
```

| Gold table | Grain | Key column |
|---|---|---|
| `gold_live_facility_metrics` | Per facility | `net_admissions` = admissions − discharges ≈ patients admitted and not yet discharged |
| `gold_live_timeline` | Per 5-minute **tumbling window** (`F.window`) | Events by type over time |
| `gold_live_diagnosis` | Per diagnosis code | Event counts |

---

Q. How did the streaming gold get into Power BI?

A. (Evan) Lakehouse → **New semantic model** `hospital_streaming_model` with the `gold_live_*` tables. The first try failed: "We cannot refresh this semantic model because one or multiple source tables either do not exist or access was denied." **Retrying** worked; the tables had just been written. Direct Lake again by default. Measures were added in the model:

```dax
Total Streaming Events = SUM('gold_live_facility_metrics'[total_events])
Total Admissions       = SUM('gold_live_facility_metrics'[admissions])
Total Discharges       = SUM('gold_live_facility_metrics'[discharges])
Total Transfers        = SUM('gold_live_facility_metrics'[transfers])
Net Admissions         = [Total Admissions] - [Total Discharges]   -- a measure built from measures
```

Then **New report** with a card for Total Streaming Events. Class ended there: "We've already built out two dashboards already, so this would just be getting repetitive."

---

# The big picture

Q. Was anything new here, apart from Power BI? (student comment)

A. (Evan) "Eventually in data engineering, everything in all of these different systems is ultimately the same process. It's just being dressed up in different ways ... You do something in Kafka. You do the same thing in Kinesis. You do the same thing in Event Hubs. You do the same thing in Google Pub/Sub. You do certain things in Databricks notebooks. You do the exact same thing in Fabric notebooks ... Data warehouses, whether you're in Snowflake or Redshift or Hive ... it's all the same basic format. The differences are basically in the specific features like the Direct Lake stuff, the mirroring stuff." Once you understand a streaming pipeline, "I don't need to necessarily have interacted with the environment before" to build one.

| Pipeline stage | AWS | Azure | Fabric | GCP | Open source |
|---|---|---|---|---|---|
| Stream broker | Kinesis | Event Hubs | Eventstream (source) | Pub/Sub | Kafka |
| Batch ingest | Glue / DMS | ADF | Copy job / pipeline / mirroring | Dataflow / Datastream | Airflow + scripts |
| Processing | EMR / Glue / Databricks | Databricks / Synapse Spark | Fabric notebooks | Dataproc / Dataflow | Spark / Flink |
| Storage | S3 | ADLS Gen2 | OneLake | GCS | MinIO / HDFS |
| Warehouse | Redshift | Synapse | Warehouse / SQL endpoint | BigQuery | Hive / Trino |
| Real-time query | OpenSearch / Timestream | Data Explorer | Eventhouse (KQL) | Bigtable / BigQuery | Druid / Pinot |
| BI | QuickSight | Power BI | Power BI | Looker | Superset / Streamlit |

---

# Interview prep

Q. What was in the SME's narrative breakdown? (shared by a student who attended the morning session)

A. (Student summary) It wasn't a mock interview but a presentation plus a document. For each profile company it gives an **"architecture at a glance"** for the project, and separate narratives for the **batch pipeline** and the **streaming pipeline** with their technologies. It has a section of **five questions you should be able to answer**, each with an opener, a **STAR**-method example answer and options, linked to sections of the profile:

| # | Question |
|---|---|
| 1 | How do you stop bad data from spreading? |
| 2 | How do you handle unexpected schema changes? |
| 3 | How do you handle slowly changing dimensions? |
| 4 | Why NoSQL instead of your warehouse (for a given use case)? |
| 5 | How did you protect payment and banking data? |

Expanded: short answer anchors from the course so far:

| Question | Anchor points |
|---|---|
| Bad data | Validate at bronze → silver (not-null, ranges, dedup), quarantine bad rows, data quality checks (DLT expectations / Great Expectations), stop the pipeline on failed gates, alerting |
| Schema changes | Schema registry and compatibility rules, schema evolution (Delta `mergeSchema`), raw bronze kept as-is so you can replay, alerts on new columns |
| SCD | Type 1 overwrite vs **Type 2** history rows with effective dates and a current flag, built with `MERGE` |
| NoSQL vs warehouse | NoSQL (DynamoDB, Cosmos DB, MongoDB) for low-latency key lookups and flexible documents in serving. Warehouse for analytical scans and aggregation |
| Payment data | Encryption at rest and in transit, KMS / Key Vault, tokenization/masking of PII, least-privilege IAM/RBAC, network isolation (VPC/private endpoints), audit logs, PCI-DSS |

Next class: start GCP, or possibly a **review day**, since Evan wants "more conversation in these classes rather than just me sitting, giving a presentation."

---

# Key terms from today

| Term | Meaning |
|---|---|
| Direct Lake | Power BI storage mode reading OneLake Delta files directly. Default for lakehouse semantic models |
| Import / DirectQuery | Copy data into the model on refresh / send live queries to the source |
| DAX | Power BI's formula language for measures and calculated columns |
| Measure | Named calculation evaluated at query time in the filter context |
| `DIVIDE()` | DAX safe division with an alternate result for divide by zero |
| Card visual | Single-number KPI tile |
| Mirroring | Continuous CDC replication of a database into OneLake Delta tables |
| Managed identity | Azure-managed identity for a resource. No stored secrets |
| Tenant | An organization's Entra ID directory. Mirroring can't cross tenants |
| Deleted database restore | Azure SQL point-in-time restore of a dropped DB within retention |
| Event Hubs namespace / event hub | Azure equivalents of a Kafka cluster / topic |
| Shared access policy | Named key with Send / Listen / Manage claims |
| Connection string | Endpoint + key name + key used by SDK clients (a secret) |
| `azure-eventhub` | Python SDK: `EventHubProducerClient`, `EventHubConsumerClient` |
| Backlog | Retained events a new consumer reads first |
| Graceful shutdown | Stopping a stream cleanly (flush, close, checkpoint) |
| Eventstream | Fabric no-code stream ingestion and routing |
| Eventhouse / KQL database | Fabric real-time analytics store (Azure Data Explorer) |
| KQL | Kusto Query Language: pipe-based read-only queries |
| Real-Time Dashboard | Auto-refreshing dashboard on KQL queries |
| Hot path / cold path | Real-time store for live views + lakehouse for historical analytics |
| Default lakehouse | The lakehouse a Fabric notebook resolves table names against |
| Tumbling window | Fixed, non-overlapping time buckets (`F.window(ts, "5 minutes")`) |
| Net admissions | Admissions − discharges ≈ current in-patients |
