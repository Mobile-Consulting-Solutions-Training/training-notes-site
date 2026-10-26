---
title: Study Guide - Day 20
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 20: AWS Glue and Redshift"
sidebar:
  order: 200
---

Study Guide - Day 20 (source: notes/Training 20.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**CLI Access Keys.** Username (top right) → Security credentials → Create access key → CLI → download the CSV (the secret is shown once) → `aws configure` (key ID, secret, `us-east-2`, `json`) → test with `aws s3 ls`. Paste, don't type. If a key leaks, deactivate and replace it. A tag error while creating the key is harmless. Evan's "security token is invalid" errors came from his keys living under a named profile (`--profile company`); students use the default profile.

**CloudWatch Logs.** Logs → Log groups (newer console: Log Management) → `/aws/lambda/<function>` → log streams. Check the region: one student saw 115 groups instead of 436 because they were in N. Virginia.

**Incremental Loading.** Regularly bringing only new data into a system in small batches (every 5 minutes here). "Not quite a streaming job": streaming is continuous (Kafka). The schedule had stopped because its end time had passed; Evan reset start 14:15 / end 17:00.

**AWS Glue vs EMR.** Both run Spark serverlessly. Evan's answer: "EMR is closer to the original technology. It functions like Hadoop does, and the code was literally just Spark code. Glue can run plain Spark too, but it has its own API with its own standards and data structures, like the DynamicFrame." Glue = Spark + GlueContext, DynamicFrame, Data Catalog, crawlers, job parameters, job bookmarks. "Not really about control."

**Creating a Glue Job.** Execution role trusting `glue.amazonaws.com` (can't reuse the EMR role) + `AWSGlueServiceRole` + an inline S3 policy; script uploaded to `scripts/glue/`; `aws glue create-job` with `glueetl`, `G.1X` × 2 workers, timeout 10, max concurrent runs 1, job bookmarks enabled, TempDir; `spark.sql.session.timeZone = UTC`.

**Five Glue Failures.** (1) Created in us-east-1 instead of us-east-2. (2) A student's job with the same name overwrote Evan's (shared account). (3) Filename hyphens vs underscores. (4) `Error downloading from S3` = policy missing `/*`, so GetObject was an **implicit deny**. (5) `s3:DeleteObject` denied because **overwrite** mode deletes first and the path wasn't in the policy; switched to **append**. Then success (~2 min, Snappy Parquet).

**DPU.** Data Processing Unit = 4 vCPU + 16 GB. "Measures allocated compute, not processing speed; more DPUs doesn't always mean faster." G.1X = 1 DPU per worker.

**Redshift Serverless.** Gold as a real warehouse (S3 Parquet would also be a valid Gold, "but Redshift is more enlightening"), modeled as a **star schema**. **Namespace** (`citibike-ns`) = storage: databases (`dev`), tables, users, IAM roles for COPY. **Workgroup** (`citibike-wg`) = compute: RPUs, VPC/subnets/security group, endpoint. Query editor v2 = "the main thing you'll look at." Core services interviewers care about: S3, Lambda, EMR, Glue, Redshift.

**Ingress vs Egress.** Ingress = traffic coming into a system; egress = traffic going out. Security group rules let Glue workers reach each other and Redshift.

**Glue → Redshift Connection.** A Glue connection holds the JDBC URL, credentials and network placement. Creating it with a password made Glue try to create a **Secrets Manager** secret, which was denied even for an admin. The workgroup had no admin password; Evan set one with `aws redshift-serverless update-namespace`. "Why can't I just specify a username and password?"

**Glue-Style Code.** `SparkContext` → `GlueContext` → `spark_session`; `Job.init` / `job.commit` (bookmarks); `DynamicFrame.fromDF`; `glueContext.write_dynamic_frame.from_jdbc_conf(..., redshift_tmp_dir=...)` stages files in S3 for Redshift to COPY. DynamicFrame = "like a DataFrame, except the columns don't have to be as strict; designed for nested JSON."

**Where It Ended.** Target table `public.citibike_station_snapshot` created; the Silver → Redshift job failed with "Could not find S3 endpoint or NAT gateway for subnet ID": a **networking** problem (the job ran inside Redshift's private subnet with no route to S3). Fixed in Training 21.

---

# Part 2: Cheat Sheet

## Access
- Create access key → CLI → CSV once → `aws configure` → `aws s3 ls` / `aws sts get-caller-identity`
- Invalid token = authentication problem (wrong/missing profile)

## Incremental Loading
- Full load (everything) · **incremental** (only new, regular batches) · streaming (continuous)

## Glue vs EMR
- EMR = closest to Hadoop/Spark, plain Spark · Glue = Spark + its own API (DynamicFrame, Catalog, crawlers, bookmarks)

## Glue Job Settings
- Role trusts `glue.amazonaws.com` · `glueetl` · G.1X × 2 · timeout 10 · MaxConcurrentRuns 1 · bookmarks on · TempDir

## Glue Failures → Lessons
- Can't see it → **region** · name clash → **unique names** · implicit deny → **`/*`** · DeleteObject → **overwrite vs append**

## Compute Units
- **DPU** (Glue) = 4 vCPU / 16 GB · **RPU** (Redshift Serverless)

## Redshift Serverless
- **Namespace** = storage · **Workgroup** = compute + network · database `dev` · Query editor v2

## Connection Pain
- Glue connection = JDBC URL + credentials + subnet/SG/AZ
- Password → Secrets Manager secret → denied · set admin password up front

## Glue Code
- GlueContext · DynamicFrame (flexible schema) · `write_dynamic_frame.from_jdbc_conf` · `redshift_tmp_dir` → COPY · `job.commit()`

## Networking Error
- "Could not find S3 endpoint or NAT gateway for subnet" = no route to S3 from the private subnet

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: How do you get AWS CLI access as an IAM user?
A: Click your username, go to Security credentials, create an access key for the CLI and download the CSV, then run aws configure with the key ID, secret, region us-east-2 and JSON output, and test with aws s3 ls.

Q: Why did Evan keep getting "the security token included in the request is invalid"?
A: His keys are stored under a named profile, so commands without --profile company used other keys. It's an authentication problem, not a permissions problem.

Q: What is incremental loading?
A: Regularly bringing only new data into a system in small batches, like every five minutes. It isn't streaming, which is continuous.

Q: Why use Glue instead of EMR, according to Evan?
A: EMR is closer to the original Hadoop and Spark technology and runs plain Spark. Glue can also run plain Spark but has its own API and data structures, like the DynamicFrame, so you choose Glue when you want that API.

Q: Why couldn't the Glue job reuse the EMR role?
A: A role's trust policy names which service can assume it. The EMR role trusts EMR Serverless, so Glue needs a role that trusts glue.amazonaws.com.

Q: Evan's create-job succeeded on the CLI but the console showed nothing. Why?
A: The CLI's default region was us-east-1 while the console was on us-east-2.

Q: What is an implicit deny?
A: IAM denies everything by default. If no statement allows an action on that exact resource, it's denied even without a Deny statement, like when an object ARN is missing the /* at the end.

Q: Why did the Glue job need s3:DeleteObject?
A: It wrote in overwrite mode, which deletes existing files first. Switching to append only adds files.

Q: What is a DPU?
A: A Data Processing Unit, Glue's compute unit: 4 vCPUs and 16 GB of memory. It measures allocated compute, not speed.

Q: What's the difference between a Redshift Serverless namespace and workgroup?
A: The namespace is the storage side: databases, tables, users and IAM roles. The workgroup is the compute side: RPUs, network settings and the endpoint you connect to.

Q: What is ingress versus egress?
A: Ingress is traffic coming into a system; egress is traffic going out.

Q: Why did creating the Glue connection to Redshift fail for an administrator?
A: Using a password made Glue try to create a Secrets Manager secret, which was denied, and the workgroup didn't have an admin password set in the first place.

Q: What's a DynamicFrame?
A: Glue's version of a DataFrame that doesn't require a strict schema, designed for messy or nested JSON. You convert with DynamicFrame.fromDF and toDF.

Q: What does redshift_tmp_dir do in a Glue write to Redshift?
A: Glue stages the data as files in S3 there, and Redshift bulk-loads them with COPY.

Q: What error ended the class, and what kind of problem was it?
A: "Could not find S3 endpoint or NAT gateway for subnet." A networking problem: the job ran in Redshift's private subnet with no route to S3.
