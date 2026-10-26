---
title: "Interview Questions: Cloud and DevOps"
description: "Interview questions with the class answer, a corrected expanded answer and a short answer to say out loud: AWS / Other Cloud Technology, Azure, GCP, CI/CD, Infrastructure as Code, Docker, Kubernetes, Monitoring and Alerting, DevOps."
sidebar:
  order: 14
---

Each question has three parts: **A. (Class answer)**, the answer from the class question bank as given; **Expanded**, a corrected and fuller explanation (starting with **Correction:** when the class answer was wrong); and **Say it out loud**, a short answer for the interview itself. Start with the [traps to unlearn](/training-notes-site/reference/interview-prep/#traps-to-unlearn).

## AWS / Other Cloud Technology


**Q. How do you submit a Spark job on EMR?**

**A. (Class answer)**

There are multiple options for how to submit a Spark job on EMR.

1. Use spark-submit from the console while logged into the cluster, in the same way that you would on a standard Hadoop cluster.
2. Using the AWS CLI with the "aws emr add-steps" command, for example:
   ```bash
   aws emr add-steps --cluster-id j-1234567890EXAMPLE \
   --steps Type=Spark,Name="Spark job",ActionOnFailure=CONTINUE,Args=[--class,org.apache.spark.examples.SparkPi,s3://my-bucket/my-spark-job.jar,100]
   ```
3. From the AWS Management Console (the web interface), click on your cluster, go to the "applications" section, click on spark, select "add job flow step" and select your jar or py file that contains the spark job.
4. Using Boto3 a Spark job can be started from a locally running program, using `emr_client.add_job_flow_steps`.

**Expanded:** Options 1, 2 and 4 are correct. Small correction on option 3: in the current EMR console you open the cluster, go to the **Steps** tab and choose **Add step** (type "Spark application"), then point it at your script or JAR in S3. There is no "add job flow step" under an "applications" section (verify against the current console). Steps are the standard way because they're logged, can be queued and can terminate the cluster when finished.

More options worth naming:

| Method | Notes |
|---|---|
| `spark-submit` over SSH on the primary node | Interactive and debugging |
| EMR **steps** (console, `aws emr add-steps`, boto3 `add_job_flow_steps`) | Standard for batch on EMR on EC2 |
| **EMR Serverless** `start-job-run` | No cluster to manage. Submit to an application |
| Orchestrators | Airflow `EmrAddStepsOperator`/`EmrServerlessStartJobOperator`, Step Functions EMR integration |
| EMR on EKS | Runs Spark on a Kubernetes cluster |

See [Training 18 notes](/training-notes-site/notes/training-18/) ("EMR (Elastic MapReduce)") and [Training 19 notes](/training-notes-site/notes/training-19/) ("EMR Serverless").

**Say it out loud:** "On EMR on EC2 I add a step, from the console, `aws emr add-steps` or boto3, pointing at my script in S3, or I SSH to the primary node and run spark-submit to debug. With EMR Serverless I call `start-job-run`, and in production an orchestrator like Airflow or Step Functions submits it."

---

**Q. What is EMR?**

**A. (Class answer)**

EMR is essentially a Hadoop cluster that runs on a cluster of EC2 instances on the AWS cloud. It is the preferred method for running Hadoop, Hive, or Spark on AWS.

**Expanded:** The teacher's answer is correct for **EMR on EC2**. Amazon EMR (Elastic MapReduce) is AWS's managed big data platform: it provisions and configures clusters that run Spark, Hive, Presto/Trino, HBase, Flink and Hadoop. Key points:
- Data usually lives in **S3** (through EMRFS), not HDFS, so clusters can be **transient**: start, run the job, terminate.
- Node types: **primary** (formerly master), **core** (run tasks and HDFS), **task** (compute only, good on Spot).
- Deployment options: **EMR on EC2**, **EMR Serverless** (no cluster, pay per use) and **EMR on EKS**.
- Uses the Glue Data Catalog as its Hive metastore if you choose.

See [Training 18 notes](/training-notes-site/notes/training-18/) ("EMR (Elastic MapReduce)" and "EMR vs Glue: When to Use Which") and [Training 19 notes](/training-notes-site/notes/training-19/) ("EMR Serverless").

**Say it out loud:** "EMR is AWS's managed big data platform for Spark, Hive and other Hadoop tools. It runs as clusters on EC2, usually reading and writing S3 so clusters can be temporary, and there are also EMR Serverless and EMR on EKS options."

---

**Q. What is Glue?**

**A. (Class answer)**

AWS Glue is essentially a serverless version of Spark which runs on the AWS cloud. While heavily based on Spark, Glue has a slightly different API, the most notable feature of which is the DynamicFrame API.

Glue jobs are priced based on the number of resources provided to the job and the amount of time that the job runs. Because it is serverless, when a job is not running you are not charged any money.

**Expanded:** The teacher's answer is correct for Glue ETL jobs. Precision: pricing is per **DPU-hour** (a DPU is 4 vCPUs and 16 GB of memory), billed per second with a 1-minute minimum on recent Glue versions. Glue is also more than serverless Spark:

| Glue component | Role |
|---|---|
| ETL jobs | Serverless Spark (PySpark/Scala), plus Python shell and Ray jobs |
| **Data Catalog** | Central metadata store shared by Athena, EMR, Redshift Spectrum |
| Crawlers | Scan S3 or databases and infer schemas into the catalog |
| Streaming ETL | Spark Structured Streaming from Kinesis or Kafka |
| Workflows / triggers | Simple orchestration |
| Job bookmarks | Remember what was already processed for incremental runs |

See [Training 18 notes](/training-notes-site/notes/training-18/) ("AWS Glue", "How Glue Charges", "Glue Crawler" and "Glue Data Catalog") and [Training 20 notes](/training-notes-site/notes/training-20/) ("AWS Glue: Bronze → Silver").

**Say it out loud:** "Glue is AWS's serverless ETL service: I write Spark jobs and Glue provides the compute only while they run, billed per DPU-hour. It also includes the Data Catalog and crawlers, which Athena and Redshift Spectrum use to find the tables."

---

**Q. What is the difference between a DataFrame and a DynamicFrame**

**A. (Class answer)**

A DataFrame is a SQL-like structured data type which is available in Spark. It contains rows, columns, and a schema, like all structured data. One restriction on it is that all rows must have the exact same number of columns.

A DynamicFrame is similar to a DataFrame, but it has a more flexible schema that allows for a dynamic number of columns for each row. This is done so that it can be optimized to work with semi-structured data in JSON format, which is the most common data format on the web.

**Expanded:** The answer is broadly right. Precision on how a DynamicFrame works: a Spark DataFrame needs **one schema up front**. A DynamicFrame is a collection of **self-describing records** (DynamicRecords), each carrying its own structure, and the schema is computed only when needed. When the same field has different types in different records (a string in some files, a number in others), it becomes a **choice type**, which you settle with `resolveChoice()`. DynamicFrames also add Glue-specific features: direct reading through the Data Catalog, **job bookmarks** and transforms like `ApplyMapping`, `Relationalize` (flattens nested JSON) and `DropNullFields`.

```python
dyf = glueContext.create_dynamic_frame.from_catalog(database="bronze", table_name="trips")
dyf = dyf.resolveChoice(specs=[("price", "cast:double")])
df = dyf.toDF()                                   # to Spark DataFrame
dyf2 = DynamicFrame.fromDF(df, glueContext, "dyf2")
```

Common practice: read and write with DynamicFrames, and do the main transformations as DataFrames.

See [Training 18 notes](/training-notes-site/notes/training-18/) ("AWS Glue").

**Say it out loud:** "A DataFrame needs one fixed schema. A Glue DynamicFrame's records are self-describing, so it tolerates messy, inconsistent schemas and records type conflicts as choice types that I resolve with `resolveChoice`. I usually read with DynamicFrames, convert to a DataFrame for the transformations, and convert back to write."

---

**Q. What is a serverless service?**

**A. (Class answer)**

Any cloud service that can be used without provisioning a virtual machine can be called serverless. Examples include AWS Lambda, AWS Glue, and AWS S3.

Cloud services that require provisioning a virtual machine are NOT serverless. Examples include EC2, EMR, and RDS.

Some services, including Redshift, have the option to be used either serverlessly or in a server-based way.

**Expanded:** The teacher's answer is correct. A sharper definition: serverless means **you don't provision or manage servers or clusters, capacity scales automatically, and you pay for use** (requests, data scanned, compute-seconds), often down to zero when idle. Servers still exist; AWS runs them. The examples are right, and the "both modes" list includes Redshift Serverless, EMR Serverless, Aurora Serverless, MSK Serverless and Kinesis Data Streams on-demand mode.

| Serverless | Server-based (you choose instances) |
|---|---|
| Lambda, Glue, S3, Athena, DynamoDB, Step Functions, EventBridge, SQS/SNS, Redshift/EMR Serverless | EC2, EMR on EC2, RDS, provisioned Redshift, MSK provisioned |

See [Training 18 notes](/training-notes-site/notes/training-18/) ("Serverless").

**Say it out loud:** "Serverless means I don't manage servers or capacity. The service scales automatically and I pay per use, like Lambda, Glue, Athena or S3. EC2, EMR on EC2 and RDS are server-based because I pick and manage the instances."

---

**Q. What is AWS Athena?**

**A. (Class answer)**

Athena is a serverless SQL query engine that works with AWS S3.

**Expanded:** The teacher's answer is correct. Details: Athena is a **serverless, interactive SQL engine based on Trino/Presto** that queries files in S3 (Parquet, ORC, JSON, CSV, Iceberg) using tables in the **Glue Data Catalog**. You pay **per TB scanned** ($5 per TB in most regions, verify current pricing), so partitioning, compression and columnar formats directly cut cost. It can also query other sources through **federated query** connectors, and run Spark notebooks.

See [Training 18 notes](/training-notes-site/notes/training-18/) ("Athena" and "Athena: Extra Points from Class").

**Say it out loud:** "Athena is a serverless SQL engine, based on Trino, that queries files in S3 through the Glue Data Catalog and charges per terabyte scanned. So I store data as partitioned Parquet to keep queries fast and cheap."

---

**Q. What is AWS Lambda?**

**A. (Class answer)**

Lambda is a serverless service in AWS that allows us to run function code without provisioning infrastructure.

**Expanded:** The teacher's answer is correct. Interview details: Lambda runs your function **in response to events** (S3 uploads, EventBridge schedules, API Gateway requests, SQS messages, Kinesis records), scales automatically, and bills per request and per millisecond of run time. Limits that shape design: **15-minute maximum** run time, up to **10 GB memory** (CPU scales with memory), and up to 10 GB of temporary `/tmp` storage. So it suits small, event-driven tasks (triggering a Glue job, light transforms, API ingestion), not heavy ETL. It should be **idempotent**, because asynchronous events can be retried or delivered more than once.

See [Training 18 notes](/training-notes-site/notes/training-18/) ("AWS Lambda") and [Training 20 notes](/training-notes-site/notes/training-20/) ("Lambda: Triggers, Retries and Idempotency").

**Say it out loud:** "Lambda runs code in response to events without servers, scales automatically and bills per millisecond. It's limited to 15 minutes per run, so I use it for lightweight event-driven work like API ingestion or kicking off a Glue job, and I make it idempotent because events can be retried."

---

**Q. What are some languages that you can use with Lambda?**

**A. (Class answer)**

Available languages include Python, Java, JavaScript, Ruby, and Go. Other JVM languages such as Scala can be used by using the Java runtime environment, but this requires additional configuration.

**Expanded:**

**Correction:** The list is missing **.NET (C#)**, and Go is no longer a managed runtime. The `go1.x` runtime was retired at the end of 2023. Go now runs on the **OS-only runtime** (`provided.al2023`), compiled to a binary named `bootstrap`. Current managed runtimes: **Python, Node.js (JavaScript/TypeScript), Java, .NET and Ruby**. Any other language (Go, Rust, C++) runs through a **custom runtime** or a **container image**. Scala works by compiling to a JAR for the Java runtime.

**Say it out loud:** "Lambda has managed runtimes for Python, Node.js, Java, .NET and Ruby. Anything else, like Go or Rust, runs on the OS-only custom runtime or as a container image. I've used Python."

---

**Q. How do you include dependencies in Lambda?**

**A. (Class answer)**

To include dependencies in Lambda, we have to package them in a zip file along with our function code, then put the file on S3 and tell Lambda its location.

To do this, create a virtual environment in Python and install all needed dependencies. Then go to the installation directory of the virtual environment, copy the dependencies to a working directory with your function code, and zip the files together. After that, copy them to the S3 bucket of your choice, then pass the location to Lambda.

**Expanded:**

**Correction:** A zip on S3 is only one of several methods, and you don't need S3 at all for small packages.

| Method | Limit | When |
|---|---|---|
| Zip uploaded directly | 50 MB zipped | Small packages |
| Zip via S3 | 250 MB unzipped (function + layers) | Bigger zips |
| **Lambda layers** | Up to 5 per function, counted in the 250 MB | Shared libraries reused across functions (e.g. the AWS SDK for pandas layer) |
| **Container image** (from ECR) | Up to **10 GB** | Large or native dependencies |

Build tip: install packages for the Lambda platform, not your Mac, for example `pip install -r requirements.txt -t package/ --platform manylinux2014_x86_64 --only-binary=:all:`, or build inside Docker. Tools like AWS SAM, the Serverless Framework or Terraform automate the packaging.

See [Training 18 notes](/training-notes-site/notes/training-18/) ("AWS Lambda").

**Say it out loud:** "For small functions I zip the code with its dependencies, built for Linux, and upload it directly or via S3. For shared libraries I use Lambda layers, and for large dependencies like pandas plus native libraries I package the function as a container image, which can be up to 10 GB."

---

**Q. What are AWS Step Functions?**

**A. (Class answer)**

Step functions are a serverless service for orchestration. They are capable of doing scheduling, but their primary purpose is to chain together a series of Lambda functions in order to create serverless algorithms or full serverless applications.

**Expanded:**

**Correction:** Chaining Lambda functions is no longer the primary purpose. Step Functions is a general **serverless workflow orchestrator** that integrates directly with **over 200 AWS services** (through optimized integrations and AWS SDK integrations): it can start a **Glue job and wait for it** (`.sync`), run EMR or EMR Serverless jobs, ECS tasks, Redshift Data API queries, SageMaker jobs and more, with no Lambda in between. It doesn't schedule by itself; **EventBridge Scheduler** starts it on a schedule.

Workflows are **state machines** written in Amazon States Language (JSON), or drawn in Workflow Studio. Key states: `Task`, `Choice`, `Parallel`, `Map` (loop over items), `Wait`, with built-in `Retry` and `Catch`. Standard workflows run up to a year with exactly-once execution; Express workflows are for high-volume, short runs.

See [Training 23 notes](/training-notes-site/notes/training-23/) ("AWS Step Functions") and [Training 24 notes](/training-notes-site/notes/training-24/) ("First controlled Step Functions run" and "Scheduling it: EventBridge Scheduler in Terraform").

**Say it out loud:** "Step Functions is AWS's serverless workflow orchestrator. I define a state machine where each step calls a service, like running a Glue job and waiting for it, then running Redshift SQL, with retries and error handling built in, and EventBridge Scheduler triggers it."

---

**Q. What is AWS S3?**

**A. (Class answer)**

S3 is a serverless object store on AWS. You can use it to store files for access by other programs. If you store data in it, you can query that data using Athena.

**Expanded:** The teacher's answer is correct. Interview details:
- **Object storage**: data is stored as objects (file + metadata) under keys in **buckets**. There are no real folders, only key prefixes.
- **Durability** of 99.999999999% (11 nines), and strong read-after-write consistency since December 2020.
- **Storage classes** for cost: Standard, Intelligent-Tiering, Standard-IA, Glacier tiers, with **lifecycle rules** to move or delete data.
- Security: private by default, Block Public Access, bucket policies + IAM, encryption (SSE-S3 by default, SSE-KMS), versioning.
- It is the foundation of AWS data lakes, queried by Athena, Glue, EMR, Redshift Spectrum.

See [Training 18 notes](/training-notes-site/notes/training-18/) ("S3 (Simple Storage Service)", "The Discrete Unit in S3: Bucket vs Object" and "S3 Versioning, Lifecycle and Security").

**Say it out loud:** "S3 is AWS's serverless object storage: objects under keys in buckets, extremely durable and cheap. It's the base of an AWS data lake, with lifecycle rules for cost and IAM, bucket policies and encryption for security."

---

**Q. What is used for security in AWS?**

**A. (Class answer)**

There are multiple AWS services used for security.

The most important is IAM, which is used for Role-Based Access Control (RBAC). IAM allows you to define multiple users within a single AWS account and control which services on that account they have access to.

Another AWS service used for security is VPC, or Virtual Private Cloud. This enables you to create a separate environment only for the cloud services that you are using, which makes it more difficult for bad actors to access your services.

Another AWS service with security implications is Cloudtrail. If you are using Cloudtrail, you are able to access a log of what each user of your AWS account was doing at what time. So, if you discover something wrong, you can use Cloudtrail to determine which user it was and what they did.

**Expanded:** The answer is right but incomplete. Two precisions: IAM is **policy-based** access control (JSON policies attached to users, groups and **roles**), which supports role-based and attribute-based models. Best practice is **roles with temporary credentials** for services and people (not long-lived access keys) and **least privilege**. And a VPC is a private network you define, with subnets, security groups and network ACLs.

| Area | Services |
|---|---|
| Identity and access | IAM (users, roles, policies), IAM Identity Center (SSO), Lake Formation (table/column-level data permissions) |
| Network | VPC, security groups, NACLs, private subnets, VPC endpoints (reach S3 without the internet) |
| Encryption and secrets | KMS (keys), Secrets Manager, Parameter Store, encryption at rest and TLS in transit |
| Audit and detection | CloudTrail (API activity), Config (resource change history), GuardDuty (threat detection), Security Hub |
| Edge | WAF, Shield |

See [Training 18 notes](/training-notes-site/notes/training-18/) ("IAM (Identity and Access Management)" and "VPC (Virtual Private Cloud)") and [Training 29 notes](/training-notes-site/notes/training-29/) ("Security & governance in interviews").

**Say it out loud:** "The core is IAM with least-privilege roles and policies, plus network isolation with a VPC, private subnets and security groups, encryption with KMS, credentials in Secrets Manager, and auditing with CloudTrail. For data lakes, Lake Formation adds table- and column-level permissions."

---

**Q. How do you do CI/CD on AWS?**

**A. (Class answer)**

CI/CD can be implemented using AWS CodePipeline.

**Expanded:** CodePipeline is one correct answer. The AWS-native set is **CodePipeline** (orchestrates the pipeline) + **CodeBuild** (runs builds and tests) + **CodeDeploy** (deploys to EC2, ECS, Lambda). In practice, many teams use **GitHub Actions** or GitLab CI with AWS through **OIDC role assumption** (no stored access keys), deploying with Terraform, CloudFormation/CDK or AWS SAM. For a data pipeline: run tests on each pull request, then on merge upload job scripts to S3, update Glue jobs or Step Functions through Terraform, and promote across dev and prod accounts.

**Say it out loud:** "AWS-native, that's CodePipeline with CodeBuild for builds and tests and CodeDeploy or CloudFormation for deployment. Often teams use GitHub Actions that assume an AWS role through OIDC and run Terraform to deploy Glue jobs and Step Functions."

---

**Q. What is AWS CodePipeline?**

**A. (Class answer)**

CodePipeline is a fully managed CI/CD service on AWS. It can listen for changes to repositories on Github or AWS CodeCommit (AWS's internal Git repo hosting service), then do automated testing and deployment.

**Expanded:** The answer is correct, with one update: **AWS CodeCommit was closed to new customers in July 2024**, so new pipelines usually take source from **GitHub, GitLab or Bitbucket** (through CodeConnections) or from S3. A pipeline is made of **stages** (Source → Build → Test → Deploy) with **actions** in each, typically CodeBuild for build and test, a **manual approval** action before production, and deploy actions for CloudFormation, ECS, Lambda or S3.

**Say it out loud:** "CodePipeline is AWS's managed CI/CD orchestrator. It watches a repo, usually GitHub now that CodeCommit is closed to new customers, and runs stages for build and test in CodeBuild, a manual approval, and deployment."

---

**Q. How do you migrate data to AWS?**

**A. (Class answer)**

Data migration to AWS can be done with any migration tool that can access cloud services, but the usual tool to use is AWS Data Migration Service, or DMS.

**Expanded:** DMS is the right answer for databases (note the name, see the next question). The full answer depends on what you're moving and how much:

| Data | Tool |
|---|---|
| Databases (one-time or ongoing CDC) | **AWS DMS**, with the **Schema Conversion Tool** (or DMS Schema Conversion) for different engines |
| Files over the network | **AWS DataSync**, `aws s3 sync`/`cp`, Transfer Family (SFTP) |
| Very large volumes (tens of TB to PB) or poor bandwidth | **AWS Snowball** devices shipped physically |
| Hadoop/HDFS | `distcp` to S3, or DataSync |
| Dedicated network link | Direct Connect |
| Streaming sources | Kinesis, MSK, Debezium |

A good answer also covers the process: assess, migrate schema, full load, ongoing CDC until cutover, validate (row counts, checksums), then switch over.

See [Training 24 notes](/training-notes-site/notes/training-24/) ("CDC and AWS DMS") and [Training 29 notes](/training-notes-site/notes/training-29/) ("Migration projects").

**Say it out loud:** "For databases I'd use DMS for a full load plus ongoing CDC until cutover, with the schema conversion tool if the engine changes. For files, DataSync or S3 sync, and for petabytes, Snowball. Then I validate row counts before switching over."

---

**Q. What is AWS DMS?**

**A. (Class answer)**

AWS DMS is their Data Migration Service, used to move data from one database to another. It can connect to databases both on-prem and in the cloud and is capable of migrating that data between either AWS or Non-AWS databases.

**Expanded:**

**Correction:** The name is **AWS Database Migration Service**, not "Data Migration Service". The description is otherwise right. How it works: a **replication instance** (or DMS Serverless) connects a **source endpoint** to a **target endpoint** and runs a **task** that can be **full load**, **CDC only** or **full load + CDC**. CDC reads the source's transaction log, so the source can stay live during migration. Targets include RDS/Aurora, Redshift, S3 (as Parquet or CSV), DynamoDB, Kinesis and Kafka. Engine changes (Oracle to Postgres) also need **schema conversion** (SCT or DMS Schema Conversion), since DMS moves data, not stored procedures.

See [Training 24 notes](/training-notes-site/notes/training-24/) ("CDC and AWS DMS").

**Say it out loud:** "DMS is AWS Database Migration Service. It connects a source and target endpoint and runs a full load, ongoing CDC from the transaction log, or both, so the source stays live during the migration. For a different target engine I'd add the schema conversion tool."

---

**Q. What is AWS RDS? What version of SQL did you use with it?**

**A. (Class answer)**

AWS RDS stands for Relational Database Service, and it's essentially an EC2-based Database server which can run most major SQL distributions.

Available distributions include MySQL, MariaDB, Postgres, Microsoft SQL Server, and Oracle, among others.

**Expanded:** The answer is correct, with precision: RDS is a **managed** relational database service. AWS handles provisioning, OS and engine patching, automated backups, point-in-time recovery, **Multi-AZ** failover and **read replicas**. Instances run on EC2 underneath, but you can't log into the server. Engines: **PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, Db2**, plus **Aurora** (AWS's MySQL- and Postgres-compatible engine with distributed storage). RDS is **OLTP**, for application databases, not the warehouse. For the second part of the question, answer with the engine you used, for example "PostgreSQL on RDS as the source database for our pipeline".

See [Training 18 notes](/training-notes-site/notes/training-18/) ("RDS (Relational Database Service)" and "RDS: Extra Points from Class").

**Say it out loud:** "RDS is AWS's managed relational database: it runs PostgreSQL, MySQL, SQL Server, Oracle and others, and handles backups, patching, Multi-AZ failover and read replicas. I used PostgreSQL on RDS as a transactional source for the pipeline."

---

**Q. What is EC2?**

**A. (Class answer)**

EC2 is a service for provisioning a virtual server using AWS. This server can be used exactly the same way as an on-premises server with a server operating system installed on it, although this means that only the command line interface is available.

EC2 can be used for many purposes, including hosting websites, hosting on premises applications, and for general purpose development and execution of code.

**Expanded:**

**Correction:** "Only the command line interface is available" is wrong. Linux instances are usually managed over **SSH** (or Systems Manager Session Manager), but **Windows Server** instances come with a full desktop over **RDP**, and Linux can run a desktop too.

EC2 (Elastic Compute Cloud) provides **virtual servers (instances)** that you configure and manage yourself. Key concepts: **AMI** (the machine image), **instance types** (families such as general purpose, compute-, memory- and storage-optimized), **EBS** volumes, **security groups**, **key pairs**, and pricing models (**On-Demand, Reserved/Savings Plans, Spot** at up to about 90% off but can be interrupted). Spark task nodes on Spot instances are a common cost saving.

See [Training 18 notes](/training-notes-site/notes/training-18/) ("EC2 (Elastic Compute Cloud)" and "EBS (Elastic Block Store)") and [Training 20 notes](/training-notes-site/notes/training-20/) ("EC2 Hands-On Basics").

**Say it out loud:** "EC2 is AWS's virtual server service: you pick an AMI and an instance type, attach EBS storage and security groups, and manage the server yourself. You can save money with Spot or Savings Plans. It's the compute under services like EMR."

---

**Q. What is Cloudformation?**

**A. (Class answer)**

Cloudformation is the Infrastructure As Code (IAC) tool for the AWS Cloud. It allows us to build templates for all the services that we need using either JSON or YAML format, and it allows us to visualize what the environment will look like based on the template before deploying it. When it is deployed, all the services specified in the template will be provisioned and made available for use.

**Expanded:** The answer is correct. Precision: you can visualize a template in **Infrastructure Composer** (formerly Application Composer) and preview exactly what will change with a **change set** before deploying. See the CloudFormation questions in the Infrastructure as Code section above for stacks, rollback, drift detection and a sample template.

**Say it out loud:** "CloudFormation is AWS's infrastructure-as-code service: a YAML or JSON template defines the resources, AWS deploys them as a stack, and change sets preview updates before they're applied."

---

**Q. What is Redshift?**

**A. (Class answer)**

Redshift is the Data Warehouse platform available on AWS. Redshift is available in both server-based and serverless modes. When server-based, we provision a Redshift cluster.

**Expanded:** The answer is correct. Interview depth:
- **Columnar, MPP** (massively parallel) data warehouse based on PostgreSQL syntax. A provisioned cluster has a **leader node** (plans queries) and **compute nodes** (store and process slices of data).
- **RA3** node types separate compute from storage (data in managed storage on S3), and **Redshift Serverless** bills per RPU-second.
- Table design: **distribution style** (`KEY`, `EVEN`, `ALL`, `AUTO`) controls how rows spread across nodes, so joins avoid data movement. **Sort keys** let queries skip blocks.
- Loading: **`COPY` from S3** in parallel (not row-by-row `INSERT`), `UNLOAD` to export.
- Extras: **Spectrum** (query S3), materialized views, data sharing, zero-ETL integrations.

See [Training 18 notes](/training-notes-site/notes/training-18/) ("AWS Redshift" and "Provisioned Redshift vs Redshift Serverless"), [Training 20 notes](/training-notes-site/notes/training-20/) ("Redshift Serverless: the Gold Layer") and [Training 4 notes](/training-notes-site/notes/training-4/) ("Redshift (Columnar Storage)").

**Say it out loud:** "Redshift is AWS's columnar, massively parallel data warehouse, provisioned or serverless. I load it with `COPY` from S3, and I design tables with distribution keys so joins don't move data and sort keys so queries skip blocks."

---

**Q. What is Kinesis**

**A. (Class answer)**

Kinesis is a serverless streaming service on AWS. It's similar to Kafka, but in place of a broker we instead have a serverless Kinesis stream. Producers and consumers can be written for Kinesis, but we can also use Kinesis Firehose in place of a consumer. Firehose is a connector program that allows us to move data directly from Kinesis into a data storage location.

**Expanded:** The answer is broadly right. Precision: "Kinesis" is a family of services:

| Service | Role |
|---|---|
| **Kinesis Data Streams** | Kafka-like durable stream. Data is split across **shards** (each about 1 MB/s or 1,000 records/s in, 2 MB/s out). **Provisioned** (you choose shards) or **on-demand** (auto-scaling) capacity. Retention 24 hours by default, up to 365 days |
| **Amazon Data Firehose** (formerly Kinesis Data Firehose) | Fully managed delivery to S3, Redshift, OpenSearch, Snowflake, HTTP endpoints, with buffering, format conversion and optional Lambda transforms |
| Managed Service for Apache Flink (formerly Kinesis Data Analytics) | Stream processing with Flink |
| Kinesis Video Streams | Video ingestion |

Shards play the role of Kafka partitions: records with the same **partition key** go to the same shard and stay in order.

See [Training 12 notes](/training-notes-site/notes/training-12/) ("AWS Kinesis"), [Training 22 notes](/training-notes-site/notes/training-22/) ("MSK vs Kinesis") and [Training 26 notes](/training-notes-site/notes/training-26/) ("Streaming Ingestion: Lambda → Kinesis").

**Say it out loud:** "Kinesis Data Streams is AWS's managed streaming service, similar to Kafka, with shards instead of partitions and on-demand or provisioned capacity. Firehose is the no-code delivery service that loads a stream into S3, Redshift or OpenSearch."

---

**Q. What is MSK?**

**A. (Class answer)**

MSK stands for Managed Service for Apache Kafka, and is AWS's version of Kafka. It is hosted on a cluster of EC2 instances and has many configuration options managed by AWS, which reduces the workload for the team using it. It is the premier option if you insist on using Kafka rather than Kinesis on the AWS cloud.

**Expanded:**

**Correction:** MSK stands for **Amazon Managed Streaming for Apache Kafka**, not "Managed Service for Apache Kafka". (The similar name "Managed Service for Apache **Flink**" is a different service.) MSK runs real open-source Kafka: AWS manages the brokers (and the controller layer), patching and broker replacement, while you keep normal Kafka APIs, tools and Kafka Connect (MSK Connect). Options: **MSK provisioned** (you choose broker instance types and storage) and **MSK Serverless** (capacity managed for you). Choose it over Kinesis when you need Kafka compatibility (existing clients, Kafka Connect, Kafka Streams, longer retention, finer control) or a multi-cloud setup.

See [Training 12 notes](/training-notes-site/notes/training-12/) ("AWS MSK (Managed Streaming for Apache Kafka)") and [Training 22 notes](/training-notes-site/notes/training-22/) ("MSK vs Kinesis").

**Say it out loud:** "MSK is Amazon Managed Streaming for Apache Kafka: real Kafka where AWS runs the brokers, provisioned or serverless. I'd pick it over Kinesis when we need Kafka compatibility, like existing Kafka clients, Kafka Connect or Kafka Streams."

---

**Q. What is SNS?**

**A. (Class answer)**

SNS, which stands for Simple Notification Service, is a system for providing notifications to users when certain events happen in your AWS environment. These can come in the form of email, SMS texts, or push notifications on your phone.

**Expanded:**

**Correction:** SNS is more than notifications to people. It is a **pub/sub messaging service**: publishers send a message to a **topic**, and SNS **pushes** a copy to every **subscriber**. Subscribers can be **SQS queues, Lambda functions, HTTP endpoints, Firehose**, as well as email, SMS and mobile push. The classic data pattern is **fan-out**: SNS topic → several SQS queues, so one event feeds several independent consumers. SNS doesn't store messages for replay; if you need durability per consumer, put SQS behind it.

| | SNS | SQS |
|---|---|---|
| Model | Pub/sub: push to all subscribers | Queue: consumers poll, each message processed once |
| Retention | None (delivered or retried) | Up to 14 days |

**Say it out loud:** "SNS is AWS's pub/sub service: you publish to a topic and it pushes a copy to every subscriber, like SQS queues, Lambda functions or email. The common pattern is fan-out from one SNS topic to several SQS queues."

---

**Q. What is SQS?**

**A. (Class answer)**

SQS, which stands for Simple Queue Service, is a system for implementing basic streaming capability in your AWS environment. We can configure a source and a destination for streaming data and use it for that purpose. However, it is not scalable - if you plan to stream hundreds or thousands of messages per second, it is better to use a scalable streaming service such as Kafka or Kinesis.

**Expanded:**

**Correction:** SQS is **highly scalable**. Standard queues support a nearly unlimited number of messages per second, and FIFO queues support up to 300 messages per second per API action (3,000 with batching, and much more in high-throughput mode). "Hundreds or thousands of messages per second" is easy for SQS. The real difference from Kafka/Kinesis is the **model**, not scale:

| | SQS | Kafka / Kinesis |
|---|---|---|
| Model | Message **queue**: each message processed by one consumer, then deleted | Replayable **log**: messages stay until retention expires |
| Multiple independent consumers | No (use SNS fan-out to several queues) | Yes, each consumer group reads everything |
| Replay | No | Yes, by offset or timestamp |
| Ordering | Standard: best effort. FIFO: per message group | Per partition / shard |
| Retention | Up to 14 days | Kafka: configurable. Kinesis: up to 365 days |

Typical uses: decoupling services, work queues, buffering events for Lambda, with a **dead-letter queue** for failures.

See [Training 12 notes](/training-notes-site/notes/training-12/) ("AWS SQS (Simple Queue Service)").

**Say it out loud:** "SQS is a fully managed message queue, and it scales to very high throughput. The difference from Kafka or Kinesis is that a message is consumed once and deleted, with no replay and no independent consumer groups, so I use SQS for work queues and decoupling, and Kafka or Kinesis when several consumers need to read or replay the stream."

---

**Q. What is DynamoDB**

**A. (Class answer)**

DynamoDB is a serverless NoSQL database on AWS. It's a table-based NoSQL database, which means that it is similar to a structured database because it has rows, columns, and a schema. It is NoSQL because it has the ability to have rows with an inconsistent number of columns in a single dataset, which makes it easier to use with semi-structured data.

There are also ways of organizing the data which are not available in regular SQL databases, notably the Global Secondary Index, or GSI. A GSI will allow you to sort the data and query it based on a metric other than the primary key.

Dynamo is highly regarded for its speed, and is currently one of the most performant databases for serving applications.

**Expanded:**

**Correction:** DynamoDB is not "similar to a structured database with rows, columns and a schema". It is a **key-value and document** NoSQL database. Tables contain **items** made of **attributes**, and only the **primary key** is fixed: a **partition key**, optionally plus a **sort key**. Every other attribute can differ from item to item (no schema). Also, a GSI doesn't "sort the data": a **Global Secondary Index** gives you an **alternate partition key (and optional sort key)**, so you can query efficiently by attributes other than the table's primary key. (A Local Secondary Index keeps the same partition key with a different sort key.)

Key facts:
- Single-digit-millisecond reads and writes at any scale. Serverless, with **on-demand** or **provisioned** capacity.
- Design starts from **access patterns**: you query by key, and scans are expensive. No joins.
- Reads are **eventually consistent** by default; strongly consistent reads are optional (not available on GSIs).
- Extras: **DynamoDB Streams** (CDC), TTL, transactions, global tables.

See [Training 18 notes](/training-notes-site/notes/training-18/) ("DynamoDB") and [Training 13 notes](/training-notes-site/notes/training-13/) ("GSI (Global Secondary Index)").

**Say it out loud:** "DynamoDB is AWS's serverless key-value and document database with millisecond latency at any scale. Items only need the partition key, and optionally a sort key, so I design the keys around the access patterns, and I add global secondary indexes to query by other attributes."

---

**Q. What is MWAA?**

**A. (Class answer)**

MWAA stands for Managed Workflows for Apache Airflow, and is essentially Apache Airflow running on the AWS cloud.

**Expanded:** The answer is correct. Details: **Amazon Managed Workflows for Apache Airflow** runs real Airflow, with AWS managing the scheduler, workers, web server and metadata database. You put your **DAG files, `requirements.txt` and plugins in an S3 bucket**, and MWAA picks them up. It integrates with IAM, CloudWatch logs and a VPC. Trade-off vs Step Functions: Airflow is Python-defined, portable and has hundreds of operators, while Step Functions is serverless and pay-per-transition with deep AWS integration.

See [Training 26 notes](/training-notes-site/notes/training-26/) ("What is MWAA, and Airflow vs Step Functions?") and [Training 23 notes](/training-notes-site/notes/training-23/) ("Orchestration").

**Say it out loud:** "MWAA is AWS's managed Apache Airflow. I upload DAGs and requirements to S3, and AWS runs the scheduler, workers and web UI. I'd choose it over Step Functions when the team wants Python-defined, portable Airflow DAGs."

---

**Q. What is Redshift Spectrum**

**A. (Class answer)**

Redshift Spectrum is a query engine for AWS Redshift. It can also be used instead of Athena to query data on S3. The advantage of Spectrum over Athena is that while Athena is serverless and has limitations on how much compute power can be provisioned to it, Spectrum is connected to your Redshift cluster and you can give it as much processing power as you have available on that cluster.

**Expanded:**

**Correction:** Spectrum's processing power does **not** come from your Redshift cluster. Spectrum runs on a **separate, AWS-managed fleet** of Spectrum nodes outside the cluster that scans the S3 files, filters and aggregates them, and sends results back to the cluster to finish the query (joins with local tables). It scales automatically and is billed **per TB scanned** (like Athena), not by cluster size.

How it works: create an **external schema** pointing at a Glue Data Catalog database, then query the external tables (S3 files) with normal SQL, and join them to local Redshift tables.

```sql
CREATE EXTERNAL SCHEMA lake
FROM DATA CATALOG DATABASE 'silver'
IAM_ROLE 'arn:aws:iam::<account-id>:role/<spectrum-role>';

SELECT d.station_name, SUM(f.trips)
FROM lake.trips f JOIN public.dim_station d USING (station_id)
GROUP BY 1;
```

| | Athena | Redshift Spectrum |
|---|---|---|
| Needs a Redshift cluster/workgroup | No | Yes |
| Best for | Ad hoc SQL on the lake | Joining lake data with warehouse tables in one query |
| Billing | Per TB scanned | Per TB scanned (plus your Redshift cost) |

See [Training 18 notes](/training-notes-site/notes/training-18/) ("AWS Redshift").

**Say it out loud:** "Spectrum lets Redshift query files in S3 through external tables in the Glue catalog. The scanning runs on a separate AWS-managed fleet, not my cluster, and is billed per terabyte scanned, so it's ideal for joining lake data with warehouse tables in one query."

---

**Q. What is EventBridge**

**A. (Class answer)**

EventBridge is a service for generating events which are available to your entire AWS environment. They can be used to trigger any service which has an event listener, including Lambda and SNS.

**Expanded:** Precision: EventBridge doesn't so much **generate** events as **route** them. It is a serverless **event bus**: events come from AWS services (an S3 object created, a Glue job state change), SaaS partners or your own applications (`PutEvents`), and **rules** match events by pattern and send them to **targets** (Lambda, Step Functions, SQS, SNS, Kinesis, Glue workflows and more). **EventBridge Scheduler** runs one-time or recurring schedules (cron or rate expressions) that start targets, which is the usual way to schedule a Step Functions pipeline. EventBridge Pipes connects a source to a target with optional filtering and enrichment.

See [Training 18 notes](/training-notes-site/notes/training-18/) ("EventBridge") and [Training 24 notes](/training-notes-site/notes/training-24/) ("Scheduling it: EventBridge Scheduler in Terraform").

**Say it out loud:** "EventBridge is AWS's serverless event bus. Rules match events from AWS services or my apps, like an S3 upload or a Glue job finishing, and route them to targets like Lambda or Step Functions. EventBridge Scheduler is how I run pipelines on a cron schedule."

---

**Q. What is Amazon OpenSearch**

**A. (Class answer)**

AWS OpenSearch is basically ElasticSearch running on the AWS Cloud.

**Expanded:** Precision: **OpenSearch is not Elasticsearch**. It is an open-source **fork of Elasticsearch 7.10 and Kibana** (OpenSearch Dashboards), created by AWS in 2021 after Elastic changed Elasticsearch's license. **Amazon OpenSearch Service** (renamed from Amazon Elasticsearch Service) is the managed service for it, with a provisioned option and **OpenSearch Serverless**. Uses: full-text search, log analytics and dashboards, and vector search for AI/RAG. It is usually fed by Firehose, Logstash, or Lambda.

See [Training 29 notes](/training-notes-site/notes/training-29/) ("Elasticsearch / AWS OpenSearch").

**Say it out loud:** "Amazon OpenSearch Service is AWS's managed search and log-analytics service. It runs OpenSearch, the open-source fork of Elasticsearch and Kibana that AWS made after Elastic's license change, and it's used for search, log analytics and vector search."

---

**Q. What is Kinesis Firehose**

**A. (Class answer)**

Firehose is a connector program that allows us to move data directly from Kinesis into a data storage location.

**Expanded:** The answer is correct. Details: now called **Amazon Data Firehose**. It is fully managed delivery: it **buffers** incoming records (by size or time), can transform them with a Lambda, **convert JSON to Parquet/ORC** using a Glue table schema, compress them, and deliver to **S3, Redshift (via S3 + `COPY`), OpenSearch, Snowflake, Splunk, Apache Iceberg tables or HTTP endpoints**. Sources: direct PUT from producers, a Kinesis Data Stream or MSK. It's near-real-time (buffering adds seconds to minutes) and has no replay; that's what the upstream stream is for.

See [Training 12 notes](/training-notes-site/notes/training-12/) ("AWS Kinesis").

**Say it out loud:** "Firehose, now Amazon Data Firehose, is a no-code delivery service: it buffers streaming records, can transform them and convert them to Parquet, and loads them into S3, Redshift, OpenSearch or Snowflake. It's near-real-time because of the buffering."

---

**Q. What is AWS Cloudwatch**

**A. (Class answer)**

Cloudwatch is a monitoring tool for the AWS environment that can provide performance metrics for any AWS services being used. It also has the feature of Cloudwatch Logs, which provides logging for AWS services.

**Expanded:** The answer is correct. More: CloudWatch has **metrics** (built-in for every AWS service plus custom metrics), **alarms** (trigger SNS notifications or auto-scaling when a metric crosses a threshold), **dashboards**, **CloudWatch Logs** (log groups from Lambda, Glue, EMR, your apps) with **Logs Insights** for querying them, and **EventBridge** integration. For a pipeline: alarms on Glue job failures or Lambda errors, a dashboard of rows loaded, and logs for debugging.

See [Training 20 notes](/training-notes-site/notes/training-20/) ("Access Setup").

**Say it out loud:** "CloudWatch is AWS's monitoring service: metrics and alarms, dashboards, and CloudWatch Logs with Logs Insights for searching logs. I use it to alert through SNS when a Glue job or Lambda fails and to debug from the logs."

---

**Q. What is AWS Cloudtrail**

**A. (Class answer)**

Cloudtrail is another logging service in AWS, slightly different from Cloudwatch Logs in that it tracks user activity on the AWS cluster and can report on who did what at which time.

**Expanded:** The answer is right, with two precisions: it tracks activity in the AWS **account** (not "cluster"), and it records **API calls**: who (IAM user or role), what action, when, from which IP, on which resource, whether through the console, CLI, SDK or another AWS service. Management events are recorded by default (90 days of event history). A **trail** stores logs long-term in S3, and data events (like S3 object reads) can be enabled for an extra cost. Use: security audits, compliance and investigating "who deleted this table?".

| | CloudWatch | CloudTrail |
|---|---|---|
| Answers | "How is it performing? What did my code log?" | "Who did what, when?" |
| Data | Metrics, logs, alarms | API call records |

See [Training 20 notes](/training-notes-site/notes/training-20/) ("Access Setup").

**Say it out loud:** "CloudTrail records every API call in the AWS account, who made it, when, from where and on which resource, so it's the audit log for security and compliance. CloudWatch is for performance metrics and application logs."

---


## Azure


**Q. What is Azure Data Factory**

**A. (Class answer)** *(no answer given)*

**Expanded:** Azure Data Factory (ADF) is Azure's managed **data integration and orchestration** service, roughly AWS Glue + Step Functions combined.

| Concept | Meaning |
|---|---|
| Pipeline | A workflow of activities |
| Activity | One step: **Copy** data, run a Databricks notebook, a stored procedure, a Data Flow, etc. |
| Linked service | Connection details for a data store or compute (like a connection string) |
| Dataset | A pointer to specific data inside a linked service (a table, a folder) |
| Integration runtime | The compute that runs activities: Azure (managed), **self-hosted** (reaches on-prem sources), or Azure-SSIS |
| Trigger | Schedule, tumbling window or event (file arrival) |
| Mapping Data Flows | Visual, Spark-based transformations |

It has 90+ connectors and is largely low-code. The same engine lives inside Synapse (Synapse pipelines) and Microsoft Fabric (Data Factory in Fabric).

See [Training 15 notes](/training-notes-site/notes/training-15/) ("Cloud Providers: AWS, Azure, GCP") and [Training 31 notes](/training-notes-site/notes/training-31/).

**Say it out loud:** "Azure Data Factory is Azure's managed ETL and orchestration service. Pipelines are made of activities like Copy or running a Databricks notebook, linked services hold the connections, and a self-hosted integration runtime reaches on-prem sources. Triggers run it on schedules or events."

---

**Q. What is Azure Databricks**

**A. (Class answer)** *(no answer given)*

**Expanded:** Azure Databricks is Databricks' lakehouse platform offered as a **first-party Azure service** (sold and supported jointly with Microsoft). It runs managed **Spark** clusters and SQL warehouses, stores data in **ADLS Gen2** as **Delta Lake** tables, and integrates with Microsoft Entra ID (formerly Azure AD), Key Vault, Data Factory, Power BI and Event Hubs. **Unity Catalog** handles governance. The workspace features (notebooks, Jobs, Lakeflow/DLT pipelines, MLflow) are the same as Databricks on AWS or GCP.

See [Training 31 notes](/training-notes-site/notes/training-31/) ("Databricks: Bronze JSON → Silver Parquet (for Synapse)") and [Training 29 notes](/training-notes-site/notes/training-29/) ("Databricks Lakeflow (Spark Declarative Pipelines)").

**Say it out loud:** "Azure Databricks is the Databricks lakehouse platform as a native Azure service: managed Spark and SQL on Delta Lake tables in ADLS Gen2, integrated with Entra ID, Data Factory and Power BI, with Unity Catalog for governance."

---

**Q. What is Azure HDInsight**

**A. (Class answer)** *(no answer given)*

**Expanded:** HDInsight is Azure's **managed open-source cluster service**: Hadoop, Spark, Hive (LLAP), Kafka and HBase clusters, roughly the Azure equivalent of Amazon EMR. Status note: Microsoft is steering new work toward Databricks, Synapse and Fabric, and HDInsight 4.0/5.0 versions have announced retirements, with HDInsight on AKS already retired (verify the current status if asked). In an interview, mention it as the legacy Hadoop-style option on Azure.

See [Training 15 notes](/training-notes-site/notes/training-15/) ("Cloud Providers: AWS, Azure, GCP").

**Say it out loud:** "HDInsight is Azure's managed Hadoop-ecosystem cluster service for Spark, Hive, Kafka and HBase, roughly Azure's EMR. Most new Azure projects use Databricks or Synapse/Fabric instead."

---

**Q. What is Azure SQL**

**A. (Class answer)** *(no answer given)*

**Expanded:** "Azure SQL" is a family of managed services built on the **SQL Server engine** (T-SQL):

| Option | What it is |
|---|---|
| **Azure SQL Database** | Fully managed single database or elastic pool (PaaS), including a serverless tier and Hyperscale |
| **Azure SQL Managed Instance** | Near-100% SQL Server compatibility (SQL Agent, cross-database queries) for lift-and-shift |
| **SQL Server on Azure VMs** | Full SQL Server on a VM you manage (IaaS) |

These are **OLTP** databases. For analytics at scale you'd use Synapse, Fabric or Databricks.

**Say it out loud:** "Azure SQL is Microsoft's managed SQL Server family: Azure SQL Database as a fully managed PaaS database, SQL Managed Instance for near-full SQL Server compatibility, and SQL Server on a VM for full control."

---

**Q. What is the difference between Azure Data Lake Service Gen 1 and Gen 2**

**A. (Class answer)** *(no answer given)*

**Expanded:** The official name is Azure Data Lake **Storage** (ADLS), not "Service".

| | ADLS Gen1 | ADLS Gen2 |
|---|---|---|
| Built on | Its own separate service (HDFS-compatible) | **Azure Blob Storage** with the **hierarchical namespace** enabled |
| Directories | Yes | Yes: real directories, so renames and deletes of folders are atomic and fast |
| Cost and features | Separate pricing, fewer features | Blob pricing and tiers (hot/cool/archive), lifecycle rules, redundancy options |
| Access | `adl://` | `abfss://` (ABFS driver), plus the Blob APIs |
| Status | **Retired in February 2024** | The current standard |

Security: Azure RBAC plus POSIX-style **ACLs** on files and folders. In class, ADLS Gen2 was the storage under Synapse and Databricks.

See [Training 15 notes](/training-notes-site/notes/training-15/) ("AWS S3, Azure Blob Storage, Azure Data Lake Storage (ADLS)").

**Say it out loud:** "Gen1 was a separate HDFS-style service and was retired in 2024. Gen2 is built on Blob Storage with a hierarchical namespace, so it has real directories and ACLs plus Blob pricing and tiers, and it's accessed with `abfss://` from Spark, Synapse and Databricks."

---

**Q. What is Azure Synapse Analytics**

**A. (Class answer)** *(no answer given)*

**Expanded:** Azure Synapse Analytics is Azure's **unified analytics workspace**, combining several engines in one Synapse Studio:

| Component | Role |
|---|---|
| **Dedicated SQL pool** | Provisioned MPP data warehouse (formerly Azure SQL Data Warehouse), billed by DWU |
| **Serverless SQL pool** | Query files in ADLS (Parquet, CSV, Delta) with T-SQL using `OPENROWSET`, billed per TB processed, like Athena |
| **Apache Spark pools** | Managed Spark |
| **Synapse pipelines** | Data Factory engine built in |
| Synapse Link | Near-real-time replication from operational stores (Cosmos DB, SQL) |

Direction: Microsoft is moving new analytics investment to **Microsoft Fabric**, so mention Fabric as the successor.

See [Training 31 notes](/training-notes-site/notes/training-31/) ("Azure Synapse Analytics" and "Back in Synapse: querying Silver Parquet").

**Say it out loud:** "Synapse is Azure's analytics workspace that combines a dedicated SQL warehouse, serverless SQL over files in ADLS, Spark pools and Data Factory pipelines. I've used serverless SQL to query Silver Parquet in ADLS directly. Microsoft's newer platform is Fabric."

---

**Q. What is Azure Event Hubs**

**A. (Class answer)** *(no answer given)*

**Expanded:** Event Hubs is Azure's managed **event streaming** service, the equivalent of Kinesis Data Streams. A **namespace** contains event hubs (like topics), each split into **partitions**, read by **consumer groups** with checkpoints. It has a **Kafka-compatible endpoint**, so existing Kafka clients work by changing configuration. **Capture** writes the stream to ADLS/Blob as Avro or Parquet automatically. Retention depends on the tier (1 day on Basic, up to 7 days on Standard, up to 90 days on Premium/Dedicated). It's consumed by Stream Analytics, Databricks/Spark Structured Streaming, Functions or Fabric.

See [Training 12 notes](/training-notes-site/notes/training-12/) ("Azure Event Hubs") and [Training 31 notes](/training-notes-site/notes/training-31/) ("Event Hubs (preview, from the start of class)").

**Say it out loud:** "Event Hubs is Azure's managed event streaming service, like Kinesis or Kafka, with partitions and consumer groups and a Kafka-compatible endpoint. Its Capture feature writes the stream straight into ADLS."

---


## GCP


**Q. Describe your GCP experience**

**A. (Class answer)** *(no answer given)*

**Expanded:** Answer honestly, and map what you know. If your hands-on work is AWS and Azure, say so and show you know the GCP equivalents:

| Need | AWS | GCP |
|---|---|---|
| Object storage | S3 | Cloud Storage (GCS) |
| Warehouse | Redshift | **BigQuery** |
| Managed Spark/Hadoop | EMR | **Dataproc** |
| Stream/batch processing | Managed Flink, Glue | **Dataflow** (Apache Beam) |
| Streaming ingestion | Kinesis | **Pub/Sub** |
| Managed Airflow | MWAA | **Cloud Composer** |
| Wide-column NoSQL | DynamoDB/Keyspaces | **Bigtable** |

See [Training 15 notes](/training-notes-site/notes/training-15/) ("Cloud Providers: AWS, Azure, GCP").

**Say it out loud:** "My hands-on cloud work has been mainly AWS and Azure, but the concepts map directly: GCS is S3, BigQuery is the warehouse, Dataproc is managed Spark like EMR, Dataflow runs Beam pipelines, Pub/Sub is streaming and Composer is managed Airflow."

---

**Q. What's GCP Dataproc**

**A. (Class answer)** *(no answer given)*

**Expanded:** Dataproc is GCP's **managed Spark and Hadoop** service, the equivalent of EMR. Clusters start in about 90 seconds and are billed per second, so they are often **ephemeral** (created per job, data in GCS through the GCS connector). It also offers **Dataproc Serverless** (Serverless for Apache Spark) to submit Spark batches without a cluster, and autoscaling with preemptible/Spot workers. Choose it to run existing Spark or Hadoop code with little change.

See [Training 15 notes](/training-notes-site/notes/training-15/).

**Say it out loud:** "Dataproc is GCP's managed Spark and Hadoop service, like EMR. Clusters spin up in about 90 seconds so they're often created per job, and there's a serverless option for Spark batches. It's the easy way to move existing Spark jobs to GCP."

---

**Q. What's GCP Dataflow**

**A. (Class answer)** *(no answer given)*

**Expanded:** Dataflow is GCP's fully managed, serverless runner for **Apache Beam** pipelines. You write one Beam pipeline (Java, Python or Go) that works for both **batch and streaming**, and Dataflow handles autoscaling, work rebalancing and exactly-once processing. Strong streaming features: event-time windows, watermarks, triggers. Typical pattern: **Pub/Sub → Dataflow → BigQuery**. Google provides templates for common jobs.

See [Training 15 notes](/training-notes-site/notes/training-15/) ("Cloud Providers: AWS, Azure, GCP").

**Say it out loud:** "Dataflow is GCP's serverless engine for Apache Beam pipelines. One programming model covers batch and streaming, it autoscales, and it has strong event-time features. A typical pipeline is Pub/Sub to Dataflow to BigQuery."

---

**Q. Difference between Dataproc and Dataflow**

**A. (Class answer)** *(no answer given)*

**Expanded:**

| | Dataproc | Dataflow |
|---|---|---|
| Engine | Spark, Hadoop, Hive, Flink | Apache Beam |
| Management | Clusters you size (or Dataproc Serverless for Spark) | Fully serverless, autoscaling |
| Best for | Lift-and-shift of existing Spark/Hadoop code, Spark ML, notebooks | New pipelines, especially **streaming**, unified batch + stream |
| Portability | Standard Spark code | Beam code (runs on other runners, but Dataflow is the main one) |

Rule of thumb: existing Spark → Dataproc. New streaming pipeline on GCP → Dataflow.

**Say it out loud:** "Dataproc runs Spark and Hadoop on clusters you manage, so it's best for existing Spark code. Dataflow is serverless Apache Beam, best for new pipelines, especially streaming. I'd pick Dataproc to migrate Spark jobs and Dataflow for new streaming work."

---

**Q. What's GCP Cloud Composer**

**A. (Class answer)** *(no answer given)*

**Expanded:** Cloud Composer is GCP's **managed Apache Airflow**, the equivalent of MWAA on AWS. It runs Airflow on GKE (Kubernetes); you put DAG files in the environment's GCS bucket. Comes with Google operators for BigQuery, Dataproc, Dataflow and GCS. Used to orchestrate GCP pipelines on schedules with dependencies, retries and monitoring.

See [Training 26 notes](/training-notes-site/notes/training-26/) ("Apache Airflow (roadmap topic for this day)").

**Say it out loud:** "Cloud Composer is GCP's managed Airflow, like MWAA on AWS. I upload DAGs to its GCS bucket, and it orchestrates BigQuery, Dataproc and Dataflow tasks with Google's operators."

---

**Q. Describe your experience with GC Storage**

**A. (Class answer)** *(no answer given)*

**Expanded:** Cloud Storage (GCS) is GCP's object storage, the equivalent of S3: **buckets** and **objects**, accessed as `gs://bucket/path`. Points to mention: storage classes (**Standard, Nearline, Coldline, Archive**) with lifecycle rules, location types (region, dual-region, multi-region), IAM (with uniform bucket-level access), strong consistency, object versioning. Tools: `gcloud storage cp` (the newer CLI, replacing `gsutil`), and the client libraries. It's the landing zone for Dataproc, Dataflow and BigQuery external tables. If your experience is with S3, say that the concepts and patterns (Bronze/Silver/Gold prefixes, Parquet, partitioned paths) carry over directly.

See [Training 15 notes](/training-notes-site/notes/training-15/) ("Google Cloud Storage (GCS)").

**Say it out loud:** "GCS is GCP's object storage, equivalent to S3, with storage classes and lifecycle rules, IAM, and `gs://` paths used by Dataproc, Dataflow and BigQuery. My lake work has been on S3 and ADLS, and the same layout and formats apply on GCS."

---

**Q. What's Google BigQuery**

**A. (Class answer)** *(no answer given)*

**Expanded:** BigQuery is GCP's **serverless, columnar data warehouse**. Storage and compute are separate, and there are no clusters to manage. It uses the **Dremel** engine with columnar Capacitor storage. Pricing: **on-demand per TB scanned** or **capacity** pricing (slots, through editions). Cost and speed come from **partitioning** (by date or integer range) and **clustering** (sorting by up to four columns), plus selecting only needed columns (`SELECT *` scans everything). It supports nested and repeated fields (`STRUCT`, `ARRAY`), streaming inserts, BigQuery ML, and querying external data.

See [Training 18 notes](/training-notes-site/notes/training-18/) ("Google BigQuery" and "Why Redshift Went Serverless: BigQuery").

**Say it out loud:** "BigQuery is Google's serverless, columnar warehouse with storage separate from compute. You pay per data scanned or for reserved slots, so I partition and cluster tables and avoid `SELECT *` to keep queries cheap."

---

**Q. What's a federated query in BigQuery**

**A. (Class answer)** *(no answer given)*

**Expanded:** A federated query lets BigQuery **query data that lives in another system without loading it first**. Two forms:
- **`EXTERNAL_QUERY`** to **Cloud SQL** or **Spanner** through a connection: the SQL inside runs on the source database and the results come back to BigQuery.
- **External tables** over files in GCS (Parquet, ORC, Avro, CSV, JSON), Google Sheets or Bigtable, and **BigLake** tables (including Iceberg) with fine-grained security.

```sql
SELECT c.customer_id, c.name, o.total
FROM EXTERNAL_QUERY('my-project.us.cloudsql_conn',
                    'SELECT customer_id, name FROM customers') AS c
JOIN analytics.orders o USING (customer_id);
```

Trade-off: no data copy and always fresh, but slower than native tables and limited by the source's capacity. The equivalents elsewhere are Athena federated queries and Redshift federated queries.

**Say it out loud:** "A federated query lets BigQuery read data in place, from Cloud SQL or Spanner with `EXTERNAL_QUERY`, or from files in GCS as external tables, without loading it first. It's great for fresh data or occasional joins, but slower than native tables."

---

**Q. What's Google BigTable**

**A. (Class answer)** *(no answer given)*

**Expanded:** Bigtable is GCP's **wide-column NoSQL** database for very large, low-latency workloads: single-digit-millisecond reads and writes, scaling to petabytes and millions of operations per second by adding nodes. It's the system that inspired **HBase** and Cassandra's data model, and it supports the **HBase API**. Data is sorted by **row key** (the only index), so row key design determines performance. Good for time series, IoT, ad tech and real-time features. Not a SQL warehouse: for analytics you'd use BigQuery.

**Say it out loud:** "Bigtable is Google's wide-column NoSQL database for huge, low-latency workloads like time series or IoT. It's the model HBase was based on and supports the HBase API. Everything is keyed and sorted by row key, so key design is critical."

---


## CI/CD


**Q. What CI/CD tool have you used the most**

**A. (Class answer)** *(no answer given)*

**Expanded:** Pick the tool you can describe concretely, and describe what your pipeline did. Common answers:

| Tool | Where it fits |
|---|---|
| GitHub Actions | Repos on GitHub. YAML workflows in `.github/workflows/` |
| GitLab CI | Repos on GitLab. `.gitlab-ci.yml` |
| Jenkins | Self-hosted, plugin-based, `Jenkinsfile` |
| Azure DevOps Pipelines | Microsoft shops |
| AWS CodePipeline / CodeBuild | AWS-native |

A good answer covers the stages: on every pull request, run linting (`ruff`/`flake8`) and unit tests (`pytest` with small Spark fixtures), and for SQL, `dbt build` against a dev target. On merge to `main`, deploy: package the job, upload it to S3, apply `terraform apply`, then promote dev → test → prod.

See [Training 3 notes](/training-notes-site/notes/training-3/) ("CI/CD Pipeline Stages" and "CI/CD Tooling: Jenkins") and [Training 4 notes](/training-notes-site/notes/training-4/) ("Pipeline YAML & Build/Test/Deploy Flow").

**Say it out loud:** "Mostly GitHub Actions. On every pull request it ran linting and pytest unit tests for the PySpark code, and on merge to main it packaged the job, uploaded it to S3 and ran Terraform to deploy, with separate dev and prod environments."

---

**Q. What is CI/CD?**

**A. (Class answer)** *(no answer given)*

**Expanded:**
- **Continuous Integration:** developers merge small changes often. Every push or pull request **automatically builds and tests** the code, so problems are caught early.
- **Continuous Delivery:** every change that passes is automatically packaged and **ready** to release, with a manual approval to production.
- **Continuous Deployment:** passing changes go to production **automatically**, with no manual step.

For data pipelines, CI/CD also covers SQL/dbt models, infrastructure (Terraform), data quality tests and promotion through **dev → test/staging → prod**, with secrets kept out of the repository and a rollback plan.

See [Training 4 notes](/training-notes-site/notes/training-4/) ("CI/CD Fundamentals") and [Training 0 notes](/training-notes-site/notes/training-0/) ("What are the three environments, and why was CI/CD invented?").

**Say it out loud:** "CI means every change is automatically built and tested when it's pushed. CD means passing changes are automatically packaged and deployed, either up to an approval step, continuous delivery, or all the way to production, continuous deployment. For data, that includes dbt models and Terraform, promoted from dev to prod."

---

**Q. What are integration tests?**

**A. (Class answer)** *(no answer given)*

**Expanded:** An integration test checks that **several components work together correctly**, with real (or realistic) dependencies, rather than testing one function in isolation. For a pipeline: run the job end to end on a small sample, reading from a test S3 bucket or a Postgres in Docker, writing to a test table, then assert on row counts, schema and key values. Slower than unit tests, so there are fewer of them (the "test pyramid": many unit tests, fewer integration tests, very few end-to-end tests). Tools: pytest with Docker or Testcontainers, LocalStack for AWS services, dbt tests against a dev warehouse.

See [Training 3 notes](/training-notes-site/notes/training-3/) ("CI/CD Pipeline Stages").

**Say it out loud:** "An integration test checks that components work together, for example running my pipeline on a small sample against a test database in Docker and asserting on row counts and schema. Unit tests check single functions in isolation."

---

**Q. Describe your experience with Jenkins**

**A. (Class answer)** *(no answer given)*

**Expanded:** Jenkins is an open-source, self-hosted automation server. Pipelines are defined as code in a **`Jenkinsfile`** (declarative syntax: `pipeline { stages { stage('Test') { steps { ... } } } }`) kept in the repository. Jobs are triggered by webhooks or schedules and run on **agents**, with plugins for Git, Docker, credentials and so on. Be honest about your level. If you've used GitHub Actions more, say so and map the concepts (a stage is a job, an agent is a runner).

```groovy
pipeline {
  agent any
  stages {
    stage('Test')   { steps { sh 'pip install -r requirements.txt && pytest' } }
    stage('Deploy') { when { branch 'main' } steps { sh './deploy.sh' } }
  }
}
```

See [Training 3 notes](/training-notes-site/notes/training-3/) ("CI/CD Tooling: Jenkins").

**Say it out loud:** "I've written declarative Jenkinsfiles with test and deploy stages triggered by webhooks from the repo, running pytest and then a deploy script only on the main branch. The concepts carry over directly to GitHub Actions, which I've also used."

---


## Infrastructure as Code


**Q. What is Terraform?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Terraform (by HashiCorp) is an **Infrastructure as Code** tool. You describe the infrastructure you want in **HCL** files (declarative), and Terraform works out how to create, change or delete resources to match. It works across many clouds and services through **providers** (AWS, Azure, GCP, Snowflake, Databricks).

| Concept | Meaning |
|---|---|
| Provider | Plugin for a platform's API (`hashicorp/aws`) |
| Resource | One piece of infrastructure (`aws_s3_bucket`) |
| State | `terraform.tfstate`: Terraform's record of what exists. Keep it in a **remote backend** (S3 with locking) for teams |
| Plan / apply | `plan` previews the changes, `apply` makes them |
| Module | Reusable group of resources |
| Import | Bring an existing, hand-made resource under Terraform's management |

Licensing note: Terraform moved to the Business Source License in 2023, and **OpenTofu** is the open-source fork.

See [Training 23 notes](/training-notes-site/notes/training-23/) ("Infrastructure as Code (Terraform)") and [Training 25 notes](/training-notes-site/notes/training-25/) ("Terraform Fundamentals").

**Say it out loud:** "Terraform is a declarative infrastructure-as-code tool. I describe resources like S3 buckets, Glue jobs or Step Functions in HCL, `terraform plan` shows the changes and `apply` makes them, with the state stored remotely so the team shares one view. It works across clouds through providers."

---

**Q. What is Cloudformation?**

**A. (Class answer)** *(no answer given)*

**Expanded:** CloudFormation is **AWS's native Infrastructure as Code service**. You write a **template** in JSON or YAML, and CloudFormation creates all its resources together as a **stack**, in the right dependency order. It tracks state for you (no state file to manage), **rolls back** automatically if creation fails, and previews changes with **change sets**. **Drift detection** finds resources changed by hand. It covers AWS only, while Terraform covers many providers. The **AWS CDK** lets you write CloudFormation in Python or TypeScript.

**Say it out loud:** "CloudFormation is AWS's own infrastructure-as-code service. I write a YAML or JSON template, AWS deploys it as a stack, manages the state, and rolls back automatically on failure. It's AWS-only, while Terraform is multi-cloud."

---

**Q. How do you write a Cloudformation template?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A template is YAML or JSON with these main sections: `Parameters` (inputs), `Resources` (the only required section), `Outputs`, and optionally `Mappings` and `Conditions`. Intrinsic functions like `!Ref`, `!Sub` and `!GetAtt` connect pieces.

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Parameters:
  Env:
    Type: String
    AllowedValues: [dev, prod]
Resources:
  RawBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "my-raw-data-${Env}"
      VersioningConfiguration:
        Status: Enabled
Outputs:
  BucketArn:
    Value: !GetAtt RawBucket.Arn
```

Deploy with `aws cloudformation deploy --template-file template.yaml --stack-name raw-data-dev --parameter-overrides Env=dev`, check it first with `aws cloudformation validate-template`, and keep the template in Git so CI/CD deploys it.

**Say it out loud:** "A template is a YAML file with Parameters, Resources and Outputs. Each resource has an AWS type and properties, and functions like `!Ref` and `!Sub` wire them together. I deploy it with `aws cloudformation deploy` as a stack from CI/CD."

---

**Q. How do you write a Terraform job?**

**A. (Class answer)** *(no answer given)*

**Expanded:** There is no "Terraform job" as such. You write a **configuration** (`.tf` files) and run the standard workflow. A minimal example:

```hcl
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {                       # shared remote state
    bucket = "my-tf-state"
    key    = "pipeline/terraform.tfstate"
    region = "us-east-2"
  }
}

provider "aws" { region = "us-east-2" }

variable "env" { default = "dev" }

resource "aws_s3_bucket" "raw" {
  bucket = "my-raw-data-${var.env}"
}

output "raw_bucket" { value = aws_s3_bucket.raw.bucket }
```

| Command | Does |
|---|---|
| `terraform init` | Downloads providers, configures the backend |
| `terraform fmt` / `validate` | Formats and checks the code |
| `terraform plan` | Shows what will change |
| `terraform apply` | Makes the changes |
| `terraform destroy` | Removes everything in the configuration |

In CI/CD: run `plan` on a pull request for review, and `apply` on merge.

See [Training 23 notes](/training-notes-site/notes/training-23/) ("Infrastructure as Code (Terraform)"), [Training 24 notes](/training-notes-site/notes/training-24/) ("Terraform: importing existing Step Functions resources") and [Training 25 notes](/training-notes-site/notes/training-25/) ("Terraform Fundamentals").

**Say it out loud:** "I write `.tf` files with a provider, a remote S3 backend for state, variables and resources, then run `terraform init`, `plan` to review the changes and `apply` to make them. In CI the plan runs on pull requests and the apply runs on merge."

---


## Docker


**Q. What is docker?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Docker is a platform for building, shipping and running applications in **containers**. You describe an environment in a **Dockerfile**, build it into an **image**, push it to a **registry** (Docker Hub, Amazon ECR), and run it as a container on any machine with a container runtime. It solves "it works on my machine": the app, its libraries and system dependencies are packaged together. **Docker Compose** runs multi-container setups (for example Kafka + Spark + Postgres) from one `docker-compose.yml`.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "ingest.py"]
```

See [Training 0 notes](/training-notes-site/notes/training-0/) ("My Homework (macOS Setup Guide: Hardware Virtualization + Docker)"), [Training 3 notes](/training-notes-site/notes/training-3/) ("Docker Hub & Image Deployment") and [Training 19 notes](/training-notes-site/notes/training-19/) ("Streamlit App on ECS/Fargate (Visualization Layer)").

**Say it out loud:** "Docker packages an application with all its dependencies into an image, defined by a Dockerfile, which runs the same way anywhere as a container. I've used it with Docker Compose to run Kafka, Spark and Postgres locally, and to deploy a Streamlit app to ECS."

---

**Q. What is a container?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A container is an **isolated process** (or group of processes) running from an image, with its own filesystem, network and process view, but **sharing the host's operating system kernel**. Isolation comes from Linux **namespaces**, and resource limits from **cgroups**. Because there's no guest OS, containers start in seconds and are lightweight, unlike virtual machines.

| | Container | Virtual machine |
|---|---|---|
| Includes | App + libraries | Full guest OS + app |
| Kernel | Shared with the host | Its own |
| Startup | Seconds | Minutes |
| Size | MBs | GBs |
| Isolation | Process-level | Stronger, hardware-level |

Containers are meant to be **ephemeral**: data that must persist goes in **volumes** or external storage.

See [Training 14 notes](/training-notes-site/notes/training-14/) ("Virtual Environment vs. Container vs. Virtual Machine").

**Say it out loud:** "A container is an isolated process running from an image, with its own filesystem and network but sharing the host's kernel. That makes it much lighter and faster to start than a VM, which runs a whole guest OS."

---

**Q. How do you list your docker containers on the CLI?**

**A. (Class answer)** *(no answer given)*

**Expanded:**

| Command | Shows |
|---|---|
| `docker ps` | Running containers (same as `docker container ls`) |
| `docker ps -a` | All containers, including stopped ones |
| `docker ps -q` | IDs only, for scripting (`docker stop $(docker ps -q)`) |
| `docker compose ps` | Containers of the current Compose project |
| `docker images` | Local images (not containers) |
| `docker logs -f <name>` | Follow a container's logs |

**Say it out loud:** "`docker ps` lists running containers, and `docker ps -a` includes stopped ones. `docker images` lists images, and `docker compose ps` shows a Compose project's containers."

---

**Q. How do you list your docker containers on Dockerhub?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Trick in the wording: Docker Hub stores **images (repositories)**, not running containers. Containers only exist on the machines running them. To see your images on Docker Hub: log in at hub.docker.com and open **Repositories** (each repository lists its **tags**). From the CLI, `docker search <term>` searches public images, and `docker login` + `docker push user/repo:tag` publishes one. Listing your own repositories can also be done through the Docker Hub API.

See [Training 3 notes](/training-notes-site/notes/training-3/) ("Docker Hub & Image Deployment").

**Say it out loud:** "Docker Hub holds images, not containers. I'd log in to Docker Hub and look under Repositories to see my images and their tags. Running containers are listed on the host with `docker ps`."

---

**Q. What is a docker image?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A Docker image is a **read-only template** used to create containers: a filesystem snapshot plus metadata (default command, environment variables, exposed ports). It is built from a Dockerfile as a stack of **layers**, one per instruction, which are cached and shared between images, so rebuilds and downloads are fast (put rarely changing steps like `pip install` before `COPY . .`). Images are named `repository:tag` (for example `python:3.12-slim`) and stored in registries. Relationship: an **image** is like a class, a **container** is a running instance of it.

**Say it out loud:** "A Docker image is a read-only, layered template built from a Dockerfile, containing the app and its dependencies. A container is a running instance of an image, and images are stored in registries like Docker Hub or ECR."

---


## Kubernetes


**Q. What is Kubernetes?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Kubernetes (K8s) is an open-source **container orchestration** platform, originally from Google and now a CNCF project. It runs containers across a **cluster of machines** and keeps the actual state matching the **desired state** you declare in YAML: it schedules containers onto nodes, restarts failed ones, scales them, rolls out updates and handles service discovery and load balancing.

| Object | Role |
|---|---|
| Pod | Smallest unit: one or more containers |
| Deployment | Keeps N replicas of a pod running, rolling updates |
| Service | Stable network address in front of pods |
| Node | A worker machine |
| Control plane | API server, scheduler, controllers, etcd (cluster state) |

Data engineering uses: **Spark on Kubernetes** (as the cluster manager), Airflow's KubernetesExecutor, Kafka via operators like Strimzi, and managed services such as EKS, AKS and GKE.

See [Training 23 notes](/training-notes-site/notes/training-23/) ("Orchestration").

**Say it out loud:** "Kubernetes orchestrates containers across a cluster: I declare the desired state in YAML, and it schedules pods onto nodes, restarts failures, scales and does rolling updates. Spark can use it as its cluster manager, and on AWS it's EKS."

---

**Q. What is a pod?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A pod is the **smallest deployable unit in Kubernetes**: one or more containers that are scheduled together on the same node and **share a network namespace (one IP address, communicate over localhost) and storage volumes**. Usually a pod has one main container, plus optional **sidecars** (log shippers, proxies) or init containers. Pods are **ephemeral**: they aren't repaired but replaced, so you normally manage them through Deployments, StatefulSets or Jobs. In Spark on Kubernetes, the driver and each executor run as pods.

**Say it out loud:** "A pod is Kubernetes' smallest unit: one or more containers that run together on one node and share an IP address and volumes. Pods are disposable and are managed by Deployments or Jobs. In Spark on Kubernetes, the driver and each executor are pods."

---


## Monitoring and Alerting


**Q. What have you used for monitoring and alerting?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Describe **what you monitored and how you were alerted**, not just tool names. A strong answer covers three levels:

| Level | What to watch | Tools |
|---|---|---|
| Infrastructure / service | Job failures, duration, CPU/memory, consumer lag | CloudWatch metrics and alarms, Spark UI, Prometheus + Grafana |
| Pipeline / orchestration | Task failures, retries, SLA misses | Airflow alerts, Step Functions execution status, EventBridge rules |
| Data quality | Row counts, nulls, duplicates, freshness, schema changes | dbt tests, Great Expectations, custom checks |

Alerts go to SNS → email, Slack or PagerDuty. Logs: CloudWatch Logs, Splunk, ELK.

See [Training 20 notes](/training-notes-site/notes/training-20/) ("Access Setup") and [Training 17 notes](/training-notes-site/notes/training-17/) ("dbt Tests").

**Say it out loud:** "I used CloudWatch alarms on Glue and Lambda failures, routed through SNS to email, plus Step Functions execution status for the pipeline, and dbt tests for data quality like nulls, duplicates and freshness. In Kafka setups I'd also watch consumer lag."

---

**Q. What is Cloudwatch?**

**A. (Class answer)** *(no answer given)*

**Expanded:** See "What is AWS Cloudwatch" in the AWS section above: AWS's monitoring service with **metrics, alarms, dashboards and CloudWatch Logs** (searched with Logs Insights). From a monitoring point of view: set **alarms** on key metrics (Glue job failures, Lambda errors and duration, Kinesis iterator age, SQS queue depth) with SNS notifications, and publish **custom metrics** (rows loaded) from your code.

**Say it out loud:** "CloudWatch is AWS's monitoring service. I use its metrics and alarms, for example on Lambda errors or Kinesis iterator age, with SNS notifications, and CloudWatch Logs to debug."

---

**Q. What is Grafana?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Grafana is an open-source **visualization and dashboarding** tool for operational data. It doesn't store data itself; it connects to **data sources** such as Prometheus, CloudWatch, Elasticsearch/OpenSearch, InfluxDB, Loki (logs), Postgres. It builds live dashboards and sends **alerts** (to Slack, PagerDuty, email). It's commonly paired with Prometheus. Managed versions: Grafana Cloud, Amazon Managed Grafana, Azure Managed Grafana.

**Say it out loud:** "Grafana is an open-source dashboarding and alerting tool. It connects to data sources like Prometheus or CloudWatch to visualize metrics and send alerts. It doesn't store the data itself."

---

**Q. What is Prometheus?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Prometheus is an open-source **metrics monitoring system and time-series database** (a CNCF project, the standard in Kubernetes). It **pulls (scrapes)** metrics over HTTP from `/metrics` endpoints exposed by applications and **exporters** (node exporter, JMX exporter for Kafka or Spark). Metrics are time series with labels, queried with **PromQL**. **Alertmanager** handles alerts (grouping, routing to Slack or PagerDuty). Grafana is usually the dashboard layer on top.

**Say it out loud:** "Prometheus is an open-source monitoring system that scrapes metrics from applications and exporters, stores them as time series and lets you query them with PromQL. Alertmanager sends the alerts, and Grafana is usually used for dashboards."

---

**Q. What is Splunk?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Splunk is a commercial platform for **collecting, indexing, searching and analyzing machine data**, mainly **logs**. It is widely used for operations monitoring and **security (SIEM)**. Forwarders ship logs to indexers, and you query with **SPL** (Search Processing Language), then build dashboards and alerts. It is powerful but expensive (licensed by data ingested). Open-source alternatives: the ELK/OpenSearch stack, Grafana Loki. Splunk is now owned by Cisco (acquisition completed in 2024).

**Say it out loud:** "Splunk is a commercial platform for indexing and searching machine data, mainly logs, used for operational monitoring and security. You search with its SPL language and build dashboards and alerts. ELK or OpenSearch is the open-source alternative."

---


## DevOps


**Q. What is DevOps?**

**A. (Class answer)** *(no answer given)*

**Expanded:** DevOps is a **culture and set of practices** that brings **development and operations** together, so teams can deliver software **quickly and reliably**. Core practices: **CI/CD**, **infrastructure as code**, automated testing, monitoring and alerting, version control for everything, small frequent releases, and shared ownership of production ("you build it, you run it"). Common measures (DORA metrics): deployment frequency, lead time for changes, change failure rate, time to restore. For data teams the same ideas are called **DataOps**: versioned pipelines and SQL, automated data tests, environment promotion, observability of data quality and freshness.

See [Training 3 notes](/training-notes-site/notes/training-3/) and [Training 4 notes](/training-notes-site/notes/training-4/) ("CI/CD Fundamentals").

**Say it out loud:** "DevOps is a culture and set of practices that joins development and operations, using CI/CD, infrastructure as code, automated testing and monitoring to ship small changes quickly and reliably. For data pipelines the same approach is called DataOps."

---

**Q. What DevOps tools have you used?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Group your tools by purpose and say what you did with each:

| Area | Examples |
|---|---|
| Version control | Git, GitHub, GitLab |
| CI/CD | GitHub Actions, Jenkins, GitLab CI, AWS CodePipeline |
| Infrastructure as Code | Terraform, CloudFormation |
| Containers | Docker, Docker Compose, Amazon ECS/Fargate, Kubernetes |
| Monitoring | CloudWatch, Prometheus, Grafana |
| Secrets | AWS Secrets Manager, environment variables in CI |

**Say it out loud:** "Git and GitHub for version control, GitHub Actions and Jenkins for CI/CD, Terraform for infrastructure as code, Docker for packaging and running services, and CloudWatch for monitoring and alerts."

---

