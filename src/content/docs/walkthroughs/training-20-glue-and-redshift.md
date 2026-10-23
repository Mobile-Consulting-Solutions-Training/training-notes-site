---
title: "Walkthrough - Training 20: Glue and Redshift Serverless"
description: "Restarting ingestion, rebuilding Bronze to Silver on AWS Glue, and starting the Gold layer in Redshift Serverless."
sidebar:
  order: 200
---

Source material: [Training 20 notes](/training-notes-site/notes/training-20/) and the class recording transcript (`transcriptions/Training 20 – 2026-10-08 13-23-23/`). Evan's reference chat: "AWS Glue Class Outline". Homework: `homework/submission/Homework - Training 20 (Answers).md`. Previous class: [Walkthrough - Training 19 (Citi Bike Pipeline Build)](/training-notes-site/walkthroughs/training-19-citi-bike-pipeline/).

**How to use this:** read it top to bottom once. It follows the day in the order Evan did it, with each step framed as the problem it solves. Then do the self-check without looking back.

---

## The one-paragraph version

Yesterday's pipeline worked once, then quietly stopped. Today Evan **restarted it** (the schedule's end time had passed), so new Citi Bike snapshots landed in Bronze every 5 minutes: **incremental loading**. Then he rebuilt the Bronze → Silver step on **AWS Glue** instead of EMR, to show a second way to run Spark on AWS. Getting it working took five fixes (wrong region, a name clash, a typo, a missing `/*` in a policy, an overwrite needing delete permission). Then he started the **Gold** layer in **Redshift Serverless**, a real data warehouse. Creating it was easy; *connecting Glue to it* hit the hard parts of the cloud: credentials (Secrets Manager) and networking (VPCs). The day ended with a networking error that was fixed the next morning (Training 21).

---

## You already know most of this

| You did this before | Class | Today's version | What changes |
|---|---|---|---|
| `aws configure` with a profile | Training 19 | Your own **access keys** for the CLI | Now students have keys too |
| A cron job on a timer | Training 1 | **EventBridge schedule** with start/end times | A schedule silently stops after its end time |
| Spark on EMR Serverless | Training 19 | **Glue job** | Same Spark code, different service |
| Hive Metastore | Training 8 | **Glue Data Catalog** | AWS's managed metastore |
| Snowflake warehouse + compute | Training 16–17 | **Redshift Serverless** namespace + workgroup | Same split: storage vs compute |
| Snowflake credits | Training 16 | Glue **DPUs**, Redshift **RPUs** | Units of compute you're billed for |
| Spark DataFrame | Training 7–9 | Glue **DynamicFrame** | A more forgiving DataFrame for messy JSON |
| Star schema theory | Training 5 | Gold in Redshift as a star | Built for real next class |

---

## Step 1: "Students can't do anything" → access keys and permissions

The first half hour was Evan discovering he could edit the student group's IAM policy himself:

- **CloudWatch Logs** access was added, and a student confirmed by opening the Lambda's log group. Another student saw 115 log groups instead of 436 because they were in **N. Virginia instead of Ohio**. *Check the region first, always.*
- **Access keys** for the CLI: username (top right) → **Security credentials → Create access key → CLI** → download the CSV (the secret is shown **once**) → `aws configure` (key, secret, `us-east-2`, `json`) → test with `aws s3 ls`.
- An error about **tags** when creating the key is harmless (students can't tag resources). If you see the ID and secret, it worked.

**Why Evan's own commands kept failing with "security token is invalid":** his keys live under a **named profile** (`company`), so he needed `--profile company` on every command. Students' keys are the **default** profile, so they don't. Remember this when copying his commands.

---

## Step 2: "The data stopped arriving" → restart the schedule (incremental loading)

Bronze had files for hours 18, 19, 20 on Oct 7, then nothing. The **EventBridge schedule's end time** had passed. Evan edited `citi-bike-ingestion-5-min` with a new start (14:15) and end (17:00) for Oct 8, and new files appeared every 5 minutes.

Evan named what this is:

> "Not quite a streaming job. You would refer to what's happening here as **incremental loading**. You are regularly bringing new data into a system, but it's not a continuous stream like Kafka."

| | Full load | **Incremental load** | Streaming |
|---|---|---|---|
| Moves | Everything, every time | Only what's new | Each event as it happens |
| Cadence | Occasional | Regular small batches (every 5 min) | Continuous |
| Here | — | Lambda + EventBridge | Kafka/Kinesis later in the course |

---

## Step 3: "Do Bronze → Silver again, the Glue way" → AWS Glue

### Why a second service for the same job?

Evan asked the class (including you) why use Glue instead of EMR. His answer:

> "The classical answer is that EMR is not serverless... but what we've been using for EMR *is* serverless. **EMR is closer to the original technology**. It functions like Hadoop does, and the code we put up there was literally just Spark code. **Glue can run plain Spark too, but it also has its own API with its own standards and data structures.** One reason you'd run Glue is if you want to use the **DynamicFrame** API." It's "not really about control."

So: **same engine (Spark), different packaging.** EMR = Spark as Spark. Glue = Spark plus AWS's ETL toolkit (GlueContext, DynamicFrame, Data Catalog, crawlers, job bookmarks).

### What a Glue job needs

| Piece | Today's value | Why |
|---|---|---|
| **Execution role** | `AWSGlueServiceRole-CitiBike`, trusting `glue.amazonaws.com` | Can't reuse the EMR role: it trusts a different service |
| Managed policy | `AWSGlueServiceRole` | Basic Glue permissions (logs, catalog) |
| Inline S3 policy | Read Bronze + script, write Silver, use TempDir | Least privilege |
| Script in S3 | `scripts/glue/citibike_glue_etl.py` | Glue downloads it at start |
| Worker type / count | `G.1X` × 2 | 2 DPUs = 8 vCPU / 32 GB |
| Timeout | 10 minutes | Cost guard |
| Max concurrent runs | 1 | Runs can't overlap |
| Job bookmarks | Enabled | Remembers processed files (incremental) |
| One code change | `spark.conf.set("spark.sql.session.timeZone", "UTC")` | Timestamps stay UTC like the Bronze keys |

### The five failures (this is the real lesson)

| # | What Evan saw | Real cause | Fix | General lesson |
|---|---|---|---|---|
| 1 | CLI said the job was created; console showed nothing | CLI default region was **us-east-1**, console on us-east-2 | Delete it there, `aws configure set region us-east-2`, recreate | "It succeeded but I can't see it" → check the region |
| 2 | A student's job appeared in Evan's console, pointing at the student's bucket | **Shared account**, same job name → overwritten | Unique names (add initials) | In a shared account, names collide |
| 3 | `s3 cp`: file does not exist | Hyphens vs underscores in the filename | Rename | Read the error literally |
| 4 | `Error downloading from S3 ... scripts/...` | Policy resource lacked `/*`, so `GetObject` was an **implicit deny** | Add `/*` to object ARNs | Bucket ARN ≠ object ARN |
| 5 | `not authorized to perform s3:DeleteObject` | Overwrite mode deletes old files first; the path wasn't covered by the policy | Write to the allowed prefix, switch to **append** | Overwrite needs delete permission |

Then it **succeeded** in about 2 minutes, with Snappy Parquet files in Silver. He reran it from the CLI (`aws glue start-job-run`, `get-job-runs`) and saw the same run in the console: CLI and console are two views of the same thing.

**Implicit deny** deserves a sentence: IAM denies everything by default. If no statement *allows* an action on that exact resource, it's denied, even though nobody wrote "Deny". A missing `/*` is enough.

### DPUs

> "A DPU measures allocated compute, not processing speed. More DPUs does not always mean a faster job." 1 DPU = 4 vCPU + 16 GB. Two G.1X workers = 8 vCPU / 32 GB "just to move our data from Bronze to Silver," but each run took 1–2 minutes so it cost little.

---

## Step 4: "We need a real warehouse" → Redshift Serverless

Evan: "Another directory of Parquet files in S3 is a completely normal and reasonable kind of gold layer, but Redshift is going to be more enlightening." And the Gold schema should be a **star schema**, because dimensional modeling is "highly relevant in a large number of projects."

Interviewers care most about: **S3, Lambda, EMR, Glue, Redshift.**

### Two pieces, like Snowflake

| Piece | Evan's | Is | Analogy |
|---|---|---|---|
| **Namespace** | `citibike-ns` | Storage: databases (`dev`), schemas, tables, users, the role Redshift uses for `COPY` | The library's books and catalog |
| **Workgroup** | `citibike-wg` | Compute: RPUs, network (VPC/subnets/security group), the endpoint | The reading room and librarians |

Settings he chose: "price-performance target" (Redshift scales itself), defaults for VPC/subnets/security group ("just handled for us"), no enhanced VPC routing, database `dev`, and **no admin username/password** (which came back to bite him). Then **Query editor v2** (connect as a federated user) is "the main thing you'll look at when you actually use Redshift."

**Ingress vs egress:** "Ingress refers to traffic coming into a system, as opposed to egress, traffic going out." He created a security group so Glue workers can reach each other and Redshift.

---

## Step 5: "Connect Glue to Redshift" → where the cloud gets hard

Glue (running Spark) has to log into Redshift (a database). That needs a **Glue connection**: JDBC URL, credentials and network placement.

| Attempt | Problem | Why |
|---|---|---|
| Create the connection with a username/password | `AccessDenied` creating a secret, **even as administrator** | Glue stores the password in **Secrets Manager**, which wasn't allowed |
| Look up the Redshift admin secret | None existed | The workgroup was created **without** an admin user/password |
| Set one: `aws redshift-serverless update-namespace` | Password needs an uppercase letter | Then the connection was created from the CLI |

Evan's frustration ("Why can't I just specify a username and password?") is worth remembering: **authentication is the most annoying part of cloud work, for everyone.** The professional move is to decide credentials up front (admin user + Secrets Manager) when creating the warehouse.

### The Glue-style script

He then wrote the Silver → Redshift job "the Glue way":

```python
sc = SparkContext()
glueContext = GlueContext(sc)          # Glue's wrapper around Spark
spark = glueContext.spark_session      # plain Spark still available
job = Job(glueContext); job.init(args["JOB_NAME"], args)
# ... read Silver, transform with normal Spark ...
dyf = DynamicFrame.fromDF(df, glueContext, "gold")
glueContext.write_dynamic_frame.from_jdbc_conf(frame=dyf, catalog_connection="<conn>",
    connection_options={"dbtable": "public.citibike_station_snapshot", "database": "dev"},
    redshift_tmp_dir="s3://<bucket>/glue-temp/")
job.commit()
```

> "A **DynamicFrame** is basically like a DataFrame, except that the number of columns doesn't have to be as strict. It's designed for handling JSON-type data, which is nested, so it's more flexible."

Note `redshift_tmp_dir`: Glue doesn't insert row by row. It **stages files in S3**, then Redshift bulk-loads them with `COPY`. (That detail caused the next day's permission error.)

### Where it ended

He created the target table in the query editor (`public.citibike_station_snapshot`: station ID, snapshot timestamp, station mode, bikes/e-bikes/docks available, utilization, is_empty, is_full, is_operational), started the job, and it failed:

> **"Could not find S3 endpoint or NAT gateway for subnet ID."** "This is not an authentication problem. This is a **networking** problem, a low-level cloud setup problem."

Too big to debug in 10 minutes, so it was carried to Training 21. Why it happened: the Glue connection made the job run **inside Redshift's private subnet**, and that subnet had **no route to S3**. (Fix in Training 21: an S3 Gateway Endpoint.)

> "Frustrating problems like this that don't seem to make any sense are just a normal part of working on cloud services... They all have NAT gateways, subnets and annoying authentication problems. Even Google Cloud."

---

## The whole picture at the end of the day

```
EventBridge (every 5 min, 14:15–17:00) ──▶ Lambda ──▶ S3 bronze/
                                                         │
                     ┌───────────────────────────────────┤
                     ▼                                   ▼
        EMR Serverless (Training 19)         Glue job (today, works)
                     │                                   │
                     └──────────────▶ S3 silver/ ◀────────┘
                                          │
                                          ▼  Glue job "the Glue way" + Glue connection
                                   ✖ networking error (no S3 route from the subnet)
                                          │
                                          ▼
                          Redshift Serverless citibike-ns / citibike-wg
                          public.citibike_station_snapshot (empty, for now)
```

---

## Corrections and clarifications

| Said or implied in class | More precisely |
|---|---|
| "Glue is basically a substitute for EMR" | For this job, yes. But Glue adds its own ETL API (DynamicFrame, Catalog, bookmarks) and EMR supports other frameworks (Hive, Presto, Flink) |
| VPCs and subnets are "low priority, more for cloud specialists" | They became the blocker for the very next step. Data engineers need the basics (Training 21) |
| The invalid-token errors looked mysterious | They're **authentication** errors from a missing `--profile`, not permission errors |

---

## Pairs people mix up

| These two | The difference |
|---|---|
| EMR vs Glue | Spark as Spark (closest to Hadoop) vs Spark + AWS's ETL API |
| DataFrame vs DynamicFrame | Strict schema vs flexible schema for messy/nested data |
| DPU vs RPU | Glue's compute unit vs Redshift Serverless's compute unit |
| Namespace vs workgroup | Storage (databases, users) vs compute (RPUs, network) |
| Overwrite vs append | Delete then write (needs `DeleteObject`) vs add new files |
| Implicit deny vs explicit deny | Nothing allowed it vs a Deny statement blocks it |
| Ingress vs egress | Traffic in vs traffic out |
| Authentication error vs authorization error | Who are you (bad token, wrong profile) vs what may you do (AccessDenied) |
| Incremental load vs streaming | Small regular batches vs continuous events |

---

## Self-check

<details><summary>1. The schedule ran yesterday but no files arrived today. What's the first thing to check?</summary>

The schedule's start/end time (it had expired), then the scheduler role's permission to invoke the Lambda.
</details>

<details><summary>2. Evan's create-job command succeeded but the console showed nothing. Why?</summary>

The CLI's default region was us-east-1; the console was on us-east-2.
</details>

<details><summary>3. Why couldn't Glue reuse the EMR execution role?</summary>

A role's trust policy names which service can assume it. The EMR role trusts emr-serverless.amazonaws.com, not glue.amazonaws.com.
</details>

<details><summary>4. The policy allowed s3:GetObject on arn:aws:s3:::bucket, but GetObject was denied. Why?</summary>

Objects need the object ARN `arn:aws:s3:::bucket/*`. Without it, nothing allows the action, so it's an implicit deny.
</details>

<details><summary>5. Why did the job need s3:DeleteObject?</summary>

It wrote in overwrite mode, which deletes existing files before writing. Append mode only adds.
</details>

<details><summary>6. What's Evan's answer to "why Glue instead of EMR?"</summary>

EMR is closer to the original Hadoop/Spark technology (plain Spark). Glue runs plain Spark too but adds its own API and data structures, like DynamicFrame. Use Glue when you want that API.
</details>

<details><summary>7. What are a namespace and a workgroup?</summary>

Namespace = storage side (databases, schemas, tables, users, IAM roles for COPY). Workgroup = compute side (RPUs, network, endpoint).
</details>

<details><summary>8. Why did creating the Glue → Redshift connection fail for an administrator?</summary>

Glue tried to create a Secrets Manager secret for the password, which was denied, and the workgroup had no admin password to begin with.
</details>

<details><summary>9. What does redshift_tmp_dir do?</summary>

Glue stages data as files in S3 there, then Redshift loads them with COPY.
</details>

<details><summary>10. "Could not find S3 endpoint or NAT gateway for subnet": authentication, authorization or networking?</summary>

Networking: the job ran inside a private subnet with no route to S3.
</details>

---

## If an interviewer asks "Glue or EMR?"

"Both run Spark serverlessly today, so it's less about serverless versus clusters. EMR is closest to open-source Hadoop and Spark: plain Spark code, more frameworks and tuning options. Glue runs plain Spark too, but adds a managed ETL layer: the Data Catalog, crawlers, job bookmarks for incremental runs, and the DynamicFrame API for messy, nested data. In my Citi Bike pipeline I ran the same Bronze-to-Silver transform on both, and used Glue for Silver to Redshift because its connections and DynamicFrame writer handle the warehouse load."
