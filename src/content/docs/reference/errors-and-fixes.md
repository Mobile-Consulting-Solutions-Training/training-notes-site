---
title: Errors & Fixes
description: Every error hit in class and homework, with its cause and fix, grouped by tool.
sidebar:
  order: 1
---

82 errors hit in class and in homework, each with its cause and fix, grouped by tool. Use Ctrl+F / Cmd+F to search for the exact error text you're seeing. The Day column links to that day's notes.

## How to debug any of these

| Habit | Why |
|---|---|
| Read the **first** error, not the last | A downstream failure is often a symptom. In Training 29, Silver failed only because Bronze had failed first |
| Copy the **exact** error text | AWS `AccessDenied` and Azure `AuthorizationFailed` name the action, the identity and the resource. That's what an admin needs to grant |
| Tell **authentication** from **authorization** | "Could not validate credentials" = wrong profile or login. "Not authorized to perform X" = a missing permission. "Permission denied for relation" = a database `GRANT`, not IAM |
| Check the **region**, **profile** and **folder** | Many "it's not there" problems were a CLI default region, a missing `--profile`, or running Terraform in the wrong folder |
| Wait for **propagation** | Azure role assignments take minutes. AWS IAM is faster but also eventually consistent |
| Match **versions** | Spark connector JARs must match your Spark's Scala version (`_2.12` vs `_2.13`), and sbt and the JDK must match the build |
| Is the thing actually **running**? | `docker ps -a`, `nc -vz localhost <port>`, `lsof -i :<port>` before changing code |

## Docker, ports and containers

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| `bind: address already in use` on 27017 | Something already held MongoDB's port | Find the owner: `sudo ss -ltnp \| grep :27017` or `sudo lsof -nP -iTCP:27017 -sTCP:LISTEN`, then `ps -fp <PID>` | [13](/training-notes-site/notes/training-13/) |
| `MongoDB cannot start: Linux kernel versions 6.19 and newer has a known incompatibility` | Recent MongoDB builds refuse to run on kernel 6.19+ (SERVER-121912) | Pin an older image: class used `mongo:8.0.4`; the homework machine used `mongo:7.0` | [13](/training-notes-site/notes/training-13/) |
| `Conflict. The container name "/mongodb" is already in use` | The failed container still exists (stopped) | `docker rm mongodb`, then `docker run` again. `docker ps` only lists running containers; use `docker ps -a` | [13](/training-notes-site/notes/training-13/), [14](/training-notes-site/notes/training-14/) |
| `docker start mongodb` → `bind: address already in use` | Another process holds 27017 | `sudo lsof -nP -iTCP:27017 -sTCP:LISTEN` → identify it before deleting anything | [14](/training-notes-site/notes/training-14/) |

## Git, CI/CD and Python environments

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| `missing ScriptRunContext! ... bare mode` | Streamlit app started with `python` | `streamlit run dashboard.py` | [13](/training-notes-site/notes/training-13/) |

## Spark and connectors

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| `[DATA_SOURCE_NOT_FOUND] Failed to find the data source: mongodb` | MongoDB **Spark connector** missing, even though MongoDB was running | Add `org.mongodb.spark:mongo-spark-connector_2.13:10.5.0` to `--packages` | [13](/training-notes-site/notes/training-13/) |

## Kafka, Flink and streaming

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| `Failed to find data source: kafka` | Spark-Kafka connector JAR not on Spark's classpath | `spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_<scala>:<spark> consumer.py` | [13](/training-notes-site/notes/training-13/), [14](/training-notes-site/notes/training-14/) |
| `NoSuchMethodError: scala.Predef$.wrapRefArray` | Connector built for the **wrong Scala version** (`_2.12` connector on a Scala 2.13 Spark) | Match both: `spark-sql-kafka-0-10_2.13:3.5.1` for Spark 3.5.1 / Scala 2.13. Check with `spark-submit --version` | [13](/training-notes-site/notes/training-13/) |
| `nc -vz localhost 9092` → Connection refused, although the broker log says it's listening | Port only open **inside** the container, not published to the host | Recreate the container with `-p 9092:9092`; check with `docker ps` / `docker port kafka` | [13](/training-notes-site/notes/training-13/) |
| `No readable meta.properties files found` | Kafka 4.x built from source (KRaft) with **unformatted storage** | `kafka-storage.sh random-uuid` → `kafka-storage.sh format --standalone -t <id> -c config/server.properties` (see `Training 14.md`) | [13](/training-notes-site/notes/training-13/), [14](/training-notes-site/notes/training-14/) |
| `Socket server failed to bind to 0.0.0.0:9092: Address already in use` | The Docker Kafka container already held port 9092 | `docker stop kafka`; confirm the port is free with `sudo lsof -i :9092` | [13](/training-notes-site/notes/training-13/) |
| `TypeError: Could not found the Java class 'org.apache.flink.connector.kafka.source.KafkaSource.builder'` | The **Flink Kafka connector** JAR is missing | Download `flink-connector-kafka-5.0.0-2.1.jar` from Maven Central; `env.add_jars("file:///...")` | [14](/training-notes-site/notes/training-14/) |
| `NoClassDefFoundError: org/apache/kafka/clients/consumer/OffsetResetStrategy` | Connector found, but its **transitive dependency** `kafka-clients` is missing (the ~418 KB connector JAR doesn't bundle it) | Also download `kafka-clients-4.1.0.jar` (the version the connector's Maven metadata requires) and add it to `add_jars` | [14](/training-notes-site/notes/training-14/) |
| `UnknownTopicOrPartitionException` | Most likely running the old `consumer.py` (subscribes to the now-deleted `test-topic`) | Run the right file; confirm the topic name with `grep -n subscribe *.py` | [14](/training-notes-site/notes/training-14/) |
| `Command 'flink' not found` | PyFlink doesn't install the CLI | Run jobs with `python`, or install the Flink binary distribution | [14](/training-notes-site/notes/training-14/) |
| pip dependency conflicts after `pip install apache-flink` | Installed into a shared Python environment | A dedicated venv for Flink | [14](/training-notes-site/notes/training-14/) |
| `Could not found the Java class ...KafkaSource.builder` | Flink Kafka connector JAR missing | `env.add_jars("file:///.../flink-connector-kafka-5.0.0-2.1.jar")` | [14](/training-notes-site/notes/training-14/) |
| `NoClassDefFoundError: .../OffsetResetStrategy` | `kafka-clients` JAR missing | Add `kafka-clients-4.1.0.jar` too | [14](/training-notes-site/notes/training-14/) |

## AWS IAM, S3, Glue and Lambda

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| Job created successfully on the CLI but not visible in the console | CLI default region was **us-east-1**; the console was on us-east-2 | Delete the job in us-east-1, `aws configure set region us-east-2`, create again | [20](/training-notes-site/notes/training-20/) |
| Another student's job showed in Evan's console (pointing at the student's bucket) | **Shared account**: same job name → one overwrites the other | Use unique names (e.g. add initials) | [20](/training-notes-site/notes/training-20/) |
| Script file "does not exist" on `s3 cp` | Local file used hyphens, command used underscores | Rename to match | [20](/training-notes-site/notes/training-20/) |
| `Error downloading from S3 bucket ... key scripts/...` | IAM policy resources missing `/*`, so `s3:GetObject` was an **implicit deny** | Edit the inline policy: object ARNs end with `/*` | [20](/training-notes-site/notes/training-20/) |
| `not authorized to perform s3:DeleteObject` | Script wrote (overwrite mode) to `silver/.../station_status` but the policy only allowed `glue_station_status` | Point the script at the allowed prefix and switch to **append** mode (more realistic for new data each run) | [20](/training-notes-site/notes/training-20/) |
| `Failed to connect` / `Connection refused` / `Unable to create executor`, then **`Not authorized`** | **IAM**: Glue couldn't create its S3 folder; the connection error was *caused by* an authorization error | `aws iam put-role-policy` from the CLI adding S3 access (a new inline policy, doesn't overwrite the others). Restarted: `RUNNING`, error message `null` (= good) | [22](/training-notes-site/notes/training-22/) |
| `Unresolved column` | The AI-generated script used **automatic JSON schema inference**, "a poor choice for a streaming demo where we already know the record structure" | Defined an explicit schema with `StructType` / `StructField` (`station_schema`) | [22](/training-notes-site/notes/training-22/) |
| `list index out of range` on `raw_column = df.columns[0]` | The DataFrame passed to `process_batch` had **zero columns**: the schema was defined but **never passed to the Kinesis reader** | Add `schema=station_schema` to the Glue Kinesis source; add a guard `if not df.columns: print(...); return` | [22](/training-notes-site/notes/training-22/) |
| Same error after "fixing" it | **Human copy/paste error** from many manual edits: the file had **two competing parsing implementations** | Asked the AI for a **complete replacement file** based on the current code; deployed it. **Worked** | [22](/training-notes-site/notes/training-22/) |
| `aws s3 ls` error | Forgot `--profile company` | Add the profile | [28](/training-notes-site/notes/training-28/) |
| "Broken pipe" error when piping the S3 listing | The listing was piped into `head`, which closes early | Harmless, ignore it | [28](/training-notes-site/notes/training-28/) |
| (Students) `ListBucket` not authorized on their own bucket | Policy `Resource` only listed Evan's bucket | Made `Resource` a list and added each student's bucket ARN | [28](/training-notes-site/notes/training-28/) |
| (Students) S3 403 on `GetObject` | `GetObject` was only allowed on Evan's bucket objects | Added `arn:aws:s3:::<student-bucket>/*` | [28](/training-notes-site/notes/training-28/) |
| `argument subcommand: Found invalid choice 'create-bucket'` from `aws s3 create bucket ...` | — | `aws s3api create-bucket ...` or `aws s3 mb s3://name` | [19](/training-notes-site/notes/training-19/) |
| `InvalidAccessKeyId: The AWS Access Key Id you provided does not exist in our records` | — | Remove/fix the exports, or pass `--profile company` | [19](/training-notes-site/notes/training-19/) |
| `BucketAlreadyExists: The requested bucket name is not available. The bucket namespace is shared by all users of the system.` | Bucket names are **globally unique across all AWS accounts**, and someone already owns `citi-bike-nyc` | Pick a more specific name. Evan switched to `citi-bike-nyc-pipeline`. Homework: **use your name** in yours | [19](/training-notes-site/notes/training-19/) |
| `IllegalLocationConstraintException: The unspecified location constraint is incompatible for the region specific endpoint this request was sent to.` | **Every region except `us-east-1`** needs `--create-bucket-configuration LocationConstraint=<region>` | Add it. ChatGPT on screen: "S3 has an odd special case: `us-east-1` doesn't require LocationConstraint, but other regions do." | [19](/training-notes-site/notes/training-19/) |
| Glue write failed, `TASK_WRITE_FAILED` | — | The Glue role lacked `s3:PutObject` on the new Silver prefix. Confirmed with `simulate-principal-policy` (`implicitDeny` → `allowed`) | [24](/training-notes-site/notes/training-24/) |
| "Missing required arguments" | — | The console Run button doesn't pass parameters. Start the job from the CLI with `--arguments` | [24](/training-notes-site/notes/training-24/) |
| Job run not visible in the console | — | Check the region, open the job's Runs tab, use View details | [24](/training-notes-site/notes/training-24/) |
| "Execution role must allow EventBridge Scheduler to assume the role" | He picked the **Lambda's** role, which trusts `lambda.amazonaws.com`, not the scheduler | New role `CitiBikeSchedulerRole` trusting `scheduler.amazonaws.com` | [19](/training-notes-site/notes/training-19/) |
| Schedule saved, but no new files arrived | The new role had a trust policy but **no permissions policy** | Inline policy allowing `lambda:InvokeFunction` on the function | [19](/training-notes-site/notes/training-19/) |

## Terraform and Step Functions

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| "No state file was found" | — | `terraform import` the existing resources | [24](/training-notes-site/notes/training-24/) |
| Plan wanted "7 to add" | — | Wrong folder, no state. Go back to the folder with the `.tfstate` | [24](/training-notes-site/notes/training-24/) |
| State machine rejected (`Sql.$`) | — | SQL moved into the coordinator Lambda | [24](/training-notes-site/notes/training-24/) |
| Failed after Glue had succeeded | — | **Redrive from failure**, not a new run | [24](/training-notes-site/notes/training-24/) |

## Redshift and SQL warehouses

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| Syntax | — | QUALIFY, or a CTE | [25](/training-notes-site/notes/training-25/) |
| `MERGE INTO` syntax errors over and over | — | Replaced with `INSERT … WHERE NOT EXISTS` | [24](/training-notes-site/notes/training-24/) |
| Query editor ran only part of the script | — | Something was highlighted. Deselect everything | [24](/training-notes-site/notes/training-24/) |
| Told to `CALL` before `CREATE PROCEDURE` | — | Create first | [24](/training-notes-site/notes/training-24/) |
| Window skipped boundary files | — | `start < ts < end` → `start <= ts < end` | [24](/training-notes-site/notes/training-24/) |
| `permission denied for relation …` (×2) | — | Redshift `GRANT`s to `IAMR:<role>` | [24](/training-notes-site/notes/training-24/) |

## Text-to-SQL and Bedrock

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| Wrong grain | — | Grain rules in the system prompt | [25](/training-notes-site/notes/training-25/) |
| Hallucinated column | — | Schema validation + refusal (`INSUFFICIENT_SCHEMA`) | [25](/training-notes-site/notes/training-25/) |
| Missing data | — | Add lat/long to the data model (Silver → Gold) | [25](/training-notes-site/notes/training-25/) |

## Azure sign-in, RBAC and Synapse

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| "Username may be incorrect" on the invite link | — | Open the link in the same browser where you're signed in to Teams, and choose to sign in with that Microsoft account | [27](/training-notes-site/notes/training-27/) |
| Authenticator seemed to need an Apple Store account on the same email | — | You don't. Install Microsoft Authenticator on your phone from its normal app store | [27](/training-notes-site/notes/training-27/) |
| "No eligible devices" | — | Set it up on the phone itself: scan the **QR code** the sign-in page shows, or use the **+** button in the Authenticator app to add the account | [27](/training-notes-site/notes/training-27/) |
| "We couldn't find an account with that username" in the CLI (portal worked on another computer) | CLI was signing in against the wrong tenant (personal Microsoft account flow) | `az logout`, `az account clear`, then `az login --tenant <tenant-id>` | [27](/training-notes-site/notes/training-27/) |
| "Subscription ... does not exist in cloud AzureCloud" | Logged in to a tenant that doesn't hold the training subscription | Log in with the right tenant first, then `az account set --subscription <id>` | [27](/training-notes-site/notes/training-27/) |
| Authenticator code rejected | It was an **email** one-time code prompt, not the Authenticator | Use the code type the prompt actually asks for | [27](/training-notes-site/notes/training-27/) |
| Asked for a "domain" | Org sign-in page wanted the organization's domain | Evan sent the domain to enter; or cancel and use `az login --tenant` / `--use-device-code` | [27](/training-notes-site/notes/training-27/) |
| "Due to a configuration change made by your administrator... you must use multi-factor authentication" when creating a resource group | Token from before MFA was enforced | `az logout`, run the suggested `az login` again, approve the Authenticator number match, choose the subscription number (Evan typed `1`) | [27](/training-notes-site/notes/training-27/) |
| "Home tenant ID" vs "tenant ID" confusion | A guest account's home tenant differs from the tenant it was invited into | Use the tenant that owns the training subscription | [27](/training-notes-site/notes/training-27/) |
| Storage browser: "You do not have permissions to list the data" | The portal browses as **your Entra user**, not the factory's identity | Gave his own user Storage Blob Data Contributor, waited, reloaded | [28](/training-notes-site/notes/training-28/) |
| (Students) No "Add role assignment" button | Students lack Owner / User Access Administrator | Send Evan the resource group, data factory and storage account names; he assigns the role (portal or CLI) | [28](/training-notes-site/notes/training-28/) |

## Azure Data Factory

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| ADLS linked service test: 403 | Factory managed identity had no data-plane role | Storage Blob Data Contributor on the storage account, then wait for propagation | [28](/training-notes-site/notes/training-28/) |
| S3 linked service test: "Credential is incorrect or does not have permission" | The inline policy lacked a list permission | Edited the IAM policy, test passed | [28](/training-notes-site/notes/training-28/) |
| ADLS linked service not in the sink dropdown | The first linked service was never saved/published | Recreated it, then clicked **Publish all** ("This resource has not been published by your data factory") | [28](/training-notes-site/notes/training-28/) |
| Copy failed after 15 s: "the operation is on a file citibike" | `citibike` was in the file-name field, so ADF treated it as a file | Put `bronze/citibike` in the **directory** field, file name blank | [28](/training-notes-site/notes/training-28/) |
| Copy succeeded but the sink path was wrong | The storage-account name was typed as a folder | Sink path = container `bronze` only. A **container** is the equivalent of an S3 bucket | [28](/training-notes-site/notes/training-28/) |

## Databricks, Delta and Auto Loader

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| Silver: "Failed to read dataset `...default.bronze_station_raw` … could not be resolved" | Downstream symptom: **Bronze failed first** | Find the *first* traceback (the Bronze one) | [29](/training-notes-site/notes/training-29/) |
| Bronze: Auto Loader can't find any JSON files | Wrong `source_path`: files were under the landing folder, not `station_status` | Correct the path | [29](/training-notes-site/notes/training-29/) |
| "Can't extract value from data: need a complex type" | Auto Loader **inferred** `data` as a string, so `.stations` can't be exploded | Pass an explicit `StructType` schema with `.schema(station_schema)` | [29](/training-notes-site/notes/training-29/) |

## MLflow

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| Run "not in Experiments" | — | `set_experiment()` with a path creates a **workspace experiment** at that path. Find it by clicking the "View run / View experiment" link MLflow prints under the cell, in the left sidebar under **Experiments** (Machine Learning / AI section), or in the Workspace browser at that path. The notebook's **Experiment** icon in the right panel shows only the notebook's default experiment, not one set by path | [30](/training-notes-site/notes/training-30/) |
| "Inferred schema contains integer columns" | — | MLflow warns that integer columns can't hold missing values, so a future input with a null would fail schema checks. Fix: cast integer feature columns to `float64` before `infer_signature` (it's only a warning) | [30](/training-notes-site/notes/training-30/) |

## Data modeling pitfalls

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| Double-counted totals | — | Write the grain sentence first; one grain per fact | [21](/training-notes-site/notes/training-21/) |
| Absurd totals (millions of "bikes") | — | `AVG`/`MIN`/`MAX`/last value over time | [21](/training-notes-site/notes/training-21/) |
| Small stations distort citywide numbers | — | Store additive parts, recompute ratios | [21](/training-notes-site/notes/training-21/) |
| Huge fact, inconsistent names | — | Move them to a dimension (Evan moved `capacity`) | [21](/training-notes-site/notes/training-21/) |
| Orphaned facts silently dropped by inner joins | — | Load dims first; run the orphan check; use an "Unknown" member row (key -1) for late-arriving dimensions | [21](/training-notes-site/notes/training-21/) |
| Past reports change after an update | — | SCD Type 2 | [21](/training-notes-site/notes/training-21/) |
| Gaps disappear from charts | — | Pre-generate the calendar | [21](/training-notes-site/notes/training-21/) |
| Fan-out (row multiplication) | — | Aggregate each fact to a common grain first, then join on conformed dimensions | [21](/training-notes-site/notes/training-21/) |
