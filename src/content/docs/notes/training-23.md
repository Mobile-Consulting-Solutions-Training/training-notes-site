---
title: "Training 23 - Terraform and Step Functions"
description: "Infrastructure as Code with Terraform, orchestration with cron and Airflow, and AWS Step Functions."
sidebar:
  order: 23
---

Teacher: Evan Flint

Syllabus Day 24 (per file numbering; Tue Oct 13). Topics: homework review (delivery guarantees), then Evan jumped ahead in the syllabus to **Terraform / Infrastructure as Code**, then **AWS Step Functions**. More filled in as class goes.

Roadmap Day 24 topics live elsewhere: Redshift design/optimization (Training 18 and 21), Kinesis (Training 22), RDS/Aurora patterns (Training 18 and 22). Terraform continues in Training 24 (import, state) and Training 25 (fundamentals); Airflow is in Training 26.

---

# Homework Review: Delivery Guarantees

Q. What are the three delivery guarantees, and which one does our Kinesis → Glue → Aurora pipeline have?

A. (Topic of the homework review; the class discussion itself wasn't captured.) At-most-once, at-least-once and exactly-once describe how many times each message can reach the sink if something fails.

Expanded:

| Guarantee | What can happen on failure | How you get it | Cost |
|---|---|---|---|
| **At-most-once** | Messages can be **lost**, never duplicated | Commit the offset/checkpoint *before* processing | Cheapest, but data loss |
| **At-least-once** | Nothing lost, but messages can be **duplicated** | Commit the checkpoint *after* the write succeeds; replay on failure | The usual default |
| **Exactly-once** | Each message affects the result once | Transactions (Kafka EOS), or at-least-once + an **idempotent sink** | Most complex |

Applied to the Training 22 streaming demo:
- Kinesis keeps records for the retention period, and the Glue streaming job checkpoints its position **after** writing a micro-batch. If it crashes mid-batch, it re-reads from the last checkpoint, so delivery is **at-least-once**.
- The Aurora sink upserts on the key `(station_id, snapshot_ts)` (`INSERT … ON CONFLICT`). A replayed record overwrites itself instead of adding a row, so the *result* is **effectively exactly-once**.

**Interview line:** "Most streaming pipelines are at-least-once end to end. I make them effectively exactly-once by making the sink idempotent: upsert or MERGE on a natural key, so a replayed message can't create a duplicate."

---

# Infrastructure as Code (Terraform)

## Resources

| Resource | Link |
|---|---|
| Install Terraform (official tutorial; Linux, Mac, Windows tabs) | https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli |
| HashiCorp apt signing key (used in the Linux install) | https://apt.releases.hashicorp.com/gpg |

---

Q. What is Terraform?

A. (Teacher's definition) Terraform — Infrastructure As Code.

Expanded: Terraform is a tool by HashiCorp that lets you describe your cloud infrastructure in a code file. That could be an S3 bucket, two Lambda functions, a Glue job and a Redshift cluster. Two commands then build all of it for you. Evan's framing: building a data pipeline *is* building infrastructure. On-prem, that means physical nodes you have to unbox and plug in. In the cloud, every resource can be created by an API call, and Terraform takes advantage of that. Clicking through the console works, but it can't be repeated and nothing records what you built. A Terraform file is the single place where "we know exactly what our infrastructure is, what is connected to what."

Evan is only teaching the basics, because we're data engineers, not DevOps engineers. Advanced Terraform covers things like managing state across a team and controlling network ingress and egress, and could be a later lesson.

| Approach | How you create resources | Repeatable? | Record of what exists? |
|---|---|---|---|
| **Console (ClickOps)** | Click through web forms | No, you redo it by hand | No |
| **AWS CLI / scripts** | One command per resource | Partly; a rerun can fail or duplicate | Only the script |
| **Terraform (IaC)** | Declare the end state in `.tf` files, then `plan` + `apply` | Yes, the same file gives the same result | Yes, the code plus Terraform's state file |

**Interview line (why IaC?):** "Infrastructure as code makes environments repeatable and reviewable. The same files build dev and prod, changes go through pull requests and `terraform plan` before anything is touched, the code documents what exists, and drift from manual changes shows up in the next plan." For Terraform state, modules and variables, see Training 25; for importing existing resources, see Training 24.

Evan also mentioned that vendors like Informatica, Pentaho, Talend and Palantir tried to sell one all-in-one pipeline platform. They're expensive to even learn, so they never really took off. Real pipelines are many services stitched together, which is exactly what Terraform describes.

---

Q. What is HCL?

A. (Teacher's definition) Hashicorp Configuration Language (HCL). Not to be confused with HCL the company.

Expanded: HCL is the language Terraform files (`.tf`) are written in. It's a **domain-specific language (DSL)**: it is built for describing infrastructure, not for general programming. It's **declarative**: you write *what* should exist, and Terraform works out the steps to get there. (HCL the company is a large Indian IT consulting firm that Evan used to work through. Same letters, unrelated.)

| Block | Purpose | In Evan's `main.tf` |
|---|---|---|
| `provider` | Which cloud to talk to, and where | `provider "aws"`, the region (us-east-2, Ohio) |
| `data` | **Looks up** something that already exists (read-only) | `data "aws_ami" "amazon_linux"`: finds the latest Amazon Linux image, filtered by name and state |
| `resource` | Something Terraform **creates and manages** | `resource "aws_instance" "demo"`: a `t3.micro` EC2 instance tagged `terraform-class-demo` |
| `output` | Values printed after `apply` | `instance_id`, `public_ip` |

| Term | Meaning |
|---|---|
| **EC2** | Elastic Compute Cloud: a virtual machine (a computer) in AWS. The most basic AWS service |
| **AMI** | Amazon Machine Image: the operating system image the EC2 instance boots from. Amazon Linux is the default, but Ubuntu, other Linux distributions, Windows or macOS are also possible |
| **t3.micro** | One of the smallest (cheapest) instance types; fine for a demo |
| **Tag** | A name/label attached to a resource so you can find and group it |
| **Instance ID** | AWS's unique ID for that EC2 instance |
| **Public IP** | The internet-facing address, if you choose to expose it |

---

Q. How do you install Terraform?

A. (Teacher's definition) Linux (Ubuntu/Debian) instructions:

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

Expanded: The Linux steps add HashiCorp's own package repository, then install from it.

| Step | What it does |
|---|---|
| `apt install gnupg software-properties-common curl` | Tools needed to verify and add a repository |
| `wget … gpg \| gpg --dearmor -o …keyring.gpg` | Downloads HashiCorp's signing key, so apt can verify the packages really come from HashiCorp |
| `echo "deb [signed-by=…] … main" \| sudo tee …hashicorp.list` | Adds HashiCorp's repository for your Ubuntu version (`UBUNTU_CODENAME`) and ties it to that key |
| `apt update` + `apt install terraform` | Refreshes the package list and installs Terraform |

Note: as pasted, the `echo "deb …"` line is split across three lines. In the official version the `deb [...] URL codename main` part is one line. If apt complains about a malformed entry, put it on one line.

**On a Mac (yours):**
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
terraform -version
```

---

Q. What is the Terraform workflow?

A. (Teacher's definition, from the demo) Write `main.tf`, then `terraform init` → `terraform plan` → `terraform apply`, and take it all down with `terraform destroy`.

Expanded:

| Command | What it does | What to look for |
|---|---|---|
| `terraform init` | Run once per folder. Downloads the provider plugin (e.g. AWS) into `.terraform/` | "Terraform has been successfully initialized" |
| `terraform plan` | Dry run: compares your code to what exists and lists the changes. Changes nothing | Green `+` = create (good). Red `-` = destroy, so check carefully |
| `terraform apply` | Shows the plan again, asks `yes`, then actually creates or changes resources in AWS | Read the plan before typing `yes`; outputs print at the end |
| `terraform destroy` | Deletes everything this configuration created | Run it at the end of a demo so nothing keeps billing |

How Terraform logs in: it uses the same AWS credentials as the CLI, from `aws configure` or a named profile. It never puts keys in the `.tf` file. Evan's account uses a profile, which Terraform can pick up with `profile = "…"` in the provider block or the `AWS_PROFILE` environment variable.

**Gotchas from the demo:**
- The console was showing **N. Virginia (us-east-1)**, but the instance was created in **Ohio (us-east-2)**. If a resource seems missing, check the console's region selector first.
- The instance can't be reached over SSH by default. The **security group** needs an inbound rule for port 22 from your IP, and you need a **key pair** or **EC2 Instance Connect**. Evan added the rule with `aws ec2 authorize-security-group-ingress`. In real Terraform you'd declare the security group and rule in `main.tf` too, so the code describes everything.
- `plan` warned that the plan wasn't saved (`-out`). That's fine for a demo. In production you save the plan and apply exactly that file.

---

# Orchestration

Q. What is orchestration?

A. (Teacher's definition) The process of managing and automating the things that your resources do, whether on cloud or on prem.

Expanded: Orchestration means coordinating the steps of a pipeline: what runs, in what order, on what schedule, what depends on what, and what happens when a step fails. The orchestrator does none of the data work itself. It tells Lambda, Glue, EMR or Redshift *when* to do their work and watches whether it succeeded. Up to now we've been triggering each piece by hand or with an EventBridge schedule. An orchestrator ties them into one managed workflow.

A student asked whether it relates to Kubernetes managing EC2 instances and other resources. Evan said yes, it involves managing resources, and Kubernetes does orchestration among many other things. But Kubernetes isn't usually called an orchestrator in this sense; it orchestrates *containers*, not pipeline steps. **The prototypical orchestrator is Apache Airflow**, which we'll cover later in the course. Step Functions is AWS's managed orchestrator.

| Tool | Type | How workflows are defined |
|---|---|---|
| **Apache Airflow** | Open-source, the industry standard | Python DAGs (tasks + dependencies) |
| **Amazon MWAA** | AWS-managed Airflow | Same Python DAGs, but AWS runs the servers |
| **AWS Step Functions** | AWS serverless orchestrator | State machines in Amazon States Language (JSON) or the visual Workflow Studio |
| **Kubernetes** | Container orchestration (different meaning) | Keeps containers running, scaled and healthy; not a pipeline scheduler |

Evan tied orchestration back to **cron**, which we covered earlier: cron is a *framework* for scheduling tasks, not one command. Edit it with `crontab -e` (`-e` = edit). Cron syntax is the near-universal scheduling syntax: the same format shows up in GitLab pipeline schedules, EventBridge and **Apache Airflow**. Cron only handles the *when*. Orchestrators add the dependencies, retries and visibility on top. Evan decided to do a quick **Airflow demo before the Step Functions demo**, because Airflow is so central to orchestration.

| Cron field (left → right) | Range | Example `0 5 * * 1` |
|---|---|---|
| Minute | 0–59 | `0` = at minute 0 |
| Hour | 0–23 | `5` = 5 AM |
| Day of month | 1–31 | `*` = any |
| Month | 1–12 | `*` = any |
| Day of week | 0–7 (0 and 7 both = Sunday) | `1` = Monday → "5:00 AM every Monday" |

Note: `*/5` in the first field means every 5 **minutes**, not seconds. Standard cron's smallest unit is one minute. Full cron notes: Training 1. Airflow uses the same syntax for `schedule`: see the Apache Airflow section in Training 26.

| What an orchestrator handles | Example in our Citi Bike pipeline |
|---|---|
| **Order / dependencies** | Run the Bronze → Silver Glue job only after the Lambda has landed new JSON |
| **Scheduling** | Run the whole pipeline every hour |
| **Retries / failure handling** | Retry Glue twice, then send an alert |
| **Visibility** | One place to see which step failed and when |

---

# AWS Step Functions

Q. What is AWS Step Functions?

A. (Teacher's definition) Step Functions

Expanded: **One-line answer:** AWS's serverless workflow orchestrator. You define a state machine of steps, and AWS runs it with retries, branching and error handling.

Step Functions is AWS's serverless **workflow orchestrator**. You define a **state machine**, a diagram of steps such as "run this Glue job, then this Lambda, if it fails retry or alert, run these in parallel". AWS then runs it, tracking each step's success or failure. It's AWS's managed counterpart to an Airflow DAG: it decides *what runs when and in what order*, while services like Lambda, Glue and Redshift do the work. Workflows are written in the **Amazon States Language** (JSON) or drawn in the visual Workflow Studio. Training 24 shows the real Citi Bike state machine built in class.

| Concept | Meaning |
|---|---|
| **State machine** | The whole workflow |
| **State** | One step: Task (call a service), Choice (branch), Parallel, Map (loop over items), Wait, Pass, Succeed/Fail |
| **Retry / Catch** | Built-in error handling per step |
| **Standard vs Express** | Standard: long-running (up to a year), exactly-once steps, priced per state transition. Express: short (≤ 5 min), high volume, priced per request and duration |

| | Standard workflow | Express workflow |
|---|---|---|
| Max duration | 1 year | 5 minutes |
| Execution semantics | **Exactly-once** | **At-least-once** (asynchronous) or **at-most-once** (synchronous) |
| What that means for your steps | A step won't run twice unless your `Retry` says so | A step can run twice, so steps must be **idempotent** |
| Pricing | Per state transition | Per request + duration/memory |
| Execution history | Kept in the console (90 days) | Sent to CloudWatch Logs |
| Typical use | Batch ETL pipelines, human approval, long Glue jobs | High-volume event processing (IoT, streaming) |

**Interview line:** "Standard is for long-running, exactly-once workflows like a nightly ETL. Express is for short, high-volume event processing; it's at-least-once, so every step has to be idempotent."

---

Q. What does a Step Functions definition look like?

A. (Not shown in class; standard Amazon States Language.) A JSON document with a `StartAt` state and a `States` map. Each Task state names a service integration, and can have `Retry` and `Catch` blocks.

Expanded: a minimal version of "run a Glue job, retry on failure, alert if it still fails":

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

| Piece | Meaning |
|---|---|
| `.sync` on the Resource | Wait until the Glue job **finishes** before moving on (not just until it starts) |
| `Retry` | Try again on matching errors: 60 s, then 120 s (`BackoffRate` 2.0), up to 2 more attempts |
| `Catch` | After retries are used up, go to another state instead of failing silently |

| Service integration pattern | Resource suffix | Step Functions waits for |
|---|---|---|
| Request-Response | none (e.g. `glue:startJobRun`) | Only the API call to return. The job may still be running |
| Run a Job | `.sync` | The job to complete (Glue, EMR, ECS, Batch, another state machine) |
| Wait for callback | `.waitForTaskToken` | Someone to call `SendTaskSuccess` / `SendTaskFailure` with the token (human approval, external systems) |

**Interview line (Step Functions vs Airflow):** see the comparison table in Training 26. Short version: Step Functions is serverless and AWS-native with JSON state machines; Airflow is Python DAGs, cloud-neutral, with scheduling, backfill and a huge operator library.

---

# Serverless Applications

Q. What is a serverless application?

A. (Teacher's definition) Serverless applications

Expanded: **One-line answer:** an application built from managed services where the cloud provider runs, patches and scales the servers, and you pay per use instead of for always-on machines.

"Serverless" doesn't mean there are no servers. It means **you don't manage them**. AWS provisions, patches and scales the machines, and you pay for what you use, often per request or per second, instead of for a machine that's always on. A serverless application is built entirely from these managed pieces, and many of them are already in our Citi Bike pipeline.

| Serverless service | Role | We've used it as |
|---|---|---|
| **Lambda** | Run code on demand | The Citi Bike producer |
| **EventBridge Scheduler** | Trigger on a schedule or event | Running the Lambda every few minutes |
| **Step Functions** | Orchestrate the steps | (today) |
| **S3** | Storage | The Bronze/Silver data lake |
| **Kinesis (on-demand)** | Streaming buffer | `citibike-station-stream` |
| **Glue** | Serverless Spark ETL | The Bronze → Silver job, streaming job |
| **Redshift Serverless / Aurora Serverless** | Databases that scale (and can pause) on their own | The Gold warehouse / the streaming sink |

| | Serverful (e.g. EC2 from the Terraform demo) | Serverless (e.g. Lambda) |
|---|---|---|
| You manage | OS, patching, scaling, uptime | Only your code and configuration |
| Billing | Per hour the machine runs, even idle | Per request / duration / data; ~$0 when idle (mostly) |
| Scaling | You add instances or set up auto-scaling | Automatic |
| Limits | Whatever the machine can do | Service limits (e.g. Lambda max 15 minutes per run) |
