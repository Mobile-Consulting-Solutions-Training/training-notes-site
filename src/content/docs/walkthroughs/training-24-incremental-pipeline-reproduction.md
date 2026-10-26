---
title: "Reproduction - Training 24: Incremental Pipeline, Step by Step"
description: "Evan's incremental Citi Bike pipeline rebuilt in order: checkpoint, batch windows, landing table, MERGE and Step Functions."
sidebar:
  order: 240
---

Exactly what Evan did on Wed Oct 14, in order, with his real commands and code, translated to **your** resources.

**Sources:** [Training 24 notes](/training-notes-site/notes/training-24/) and Evan's shared chat for that class.

**Names:** replace `<your-name>` and `<initials>` with your own (for example `jdoe-citibike-ingest`, `jd-citibike-wg`). The class shares one AWS account, so resource names must be unique to you.

**What you end with:**

```text
Lambda (every 5 min) ──> S3 Bronze
                             │  every 30 min
EventBridge Scheduler ──> Step Functions
                             ├─ PrepareBatch      coordinator Lambda reads checkpoint, makes the window + batch_id
                             ├─ BronzeToSilver    Glue job 1, only files inside the window, writes one batch folder
                             ├─ SilverToRedshift  load that batch into a landing table
                             ├─ CompleteBatch     coordinator Lambda CALLs the stored procedure:
                             │                      landing → canonical → Gold, then advances the checkpoint
                             └─ PipelineSucceeded
```

You run every command yourself. Phases 1–8 need only things you already have (S3, Glue, Redshift). **Phases 9–12 need new IAM roles** (see "What's blocked for you" at the end).

---

## Name map: Evan → you

| Thing | Evan | You |
|---|---|---|
| Bucket | `citi-bike-nyc-pipeline` | `<your-name>-citibike-pipeline` |
| Ingestion Lambda | `citibike-ingestion` | `<your-name>-citibike-ingest` |
| Glue role | `AWSGlueServiceRole-CitiBike` | `<your-name>-citibike-glue-role` |
| Existing Glue job | `CitiBikeBronzeToSilverBackfillV2` | `<your-name>-citibike-bronze-to-silver` |
| New incremental Glue job | `CitiBikeBronzeToSilverIncrementalV2` | `<your-name>-citibike-bronze-to-silver-incremental` |
| Silver → Redshift | Glue job 2 over a JDBC connection | **Redshift `COPY`** (what you already use), see Phase 4 |
| Redshift role for COPY | n/a | `<your-name>-citibike-redshift-role` |
| Workgroup / namespace | `citibike-wg` | `<initials>-citibike-wg` / `<initials>-citibike-ns` |
| Canonical (staging) table | `public.citibike_station_snapshot_v2` | `public.citibike_station_snapshot` |
| Landing table | `public.citibike_station_snapshot_landing_v2` | `public.citibike_station_snapshot_landing` |
| Timestamp column | `snapshot_timestamp` | `snapshot_ts` (from your Silver job), confirm in Phase 0 |
| Checkpoint table | `public.citibike_pipeline_checkpoint` | same name |
| Procedures | `sp_process_citibike_batch`, `sp_complete_citibike_batch` | same names |
| Coordinator Lambda | `citibike-batch-coordinator` | `<your-name>-citibike-batch-coordinator` |
| State machine | `citibike-class-orchestration` | `<your-name>-citibike-orchestration` |
| 30-min schedule | `citibike-incremental-every-30-min` | `<your-name>-citibike-incremental-every-30-min` |
| CLI profile | `company` | your profile (below: `<profile>`) |
| Account ID | (his) | `<account-id>`: type it yourself, never paste it into files |

---

## Phase 0: Check your starting point (5 min)

Evan's first move every time was to look before changing anything. In **Query editor v2** → `<initials>-citibike-wg` → `dev`:

```sql
-- 1. Exact columns and order of your canonical table (the landing table will copy this)
SELECT ordinal_position, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'citibike_station_snapshot'
ORDER BY ordinal_position;

-- 2. Exact columns of your Gold tables
SELECT table_name, ordinal_position, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'gold'
ORDER BY table_name, ordinal_position;

-- 3. Row counts and latest snapshot
SELECT 'canonical' AS layer, COUNT(*), MAX(snapshot_ts) FROM public.citibike_station_snapshot
UNION ALL
SELECT 'gold_fact', COUNT(*), NULL FROM gold.fact_station_snapshot;
```

Write down the results. **Everything below assumes the column names from your Training 19 Silver job:**

```text
station_id, station_name, capacity, lat, lon, snapshot_ts, last_reported_ts,
bikes_available, ebikes_available, docks_available, utilization_pct,
is_empty, is_full, is_operational
```

If query 1 shows a different order or names, change the Glue `select(...)` in Phase 3 to match exactly. If your Gold fact uses `snapshot_timestamp` instead of `snapshot_ts`, change it in Phases 5–6.

And confirm Bronze is still filling (ingestion keeps running separately):

```bash
aws s3 ls s3://<your-name>-citibike-pipeline/bronze/citibike/station_status/ --recursive --profile <profile> | tail -5
```

---

## Phase 1: The first hour, historical backfill and Gold full refresh

**What Evan did (first hour of class):** his Silver v2 backfill job had failed the day before. He found "Glue job runner session is not authorized to perform S3 PutObject", fixed the Glue role's policy, checked for partial output (`aws s3 ls … --summarize`, 0 objects), deleted the half-written folder, and reran. Then he created and ran the Silver → Redshift backfill job. Redshift then held **1,551,706** observations (Oct 7–14).

Then, before any incremental work, he **backed up Gold** and did **one full refresh** of Gold from staging. "This is a full refresh, not an incremental merge. That's appropriate for establishing the initial clean gold data set, but we don't want to delete 1.5 million rows on every scheduled execution."

**Your version:** your Gold only holds the one snapshot from Oct 12 (2,519 rows), but Bronze has kept collecting since then.

1. Rebuild Silver from all of Bronze: run your existing job `<your-name>-citibike-bronze-to-silver` once (it overwrites, which is fine for a backfill).
2. Reload canonical from Silver:
   ```sql
   TRUNCATE public.citibike_station_snapshot;
   COPY public.citibike_station_snapshot
   FROM 's3://<your-name>-citibike-pipeline/silver/citibike/station_snapshot/'
   IAM_ROLE 'arn:aws:iam::<account-id>:role/<your-name>-citibike-redshift-role'
   FORMAT AS PARQUET;
   ```
3. Back up Gold (Evan's exact pattern):
   ```sql
   CREATE SCHEMA IF NOT EXISTS backup;
   CREATE TABLE backup.dim_station_pre_v2 AS SELECT * FROM gold.dim_station;
   CREATE TABLE backup.dim_date_pre_v2 AS SELECT * FROM gold.dim_date;
   CREATE TABLE backup.fact_station_snapshot_pre_v2 AS SELECT * FROM gold.fact_station_snapshot;
   ```
4. Full Gold refresh in one transaction: `BEGIN;` → `DELETE` from fact, dim_station, dim_date → insert dims → insert fact → `COMMIT;`. Use the same three `INSERT`s as the procedure in Phase 6, without the `WHERE batch_id = …` filters and reading from `public.citibike_station_snapshot`.
5. Validate: canonical count = fact count, and 0 duplicates (query in "Validation queries" below).

> Evan's later question: "If the incremental jobs can handle the backfill, what did we do the backfill jobs for?" Answer from his chat: the first incremental run is a **catch-up** run, so an incremental job with a wide window can do the backfill. Doing the full backfill first gave him a clean, validated baseline.

---

## Phase 2: Landing table (2 min)

Each batch lands here first, tagged with its `batch_id`. It's allowed to have duplicates; the procedure filters them.

```sql
CREATE TABLE public.citibike_station_snapshot_landing
(LIKE public.citibike_station_snapshot);

ALTER TABLE public.citibike_station_snapshot_landing
ADD COLUMN batch_id VARCHAR(64);
```

`batch_id` ends up as the **last** column. That matters for `COPY` in Phase 4.

---

## Phase 3: Incremental Glue job 1, Bronze → one Silver batch

**Evan's design (keep all of it):**

| Rule | Why |
|---|---|
| Takes `--BATCH_ID`, `--START_AFTER_UTC`, `--END_BEFORE_UTC` | The window is decided outside the job (later by the coordinator) |
| Selects files by the **timestamp in the file name**, not S3 LastModified | The filename is when the snapshot was taken |
| Window is **half-open `[start, end)`**: `start <= ts < end` | His first version used `start < ts < end` and would skip a file exactly on the boundary. He fixed it with `sed` |
| Writes to `incremental_batches/batch_id=<id>/` with `mode("errorifexists")` | Each batch is immutable. A retry can't silently overwrite. |
| Glue **bookmarks disabled** | The checkpoint controls progress; a bookmark wouldn't know about the backfill |
| Uses the latest `station_information` file before the window end | Station names/capacity |
| Dedups on `(station_id, snapshot)` | Same row twice in a batch |

**One change for you:** Evan's job 2 loaded Redshift through a Glue JDBC connection. You use `COPY` instead, and `COPY … FORMAT AS PARQUET` matches columns **by position**. So this job writes the batch **unpartitioned**, in **exactly the landing table's column order**, with `batch_id` last.

Save as `<your_name>_citibike_bronze_to_silver_incremental.py`:

```python
"""
Incremental Bronze -> one immutable Silver batch (Evan's Training 24 design,
adapted for Redshift COPY).

Job parameters: --BUCKET --BATCH_ID --START_AFTER_UTC --END_BEFORE_UTC (UTC, YYYY-MM-DDTHH:MM:SSZ)
    --BUCKET   <your-name>-citibike-pipeline   (same as the full-refresh job)
Window is [START_AFTER_UTC, END_BEFORE_UTC). Refuses to overwrite an existing batch.
"""
import re
import sys
from datetime import datetime, timezone

import boto3
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.window import Window

args = getResolvedOptions(sys.argv, ["JOB_NAME", "BUCKET", "BATCH_ID", "START_AFTER_UTC", "END_BEFORE_UTC"])
batch_id = args["BATCH_ID"]
if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", batch_id):
    raise ValueError("BATCH_ID must be 1-64 letters, numbers, _ or -")


def parse_utc(s):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", s):
        raise ValueError("Timestamp must be YYYY-MM-DDTHH:MM:SSZ")
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


start = parse_utc(args["START_AFTER_UTC"])
end = parse_utc(args["END_BEFORE_UTC"])
if end <= start:
    raise ValueError("END_BEFORE_UTC must be after START_AFTER_UTC")

BUCKET = args["BUCKET"]
STATUS_PREFIX = "bronze/citibike/station_status/"
INFO_PREFIX = "bronze/citibike/station_information/"
OUTPUT_PREFIX = f"silver/citibike/incremental_batches/batch_id={batch_id}/"
OUTPUT_URI = f"s3://{BUCKET}/{OUTPUT_PREFIX}"

s3 = boto3.client("s3", region_name="us-east-2")
if s3.list_objects_v2(Bucket=BUCKET, Prefix=OUTPUT_PREFIX, MaxKeys=1).get("KeyCount", 0):
    raise RuntimeError(f"Batch already exists; refusing to overwrite: {OUTPUT_URI}")

# ---------------------------------------------------------
# Pick files by the timestamp in the file name
# ---------------------------------------------------------
status_re = re.compile(r"station_status_(\d{8}T\d{6}Z)\.json$")
info_re = re.compile(r"station_information_(\d{8}T\d{6}Z)\.json$")
status_keys, latest_info_key, latest_info_dt = [], None, None
paginator = s3.get_paginator("list_objects_v2")

for page in paginator.paginate(Bucket=BUCKET, Prefix=STATUS_PREFIX):
    for obj in page.get("Contents", []):
        m = status_re.search(obj["Key"])
        if m:
            ts = datetime.strptime(m.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            if start <= ts < end:                       # half-open window
                status_keys.append(obj["Key"])

for page in paginator.paginate(Bucket=BUCKET, Prefix=INFO_PREFIX):
    for obj in page.get("Contents", []):
        m = info_re.search(obj["Key"])
        if m:
            ts = datetime.strptime(m.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            if ts < end and (latest_info_dt is None or ts > latest_info_dt):
                latest_info_dt, latest_info_key = ts, obj["Key"]

print(f"BATCH_ID={batch_id} window=[{start}, {end}) status_files={len(status_keys)} info={latest_info_key}")
if not status_keys:
    raise RuntimeError("No station_status files in the window. No batch written.")
if not latest_info_key:
    raise RuntimeError("No station_information file before the window end")

# ---------------------------------------------------------
# Glue setup
# ---------------------------------------------------------
sc = SparkContext.getOrCreate()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
spark.conf.set("spark.sql.session.timeZone", "UTC")
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

# ---------------------------------------------------------
# Transform (same columns as your Training 19 Silver job)
# ---------------------------------------------------------
status = (
    spark.read.option("multiLine", True)
    .json([f"s3://{BUCKET}/{k}" for k in sorted(status_keys)])
    .select(
        F.regexp_extract(F.input_file_name(), r"_(\d{8}T\d{6}Z)\.json$", 1).alias("snapshot_id"),
        F.input_file_name().alias("source_file"),
        F.explode("data.stations").alias("s"),
    )
    .select(
        F.to_timestamp("snapshot_id", "yyyyMMdd'T'HHmmss'Z'").alias("snapshot_ts"),
        "source_file",
        F.col("s.station_id").cast("string").alias("station_id"),
        F.col("s.num_bikes_available").cast("long").alias("bikes_available"),
        F.col("s.num_ebikes_available").cast("long").alias("ebikes_available"),
        F.col("s.num_docks_available").cast("long").alias("docks_available"),
        F.col("s.is_installed").alias("is_installed"),
        F.col("s.is_renting").alias("is_renting"),
        F.col("s.is_returning").alias("is_returning"),
        F.col("s.last_reported").cast("long").alias("last_reported"),
    )
    .filter(F.col("station_id").isNotNull() & F.col("snapshot_ts").isNotNull())
)
# Dedup inside the batch (Evan's window, newest source file wins)
w = Window.partitionBy("station_id", "snapshot_ts").orderBy(F.col("source_file").desc())
status = status.withColumn("_rn", F.row_number().over(w)).filter("_rn = 1").drop("_rn", "source_file")

info = (
    spark.read.option("multiLine", True).json(f"s3://{BUCKET}/{latest_info_key}")
    .select(F.explode("data.stations").alias("s"))
    .select(
        F.col("s.station_id").cast("string").alias("station_id"),
        F.col("s.name").alias("station_name"),
        F.col("s.capacity").cast("long").alias("capacity"),
        F.col("s.lat").alias("lat"),
        F.col("s.lon").alias("lon"),
    )
    .dropDuplicates(["station_id"])
)

silver = (
    status.join(F.broadcast(info), "station_id", "left")
    .withColumn("last_reported_ts",
                F.when(F.col("last_reported") > 86400, F.to_timestamp(F.from_unixtime("last_reported"))))
    .withColumn("is_operational",
                (F.col("is_installed") == 1) & (F.col("is_renting") == 1) & (F.col("is_returning") == 1))
    .withColumn("utilization_pct",
                F.when(F.col("capacity") > 0, F.round(F.col("bikes_available") / F.col("capacity") * 100, 1)))
    .withColumn("is_empty", F.col("bikes_available") == 0)
    .withColumn("is_full", F.col("docks_available") == 0)
    .withColumn("batch_id", F.lit(batch_id))
    # EXACT landing-table column order (Phase 0, query 1), batch_id last, for COPY
    .select(
        "station_id", "station_name", "capacity", "lat", "lon",
        "snapshot_ts", "last_reported_ts",
        "bikes_available", "ebikes_available", "docks_available",
        "utilization_pct", "is_empty", "is_full", "is_operational",
        "batch_id",
    )
)

count = silver.count()
print(f"SILVER BATCH ROWS={count} OUTPUT={OUTPUT_URI}")
if count == 0:
    raise RuntimeError("No station rows produced; refusing an empty batch")

silver.write.mode("errorifexists").option("compression", "snappy").parquet(OUTPUT_URI)
job.commit()
print("INCREMENTAL SILVER BATCH COMPLETE")
```

**Upload it and create the job.** Evan cloned his working job's settings with a small boto3 script (`create_incremental_jobs.py`). The console way is the same thing:

1. Upload:
   ```bash
   aws s3 cp <your_name>_citibike_bronze_to_silver_incremental.py \
     s3://<your-name>-citibike-pipeline/scripts/ --profile <profile> --region us-east-2
   ```
2. Glue console → your job `<your-name>-citibike-bronze-to-silver` → **Actions → Clone job**. Name it `<your-name>-citibike-bronze-to-silver-incremental`.
3. In the clone, change these settings:
   - Script path: the file you just uploaded.
   - Job bookmark: **Disable**.
   - Retries: **0**.
   - Max concurrency: **1**.
   - Keep `--BUCKET <your-name>-citibike-pipeline` (same convention as the full-refresh job).

**Check the Glue role can write the new prefix first.** This was Evan's first failure ("TASK_WRITE_FAILED … SQLSTATE: 58030"), because his policy covered a different Silver prefix:

```bash
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::<account-id>:role/<your-name>-citibike-glue-role \
  --action-names s3:PutObject s3:DeleteObject \
  --resource-arns arn:aws:s3:::<your-name>-citibike-pipeline/silver/citibike/incremental_batches/batch_id=test/x.parquet \
  --profile <profile> \
  --query 'EvaluationResults[].{Action:EvalActionName,Decision:EvalDecision}'
```

You want `allowed` for both. If you get `implicitDeny`, edit your inline policy `<your-name>-citibike-glue-s3-access` so its write statement covers `silver/*`.

**Run the first catch-up batch.** Same as Evan's `catchup_20261014_a`. Pick a start a bit **before** your latest canonical `snapshot_ts` (overlap is safe; the procedure dedups) and an end after the newest Bronze file:

```bash
BATCH_ID=catchup_20261020_a
START_AFTER_UTC=2026-10-20T10:00:00Z     # replace: ~1 h before MAX(snapshot_ts)
END_BEFORE_UTC=2026-10-20T16:00:00Z      # replace: after your newest Bronze file

aws glue start-job-run \
  --job-name <your-name>-citibike-bronze-to-silver-incremental \
  --arguments "{\"--BUCKET\":\"<your-name>-citibike-pipeline\",\"--BATCH_ID\":\"$BATCH_ID\",\"--START_AFTER_UTC\":\"$START_AFTER_UTC\",\"--END_BEFORE_UTC\":\"$END_BEFORE_UTC\"}" \
  --profile <profile> --region us-east-2
```

Two things Evan hit here:
- **"Missing required arguments"** when he clicked **Run** in the console. The console doesn't pass the three parameters, so use the CLI command above.
- **The run didn't show in the Glue job list** even though he had a run ID. Check the region (us-east-2), then open the job → **Runs** tab. Tip from a classmate: open the run → **View details**, and it updates live.

If a run fails partway, check the folder and delete **only that batch's prefix**, or just use a new batch ID:

```bash
aws s3 ls s3://<your-name>-citibike-pipeline/silver/citibike/incremental_batches/batch_id=$BATCH_ID/ --recursive --summarize --profile <profile>
```

---

## Phase 4: Load the batch into landing

**Evan:** Glue job 2 (`CitiBikeSilverToRedshiftIncrementalV2`, `--BATCH_ID` only) read that one batch folder and appended to landing over the `citibike-redshift-connection`.

**You:** one `COPY` of that one folder. It's simpler and uses the role you already have (it can read `silver/*`):

```sql
COPY public.citibike_station_snapshot_landing
FROM 's3://<your-name>-citibike-pipeline/silver/citibike/incremental_batches/batch_id=catchup_20261020_a/'
IAM_ROLE 'arn:aws:iam::<account-id>:role/<your-name>-citibike-redshift-role'
FORMAT AS PARQUET;
```

Check what landed (Evan's query):

```sql
SELECT batch_id, COUNT(*) AS observations,
       MIN(snapshot_ts) AS earliest, MAX(snapshot_ts) AS latest
FROM public.citibike_station_snapshot_landing
GROUP BY batch_id;
```

Running `COPY` twice appends the rows twice. That's fine **in landing**, because the next step only inserts rows that aren't already in canonical or Gold.

---

## Phase 5: Landing → canonical → Gold, by hand first

**What happened:** Evan's template used `MERGE INTO … WHEN NOT MATCHED THEN INSERT`. Redshift kept rejecting it ("unexpected input"), and the AI went back and forth. Evan: "you keep saying to use merge into and it keeps not working." The fix was to **drop MERGE** and use `INSERT … SELECT … WHERE NOT EXISTS`. It does the same job here, because we only ever insert new observations and never update them.

Run it once by hand in Query editor v2 with **Isolated session ON**. Also, if any text is highlighted, Query editor runs only the highlighted part.

```sql
BEGIN;

-- 1. New observations into canonical (dedup inside the batch, skip ones already there)
INSERT INTO public.citibike_station_snapshot (
    station_id, station_name, capacity, lat, lon, snapshot_ts, last_reported_ts,
    bikes_available, ebikes_available, docks_available, utilization_pct,
    is_empty, is_full, is_operational
)
SELECT station_id, station_name, capacity, lat, lon, snapshot_ts, last_reported_ts,
       bikes_available, ebikes_available, docks_available, utilization_pct,
       is_empty, is_full, is_operational
FROM (
    SELECT *
    FROM public.citibike_station_snapshot_landing
    WHERE batch_id = 'catchup_20261020_a'
      AND station_id IS NOT NULL AND snapshot_ts IS NOT NULL
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY station_id, snapshot_ts
        ORDER BY station_name DESC NULLS LAST, capacity DESC NULLS LAST
    ) = 1
) src
WHERE NOT EXISTS (
    SELECT 1 FROM public.citibike_station_snapshot tgt
    WHERE tgt.station_id = src.station_id AND tgt.snapshot_ts = src.snapshot_ts
);

COMMIT;
```

Then run the three Gold inserts (new dates, new stations, new facts). They're the same as steps 2–4 of the procedure in Phase 6, with `p_batch_id` replaced by `'catchup_20261020_a'`, inside `BEGIN; … COMMIT;`.

Validate (see the end): canonical count = Gold fact count, 0 duplicates, 0 orphans. Evan's numbers after this step were 1,579,415 in both, with 27,709 new observations.

---

## Phase 6: Turn it into a stored procedure

Once the hand-run SQL worked, Evan wrapped it so the whole Redshift side becomes one `CALL`. **Create it first, then call it.** The AI gave him the `CALL` before the `CREATE`.

Match the Gold column lists to your Phase 0 results. These are Evan's Gold columns.

```sql
CREATE OR REPLACE PROCEDURE public.sp_process_citibike_batch(p_batch_id IN VARCHAR)
AS $$
BEGIN
    -- 1. Missing observations into canonical
    INSERT INTO public.citibike_station_snapshot (
        station_id, station_name, capacity, lat, lon, snapshot_ts, last_reported_ts,
        bikes_available, ebikes_available, docks_available, utilization_pct,
        is_empty, is_full, is_operational
    )
    SELECT station_id, station_name, capacity, lat, lon, snapshot_ts, last_reported_ts,
           bikes_available, ebikes_available, docks_available, utilization_pct,
           is_empty, is_full, is_operational
    FROM (
        SELECT *
        FROM public.citibike_station_snapshot_landing
        WHERE batch_id = p_batch_id
          AND station_id IS NOT NULL AND snapshot_ts IS NOT NULL
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY station_id, snapshot_ts
            ORDER BY station_name DESC NULLS LAST, capacity DESC NULLS LAST
        ) = 1
    ) src
    WHERE NOT EXISTS (
        SELECT 1 FROM public.citibike_station_snapshot tgt
        WHERE tgt.station_id = src.station_id AND tgt.snapshot_ts = src.snapshot_ts
    );

    -- 2. Missing calendar dates
    INSERT INTO gold.dim_date (date_key, calendar_date, year_number, month_number, day_number, day_of_week)
    SELECT DISTINCT
        CAST(TO_CHAR(l.snapshot_ts, 'YYYYMMDD') AS INTEGER),
        CAST(l.snapshot_ts AS DATE),
        EXTRACT(YEAR FROM l.snapshot_ts),
        EXTRACT(MONTH FROM l.snapshot_ts),
        EXTRACT(DAY FROM l.snapshot_ts),
        EXTRACT(DOW FROM l.snapshot_ts)
    FROM public.citibike_station_snapshot_landing l
    WHERE l.batch_id = p_batch_id
      AND l.snapshot_ts IS NOT NULL
      AND NOT EXISTS (SELECT 1 FROM gold.dim_date d
                      WHERE d.calendar_date = CAST(l.snapshot_ts AS DATE));

    -- 3. Missing stations (latest name/capacity in the batch)
    INSERT INTO gold.dim_station (station_id, station_name, capacity, lat, lon)
    SELECT l.station_id, l.station_name, l.capacity, l.lat, l.lon
    FROM public.citibike_station_snapshot_landing l
    WHERE l.batch_id = p_batch_id
      AND l.station_id IS NOT NULL
      AND NOT EXISTS (SELECT 1 FROM gold.dim_station d WHERE d.station_id = l.station_id)
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY l.station_id
        ORDER BY l.snapshot_ts DESC, l.station_name DESC NULLS LAST
    ) = 1;

    -- 4. Missing fact rows
    INSERT INTO gold.fact_station_snapshot (
        station_id, date_key, snapshot_ts, bikes_available, ebikes_available,
        docks_available, utilization_pct, is_empty, is_full, is_operational
    )
    SELECT l.station_id,
           CAST(TO_CHAR(l.snapshot_ts, 'YYYYMMDD') AS INTEGER),
           l.snapshot_ts, l.bikes_available, l.ebikes_available,
           l.docks_available, l.utilization_pct, l.is_empty, l.is_full, l.is_operational
    FROM public.citibike_station_snapshot_landing l
    WHERE l.batch_id = p_batch_id
      AND l.station_id IS NOT NULL AND l.snapshot_ts IS NOT NULL
      AND NOT EXISTS (SELECT 1 FROM gold.fact_station_snapshot f
                      WHERE f.station_id = l.station_id AND f.snapshot_ts = l.snapshot_ts)
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY l.station_id, l.snapshot_ts
        ORDER BY l.station_name DESC NULLS LAST, l.capacity DESC NULLS LAST
    ) = 1;
END;
$$ LANGUAGE plpgsql;
```

There's no `COMMIT` inside. Called outside a transaction, Redshift runs the whole procedure as **one transaction**, so Gold is never half-updated.

**Idempotency test (Evan's):** call it on the batch you already loaded. Nothing should change.

```sql
CALL public.sp_process_citibike_batch('catchup_20261020_a');
-- then re-run the count query: canonical and Gold counts must not move
```

---

## Phase 7: Checkpoint table and the wrapper procedure

**Why not DynamoDB:** the AI first proposed a DynamoDB checkpoint. Evan asked, "what's the rationale for the dynamodb checkpoint table? dynamo was never part of the plan." So the checkpoint lives in **Redshift**, next to the data. It's one less service and one less set of permissions.

```sql
CREATE TABLE IF NOT EXISTS public.citibike_pipeline_checkpoint (
    pipeline_name      VARCHAR(100),
    last_completed_utc TIMESTAMP,
    last_batch_id      VARCHAR(100),
    updated_at         TIMESTAMP DEFAULT GETDATE()
);

-- Seed it with your last validated snapshot (use YOUR value from the catch-up batch)
INSERT INTO public.citibike_pipeline_checkpoint (pipeline_name, last_completed_utc, last_batch_id)
SELECT 'citibike_incremental',
       (SELECT MAX(snapshot_ts) FROM public.citibike_station_snapshot),
       'catchup_20261020_a'
WHERE NOT EXISTS (SELECT 1 FROM public.citibike_pipeline_checkpoint
                  WHERE pipeline_name = 'citibike_incremental');

SELECT * FROM public.citibike_pipeline_checkpoint;
```

Don't set the checkpoint to "now". That would skip everything collected since the last good batch.

**The wrapper.** "I definitely don't want to replace a working procedure if I can help it." So Evan wrote a second procedure that **calls** the first one, runs checks, and then moves the checkpoint:

```sql
CREATE OR REPLACE PROCEDURE public.sp_complete_citibike_batch(
    p_batch_id   IN VARCHAR,
    p_window_end IN TIMESTAMP
)
AS $$
DECLARE
    v_rows INTEGER;
    v_missing INTEGER;
    v_current_checkpoint TIMESTAMP;
BEGIN
    -- The batch must exist in landing
    SELECT COUNT(*) INTO v_rows
    FROM public.citibike_station_snapshot_landing
    WHERE batch_id = p_batch_id;
    IF v_rows = 0 THEN
        RAISE EXCEPTION 'Batch contains no landing records';
    END IF;

    -- Canonical + Gold
    CALL public.sp_process_citibike_batch(p_batch_id);

    -- Gold must contain every canonical observation
    SELECT COUNT(*) INTO v_missing
    FROM public.citibike_station_snapshot s
    LEFT JOIN gold.fact_station_snapshot f
      ON s.station_id = f.station_id AND s.snapshot_ts = f.snapshot_ts
    WHERE f.station_id IS NULL;
    IF v_missing > 0 THEN
        RAISE EXCEPTION 'Gold is missing staging observations';
    END IF;

    -- Never move the checkpoint backwards
    SELECT MAX(last_completed_utc) INTO v_current_checkpoint
    FROM public.citibike_pipeline_checkpoint
    WHERE pipeline_name = 'citibike_incremental';
    IF v_current_checkpoint IS NULL THEN
        RAISE EXCEPTION 'Pipeline checkpoint is missing';
    END IF;
    IF p_window_end <= v_current_checkpoint THEN
        RAISE EXCEPTION 'Batch window does not advance checkpoint';
    END IF;

    -- Advance ONLY after everything above succeeded
    UPDATE public.citibike_pipeline_checkpoint
    SET last_completed_utc = p_window_end,
        last_batch_id = p_batch_id,
        updated_at = GETDATE()
    WHERE pipeline_name = 'citibike_incremental';
END;
$$ LANGUAGE plpgsql;
```

- Call it **outside** an explicit transaction.
- Don't call it with the catch-up batch, which is already committed. The first real call comes from the pipeline.
- Any `RAISE EXCEPTION` rolls back the whole call, including the inserts. So a failed batch never moves the checkpoint.

**With Phases 1–7 done, you have a working incremental pipeline that you run by hand:** Glue (with a window) → COPY → `CALL sp_complete_citibike_batch(...)`. You can show that in class even without Step Functions.

---

## Phase 8: The batch contract (how the automation picks windows)

These are the rules the coordinator follows (from Evan's chat):

| Property | Rule |
|---|---|
| Batch ID | The Step Functions **execution name**, unique per run |
| Start | Checkpoint **minus 2 hours** (overlap, so late files get a second chance) |
| End | Now **minus 10 minutes**, rounded to the minute (don't grab a file that's still being written) |
| If end ≤ checkpoint | Fail: "No safe new batch window yet" |
| Landing | Append; dedup downstream |
| Checkpoint | Advances only inside `sp_complete_citibike_batch` |
| Failure | Checkpoint stays put; the next run gets a new batch ID |

The 2-hour overlap means each run re-reads up to 2 hours of files it has already processed. That's safe, because the `NOT EXISTS` inserts skip rows that are already there. Files arriving **more than 2 hours late** would still be missed.

---

## Phase 9: Coordinator Lambda (needs a role, see the end)

One Lambda with two phases. It talks to Redshift through the **Redshift Data API**. Evan's first version built the SQL inside Step Functions (`Sql.$`), and AWS rejected the definition, so the SQL moved into Python. Evan's file with your names:

```python
# coordinator.py
import os
import re
import time
from datetime import datetime, timezone, timedelta

import boto3

client = boto3.client("redshift-data")
WORKGROUP = os.environ["REDSHIFT_WORKGROUP"]
DATABASE = os.environ["REDSHIFT_DATABASE"]
BATCH_RE = re.compile(r"[A-Za-z0-9_-]{1,60}\Z")


def execute_and_wait(sql, expect_records=False):
    statement_id = client.execute_statement(WorkgroupName=WORKGROUP, Database=DATABASE, Sql=sql)["Id"]
    for _ in range(105):
        result = client.describe_statement(Id=statement_id)
        if result["Status"] == "FINISHED":
            return client.get_statement_result(Id=statement_id)["Records"] if expect_records else statement_id
        if result["Status"] in ("FAILED", "ABORTED"):
            raise RuntimeError(f"Redshift statement {statement_id} {result['Status']}: {result.get('Error', '')}")
        time.sleep(2)
    raise TimeoutError(f"Redshift statement {statement_id} did not finish within 210s")


def handler(event, context):
    phase = event.get("phase")

    if phase == "prepare":
        execution_name = event.get("execution_name", "")
        if not BATCH_RE.fullmatch(execution_name):
            raise ValueError("Invalid execution_name; use 1-60 letters, numbers, _ or -")
        records = execute_and_wait(
            "SELECT TO_CHAR(last_completed_utc, 'YYYY-MM-DD HH24:MI:SS') "
            "FROM public.citibike_pipeline_checkpoint WHERE pipeline_name = 'citibike_incremental'",
            expect_records=True,
        )
        if len(records) != 1 or not records[0][0].get("stringValue"):
            raise RuntimeError("Expected exactly one populated checkpoint row")
        checkpoint = datetime.strptime(records[0][0]["stringValue"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        start = checkpoint - timedelta(hours=2)
        end = (datetime.now(timezone.utc) - timedelta(minutes=10)).replace(second=0, microsecond=0)
        if end <= checkpoint:
            raise RuntimeError("No safe new batch window yet; wait before rerunning")
        return {
            "batch_id": execution_name,
            "start_after_utc": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_before_utc": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "window_end_sql": end.strftime("%Y-%m-%d %H:%M:%S"),
        }

    if phase == "complete":
        batch_id = event.get("batch_id", "")
        window_end_sql = event.get("window_end_sql", "")
        if not BATCH_RE.fullmatch(batch_id):
            raise ValueError("Invalid batch_id")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", window_end_sql):
            raise ValueError("Invalid window_end_sql")
        statement_id = execute_and_wait(
            f"CALL public.sp_complete_citibike_batch('{batch_id}', TIMESTAMP '{window_end_sql}');"
        )
        return {"batch_id": batch_id, "redshift_statement_id": statement_id, "status": "FINISHED"}

    raise ValueError("phase must be prepare or complete")
```

The regex checks matter: they're what make it safe to put `batch_id` straight into the SQL string.

**Your extra phase:** your Silver → landing step is `COPY`, not a Glue job, so add a third phase, `"load"`, that runs the Phase 4 `COPY` through `execute_and_wait(...)`, with the batch folder built from `batch_id`. Step Functions then calls the coordinator for SilverToRedshift instead of a second Glue job.

**Lambda settings:**
- Python 3.12, handler `coordinator.handler`, timeout 240 s.
- Environment variables: `REDSHIFT_WORKGROUP=<initials>-citibike-wg`, `REDSHIFT_DATABASE=dev`.

**Its role needs:**
- `redshift-data:ExecuteStatement`, `DescribeStatement` and `GetStatementResult`
- `redshift-serverless:GetCredentials` on your workgroup
- CloudWatch Logs

---

## Phase 10: Step Functions + Terraform

**What Evan did, in order:**

1. **"No state file was found!"** His Terraform folder had only `main.tf`, because the state machine had been created earlier without saved state. Running `apply` would have tried to create duplicates. So he **imported** the existing resources first:
   ```bash
   terraform init
   terraform import aws_cloudwatch_log_group.sfn /aws/vendedlogs/states/citibike-class-orchestration
   terraform import aws_iam_role.sfn CitiBikeStepFunctionsClassRole
   terraform import aws_iam_role_policy.sfn CitiBikeStepFunctionsClassRole:CitiBikeStepFunctionsClassPermissions
   terraform import aws_sfn_state_machine.pipeline arn:aws:states:us-east-2:<account-id>:stateMachine:citibike-class-orchestration
   terraform state list
   terraform plan
   ```
   You have no existing state machine, so **skip the imports**. Your first `apply` creates everything.
2. **Wrong-folder scare:** he once ran `init` in a new folder (`terraform2`) without the state. The plan said **"7 to add"**, which meant recreating resources that already existed. He moved back to the original folder, and the plan said **"3 to add, 2 to change, 0 to destroy"**. Lesson: **always run Terraform in the folder that holds the `.tfstate`**, and read the plan before applying.
3. **First apply failed partway** on the `Sql.$` field in the state machine. The fix was moving the SQL into the coordinator (Phase 9). After that he asked for full file replacements, "I DO NOT WANT TO SEE THESE ERRORS ANYMORE." The final apply: **"0 added, 4 changed, 0 destroyed."**
4. His routine every time:
   ```bash
   python3 -m py_compile coordinator.py
   terraform fmt
   terraform validate
   terraform plan -out=citibike-final.tfplan
   terraform apply "citibike-final.tfplan"
   ```

**His final files** (folder `citibike-stepfunctions-terraform/`: `main.tf`, `orchestration.tf`, `coordinator.py`, later `scheduler.tf`):

- **`main.tf`** contains:
  - the provider (`us-east-2`, `profile`, `allowed_account_ids`)
  - the log group `/aws/vendedlogs/states/<name>` (7-day retention)
  - the Step Functions role, trusting `states.amazonaws.com`, with an inline policy that allows:
    - `lambda:InvokeFunction` on the coordinator
    - `glue:StartJobRun`, `GetJobRun`, `GetJobRuns` and `BatchStopJobRun` on the incremental job(s)
    - `events:PutRule`, `PutTargets` and `DescribeRule` on `rule/StepFunctionsGetEventsForGlueJobRule` (needed for `.sync`)
    - the `logs:*LogDelivery*` actions
  - the state machine itself (`STANDARD`, logging level `ALL`)
- **`orchestration.tf`** contains:
  - `archive_file`, which zips `coordinator.py`
  - the coordinator role, trusting `lambda.amazonaws.com`, with the inline policy from Phase 9
  - `aws_lambda_function.coordinator`
- Use **inline** policies (`aws_iam_role_policy`). Student accounts can't create standalone managed policies.

**The state machine** (from his `main.tf`, with your names and your COPY step):

```hcl
definition = jsonencode({
  Comment = "Citi Bike: checkpoint -> incremental Glue -> COPY -> stored procedure"
  StartAt = "PrepareBatch"
  States = {
    PrepareBatch = {
      Type     = "Task"
      Resource = "arn:aws:states:::lambda:invoke"
      Parameters = {
        FunctionName = aws_lambda_function.coordinator.arn
        Payload      = { "execution_name.$" = "$$.Execution.Name", phase = "prepare" }
      }
      ResultSelector = { "batch.$" = "$.Payload" }
      ResultPath     = "$.prepared"
      Next           = "BronzeToSilver"
    }
    BronzeToSilver = {
      Type     = "Task"
      Resource = "arn:aws:states:::glue:startJobRun.sync"     # .sync = wait until the job finishes
      Parameters = {
        JobName = "<your-name>-citibike-bronze-to-silver-incremental"
        Arguments = {
          "--BATCH_ID.$"        = "$.prepared.batch.batch_id"
          "--START_AFTER_UTC.$" = "$.prepared.batch.start_after_utc"
          "--END_BEFORE_UTC.$"  = "$.prepared.batch.end_before_utc"
        }
      }
      ResultPath = "$.bronze_result"
      Next       = "SilverToRedshift"
    }
    SilverToRedshift = {                                       # Evan: a 2nd Glue job. You: coordinator "load" (COPY)
      Type     = "Task"
      Resource = "arn:aws:states:::lambda:invoke"
      Parameters = {
        FunctionName = aws_lambda_function.coordinator.arn
        Payload      = { phase = "load", "batch_id.$" = "$.prepared.batch.batch_id" }
      }
      ResultPath = "$.load_result"
      Next       = "CompleteBatch"
    }
    CompleteBatch = {
      Type     = "Task"
      Resource = "arn:aws:states:::lambda:invoke"
      Parameters = {
        FunctionName = aws_lambda_function.coordinator.arn
        Payload = {
          phase              = "complete"
          "batch_id.$"       = "$.prepared.batch.batch_id"
          "window_end_sql.$" = "$.prepared.batch.window_end_sql"
        }
      }
      ResultSelector = { "completion.$" = "$.Payload" }
      ResultPath     = "$.redshift_completion"
      Next           = "PipelineSucceeded"
    }
    PipelineSucceeded = { Type = "Succeed" }
  }
})
```

`ResultPath` keeps each step's output **next to** the input instead of replacing it. That's how `$.prepared.batch.batch_id` is still available three steps later.

---

## Phase 11: First run, the Redshift grants, and redrive

Start one run by hand, with the schedule still off:

```bash
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:us-east-2:<account-id>:stateMachine:<your-name>-citibike-orchestration \
  --name "<your-name>-test-$(date -u +%Y%m%dT%H%M%SZ)" \
  --input '{}' \
  --profile <profile> --region us-east-2
```

**Evan's run 1 failed in PrepareBatch:** "permission denied for relation citibike_pipeline_checkpoint". IAM was fine. **Inside Redshift**, the Lambda is a *different database user*, so it needs `GRANT`s. Two separate permission layers:

| Layer | Controls | Fix |
|---|---|---|
| IAM | "May this role call the Redshift Data API?" | Role policy (Terraform) |
| Redshift database | "May this DB user read or write this table?" | SQL `GRANT` |

He found the error with:

```bash
aws logs filter-log-events --log-group-name /aws/lambda/citibike-batch-coordinator \
  --filter-pattern "ERROR" --query 'events[*].message' --output text --profile <profile> --region us-east-2
```

He found the database user name in query history / `pg_user`: it's **`IAMR:<role name>`**.

**Run 2** got through both Glue jobs, then failed in CompleteBatch on the landing table. The full set of grants that fixed it (your names):

```sql
GRANT USAGE ON SCHEMA public TO "IAMR:<your-name>-citibike-coordinator-role";
GRANT USAGE ON SCHEMA gold   TO "IAMR:<your-name>-citibike-coordinator-role";
GRANT SELECT, INSERT ON TABLE public.citibike_station_snapshot_landing TO "IAMR:<your-name>-citibike-coordinator-role";  -- INSERT for your COPY
GRANT SELECT, INSERT ON TABLE public.citibike_station_snapshot        TO "IAMR:<your-name>-citibike-coordinator-role";
GRANT SELECT, INSERT, UPDATE ON TABLE gold.dim_station                TO "IAMR:<your-name>-citibike-coordinator-role";
GRANT SELECT, INSERT ON TABLE gold.dim_date                           TO "IAMR:<your-name>-citibike-coordinator-role";
GRANT SELECT, INSERT ON TABLE gold.fact_station_snapshot              TO "IAMR:<your-name>-citibike-coordinator-role";
GRANT SELECT, UPDATE ON TABLE public.citibike_pipeline_checkpoint     TO "IAMR:<your-name>-citibike-coordinator-role";
GRANT EXECUTE ON PROCEDURE public.sp_process_citibike_batch(VARCHAR)             TO "IAMR:<your-name>-citibike-coordinator-role";
GRANT EXECUTE ON PROCEDURE public.sp_complete_citibike_batch(VARCHAR, TIMESTAMP) TO "IAMR:<your-name>-citibike-coordinator-role";
```

Your `COPY` from the Lambda also uses `<your-name>-citibike-redshift-role`, which is already associated with your namespace.

**Then: Redrive from failure.** In the Step Functions console, open the failed run → **Redrive**. It restarts at the failed step and keeps the Glue work that already succeeded, so nothing is reprocessed. All five states went green. Before redriving, check the checkpoint hasn't moved.

---

## Phase 12: The 30-minute schedule (needs the scheduler role)

Evan's `scheduler.tf`. Note it's created **DISABLED** first.

```hcl
resource "aws_iam_role" "scheduler" {
  name = "<your-name>-citibike-sfn-scheduler-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "scheduler.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy" "scheduler" {
  name = "<your-name>-citibike-sfn-scheduler-permissions"
  role = aws_iam_role.scheduler.id
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = ["states:StartExecution"], Resource = aws_sfn_state_machine.pipeline.arn }]
  })
}

resource "aws_scheduler_schedule" "citibike_incremental" {
  name                         = "<your-name>-citibike-incremental-every-30-min"
  schedule_expression          = "rate(30 minutes)"
  schedule_expression_timezone = "UTC"
  state                        = "DISABLED"     # flip to ENABLED only after a clean manual run
  flexible_time_window { mode = "OFF" }
  target {
    arn      = aws_sfn_state_machine.pipeline.arn
    role_arn = aws_iam_role.scheduler.arn
    input    = jsonencode({})
    retry_policy {
      maximum_retry_attempts       = 0
      maximum_event_age_in_seconds = 60
    }
  }
  depends_on = [aws_iam_role_policy.scheduler]
}
```

It's exactly the role you asked Evan for: trusts `scheduler.amazonaws.com`, allowed `states:StartExecution`.

Verify after enabling:

```bash
aws scheduler get-schedule --name <your-name>-citibike-incremental-every-30-min \
  --query '{Name:Name,State:State,Schedule:ScheduleExpression}' --profile <profile> --region us-east-2

aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:us-east-2:<account-id>:stateMachine:<your-name>-citibike-orchestration \
  --max-results 10 --query 'executions[*].{Name:name,Status:status,Started:startDate}' --output table \
  --profile <profile> --region us-east-2
```

You want a new run about every 30 minutes and the checkpoint moving forward. **Cost:** each run starts a Glue job. Keep the schedule disabled except while you're collecting evidence (2 automatic runs), and follow Evan's weekend rule: disable it, don't delete it.

**What Evan left open:**
- **Nothing stops two runs overlapping.** Both would read the same checkpoint. Checking `list-executions --status-filter RUNNING` is diagnostic, not a lock. The fix is a conditional-write lock.
- **No failure alerts yet.** The next step would be an EventBridge rule on failed executions → SNS.

---

## Validation queries (run after every phase)

```sql
-- Checkpoint
SELECT * FROM public.citibike_pipeline_checkpoint WHERE pipeline_name = 'citibike_incremental';

-- Canonical vs Gold counts (must match)
SELECT 'canonical' AS source, COUNT(*) FROM public.citibike_station_snapshot
UNION ALL
SELECT 'gold_fact', COUNT(*) FROM gold.fact_station_snapshot;

-- Duplicates (expect 0 rows)
SELECT station_id, snapshot_ts, COUNT(*) FROM public.citibike_station_snapshot
GROUP BY station_id, snapshot_ts HAVING COUNT(*) > 1 LIMIT 20;

-- Orphan facts (expect 0 and 0)
SELECT COUNT(*) FROM gold.fact_station_snapshot f
LEFT JOIN gold.dim_station s ON f.station_id = s.station_id WHERE s.station_id IS NULL;
SELECT COUNT(*) FROM gold.fact_station_snapshot f
LEFT JOIN gold.dim_date d ON f.date_key = d.date_key WHERE d.date_key IS NULL;
```

Screenshot each result for the homework's Part 3 evidence.

---

## Every problem Evan hit (and the fix)

| # | Problem | Fix |
|---|---|---|
| 1 | Glue write failed, `TASK_WRITE_FAILED` | The Glue role lacked `s3:PutObject` on the new Silver prefix. Confirmed with `simulate-principal-policy` (`implicitDeny` → `allowed`) |
| 2 | "Missing required arguments" | The console Run button doesn't pass parameters. Start the job from the CLI with `--arguments` |
| 3 | Job run not visible in the console | Check the region, open the job's Runs tab, use View details |
| 4 | `MERGE INTO` syntax errors over and over | Replaced with `INSERT … WHERE NOT EXISTS` |
| 5 | Query editor ran only part of the script | Something was highlighted. Deselect everything |
| 6 | Told to `CALL` before `CREATE PROCEDURE` | Create first |
| 7 | AI added DynamoDB | Checkpoint kept in Redshift |
| 8 | Window skipped boundary files | `start < ts < end` → `start <= ts < end` |
| 9 | "No state file was found" | `terraform import` the existing resources |
| 10 | Plan wanted "7 to add" | Wrong folder, no state. Go back to the folder with the `.tfstate` |
| 11 | State machine rejected (`Sql.$`) | SQL moved into the coordinator Lambda |
| 12 | `permission denied for relation …` (×2) | Redshift `GRANT`s to `IAMR:<role>` |
| 13 | Failed after Glue had succeeded | **Redrive from failure**, not a new run |

---

## What's blocked for you

| Phase | Needs | Status |
|---|---|---|
| 0–8 | S3, your Glue role, your Redshift role, Query editor | **You can do these now** |
| 9 | A role for the coordinator Lambda (trusts `lambda.amazonaws.com`) | Same role problem as EventBridge, so ask Evan |
| 10 | A Step Functions role (trusts `states.amazonaws.com`), plus Step Functions access on your account | Ask Evan. Step Functions wasn't in the original student policy |
| 12 | The scheduler role (trusts `scheduler.amazonaws.com`, `states:StartExecution`) | Already asked |

**One message to Evan can cover all three roles:** coordinator Lambda, Step Functions, and scheduler, with the permissions listed above. Until then, Phases 0–8 run end to end by hand, which shows the incremental logic, the checkpoint, and idempotency.
