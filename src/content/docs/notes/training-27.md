---
title: "Training 27 - Getting into Azure"
description: "The AWS to Azure service map, Blob Storage and ADLS Gen2, Entra ID and managed identities, Databricks, Delta Lake, Unity Catalog, Synapse and Fabric, plus Azure CLI setup."
sidebar:
  order: 27
---

Teacher: Evan Flint

Syllabus Day 28 (per file numbering; Mon Oct 19, 2026).

Source: class notes.

**Code note:** the commands below are written from the class demo plus standard Azure CLI syntax. They are not an exact copy of Evan's commands. Evan followed AI-generated step-by-step instructions on screen and shared them with the class in the chat.

---

# Today at a glance

| # | What happened |
|---|---|
| 1 | Student updates on the AWS pipelines (Step Functions, incremental loads, Redshift). New homework idea: propose an **original pipeline** and a **presentation** for management |
| 2 | Access fixes: AWS console stuck in a login loop for Evan (used the CLI instead), an EventBridge `events:ListRules` permission, first sign-ins to the **Azure portal** with **Microsoft Authenticator** |
| 3 | Lecture: AWS → Azure service map. **Blob Storage vs ADLS Gen1 vs ADLS Gen2**, the **hierarchical namespace**, "always say ADLS Gen2" |
| 4 | Lecture: **Entra ID**, managed identities, **tenant vs subscription**, Azure VMs, **Event Hubs**, **Azure Data Factory** |
| 5 | Lecture: **Databricks** history, **Delta Lake**, Delta tables, DLT / Lakeflow, **open table formats** (Delta, Iceberg, Hudi). Break |
| 6 | Q&A: why ADLS Gen2 moved to a Blob Storage base (atomic directory rename). Lecture: **Unity Catalog**, Databricks workspaces, dev / UAT / prod |
| 7 | Lecture: **Azure Synapse**, **Microsoft Fabric**, Power BI vs Tableau, all-in-one vendors (Talend, Pentaho, Informatica, **Palantir**). Break |
| 8 | Installing the **Azure CLI** (WSL or Windows), `az login`, tenant and MFA problems |
| 9 | Demo: environment variables, **resource group**, a tour of the storage-account create screen, then an **ADLS Gen2 storage account** from the CLI. `AuthorizationFailed` for students until Evan granted Contributor. Break |
| 10 | Demo: `bronze` container, real directories, upload `customers.csv`, view it in Storage browser, download it again, the `abfss://` path |
| 11 | Quick **Databricks tour**: Genie, a serverless notebook, the built-in `spark` variable, Catalog, Jobs & Pipelines, Compute, **Photon** |
| 12 | Databricks vs Snowflake. Homework: reading and review plus the **final-project presentation outline** |

---

# Class admin and project updates

Q. What were students working on?

A. (Evan) Finishing the AWS Citi Bike pipelines: moving from the local `customers.csv` to live Citi Bike data, fixing Bronze/Silver jobs that pointed at Evan's bucket instead of the student's own, adding **Step Functions** and **incremental** processing, and loading Silver into **Redshift**. "Unfortunately, we as a class have to soldier on and start with the Azure stuff."

Expanded: one student had redone AI-written parts of the pipeline by hand "so I can understand it a little bit better." That's a good habit before interviews, where you'll have to explain every step.

---

Q. What should you do when an AWS action is denied?

A. (Evan) "Usually it says in the error message fairly clearly what you're not allowed to do." Post the message so he can look. A student got `no identity-based policy allows the events:ListRules action` while checking that their EventBridge rules didn't trigger the shared pipeline. Evan's AWS web console was stuck in a login loop, so he added the permission from the **AWS CLI** and ran a verification. "In order to do verifications like that, sometimes you do need permissions that you don't necessarily need in order to build things out."

Expanded: an AWS `AccessDenied` message names the **action** (`events:ListRules`), the **principal** (your user or role) and often the **resource**. That's exactly what an admin needs to add a policy statement. List/Describe permissions are read-only, which is why Evan was comfortable granting this one.

---

Q. A Glue job in Step Functions has been running for 20 minutes without failing. Cancel it? (a student)

A. (Evan) "You shouldn't just cancel it... That is a suspiciously long amount of time for it to take, but don't cancel it until you're sure that it's hanging because of a problem." He sent an article with commands for diagnosing it on the Glue side.

Expanded: useful checks are `aws glue get-job-runs --job-name <job>` (state, error message, execution time), the job's **CloudWatch** logs, and the Step Functions execution history. A run stuck "RUNNING" with no log output often means it's waiting on something (a Redshift connection, a lock, a network route), not doing work.

---

# Getting into Azure

Q. How did students first sign in to Azure?

A. (Evan, demo) Through the invite link the company admin sent, using the training (company) email. You should land on the **Azure portal** home screen at `portal.azure.com`. The only app you need is **Microsoft Authenticator**, not the Azure mobile app.

| Problem | Fix |
|---|---|
| "Username may be incorrect" on the invite link | Open the link in the same browser where you're signed in to Teams, and choose to sign in with that Microsoft account |
| Authenticator seemed to need an Apple Store account on the same email | You don't. Install Microsoft Authenticator on your phone from its normal app store |
| "No eligible devices" | Set it up on the phone itself: scan the **QR code** the sign-in page shows, or use the **+** button in the Authenticator app to add the account |
| No mobile phone at all | A real problem: authenticator apps are generally required |

Expanded: this is **multi-factor authentication (MFA)**. Entra ID often uses **number matching**: the sign-in screen shows a number (Evan's was 95) and you type it into the Authenticator prompt, then confirm with a fingerprint or PIN. Some prompts send a **one-time code by email** instead; one student mixed up the email code and the Authenticator code.

---

# The AWS → Azure service map

Q. Which AWS services have a close Azure equivalent?

A. (Evan) "The best way to get a relatively quick understanding of what it is that we're doing is to have a little discussion about which technologies that we used in AWS have something that is basically exactly the same on the Azure side."

| AWS | Azure | Evan's note |
|---|---|---|
| S3 | Azure Storage (Blob Storage, **ADLS Gen2**) | Similar, "not quite as simple" |
| IAM | **Microsoft Entra ID** (+ Azure RBAC) | Authentication and permissions |
| EC2 | **Azure Virtual Machines** | Same simple concept |
| Kinesis | **Azure Event Hubs** | "Basically the same thing as Kafka, just located on the cloud" |
| Step Functions / Managed Airflow | **Azure Data Factory (ADF)** | Orchestration plus basic ETL |
| Glue / EMR (Spark) | **Azure Databricks** (or Synapse Spark) | "The main way that we work with data in an Azure environment" |
| Redshift (+ Glue) | **Azure Synapse Analytics** | "Like Redshift, but not really" |
| QuickSight | **Power BI** | Separate product |

Expanded: the table is a memory aid, not a one-to-one match. In particular, Entra ID handles **identity** (who you are), while **Azure RBAC** role assignments handle **authorization** (what you can do on which resource). AWS IAM does both.

---

# Azure storage: Blob Storage and ADLS Gen2

Q. What is a blob?

A. (Teacher's definition) "Blob is actually a pretty old computing term that basically just means a defined amount of data that describes basically anything. So a blob could be something that could be converted to a file or could be actually a file, or it could be just some text, or it could be just some encoded numbers... anything that can be represented in a discrete way by a computer."

Expanded: BLOB stands for **Binary Large Object**. In Azure Blob Storage, a blob is one object (file) inside a **container**, the same idea as an S3 object inside a bucket.

---

Q. What is Azure Blob Storage?

A. (Evan) "That's going to be the one that is most similar to S3... You create a bucket. The bucket has what looks like a folder structure. You put the data into the bucket within the folder structure and you use it, pretty much just like S3."

Expanded: in Azure the "bucket" is called a **container**, and it lives inside a **storage account**. The folder structure in plain Blob Storage is a **facade**: the name `customers/raw/customers.csv` is just one long object key containing slashes (a **flat namespace**).

| AWS S3 | Azure Storage |
|---|---|
| (account) | **Storage account** (globally unique name, region, redundancy, settings) |
| Bucket | **Container** (called a **file system** in ADLS Gen2 APIs) |
| Object | **Blob** (a file, in ADLS Gen2) |
| Prefix ("folder") | Virtual folder in Blob Storage; **real directory** in ADLS Gen2 |

---

Q. What are ADLS Gen1 and ADLS Gen2?

A. (Evan) "There is another kind of Azure storage account, and it is the other kind... that we mostly are going to be using as data engineers, and that is Azure Data Lake Storage, or ADLS... there is ADLS Gen1 and ADLS Gen2. And we normally use ADLS Gen2." "ADLS Gen1 is based on HDFS. It has a hierarchical namespace. And then ADLS Gen2 is based on Blob Storage. And unlike base Blob Storage, it also has a hierarchical namespace."

Expanded (correction): Gen1 was **HDFS-compatible** (it exposed the WebHDFS API so Hadoop and Spark could use it), but it ran on Microsoft's own storage system, not on HDFS itself. Gen1 was **retired in February 2024**, so ADLS Gen2 is the only ADLS today.

| | Blob Storage | ADLS Gen1 (retired) | ADLS Gen2 |
|---|---|---|---|
| Built on | Azure Blob Storage | Separate Hadoop-compatible service | Azure Blob Storage |
| Namespace | Flat (folders are a facade) | Hierarchical | **Hierarchical** (when enabled) |
| Directory rename/delete | Copy + delete every object | One operation | One **atomic** metadata operation |
| Folder/file permissions | No | POSIX-style ACLs | POSIX-style **ACLs** + RBAC |
| Path for Spark | `wasbs://` | `adl://` | `abfss://` |
| Today | General object storage | Gone | The data-lake choice for data engineering |

---

Q. What is a hierarchical namespace?

A. (Teacher's definition) "The essential thing with it is the hierarchy. Hierarchical namespace. Okay, that's the buzzword that everybody associates with ADLS... By hierarchical namespace, we mean that directory structure. We mean that you can have actual directories as they are in a file system. And you can put things into folders and it will actually be represented on the file system as a folder, not just as a facade."

Expanded: ADLS Gen2 isn't a separate product you pick from a list. It's a normal **general-purpose v2 storage account** with **Hierarchical namespace** turned on (`--hns true`, or the checkbox on the Advanced tab). You choose it when you create the account; you can't simply untick it later. See also Training 15 for flat vs hierarchical storage and Training 5 for the ADLS vs Blob naming note.

---

Q. Why did Microsoft build Gen2 on Blob Storage instead of keeping the HDFS-style Gen1? (a student)

A. (Evan) He read from the article: "a key advantage is atomic directory renaming. Traditional flat object storage requires copying and deleting multiple objects to simulate renaming a directory. ADLS Gen2 can perform the rename operation as a metadata operation, which is particularly useful for Spark writes and commits." The rationale was "to combine the Hadoop-compatible file system capabilities of Gen1 with the scalability, lower costs and broader ecosystem of Blob storage." His summary: running two completely different storage systems was expensive for Microsoft, so Gen2 simplified things on their side and made storage "cheaper and more efficient."

Expanded: why the rename matters. Spark (and Hive) jobs often write output to a temporary folder and then **rename** it to the final folder to "commit" the job. On flat storage, renaming a folder of 10,000 files means 10,000 copies and 10,000 deletes, which is slow and not atomic (a crash can leave half the files moved). With a hierarchical namespace it's one quick, all-or-nothing change.

---

Q. Should you say "Azure Blob Storage" on your profile?

A. (Evan) "I do not want to hear anybody in this class talk about having used Azure Blob Storage in any of their Azure projects on their profile. Please always, always, always say ADLS Gen2. Anything that you say that is not ADLS Gen2 is going to make you sound like an amateur." Interviewers will think "what do you mean you were using Blob Storage? Weren't you using ADLS Gen2?" This topic "does occasionally come up in job interviews."

Expanded: a good one-line answer if asked: "ADLS Gen2 is Blob Storage with a hierarchical namespace, which gives real directories, atomic renames and folder-level ACLs, so it's what we use for the data lake."

---

# Identity: Entra ID, managed identities, tenants and subscriptions

Q. What is Microsoft Entra ID?

A. (Evan) "IAM in AWS is basically Azure Entra ID." "Azure has just its own standards for how authentication is done." He admitted it's the part he knows least, because he doesn't enjoy cloud authentication, and predicted: "I tell all of you guys to go and do something and you all come back at me and say, hey, I don't have permission to do that."

Expanded: **Microsoft Entra ID** (formerly **Azure Active Directory**, Azure AD) is Microsoft's cloud identity service. It holds **users**, **groups**, **service principals** (identities for apps) and **managed identities**, and it handles sign-in and MFA. What an identity may do in Azure is set separately by **Azure RBAC**: a **role assignment** = a principal + a role + a scope.

| Piece | Question it answers | Example from today |
|---|---|---|
| Entra ID (authentication) | Who are you? | Signing in with the company email + Authenticator |
| Azure RBAC (authorization) | What can you do, and where? | Evan giving students **Contributor** so they could create resource groups |
| Role | Which set of permissions? | Contributor, Reader, Storage Blob Data Contributor |
| Scope | On what? | Subscription → resource group → resource |

Training 28 continues this with role assignments for managed identities and the control-plane vs data-plane split.

---

Q. What is an Azure managed identity?

A. (Evan) "It's a separate way to authenticate yourself, which is going to be easier." He was surprised to learn that "if you have an Azure Managed Identity, it can work for authentication for things outside of Azure," even AWS.

Expanded: a **managed identity** is an Entra ID identity that Azure creates for a resource (a VM, a data factory, a Databricks Access Connector) and whose credentials Azure manages, so no password or key is stored in your code. Evan was right about AWS: through **workload identity federation**, a managed identity can get a token from Entra ID and exchange it for temporary AWS credentials with `AssumeRoleWithWebIdentity` (OIDC), without long-lived AWS keys. The class will use managed identities for ADF and Databricks in Training 28.

---

Q. What is the difference between a tenant and a subscription?

A. (Evan) "When I was getting all of you guys authenticated, I needed to provide the admin with your tenant ID, so that's just a long string of characters. And then the subscription is the entire account, basically, it's what keeps track of all of the services that are being used."

Expanded (correction): it's closer to the other way around. The **tenant** is the top: one **Entra ID directory** for an organization, holding all its users and identities. A **subscription** is a **billing and management container** inside that tenant; a tenant can have many subscriptions (the class works in the training subscription). Each subscription contains **resource groups**, which contain **resources**. Both IDs are GUIDs, and the CLI needs both to log you in to the right place.

| Level | What it is | Rough AWS equivalent |
|---|---|---|
| Tenant | The organization's Entra ID directory | AWS Organization / IAM Identity Center |
| Subscription | Billing + access boundary for resources | An AWS account |
| Resource group | Folder of related resources | (Tags / CloudFormation stack) |
| Resource | One service instance, e.g. a storage account | One S3 bucket, one EC2 instance |

---

# Other Azure services

Q. What is an Azure Virtual Machine?

A. (Evan) "AWS EC2... maps directly onto Azure Virtual Machines... It is a virtual machine in the cloud, which you can treat like it's a regular computer... most people don't use it for work. They use it to deploy some kind of application and make it available to the general public over the internet."

---

Q. What is Azure Event Hubs?

A. (Evan) "AWS Kinesis maps to Azure Event Hubs. The Event Hubs interface is actually even simpler than the Kinesis interface... all that you see on Event Hubs is just a page saying that you've got a stream going, and it doesn't even give you any analytics." "You just create the stream, you create a Kafka producer, you create a Kafka consumer, you use exact Kafka syntax, and you just use the address of the Azure Event Hubs stream, and it just works." Like Kinesis, it's Kafka as a managed service.

Expanded (correction): the portal does show **metrics** (incoming and outgoing messages, bytes, throttled requests) for each namespace and event hub, though not message contents. Kafka clients work against the **Kafka endpoint** (Standard tier and above, port 9093), but you also set SASL_SSL authentication (a connection string or Entra ID token), not just the address. Naming: an Event Hubs **namespace** ≈ a Kafka cluster, an **event hub** ≈ a Kafka topic. Evan covers it hands-on with Synapse in Training 31.

---

Q. What is Azure Data Factory?

A. (Evan) "Azure Data Factory, often abbreviated to ADF, is not something that has a direct parallel in any of the other cloud systems. Basically what it is is an orchestration tool," used for the kind of automation you'd do on AWS with Step Functions or managed Apache Airflow. "But Data Factory is also capable of doing at least basic level ETL." It has a drag-and-drop UI "sort of analogous to like Step Functions or Apache NiFi" where you build a visual diagram of the pipeline, trigger it and watch it progress. "Microsoft wants you to use Data Factory as sort of your command center for the rest of the cloud." It's asked about "in at least a basic capacity in most Azure-focused interviews."

Expanded (correction): the closest AWS match is **AWS Glue** (visual ETL plus workflows/triggers), and on GCP **Cloud Data Fusion** with **Cloud Composer** (managed Airflow). So it has rough parallels, just none that combine orchestration and low-code ETL the same way. The full ADF walkthrough (Copy activity, linked services, datasets, integration runtimes) is in Training 28.

---

# Databricks, Delta Lake and open table formats

Q. What is Databricks, and why does it matter?

A. (Evan) "Databricks is the main way that we work with data in an Azure environment." About "30 to 40% of interviews that I see are gonna involve Databricks in some capacity. Sometimes it's on Azure, sometimes it's on AWS, sometimes it's on GCP." On Azure "you can just go to the Azure portal, you can type Databricks, you click two buttons" and you're in, "so that's why we've waited to introduce it until we get to the Azure portion, so that you guys don't need to have your own unique Databricks accounts."

Expanded: there are two dedicated Databricks days coming (Training 28 starts with a workspace, Unity Catalog storage setup, and a Bronze/Silver/Gold notebook).

---

Q. Where did Databricks come from?

A. (Evan) "It is a company that was founded by the people who created Apache Spark." Spark "came out of the University of California at Berkeley," and as a university project it was released free and open source. Big companies started using it, so the creators did what open-source creators usually do: "set up a company that's got a different name from the open source product, but we offer the enterprise version... a flashier UI... extra bells and whistles... and we will provide you with enterprise support. Enterprise support is basically the business model for turning an open source product into a commercial product." But "Databricks didn't just stop there... They wanted to basically take over the data processing world," so they added "this whole extra data storage layer to Spark."

Expanded: Spark started at UC Berkeley's **AMPLab** (2009), became an **Apache** project, and Databricks was founded in 2013 by its creators.

---

Q. Why does Spark need a storage layer?

A. (Evan) "If you download regular open source Spark, what you have is an ETL tool. It is for data processing. It is not for data storage... if you want that data to actually go anywhere, you need to get a separate place to store it," such as Hive, HDFS, Redshift, S3 or any database. Selling a product, "you kind of want to have a data processing technology... but then also a data storage technology so that the data that is processed can just be naturally thrown in to a place to store it... that is how we got a thing called Delta Lake."

---

Q. What do all the "Delta" names mean?

A. (Evan) "Delta Lake is the data lake that is offered by Databricks... Anytime you hear anything with the name Delta in it, it is going to refer to a Databricks service. Nobody else calls anything Delta." Then there's the **Delta format** ("an OTF format that's used in Delta Lake"), **Delta tables** ("tables that are unique to Delta Lake"), and **Delta Live Tables (DLT)**, "also known as Spark Declarative Pipelines, and also known as Lakeflow... Delta Live Tables, Spark Declarative Pipelines, and Lakeflow all mean exactly the same thing. Those are basically ELT syntax and automation for a Databricks environment."

Expanded (correction): three fixes.

| Evan said | More precisely |
|---|---|
| Delta Lake is Databricks' data lake | Delta Lake is an **open-source storage layer / table format**, not a separate storage service. The data still sits in your own ADLS Gen2, S3 or GCS as Parquet files plus a `_delta_log` transaction log |
| "Nobody else calls anything Delta" | Databricks created it, but it's now a **Linux Foundation** project. Microsoft Fabric, Synapse Spark, Spark on EMR, Trino and others read and write Delta tables |
| DLT = Spark Declarative Pipelines = Lakeflow | DLT was **renamed Lakeflow Declarative Pipelines** in 2025. **Lakeflow** is the umbrella brand (Lakeflow Connect, Lakeflow Jobs, Lakeflow Declarative Pipelines). **Spark Declarative Pipelines** is the open-source version of the same framework contributed to Apache Spark. Related, not identical |

See Training 29 for Delta time travel, `MERGE` and Lakeflow Declarative Pipelines.

---

Q. What is an open table format (OTF)? (a student asked for a reminder)

A. (Teacher's definition) "OTF is Open Table Formats... there are basically three that you need to know about and only two that you need to care about... Delta, Iceberg, and Hudi." Hudi: "know that it exists... Don't put an especially large amount of effort into learning it because it's basically the same as the other two, and nobody ever asks about it in job interviews." "Delta format is what you are going to be using if you are working in Databricks... Iceberg is the open source one... if you're building out a data lakehouse on basically any platform which is not Databricks Delta Lake, you are going to be using Iceberg," for example Snowflake, S3 + Redshift, or Google Cloud Storage + BigQuery. "An OTF format is going to contain both the data, usually in Parquet format, and the schema... in either JSON or Avro." OTF "files are some of the most complicated individual files that you're going to encounter": like a Parquet "file" it's really a **directory**, with a data subdirectory of Parquet part files and a separate subdirectory holding the schemas, "probably going to be JSON formatted."

Expanded (correction): **all three are open source** (Delta under the Linux Foundation, Iceberg and Hudi under Apache), so "the open source one" should be "the vendor-neutral, most widely adopted one." The metadata also holds much more than the schema: the list of data files in each version (snapshot), partition info and statistics, which is what gives ACID transactions and time travel on plain object storage.

| Format | Created by | Metadata folder | Metadata files | Typical home |
|---|---|---|---|---|
| **Delta Lake** | Databricks | `_delta_log/` | JSON commits + Parquet checkpoints | Databricks, Fabric |
| **Apache Iceberg** | Netflix | `metadata/` | JSON table metadata + **Avro** manifest lists and manifests | Snowflake, Athena/Redshift/Glue, BigQuery, Trino |
| **Apache Hudi** | Uber | `.hoodie/` | Timeline files | Upsert-heavy workloads on EMR |

Interoperability is improving: Databricks' **UniForm** can expose a Delta table as Iceberg too.

---

# Unity Catalog and Databricks workspaces

Q. What is Unity Catalog?

A. (Teacher's definition) "Unity Catalog, abbreviated to UC often... Basically, what Unity Catalog is, is a governance framework for Databricks and Delta Lake." With Databricks you use Spark to process data into Delta Lake, or build "an ELT lakehouse type of architecture... where you'll just do the transfer into a bronze bucket and then use Spark as essentially an ELT tool instead of an ETL tool to move data from bronze to silver and silver to gold."

---

Q. What is a Databricks workspace?

A. (Teacher's definition) "The Databricks workspace is just an environment that is separate from all the other Databricks environments in the account, which is there so that you can have multiple projects that are configured in multiple ways." For example, an accounting pipeline in one workspace, finance in another and HR in a third, "and you can apply different governance rules to each one of them and just keep them isolated." That works for a small account, but "because we're working with big data... at the entire enterprise scale, sometimes having those isolated workspaces can actually lead to some complications."

---

Q. What are dev, UAT and production clusters?

A. (Evan) "The typical compute resources that you're going to be having in a production project are basically gonna be three clusters. There's the dev cluster, the testing or UAT cluster, and the production cluster... very, very, very important terms to know."

| Environment | Evan's description |
|---|---|
| **Dev** | Where the engineering team works toward the next version. If someone breaks it, "it interrupts everybody's work, but it doesn't interrupt the actual business" |
| **Test / UAT** | QA and extra testing "after you've combined everybody's work together," to make sure it won't break production |
| **Production** | Runs the actual business; a failure is "a top priority to fix": find the cause, **roll back**, fix, redeploy |

Expanded (correction): UAT stands for **User Acceptance Testing** (Evan said "user access testing"): business users confirm the system does what they need. Also, these are usually separate **environments** (often separate workspaces, storage and catalogs), not just three clusters; each environment can have many clusters or jobs.

---

Q. What problem does Unity Catalog solve?

A. (Evan) Workspaces "are isolated from each other completely. And so each workspace is gonna need its own compute resources." UC lets "these different workspaces... all have the same governance rules applied to them," and lets you "combine the data from the different workspaces and interact with the data from all of those different workspaces in the same set of clusters. So instead of having three clusters for each one of your data pipelines, you can have just three clusters for all your data pipelines," which saves money and admin work.

Expanded (correction): the governance part is right; the cluster part isn't. Compute still belongs to **one workspace**: a cluster in workspace A can't be used from workspace B. What Unity Catalog does share is the **metastore** (one per region, attached to many workspaces), so the **same catalogs, tables, permissions, lineage and audit logs** are visible from every attached workspace. You save effort because data doesn't need copying between workspaces and permissions are defined once, not because clusters are shared.

| Without UC (legacy) | With Unity Catalog |
|---|---|
| Each workspace has its own **Hive metastore** and table permissions | One **metastore** shared by all workspaces in the region |
| Sharing data means copying or remounting storage | Any attached workspace can query the same `catalog.schema.table` (if granted) |
| Permissions set per workspace | Central `GRANT`s, auditing and **lineage** |

---

Q. Will the class set up Unity Catalog?

A. (Evan) "It may be a slight challenge to get Unity Catalog set up on our corporate account." Earlier in the year he did a week of live demos on UC governance and "for like three and a half of the five days, all that anybody was watching me do was just wrestle with the technology. Unity Catalog is tremendously difficult and annoying to get set up properly." "Unity Catalog in particular" is "the bottom of the pit of cloud authentication." But once it's running "it serves to streamline and normalize your entire environment." He has a UC-managed environment on a personal Azure account he can show if needed.

Expanded: it turned out easier than feared. In Training 28 the class's new workspace already had Unity Catalog enabled, because new Azure Databricks workspaces are now **automatically enabled for UC**.

---

# Azure Synapse

Q. What is Azure Synapse?

A. (Evan) "Azure Synapse is gonna be kind of like Redshift, but not really... Synapse is the closest thing that Microsoft Azure has to a traditional data warehouse." It adds two things beyond a warehouse: a **code execution environment** for Spark ("it used to be normal in an Azure environment to write Spark code, which would execute in Synapse's code environment") and an **analytics platform**. "Synapse has code execution, warehouse, and analytics all rolled into a single service." Today "most Azure users want to use Databricks rather than Synapse." At one client, the American Bureau of Shipping, a senior consultant helped move them from Spark + Synapse warehouse + Synapse analytics to Databricks Spark + Delta Lake + Databricks analytics. He's heard "Synapse is pretty frustrating to work with," but Microsoft still offers it, "so as data engineers looking for work, we must learn about Synapse still."

Expanded: Synapse pieces are **dedicated SQL pools** (MPP warehouse, formerly Azure SQL Data Warehouse), **serverless SQL pools** (query files in the lake), **Apache Spark pools** and **pipelines** (ADF built in), all in **Synapse Studio**. Microsoft now points new analytics work toward **Microsoft Fabric**, which is the successor to many Synapse features. Hands-on Synapse is in Training 31.

---

Q. If Synapse runs Spark, isn't it more like EMR or Glue than Redshift? (a student)

A. (Evan) "It would, yeah, except that it's got both Spark and a data warehouse in it." Asked if he meant an SQL-queryable warehouse: "Every data warehouse is an SQL warehouse." He dismissed NoSQL "data warehouses": "The whole point of a data warehouse is to have tables that are associated with each other. And in order to work with them, you have to do joins. You can't do joins in MongoDB." So Synapse is "like a combination of Glue and Redshift."

Expanded (correction): MongoDB **can** join, using the `$lookup` aggregation stage (a left outer join), but it isn't built for large analytical joins, so Evan's main point stands: warehouses are relational and SQL-based.

---

# Microsoft Fabric, Power BI and all-in-one platforms

Q. What is Microsoft Fabric?

A. (Evan) "It's only like two years old, and it only started actually being asked about in job interviews in the past year." "Microsoft Fabric is a service that is independent of Azure, but which offers a group of the same big data services that you find in Azure packaged together and with authentication and connections streamlined. It's sold as a package separately from mainline Azure." He listed ADLS, Databricks, Data Factory, Synapse, and **Power BI** included. There will be two days of Fabric training, with a separate Fabric sign-in.

Expanded (correction): Fabric went generally available in **November 2023** (about three years before this class). It's a **SaaS** analytics platform (billed by Fabric capacity) whose storage is **OneLake**, built on ADLS Gen2, with Delta Lake as its table format. Its workloads are Data Factory, Data Engineering (Spark), Data Warehouse, Real-Time Intelligence, Data Science and Power BI, with **Copilot** built in. It does **not include Databricks**: Databricks is a separate product that can read and write OneLake.

---

Q. Why would anyone pay for Fabric when Azure already has these services?

A. (Evan) There's "a long history in the market for big data services for something that can be sold to businesses as an all-in-one data pipeline solution." Engineers know a pipeline needs ingestion, intermediate storage, processing, a lake or warehouse, and BI, all wired together. But a CEO asks "why does working with my data need to be such a big deal?... Why can't I just pay for one product?" No tool has captured that whole market, but expensive enterprise products are sold that way: "Talend, Pentaho, Informatica, Palantir." They show up in interviews occasionally, but the company doesn't train on them because of the price tags, and each has its own framework you have to pay to learn ("there is no open source version of Informatica").

Fabric's advantages, per Evan:

| Advantage | Evan's point |
|---|---|
| Talent pool | It's built from Azure services, so "you can hire anybody who has Microsoft Azure experience" |
| Familiar tools | "Everybody knows Power BI, everybody uses Power BI" |
| Windows integration | Desktop clients that connect Windows and the cloud (they "take up a tremendous amount of disk space"). Evan, on Linux, uses the Azure CLI instead |
| OpenAI partnership | "Microsoft has specifically ChatGPT as its extension" |

Expanded (correction): Fabric's AI assistant is **Copilot in Fabric**, which runs on OpenAI models through **Azure OpenAI**. It isn't the ChatGPT product itself, but the "OpenAI models built in" point is fair.

---

Q. What is Power BI, and Power BI or Tableau?

A. (Evan) "Power BI is Microsoft's premier business intelligence analytics, maps and charts making tool." The two big names are **Tableau** and **Power BI**; "these days you hear more about Power BI," and sometimes AWS QuickSight. The class used Streamlit because it's free, "but if you're doing BI professionally, then you really should learn something like Power BI or Tableau." Start with Power BI: it has a free tier ("somewhat limited") that lets you learn the interface. Tableau gives a two-week trial, then "it's like 700 US dollars a year." Power BI isn't bundled with an Azure account; it's "a separate application with its own registration and authentication and payment."

Expanded (correction): **Tableau Public** is free (your workbooks are public), so you can learn Tableau without paying. **Power BI Desktop** is free for building reports on your own machine; sharing reports needs a Pro or Fabric license. Paid Tableau Creator is roughly $75 per user per month billed yearly.

---

Q. What is Palantir?

A. (Evan) "Its main product is called Foundry." Palantir is "very much in the business of trying to simplify the entire data pipeline, as well as the analytics side of it." "It would be a really, really cool tool to work with if you could do so for anything like a reasonable amount of money." It's associated with Peter Thiel; you can't just buy the software, "you actually have to like hire Palantir people that come with the software," and Evan's view is it's "being completely propped up by the US government." "For the most part, you can do the same things with Fabric as you can do with Palantir." Palantir jobs exist, but it's hard to get one without Palantir experience, and hard to get the experience without the job.

Expanded: Palantir's products are **Foundry** (commercial data platform), **Gotham** (government and defense) and **AIP** (its AI platform). Government contracts are a large share of its revenue, but it also has a big and growing commercial business, so "propped up" is Evan's opinion.

---

# Azure CLI setup and login

Q. How do you install the Azure CLI and sign in?

A. (Evan, demo) Install it in **WSL** (Linux, like Evan) or in **Windows PowerShell**, then log in and check which account you're in. "The first command... with curl, that's for Linux. The one with winget is for Windows."

Commands from the class demo (not exact):

```bash
# WSL / Ubuntu
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Windows PowerShell
winget install -e --id Microsoft.AzureCLI

az login                      # opens a browser sign-in
az login --use-device-code    # if no browser opens (prints a code to enter at microsoft.com/devicelogin)
az account show --output json # which tenant and subscription you're using
```

Expanded: `az account show` should list the **training subscription** as the default (`isDefault: true`). If you have more than one subscription, `az account list -o table` shows them all and `az account set --subscription "<name-or-id>"` picks one.

---

Q. What went wrong with logging in, and how was it fixed?

A. (Evan, demo)

| Error / symptom | Cause | Fix |
|---|---|---|
| "We couldn't find an account with that username" in the CLI (portal worked on another computer) | CLI was signing in against the wrong tenant (personal Microsoft account flow) | `az logout`, `az account clear`, then `az login --tenant <tenant-id>` |
| "Subscription ... does not exist in cloud AzureCloud" | Logged in to a tenant that doesn't hold the training subscription | Log in with the right tenant first, then `az account set --subscription <id>` |
| Authenticator code rejected | It was an **email** one-time code prompt, not the Authenticator | Use the code type the prompt actually asks for |
| Asked for a "domain" | Org sign-in page wanted the organization's domain | Evan sent the domain to enter; or cancel and use `az login --tenant` / `--use-device-code` |
| (Evan) "Due to a configuration change made by your administrator... you must use multi-factor authentication" when creating a resource group | Token from before MFA was enforced | `az logout`, run the suggested `az login` again, approve the Authenticator number match, choose the subscription number (Evan typed `1`) |
| "Home tenant ID" vs "tenant ID" confusion | A guest account's home tenant differs from the tenant it was invited into | Use the tenant that owns the training subscription |

Expanded: environment variables help here too: Evan shared commands to set the subscription and tenant IDs as variables so every command uses the same ones. Keep those IDs in your own notes, not in shared files.

---

# Demo: creating an ADLS Gen2 storage account

Q. What is a resource group?

A. (Teacher's definition) "This is one of those basic things that we need for all of our Azure services, our resource groups. Basically, it is an abstract grouping of things together, sort of conceptually like an AWS VPC, although I don't believe that it actually does what a VPC does... You want all of your resources that are going to be working with each other to be inside of the same resource group."

Expanded (correction): Evan's doubt is right: a resource group has nothing to do with networking. Azure's VPC equivalent is a **Virtual Network (VNet)**. A resource group is a **management and lifecycle container**: you can set permissions and policies on it, see its costs, and **delete it to delete everything inside**. Every resource belongs to exactly one resource group, and the group itself has a region (for its metadata only).

---

Q. How did Evan set up the environment variables?

A. (Evan, demo) The steps used a student identifier variable: "change student01 to your own identifier," which is "completely arbitrary." Evan used `teacher`. Then resource group, location, storage account and container variables.

Code from the class demo (not exact):

```bash
STUDENT="teacher"                       # your own identifier
RG="rg-adls-$STUDENT"
LOCATION="eastus"                       # Evan's group showed East US
STORAGE="adls${STUDENT}$(openssl rand -hex 3)"   # must be globally unique
CONTAINER="bronze"
echo $RG $LOCATION $STORAGE $CONTAINER
```

Expanded: Evan wasn't sure where to check a region in Azure. It's on every resource's **Overview** page, in `az group show -n $RG --query location`, and `az account list-locations -o table` lists valid names (`eastus`, `eastus2`, ...). Keep everything for one project in the **same region** to avoid latency and data-transfer costs. Variables live only in the current shell, which caused a student error later.

---

Q. How do you create the resource group?

A. (Evan, demo)

```bash
az group create --name $RG --location $LOCATION
az group show --name $RG -o table
```

It returned JSON, and the verification showed East US and `rg-adls-teacher`. "Fantabulous."

---

Q. What does the storage-account create screen look like in the portal?

A. (Evan, demo) He toured it without clicking Create, then built the real one in the CLI.

| Tab / field | What Evan chose or said |
|---|---|
| Subscription, resource group | Training subscription, `rg-adls-teacher` |
| Storage account name | Letters and numbers only (no dashes), 3–24 characters, **globally unique** |
| Region | East US |
| Primary service | **Azure Data Lake Storage** (not Blob Storage) |
| Primary workload | Not required, skipped |
| Performance / redundancy | Standard, geo-redundant (GRS) "is fine" |
| **Advanced → Enable hierarchical namespace** | "We really, really, really want to click this" |
| Networking | Public network access, defaults |
| Data protection, Encryption, Tags | Defaults |
| Review + create | Stopped here |

Expanded: the name must also be **all lowercase**, because it becomes part of the URL (`<name>.blob.core.windows.net`, `<name>.dfs.core.windows.net`). Redundancy options: **LRS** (3 copies in one datacenter), **ZRS** (across availability zones), **GRS** (plus a copy in a paired region), **GZRS**. The CLI version used LRS, the cheapest, which is fine for a class.

---

Q. How did Evan create the storage account from the CLI?

A. (Evan, demo)

Command from the class demo (not exact):

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

| Flag | Evan's explanation | Expanded |
|---|---|---|
| `--sku Standard_LRS` | SKU | Standard performance, locally redundant |
| `--kind StorageV2` | "That's basically going to mean ADLS Gen2" | See correction below |
| `--hns true` | Hierarchical namespace: "the equivalent of that box that you need to tick" | This is what makes it ADLS Gen2 |
| `--https-only true` | "I guess that's fine" | Rejects plain-HTTP requests |
| `--allow-blob-public-access false` | Fine | No anonymous public containers |
| `--allow-shared-key-access false` | "Fair enough" | Disables account keys and key-based SAS; you must use **Entra ID** (your login, or a managed identity) |

"We got a ton of output, which means that it was successful." The verification showed the account (named like `adlsteacher` plus a random suffix) with hierarchical namespace **true**, and it appeared in the portal.

Expanded (correction): `--kind StorageV2` only means a **general-purpose v2** storage account, the normal kind for Blob, Files, Queues and Tables. It's `--hns true` that turns that account into ADLS Gen2. Because shared-key access is off, every data command below needs `--auth-mode login` and your user needs a data role such as **Storage Blob Data Contributor** (the class had it through the subscription).

---

Q. Students got "AuthorizationFailed" creating a resource group. What happened?

A. (Evan, demo) Their accounts had no role that allowed creating resources. "I happen to be able to see your object ID from that error message. So I am gonna try and assign you as a contributor... And that should give you authorization to create a resource group." For the others, "I apparently can't do that unless I know your object ID," so he asked AI how to look them up, ran a long command, and after the break everyone could create a resource group.

Expanded: `AuthorizationFailed` is Azure's version of AWS `AccessDenied`. The message includes the **object ID** of the identity (its ID in Entra ID), the **action** (`Microsoft.Resources/subscriptions/resourcegroups/write`) and the **scope**. An admin can look up a user's object ID with `az ad user show --id <email> --query id -o tsv` and grant a role with `az role assignment create --assignee <object-id> --role Contributor --scope /subscriptions/<sub-id>`. **Contributor** lets you create and manage resources but not grant roles to others, which is why students later couldn't use "Add role assignment" (Training 28). Like in Training 28, a new role can take a few minutes to apply.

---

Q. A student got "Check name availability request must have an account name." Why?

A. (Evan) "It's probably because the storage environment variable is still undefined."

Expanded: if `$STORAGE` is empty, `--name $STORAGE` passes nothing. Run `echo $STORAGE` first; variables vanish when you open a new terminal.

---

# Demo: container, directories and a first upload

Q. How did Evan create the bronze container and folders?

A. (Evan, demo) Created the `bronze` container, verified it ("has immutability policy, has legal hold, both false. I think that's probably fine"), then created `customers/raw/` inside it. "ADLS Gen2 supports real directories and file system operations. So this is not just a facade. This is actually real directories."

Commands from the class demo (not exact):

```bash
az storage fs create --name $CONTAINER --account-name $STORAGE --auth-mode login
az storage container show --name $CONTAINER --account-name $STORAGE --auth-mode login

az storage fs directory create --name customers/raw \
  --file-system $CONTAINER --account-name $STORAGE --auth-mode login
```

Expanded: `az storage fs` ("file system") commands are the ADLS Gen2 versions of the container and blob commands. **Immutability policy** (WORM, write once read many) and **legal hold** are compliance features that stop data from being changed or deleted; you don't want them on a working Bronze container.

---

Q. How did Evan upload, check and download the file?

A. (Evan, demo) From the local folder holding `customers.csv` (the same file used in earlier classes; Evan re-shared it): "The source line in the upload command is just `./customers.csv`, which means that it assumes that customers.csv is in my local directory."

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

Then in the portal: storage account → **Storage browser** → Blob containers → `bronze` → `customers` → `raw` → `customers.csv`. You can see its properties, download it, and (to Evan's surprise) **view its contents** in the portal.

---

Q. What is the abfss:// path?

A. (Evan, demo) "Spark workloads commonly reference ADLS Gen2 using an abfss:// URL." The step just echoed the path: "that just echoes the raw text, that doesn't actually confirm anything." Reading it needs "an appropriately authenticated Spark environment," which was for the next class.

```bash
echo "abfss://$CONTAINER@$STORAGE.dfs.core.windows.net/customers/raw/customers.csv"
```

Expanded: **ABFS** is the Azure Blob File System driver in Hadoop/Spark; the extra **s** means TLS (HTTPS). The form is `abfss://<container>@<account>.dfs.core.windows.net/<path>`. Note the **dfs** endpoint (Data Lake) rather than **blob**. Training 28 reads this exact kind of path from Databricks through a Unity Catalog external location.

---

Q. With 30 minutes left, why not build Silver and Gold now?

A. (Evan) "The AI's advice was terrible. The AI just basically said, well, just demonstrate moving it up a lakehouse architecture, but not with Databricks yet... create the silver storage bucket and the gold one and just do your processing in pandas. I am not going to do that." Instead he gave a Databricks tour.

---

# A quick tour of Databricks

Q. What did Evan show in Databricks?

A. (Evan, demo) Azure portal → search **Azure Databricks** → he opened an existing workspace someone else had created ("we'll create our own Databricks workspace tomorrow") → Launch workspace.

| Area | What Evan showed |
|---|---|
| **Genie** (AI assistant) | Asked it to summarize the environment. "An AI tool which is really truly integrated with the environment... can actually give a report based on real information rather than hallucinating." It found 11 Unity Catalog catalogs (a USGS pipeline, a dbt tutorial, a DLT catalog) |
| **Workspace → New notebook** | "If you have ever used Jupyter Notebook... this will look very, very familiar." Ran on **serverless** compute |
| **Catalog** | Catalogs, `default` and `information_schema` schemas, `system`, and **hive_metastore** ("Legacy Hive Metastore") |
| **Jobs & Pipelines** | Jobs for orchestration; the **ETL pipeline** option is where you write DLT code |
| **Compute** | All-purpose compute form: Databricks Runtime version, **Photon acceleration** |
| SQL editor, Genie agents, Marketplace | Mentioned, not explored |

Expanded: on Databricks the built-in AI helper in notebooks and the editor is the **Databricks Assistant**; **Genie** (AI/BI Genie) lets business users ask natural-language questions over tables. Both use Unity Catalog metadata, which is why the answers are grounded in what actually exists.

---

Q. What was missing from the AI's Spark code, and why didn't it matter?

A. (Evan, demo) The notebook built a small DataFrame with `spark.createDataFrame`, then a **filter** (spend under 1,000 removed) and a **transformation** (a `customer_tier` column, premium or standard by total spent). Evan asked what "looks a little fishy." Students guessed types, a connector, try/except. His answer: "How does the environment know what Spark is? In an ordinary Spark environment, what you'd have to do is `from pyspark.sql import SparkSession`" and build the session. "In a Databricks notebook, Spark is a top-level variable... there is absolutely no reason to manually type out your Spark session."

Code from the class demo (not exact):

```python
from pyspark.sql import functions as F

# Plain PySpark would need this first; Databricks already provides `spark`:
# from pyspark.sql import SparkSession
# spark = SparkSession.builder.appName("demo").master("local[*]").getOrCreate()

data = [(1, "Ana", 1500.0), (2, "Ben", 800.0), (3, "Cy", 2400.0)]
df = spark.createDataFrame(data, ["customer_id", "name", "total_spent"])
display(df)

display(df.filter(F.col("total_spent") >= 1000))

display(df.withColumn("customer_tier",
        F.when(F.col("total_spent") >= 2000, "premium").otherwise("standard")))
```

Evan then moved the notebook to **Trash**, since it was in someone else's workspace.

---

Q. What is a Databricks cluster?

A. (Evan) "This create new resource thing right here, that is gonna be for creating a Databricks cluster... something like an AWS EMR cluster. That is, it's like a Hadoop cluster just on the cloud and having some extra little bells and whistles." Serverless "is only going to charge us for exactly what it uses."

Expanded: a Databricks cluster is a **Spark** cluster (a driver node plus worker nodes) running the **Databricks Runtime**; it doesn't need Hadoop or HDFS. **All-purpose** clusters are for interactive notebooks, **job** clusters start for one job and shut down, and **serverless** compute is run by Databricks with no cluster to configure.

---

Q. What did the Catalog page show about Unity Catalog and the Hive metastore?

A. (Evan, demo) "Legacy Hive Metastore. Okay, so this is an important thing to note. Everything in Databricks Unity Catalog is based on the Hive Metastore." It said "warehouse has stopped, please start or select a running warehouse," which he blamed on serverless: "In order to use a Unity Catalog managed environment in Databricks, you can't use serverless... if you're seeing the Hive Metastore here, that probably indicates that your Databricks environment is being managed by Unity Catalog, and that probably therefore means that you're going to need to provision cluster resources."

Expanded (correction): both points are backwards.

| Evan said | Correct |
|---|---|
| UC is based on the Hive metastore | `hive_metastore` is the **legacy per-workspace metastore**, shown as a separate catalog for backward compatibility. Unity Catalog is a different, account-level metastore |
| Seeing `hive_metastore` means UC is managing the workspace | It appears in both UC and non-UC workspaces. UC is shown by catalogs like the workspace catalog and `system` |
| You can't use serverless with UC | **Serverless compute requires Unity Catalog.** The notebook ran on serverless in this UC workspace |
| "Warehouse has stopped" | A **SQL warehouse** (compute for SQL and catalog browsing) wasn't running. Start it or pick a running one |

---

Q. What are Databricks Jobs & Pipelines?

A. (Evan) "A job is actually very useful because what you can do is you can use Databricks for orchestration with Databricks jobs. So that's gonna take the place of something like Airflow or of Step Functions, or in the Azure sense..." (he couldn't recall the name). "The big feature in jobs and pipelines is this ETL pipeline thing right here, because this enables us to build out Delta Live Tables."

Expanded: the Azure tool he was reaching for is **Azure Data Factory**, covered earlier the same day. **Lakeflow Jobs** (Databricks Jobs) schedule and chain notebooks, scripts, SQL and pipelines as tasks. The **ETL pipeline** option creates a **Lakeflow Declarative Pipeline** (formerly DLT). See Training 29.

---

Q. What is Photon acceleration? (an interview question)

A. (Teacher's definition) "Photon is a Databricks processing engine, which is essentially Spark Core, rewritten and optimized in C++." Spark's creators "wrote Spark in Scala because Scala is optimized for scalability," and while Scala is about as fast as Java, "there are some optimizations that you can really only get if you go to an even lower level programming language like C++." C++ is tied to the processor it's compiled for, but "Photon is never going to run on anybody else's system," only on Databricks compute, so that's fine. "Photon is pretty much the only way that you can find a version of Spark that is faster than other versions of Spark." It's not open source. "Something that you are generally gonna wanna have turned on."

Expanded (correction): Photon doesn't replace all of Spark Core. It's a **vectorized query engine** written in C++ that runs the **SQL and DataFrame** operators (scans, filters, joins, aggregations) instead of Spark's JVM code. Scheduling, the driver, RDD code and Python UDFs still run on normal Spark, and operators Photon doesn't support fall back to Spark automatically. It gives the biggest wins on SQL-heavy workloads and costs more DBUs per hour, so "generally on" is a reasonable default for SQL/ETL, not a must for everything.

---

Q. Why do people choose Databricks? (a student)

A. (Evan) "That's one of the many things... There's Photon acceleration. There's Unity Catalog. There's Delta Live Tables. There's Delta Lake. There's the Delta format." "The two premier frameworks that people want to use are Databricks and Snowflake... If you're an iOS person, you probably prefer Snowflake. If you're an Android person, you probably prefer Databricks. Databricks gives you a little bit more control at the cost of a little bit more responsibility. Snowflake gives you the ability to do things more simply at the sacrifice of some degree of control." Evan is "more of a Databricks fan." "Everything is basically gonna be leading up to either a Databricks project or a Snowflake project." If a company uses neither, it's running a legacy pipeline that works, moving back on-prem, or "just doesn't know what the latest and greatest even is."

| | Databricks | Snowflake |
|---|---|---|
| Started as | Spark / lakehouse platform | Cloud SQL data warehouse |
| Main language | Python, SQL, Scala | SQL (plus Snowpark for Python) |
| Storage | Your cloud storage (Delta, open formats) | Snowflake-managed storage (plus Iceberg tables) |
| Feel | More control, more responsibility | Simpler, less control |

---

Q. Is dbt used with Databricks?

A. (Evan) Seeing a dbt tutorial catalog in the workspace: "dbt can definitely be used with Databricks. I would say it is not the usual thing to do," because Databricks "is already perfectly capable of doing ELT code in Delta Live Tables / Lakeflow."

Expanded (correction): dbt on Databricks is actually common. The `dbt-databricks` adapter is one of dbt's most-used adapters, and many teams use dbt for SQL transformations on Databricks SQL warehouses alongside or instead of declarative pipelines. Both are valid choices.

---

# Homework and the final project

Q. What's the homework?

A. (Evan) "I'm giving you both some reading and review to do plus an outline of what we're going to be doing for the actual presentations." Also from the start of class: propose "some kind of original concept for a pipeline," and tell Evan whether you have access to PowerPoint or another slideshow tool ("it doesn't particularly matter to me, just as long as it's some sort of presentation tool"). "What the management is going to want to see is both the pipeline itself and an accompanying presentation."

---

Q. What are the final-project presentation requirements?

A. (Evan) "I don't want everybody to just present the exact same pipeline with the Citi Bike data. I'm gonna want you guys to find your own data sources and design some kind of a pipeline on either AWS or on Azure based on whatever's going to be more convenient for the particular kind of data that you use."

| Requirement | Evan's words |
|---|---|
| Audience | Management, "who are not necessarily technical": open with a **high concept**, e.g. weather patterns that could affect a company's shipments |
| Pitch style | "More of a research pitch rather than a developer pitch? Yes, exactly" |
| Core | "The pipeline construction itself": the **ingestion** stage, the **processing** stage, the **storage** stage, and the **analytics** that answer the main question |
| Architecture | "A multi-layer data lakehouse. So bronze, silver and gold," on any platform that can host it |
| Data | Your own source: "investigate... look at them, analyze them, see what kind of code you're going to need to process this data" |
| Length | Five to 10 minutes (he also said eight to 10); "the longer the better if a longer presentation will contain actually good information" |
| Date | Not set. The syllabus says end of this week, but it assumes a Monday start and class started on a Wednesday. "Probably in like five to seven working days." Evan will confirm |

Expanded: Training 28 adds advice on picking a bigger, real dataset (Kaggle, NYC taxi data) and confirms that AWS, Azure or multi-cloud are all fine.

---

# Interview-ready from today

| Question | Your one-line answer |
|---|---|
| Blob Storage vs ADLS Gen2? | ADLS Gen2 is Blob Storage with a hierarchical namespace: real directories, atomic renames and POSIX ACLs, so it's the data-lake choice |
| What is a hierarchical namespace? | Real directories in object storage, so directory operations are single metadata operations instead of copying every object |
| Why does atomic rename matter for Spark? | Spark commits output by renaming a temp folder; on flat storage that's thousands of copy+deletes and not atomic |
| How do you make a storage account ADLS Gen2? | Create a StorageV2 account with hierarchical namespace enabled (`--hns true` or the Advanced-tab checkbox) |
| What is the ADLS Gen2 path format? | `abfss://<container>@<account>.dfs.core.windows.net/<path>` |
| What is Entra ID? | Microsoft's cloud identity service (formerly Azure AD) for users, groups, service principals and managed identities |
| Entra ID vs Azure RBAC? | Entra ID authenticates who you are; RBAC role assignments (principal + role + scope) authorize what you can do |
| Tenant vs subscription? | A tenant is the organization's Entra ID directory; subscriptions inside it are billing and access containers for resources |
| What is a resource group? | A management and lifecycle container for related resources; delete it and everything inside goes too (not a network like a VPC) |
| What is a managed identity? | An Entra identity Azure creates for a resource, with credentials Azure manages, so no secrets in code |
| AWS → Azure: Kinesis, EC2, Step Functions, Redshift? | Event Hubs, Virtual Machines, Data Factory, Synapse |
| What are the open table formats? | Delta Lake, Apache Iceberg and Apache Hudi: Parquet data plus a metadata/transaction log that adds ACID, schema evolution and time travel |
| Delta vs Iceberg? | Delta is Databricks' native format (`_delta_log`); Iceberg is the vendor-neutral format used by Snowflake, AWS, BigQuery and Trino |
| What does Unity Catalog do? | Central governance for Databricks: one metastore shared across workspaces with permissions, auditing and lineage on catalogs, schemas, tables and volumes |
| Dev, UAT, prod? | Separate environments for development, user acceptance testing, and live business workloads |
| What is Photon? | Databricks' C++ vectorized engine that speeds up SQL and DataFrame operations, falling back to Spark for unsupported operators |
| Do you need a SparkSession in Databricks? | No, `spark` is predefined in every notebook |
| Synapse vs Databricks? | Synapse combines SQL warehouse, Spark pools and pipelines; many teams now use Databricks (or Fabric) for Spark and lakehouse work |
| What is Microsoft Fabric? | Microsoft's SaaS all-in-one analytics platform on OneLake: Data Factory, Spark, warehouse, real-time and Power BI with Copilot |
