---
title: "Code: Shell and Config"
description: "Shell commands, Dockerfiles, YAML, JSON policies and other config from the notes, grouped by training day."
sidebar:
  order: 10
---

Shell commands, Dockerfiles, YAML, JSON policies and other config from the notes, grouped by training day. Each example is titled with the question it answers in the notes; the day heading links to the full notes for context. Use the copy button on any block.
**45 examples.**


Code marked "from the class demo (not exact)" in the notes was rewritten from the demo, so check names and paths before running it.

## Training 1: Linux and Shell Scripting

[Open the Training 1 notes](/training-notes-site/notes/training-1/)

### How do I use regex inside a Bash script (=~, BASH_REMATCH)?

```bash
value="customer_12345"
if [[ $value =~ ^customer_[0-9]+$ ]]; then
    echo "Valid customer ID"
else
    echo "Invalid customer ID"
fi
```

```bash
value="customer_12345"
if [[ $value =~ customer_([0-9]+) ]]; then
    echo "Complete match: ${BASH_REMATCH[0]}"
    echo "Customer number: ${BASH_REMATCH[1]}"
fi
# Complete match: customer_12345
# Customer number: 12345
```

### What is a shell script, and how do I make one runnable?

```bash
#!/bin/bash
echo "Current user: $(whoami)"
echo "Current date: $(date)"
echo "Working directory: $(pwd)"
```

### What are the core shell scripting building blocks (variables, arguments, exit codes, if/for, functions, set -euo pipefail)?

```bash
#!/bin/bash
set -euo pipefail

INPUT_DIR="${1:?usage: $0 <input_dir>}"
LOG=/tmp/ingest.log
failed=0

log() { echo "$(date '+%F %T') $*" >> "$LOG"; }

for f in "$INPUT_DIR"/*.csv; do
    if rows=$(wc -l < "$f"); then
        log "OK $f rows=$rows"
    else
        log "FAIL $f"
        failed=1
    fi
done

exit "$failed"
```

### What is curl, and what is it used for?

```bash
curl https://example.com                    # GET request, prints the response body to the terminal
curl -I https://example.com                 # HEAD request - headers only, no body (quick status check)
curl -o output.html https://example.com     # save the response to a file instead of printing it
curl -L https://example.com                 # follow redirects (curl does NOT follow them by default)
curl -s https://example.com                 # "silent" - suppress the progress meter, just show output
```

## Training 2: Python and Pandas

[Open the Training 2 notes](/training-notes-site/notes/training-2/)

### What is a virtual environment and requirements.txt?

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install pandas
pip freeze > requirements.txt      # record exact versions
pip install -r requirements.txt    # recreate on another machine / in CI
```

## Training 3: Git Workflow

[Open the Training 3 notes](/training-notes-site/notes/training-3/)

### What is Git Flow, and what are the standard branch types?

```bash
git branch                     # list local branches
git branch feature/my-work     # create a new branch (doesn't switch to it)
git checkout feature/my-work   # switch to an existing branch
git checkout -b feature/my-work   # create AND switch in one step (older syntax)
git switch -c feature/my-work     # create AND switch in one step (newer, clearer syntax)
git switch develop                # switch to an existing branch (newer syntax)
git merge feature/my-work         # merge that branch into the current branch
git branch -d feature/my-work     # delete a branch (only if already merged)
git branch -D feature/my-work     # force-delete a branch (even if unmerged - use with caution)
```

### What are the core Git commands for tracking and saving changes?

```bash
git init                  # turn the current folder into a new Git repository
git status                # show what's changed, staged, or untracked
git add <file>             # stage a specific file's changes
git add .                  # stage everything changed in the current directory
git commit -m "message"    # save the staged changes as a new commit, with a message
git log                    # view commit history
git log --oneline          # condensed one-line-per-commit view
git diff                   # show unstaged changes compared to the last commit
git diff --staged          # show staged changes compared to the last commit
```

### What is the difference between git merge and git rebase?

```bash
git switch feature/login
git merge main        # adds a merge commit; existing commits unchanged
git rebase main       # rewrites feature/login's commits on top of main's latest commit
git rebase --abort    # give up mid-rebase and go back
```

### What is the difference between git fetch and git pull?

```bash
git fetch origin                 # update origin/main etc., your files untouched
git log main..origin/main        # see what's new before taking it
git pull                         # fetch + merge into the current branch
git pull --rebase                # fetch + rebase your local commits on top
```

### How do I clone a repo, connect a remote, and push a new branch?

```bash
git clone https://github.com/<user>/<repo>.git    # copy a repo; remote "origin" is set up
git remote -v                                     # list remotes and their URLs
git remote add origin <url>                       # connect a repo created with git init
git push -u origin feature/my-work                # first push; -u sets upstream tracking
git push                                          # later pushes - upstream already known
```

### How does a team actually cut and track a new release?

```bash
git tag v1.2.0                                  # lightweight tag - just a name pointing at a commit
git tag -a v1.2.0 -m "Release 1.2.0"            # annotated tag - includes a message, author, and date
git push origin v1.2.0                           # tags aren't pushed automatically - must be pushed explicitly
git tag                                          # list all tags
```

### What is Jenkins, and what is a Jenkinsfile?

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Lint') {
            steps {
                sh 'ruff check .'
            }
        }
        stage('Unit Test') {
            steps {
                sh 'pytest tests/unit'
            }
        }
        stage('Integration Test') {
            steps {
                sh 'pytest tests/integration'
            }
        }
        stage('Security Scan') {
            steps {
                sh 'pip-audit'
            }
        }
        stage('Artifact Creation') {
            steps {
                sh 'docker build -t myapp:latest .'
            }
        }
    }
}
```

### What is Docker Hub, and how do you deploy an image to it?

```bash
docker login                                          # authenticate with your Docker Hub account

docker build -t <your-dockerhub-user>/my-etl-app:1.0.0 .        # build the image, tagged as username/repo:tag

docker push <your-dockerhub-user>/my-etl-app:1.0.0              # upload that tagged image to Docker Hub
```

## Training 4: SQL Fundamentals & Data Warehousing

[Open the Training 4 notes](/training-notes-site/notes/training-4/)

### What does a CI pipeline definition (e.g. GitHub Actions YAML) look like, and what are its key parts?

```yaml
name: ci
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest -q

  deploy:
    needs: test                     # only runs if tests pass
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: prod               # can require a manual approval
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh
        env:
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

## Training 7: Spark Submit, Architecture & Execution

[Open the Training 7 notes](/training-notes-site/notes/training-7/)

### What does --executor-cores control?

```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --name CustomerETL \
  --driver-memory 4g \
  --executor-memory 8g \
  --executor-cores 4 \
  --num-executors 10 \
  job.py
```

### Why isn't there a dedicated spark-submit flag for every Spark setting?

```bash
spark-submit \
  --conf spark.sql.shuffle.partitions=400 \
  --conf spark.sql.adaptive.enabled=true \
  --conf spark.executor.memoryOverhead=2g \
  --conf spark.dynamicAllocation.enabled=true \
  job.py
```

### Do all spark-submit arguments apply to every cluster manager?

```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --queue analytics \
  --num-executors 20 \
  --executor-cores 4 \
  --executor-memory 8g \
  job.py
```

```bash
spark-submit \
  --master k8s://https://my-k8s-api:6443 \
  --deploy-mode cluster \
  --name my-job \
  --conf spark.kubernetes.container.image=my-spark:latest \
  --conf spark.executor.instances=5 \
  local:///opt/spark/jobs/job.py
```

### How does spark-submit decide which arguments belong to it versus the application being run?

```bash
spark-submit \
  --master yarn \
  --executor-memory 8g \
  my_job.py \
  --input s3://bucket/input \
  --date 2026-09-21
```

## Training 9: IntelliJ/Scala Setup & Scala Fundamentals

[Open the Training 9 notes](/training-notes-site/notes/training-9/)

### What is the difference between sbt package and sbt assembly, and how do you run the JAR?

```bash
sbt package
spark-submit --class SalesAnalysis \
  --jars postgresql-42.7.4.jar \
  target/scala-2.13/salesanalysis_2.13-0.1.0-SNAPSHOT.jar
```

## Training 13: Open Table Formats and NoSQL

[Open the Training 13 notes](/training-notes-site/notes/training-13/)

### Querying MongoDB (mongosh)

```javascript
use streaming_demo
show collections
db.weather.find().pretty()
db.weather.countDocuments()
db.weather.find().sort({ processed_at: -1 }).limit(10)                               // newest 10
db.weather.find({}, { _id: 0, city: 1, temperature: 1, processed_at: 1 }).limit(10)  // projection: chosen fields only
```

## Training 14: Kafka Cluster Setup & Spark Streaming

[Open the Training 14 notes](/training-notes-site/notes/training-14/)

### How do you initialize a KRaft-mode Kafka broker?

```bash
bin/kafka-storage.sh format \
  --standalone \
  -t "$KAFKA_CLUSTER_ID" \
  -c config/server.properties
```

### 2. Kafka Topic

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic market_ticks \
  --partitions 1 \
  --replication-factor 1
```

## Training 15: Cloud Platforms and Snowflake

[Open the Training 15 notes](/training-notes-site/notes/training-15/)

### Installing dbt (class follow-along)

```bash
cd ~/MCS/BigData/dbt-practice
source .venv/bin/activate      # (.venv) appears in the prompt
dbt --version                  # confirm core + adapters
pip install <anything else>    # pip works inside the venv
```

### Using Snowflake from the Command Line

```bash
pip install snowflake-cli          # inside a venv (e.g. dbt-practice)
snow connection add                # one-time: account identifier, user, auth, role, warehouse
snow connection test
snow sql -q "SELECT CURRENT_VERSION();"
snow sql -f load_market_ticks.sql
snow stage copy ./market-lake @market_stage --recursive   # upload local files to an internal stage
snow object list warehouse         # also: database, schema, table, ...
```

### Installing Snowflake CLI (class instructions, via ChatGPT)

```powershell
python --version                  # or: py --version  (the py launcher is more reliable on Windows)
py -m pip install --user pipx
py -m pipx ensurepath
# CLOSE AND REOPEN POWERSHELL (so the PATH change takes effect)
pipx --version
pipx install snowflake-cli
snow --version
snow connection add
snow connection list
snow sql -q "SELECT CURRENT_VERSION(), CURRENT_REGION();"
```

## Training 16: Snowflake Dynamic Tables

[Open the Training 16 notes](/training-notes-site/notes/training-16/)

### How do you write an IAM policy that allows S3 read/write but blocks deletes? (More IAM: Training 19.md.)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowBucketInspection",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation",
        "s3:GetBucketVersioning"
      ],
      "Resource": "arn:aws:s3:::company-data"
    },
    {
      "Sid": "AllowReadWriteObjects",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::company-data/*"
    },
    {
      "Sid": "ExplicitlyDenyDeletion",
      "Effect": "Deny",
      "Action": [
        "s3:DeleteObject",
        "s3:DeleteObjectVersion"
      ],
      "Resource": "arn:aws:s3:::company-data/*"
    },
    {
      "Sid": "ExplicitlyDenyBucketAdministration",
      "Effect": "Deny",
      "Action": [
        "s3:DeleteBucket",
        "s3:PutBucketPolicy",
        "s3:PutBucketVersioning"
      ],
      "Resource": "arn:aws:s3:::company-data"
    }
  ]
}
```

## Training 17: dbt with Snowflake

[Open the Training 17 notes](/training-notes-site/notes/training-17/)

### What is a dbt test?

```yaml
sources:
  - name: raw
    database: DE_CLASS
    schema: RAW
    tables:
      - name: orders
        columns:
          - name: order_number
            data_tests:
              - not_null
              - unique
          - name: status
            data_tests:
              - not_null
              - accepted_values:
                  values: ['Shipped', 'Cancelled', 'Resolved', 'On Hold', 'Disputed', 'In Process']
```

## Training 18: AWS Cloud Fundamentals

[Open the Training 18 notes](/training-notes-site/notes/training-18/)

### If you wanted to grant yourself certain permissions, which AWS service would you use?

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::company-bronze/*"
    }
  ]
}
```

### What is the difference between a role's trust policy and its permissions policy?

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "glue.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### What do S3 versioning and lifecycle rules do?

```json
{
  "Rules": [
    {
      "ID": "bronze-to-glacier",
      "Filter": { "Prefix": "orders/" },
      "Status": "Enabled",
      "Transitions": [{ "Days": 90, "StorageClass": "GLACIER" }],
      "NoncurrentVersionExpiration": { "NoncurrentDays": 30 }
    }
  ]
}
```

## Training 19: AWS Batch Pipelines

[Open the Training 19 notes](/training-notes-site/notes/training-19/)

### What is EMR Serverless?

```bash
aws emr-serverless start-job-run \
  --application-id <application-id> \
  --execution-role-arn <job-role-arn> \
  --job-driver '{
    "sparkSubmit": {
      "entryPoint": "s3://company-code/jobs/clean_sales.py",
      "entryPointArguments": ["s3://company-bronze/sales/", "s3://company-silver/sales/"]
    }
  }'
```

### Deploy steps

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt     # streamlit, pandas, redshift_connector
COPY app.py .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### What a run showed (Oct 7, 18:31 UTC)

```json
{
  "station_id": "1860189650739626488",
  "num_bikes_available": 0,
  "num_bikes_disabled": 13,
  "num_docks_available": 8,
  "is_installed": 1,
  "is_renting": 0,
  "is_returning": 0,
  "last_reported": 1791315217,
  "num_ebikes_available": 0
}
```

### How is the ingestion Lambda packaged and scheduled?

```bash
aws scheduler create-schedule \
  --name citi-bike-ingestion-5-min \
  --schedule-expression "rate(5 minutes)" \
  --flexible-time-window '{"Mode": "OFF"}' \
  --target '{"Arn": "<lambda-function-arn>", "RoleArn": "<scheduler-role-arn>"}'
```

## Training 23: Terraform and Step Functions

[Open the Training 23 notes](/training-notes-site/notes/training-23/)

### How do you install Terraform?

```bash
sudo apt update
sudo apt install -y gnupg software-properties-common curl

wget -O- https://apt.releases.hashicorp.com/gpg |
sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg]
https://apt.releases.hashicorp.com
$(. /etc/os-release && echo "${UBUNTU_CODENAME}") main" |
sudo tee /etc/apt/sources.list.d/hashicorp.list

sudo apt update
sudo apt install -y terraform
```

### What does a Step Functions definition look like?

```json
{
  "StartAt": "BronzeToSilver",
  "States": {
    "BronzeToSilver": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": { "JobName": "CitiBikeBronzeToSilver" },
      "Retry": [{
        "ErrorEquals": ["States.ALL"],
        "IntervalSeconds": 60,
        "MaxAttempts": 2,
        "BackoffRate": 2.0
      }],
      "Catch": [{ "ErrorEquals": ["States.ALL"], "Next": "NotifyFailure" }],
      "Next": "Done"
    },
    "NotifyFailure": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": { "TopicArn": "<sns-topic-arn>", "Message": "Glue job failed" },
      "Next": "Failed"
    },
    "Failed": { "Type": "Fail" },
    "Done": { "Type": "Succeed" }
  }
}
```

## Training 27: Getting into Azure

[Open the Training 27 notes](/training-notes-site/notes/training-27/)

### How do you install the Azure CLI and sign in?

```bash
# WSL / Ubuntu
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Windows PowerShell
winget install -e --id Microsoft.AzureCLI

az login                      # opens a browser sign-in
az login --use-device-code    # if no browser opens (prints a code to enter at microsoft.com/devicelogin)
az account show --output json # which tenant and subscription you're using
```

### How did Evan set up the environment variables?

```bash
STUDENT="teacher"                       # your own identifier
RG="rg-adls-$STUDENT"
LOCATION="eastus"                       # Evan's group showed East US
STORAGE="adls${STUDENT}$(openssl rand -hex 3)"   # must be globally unique
CONTAINER="bronze"
echo $RG $LOCATION $STORAGE $CONTAINER
```

### How did Evan create the storage account from the CLI?

```bash
az storage account create \
  --name $STORAGE --resource-group $RG --location $LOCATION \
  --sku Standard_LRS --kind StorageV2 \
  --hns true \
  --https-only true \
  --allow-blob-public-access false \
  --allow-shared-key-access false

az storage account show --name $STORAGE --resource-group $RG \
  --query "{name:name, hns:isHnsEnabled}" -o table
```

### How did Evan create the bronze container and folders?

```bash
az storage fs create --name $CONTAINER --account-name $STORAGE --auth-mode login
az storage container show --name $CONTAINER --account-name $STORAGE --auth-mode login

az storage fs directory create --name customers/raw \
  --file-system $CONTAINER --account-name $STORAGE --auth-mode login
```

### How did Evan upload, check and download the file?

```bash
az storage fs file upload --source ./customers.csv \
  --path customers/raw/customers.csv \
  --file-system $CONTAINER --account-name $STORAGE --auth-mode login

az storage fs file list --path customers/raw \
  --file-system $CONTAINER --account-name $STORAGE --auth-mode login -o table

az storage fs file download --path customers/raw/customers.csv \
  --destination ./customers-downloaded.csv \
  --file-system $CONTAINER --account-name $STORAGE --auth-mode login
cat customers-downloaded.csv
```

## Training 28: ADF and Databricks Medallion

[Open the Training 28 notes](/training-notes-site/notes/training-28/)

### How did Evan connect ADF to S3?

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket", "s3:GetBucketLocation"],
      "Resource": [
        "arn:aws:s3:::<teacher-bucket>",
        "arn:aws:s3:::<student-bucket>"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": [
        "arn:aws:s3:::<teacher-bucket>/*",
        "arn:aws:s3:::<student-bucket>/*"
      ]
    }
  ]
}
```

### How do you assign the role from the CLI for several students?

```bash
RG="<resource-group>"; ADF="<data-factory>"; SA="<storage-account>"

ADF_PRINCIPAL_ID=$(az datafactory show -g "$RG" -n "$ADF" --query identity.principalId -o tsv)
SA_ID=$(az storage account show -g "$RG" -n "$SA" --query id -o tsv)

az role assignment create \
  --assignee-object-id "$ADF_PRINCIPAL_ID" --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Contributor" --scope "$SA_ID"

az role assignment list --assignee "$ADF_PRINCIPAL_ID" --scope "$SA_ID" -o table
```
