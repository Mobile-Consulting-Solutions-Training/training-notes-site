---
title: Study Guide - Day 23
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 23: Terraform and Step Functions"
sidebar:
  order: 230
---

Study Guide - Day 23 (source: notes/Training 23.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Terraform.** Infrastructure as Code, by HashiCorp. You describe cloud resources (buckets, Lambdas, Glue jobs, EC2) in `.tf` files and Terraform builds them. Building a pipeline *is* building infrastructure; a Terraform file is the one place that records exactly what exists and what connects to what. Compared with clicking the console (not repeatable, no record) or CLI scripts (partly repeatable), Terraform is repeatable and tracked in code plus a **state file**.

**HCL.** HashiCorp Configuration Language (not HCL the company). A **declarative DSL**: you write what should exist and Terraform works out the steps. Blocks: `provider` (which cloud and region), `data` (look up something that exists, e.g. the latest Amazon Linux AMI), `resource` (something Terraform creates, e.g. `aws_instance`), `output` (values printed after apply, e.g. instance ID, public IP).

**Installing.** Ubuntu: add HashiCorp's GPG key and apt repository, then `apt install terraform`. Mac: `brew tap hashicorp/tap && brew install hashicorp/tap/terraform`.

**Workflow.** `terraform init` (download the provider, once per folder) → `terraform plan` (dry run: green `+` create, red `-` destroy) → `terraform apply` (asks `yes`, then builds) → `terraform destroy` (remove everything so nothing bills). Terraform uses the same credentials as the AWS CLI (`aws configure`, a profile or `AWS_PROFILE`), never keys in the file. Gotchas: check the console Region; SSH needs a security group rule on port 22 and a key pair, which should also be declared in Terraform; production saves the plan with `-out`.

**Orchestration.** "The process of managing and automating the things that your resources do, whether on cloud or on prem." The orchestrator does no data work; it decides what runs, in what order, on what schedule, and handles dependencies, retries and visibility. **Apache Airflow** is the prototypical orchestrator (Python DAGs); **MWAA** is managed Airflow; **Step Functions** is AWS's serverless orchestrator. Kubernetes orchestrates containers, a different meaning.

**Cron.** A scheduling framework (`crontab -e`); its syntax is used by GitLab, EventBridge and Airflow. Fields: minute, hour, day of month, month, day of week. `0 5 * * 1` = 5:00 AM every Monday; `*/5` in the first field = every 5 minutes (minimum unit is a minute). Cron only handles *when*; orchestrators add dependencies, retries and visibility.

**AWS Step Functions.** Serverless workflow orchestrator. A **state machine** is the workflow, made of **states**: Task, Choice, Parallel, Map, Wait, Pass, Succeed/Fail, each with Retry/Catch. Written in **Amazon States Language** (JSON) or drawn in Workflow Studio. **Standard** (up to a year, exactly-once, per state transition) vs **Express** (≤ 5 minutes, high volume, per request and duration).

**Serverless Applications.** You don't manage servers; AWS provisions, patches and scales, and you pay per use, close to $0 when idle. The Citi Bike pipeline is mostly serverless: Lambda, EventBridge Scheduler, Step Functions, S3, Kinesis on-demand, Glue, Redshift/Aurora Serverless. Serverful (EC2) means you manage OS, patching and uptime and pay while it runs; serverless has service limits (Lambda 15 minutes).

---

# Part 2: Cheat Sheet

## Terraform
- IaC · declarative HCL · `.tf` files + state file
- Blocks: `provider` · `data` (lookup) · `resource` (create) · `output`
- `init` → `plan` → `apply` → `destroy`
- Credentials from AWS CLI profile · never keys in code · check Region · declare security groups too

## Orchestration
- Coordinates order, schedule, retries, visibility · does no data work
- Airflow (Python DAGs) · MWAA · Step Functions · Kubernetes = containers

## Cron
- minute hour day-of-month month day-of-week
- `0 5 * * 1` = Mon 5 AM · `*/5 * * * *` = every 5 min

## Step Functions
- State machine · states: Task, Choice, Parallel, Map, Wait, Pass, Succeed/Fail
- Retry / Catch · Amazon States Language (JSON) · Workflow Studio
- Standard (long, exactly-once) vs Express (≤ 5 min, high volume)

## Serverless
- No server management · pay per use · service limits
- Lambda, EventBridge, Step Functions, S3, Kinesis, Glue, Redshift Serverless

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What is Terraform?
A: An Infrastructure as Code tool from HashiCorp. You describe cloud resources in code files, and Terraform creates, changes and deletes them to match.

Q: Why use Terraform instead of clicking through the console?
A: Console work can't be repeated and leaves no record. A Terraform file is repeatable and is the single place that says exactly what infrastructure exists and how it connects.

Q: What is HCL?
A: HashiCorp Configuration Language, the declarative language Terraform files are written in. You describe what should exist, and Terraform figures out how to get there.

Q: What's the difference between a data block and a resource block?
A: A data block looks up something that already exists, like the latest Amazon Linux image, without changing it. A resource block is something Terraform creates and manages, like an EC2 instance.

Q: Walk through the Terraform workflow.
A: terraform init downloads the provider plugins. terraform plan shows what will change without changing anything. terraform apply makes the changes after you confirm. terraform destroy deletes everything the configuration created.

Q: What should you look for in a Terraform plan?
A: Green plus signs mean resources will be created. Red minus signs mean something will be destroyed, so read those carefully before typing yes.

Q: How does Terraform get AWS credentials?
A: The same way the AWS CLI does, from aws configure or a named profile. Keys never go in the Terraform file.

Q: What is orchestration?
A: Managing and automating what your resources do: which steps run, in what order, on what schedule, and what happens when one fails. The orchestrator tells services like Glue and Lambda when to work but doesn't do the data work itself.

Q: What's the most well-known orchestrator?
A: Apache Airflow, which defines workflows as Python DAGs. AWS offers it managed as MWAA, and Step Functions is AWS's own serverless orchestrator.

Q: Is Kubernetes an orchestrator in the same sense?
A: It orchestrates containers, keeping them running and scaled, but it isn't a pipeline scheduler like Airflow or Step Functions.

Q: What does the cron expression 0 5 * * 1 mean?
A: At minute 0 of hour 5 on any day of the month, any month, on Monday. So 5 AM every Monday.

Q: What does an orchestrator add on top of cron?
A: Cron only decides when something runs. An orchestrator adds dependencies between steps, retries, failure handling and one place to see what happened.

Q: What is AWS Step Functions?
A: AWS's serverless workflow orchestrator. You define a state machine of steps, like run a Glue job then a Lambda, with retries and branches, and AWS runs it and tracks each step.

Q: What's the difference between Standard and Express workflows?
A: Standard workflows can run up to a year with exactly-once steps and are priced per state transition. Express workflows are short, under five minutes, for high volume, priced per request and duration.

Q: What does serverless mean for an application?
A: You don't manage any servers. AWS provisions and scales them, and you pay for what you use, often close to nothing when idle, within service limits like Lambda's 15 minutes.
