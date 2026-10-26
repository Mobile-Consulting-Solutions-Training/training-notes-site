---
title: Command Cheat Sheets
description: The commands used across the course, organized by task - Linux, Git, Docker, Postgres, Hadoop/Hive, Spark, Kafka, AWS CLI, Terraform, Azure CLI, Databricks and dbt.
sidebar:
  order: 4
---

The commands from class, organized by what you're trying to do. Replace anything in `<angle brackets>` with your own value. The day links go to the notes where each tool was taught.

## Linux and the shell

Covered in Training [0](/training-notes-site/notes/training-0/), [1](/training-notes-site/notes/training-1/).

| Task | Command |
|---|---|
| Where am I / what's here (with hidden files, sizes) | `pwd` · `ls -lah` |
| Move around | `cd <dir>` · `cd ..` · `cd ~` · `cd -` (previous folder) |
| Make, copy, move, delete | `mkdir -p a/b/c` · `cp -r <src> <dst>` · `mv <src> <dst>` · `rm -r <dir>` |
| Read a file | `cat <file>` · `less <file>` · `head -n 20 <file>` · `tail -n 50 <file>` |
| Follow a growing log | `tail -f <file>` |
| Write / append to a file | `echo "text" > file.txt` · `echo "more" >> file.txt` |
| Search inside files | `grep -i "error" app.log` · `grep -rn "TODO" .` · `grep -E "ERROR\|WARN" app.log` |
| Pull just the matches | `grep -oE "customer_id=[0-9]+" file` |
| Pick columns / sum a column | `awk -F, '{print $1, $3}' data.csv` · `awk -F, '{s+=$3} END {print s}' data.csv` |
| Find and replace | `sed 's/old/new/g' file` (print) · `sed -i 's/old/new/g' file` (in place; macOS: `sed -i '' ...`) |
| Count, sort, de-duplicate | `wc -l file` · `sort file \| uniq -c \| sort -rn` |
| Find files | `find . -name "*.csv"` · `find . -size +100M` |
| Permissions | `chmod 600 file` (owner read/write) · `chmod u+x script.sh` · `chown <user>:<group> file` |
| Run as another user / root | `sudo <cmd>` · `su - <user>` |
| Users and groups | `sudo useradd -m <user>` · `sudo usermod -aG <group> <user>` · `id <user>` |
| Processes | `ps aux \| grep <name>` · `top` / `htop` · `kill <pid>` · `kill -9 <pid>` |
| Services and their logs (systemd) | `systemctl status <svc>` · `sudo systemctl restart <svc>` · `journalctl -u <svc> -f` |
| Disk and memory | `df -h` · `du -sh *` · `free -h` |
| What's using a port | `lsof -nP -iTCP:<port> -sTCP:LISTEN` · `ss -ltnp \| grep :<port>` |
| Is a port open | `nc -vz localhost <port>` |
| Environment variables | `export NAME=value` · `echo $NAME` · `env \| grep NAME` (gone when the terminal closes) |
| Archives | `tar -czf out.tar.gz <dir>` · `tar -xzf file.tar.gz` |
| Remote machines | `ssh <user>@<host>` · `scp file <user>@<host>:/path/` |
| Schedule a job | `crontab -e` then `*/5 * * * * /path/script.sh` (every 5 minutes) |
| Call an API | `curl -s https://<url> \| jq .` |

## Git

Covered in Training [3](/training-notes-site/notes/training-3/).

| Task | Command |
|---|---|
| Start or copy a repo | `git init` · `git clone <url>` |
| What changed | `git status` · `git diff` · `git diff --staged` · `git log --oneline -10` |
| Save work | `git add <file>` (or `git add -A`) · `git commit -m "message"` |
| Share work | `git push` · `git push -u origin <branch>` (first push of a branch) · `git pull` |
| Branches | `git switch -c <branch>` (create + switch) · `git switch <branch>` · `git branch -d <branch>` |
| Combine branches | `git merge <branch>` · `git rebase main` |
| Undo safely | `git restore <file>` (discard edits) · `git restore --staged <file>` (unstage) · `git revert <commit>` (new commit that undoes one) |
| Stop tracking a committed file | `git rm -r --cached <path>` then add it to `.gitignore` |
| Put work aside | `git stash` · `git stash pop` |
| GitHub Actions location | Workflows only run from `.github/workflows/*.yml` |

## Docker

Covered in Training [0](/training-notes-site/notes/training-0/), [3](/training-notes-site/notes/training-3/), [11](/training-notes-site/notes/training-11/), [13](/training-notes-site/notes/training-13/).

| Task | Command |
|---|---|
| Check it works | `docker --version` · `docker run hello-world` |
| Run a container (named, background, port, env) | `docker run -d --name <name> -p <host>:<container> -e KEY=value <image>` |
| Interactive shell in a new container | `docker run -it ubuntu bash` |
| Shell in a running container | `docker exec -it <name> bash` |
| List containers (running / all) | `docker ps` · `docker ps -a` |
| Logs | `docker logs <name>` · `docker logs -f <name>` |
| Start, stop, remove | `docker start <name>` · `docker stop <name>` · `docker rm <name>` · `docker rm -f <name>` |
| Which ports are published | `docker port <name>` |
| Images | `docker images` · `docker pull <image>:<tag>` · `docker rmi <image>` |
| Build and tag (from the repo root) | `docker build -t <name>:<tag> .` |
| Mount a folder | `docker run -v $(pwd)/data:/data <image>` |
| Compose stacks | `docker compose up -d` · `docker compose ps` · `docker compose logs -f` · `docker compose down` |
| Free space | `docker system df` · `docker system prune` |

## Python environments

Covered in Training [2](/training-notes-site/notes/training-2/), [3](/training-notes-site/notes/training-3/).

| Task | Command |
|---|---|
| Create and use a virtual environment | `python3 -m venv .venv` · `source .venv/bin/activate` · `deactivate` |
| Install packages / save the list | `pip install <pkg>` · `pip install -r requirements.txt` · `pip freeze > requirements.txt` |
| Make sure pip matches the Python you run | `python -m pip install <pkg>` · `python -m pytest` |
| Run tests | `pytest` · `pytest -k <name> -v` |
| Run a web app | `uvicorn main:app --reload` · `streamlit run app.py` (not `python app.py`) |

## PostgreSQL (psql)

Covered in Training [4](/training-notes-site/notes/training-4/), [5](/training-notes-site/notes/training-5/).

| Task | Command |
|---|---|
| Connect | `psql -h localhost -p 5432 -U <user> -d <db>` · in Docker: `docker exec -it <container> psql -U <user> -d <db>` |
| List databases / switch | `\l` · `\c <db>` |
| List schemas, tables, describe a table | `\dn` · `\dt <schema>.*` · `\d <table>` |
| Indexes on a table | `\di` · `\d <table>` |
| Run a SQL file | `\i file.sql` · `psql -d <db> -f file.sql` |
| Time and plan a query | `\timing on` · `EXPLAIN ANALYZE <query>;` |
| Load / export CSV | `\copy <table> FROM 'file.csv' CSV HEADER` · `\copy (<query>) TO 'out.csv' CSV HEADER` |
| Quit | `\q` (a `-#` prompt means you're missing a `;`) |

## Hadoop, HDFS and Hive

Covered in Training [6](/training-notes-site/notes/training-6/), [8](/training-notes-site/notes/training-8/), [11](/training-notes-site/notes/training-11/).

| Task | Command |
|---|---|
| List / make folders in HDFS | `hdfs dfs -ls /` · `hdfs dfs -mkdir -p /data/raw` |
| Upload / download | `hdfs dfs -put file.csv /data/raw/` · `hdfs dfs -get /data/raw/file.csv .` |
| Read, size, delete | `hdfs dfs -cat <path> \| head` · `hdfs dfs -du -h <path>` · `hdfs dfs -rm -r <path>` |
| Cluster health | `hdfs dfsadmin -report` · `hdfs fsck / -files -blocks` |
| Connect to HiveServer2 | `beeline -u jdbc:hive2://localhost:10000` |
| Look around | `SHOW DATABASES;` · `SHOW TABLES;` · `DESCRIBE FORMATTED <table>;` · `SHOW PARTITIONS <table>;` |
| Is the metastore up | `nc -vz localhost 9083` |

## Spark

Covered in Training [7](/training-notes-site/notes/training-7/), [8](/training-notes-site/notes/training-8/), [9](/training-notes-site/notes/training-9/), [10](/training-notes-site/notes/training-10/).

| Task | Command / code |
|---|---|
| Submit a job | `spark-submit --master <local[*]\|yarn> --deploy-mode <client\|cluster> app.py` |
| Resources | `--driver-memory 4g --executor-memory 8g --executor-cores 4 --num-executors 10` |
| Add libraries (connectors, JDBC drivers) | `--packages org.apache.spark:spark-sql-kafka-0-10_2.12:<spark-version>` · `--jars driver.jar` |
| Config | `--conf spark.sql.shuffle.partitions=200 --conf spark.sql.adaptive.enabled=true` |
| Scala JAR | `spark-submit --class <MainObject> target/scala-2.13/<app>.jar` |
| Which Spark / Scala version | `spark-submit --version` (connector suffix `_2.12` / `_2.13` must match) |
| Start a session (outside Databricks) | `spark = SparkSession.builder.appName("app").getOrCreate()` |
| Read / write | `spark.read.option("header", True).csv(path)` · `df.write.mode("overwrite").partitionBy("dt").parquet(path)` |
| Inspect | `df.printSchema()` · `df.show(5, truncate=False)` · `df.explain(True)` · `df.rdd.getNumPartitions()` |
| Partitions | `df.repartition(200, "key")` (full shuffle) · `df.coalesce(10)` (fewer files, no shuffle) |
| Broadcast a small table | `big.join(F.broadcast(small), "key")` |
| Cache | `df.cache()` · `df.persist(StorageLevel.MEMORY_AND_DISK)` · `df.unpersist()` |
| Latest row per key | `w = Window.partitionBy("id").orderBy(F.col("ts").desc())` → `df.withColumn("rn", F.row_number().over(w)).filter("rn = 1")` |
| Spark UI | `http://localhost:4040` while a job runs |

## Scala and sbt

Covered in Training [9](/training-notes-site/notes/training-9/), [10](/training-notes-site/notes/training-10/).

| Task | Command |
|---|---|
| Compile, run, test | `sbt compile` · `sbt run` · `sbt test` |
| Pick a main class | `sbt "runMain <ObjectName>"` |
| Build a JAR | `sbt package` (thin) · `sbt assembly` (fat JAR, needs the plugin) |
| Pin the sbt version | `project/build.properties` → `sbt.version=1.11.7` |
| Reload after editing `build.sbt` | `sbt reload` · IntelliJ: sbt tool window → Reload All sbt Projects |

## Kafka

Covered in Training [12](/training-notes-site/notes/training-12/), [13](/training-notes-site/notes/training-13/), [14](/training-notes-site/notes/training-14/).

| Task | Command |
|---|---|
| Format storage (KRaft, first start) | `kafka-storage.sh random-uuid` → `kafka-storage.sh format --standalone -t <id> -c config/server.properties` |
| Start the broker | `kafka-server-start.sh config/server.properties` |
| Create / list / describe topics | `kafka-topics.sh --bootstrap-server localhost:9092 --create --topic <t> --partitions 3 --replication-factor 1` · `--list` · `--describe --topic <t>` |
| Send test messages | `kafka-console-producer.sh --bootstrap-server localhost:9092 --topic <t>` |
| Read messages | `kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic <t> --from-beginning` |
| Consumer group lag | `kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group <g>` |
| In Docker | prefix with `docker exec -it kafka /opt/kafka/bin/` (and publish `-p 9092:9092`) |

## AWS CLI

Covered in Training [18](/training-notes-site/notes/training-18/), [19](/training-notes-site/notes/training-19/), [20](/training-notes-site/notes/training-20/), [21](/training-notes-site/notes/training-21/), [22](/training-notes-site/notes/training-22/), [24](/training-notes-site/notes/training-24/).

| Task | Command |
|---|---|
| Set up / check who you are | `aws configure --profile <name>` · `aws sts get-caller-identity --profile <name>` |
| Region | `aws configure set region us-east-2 --profile <name>` (or `--region us-east-2` per command) |
| S3: list, copy, sync, delete | `aws s3 ls s3://<bucket>/<prefix>/ --recursive` · `aws s3 cp file s3://<bucket>/<key>` · `aws s3 sync ./dir s3://<bucket>/dir/` · `aws s3 rm s3://<bucket>/<key>` |
| S3: make a bucket (outside us-east-1) | `aws s3api create-bucket --bucket <name> --region us-east-2 --create-bucket-configuration LocationConstraint=us-east-2` |
| Lambda: invoke, logs | `aws lambda invoke --function-name <fn> out.json` · `aws logs tail /aws/lambda/<fn> --follow` |
| Glue: run and check a job | `aws glue start-job-run --job-name <job> --arguments '{"--KEY":"value"}'` · `aws glue get-job-runs --job-name <job> --max-items 3` |
| Step Functions | `aws stepfunctions start-execution --state-machine-arn <arn> --input '{}'` · `aws stepfunctions describe-execution --execution-arn <arn>` |
| Kinesis | `aws kinesis describe-stream-summary --stream-name <s>` · `aws kinesis put-record --stream-name <s> --partition-key k --data <base64>` |
| Redshift Data API | `aws redshift-data execute-statement --workgroup-name <wg> --database dev --sql "SELECT 1"` → `get-statement-result --id <id>` |
| IAM: add an inline policy / test one | `aws iam put-role-policy --role-name <r> --policy-name <p> --policy-document file://policy.json` · `aws iam simulate-principal-policy --policy-source-arn <arn> --action-names s3:GetObject --resource-arns <arn>` |
| EventBridge Scheduler | `aws scheduler list-schedules` · `aws scheduler update-schedule ... --state DISABLED` |

## Terraform

Covered in Training [23](/training-notes-site/notes/training-23/), [24](/training-notes-site/notes/training-24/), [26](/training-notes-site/notes/training-26/).

| Task | Command |
|---|---|
| Set up a folder (downloads providers) | `terraform init` |
| Format and check | `terraform fmt` · `terraform validate` |
| Preview / apply / remove | `terraform plan` · `terraform apply` · `terraform destroy` |
| Adopt something that already exists | `terraform import <resource.address> <id>` |
| What Terraform manages | `terraform state list` · `terraform show` · `terraform output` |
| Remember | Terraform only reads `.tf` files in the **current folder**, and the `.tfstate` lives there too |

## Azure CLI

Covered in Training [27](/training-notes-site/notes/training-27/), [28](/training-notes-site/notes/training-28/), [31](/training-notes-site/notes/training-31/).

| Task | Command |
|---|---|
| Install | WSL/Linux: `curl -sL https://aka.ms/InstallAzureCLIDeb \| sudo bash` · Windows: `winget install -e --id Microsoft.AzureCLI` · Mac: `brew install azure-cli` |
| Sign in to the right tenant | `az login --tenant <tenant-id>` · `az login --use-device-code` |
| Which subscription / switch | `az account show -o table` · `az account list -o table` · `az account set --subscription <id>` |
| Resource group | `az group create -n <rg> -l eastus` · `az group show -n <rg> -o table` · `az group delete -n <rg>` |
| ADLS Gen2 account | `az storage account create -n <name> -g <rg> -l eastus --sku Standard_LRS --kind StorageV2 --hns true` |
| Container, folder, upload, list | `az storage fs create -n <container> --account-name <acct> --auth-mode login` · `az storage fs directory create -n raw -f <container> --account-name <acct> --auth-mode login` · `az storage fs file upload -s ./f.csv -p raw/f.csv -f <container> --account-name <acct> --auth-mode login` · `az storage fs file list -p raw -f <container> --account-name <acct> --auth-mode login -o table` |
| Grant a role | `az role assignment create --assignee <object-id> --role "Storage Blob Data Contributor" --scope <resource-id>` |
| Look up IDs | `az ad user show --id <email> --query id -o tsv` · `az storage account show -n <acct> -g <rg> --query id -o tsv` |
| Valid regions | `az account list-locations -o table` |

## Databricks

Covered in Training [28](/training-notes-site/notes/training-28/), [29](/training-notes-site/notes/training-29/), [30](/training-notes-site/notes/training-30/).

| Task | Command / code |
|---|---|
| Switch a cell's language | First line `%sql`, `%python`, `%md`, `%sh` |
| List files | `display(dbutils.fs.ls("/Volumes/<catalog>/<schema>/<volume>/"))` |
| Read JSON from a volume | `spark.read.option("multiLine", True).option("recursiveFileLookup", True).json(path)` |
| Write a Delta table | `df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("cat.schema.table")` |
| Table history / details | `DESCRIBE HISTORY t;` · `DESCRIBE DETAIL t;` |
| Time travel / roll back | `SELECT * FROM t VERSION AS OF 3;` · `... TIMESTAMP AS OF '2026-10-22 18:00';` · `RESTORE TABLE t TO VERSION AS OF 3;` |
| Upsert | `MERGE INTO t USING s ON t.id = s.id WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *;` |
| Maintenance | `OPTIMIZE t;` · `VACUUM t;` |
| Auto Loader | `spark.readStream.format("cloudFiles").option("cloudFiles.format", "json").load(path)` → `.writeStream.option("checkpointLocation", cp).trigger(availableNow=True).toTable("cat.schema.t")` |
| Permissions | `GRANT SELECT ON TABLE cat.schema.t TO \`group\`;` · `SHOW GRANTS ON TABLE cat.schema.t;` |
| Secrets | `dbutils.secrets.get(scope="<scope>", key="<key>")` |
| MLflow run | `with mlflow.start_run(): mlflow.log_param("depth", 5); mlflow.log_metric("mae", mae)` |

## dbt

Covered in Training [15](/training-notes-site/notes/training-15/), [17](/training-notes-site/notes/training-17/).

| Task | Command |
|---|---|
| Check the connection | `dbt debug` |
| Build models / one model and its parents | `dbt run` · `dbt run --select +<model>` |
| Test | `dbt test` · `dbt build` (run + test in order) |
| Seeds and snapshots | `dbt seed` · `dbt snapshot` (SCD Type 2) |
| Docs and lineage | `dbt docs generate` · `dbt docs serve` |
| See the compiled SQL | `dbt compile` then look in `target/compiled/` |
