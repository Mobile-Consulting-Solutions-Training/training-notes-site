---
title: "Training 30 - Delta Lake, Auto Loader and MLflow"
description: "Delta Lake MERGE, time travel and RESTORE, CDC vs SCD, Auto Loader, Lakeflow Jobs and an introduction to MLflow, plus profile narratives."
sidebar:
  order: 30
---

Teacher: Evan Flint

Syllabus Day 31 (per file numbering; Thu Oct 22, 2026). The roadmap had **ADF + Unity Catalog** for today. Evan spent the first part on profile narratives, then taught a deeper Databricks day: **Delta Lake operations** (time travel, RESTORE, MERGE), **Auto Loader**, **Lakeflow Jobs** and an introduction to **MLflow**. ADF was mostly covered on the Training 28 day; Unity Catalog only came up in passing (a short catch-up section is at the end).

Source: class notes.

**Code note:** the code below is written from the class demo plus standard Databricks syntax. It is not an exact copy of Evan's code. The demo continued the Citi Bike data from Training 29.

---

# Today at a glance

| # | What happened |
|---|---|
| 1 | Pre-class chat: students compare Azure + Databricks with AWS (fewer services, fewer permission roadblocks). Evan: having opinions about frameworks is an underrated interview quality |
| 2 | Profile narratives, first hour: seat-booking story, Datadog's role, Airflow "kill switch", a pre-launch satellite project, a mixed GCP stack, Databricks-on-GCP, lead vs. senior titles |
| 3 | A quick LangChain chatbot demo (a missing-package error, then it worked) |
| 4 | Break |
| 5 | One more narrative: warehouse scanning app, the LLM part, and NVIDIA RAPIDS (GPU Spark) economics |
| 6 | Delta Lake theory: MERGE, time travel, RESTORE |
| 7 | Delta demo: create a table, `DESCRIBE HISTORY`, `UPDATE`, `VERSION AS OF`, a "bad update", `RESTORE`, `MERGE INTO`, idempotency, a CDC-style merge |
| 8 | Theory detour: **idempotency**, **CDC** vs **SCD** (Type 0 / 1 / 2) |
| 9 | Break |
| 10 | Auto Loader: `cloudFiles`, checkpoints, `availableNow`, incremental ingestion (1230 → 1231 rows), checkpointing vs. deduplication, schema evolution recap |
| 11 | Lakeflow Jobs: Bronze/Silver and Gold notebooks wired into a two-task Job (after first creating an ETL pipeline by mistake) |
| 12 | Break. Q&A: Databricks Jobs vs. ADF; is ETL outdated? |
| 13 | MLflow: tabular ML, the fraud-detection story, local MLflow server UI (experiments, model registry, traces) |
| 14 | MLflow in Databricks: train a random forest on Citi Bike Silver, log params and metrics. The experiment didn't show up in the UI; the rest (registry, batch predictions) moves to a later class |
| 15 | Homework (Delta, Auto Loader, Lakeflow Jobs, MLflow reading + exercises; main priority: profile narratives). Next class starts with narratives and elevator pitches |

---

# Class admin and heads-ups

Q. What's the homework?

A. (Evan) The main priority is still the **professional profile narratives**. The technical part is reading plus four short exercises on today's topics.

| Part | What | Time |
|---|---|---|
| 1 (main) | Updated professional summary + **two project narratives** (business problem, architecture, your responsibilities, challenges, impact). Practice telling them conversationally | Most of your time |
| 2 | Databricks reading: Delta Lake (vs. Parquet, time travel, `RESTORE` / `MERGE` / `VACUUM`), Auto Loader (`cloudFiles`, checkpoints), Lakeflow Jobs (tasks, dependencies, failures) | 15–20 min |
| 3 | MLflow reading: experiments vs. runs, params / metrics / artifacts, Model Registry, MLflow in Databricks | 10–15 min |
| 4 | Four short exercises: time travel + restore SQL, Auto Loader code questions, a Bronze → Silver → Gold Job failure question, an MLflow `start_run()` snippet | 15–20 min |
| 5 (optional) | Create an MLflow experiment in Databricks, log a parameter and a metric, find it in the UI | — |

Full prompt: `homework/assignment/Homework - Training 30 (Assignment).md`.

---

Q. What's happening next class?

A. (Evan) Next class starts with **narratives and elevator pitches**. He confirmed this with a program staff member who joined to observe. Delivery (how you speak) will be worked on in the **soft-skills sessions**, so today's feedback focused on content.

---

# Opinions and platform comparisons (pre-class chat)

Q. Why did students find Azure + Databricks easier than AWS?

A. (Evan) "You're empowered to do a lot more things with a lot fewer services in Azure." On AWS the class built pipelines out of **S3, EventBridge, Lambda, Glue, EMR and Redshift**. On Azure "you can put something up on ADLS, bring it into Databricks and do pretty much what you need to do with it within Databricks." Databricks is "considered to be the engineer's favorite framework for big data operations… the competition is between Databricks and Snowflake for the most part, and organizations tend to prefer Snowflake and engineers tend to prefer Databricks."

Expanded: students also liked having Python and SQL in the same notebook. On permissions, Evan pointed out that Azure security isn't actually simple. There's **Microsoft Entra ID** (users and groups) and **managed identities** (identities for services), and both need the right roles. The difference is that once you have Databricks permissions, you can do most of the work inside one tool, so you aren't asking for a new permission for every new service.

| | AWS pipeline (class) | Azure pipeline (class) |
|---|---|---|
| Storage | S3 | ADLS Gen2 |
| Trigger / orchestration | EventBridge, Lambda, Step Functions | Databricks Jobs (or ADF) |
| Processing | Glue, EMR | Databricks |
| Warehouse | Redshift | Databricks SQL / Synapse ([Training 31](Training%2031.md#azure-synapse-analytics)) |
| Permissions | IAM policy per service, per bucket, per prefix | Entra ID + managed identities + RBAC roles (e.g. Storage Blob Data Contributor), then Databricks / Unity Catalog grants |

---

Q. Why does having opinions help in an interview?

A. (Evan) "One of the underrated qualities to have in an interview situation is the ability to express opinions about how good one framework is versus another. That shows that you have experience, and it lets the interviewer know that you've got enough hands-on with these things to actually do something."

---

# Profile narratives (first hour)

Q. How detailed does a narrative need to be? Will they ask for table names?

A. (Evan) Interviewers "generally don't ask you about table names, both because it's often not that practical an avenue to go down and because it could be considered as asking for improper information." But you still need a **mental model** of the tables: you can talk about what a table's relationship is to other tables, or why one table is stored somewhere different.

Expanded: for a student's airline seat-booking story (the airline moving from open seating to assigned seats at booking), Evan had AI generate plausible example tables that would have needed a new column, plus a realistic explanation. A big change like that means a fairly complex back end (reservations, inventory, booking stores), so assume a complex architecture if you want a sophisticated story.

---

Q. What does Datadog actually do in a data pipeline story?

A. (Evan) It's not analytics for marketing. "It's to create analytics for your technical infrastructure… monitoring the infrastructure that the pipeline is built out of." For example, for an Event Hubs pipeline it can show throughput and the number of messages in a time window. It collects those metrics into a dashboard so the people who manage the infrastructure can see a problem, and it alerts people "as quickly as possible if something has gone wrong… something which might break the pipeline."

Expanded (correction): Evan mentioned "number of shards" as an Event Hubs metric. **Shards** are the Kinesis term; Event Hubs calls them **partitions**. Typical things to monitor: consumer lag, throughput, error rates, job durations, CPU and memory.

| Tool | What it watches | Who uses it |
|---|---|---|
| Datadog (observability) | The infrastructure and jobs: throughput, lag, errors, latency, resource use | Engineers / on-call |
| BI dashboard (Power BI, Streamlit) | The business data itself | Analysts, business teams |

---

Q. Can Airflow be a "kill switch" or circuit breaker for a pipeline?

A. (Evan) "Airflow isn't in charge of the content of the data. Airflow is about scheduling the jobs that handle the data." It won't stop unless a task fails. But it can evaluate the results of quality checks that another framework returns "and can make a decision about whether to execute a downstream task or not." So the narrative is: "Airflow is responsible for whether downstream tasks get executed or not, and based on the results of a quality check it can be made to halt." That's believable.

Expanded: a planned change, like a country's regulation forcing you to stop collecting data there, usually isn't handled automatically. The team builds a separate place for those records or decides not to keep them. Incomplete data (a country or station that stops sending) doesn't break a pipeline; it just isn't there at the end. **Malformed** data is what makes a processing job fail. How you'd build the circuit breaker in Airflow:

| Airflow piece | Use |
|---|---|
| **Sensor** | Wait for a condition (a file landed, a check table says "pass") before continuing |
| `ShortCircuitOperator` / branch operator | A Python check that returns False skips all downstream tasks |
| Failing a quality-check task (e.g. a Great Expectations or dbt test task) | Downstream tasks with the default trigger rule (`all_success`) don't run |
| A config table or Airflow Variable per country | The "feature flag" a task reads to decide whether to process that country |

---

Q. Can you tell a story about a project that never launched?

A. (Evan) Yes. "Just because it hasn't gone live doesn't mean that it wasn't something that was being worked on… People get hired to work on projects that are later canceled all the time." A beta test of a satellite internet network would still involve a fair amount of data. And "the infrastructure that has to be built is going to be the same whether the flow of data through that infrastructure was really big or not." It can be a **building-out-infrastructure** story rather than a managing-an-existing-pipeline story.

---

Q. Why would one pipeline use both PySpark/Dataproc and dbt/BigQuery?

A. (Evan) It "looks accurate because it's not completely straightforward." It's more complex than it needs to be, but there's always an organizational reason. "PySpark is going to be an ETL pipeline, whereas dbt is always going to be ELT." So find a part of the company where ETL made sense and a part where ELT did. Also: if you ingest from many APIs, some will be REST and some GraphQL, and you don't need a special reason for that. An interviewer won't ask.

Expanded: another student suggested a believable reason: the company was in the middle of a big migration, so old and new stacks were running side by side. Evan also said Iceberg and BigQuery can coexist simply by saying Iceberg held the Silver layer.

---

Q. How do you turn a mixed Databricks + GCP profile into one story?

A. (Evan) Call it a **Databricks-on-GCP** project. Pub/Sub → Dataflow → BigQuery for one feed, with Bronze and Silver in **Delta Lake** and **BigQuery as the Gold layer**: "that's a totally acceptable use case." He said to remove Snowflake from that profile: "we don't want to use Databricks and Snowflake in the same project." For the RAG part, LangChain fits: "LangChain is a framework just for interacting with the AI model and building out the app… it just won't have all the pretty visualizations" like Streamlit. Unity Catalog fits too, since "Unity Catalog is what we're working on by default right now."

Expanded: plenty of real companies do run Databricks and Snowflake together. Evan's point is about narratives: two competing platforms in one project invites "why both?" questions you'd have to answer. Keep the story simple.

---

Q. What if the profile says "lead" and you're not comfortable with that?

A. (Evan) "If you're not comfortable being marketed as a lead, then we shouldn't market you as a lead." The student raised it with the program's marketing contact to change it to **senior**. A lead narrative would lean toward architecture, stakeholders and managing the team, not pipeline details.

Expanded: the student also noted that interviewers usually ask about your **current and previous** role, or about a past employer in the same industry as the one you're interviewing with.

---

Q. How do you fill the gap between Flink and BigQuery in a GCP story?

A. (Evan) "Flink is very unlikely to just directly put anything into BigQuery." Have the Flink streaming job write to **Google Cloud Storage (GCS)**, "the exact same thing as S3 or ADLS, just on Google Cloud." Flink does basic cleanup (duplicates, nulls) into a Bronze landing zone. Because the profile also listed **dbt**, the story changes: "dbt doesn't actually process the data itself. It needs a processing engine," so **BigQuery is dbt's engine** for Bronze → Silver → Gold. Without dbt you'd fall back on **Cloud Dataproc**, "basically the same thing as AWS EMR." The RAG pipeline then reads from the BigQuery warehouse.

Expanded (correction): Flink can write to BigQuery directly with a BigQuery sink connector, so it's possible, just less common than landing files in GCS first. Landing in GCS is still the cleaner story. On vector stores, Evan said **S3 Vectors** (used in last week's RAG lesson) and **pgvector** are "functionally the same thing": S3 Vectors is vector storage inside S3, pgvector is a PostgreSQL extension.

| GCP | AWS | Azure |
|---|---|---|
| Cloud Storage (GCS) | S3 | ADLS Gen2 |
| Pub/Sub | Kinesis / MSK | Event Hubs |
| Dataflow (Apache Beam) | Kinesis Data Analytics / Glue streaming | Stream Analytics |
| Dataproc | EMR | HDInsight / Databricks |
| BigQuery | Redshift / Athena | Synapse |
| Cloud Composer (managed Airflow) | MWAA | ADF / Airflow in ADF |

---

Q. What did the LangChain demo show?

A. (Evan, demo) A very simple chatbot: a small Python web app with one HTML page and a `/chat` route. It failed first with a 404 because the packages weren't installed for the Python version he was using. After installing them it answered "What's the capital of France?"

| Step | What |
|---|---|
| Error | Not found / 404 when running the app; dependencies missing for that Python |
| Fix | `pip install langchain-core langchain-openai` for the right interpreter, then rerun |
| How it works | `ChatOpenAI` creates the LLM object (an older config using `gpt-4o-mini`), a prompt template takes the user input, `chain.invoke(user_input)` returns the answer as JSON, and the page's script shows it |

```python
# from the class demo (not exact)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{user_input}"),
])
chain = prompt | llm

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.get_json()["message"]
    try:
        response = chain.invoke({"user_input": user_input})
        return jsonify({"response": response.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

"This is the most basic use case for LangChain… not a full-scale multimodal production app like the actual ChatGPT website."

---

Q. How should an LLM feature appear in a narrative?

A. (Evan) Not as something that takes work off the pipeline team. Present it as a **product for another team** (business, managers), "so that they can ask questions about what part of the data is pertinent to their job rather than having to write SQL." And follow **Occam's razor**: "simplest is best… anything that you mention in an interview becomes fair game for the interviewer to ask follow-up questions," which could turn it into an AI interview instead of a data engineering one. If you don't want to go deep on LLMs, leave them out.

---

Q. What is NVIDIA RAPIDS, and does it belong in a narrative?

A. (Evan) A way to run Spark processing on **GPUs**. He put it in "the category of technically impressive, commercially relevant, but relatively niche technologies. Most Spark workloads don't use GPUs… the economics aren't universally favorable." The GPU is always the most expensive part of a computer, so if CPUs already give production speed, there's little reason to pay for GPUs. An AI example: 15 TB a day in 4 hours on CPU Spark (~$40/hour) vs. 50 minutes on GPU Spark (~$100/hour), so "is four times the speed worth more than double the cost?" A fraud-feature example was about 10× faster. At NVIDIA itself the marginal cost of an internal GPU is lower, but "they're expensive for a reason."

Expanded (correction): Evan doubted the student's "around 2019" date ("there's no way it's been around since 2019"). The student was close: **RAPIDS** was released by NVIDIA in **late 2018**, and the **RAPIDS Accelerator for Apache Spark** (the plugin that runs Spark SQL and DataFrame work on GPUs) came with Spark 3.0 in **2020**. It works best on large joins, aggregations and sorts; small data gains little. Evan also thought 15 TB in 4 hours on CPU would need a very large cluster ("I would say four hours for each two of those terabytes").

---

# Delta Lake: MERGE, time travel, RESTORE

Q. What is Delta MERGE?

A. (Teacher's definition) "A method of combining two tables together, which is different from that of a SQL join or a SQL union. Merge seeks to take some of the common operations of joins and unions and simplify them, by combining the operations of taking the two data sets and bringing them together and also updating any older values to the newest ones, so that the newest value is represented in every case for every data point. So it's basically a combination insert and update operation." He called it "probably the most on-the-ground operationally important" of today's three.

Expanded: MERGE is an **upsert**. It matches source rows to target rows on a key, then for each row decides: update, insert or delete. It all happens in **one atomic commit** in the Delta log. More in [Training 29, Delta Lake Operations](Training%2029.md#delta-lake-operations-roadmap-topic-not-taught-in-class) and the Redshift MERGE in Training 24.

---

Q. What is time travel?

A. (Teacher's definition) "It's a feature of some data formats which will allow you to query a table in terms of the way that it looked at a previous time." Example: an ingestion job runs every 10 minutes, and you want to compare the table now vs. an hour ago vs. 24 hours ago. "Time travel is a feature of open table formats, so that's Delta, Iceberg and Hudi. They all can do time-travel-style queries if you're using an engine that is capable of doing that with them." He thought there's a limit and the default might be 24 hours, "but I may be wrong about that." Also: "it's a lot more boring in data engineering than it is in the movies," but it "gets talked about in interviews… because its name sounds interesting."

Expanded (correction): Delta has no 24-hour limit. How far back you can go depends on two table settings:

| Setting | Default | Controls |
|---|---|---|
| `delta.logRetentionDuration` | **30 days** | How long the history (log entries) is kept |
| `delta.deletedFileRetentionDuration` | **7 days** | How old unreferenced data files must be before `VACUUM` can delete them |

Until you run `VACUUM`, old versions are readable as long as the log has them. After `VACUUM`, you can only go back about **7 days** by default. Raise both settings for a longer window.

---

Q. How does Databricks time travel compare with Snowflake's? (student question)

A. (Evan) He asked AI: Snowflake's maximum retention is **up to 90 days**; Databricks "is not limited to a fixed 90-day maximum."

Expanded:

| | Snowflake Time Travel | Delta Lake time travel |
|---|---|---|
| Default | 1 day | History 30 days; files 7 days after VACUUM |
| Maximum | 90 days (Enterprise edition and up) | No fixed max; set by the retention properties (and storage cost) |
| After the window | **Fail-safe**: 7 more days, recoverable only by Snowflake support | Gone once VACUUM deletes the files |
| Syntax | `AT(OFFSET => -3600)`, `AT(TIMESTAMP => ...)`, `BEFORE(STATEMENT => ...)` | `VERSION AS OF n`, `TIMESTAMP AS OF '...'` |
| Undo | `UNDROP TABLE`, clone at a point in time | `RESTORE TABLE ... TO VERSION AS OF n` |

---

Q. What is time travel used for? (student question)

A. (Evan) "It's for comparing data." If you suspect data was deleted, run a time-travel query to diagnose it. Or if invalid records start appearing in an incremental or streaming job, "do time travel on versions farther and farther back until you identify which version of it has none of those records," then use that version's timestamp to find when the problem began.

Expanded: other uses: auditing (what did the table say on the date of a report), reproducing an ML training set exactly, and rolling back with RESTORE.

---

Q. Is time travel like the LAG function? (student question)

A. (Evan) "Well, LAG is an operation that permanently changes the data, whereas time travel just looks at older versions of the data." Then: "I guess you could just do a select query that has a LAG… but you're not going to be able to do a LAG operation on an entire table."

Expanded (correction): `LAG()` doesn't change any data. It's a read-only **window function** that returns a value from a previous row in the same query result (e.g. yesterday's count next to today's). The real difference: LAG compares **rows within one version** of the table; time travel compares **whole versions** of the table at different points in time.

| | `LAG()` | Time travel |
|---|---|---|
| Compares | Rows in the current data (ordered by a column) | The whole table at an earlier version or timestamp |
| Changes data? | No | No (only `RESTORE` writes) |
| Example | `LAG(bikes) OVER (PARTITION BY station ORDER BY ts)` | `SELECT * FROM t VERSION AS OF 3` |

---

Q. What is RESTORE?

A. (Teacher's definition) "The restore operation is pretty much what it sounds like. You've deleted some data, you would like for that deleted data to be undeleted. Well, you can use restore to bring it back." It's "useful if you have an accident, which happens more often than you might want it to."

Expanded: `RESTORE` rolls the table back to an earlier version by writing a **new commit** that points at the old files. History isn't erased: the restore shows up in `DESCRIBE HISTORY` as its own version with operation `RESTORE`, so you can even undo the undo. It needs the old data files to still exist (not vacuumed).

---

Q. How do RESTORE, MERGE and VACUUM differ? (homework question)

A. (VACUUM wasn't shown in class.)

| Command | What it does | Adds a version? | Changes history access? |
|---|---|---|---|
| `RESTORE TABLE t TO VERSION AS OF n` | Rolls the table back to version `n` | Yes (operation `RESTORE`) | No |
| `MERGE INTO t USING s ON ...` | Upserts (and optionally deletes) source rows into the target | Yes (operation `MERGE`) | No |
| `VACUUM t [RETAIN n HOURS]` | Physically deletes data files no longer referenced and older than the retention (default 7 days) | No new data version (it's logged as maintenance) | **Yes**: you can't time travel to versions whose files are gone |

Details on VACUUM, OPTIMIZE and liquid clustering are in [Training 29](Training%2029.md#delta-lake-operations-roadmap-topic-not-taught-in-class).

---

Q. How did the Delta demo go? (step by step)

A. (Evan, demo) A new notebook in his Azure Databricks workspace, one small table of two stations, `%sql` cells.

| Step | Command | Result |
|---|---|---|
| 1 | `CREATE OR REPLACE TABLE ... USING DELTA AS SELECT ... UNION ALL ...` | "No rows returned" (it's a create statement). Version 0 |
| 2 | `SELECT *` | 001 → 10 bikes, 002 → 15 bikes |
| 3 | `DESCRIBE HISTORY` | One row: version 0, `CREATE OR REPLACE TABLE AS SELECT` |
| 4 | `UPDATE ... SET bikes_available = 4 WHERE station_id = '001'` | 1 row affected. Version 1 |
| 5 | `DESCRIBE HISTORY` | Two rows; the new one is the `UPDATE` |
| 6 | `SELECT ... VERSION AS OF 0` | 001 shows **10** again (the old value) |
| 7 | "Simulate a production mistake": `UPDATE ... SET bikes_available = 0` with **no WHERE** | Every row affected; both stations now 0. Version 2 |
| 8 | `DESCRIBE HISTORY` to find the last good version | Version 1 |
| 9 | `RESTORE TABLE ... TO VERSION AS OF 1` | Back to 001 → 4, 002 → 15. History shows a new version with operation **RESTORE** |
| 10 | `MERGE INTO` with a "new API response": 001 updated to 20, 003 new | 2 rows affected; 002 unchanged |
| 11 | Run the same MERGE again | Same result, no duplicates (idempotent) |
| 12 | CDC-style MERGE: 001 → 12, delete 002, insert 004 | 002 gone, 004 added, 003 unchanged |

```sql
-- from the class demo (not exact)
%sql
CREATE OR REPLACE TABLE <catalog>.default.delta_demo
USING DELTA
AS
SELECT '001' AS station_id, 10 AS bikes_available
UNION ALL
SELECT '002' AS station_id, 15 AS bikes_available;

DESCRIBE HISTORY <catalog>.default.delta_demo;

UPDATE <catalog>.default.delta_demo
SET bikes_available = 4
WHERE station_id = '001';

-- Time travel by version
SELECT * FROM <catalog>.default.delta_demo VERSION AS OF 0 ORDER BY station_id;

-- The "production mistake": no WHERE clause
UPDATE <catalog>.default.delta_demo SET bikes_available = 0;

-- Recover
RESTORE TABLE <catalog>.default.delta_demo TO VERSION AS OF 1;
```

Expanded (correction): for time travel by time, Evan said you'd need to "convert the timestamp to a string and do matching." You don't. Delta has a built-in form: `SELECT * FROM t TIMESTAMP AS OF '2026-10-22 18:30:00'` (or a date, or an expression like `current_timestamp() - INTERVAL 1 HOUR`). It returns the latest version committed at or before that time. You can copy a timestamp straight from `DESCRIBE HISTORY`.

---

Q. What does the MERGE syntax look like?

A. (Evan, demo) "Unfortunately it's not as simple as merge into one table another table. You have to have this USING clause and these WHEN clauses, but those are necessary for you to be able to tell it how to merge properly, so you can change up the rules of how the merge actually behaves."

```sql
-- from the class demo (not exact)
MERGE INTO <catalog>.default.delta_demo AS target
USING (
  SELECT '001' AS station_id, 20 AS bikes_available
  UNION ALL
  SELECT '003' AS station_id, 8 AS bikes_available
) AS source
ON target.station_id = source.station_id
WHEN MATCHED THEN
  UPDATE SET target.bikes_available = source.bikes_available
WHEN NOT MATCHED THEN
  INSERT (station_id, bikes_available)
  VALUES (source.station_id, source.bikes_available);
```

Expanded:

| Clause | Meaning |
|---|---|
| `MERGE INTO target` | The table that changes |
| `USING source` | The new data: a table, view or subquery |
| `ON` | The match key (station_id here) |
| `WHEN MATCHED [AND cond] THEN UPDATE / DELETE` | The key exists in both |
| `WHEN NOT MATCHED [AND cond] THEN INSERT` | The key is only in the source (new row) |
| `WHEN NOT MATCHED BY SOURCE THEN DELETE / UPDATE` | The key is only in the target (e.g. delete rows missing from a full snapshot) |
| `UPDATE SET *` / `INSERT *` | Shortcut when source and target have the same columns |

The source must have **at most one row per key**, or MERGE fails with a "multiple source rows matched" error. Deduplicate first (e.g. `ROW_NUMBER()` and keep the latest).

---

Q. What is idempotency? (**common interview question**)

A. (Teacher's definition) "Idempotency is the noun and idempotent is the adjective. An idempotent operation is an operation that you can do over and over again and be sure that only the results that need to be updated are actually executed, and you are not going to get any duplicates as a result of that operation." It matters for automated pipelines: "if you have an automated job that is going to potentially run multiple times, you don't want multiple runs of that job to give you thousands of rows of duplicate data." Delta MERGE gives you that: "updates will be applied, rows as they already are will not be affected." "Memorize that word and its definition."

Expanded: the formal meaning is **running it once or many times gives the same end state**. A plain `INSERT` (or `append`) isn't idempotent: run it twice and you get duplicates. A keyed MERGE, an overwrite of one partition, or a streaming write with a checkpoint are. Small nuance: re-running the class MERGE still writes a new table version (the matched row is rewritten with the same value), but the **data** ends up identical, which is what counts.

| Idempotent | Not idempotent |
|---|---|
| `MERGE` on a key | `INSERT INTO` / `.mode("append")` with no key check |
| `INSERT OVERWRITE` of a partition / `replaceWhere` | `UPDATE t SET count = count + 1` |
| Auto Loader / streaming write with a checkpoint | Re-reading the whole folder every run and appending |

---

Q. What did the CDC-style merge do?

A. (Evan, demo) It showed one MERGE transaction processing different change types: after it, 001 should have 12 bikes, 002 should be deleted and 004 should be inserted. He wrote his own check query: 002 was gone, 004 was there, 003 unchanged.

```sql
-- from the class demo (not exact)
MERGE INTO <catalog>.default.delta_demo AS target
USING (
  SELECT '001' AS station_id, 12   AS bikes_available, 'UPDATE' AS op
  UNION ALL
  SELECT '002' AS station_id, NULL AS bikes_available, 'DELETE' AS op
  UNION ALL
  SELECT '004' AS station_id, 6    AS bikes_available, 'INSERT' AS op
) AS source
ON target.station_id = source.station_id
WHEN MATCHED AND source.op = 'DELETE' THEN DELETE
WHEN MATCHED THEN UPDATE SET target.bikes_available = source.bikes_available
WHEN NOT MATCHED AND source.op <> 'DELETE' THEN
  INSERT (station_id, bikes_available) VALUES (source.station_id, source.bikes_available);
```

Expanded: this is the shape of applying a **CDC feed** (rows tagged insert / update / delete) to a table. In Lakeflow Declarative Pipelines the same thing is done for you with `AUTO CDC` / `APPLY CHANGES INTO` (Training 29). Delta can also produce a change feed of its own (**Change Data Feed**, `delta.enableChangeDataFeed = true`, read with `table_changes()`), so downstream tables can process only what changed.

---

# CDC vs. SCD

Q. What is CDC?

A. (Teacher's definition) "Change data capture is not a specific technology. It's a combination of techniques. The idea of change data capture is that you want to have a record of all of the changes of the data as they happen." The `DESCRIBE HISTORY` table is a sort of example: "it tracks every single change that happens to another table." "The most common application for CDC is in migrations": if you migrate a **hot table** (one users are still writing to), the copy is out of date by the time it finishes. "CDC is basically the way that you are going to be able to track what changes have happened to the table since you began the migration, and then to schedule a subsequent migration to migrate all of those until you are right up to being current, and then you can switch the endpoint to the new table."

Expanded: migrations are a great example, but in day-to-day work CDC is just as common for **continuous replication**: streaming every insert, update and delete from an operational database (OLTP) into the lake or warehouse, so analytics stays current without full reloads.

| CDC method | How | Example tools |
|---|---|---|
| **Log-based** (best) | Read the database's transaction log (MySQL binlog, Postgres WAL, SQL Server CDC) | Debezium → Kafka, AWS DMS, Fivetran, Datastream |
| Timestamp / query-based | Poll for rows where `updated_at > last_run` | Simple jobs; misses hard deletes |
| Trigger-based | Database triggers write changes to an audit table | Older systems; slows writes |
| Table-format change feed | Delta Change Data Feed, Iceberg incremental reads | Lakehouse Silver → Gold |

---

Q. What is SCD, and how is it different from CDC? (**common interview trap**)

A. (Teacher's definition) Interviewers "like to confuse you by mixing up a similar but absolutely not the same concept, which is called SCD, that's slowly changing dimensions. SCD is also a way of tracking changes, but in a much more gradual and long-term sense." Type 0 is that "you just don't track the changes." Type 1 "you overwrite the original record with every change." Type 2 is "the process of tracking changes over a long period of time by adding a column that contains the timestamp of the time when the record was last updated… so you can query the table and come up with a history of changes." Type 2 is "the most frequently asked about in interviews." His example: Amazon keeps every address you've ever shipped to. Addresses change every few months to every 20 years, and companies want to know when they changed.

Expanded (correction): Type 2 isn't just a "last updated" column. Type 2 **adds a new row** for every change and keeps the old row, marked as no longer current. A "last updated" timestamp on one row would only tell you when it changed, not what it used to be. Type 0 more precisely means the attribute is **never allowed to change** (the original value is kept, e.g. original sign-up date).

| Type | On a change | History? | Example |
|---|---|---|---|
| 0 | Keep the original value; ignore changes | No | Date of birth, original sign-up date |
| 1 | Overwrite the old value | No | Fixing a typo in a name |
| **2** | Close the old row (`valid_to`, `is_current = false`) and insert a new row (`valid_from`, `is_current = true`) | **Full** | Customer address history |
| 3 | Add a "previous value" column | One step back | Current and previous region |

Example SCD Type 2 rows:

| customer_key | customer_id | city | valid_from | valid_to | is_current |
|---|---|---|---|---|---|
| 1 | C42 | Dallas | 2019-03-01 | 2023-06-14 | false |
| 2 | C42 | Austin | 2023-06-15 | 9999-12-31 | true |

| | CDC | SCD |
|---|---|---|
| What | **Capturing** changes from a source as they happen | **Storing** history of dimension attributes in the warehouse |
| Time scale | Seconds to minutes | Months to years |
| Where | Source → pipeline (replication, migrations) | Dimension tables in the warehouse / Gold |
| Relationship | CDC is often the **input** that feeds an SCD Type 2 MERGE | |

The SCD Type 2 MERGE pattern is in [Training 29](Training%2029.md#delta-lake-operations-roadmap-topic-not-taught-in-class).

---

# Auto Loader

Q. What is Auto Loader?

A. (Teacher's definition) "An occasional interview topic… it's for incrementally ingesting data as it is delivered, whether that's by an actual incremental job, by a streaming job, whatever you are using to consistently deliver new data into your Databricks environment. Auto Loader is there in order to facilitate that data actually coming into the environment and being able to be made use of." There's no `use_autoloader()` call: "we use format cloudFiles, option cloudFiles.format and then whatever format we feel like using."

Expanded: the problem it solves: a landing folder that keeps getting new files. Re-reading the whole folder every run is slow and creates duplicates; tracking "which files did I already load" by hand is error-prone. Auto Loader is a **Structured Streaming source** that discovers only **new** files, remembers what it loaded (in the checkpoint), and can infer and evolve the schema. The Training 29 Lakeflow pipeline used it behind the scenes.

| Option | Purpose |
|---|---|
| `.format("cloudFiles")` | Use Auto Loader |
| `cloudFiles.format` | The file type: `json`, `csv`, `parquet`, `avro`, `text`, `binaryFile`… |
| `cloudFiles.schemaLocation` | Where the inferred schema and its changes are stored (needed if you don't pass `.schema()`) |
| `cloudFiles.schemaEvolutionMode` | `addNewColumns` (default), `rescue`, `failOnNewColumns`, `none` |
| `cloudFiles.useNotifications` | File notification mode (queue events) instead of directory listing, for huge folders |

---

Q. How did the Auto Loader demo go? (step by step)

A. (Evan, demo)

| Step | What happened |
|---|---|
| 1 | Plain batch read for comparison: `NameError` because `source_path` wasn't defined |
| 2 | Fix: opened the previous day's notebook and did **Run all** so the variable existed. Then started a fresh notebook from the tutorial instead, setting the paths up front |
| 3 | Verify access to the JSON files (`multiLine` and `recursiveFileLookup` = true), `printSchema()` |
| 4 | An AI-generated nested `StructType` schema for the Citi Bike JSON ("the kind of thing where you just have to sit and write it out… thanks to AI we can expedite that") |
| 5 | Define a **checkpoint location** |
| 6 | `readStream.format("cloudFiles")` → `bronze_stream`, a streaming DataFrame |
| 7 | `writeStream` to a Delta table with `trigger(availableNow=True)` and `awaitTermination()`; display `last_updated`, `source_file`, `ingested_at` |
| 8 | Count rows by source file: 1 per file |
| 9 | Run the ingestion again: still **1230** rows (no new files, nothing reloaded) |
| 10 | Create one new JSON file with `json.dumps`, run Auto Loader again: **1231** rows |

```python
# from the class demo (not exact)
from pyspark.sql import functions as F

source_path     = "<landing folder with the Citi Bike JSON>"
checkpoint_path = "<checkpoint folder>/bronze_station_status"
target_table    = "<catalog>.<schema>.bronze_station_status"

bronze_stream = (
    spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("multiLine", "true")
        .schema(station_status_schema)          # the AI-generated nested schema
        .load(source_path)
        .withColumn("source_file", F.col("_metadata.file_path"))
        .withColumn("ingested_at", F.current_timestamp())
)

query = (
    bronze_stream.writeStream
        .format("delta")
        .option("checkpointLocation", checkpoint_path)
        .trigger(availableNow=True)
        .toTable(target_table)
)
query.awaitTermination()

spark.table(target_table).count()   # 1230, then 1231 after one new file
```

Expanded: "1 per file" in step 8 is expected: each Citi Bike file is one multi-line JSON snapshot, so it becomes one Bronze row with a nested array of stations (Silver flattens it). Evan's own verdict: the tutorial "maybe isn't super representative of the way that it's used in real life," because nothing arrived automatically. They ran it by hand after adding a file. In real life data arrives at a regular pace from a source (e.g. an Event Hubs capture or an app writing files), and the job runs on a schedule or continuously.

---

Q. What's the difference between readStream and writeStream?

A. (Evan) `readStream` "takes files in from an existing stream of data and it makes them available" to do operations. That's "as opposed to a write stream, which takes a read stream and periodically writes its data to an output location." `awaitTermination()` means "we expect this to just keep on executing" (unless the trigger says otherwise).

Expanded:

| Trigger | Behavior | Use |
|---|---|---|
| (default) | Micro-batch every ~0.5 s, runs forever | Always-on streaming |
| `processingTime="5 minutes"` | Micro-batch every 5 minutes, runs forever | Near-real-time on a cluster that stays up |
| `availableNow=True` | Processes everything new (in several batches), **commits its progress and stops** | Incremental batch from a scheduled Job: the cheap, common choice |
| `once=True` | Like availableNow in one batch (deprecated) | Older code |

---

Q. Why are checkpoints important?

A. (Teacher's definition) "Checkpointing is a fault tolerance mechanism that we have in streaming services. Checkpointing is also a concept in Kafka and Kinesis and Event Hubs." For Auto Loader, "checkpointing tracks ingestion progress so that previously processed files are not repeatedly loaded. So it's a way of achieving idempotency in a streaming environment." Compared with deduplication: "deduplication as we've already seen will remove duplicate records from an existing table, but not necessarily be something that we are going to want to run on every single ingestion. Checkpointing is a more convenient method for doing the same thing."

Expanded: the checkpoint folder stores which files (or offsets) were processed and which batch was committed. If the job crashes, it restarts from the last committed batch: nothing lost, nothing loaded twice. With a Delta sink that gives **exactly-once** results.

| Rule | Why |
|---|---|
| One checkpoint per stream (per target) | Two streams sharing one checkpoint corrupt each other's progress |
| Never delete it casually | Deleting it makes Auto Loader reload **every** file (duplicates) |
| Keep it next to the table, not in temp storage | It must survive cluster restarts |
| Checkpoint ≠ dedup of the data itself | If the same record arrives in two different files, both load. You still need a MERGE or dedup on a key for that |

| | Checkpointing | Deduplication |
|---|---|---|
| Prevents | Reprocessing the same **file / offset** | The same **record** appearing twice |
| When | Automatically, every batch | A step you add (`dropDuplicates`, `ROW_NUMBER`, MERGE) |
| Cost | Cheap | Can be expensive on big tables |

---

Q. What is schema evolution (recap)?

A. (Teacher's definition) "It's a way of being able to automatically account for schema changes that are done on streaming data." Example: ingesting from many hospitals; each one's management decides its own systems and schemas, and one might add or remove a column. "Traditionally this would break a Spark pipeline, because we need to know what the columns are if we're going to ingest the data into a data frame." How you handle it depends on the technology: a **Protobuf** schema has to be compiled first (good for app developers, more confusing for data engineers); Evan prefers **Avro**, where the schema "can be changed and monitored without needing a compilation step."

Expanded: Auto Loader handles it with `cloudFiles.schemaLocation` + `schemaEvolutionMode`. In the default `addNewColumns` mode, when a new column appears the stream **stops once** with an `UnknownFieldException`, records the new schema, and works after a restart (a Job with retries restarts it for you). Columns that don't fit the schema go to `_rescued_data` instead of being lost. More in [Training 29](Training%2029.md#delta-lake-operations-roadmap-topic-not-taught-in-class).

The tutorial's "monitor the stream for two minutes" step didn't work: the status said **stopped**, because "if it's from within the same notebook, you can't really monitor one cell with another cell, because the cells have to execute their own code and finish executing in sequence." Use two notebooks (or the streaming dashboard under the cell) for that.

---

# Lakeflow Jobs

Q. What is a Databricks (Lakeflow) Job?

A. (Evan, demo) A way to run notebooks as **tasks** in order, under **Jobs & Pipelines**. He built Citi Bike Bronze → Silver → Gold as a Job.

Expanded: a Job is Databricks' built-in **orchestrator**. It has one or more **tasks** (notebook, Python script, SQL, a Lakeflow pipeline, dbt, JAR, another job…), **dependencies** between them (a DAG), compute, **triggers** (schedule, file arrival, table update, continuous) and settings like **retries**, timeouts and alerts. "Lakeflow Jobs" is the new name for Databricks Workflows ([Training 29, Databricks Lakeflow](Training%2029.md#databricks-lakeflow-spark-declarative-pipelines) explains the Lakeflow family).

---

Q. How did the Job demo go? (step by step)

A. (Evan, demo)

| Step | What happened |
|---|---|
| 1 | Bronze notebook: the same Auto Loader `writeStream` as before |
| 2 | Silver code (PySpark): flatten the nested array, cast fields, select and transform columns, filter. Ran it ("transformation completed") and queried the Silver table |
| 3 | Gold code: a window function to keep the latest snapshot per station per hour, then hourly aggregates (active stations, bikes available, docks available) |
| 4 | **Mistake**: Jobs & Pipelines → **ETL pipeline**, named `citibike_bronze_silver_gold`. No **Add task** button anywhere |
| 5 | Fix: it was a pipeline, not a job. Jobs & Pipelines → Create → **Job** |
| 6 | Renamed the notebook to `citibike_autoloader_demo`. Task 1: type **Notebook**, source Workspace, that notebook, **serverless** compute. Named Bronze ingestion + Silver transformation, because Bronze and Silver code were in one notebook |
| 7 | New notebook `citibike_gold_transformation` with the Gold code; test-ran it, then cancelled |
| 8 | Task 2: Gold transformation, **depends on** task 1, **Run if dependencies: All succeeded** |
| 9 | **Run now**, then watched the run in the job's run view |

Evan's lesson: "I was supposed to create notebooks beforehand." Create and test each task's notebook first, then wire them into the Job.

```python
# Gold notebook, from the class demo (not exact)
from pyspark.sql import functions as F
from pyspark.sql.window import Window

silver = spark.table("<catalog>.<schema>.station_status_silver")
hourly = silver.withColumn("snapshot_hour", F.date_trunc("hour", "snapshot_time"))

w = Window.partitionBy("station_id", "snapshot_hour").orderBy(F.col("snapshot_time").desc())

latest_per_station = (
    hourly.withColumn("rn", F.row_number().over(w))
          .filter(F.col("rn") == 1)            # dedup: latest snapshot per station per hour
)

gold = (
    latest_per_station.groupBy("snapshot_hour")
        .agg(
            F.countDistinct("station_id").alias("active_stations"),
            F.sum("num_bikes_available").alias("bikes_available"),
            F.sum("num_docks_available").alias("docks_available"),
            F.avg("num_bikes_available").alias("avg_bikes_per_station"),
        )
)

gold.write.mode("overwrite").saveAsTable("<catalog>.<schema>.station_hourly_gold")
```

Expanded (correction): Evan described the Silver code as being "in the format of DLT Lakeflow." It was ordinary PySpark in a notebook (read a table, transform, `write`), run as a Job task. Lakeflow **Declarative Pipelines** (DLT) code is different: functions decorated with `@dlt.table` / `@dp.table` that the pipeline engine runs and orders for you (Training 29).

---

Q. ETL pipeline vs. Job: what's the difference? When would you use which? (student question)

A. (Evan) "It's entirely up to you in the situation on the ground… It depends on the amount of automation that you want to do, how regularly you need to run the job." If data arrives weekly at an unknown time and a human should look at it, a regular notebook run by hand is fine. "All of these things are things that you can do in Databricks, but they're not necessarily things that you have to do… You have to at least be aware of what all of this stuff is to talk about it in interviews." The student found a plain Job much easier to set up than the ETL pipeline version.

Expanded:

| | Lakeflow **Job** | Lakeflow **ETL pipeline** (Declarative Pipelines / DLT) |
|---|---|---|
| What it is | An orchestrator: runs tasks in a DAG | A framework: you declare tables, the engine builds and maintains them |
| Code | Any notebook / script / SQL / dbt | `@dlt.table` Python or `CREATE STREAMING TABLE` / `MATERIALIZED VIEW` SQL |
| Order | You set dependencies | Inferred from which table reads which |
| Extras | Schedules, retries, alerts, many task types | Data quality expectations, auto checkpoints, CDC (`AUTO CDC`), lineage graph |
| Together | A Job can have a **pipeline task**, so a Job often schedules a pipeline | |

---

Q. What happens to downstream tasks when an upstream task fails? (homework question)

A. (Shown in the Job settings, not tested in class.) With the default **Run if dependencies: All succeeded**, if Bronze/Silver fails, Gold is **not run** (marked *Upstream failed*). That's why Gold should depend on Silver: otherwise Gold would aggregate old or half-written data and publish wrong numbers.

Expanded:

| Setting | What it does |
|---|---|
| Run if: **All succeeded** (default) | Run only if every upstream task succeeded |
| At least one succeeded / None failed / All done / At least one failed / All failed | Other run-if conditions, e.g. a cleanup or alert task that runs **All done** |
| **Retries** (per task) | Re-run a failed task N times with a delay |
| **Repair run** | Re-run only the failed task and those after it, not the whole job |

Why a failed task might succeed on retry: a **transient** problem, e.g. a network timeout, a cloud API throttling you, a spot/serverless capacity issue, a file still being written when the task read it, or a concurrent-write conflict on a Delta table. A bug in the code or bad data will fail again.

---

Q. Are Databricks Jobs a form of ADF? (student question)

A. (Evan) "That is completely separate. ADF is one scheduler and Databricks Jobs is a different scheduler. If we were using ADF we would have brought up the ADF interface from within the Azure portal rather than doing anything directly within Databricks."

Expanded: in real Azure shops both are common: ADF does copy and orchestration across many Azure services, and calls a **Databricks Notebook activity** (or a Databricks Job) for the Spark work. If everything is in Databricks, Lakeflow Jobs alone is simpler. ADF notes are in the Training 28 material; Synapse has the same ADF engine built in as **Synapse Pipelines** ([Training 31](Training%2031.md#azure-synapse-analytics)).

| | Azure Data Factory | Lakeflow Jobs |
|---|---|---|
| Lives in | Azure portal / ADF Studio | The Databricks workspace |
| Strength | 90+ connectors, Copy activity, orchestrating many services | Running Databricks notebooks, pipelines, SQL, dbt |
| Like on AWS | Step Functions / Glue Workflows / MWAA | — |

---

Q. Is ETL outdated? (student question)

A. (Evan) "There's no reason to say that ETL is outdated. It isn't actually outdated." If you're designing from scratch, "ELT is largely considered to be the most modern way to design and build a new data pipeline." But ETL still works fine on new projects, and you may be hired onto a project with older ETL jobs that "still do what they're supposed to do… there isn't a need to think 'oh, there's ETL here that needs to be converted to ELT.'" "ETL is actually the better one if what you are doing is not building a multi-layered data lakehouse," e.g. processing data on its way to a Postgres instance in RDS or locally, because "a regular Postgres instance isn't really designed to do anything that resembles ELT." ELT came in with the innovations behind Databricks and Snowflake. "For a bronze-silver-gold data lakehouse, ELT is going to be the preferred pattern."

Expanded:

| | ETL | ELT |
|---|---|---|
| Order | Transform **before** loading | Load raw, transform **inside** the platform |
| Raw data kept? | Usually not | Yes (Bronze), so you can reprocess |
| Fits | Small/medium targets (Postgres, RDS), compliance (mask before load) | Lakehouses and cloud warehouses (Databricks, Snowflake, BigQuery) |
| Typical tools | PySpark, Glue, SSIS, Informatica | dbt, Databricks SQL, Lakeflow pipelines |

---

# MLflow and tabular ML

Q. What is MLflow?

A. (Teacher's definition) "A lot of people talk about MLflow as though it were a Databricks service, but it is not, and I can prove that to you by running it on-prem." MLflow is "basically our window into the one kind of data endpoint that we haven't talked about yet": **tabular ML**. "MLflow is the environment that you use to host the model, train the model and deploy the model."

Expanded: MLflow is an **open-source** platform for the ML lifecycle. Databricks created it (2018) and runs a managed version inside the workspace, but anyone can `pip install mlflow`.

| MLflow piece | What it does |
|---|---|
| **Tracking** | Logs each training **run**: parameters, metrics, artifacts, code version. Runs are grouped into **experiments** |
| **Models** | A standard package format ("flavors": sklearn, pytorch, xgboost…) with a **signature** (input/output schema) |
| **Model Registry** | Named, **versioned** models with aliases (e.g. `@champion`). On Databricks it lives in **Unity Catalog** |
| **Serving** | Deploy a registered model as a REST endpoint (Databricks Model Serving, or `mlflow models serve`) |
| **Tracing / GenAI** | Records each step of an LLM app (prompts, tool calls, retrieval, outputs, latency) |

Expanded (correction): MLflow doesn't train the model itself. Your code (scikit-learn, PyTorch…) trains it on some compute (a Databricks cluster, serverless, your laptop). MLflow **records** the training, **stores and versions** the result, and helps **deploy** it.

---

Q. What is tabular ML, and how is it different from an LLM?

A. (Teacher's definition) "Machine learning that is done with relational databases such as SQL tables or Spark data frames." It "makes use of traditional machine learning models, not LLMs." "An LLM is like ChatGPT or Claude, where you ask it a natural language question and you get a natural language response. Traditional ML models are basically statistical analysis programs in which the machine is trained to seek out a certain result and then iteratively become better and better at achieving that result over time." Why learn it: **MLOps** is a growing related field, and fraud detection is one of the most common narrative stories.

Expanded:

| | Tabular (traditional) ML | LLM |
|---|---|---|
| Input | Rows and columns of features | Text (and images, audio) |
| Output | A number (regression) or class (classification), e.g. "fraud: 0.93" | Generated text |
| Models | Linear/logistic regression, random forest, gradient boosting (XGBoost, LightGBM) | GPT, Claude, Llama |
| Training cost | Minutes on a normal cluster | Huge (Evan: building your own LLM "is a fool's errand") |
| Libraries | scikit-learn, XGBoost; PyTorch / TensorFlow for deep learning | PyTorch, Hugging Face |

---

Q. How does a fraud-detection pipeline work? (the "canned" narrative)

A. (Evan) "One of the easiest pipeline stories to put together… every single financial organization does fraud detection," so anyone with a bank or payments company on their profile could have worked on one. The flow: a card is used (by the owner or a bad actor) → the card company's servers process it → it reaches the organization's endpoint → a streaming framework (Kafka, Kinesis, Event Hubs, Pub/Sub) brings it in → optional processing → the model hosted with MLflow flags it as **potentially fraudulent** or **OK**. OK transactions complete. Flagged ones trigger notifications (email, SMS, push); the customer confirms it was them, or says no, and the bank refunds, cancels the card and sends a new one. "The data is 100% of the time always going to be streaming in a fraud detection pipeline. Batches don't work, because there is time pressure."

Expanded (correction): the **scoring** of each transaction is real-time, but a fraud system isn't streaming-only. Model **training**, historical feature computation (e.g. a customer's 90-day spending pattern) and reporting are **batch**. Real-time scoring is also often a synchronous call to a **model serving endpoint** from the authorization service, with the stream used for features and logging. The data engineer's part of the story: build the streaming ingestion, compute and serve the **features**, prepare training data, and keep it all reliable.

```
Card swipe → payment processor → Kafka / Event Hubs → feature computation (Spark Structured Streaming)
                                                        │
                                                        ▼
                                  model serving endpoint (registered MLflow model) → OK / flag
                                                        │ flag
                                                        ▼
                                         notify customer → confirm or block + reissue card
Batch side: Delta history → training features → train + log with MLflow → register new version
```

---

Q. Who does what between data science and data engineering / MLOps?

A. (Evan) Designing the model "is outside of the data engineer's wheelhouse." The data science team builds it (scikit-learn, PyTorch, TensorFlow) and delivers it, probably as a Python file, JAR or other package. Data engineers and MLOps people deploy it: in production on Databricks you'd run MLflow in one workspace to host and deploy the model, and probably a separate workspace with its own MLflow to train the next iteration. Data scientists are "mainly statisticians who know a little bit of Python and don't really know about infrastructure and deployments." Training means giving the model data and getting statistics on how close it was; "the best model is the one with the highest statistical scores, but that is not always true. There's such a thing as overfitting."

Expanded: **overfitting** means the model memorized the training data (including its noise), so it scores great in training and badly on new data. That's why you test on data the model never saw.

---

Q. What's in the MLflow UI? (local demo)

A. (Evan, demo) He ran `mlflow server` on his own machine and opened `localhost:5000`.

| UI area | What it's for |
|---|---|
| **Model training** | Tabular ML: experiments, runs, the model registry |
| **GenAI** | Working with LLMs (can also host an LLM, though Evan wouldn't use MLflow for that) |
| Experiments list | His old experiment showed "No runs logged" (an old PyTorch run had disappeared) |
| Model registry | Register and version a model so it can be hosted |
| **Traces** | What made Evan go from not caring about MLflow to finding it "very, very valuable" |

---

Q. What are MLflow traces, and why are they useful?

A. (Teacher's definition) "Traces are insanely useful when you are trying to build an AI-powered application." In application code, "all that's accessible to you is the prompt and the response. The thinking process is not accessible to you. Traces in MLflow make it accessible to you. So if you ever wonder why did the AI make the decision that it made… with traces you can go and read the AI's thought process for that particular prompt." They're even more useful for multi-agent apps, like his first agentic framework, **CrewAI**, where agents talk to each other and "all of that behind-the-scenes work gets lost in the normal application logs."

Expanded (correction): a trace records the **steps your application took**, as a tree of **spans**: each LLM call with its exact input and output, tool calls, retrieval results, agent-to-agent messages, timings, token counts and errors. That's what lets you see why an answer went wrong. It shows the model's own internal reasoning only when the model provider returns it (some return reasoning text or summaries, many hide it). You turn it on with e.g. `mlflow.openai.autolog()` / `mlflow.langchain.autolog()` or the `@mlflow.trace` decorator.

---

Q. How did the Databricks MLflow demo go? (step by step)

A. (Evan, demo) Goal from his tutorial: read Citi Bike **Silver**, train a model in Python + scikit-learn to predict `num_bikes_available`, track it with MLflow, register it in the **Unity Catalog model registry**, and run batch predictions. They got as far as training and logging.

| Step | What happened |
|---|---|
| 1 | Imports in a new notebook. MLflow and scikit-learn are **already installed** in Databricks (otherwise `%pip install ...` then restart Python). The notebook offered "Try machine learning in Genie Code"; Evan skipped it ("MLflow is talked about in interviews and Genie Code is not") |
| 2 | `mlflow.set_tracking_uri("databricks")`, `mlflow.set_registry_uri("databricks-uc")` (models will register in Unity Catalog) |
| 3 | Read the Silver table and check it's visible |
| 4 | Features: station identity + time features (hour, day of week), with filters to validate the data |
| 5 | `orderBy(...).limit(...).toPandas()` to a **pandas** DataFrame (`pdf`) |
| 6 | Time-based train/test split: **40,000** training rows, **10,000** test rows |
| 7 | `mlflow.set_experiment(path)`: "does not exist… creating a new experiment" (fine) |
| 8 | Model: a `ColumnTransformer` with a `OneHotEncoder` for station_id + a **random forest** |
| 9 | `with mlflow.start_run():` fit, predict, log params and metrics (MAE, RMSE), infer a signature, log the model. Printed a run ID, MAE, RMSE and model URI |
| 10 | Warning: "inferred schema contains integer columns" (didn't stop it) |
| 11 | **MAE = 10.067**: "not very accurate… it's wrong by 10 bikes on average." RMSE was higher than MAE |
| 12 | Looked for the run under **Experiments**: it didn't appear, even after Run all. Registering the model and batch predictions were left for a later class |

```python
# from the class demo (not exact)
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from pyspark.sql import functions as F
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

mlflow.set_tracking_uri("databricks")
mlflow.set_registry_uri("databricks-uc")

df = spark.table("<catalog>.<schema>.station_status_silver")
features_df = (
    df.select("station_id", "snapshot_time", "num_bikes_available")
      .filter(F.col("num_bikes_available").isNotNull())
      .withColumn("hour", F.hour("snapshot_time"))
      .withColumn("day_of_week", F.dayofweek("snapshot_time"))
)

pdf = features_df.orderBy("snapshot_time").limit(50000).toPandas()   # pandas, not a PDF file

cutoff = pdf["snapshot_time"].quantile(0.8)                           # time-based split
train_df, test_df = pdf[pdf.snapshot_time <= cutoff], pdf[pdf.snapshot_time > cutoff]
features, target = ["station_id", "hour", "day_of_week"], "num_bikes_available"
X_train, y_train = train_df[features], train_df[target]
X_test,  y_test  = test_df[features],  test_df[target]

mlflow.set_experiment("/Users/<your-user>/citibike_mlflow_class")

model = Pipeline([
    ("prep", ColumnTransformer(
        [("station", OneHotEncoder(handle_unknown="ignore"), ["station_id"])],
        remainder="passthrough")),
    ("rf", RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)),
])

with mlflow.start_run() as run:
    mlflow.log_params({"n_estimators": 50, "max_depth": 10})
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = mean_squared_error(y_test, preds) ** 0.5
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("rmse", rmse)
    signature = infer_signature(X_train, preds)
    info = mlflow.sklearn.log_model(model, "model", signature=signature)
    print(run.info.run_id, mae, rmse, info.model_uri)
```

Expanded: where the run went, and the warning:

| Issue | Explanation / fix |
|---|---|
| Run "not in Experiments" | `set_experiment()` with a path creates a **workspace experiment** at that path. Find it by clicking the "View run / View experiment" link MLflow prints under the cell, in the left sidebar under **Experiments** (Machine Learning / AI section), or in the Workspace browser at that path. The notebook's **Experiment** icon in the right panel shows only the notebook's default experiment, not one set by path |
| "Inferred schema contains integer columns" | MLflow warns that integer columns can't hold missing values, so a future input with a null would fail schema checks. Fix: cast integer feature columns to `float64` before `infer_signature` (it's only a warning) |
| Not done yet | Register: `mlflow.register_model(info.model_uri, "<catalog>.<schema>.citibike_bikes_model")`; batch predict: `mlflow.pyfunc.spark_udf(spark, "models:/<catalog>.<schema>.citibike_bikes_model/1")` on a Spark DataFrame |

---

Q. What do the ML terms in the demo mean? (Evan skipped several)

A. (Evan) He left most of it as "data scientist territory": "defining X and Y variables, that is data scientist territory." He said "I don't even know what one-hot encoder does," "RMSE, I don't even know what that is," and "we're doing a random forest, not a regression."

Expanded (correction): a random forest **can** be a regression model. "Regression" means predicting a **number**; "random forest" is the algorithm. `RandomForestRegressor` predicts a number (bikes available), so this was regression with a random forest, not linear regression.

| Term | Meaning |
|---|---|
| **Features (X)** | The input columns the model learns from (station, hour, day of week) |
| **Target / label (y)** | What it predicts (`num_bikes_available`) |
| **Train/test split** | Train on one part, score on data it never saw. **Time-based** (train on earlier, test on later) mimics real use and avoids leaking the future |
| **Linear regression** | Fits a straight-line trend through the points: is the trend up or down? |
| **Random forest** | Many decision trees on random samples of rows and columns, averaged |
| **One-hot encoder** | Turns a category (station "001", "002"…) into 0/1 columns, one per value, because models need numbers |
| **MAE** (mean absolute error) | Average size of the error, in the target's units: "off by 10 bikes on average" |
| **RMSE** (root mean squared error) | Square the errors, average, take the root. Punishes big misses more. RMSE ≥ MAE always; a much bigger RMSE means some large errors |
| **Overfitting** | Great on training data, bad on new data |
| **Parameter** (MLflow) | An input setting you chose (`max_depth = 5`) |
| **Metric** (MLflow) | A measured result (`accuracy = 0.92`, `mae = 10.07`) |
| **Artifact** (MLflow) | A file saved with the run: the model itself, plots, a feature list |
| **Experiment vs. run** | An experiment is a folder of attempts at one problem; a run is one training attempt with its params, metrics and artifacts |
| **Signature** | The model's expected input columns/types and output type |

---

Q. What's the difference between a pandas and a Spark DataFrame?

A. (Evan) "`toPandas()` is a built-in function of Spark which just takes the Spark data frame and converts it to a pandas data frame… a pandas data frame cannot be distributed across a cluster of computers, whereas a Spark data frame can." "PDF" in the code means a pandas DataFrame, not a PDF file.

Expanded: `toPandas()` pulls all the rows to the **driver**'s memory, which is why the demo used `limit()` first. scikit-learn needs pandas/NumPy, so this is a normal pattern for small training sets. For big data, use Spark ML or `pandas_udf` / `applyInPandas`.

---

Q. What will an interviewer ask about MLflow / MLOps, and what's your takeaway? (student question)

A. (Evan) The ML team should hand you "the code that has the X train and the Y train and all of the model imports… in a nice neat little package… It's our job to just deploy the infrastructure, in either Databricks or on-prem, and bring the model in and either train it ourselves or say 'the infrastructure is set up now, ML people, train the model.'" A typical question is as general as "have you ever done anything with MLOps / MLflow?" or "break down how the deployment went for an ML model you deployed in production." A good answer: "I deployed a fraud detection model for XYZ Bank. My main part of the process was cleaning and preparing the data to be passed to the model. I worked a little bit with the deployment, but it wasn't my full responsibility." "MLOps basically is using MLflow to train and deploy models which are built by somebody else, but we provide the data."

Expanded: you aren't expected to be an ML expert for data engineering roles. Know the vocabulary (experiment, run, params, metrics, artifacts, registry, serving), where MLflow sits in Databricks, and the data engineer's part (features, training data, pipelines, monitoring).

---

# Unity Catalog (roadmap topic, only touched in class)

Q. Where did Unity Catalog show up today?

A. (Evan) It's the default in the class workspace ("Unity Catalog is what we're working on by default right now"). Tables were named `catalog.default.table`, and the MLflow demo set `registry_uri("databricks-uc")` so models register in Unity Catalog.

Expanded: **Unity Catalog** is Databricks' governance layer: one place for permissions, lineage, auditing and discovery across workspaces, for tables, views, volumes (files), functions and ML models.

| Concept | Meaning |
|---|---|
| **Three-level namespace** | `catalog.schema.table` (e.g. `main.citibike.station_status_silver`). `hive_metastore` is the old two-level one |
| **Metastore** | The top container, one per region, attached to workspaces |
| **Managed vs. external table** | Managed: UC owns the storage location and lifecycle. External: data in your own ADLS path |
| **Volume** | Governed files (e.g. `/Volumes/catalog/schema/landing/` in the homework's Auto Loader code) |
| **Storage credential / external location** | How UC is allowed to reach your ADLS (via a managed identity) |
| **GRANT** | `GRANT SELECT ON TABLE main.citibike.gold TO \`analysts\`;` Privileges like `USE CATALOG`, `USE SCHEMA`, `SELECT`, `MODIFY`, `CREATE TABLE` |
| **Lineage** | Automatic table- and column-level lineage: which job/notebook read what and wrote what |
| **Row filters / column masks** | A SQL function attached to a table that hides rows or masks a column depending on who's querying (e.g. only the EU team sees EU rows) |

---

# Interview-ready from today

| Question | Your one-line answer |
|---|---|
| What is Delta MERGE? | An upsert: match source rows to the target on a key, then update, insert or delete in one atomic commit |
| What is time travel? | Querying a table as it was at an earlier version or timestamp (`VERSION AS OF` / `TIMESTAMP AS OF`), using the Delta log. Delta, Iceberg and Hudi all support it |
| How far back can Delta time travel go? | As long as the log and data files exist: history 30 days and files 7 days after VACUUM by default, configurable. Snowflake caps at 90 days |
| RESTORE vs. MERGE vs. VACUUM? | RESTORE rolls back to an old version (as a new commit); MERGE upserts new data; VACUUM deletes unreferenced old files and limits time travel |
| What is idempotency? | Running an operation once or many times gives the same result, with no duplicates. Needed for pipelines that can rerun (MERGE, checkpoints, partition overwrite) |
| CDC vs. SCD? | CDC captures every change from a source as it happens (replication, migrations). SCD stores long-term history of dimension attributes in the warehouse. CDC often feeds an SCD Type 2 MERGE |
| What is SCD Type 2? | Each change closes the old row (`valid_to`, `is_current = false`) and inserts a new current row, keeping full history |
| What does Auto Loader solve? | Incremental file ingestion: `cloudFiles` picks up only new files in a folder, tracks them in a checkpoint, and handles schema inference and evolution |
| Why checkpoints? | They record what was processed, so a restart resumes without loss or reloading, giving exactly-once with a Delta sink |
| What does `availableNow=True` do? | Processes all new data, commits progress and stops: incremental batch on a schedule |
| What is a Lakeflow Job? | Databricks' orchestrator: tasks (notebooks, pipelines, SQL…) in a DAG with dependencies, schedules, retries and alerts |
| What if an upstream task fails? | With "All succeeded", downstream tasks don't run (upstream failed). Fix and use repair run to rerun only failed tasks |
| Databricks Jobs vs. ADF? | Two different schedulers. Jobs run inside Databricks; ADF orchestrates many Azure services and can call Databricks |
| Is ETL outdated? | No. ELT is preferred for lakehouses; ETL still fits simpler targets like Postgres and existing pipelines that work |
| What is MLflow? | Open-source ML lifecycle platform (made by Databricks): tracking experiments and runs, model packaging, a versioned registry and serving |
| Experiment vs. run; param vs. metric vs. artifact? | An experiment groups runs; a run is one training attempt. Params are inputs, metrics are measured results, artifacts are saved files like the model |
| What is the Model Registry? | A versioned, governed store of named models (in Unity Catalog on Databricks) used to promote and serve models |
| What are MLflow traces? | Step-by-step records of an LLM/agent app's calls (inputs, outputs, tool calls, timings) for debugging why it answered what it did |
| What's a data engineer's role in MLOps? | Build the data pipelines and features, prepare training data, deploy and run the infrastructure; data scientists build the model |
| What is Unity Catalog? | Databricks' governance layer: `catalog.schema.table`, GRANTs, lineage, auditing, row filters and column masks |
