---
title: "Training 28 - ADF and Databricks Medallion"
description: "The Azure Citi Bike pipeline: Azure Data Factory ingestion, Databricks setup, and Bronze, Silver and Gold notebooks ending in hourly network availability."
sidebar:
  order: 28
---

Teacher: Evan Flint

Syllabus Day 29 (per file numbering; Tue Oct 20, 2026).

Source: class notes.

**Code note:** the code below is written from the class demo plus standard ADF / PySpark / Databricks SQL syntax. It is not an exact copy of Evan's code. Evan built most of today's steps by following AI-generated step-by-step instructions on screen, so the code also came from that.

---

# Today at a glance

| # | What happened |
|---|---|
| 1 | Student updates on final-project ideas and the Azure homework. Evan's advice: pick a real dataset, and a **bigger** one (gigabytes, not kilobytes). Kaggle link shared |
| 2 | Plan for the Azure-style pipeline: **ADLS Gen2 + Azure Data Factory + Databricks** (Synapse later) |
| 3 | ADF basics: the **Copy activity** (a common interview question), and why huge migrations use **DMS** instead |
| 4 | Created a data factory, toured ADF Studio, built the **Amazon S3 linked service** with a dedicated read-only IAM user |
| 5 | Built the **ADLS Gen2 linked service** with the factory's managed identity: 403, role assignment, wait for propagation. Break |
| 6 | Fixed the S3 IAM policy, both linked services pass. Built a pipeline with a **Copy data** activity (Binary datasets). Hit "not published", "file vs directory" and container-path problems; copy succeeded |
| 7 | Why bother with ADF: re-runnable, schedulable. Fixed students' S3 and RBAC access. Break |
| 8 | Created a Databricks workspace. More student access fixes (CLI role assignments, adding a user to a workspace) |
| 9 | Found Unity Catalog already enabled. Four-step chain: **Access Connector → role on storage → storage credential → external location**, then an **external volume** |
| 10 | Notebook: listed the volume, read the JSON with Spark, created schemas. Break |
| 11 | **Bronze**: `explode` the nested stations array, write a Delta table (3,098,269 rows) |
| 12 | **Silver**: cast, filter nulls and negatives, drop duplicates, write Delta, compare row counts, `DESCRIBE HISTORY` |
| 13 | **Gold**: hourly network aggregation, "latest observation per station per hour" with a window, the five lowest-availability hours, a line chart |
| 14 | Last access fixes, homework assigned, Evan's new YouTube tech videos, "is Databricks big in interviews?" |

---

# Class admin and project updates

Q. What did Evan say about choosing a final-project dataset?

A. (Evan) Get the concept right before you build anything. Use real data, not a generated CSV: "a generated CSV is gonna be fake data... I like the aesthetic of having something real to work with so that at the end of the pipeline... we have something real to show." And go bigger: "learning how to work with a larger data set is a valuable thing, so I would encourage you to work with a larger data set if you can rather than a smaller one."

Expanded: student ideas included government unemployment vs. assistance-program data (with lag analysis), the MovieLens ratings dataset, theme-park wait times, open-source dependency risk, and retail transactions. Evan's size guidance:

| Size | Evan's take |
|---|---|
| 40 KB CSV | "Excellent for learning the ropes", too small for the project |
| ~224 MB (MovieLens 32M ratings) | "That's not even big data", but hundreds of MB is a good start because it makes you think about size |
| 5–10 GB (Kaggle has many) | Good to work with. ~5 GB is ideal for a live demo: minutes of waiting, not hours |
| Hundreds of GB to TB | What production looks like |

He suggested **NYC taxi trip records** as a big dataset that complements Citi Bike, and shared a **Kaggle** link (free account needed).

---

Q. How big is "real" big data, from Evan's experience?

A. (Evan) At JP Morgan Chase "our average file size was between... 500 gigabytes at the low end and one and a half terabytes at the high end", about a day's worth of data. For an archival job, the outputs "were saved to like one megabyte partitions and that was screwing up the archival job. As soon as I repartitioned that to 10 gigabyte partitions everything started going smoothly."

Expanded: the lesson is the **small-files problem**. Millions of tiny files mean huge metadata and task overhead, so repartitioning (`df.repartition(n)` or `coalesce(n)` before writing) to fewer, larger files fixes it. With big data, you also start caring about incremental loading, scaling and memory tuning. Evan wants you to develop the habit of asking "is there anything extra I have to do because of the size of this data?"

Expanded (correction): 10 GB per file is unusually large. The common target for Parquet/Delta files is roughly **128 MB to 1 GB** each (Delta's `OPTIMIZE` aims for about 1 GB). A "500 GB file" is best read as a 500 GB dataset or partition made of many files. The direction of his fix (far fewer, bigger files) is right.

---

Q. Can the project use something other than Azure?

A. (Evan) Yes. The planning document said Azure only because "I generated it on the fly and maybe didn't give it perfect information. You can choose your own tech stack." AWS, on-prem, or ideally **multi-cloud** if you have the time. If you're behind on Azure, an AWS pipeline is "totally fine" for the demo.

Expanded: company managers will watch the presentations. Evan said presenting a whole pipeline isn't a daily task for most data engineers (architects present designs for approval; data scientists usually present results), but it's a trial run for interviews, where "the onus is going to be on you to explain the technology and explain what you've done with the technology."

---

Q. Do jobs use both Azure and AWS? (a student)

A. (Evan) "It is entirely possible that a job would prefer a multi-cloud architecture. It's not going to be every job... but it absolutely exists."

Expanded: today's demo (S3 → ADF → ADLS) is the class's first multi-cloud pipeline.

---

Q. Is there a particular "workspace" to use on Azure? (a student)

A. (Evan) Workspaces are "more of a Databricks concept than a general Azure concept." The class would create a dedicated Databricks workspace.

Expanded (correction): Databricks isn't the only one. Azure also has **Synapse workspaces** (Training 31), **Log Analytics workspaces** and **Microsoft Fabric workspaces**. Each is a container for one service's assets, not a general Azure-wide thing, so Evan's point mostly holds.

---

# The Azure pipeline plan

Q. What does the Azure-style pipeline look like?

A. (Evan) It's "rooted in the use of mainly ADLS, ADF, Databricks and eventually Synapse," and for now just the first three, "because that's going to be sort of the core organizational side of what most pipelines on Azure are going to look like." It's analogous to what the class did on AWS.

Expanded:

```
AWS S3 (Bronze JSON) ──ADF Copy activity──▶ ADLS Gen2 (bronze container) ──Unity Catalog volume──▶ Databricks notebook
                                                                                   Bronze ▶ Silver ▶ Gold Delta tables ▶ SQL / charts
```

| Job | AWS pipeline (Training 19/20, 24) | Azure pipeline (today) |
|---|---|---|
| Object storage / data lake | S3 | ADLS Gen2 (storage account + container) |
| Move / orchestrate data | Lambda, Step Functions, `aws s3 cp` | Azure Data Factory |
| Transform with Spark | Glue / EMR Serverless | Databricks notebook |
| Table format | Parquet files | Delta tables |
| Warehouse / serving | Redshift Serverless | Gold Delta tables (Synapse in Training 31) |
| Identity | IAM roles and policies | Entra ID, RBAC role assignments, managed identities |

Evan's plan for later: point the existing Streamlit + AI app (still on AWS) at the Azure Gold data instead of building an Azure VM deployment.

---

# Azure Data Factory (ADF)

Q. What is a Copy activity in Azure Data Factory?

A. (Teacher's definition) "The things that you can do in Azure Data Factory are called activities... the most basic one... it's the copy activity. It's basically exactly what it sounds like: it serves to take data that is in one place and copy it to another place. Simple as that." Ideally it would be as simple as Ctrl+C and Ctrl+V, "but because we're dealing with significant amounts of data, it isn't that simple."

Expanded: a Copy activity reads from a **source dataset** and writes to a **sink dataset** (ADF's word for destination). It can copy files as-is (Binary) or convert formats (JSON → Parquet, CSV → SQL table) and map columns, but it doesn't do real transformations. For transformations you use a **Data Flow** activity, or call **Databricks** (Notebook activity) or a stored procedure.

| ADF activity type | Examples | Does |
|---|---|---|
| Data movement | Copy data | Moves data from source to sink |
| Data transformation | Data Flow, Databricks Notebook, Stored Procedure | Changes the data |
| Control flow | ForEach, If Condition, Wait, Execute Pipeline, Get Metadata | Logic and orchestration |

---

Q. What are the main ADF building blocks?

A. (from the homework reading, used in class)

| Building block | What it is | Today's example |
|---|---|---|
| **Pipeline** | A logical group of activities that runs as a unit | `pl_copy_citibike_s3_to_adls` |
| **Activity** | One step in a pipeline | Copy data, renamed `copy_citibike_raw` |
| **Linked service** | A connection string: *how* to connect and authenticate to a system | `s3_citibike` (access key), ADLS Gen2 (managed identity) |
| **Dataset** | A named pointer to specific data *inside* a linked service: folder, file, format | Binary dataset on `bronze/citibike/` in S3; Binary dataset on the `bronze` container |
| **Integration runtime (IR)** | The compute that actually runs activities and moves the bytes | The default **AutoResolveIntegrationRuntime** (Azure IR) |
| **Trigger** | What starts a pipeline run: schedule, tumbling window, storage event, manual | None yet; Evan ran it with Debug |

Expanded: linked service vs dataset is the classic interview pair. The linked service is like a database connection; the dataset is like a table name used over that connection. Integration runtimes come in three types: **Azure IR** (managed, in the cloud, the default), **self-hosted IR** (software you install to reach on-prem or private-network data) and **Azure-SSIS IR** (to lift-and-shift SSIS packages).

---

Q. When do you use DMS instead of ADF?

A. (Evan) For data "big enough to be called a migration... we would use Azure DMS." "Data migration service is called that on all three cloud platforms... There's AWS DMS, there's Azure DMS, there's GCP DMS." Use it to take something like "30 terabytes of data in one database and migrate it to a new database that's going to be organized in more or less the same way. You're not doing any transformations." Citi Bike is small enough for ADF, and ADF is the more commonly used tool.

Expanded (correction): the full name is **Database Migration Service** on all three clouds (AWS DMS, Azure Database Migration Service, Google Cloud Database Migration Service). It's for **databases** (schemas, tables, ongoing CDC replication), not for bulk files. For large file or object-storage migrations you'd use **AzCopy**, **Azure Storage Mover**, **Azure Data Box** (physical devices), or **AWS DataSync** on the AWS side. ADF is still a valid choice for moderate S3 → ADLS copies like today's. See Training 24 for AWS DMS and CDC.

---

Q. How did Evan create the data factory?

A. (Evan, demo)

| Step | Action |
|---|---|
| 1 | Confirmed the Citi Bike JSON still exists in S3 (`aws s3 ls ... --profile company`) |
| 2 | Azure portal → **Data factories** → Create. Subscription, his resource group, name like `adf-citibike-training`, region East US 2. No encryption or tags for a demo |
| 3 | Review + create, wait for deployment, **Go to resource** |
| 4 | **Launch studio** to open ADF Studio |

Expanded: ADF Studio has **Home, Author, Monitor, Manage** and a Learning center. **Author** is where you build pipelines, datasets and data flows. **Manage** holds linked services, integration runtimes, triggers and Git settings. **Monitor** shows pipeline and activity runs. The studio also showed a banner pushing **Microsoft Fabric** (Fabric Data Factory is the successor experience).

---

Q. How did Evan connect ADF to S3?

A. (Evan, demo) Manage → Linked services → New → **Amazon S3**. The name can't use dashes, so underscores. It wants an **access key and secret key**, and he didn't want to expose his admin credentials, so he created a **dedicated IAM user** with read-only S3 access: "otherwise I'd be exposing administrator credentials."

| Step | Action |
|---|---|
| 1 | IAM → Users → Create user `adf-citibike-reader` |
| 2 | Attach the `AmazonS3ReadOnlyAccess` managed policy |
| 3 | Add an **inline policy** (JSON editor) allowing `s3:ListBucket`, `s3:GetBucketLocation`, `s3:GetObject` |
| 4 | Security credentials tab → Create access key → use case "Third-party service" → acknowledge the "use temporary credentials" warning |
| 5 | Paste the access key ID and secret into the ADF linked service. Integration runtime: AutoResolve |
| 6 | Tested the same keys from the CLI: same output as his admin profile |

Inline policy, from the class demo (not exact), after the student-bucket fixes later in class:

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

Expanded: `ListBucket` and `GetBucketLocation` apply to the **bucket** ARN; `GetObject` applies to **objects**, so its ARN needs `/*`. Mixing those up is the most common S3 policy bug, and it's exactly what blocked students later in class. Evan shared this reader user's access key with the class so everyone could build their own S3 linked service against their own bucket.

Expanded (correction): Evan said he had no problem showing this access key because it's a dedicated read-only user. That limits the damage, but a long-lived key posted in a chat is still a live credential: anyone who gets it can read every bucket in that policy. Better practice: store the secret in **Azure Key Vault** and reference it from the linked service, rotate or delete the key when the class is done, and prefer temporary credentials where the tool supports them.

---

Q. How did Evan connect ADF to ADLS Gen2?

A. (Evan, demo) New linked service → **Azure Data Lake Storage Gen2** → his subscription and storage account → authentication **System-assigned managed identity**. Test connection: **failed**. "If connection fails, the ADF managed identity probably lacks data plane permissions," fixed by adding a role assignment on the storage account.

| Step | Action |
|---|---|
| 1 | Storage account → **Access control (IAM)** (not Entra ID; he went there first by mistake) |
| 2 | Add → **Add role assignment** → role **Storage Blob Data Contributor** |
| 3 | Assign access to **Managed identity** → type **Data factory** → select his factory |
| 4 | Review + assign. Tested again: still a 403 |
| 5 | Break. After the break, with no other change: **connection successful** |

Expanded: the reason it "magically worked" is **RBAC propagation delay**. Azure role assignments can take several minutes to take effect (Microsoft says up to about 10 minutes, sometimes longer). A **managed identity** is an identity Azure creates for a resource (here the data factory) so it can authenticate to other Azure services with no passwords or keys stored anywhere. Assigning a data-plane role like Storage Blob Data Contributor to that identity is the whole setup. The `Contributor` role on a subscription does **not** let you read blob data; that needs a "Storage Blob Data ..." role.

| Plane | What it controls | Example role |
|---|---|---|
| Control (management) plane | Create, delete, configure the storage account | Contributor, Owner |
| Data plane | Read and write the blobs/files inside | Storage Blob Data Reader / Contributor / Owner |

---

Q. How did Evan build the copy pipeline?

A. (Evan, demo)

| Step | Action |
|---|---|
| 1 | Author → Factory resources → **+** → Pipeline, named `pl_copy_citibike_s3_to_adls` |
| 2 | Activities → Move and transform → drag **Copy data**, rename to `copy_citibike_raw` |
| 3 | **Source** tab → New dataset → Amazon S3 → format **Binary** → linked service `s3_citibike` → path: bucket + directory `bronze/citibike`, file name blank, **Recursively** checked, no compression, no "delete after" |
| 4 | **Sink** tab → New dataset → ADLS Gen2 → Binary → ADLS linked service → path: the `bronze` container |
| 5 | Copy behavior **Preserve hierarchy** |
| 6 | **Validate** (no errors) → **Debug** to run it → **Publish all** |
| 7 | Checked the Output panel, then the storage account's Storage browser |

Expanded: **Binary** format means "copy the bytes as-is, don't parse them", which is right for a raw Bronze copy and the fastest option. **Preserve hierarchy** keeps the S3 folder structure (feed/date/hour) in ADLS. **Debug** runs the current draft without publishing or a trigger; production runs use a published pipeline plus a trigger.

---

Q. What went wrong during the ADF setup, and how was each fixed?

A. (Evan, demo)

| Error / symptom | Cause | Fix |
|---|---|---|
| `aws s3 ls` error | Forgot `--profile company` | Add the profile |
| "Broken pipe" error when piping the S3 listing | The listing was piped into `head`, which closes early | Harmless, ignore it |
| ADLS linked service test: 403 | Factory managed identity had no data-plane role | Storage Blob Data Contributor on the storage account, then wait for propagation |
| S3 linked service test: "Credential is incorrect or does not have permission" | The inline policy lacked a list permission | Edited the IAM policy, test passed |
| ADLS linked service not in the sink dropdown | The first linked service was never saved/published | Recreated it, then clicked **Publish all** ("This resource has not been published by your data factory") |
| Copy failed after 15 s: "the operation is on a file citibike" | `citibike` was in the file-name field, so ADF treated it as a file | Put `bronze/citibike` in the **directory** field, file name blank |
| Copy succeeded but the sink path was wrong | The storage-account name was typed as a folder | Sink path = container `bronze` only. A **container** is the equivalent of an S3 bucket |
| Storage browser: "You do not have permissions to list the data" | The portal browses as **your Entra user**, not the factory's identity | Gave his own user Storage Blob Data Contributor, waited, reloaded |
| (Students) `ListBucket` not authorized on their own bucket | Policy `Resource` only listed Evan's bucket | Made `Resource` a list and added each student's bucket ARN |
| (Students) S3 403 on `GetObject` | `GetObject` was only allowed on Evan's bucket objects | Added `arn:aws:s3:::<student-bucket>/*` |
| (Students) No "Add role assignment" button | Students lack Owner / User Access Administrator | Send Evan the resource group, data factory and storage account names; he assigns the role (portal or CLI) |

Expanded: Evan's comment on Azure vs AWS: "With AWS when you change permissions the effect is immediate, but I guess with Azure it's just not going to be that way."

Expanded (correction): AWS IAM is also **eventually consistent**. Changes usually apply within seconds, but AWS documents that they can take a short time to propagate. Azure RBAC delays are just more noticeable (minutes).

---

Q. Why go through all that just to copy some files?

A. (Evan) First, "often that's going to be the way the company wants you to do it." Second, "now that we've got all this copy activity set up... we can just run it again and again and again at regular intervals and all of the setup is already done. From here on out we just press debug or we add a trigger." He said a trigger could receive an event from AWS, so new data in S3 would automatically be copied to Azure. "Yes, the initial setup is a pain... but once the setup is done it's done."

Expanded (correction): ADF's **storage event triggers** only watch Azure Blob / ADLS Gen2, not S3. To react to S3 arrivals you'd use a **schedule** or **tumbling window trigger** (with the Copy activity filtering by last-modified time), or have an AWS **Lambda** on the S3 event call ADF's REST API to start a pipeline run. Also, "press debug" is for testing; repeatable production runs use a published pipeline with a trigger.

---

Q. How do you assign the role from the CLI for several students?

A. (Evan, demo) He followed CLI steps: set environment variables, look up the data factory's principal ID, get the storage account's resource ID, create the role assignment, verify it. The `az datafactory` command needed an extension, which the CLI offered to install.

Code from the class demo (not exact):

```bash
RG="<resource-group>"; ADF="<data-factory>"; SA="<storage-account>"

ADF_PRINCIPAL_ID=$(az datafactory show -g "$RG" -n "$ADF" --query identity.principalId -o tsv)
SA_ID=$(az storage account show -g "$RG" -n "$SA" --query id -o tsv)

az role assignment create \
  --assignee-object-id "$ADF_PRINCIPAL_ID" --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Contributor" --scope "$SA_ID"

az role assignment list --assignee "$ADF_PRINCIPAL_ID" --scope "$SA_ID" -o table
```

Expanded: `--scope` set to the storage account's ID gives the role on that account only, which is least privilege. Scoping it to the resource group or subscription would cover every storage account there.

---

# Azure Databricks setup

Q. How did Evan create the Databricks workspace?

A. (Evan, demo) Azure portal → **Azure Databricks** → Create → his resource group → workspace name like `citibike-workspace-teacher` → Review + create. After deployment: Go to resource → **Launch workspace** → New → **Notebook** (named `01_citibike_bronze_to_silver`).

Expanded: students should create **their own** workspace; use Evan's only if you lack permissions. Unity Catalog needs the **Premium** tier. A new workspace is usually **serverless-compute enabled**, so a notebook can attach to serverless compute without creating a cluster.

---

Q. How do you tell if a workspace has Unity Catalog?

A. (Evan, demo) He assumed it wasn't Unity Catalog-enabled, then checked: left sidebar → **Catalog**. If Unity Catalog is enabled you see catalogs such as the workspace catalog and `system`. It was enabled, which he called "phenomenally fantastic news" because earlier this year Unity Catalog setup "was no joke... a very, very difficult and time-consuming thing to do."

Expanded: new Azure Databricks workspaces are **automatically enabled for Unity Catalog** (a metastore is attached and a workspace catalog is created with the workspace's name). **Unity Catalog** is Databricks' governance layer: one place for permissions, auditing and lineage on catalogs, schemas, tables, volumes and the cloud storage behind them. It uses a three-level name `catalog.schema.table`. See Training 29.

---

Q. How did Evan connect Databricks to ADLS Gen2?

A. (Evan, demo) "Access connector for Azure Databricks, to managed identity, to Unity Catalog storage credential, to external location. So four steps to do something that seems simple... the magic of cloud." Databricks "does not automatically inherit permissions" from what was granted to ADF.

| Step | Where | Action |
|---|---|---|
| 1 | Azure portal | Create an **Access Connector for Azure Databricks** in your resource group. Note its **resource ID** |
| 2 | Storage account → Access control (IAM) | Add role assignment: **Storage Blob Data Contributor** → Managed identity → select *your* connector (not one someone else made) |
| 3 | Databricks → Catalog → External data → **Credentials** | Create credential → **Storage credential**, type **Azure Managed Identity** → paste the connector's resource ID (managed identity ID blank for system-assigned) |
| 4 | Databricks → Catalog → External data → **External locations** | Create external location → type ADLS → URL `abfss://bronze@<account>.dfs.core.windows.net/` → choose the credential. Got "File permissions not verified" → skip file events → **Force create** |
| 5 | Catalog Explorer → catalog → `default` schema | Create volume → **External volume** `citibike_bronze_landing` on that location |
| 6 | Notebook | List the volume to test |

Expanded: each piece has one job.

| Object | What it is |
|---|---|
| **Access Connector** | An Azure resource whose only purpose is to own a managed identity that Databricks can use |
| **Storage credential** | Unity Catalog's record of that identity ("use this connector to authenticate") |
| **External location** | A storage path (`abfss://...`) paired with a storage credential. Controls who may use that path |
| **External volume** | A Unity Catalog object over files in an external location, readable at `/Volumes/<catalog>/<schema>/<volume>/` |
| **Managed volume** | Same idea, but the files live in Unity Catalog's own managed storage (no RBAC setup needed) |

---

Q. How do you give a classmate access to your workspace?

A. (Evan, demo) Workspace → profile icon → **Settings** → **Identity and access** → Users → Add (by email), with every permission except admin. It said the user "already exists in the account", meaning the person was already in the Databricks account and only needed adding to this workspace.

Expanded: Databricks has an **account** level (all workspaces, the metastore, identities synced from Entra ID) and a **workspace** level. A user can exist in the account without being assigned to a workspace, which gives an "access denied" when they open its URL.

---

# Databricks notebooks and reading the data

Q. What is a Databricks notebook?

A. (Evan) Cells "can operate in Markdown, Python, SQL, Scala or R. In the vast majority of our use cases, we're going to be using Python and SQL." R "is more the domain of data scientists than data engineers." When he pasted SQL into a cell, the cell's language switched to SQL automatically.

Expanded: a notebook attaches to **compute** (serverless or a cluster). `spark` (the SparkSession) and `dbutils` are already defined. Each cell has a default language, and you can switch one cell with a **magic command**: `%sql`, `%python`, `%md`, `%scala`, `%r`, `%sh`. Variables from earlier cells stay defined while the session lives, so run cells in order (this caused a `NameError` today).

---

Q. How did Evan test the connection and read the JSON?

A. (Evan, demo) Listed the volume, which showed `gbfs_discovery`, `station_information`, `station_status` and `system_information` with size 0. Reading one file with its full `https://` URL failed. Reading through the volume path worked and returned deeply nested JSON. Asked whether that was really ADLS, the answer was: "you're already reading data from ADLS Gen2... Unity Catalog is providing a governed way to access it."

Code from the class demo (not exact):

```python
landing_path = "/Volumes/<catalog>/default/citibike_bronze_landing/"
display(dbutils.fs.ls(landing_path))

df = (spark.read
      .option("multiLine", "true")
      .json(landing_path + "station_information/<date>/<hour>/<file>.json"))
df.printSchema()
display(df.limit(10))
```

Expanded: size 0 is normal for **directories** in a listing; only files have sizes. Three path styles you'll see:

| Path | What it is | Use it? |
|---|---|---|
| `https://<account>.blob.core.windows.net/...` | Browser / REST URL | No, Spark can't read it this way |
| `abfss://<container>@<account>.dfs.core.windows.net/...` | Direct ADLS Gen2 path (needs an external location) | Yes |
| `/Volumes/<catalog>/<schema>/<volume>/...` | Unity Catalog volume path (the `dbfs:` prefix is optional) | Yes, the governed way |

Evan said nested JSON "really shouldn't be in a data frame, but that's what processing is for."

Expanded (correction): nested data is perfectly valid in a Spark DataFrame. Spark has `struct`, `array` and `map` column types, and `printSchema()` shows the nesting. The reason to flatten is that SQL queries, joins and BI tools want flat, typed columns.

---

Q. How did Evan create the schemas?

A. (Evan, demo) A SQL cell:

```sql
CREATE SCHEMA IF NOT EXISTS <catalog>.bronze;
CREATE SCHEMA IF NOT EXISTS <catalog>.silver;
-- later: CREATE SCHEMA IF NOT EXISTS <catalog>.gold;
```

Expanded: in Unity Catalog a **schema** (also called a database) sits inside a catalog and holds tables, views and volumes. Using one schema per medallion layer (`bronze`, `silver`, `gold`) gives names like `<catalog>.silver.station_history`.

---

# Bronze: flattening the JSON

Q. What does "flatten" mean, and how did Evan do it?

A. (Teacher's definition) "If there's an object inside an object inside an object, it takes the objects that are inside, that is the nested objects, and it moves them to the top level so that they're all treated as equal... which can then be converted into columns in an actual data frame." "All we really needed was the explode function."

Code from the class demo (not exact):

```python
from pyspark.sql import functions as F

root = "/Volumes/<catalog>/default/citibike_bronze_landing/"
src = root + "station_status/"

raw = (spark.read
       .option("multiLine", "true")
       .option("recursiveFileLookup", "true")
       .json(src))

bronze_df = (raw
    .select(F.explode("data.stations").alias("station"),
            F.col("last_updated").alias("snapshot_epoch"),
            F.col("_metadata.file_path").alias("source_file"))
    .select("station.*", "snapshot_epoch", "source_file")
    .withColumn("ingested_at", F.current_timestamp()))

(bronze_df.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("<catalog>.bronze.station_status"))
```

Expanded (correction): two different operations do the flattening, and it helps to name them separately.

| Operation | What it does | Here |
|---|---|---|
| `F.explode(array_col)` | Turns **one row with an array** into **one row per element** | Each file's `data.stations` array (about 2,500 stations) → one row per station |
| `select("struct_col.*")` | Turns a **struct's fields** into **top-level columns** | `station` → `station_id`, `num_bikes_available`, `num_docks_available`, `is_installed`, `is_renting`, `is_returning`, `last_reported`, ... |

`recursiveFileLookup` reads every file in all the date/hour subfolders. `multiLine` is needed because each GBFS file is one JSON document spread over many lines, not one JSON object per line. `_metadata.file_path` records which file each row came from.

---

Q. What do the write options mean?

A. (Evan) "We're using Delta format as our output storage, which is the normal kind of format to use when you're working with Delta Lake." `overwriteSchema` true "means we're replacing the original schema with this new one." Then `saveAsTable` with the three-part name.

Expanded:

| Option | Meaning |
|---|---|
| `format("delta")` | Write a Delta table: Parquet data files plus a `_delta_log` transaction log |
| `mode("overwrite")` | Replace the table's data (a full reload). Delta keeps the old version in history |
| `option("overwriteSchema", "true")` | Allow the new write to change columns or types. Without it, Delta's **schema enforcement** rejects a mismatched write |
| `saveAsTable("cat.schema.table")` | Register a **managed** table in Unity Catalog (files in managed storage) |

Result: `SELECT COUNT(*)` on Bronze returned **3,098,269 rows** (a week of 5-minute-ish snapshots × ~2,500 stations).

---

# Silver: cleaning and deduplicating

Q. What did the Bronze → Silver job do?

A. (Evan, demo) Cast columns, convert the epoch to a timestamp, filter out null station IDs and negative counts ("you can't have negative one bikes available at the station, that doesn't make any sense"), and drop duplicates on station ID + snapshot.

Code from the class demo (not exact):

```python
bronze = spark.table("<catalog>.bronze.station_status")

silver_df = (bronze
    .select(
        F.col("station_id").cast("string").alias("station_id"),
        F.col("num_bikes_available").cast("int").alias("num_bikes_available"),
        F.col("num_docks_available").cast("int").alias("num_docks_available"),
        F.col("snapshot_epoch").cast("long").alias("snapshot_epoch"),
        "source_file")
    .withColumn("snapshot_time", F.to_timestamp(F.from_unixtime("snapshot_epoch")))
    .filter(F.col("station_id").isNotNull())
    .filter(F.col("num_bikes_available") >= 0)
    .filter(F.col("num_docks_available") >= 0)
    .dropDuplicates(["station_id", "snapshot_epoch"]))

(silver_df.write.format("delta").mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("<catalog>.silver.station_history"))
```

Evan's explanations, with corrections:

| Piece | Evan said | Expanded (correction) |
|---|---|---|
| `.alias("station_id")` with the same name | "Not sure why" | `cast()` renames the column to something like `CAST(station_id AS STRING)`, so the alias restores the original name |
| `.cast("long")` | "That basically just means it's a longer string of characters" | Wrong. **Long** (`LongType`, `BIGINT`) is a **64-bit integer**, not a string. Epoch timestamps in seconds fit in an int today, but in milliseconds they don't, so long is the safe choice |
| `from_unixtime` | Creates a snapshot time column | Converts epoch seconds to a timestamp string; `to_timestamp` makes it a real `TIMESTAMP` |
| `dropDuplicates([...])` | "Ensures that we've only got one unique value for every one unique value in both of these columns" | Keeps **one row per unique combination** of `station_id` + `snapshot_epoch`. Which duplicate survives is not guaranteed; use a window with `row_number()` if it matters |

Expanded: Evan noticed some station IDs looked different from the others and said "we might want to do more validation on this data." Citi Bike's GBFS feed uses UUID-style station IDs (the old numeric ID is kept in a separate `legacy_id` field), so IDs can look inconsistent at a glance. That's one reason to cast them to **string**, never to a number.

---

Q. How did Evan validate Silver?

A. (Evan, demo) Compared row counts with a `UNION ALL`, inspected Silver rows, and ran `DESCRIBE HISTORY`.

```sql
SELECT 'bronze' AS layer, COUNT(*) AS row_count FROM <catalog>.bronze.station_status
UNION ALL
SELECT 'silver', COUNT(*) FROM <catalog>.silver.station_history;

DESCRIBE HISTORY <catalog>.silver.station_history;
```

Bronze had about 3,098,000 rows and Silver about 3,090,000, so roughly 7,500 rows were removed (duplicates and invalid values). "The validation's worked, we've got a smaller row count in Silver than we did in Bronze."

Expanded: `DESCRIBE HISTORY` first gave a syntax error because it was on the same line as the previous statement; put each SQL statement on its own (ending with `;`). The history showed **version 0** with operation **CREATE OR REPLACE TABLE AS SELECT**. Every Delta write adds a version, which is what makes **time travel** possible (`SELECT * FROM t VERSION AS OF 0`). See Training 29's Delta Lake section for time travel, `RESTORE`, `MERGE` and `VACUUM`.

---

Q. Why does the history say CREATE OR REPLACE TABLE AS SELECT when the code never says that?

A. (Evan) "Create or replace table as select is the syntax that you're going to use in SQL-based ELT code... that's the kind of thing that you would write in dbt." The PySpark code is "logically equivalent": build a DataFrame from Bronze with these columns, transformations and filters, then save it as a table. "The syntax looks different but the logic is exactly the same."

Expanded: `df.write.mode("overwrite").saveAsTable(...)` is recorded by Delta as a CTAS-style replace. The SQL version of today's Silver step would be `CREATE OR REPLACE TABLE silver.station_history AS SELECT ... FROM bronze.station_status WHERE ...`, which is what a dbt `table` materialization runs (Training 15).

---

Q. Where do you see Delta tables in the UI?

A. (Evan, demo) **Catalog** (Catalog Explorer) → catalog → schema → table. It shows the table's **schema** (columns and types), "not actually our files", and not rows unless you query. "The interface is just a little bit different than it is in a storage bucket like ADLS or S3."

Expanded: Catalog Explorer also has tabs for Sample data, Details (including the storage location), History, Lineage and Permissions. To see the files behind a table, run `DESCRIBE DETAIL <table>` for its location. Managed table files are deliberately hidden in managed storage; you're meant to use the table, not the files.

---

# Gold: hourly network availability

Q. What belongs in the Gold layer?

A. (Evan) "Aggregated data is what you want in the gold layer." A basic aggregation "is a perfectly acceptable test for just being able to get a gold layer going." It answers questions like "on the 8th of October at 8 PM, how many total bikes were observed?", and you can pass it to "a BI tool to create a visual, or pass it to an AI to ask it a natural-language question."

Expanded: medallion summary.

| Layer | Contains | Today |
|---|---|---|
| Bronze | Raw or minimally processed data, plus load metadata | Flattened station rows + `source_file`, `ingested_at` |
| Silver | Cleaned, typed, validated, deduplicated | Casts, null/negative filters, one row per station per snapshot |
| Gold | Business-level aggregates for analytics | One row per hour for the whole network |

---

Q. How was the Gold table built?

A. (Evan, demo) First version: add an `hour` column with `date_trunc`, group by hour, aggregate. "Remember, to aggregate you first need to group by." Then the AI suggested a better version that keeps only the **latest observation for each station within each hour** using a window and `row_number()`. Evan described it as "an additional way of getting rid of duplicates... if row number is one then it is included; if it is any number other than one then we get rid of it."

Code from the class demo (not exact):

```python
from pyspark.sql import Window

silver = spark.table("<catalog>.silver.station_history")

w = (Window.partitionBy("station_id", "hour")
           .orderBy(F.col("snapshot_time").desc()))

latest_hourly = (silver
    .withColumn("hour", F.date_trunc("hour", "snapshot_time"))
    .withColumn("rn", F.row_number().over(w))
    .filter("rn = 1")
    .drop("rn"))

gold_df = (latest_hourly.groupBy("hour")
    .agg(F.countDistinct("station_id").alias("stations_reporting"),
         F.sum("num_bikes_available").alias("total_bikes_available"),
         F.sum("num_docks_available").alias("total_docks_available"),
         F.round(F.avg("num_bikes_available"), 2).alias("avg_bikes_per_station"))
    .orderBy("hour"))

(gold_df.write.format("delta").mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("<catalog>.gold.hourly_network_availability"))
```

Expanded (correction): this isn't really deduplication. Silver already has one row per station per snapshot, but a station can have **several snapshots in one hour**. Summing all of them would count the same bikes several times. The window picks **one** snapshot per station per hour (the latest, which is why the order is `desc`), so the hourly totals are a true point-in-time picture. The window must partition by **station and hour**; partitioning by station alone would keep just one row per station for the whole dataset. Evan saw the two versions "look similar" because his snapshots were roughly hourly.

Example Gold row from class: Oct 7, 18:00, 2,520 stations reporting, 34,772 bikes available, 31,756 docks available.

---

Q. What was the Gold query?

A. (Evan, demo) The five hours with the fewest bikes across the network:

```sql
SELECT hour, stations_reporting, total_bikes_available,
       total_docks_available, avg_bikes_per_station
FROM <catalog>.gold.hourly_network_availability
ORDER BY total_bikes_available ASC
LIMIT 5;
```

The lowest was 32,148 bikes (Oct 15, 9 PM), then Oct 14 9 PM, Oct 13, and Oct 15 10 PM. Evan expected possible zeros and didn't get them. His reading: "people in New York City are most likely to want to be riding one of these bikes at around 9 or 10 PM."

Expanded: a reasonable first guess, but check before you present it. Fewer bikes docked can mean more bikes in use, but also bikes being rebalanced by trucks, or **fewer stations reporting** that hour (the homework says to consider `stations_reporting`). Comparing `avg_bikes_per_station` or bikes per reporting station is fairer than the raw total.

---

Q. How do you make a chart in Databricks?

A. (Evan, demo) `display(df)` shows a table; then click **+** next to the results → **Visualization** → Line chart (hour on X, total bikes and total docks on Y) → Save. He said bikes and docks "would be inverse, wouldn't they, since if a bike is in a dock then the dock isn't available, and neither is the bike."

Expanded (correction): the inverse shape is right, but the reason is slightly off. A bike sitting in a dock **is** available to rent; it's the **dock** that's taken. So for each station, bikes available + docks available ≈ capacity (minus disabled bikes and docks). When a bike is ridden away, bikes go down by one and docks go up by one, which is why the two lines mirror each other.

---

# Databricks in interviews

Q. Is Databricks big in interviews, and is it Azure Databricks specifically? (a student)

A. (Evan) "The ADF and Databricks stuff really genuinely is important. This is one of the most important things to understand in terms of taking interviews because so many interviews are Databricks-centric." It's "Databricks in general. Azure Databricks is only different from any other kind of Databricks in that it makes it easier to access other Azure resources." On AWS or GCP you do a few more configuration and authorization steps, "but what you do in the Databricks notebook, the Spark operations, the data operations themselves, those are going to be the same across cloud platforms." Databricks can also run on its own, not tied to your cloud account.

Expanded:

| | Apache Spark | Databricks |
|---|---|---|
| What | Open-source distributed processing engine | A managed platform built by Spark's creators, around Spark |
| You manage | Clusters, configs, libraries, storage, security | Mostly just your code |
| Adds | — | Notebooks, serverless compute, Delta Lake, Unity Catalog, Jobs / Lakeflow, SQL warehouses, MLflow, optimized runtime (Photon) |

See Training 29 for Lakeflow Declarative Pipelines, the next step after today's notebook pipeline.

---

# Homework and announcements

Q. What's the homework?

A. (Evan) "A little bit of reading. Try to get as caught up to the level of Databricks that I'm at as you can," and work on the presentation idea, ideally starting the actual pipeline and presentation. "Let me know tomorrow if this homework assignment winds up bogging you down." For access or permission problems, send Evan the exact error, the resource name and the step, rather than spending hours on it.

Expanded: the written assignment (`Homework - Training 28 (Assignment)`):

| Part | What |
|---|---|
| 1 | Reading: ADF (pipelines, activities, linked services, datasets, IR, managed identities), Databricks vs Spark, Delta Lake, medallion, Unity Catalog, external volumes |
| 2 | Hands-on: S3 → ADF → ADLS Gen2; Access Connector, storage credential, external location, volume; Bronze, Silver, Gold Delta tables; a Gold SQL query |
| 3 | Six short written questions |
| 4 | Screenshots, notebook, answers, status |
| Optional | `DESCRIBE HISTORY`, time travel, line chart, `MERGE` for latest station status, Auto Loader for incremental loads |

---

Q. What else did Evan share?

A. (Evan) New technology videos on his YouTube channel, published that day: **Databricks, Snowflake, Python, SQL, Hadoop and Spark**. Informal, not assigned, but "this absolutely ties into what we've been doing today." The Databricks one has imperfect editing and "a little bit of AI weirdness," but "the information is pretty good."

---

# Interview-ready from today

| Question | Your one-line answer |
|---|---|
| What is a Copy activity in ADF? | The basic ADF activity that copies data from a source dataset to a sink dataset, optionally converting format, with no real transformation |
| Linked service vs dataset? | A linked service is the connection and authentication to a system; a dataset points to specific data (path, file, format) inside it |
| What is an integration runtime? | The compute that runs ADF activities and moves the data: Azure IR (managed), self-hosted IR (on-prem/private networks), or Azure-SSIS IR |
| Why a managed identity for ADLS? | Azure manages the identity's credentials, so no keys are stored; you just grant it an RBAC role like Storage Blob Data Contributor |
| Why did the connection fail right after granting the role? | Azure RBAC role assignments take a few minutes to propagate |
| ADF or DMS for a migration? | DMS (Database Migration Service) for moving whole databases with little or no transformation; ADF for pipelines and moderate data copies; AzCopy / Data Box for bulk files |
| How does Databricks reach ADLS under Unity Catalog? | Access Connector (managed identity) → Storage Blob Data role → storage credential → external location → external volume or tables |
| External vs managed volume? | External: files stay in your ADLS path governed by UC; managed: files live in UC's managed storage |
| What does `explode` do? | Turns each element of an array column into its own row; `struct.*` then turns struct fields into columns |
| Bronze, Silver, Gold? | Raw data plus load metadata; cleaned, typed, deduplicated data; business-level aggregates |
| What does Delta add over plain Parquet/JSON? | ACID transactions, schema enforcement, a transaction log with version history (time travel), MERGE/UPDATE/DELETE |
| How do you keep the latest row per key? | `row_number()` over a window partitioned by the key, ordered by timestamp desc, then filter `rn = 1` |
| Databricks vs Spark? | Spark is the open-source engine; Databricks is a managed platform around it with notebooks, Delta, Unity Catalog, jobs and serverless compute |
| Is Azure Databricks different from Databricks on AWS? | The notebook and Spark code are the same; only the cloud integration and authorization setup differ |
