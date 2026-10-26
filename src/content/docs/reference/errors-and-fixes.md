---
title: Errors & Fixes
description: Every error hit in class and homework, with its cause and fix, grouped by tool.
sidebar:
  order: 1
---

226 errors hit in class and in homework, each with its cause and fix, grouped by tool. Use Ctrl+F / Cmd+F to search for the exact error text you're seeing. The Day column links to that day's notes.

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
| `permission denied ... docker.sock` | Your user can't reach the Docker daemon | Make sure Docker Desktop (or the daemon) is running and your user has access | [13](/training-notes-site/notes/training-13/) |
| `mongodb` container exits right away | Image incompatible with the host | `docker logs mongodb` first. Pin an older image, e.g. `mongo:7.0` or `mongo:8.0.4` (the class version) | [13](/training-notes-site/notes/training-13/) |
| `Cannot connect to the Docker daemon` | Docker Desktop isn't running | Open Docker Desktop, wait for "Engine running", retry | [22](/training-notes-site/notes/training-22/) |
| `port is already allocated` | Something else is on 5433 | Change `-p 5433:5432` to `-p 5434:5432` | [22](/training-notes-site/notes/training-22/) |
| `Conflict. The container name "/cicd-homework" is already in use` | — | `docker rm -f cicd-homework` | [3](/training-notes-site/notes/training-3/) |
| `Bind for 0.0.0.0:8111 failed: port is already allocated` | — | Something else holds 8111. `docker ps` to find it, then remove it. Don't change the port | [3](/training-notes-site/notes/training-3/) |
| `curl: (7) Failed to connect` right after `run` | — | Uvicorn needs a second to start. Retry, or `docker logs cicd-homework` | [3](/training-notes-site/notes/training-3/) |
| `COPY failed: file not found` | — | You ran `docker build` from inside `app/`. Build from the repo root; the `.` is the build context | [3](/training-notes-site/notes/training-3/) |
| `denied` / `unauthorized` on `docker pull` | — | GHCR packages are often private by default. Either set the package's visibility to public in its package settings, or `docker login ghcr.io` with your own token that can read packages. Never put that token in the repo | [3](/training-notes-site/notes/training-3/) |

## Git, CI/CD and Python environments

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| `missing ScriptRunContext! ... bare mode` | Streamlit app started with `python` | `streamlit run dashboard.py` | [13](/training-notes-site/notes/training-13/) |
| `psycopg2` import error | Wrong Python environment | Install it in the interpreter you're running | [11](/training-notes-site/notes/training-11/) |
| `ModuleNotFoundError: streamlit` | venv not activated | `source .venv/bin/activate` | [26](/training-notes-site/notes/training-26/) |
| Page reruns and loses state when you click | Normal Streamlit behaviour | `st.session_state` | [26](/training-notes-site/notes/training-26/) |
| `__pycache__/` shows up in `git ls-files` | — | It was committed before `.gitignore` existed. Notes, Repository Discipline: `git rm -r --cached app/__pycache__`, then commit | [3](/training-notes-site/notes/training-3/) |
| Folder named `workflow` or `.github/workflows` missing the leading dot | — | Actions only reads `.github/workflows/`. The run never starts | [3](/training-notes-site/notes/training-3/) |
| `ModuleNotFoundError: No module named 'main'` | — | You ran pytest from the repo root. `cd app` first | [3](/training-notes-site/notes/training-3/) |
| `RuntimeError` / import error mentioning `httpx` | — | `httpx` didn't install. Re-run the `pip install` line | [3](/training-notes-site/notes/training-3/) |
| `pytest: command not found` | — | It installed into a different Python. Try `python -m pytest` | [3](/training-notes-site/notes/training-3/) |
| Run tests: `No module named 'main'` | — | `working-directory: app` missing on that step | [3](/training-notes-site/notes/training-3/) |
| Build: `invalid reference format: repository name must be lowercase` | — | The problem your lowercase step solves | [3](/training-notes-site/notes/training-3/) |
| Push: `denied: installation not allowed to Write organization package` or `permission_denied` | — | Check `permissions: packages: write` is still in the file; in an org, ask the org admin whether Actions may write packages. Don't create a token | [3](/training-notes-site/notes/training-3/) |
| Workflow never starts | — | Pushed to a branch other than `main`, or the file isn't in `.github/workflows/` | [3](/training-notes-site/notes/training-3/) |
| `manifest unknown` | — | Wrong owner path (old vs new, see above) or the push step didn't run | [3](/training-notes-site/notes/training-3/) |
| Warning that the image platform `linux/amd64` doesn't match the host | — | GitHub's runner builds amd64 images. Usually it still runs; the warning is informational | [3](/training-notes-site/notes/training-3/) |

## Postgres and SQL basics

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| `subquery in FROM must have an alias` | Missing alias on the derived table | Keep it | [22](/training-notes-site/notes/training-22/) |
| `relation "idx_orderdetails_product_category" already exists` | — | Use `CREATE INDEX IF NOT EXISTS ...`, or put `DROP INDEX IF EXISTS idx_orderdetails_product_category;` before the first `EXPLAIN ANALYZE` so the "before" plan really is before | [4](/training-notes-site/notes/training-4/) |
| `relation "orderdetails" does not exist` | — | You're connected to the wrong database. `\c sample_database`, then `\dt` to see the seven tables | [4](/training-notes-site/notes/training-4/) |
| Prompt changes from `=#` to `-#` | — | A statement is missing its `;`. Psql is still waiting. Type `;` and Enter | [4](/training-notes-site/notes/training-4/) |
| `column "Classic Cars" does not exist` | — | Double quotes mean an identifier. String values take single quotes: `'Classic Cars'` | [4](/training-notes-site/notes/training-4/) |
| Plan looks identical before and after | — | Check `\d orderdetails` lists your index. If it does, the planner chose not to use it (that's a valid answer) | [4](/training-notes-site/notes/training-4/) |
| Numbers vary run to run | — | Normal. `Execution Time` includes caching effects; compare the scan type, not milliseconds | [4](/training-notes-site/notes/training-4/) |
| `Connection to localhost:5432 refused` | — | Postgres container isn't running, or is mapped to a different port | [9](/training-notes-site/notes/training-9/) |
| `password authentication failed` | — | Wrong value in `PG_PASSWORD` | [9](/training-notes-site/notes/training-9/) |
| `relation "gold.fact_sales" does not exist` | — | Wrong database in `JDBC_URL`, or the `gold` schema lives in another database | [9](/training-notes-site/notes/training-9/) |

## Spark and connectors

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| `[DATA_SOURCE_NOT_FOUND] Failed to find the data source: mongodb` | MongoDB **Spark connector** missing, even though MongoDB was running | Add `org.mongodb.spark:mongo-spark-connector_2.13:10.5.0` to `--packages` | [13](/training-notes-site/notes/training-13/) |
| `NoSuchElementException: key not found: PG_PASSWORD` | Env var not exported in this shell | Export it, then re-run | [9](/training-notes-site/notes/training-9/), [11](/training-notes-site/notes/training-11/) |
| Wall of log text | Spark INFO logging | Set `spark.sparkContext.setLogLevel("ERROR")`. In a big stack trace, look for the one meaningful line | [12](/training-notes-site/notes/training-12/) |
| `java.lang.IllegalAccessError ... sun.nio.ch` on JDK 17 | — | Spark 3.x on JDK 17 sometimes needs `--add-opens` VM options. Bring the exact text and we'll pick the right ones | [9](/training-notes-site/notes/training-9/) |
| `Detected implicit cartesian product` | — | Happens when a join has no usable condition. You have `lit(false)` as the condition, so you shouldn't see it. If you do, bring the text | [9](/training-notes-site/notes/training-9/) |
| Join returns 0 rows in Task 4 | — | Key types differ (for example text vs integer) or values don't match. Compare `printSchema()` for both sides | [9](/training-notes-site/notes/training-9/) |
| `spark-submit: command not found` | — | Spark isn't on your `PATH`. Use the full path to `bin/spark-submit` in your Spark install | [9](/training-notes-site/notes/training-9/) |
| `ClassNotFoundException: SalesAnalysis` | — | `--class` must match the object name exactly, and the JAR path must point to the file you just built | [9](/training-notes-site/notes/training-9/) |
| `ClassNotFoundException: org.postgresql.Driver` / `No suitable driver` | — | You forgot `--packages` or `--jars`. A thin JAR doesn't include the driver | [9](/training-notes-site/notes/training-9/) |
| `NoSuchMethodError` mentioning `scala.` | — | Your JAR is Scala 2.13 but your Spark install was built for a different Scala version. `spark-submit --version` shows which Scala it uses; the two must match (rebuild with a matching `scalaVersion`, or use a Spark download built for 2.13) | [9](/training-notes-site/notes/training-9/) |

## Scala, sbt and IntelliJ

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| `not found: value rootProject` | — | Your sbt is older than the syntax in your `build.sbt`. Either add `project/build.properties` with a current `sbt.version`, or use the form from the Training 9 notes: `lazy val root = (project in file("."))` | [9](/training-notes-site/notes/training-9/), [10](/training-notes-site/notes/training-10/) |
| IntelliJ: "Code insight is unavailable because the sbt project is not loaded" | — | Training 9 fix order: Project SDK = JDK 17, sbt JRE = Project JDK, "Load sbt project", then sbt tool window → Reload All sbt Projects | [9](/training-notes-site/notes/training-9/), [10](/training-notes-site/notes/training-10/) |
| No `project/build.properties` in the folder | — | It isn't required, but sbt uses it to pick its own version. If imports act up, add one | [10](/training-notes-site/notes/training-10/) |
| `Multiple main classes detected` | — | Not an error. Pick a number, or use `runMain <ObjectName>` | [10](/training-notes-site/notes/training-10/) |
| `No main class detected` | — | The file is outside `src/main/scala/`, or `main`'s signature is wrong. Must be `def main(args: Array[String]): Unit` | [10](/training-notes-site/notes/training-10/) |
| `class PostgresSource needs to be abstract, since method readData ... is not defined` | — | A class that extends the trait must implement every abstract method, or be marked `abstract` | [10](/training-notes-site/notes/training-10/) |
| `trait DataSource is abstract; cannot be instantiated` | — | You wrote `new DataSource()`. Instantiate a concrete class | [10](/training-notes-site/notes/training-10/) |
| `type mismatch; found: String("bob@...") required: Option[String]` | — | Wrap it: `Some("bob@...")` | [10](/training-notes-site/notes/training-10/) |
| `match may not be exhaustive. It would fail on: None` | — | You left out `case None` | [10](/training-notes-site/notes/training-10/) |
| `Pipeline` resolves but `create` is not a member | — | The `object` is misspelled, or it's nested inside another object, so it isn't the companion | [10](/training-notes-site/notes/training-10/) |
| Companion can't see a `private` member | — | The class and the object must be in the same file | [10](/training-notes-site/notes/training-10/) |
| `missing argument list for method calculateTaxCurried` | — | Keep the `: Double => Double` annotation, or add a trailing `_` | [10](/training-notes-site/notes/training-10/) |
| `type mismatch; found: Double => Double, required: Double` | — | You called it with only one argument list where a number was expected. Supply both: `calculateTaxCurried(0.0825)(100.0)` | [10](/training-notes-site/notes/training-10/) |
| Dependency for `spark-sql_2.13` can't be resolved | — | Check the Spark version string in `build.sbt` exists on Maven Central for Scala 2.13 | [9](/training-notes-site/notes/training-9/) |
| Weird compile errors on a JDK newer than 17 | — | Switch both JDK settings back to 17 | [9](/training-notes-site/notes/training-9/) |

## Hive and metastore

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| `TTransportException ... Broken pipe` on the first `saveAsTable` | Nothing listening on 9083 (metastore process not started) | Start the metastore, then re-check with `nc` | [11](/training-notes-site/notes/training-11/) |
| `NoSuchDatabaseException: SCHEMA_NOT_FOUND` | Database not created in the metastore | Your job's `CREATE DATABASE IF NOT EXISTS` lines handle this; make sure they're still at the top | [11](/training-notes-site/notes/training-11/) |
| `MetaException(... is not a directory or unable to create one)` | Warehouse path means different things to Spark and the container | The bind mount path and `spark.sql.warehouse.dir` must be identical strings | [11](/training-notes-site/notes/training-11/) |
| HiveServer2 won't start, "already running" | Stale pidfile baked into a committed image | Remove the stale pidfile, keep `--entrypoint /entrypoint.sh` | [11](/training-notes-site/notes/training-11/) |
| `Invalid method name` (Thrift) | Metastore client/server version mismatch | See the class-vs-docs table at the end | [11](/training-notes-site/notes/training-11/) |
| `New sales: 0` right after generating | Job read a different Postgres DB, or generate failed silently | Check `generate_sales.py` printed "Successfully inserted"; both point at `warehouse_practice` | [11](/training-notes-site/notes/training-11/) |
| Count went up by 2,800+ | Silver write is `append` without the anti join, or the anti join key is wrong | Check the join is on `Seq("sale_id")` with `"left_anti"` | [11](/training-notes-site/notes/training-11/) |
| Count went **down** | An `overwrite` of `silver.sales` crept back in | Search the file for `saveAsTable("silver.sales")`; only the append should remain | [11](/training-notes-site/notes/training-11/) |

## Kafka, Flink and streaming

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| `Failed to find data source: kafka` | Spark-Kafka connector JAR not on Spark's classpath | `spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_<scala>:<spark> consumer.py` | [12](/training-notes-site/notes/training-12/), [13](/training-notes-site/notes/training-13/), [14](/training-notes-site/notes/training-14/) |
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
| `Conflict. The container name "/kafka" is already in use` | The container from class still exists (maybe stopped) | `docker ps -a`, then `docker start kafka` (or `docker rm kafka` and run again) | [12](/training-notes-site/notes/training-12/) |
| `nc` says Connection refused | Port not published | Recreate with `-p 9092:9092` | [12](/training-notes-site/notes/training-12/) |
| Producer later says `NoBrokersAvailable` | Kafka isn't up yet or the port isn't reachable | Check the container is running, the port is published and the broker has started | [12](/training-notes-site/notes/training-12/) |
| `NoSuchMethodError: scala.Predef$...` or similar class errors | Connector built for a different Spark/Scala version | The connector version must match **your Spark**, not the broker. Run `spark-submit --version`. Use the connector version that matches what it prints, or run in the Spark 3.5.1 setup from class | [12](/training-notes-site/notes/training-12/) |
| `NoBrokersAvailable` (producer) | Kafka not reachable | Check the broker is up and the port is published | [12](/training-notes-site/notes/training-12/), [14](/training-notes-site/notes/training-14/) |
| Batches appear but always empty | Normal for short jokes, or the field is missing | Check with the console consumer that `joke_length` is in the raw JSON | [12](/training-notes-site/notes/training-12/) |
| `joke_length` column is all `null` | Name mismatch between producer key and schema field | Both must be exactly `joke_length` | [12](/training-notes-site/notes/training-12/) |
| `bind: address already in use` on 9092 or 27017 | Something else holds the port (often a second Kafka) | `lsof -nP -iTCP:9092 -sTCP:LISTEN` to find it before killing anything | [13](/training-notes-site/notes/training-13/) |
| `Failed to find data source: kafka` / `...: mongodb` | Connector JAR missing | Keep both packages in `spark.jars.packages`, and in only one place (code **or** `--packages`, not both) | [13](/training-notes-site/notes/training-13/) |
| `MongoTimeoutException ... Connection refused` | MongoDB not up, or wrong URI | `docker ps`, `docker logs mongodb`; the Spark error rarely says the real cause | [13](/training-notes-site/notes/training-13/) |
| Restart picks up nothing new / reprocesses everything | Checkpoint kept vs deleted | `checkpoints/readings` decides the resume point. Delete it only to deliberately replay | [13](/training-notes-site/notes/training-13/) |
| Documents have nulls everywhere | Schema names/types don't match the JSON | Compare with a message from the console consumer | [13](/training-notes-site/notes/training-13/) |
| `Producer error: ... Connection refused` | API not running | Start terminal 1 first | [14](/training-notes-site/notes/training-14/) |
| `No readable meta.properties files found` when starting Kafka | KRaft storage was wiped (it lived under `/tmp`) | `kafka-storage.sh random-uuid` → `format --standalone` → start → recreate `market_ticks` (reformatting deletes all topics) | [14](/training-notes-site/notes/training-14/) |
| `NoSuchMethodError` / `ClassNotFoundException` mentioning Scala | Connector's `_2.12`/`_2.13` suffix doesn't match your Spark build | pip PySpark 3.5 is Scala 2.12, so `_2.12`. the class machine used `_2.13:3.5.1` because his Spark build was 2.13. Match the engine, not the broker | [14](/training-notes-site/notes/training-14/) |
| `Append output mode not supported when there are streaming aggregations ... without watermark` | Aggregation written in `append` mode | Use `complete`/`update`, or add a watermark (a windowed query has one) | [14](/training-notes-site/notes/training-14/) |
| `Sorting is not supported on streaming DataFrames...` | `orderBy` outside `complete` mode | Remove the sort in `update` mode | [14](/training-notes-site/notes/training-14/) |
| Table prints but every column is `null` | Schema names or types don't match the JSON | Compare with one raw message; your `filter(symbol isNotNull)` hides these rows, so a silent empty table can mean this too | [14](/training-notes-site/notes/training-14/) |
| Folder exists but no `part-` files | Job stopped before the first trigger, or no ticks arrived | Check the producer; wait past 10 s | [14](/training-notes-site/notes/training-14/) |
| Hour folder doesn't match your clock | Session time zone is UTC on purpose | Expected. 21 UTC = 17 EDT | [14](/training-notes-site/notes/training-14/) |
| Restart reprocesses or skips data | Checkpoint deleted, or `startingOffsets` changed | One checkpoint per query; never share or casually delete it | [14](/training-notes-site/notes/training-14/) |
| `AnalysisException ... checkpoint` after you change the query | Old checkpoint doesn't match new logic | Use a new `CHECKPOINT_DIR` | [14](/training-notes-site/notes/training-14/) |

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
| `BucketAlreadyExists: The requested bucket name is not available. The bucket namespace is shared by all users of the system.` | Bucket names are **globally unique across all AWS accounts**, and someone already owns `citi-bike-nyc` | Pick a more specific name. Evan switched to `citi-bike-nyc-pipeline`. Put **your name** in yours | [19](/training-notes-site/notes/training-19/) |
| `IllegalLocationConstraintException: The unspecified location constraint is incompatible for the region specific endpoint this request was sent to.` | **Every region except `us-east-1`** needs `--create-bucket-configuration LocationConstraint=<region>` | Add it. ChatGPT on screen: "S3 has an odd special case: `us-east-1` doesn't require LocationConstraint, but other regions do." | [19](/training-notes-site/notes/training-19/) |
| Glue write failed, `TASK_WRITE_FAILED` | — | The Glue role lacked `s3:PutObject` on the new Silver prefix. Confirmed with `simulate-principal-policy` (`implicitDeny` → `allowed`) | [24](/training-notes-site/notes/training-24/) |
| "Missing required arguments" | — | The console Run button doesn't pass parameters. Start the job from the CLI with `--arguments` | [24](/training-notes-site/notes/training-24/) |
| Job run not visible in the console | — | Check the region, open the job's Runs tab, use View details | [24](/training-notes-site/notes/training-24/) |
| "Execution role must allow EventBridge Scheduler to assume the role" | He picked the **Lambda's** role, which trusts `lambda.amazonaws.com`, not the scheduler | New role `CitiBikeSchedulerRole` trusting `scheduler.amazonaws.com` | [19](/training-notes-site/notes/training-19/) |
| Schedule saved, but no new files arrived | The new role had a trust policy but **no permissions policy** | Inline policy allowing `lambda:InvokeFunction` on the function | [19](/training-notes-site/notes/training-19/) |
| `AWS was not able to validate the provided credentials` (CLI) | Authentication: no or wrong profile | Pass your `--profile` explicitly (hit in class) | [25](/training-notes-site/notes/training-25/) |
| `Glue.ConcurrentRunsExceededException` | — | Max concurrency 1 (good). Another run is going; don't start overlapping executions | [26](/training-notes-site/notes/training-26/) |
| `NoCredentialsError` / `The config profile (x) could not be found` | No CLI profile on this machine, or the wrong name | Set up the profile with `aws configure --profile <name>` (keys never in code) | [26](/training-notes-site/notes/training-26/) |
| `UnrecognizedClientException` / "not able to validate the provided credentials" | Authentication, not permission (Training 25) | Pass the right `--profile` / `AWS_PROFILE` | [26](/training-notes-site/notes/training-26/) |

## Terraform and Step Functions

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| "No state file was found" | — | `terraform import` the existing resources | [24](/training-notes-site/notes/training-24/) |
| Plan wanted "7 to add" | — | Wrong folder, no state. Go back to the folder with the `.tfstate` | [24](/training-notes-site/notes/training-24/) |
| State machine rejected (`Sql.$`) | — | SQL moved into the coordinator Lambda | [24](/training-notes-site/notes/training-24/) |
| Failed after Glue had succeeded | — | **Redrive from failure**, not a new run | [24](/training-notes-site/notes/training-24/) |
| `Error: Missing newline after argument` / `Invalid single-argument block definition` | One-line block with two arguments | Make it multi-line; run `terraform fmt` | [26](/training-notes-site/notes/training-26/) |
| `Reference to undeclared resource` | e.g. `aws_lambda_function.coordinator` used but not defined yet | Add the resource, or temporarily point at a variable | [26](/training-notes-site/notes/training-26/) |
| `Unsupported argument` | Wrong argument name for that resource (often from an AI-generated example) | Check the provider docs page for that resource | [26](/training-notes-site/notes/training-26/) |
| `Invalid template interpolation value` / `templatefile` errors | The ASL JSON contains a literal `${` or a variable name not passed in | Only use `${coordinator_arn}`-style placeholders you pass in the map | [26](/training-notes-site/notes/training-26/) |
| `Error: No valid credential sources found` during `validate` | Shouldn't happen on `validate`; usually you ran `plan` | Stop. `plan` waits for AWS | [26](/training-notes-site/notes/training-26/) |
| `Failed to query available provider packages` | No internet / registry blocked | Retry on another network | [26](/training-notes-site/notes/training-26/) |
| `validate` passes but sees "no configuration files" | Wrong folder (Training 24 lesson: Terraform reads only the current folder) | `cd` into `terraform/` | [26](/training-notes-site/notes/training-26/) |
| `SCHEMA_VALIDATION_FAILED` … `The field "X.$" ...` | — | A key ending in `.$` must have a JSONPath string value starting with `$` | [26](/training-notes-site/notes/training-26/) |
| `States.Runtime` … `JSONPath '$.prepare.batch.batch_id' could not be found` | — | Check `ResultSelector` / `ResultPath`. Open the execution's step input/output in the console | [26](/training-notes-site/notes/training-26/) |
| Glue state "succeeds" instantly, COPY finds 0 files | — | You used `startJobRun` without `.sync` | [26](/training-notes-site/notes/training-26/) |
| `AccessDeniedException` on `glue:StartJobRun` | — | Step Functions role policy: job ARN or action missing | [26](/training-notes-site/notes/training-26/) |

## Redshift and SQL warehouses

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| Syntax | — | QUALIFY, or a CTE | [25](/training-notes-site/notes/training-25/) |
| `MERGE INTO` syntax errors over and over | — | Replaced with `INSERT … WHERE NOT EXISTS` | [24](/training-notes-site/notes/training-24/) |
| Query editor ran only part of the script | — | Something was highlighted. Deselect everything | [24](/training-notes-site/notes/training-24/) |
| Told to `CALL` before `CREATE PROCEDURE` | — | Create first | [24](/training-notes-site/notes/training-24/) |
| Window skipped boundary files | — | `start < ts < end` → `start <= ts < end` | [24](/training-notes-site/notes/training-24/) |
| `permission denied for relation …` (×2) | — | Redshift `GRANT`s to `IAMR:<role>` | [24](/training-notes-site/notes/training-24/), [25](/training-notes-site/notes/training-25/) |
| `syntax error at or near "QUALIFY"` | You pasted a Redshift version | Postgres has no QUALIFY. Use your subquery version | [22](/training-notes-site/notes/training-22/) |
| `function round(double precision, integer) does not exist` | `ROUND` on a float in Postgres | If it shows up, cast: `ROUND(AVG(x)::numeric, 2)` | [22](/training-notes-site/notes/training-22/) |
| Query editor shows no `gold` schema | Connected to the wrong database | Switch the database in the editor's dropdown | [25](/training-notes-site/notes/training-25/) |
| `column "s.station_name" must appear in the GROUP BY clause` | — | Every non-aggregated column in `SELECT` goes in `GROUP BY` | [25](/training-notes-site/notes/training-25/) |
| `AVG` returns a whole number | — | `bikes_available` is an integer type, so Redshift's `AVG` of integers can truncate. Cast inside: `AVG(f.bikes_available::DECIMAL(10,2))` | [25](/training-notes-site/notes/training-25/) |
| `Window function is not allowed in where clause` | — | The exact error from class. Move the condition to `QUALIFY`, or use the CTE | [25](/training-notes-site/notes/training-25/) |
| `column "snapshot_timestamp" does not exist` | — | The column name differs between versions of the table (e.g. `snapshot_ts`). Check with `\d` or the schema browser | [25](/training-notes-site/notes/training-25/) |
| More than one row per station | — | `PARTITION BY` is missing or includes a second column (e.g. `snapshot_ts`) | [25](/training-notes-site/notes/training-25/) |
| Oldest row per station instead of newest | — | `ORDER BY … DESC` was left out | [25](/training-notes-site/notes/training-25/) |
| `pct_time_empty` is always 0 or 100 | — | Integer division. Keep the `100.0 *` at the front | [25](/training-notes-site/notes/training-25/) |
| `CASE WHEN f.is_empty` errors | — | If `is_empty` isn't boolean in the table, Then use `CASE WHEN f.is_empty = 1` | [25](/training-notes-site/notes/training-25/) |
| `HAVING COUNT(*) >= 3` filters everything | — | If a station missed a snapshot it drops out. Fine for now; lower it or remove it if the result is empty | [25](/training-notes-site/notes/training-25/) |
| `AccessDeniedException` … `redshift-data:ExecuteStatement` | IAM layer | Ask an admin to grant that exact action (the class accounts have limited permissions) | [26](/training-notes-site/notes/training-26/) |
| `permission denied for relation fact_station_snapshot` | Redshift GRANT layer | `GRANT USAGE ON SCHEMA gold` + `GRANT SELECT` to your user (Training 24) | [26](/training-notes-site/notes/training-26/) |

## Text-to-SQL and Bedrock

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| Wrong grain | — | Grain rules in the system prompt | [25](/training-notes-site/notes/training-25/) |
| Hallucinated column | — | Schema validation + refusal (`INSUFFICIENT_SCHEMA`) | [25](/training-notes-site/notes/training-25/) |
| Missing data | — | Add lat/long to the data model (Silver → Gold) | [25](/training-notes-site/notes/training-25/) |
| `AccessDeniedException` … `bedrock:InvokeModel` | — | The student policy needs `bedrock:InvokeModel` (granted in Training 25). Send the exact error to the admin | [26](/training-notes-site/notes/training-26/) |
| `ValidationException` … "on-demand throughput isn't supported" | — | Use the cross-region **inference profile** ID (prefixed `us.`) for the Nova model instead of the bare model ID | [26](/training-notes-site/notes/training-26/) |
| `ValidationException: The provided model identifier is invalid` | — | Typo, or model not available in `us-east-2`; list them with `aws bedrock list-foundation-models` | [26](/training-notes-site/notes/training-26/) |
| Generated SQL uses a column you don't have | — | The model invented a column (Training 25's `ds.latitude` case). Give the prompt the real schema, tell it to answer `INSUFFICIENT_SCHEMA` when a column is missing, and validate the SQL before running it | [26](/training-notes-site/notes/training-26/) |

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
| `location 'eastus2' is not accepting new SQL Database server creations` | Region out of capacity | Pick another region (Brazil South worked) | [31](/training-notes-site/notes/training-31/) |
| `Content of directory on path '.../<container>/<path>/*.parquet' cannot be listed` | Pasted template path with placeholders | Copy the real URL from the storage browser | [31](/training-notes-site/notes/training-31/) |
| `Incorrect syntax near 'FORMAT'` | Serverless SQL has no `FORMAT='JSON'` | `FORMAT='CSV'` + `FIELDTERMINATOR/FIELDQUOTE='0x0b'` + `WITH (jsonContent ...)`, or convert to Parquet | [31](/training-notes-site/notes/training-31/) |
| `Stored procedures cannot be permanently stored in master database` | Working in `master` | `CREATE DATABASE CitiBikeAnalytics; USE CitiBikeAnalytics;` | [31](/training-notes-site/notes/training-31/) |
| `Could not find stored procedure 'pct_time_empty'` / `'MAX'` | Only highlighted text ran | Deselect, or Ctrl+A, then Run | [31](/training-notes-site/notes/training-31/) |
| `... failed because 'v_station_status_clean' is a view object` | Only highlighted text ran | Deselect, or Ctrl+A, then Run | [31](/training-notes-site/notes/training-31/) |
| `Invalid object name 'dbo.v_station_status_clean'` | Dependent view created before its base view | Create views in dependency order | [31](/training-notes-site/notes/training-31/) |
| Every station 100% empty **and** 100% full | 55 inactive stations (0 bikes and 0 docks, flags = 0) | Classify `INACTIVE`, then filter to active stations | [31](/training-notes-site/notes/training-31/) |
| Spark cell "hangs" for minutes | Provisioned Spark pool cold start (~3–4 min) | Expected; later cells are fast | [31](/training-notes-site/notes/training-31/) |
| Power BI `Invalid credentials` | Probably the wrong server name | Use `<workspace>-ondemand.sql.azuresynapse.net` | [31](/training-notes-site/notes/training-31/) |

## Azure Data Factory

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| ADLS linked service test: 403 | Factory managed identity had no data-plane role | Storage Blob Data Contributor on the storage account, then wait for propagation | [28](/training-notes-site/notes/training-28/) |
| S3 linked service test: "Credential is incorrect or does not have permission" | The inline policy lacked a list permission | Edited the IAM policy, test passed | [28](/training-notes-site/notes/training-28/) |
| ADLS linked service not in the sink dropdown | The first linked service was never saved/published | Recreated it, then clicked **Publish all** ("This resource has not been published by your data factory") | [28](/training-notes-site/notes/training-28/) |
| Copy failed after 15 s: "the operation is on a file citibike" | `citibike` was in the file-name field, so ADF treated it as a file | Put `bronze/citibike` in the **directory** field, file name blank | [28](/training-notes-site/notes/training-28/) |
| Copy succeeded but the sink path was wrong | The storage-account name was typed as a folder | Sink path = container `bronze` only. A **container** is the equivalent of an S3 bucket | [28](/training-notes-site/notes/training-28/) |
| "Credential is incorrect or does not have permission" | The reader policy can't list *your* bucket | Your bucket ARN isn't in that user's inline policy. and `arn:aws:s3:::<your-bucket>/*` (GetObject) | [28](/training-notes-site/notes/training-28/) |
| 403 on `GetObject` during the copy | The policy is missing the `/*` object ARN | Same fix, the `/*` half | [28](/training-notes-site/notes/training-28/) |
| Fails after ~15 s: "the operation is on a file citibike" | `citibike` typed in the file-name box | Move it to the directory box | [28](/training-notes-site/notes/training-28/) |
| Succeeds but files land in a weird nested path | Storage account name typed as a folder | Sink path = container `bronze` only | [28](/training-notes-site/notes/training-28/) |
| Your ADLS linked service missing from the sink dropdown | Not published | Publish all, refresh | [28](/training-notes-site/notes/training-28/) |

## Databricks, Delta and Auto Loader

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| Silver: "Failed to read dataset `...default.bronze_station_raw` … could not be resolved" | Downstream symptom: **Bronze failed first** | Find the *first* traceback (the Bronze one) | [29](/training-notes-site/notes/training-29/) |
| Bronze: Auto Loader can't find any JSON files | Wrong `source_path`: files were under the landing folder, not `station_status` | Correct the path | [29](/training-notes-site/notes/training-29/) |
| "Can't extract value from data: need a complex type" | Auto Loader **inferred** `data` as a string, so `.stations` can't be exploded | Pass an explicit `StructType` schema with `.schema(station_schema)` | [29](/training-notes-site/notes/training-29/) |
| `TABLE_OR_VIEW_NOT_FOUND` | — | Typo in the three-part name, or Gold cell never ran in this catalog. `SHOW TABLES IN <your-catalog>.gold;` | [28](/training-notes-site/notes/training-28/), [30](/training-notes-site/notes/training-30/) |
| Syntax error near `DESCRIBE` / second statement | — | One statement per line, each ending in `;` (the class hit this) | [28](/training-notes-site/notes/training-28/) |
| Cell runs as Python | — | The `%sql` must be the very first line of the cell | [28](/training-notes-site/notes/training-28/) |
| `Cannot time travel Delta table to version X` / version doesn't exist | — | Check `DESCRIBE HISTORY` for the real version numbers (they start at 0) | [30](/training-notes-site/notes/training-30/) |
| Error about files missing after VACUUM | — | The old version's files were vacuumed; that version can't be read or restored | [30](/training-notes-site/notes/training-30/) |

## MLflow

| Error / symptom | Cause | Fix | Day |
|---|---|---|---|
| Run "not in Experiments" | — | `set_experiment()` with a path creates a **workspace experiment** at that path. Find it by clicking the "View run / View experiment" link MLflow prints under the cell, in the left sidebar under **Experiments** (Machine Learning / AI section), or in the Workspace browser at that path. The notebook's **Experiment** icon in the right panel shows only the notebook's default experiment, not one set by path | [30](/training-notes-site/notes/training-30/) |
| "Inferred schema contains integer columns" | — | MLflow warns that integer columns can't hold missing values, so a future input with a null would fail schema checks. Fix: cast integer feature columns to `float64` before `infer_signature` (it's only a warning) | [30](/training-notes-site/notes/training-30/) |
| Run not in the notebook's Experiment side panel | — | Expected: that panel shows the notebook's default experiment. Use the sidebar **Experiments** page or the link under the cell | [30](/training-notes-site/notes/training-30/) |
| `RESOURCE_DOES_NOT_EXIST` / permission error on the experiment path | — | Use a path under your own `/Users/<your-user>/` folder, not someone else's or the workspace root | [30](/training-notes-site/notes/training-30/) |
| `MlflowException: Changing param values is not allowed` | — | You logged the same param name twice in one run with a different value. Start a new run | [30](/training-notes-site/notes/training-30/) |
| Nothing logged | — | The log calls must be **inside** the `with mlflow.start_run():` block | [30](/training-notes-site/notes/training-30/) |

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
