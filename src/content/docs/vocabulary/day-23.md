---
title: Day 23 Vocabulary
description: Glossary of terms and definitions from the Training 23 notes.
sidebar:
  order: 23
---

Vocabulary — Study Guide Day 23

Source: notes/Training 23.md

## Infrastructure as Code (Terraform)
- **Terraform** — A HashiCorp Infrastructure as Code tool that describes cloud infrastructure in code files and builds it with a couple of commands.
- **IaC (Infrastructure as Code)** — Defining infrastructure in version-controllable code files so it is repeatable and recorded, instead of clicking through a console.
- **HashiCorp** — The company that makes Terraform.
- **ClickOps** — Creating resources by clicking through web console forms; not repeatable and leaves no record.
- **DevOps** — The engineering discipline focused on infrastructure, deployment and operations; advanced Terraform belongs here.
- **HCL (HashiCorp Configuration Language)** — The declarative, domain-specific language Terraform `.tf` files are written in (not HCL the company).
- **DSL (Domain-Specific Language)** — A language built for one purpose, such as describing infrastructure, rather than general programming.
- **Declarative** — Writing what should exist and letting the tool work out the steps to get there.
- **.tf file** — A Terraform configuration file written in HCL, e.g. `main.tf`.
- **provider block** — Declares which cloud Terraform talks to and where, e.g. `provider "aws"` with a region.
- **data block** — A read-only lookup of something that already exists, e.g. the latest Amazon Linux AMI.
- **resource block** — Something Terraform creates and manages, e.g. an `aws_instance`.
- **output block** — Values printed after `apply`, such as an instance ID or public IP.
- **Provider plugin** — The downloaded component that lets Terraform call a cloud's API, stored in `.terraform/`.
- **State file** — Terraform's record of the real resources it has created and manages.
- **terraform init** — Run once per folder to download the provider plugin.
- **terraform plan** — A dry run comparing code to what exists and listing changes (`+` create, `-` destroy) without changing anything.
- **terraform apply** — Shows the plan, asks for `yes`, then creates or changes resources.
- **terraform destroy** — Deletes everything the configuration created.
- **-out (saved plan)** — A `plan` flag that saves the plan to a file so production applies exactly that plan.
- **AWS_PROFILE** — Environment variable that selects a named AWS CLI profile, which Terraform can use for credentials.
- **Named profile** — A saved set of AWS credentials/config selected by name, set up via `aws configure`.
- **Informatica / Pentaho / Talend / Palantir** — Vendors that sold expensive all-in-one pipeline platforms that never really took off.

## AWS Compute Basics
- **EC2 (Elastic Compute Cloud)** — A virtual machine in AWS; the most basic AWS service.
- **AMI (Amazon Machine Image)** — The operating system image an EC2 instance boots from, e.g. Amazon Linux.
- **t3.micro** — One of the smallest and cheapest EC2 instance types.
- **Tag** — A name/label attached to a resource so you can find and group it.
- **Instance ID** — AWS's unique ID for an EC2 instance.
- **Public IP** — An instance's internet-facing address.
- **Region** — A geographic AWS location such as us-east-2 (Ohio) or us-east-1 (N. Virginia); check the console's region selector if a resource seems missing.
- **Security group** — A virtual firewall; SSH requires an inbound rule for port 22 from your IP.
- **SSH (Secure Shell)** — Encrypted remote login to a server, on port 22.
- **Key pair** — A public/private key used to SSH into an EC2 instance.
- **EC2 Instance Connect** — A way to connect to an EC2 instance through AWS without managing your own key pair.
- **authorize-security-group-ingress** — AWS CLI command that adds an inbound rule to a security group.

## Linux Install Tools
- **apt** — The Ubuntu/Debian package manager used to install software.
- **gnupg (GPG)** — Tool for verifying signatures; used to check packages really come from HashiCorp.
- **Signing key** — A cryptographic key that lets apt verify a repository's packages.
- **gpg --dearmor** — Converts a downloaded key into the binary keyring format apt uses.
- **tee** — Command that writes its input to a file (here, with `sudo`) and to the screen.
- **UBUNTU_CODENAME** — The release name of your Ubuntu version, used to pick the right repository.
- **Homebrew (brew)** — The Mac package manager; `brew tap` adds a third-party repository.

## Orchestration
- **Orchestration** — The process of managing and automating the things that your resources do, whether on cloud or on prem: ordering, scheduling, retries and visibility.
- **Orchestrator** — A tool that tells services when to run and tracks success, without doing the data work itself.
- **Apache Airflow** — The prototypical, industry-standard open-source orchestrator, with workflows defined as Python DAGs.
- **DAG (Directed Acyclic Graph)** — A workflow of tasks and dependencies with no cycles, as used in Airflow.
- **Amazon MWAA (Managed Workflows for Apache Airflow)** — AWS-managed Airflow.
- **Kubernetes** — A container orchestration system that keeps containers running, scaled and healthy; not a pipeline scheduler.
- **Container** — A packaged, isolated unit of software with its dependencies.
- **cron** — A scheduling framework on Unix systems; its syntax is used near-universally (GitLab, EventBridge, Airflow).
- **crontab -e** — Command to edit your cron schedule.
- **Cron expression** — Five fields (minute, hour, day of month, month, day of week) defining a schedule, e.g. `0 5 * * 1` = 5 AM every Monday.
- **\*/5** — Cron step syntax meaning "every 5" units; in the first field, every 5 minutes.
- **Dependencies** — Rules that a step runs only after another step succeeds.
- **Retries** — Automatically re-running a failed step before alerting.
- **EventBridge** — AWS service that triggers targets on a schedule or event.

## AWS Step Functions
- **AWS Step Functions** — AWS's serverless workflow orchestrator that runs a state machine of steps and tracks each one's success or failure.
- **State machine** — The whole Step Functions workflow.
- **State** — One step in a state machine.
- **Task state** — A state that calls a service such as Lambda or Glue.
- **Choice state** — A state that branches based on a condition.
- **Parallel state** — A state that runs branches at the same time.
- **Map state** — A state that loops over a list of items.
- **Wait state** — A state that pauses for a time.
- **Pass state** — A state that passes input to output without doing work.
- **Succeed / Fail state** — States that end an execution successfully or as a failure.
- **Retry / Catch** — Built-in per-step error handling in Step Functions.
- **Amazon States Language** — The JSON language Step Functions workflows are written in.
- **Workflow Studio** — The visual drag-and-drop editor for Step Functions.
- **Standard workflow** — Long-running (up to a year), exactly-once Step Functions workflow priced per state transition.
- **Express workflow** — Short (up to 5 minutes), high-volume Step Functions workflow priced per request and duration.

## Serverless Applications
- **Serverless** — You don't manage the servers; AWS provisions, patches and scales them and you pay for what you use.
- **Serverless application** — An application built entirely from managed serverless pieces.
- **Serverful** — Compute such as EC2 where you manage the OS, patching, scaling and uptime and pay while it runs.
- **Lambda** — AWS serverless function that runs code on demand, max 15 minutes per run.
- **EventBridge Scheduler** — Serverless scheduler that triggers targets on a schedule.
- **Glue** — AWS serverless Spark ETL service.
- **Redshift Serverless** — A Redshift warehouse that scales and bills compute automatically.
- **Aurora Serverless** — An Aurora database that scales (and can pause) on its own.
- **Auto-scaling** — Automatically adding or removing capacity based on load.
- **Delivery guarantees** — Promises about how many times a message is processed (at-most-once, at-least-once, exactly-once), reviewed in the homework.
