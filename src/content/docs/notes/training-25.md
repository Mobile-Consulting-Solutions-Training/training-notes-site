---
title: "Training 25 - AI on the Pipeline"
description: "Local AI with Ollama, RAG and vector databases, and Amazon Bedrock added to the Citi Bike dashboard as a text-to-SQL chatbot over Redshift."
sidebar:
  order: 25
---

Teacher: Evan Flint

Syllabus Day 26 (per file numbering; Thu Oct 15). Topics: AI on top of the pipeline. Local AI (Ollama), RAG pipelines and vector databases, then **Amazon Bedrock** added to the Citi Bike Streamlit dashboard as a **text-to-SQL chatbot** that queries Redshift and explains the results.

Note: I was out on PTO for this class. Notes compiled after class from the class materials and Evan's shared chat. Homework: `homework/assignment/Homework - Training 25 (Assignment).md`.

---

# Class Logistics

- **Progress check:** Evan asked everyone for a pipeline update. Several students were behind on time.
  - On homework time: in his demos he spends "probably three, three and a half of the four hours" building, so expect that much if working "relatively unguided."
  - A student said the AI suggested waiting an hour between scheduler steps. Evan: "sometimes that guy gives really bad advice." He wants runtimes as short as possible: "processing the data in the smallest possible amount of time" is "one professional goal of a big data engineer." Don't "artificially inflate processing times."
  - **Advice if you're behind:** start from the **incremental scripts** from Training 24. "If you start with the incremental scripts, you'll never need to do the backfill stuff." The backfill only existed because he built the pipeline before designing it to be incremental.
  - A student pointed out ChatGPT estimated the Training 24 homework at 6-10 hours. Evan: "I cannot in good conscience recommend that you do ten hours of work in a day on top of class." What he wants is **evidence of progress each day**, not the whole thing done.
  - Focus "less on the reading side and more on the building side." He wants a progress report at the start of each class.
- **Looking ahead:** next week the class turns to **Azure** infrastructure, tied into DevOps and AI. "Azure is just going to take the place of AWS services, but the endpoint can remain the same." Friday may introduce a basic ML model deployed on **MLflow** on the EC2 instance.
- Evan shared a zip of the day's files and the chat link in Teams at the end.

---

# AI Concepts

Q. What is local AI?

A. (From class) Running models on your own hardware. Evan SSH'd into his **ASUS GX10** (a machine "purpose-built for running local AI," located in Nevada while he teaches from Brazil) and ran models with **Ollama**: `ollama list`, `ollama serve`, `ollama run qwen2.5:7b-instruct`. "It cost me the price of the electricity."

Expanded: Local models are free per request, but the hardware is expensive and they're much weaker than hosted ones. Evan's demo showed this: Qwen wrote a Python client for the Ollama API that didn't work at first. It didn't know the default port and missed the `/api` path, and he had to fall back to ChatGPT for the port (`127.0.0.1:11434`). Without a GPU, only the smallest models are practical.

| | Local AI (Ollama on your machine) | Hosted AI (Bedrock, OpenAI API) |
|---|---|---|
| Cost per request | Electricity only | Pay per token |
| Up-front cost | Expensive GPU hardware | None |
| Model quality | Smaller, weaker models | Largest, strongest models |
| Data leaves your network? | No | Yes |
| Can search the internet? | No | Depends on the product |

**SSH reminder (a student asked):** the prompt `evan@sophia-lemur` is his laptop. After `ssh gx-10`, every command runs on the remote machine. The directory you were in on your laptop doesn't matter there.

---

Q. What is a system prompt?

A. (From class) "This up here, by the way, is what we would call a system prompt. It starts out with 'you are an expert in data warehousing, use only the provided context,' etc." … "System prompts are very important." … "You can also tell it things like 'you are a strict parser, your job is to take the questions … and convert them into SQL statements and put out only the SQL statement.'"

Expanded: The system prompt is instructions sent with every request, before the user's question. It sets the model's role, rules and output format. Evan's point is that a model "has no memory" and "is just a blank slate." ChatGPT or Claude seem to know you only because the *app* stores a profile and passes it in with each request. The model itself starts from nothing every time. So everything the model must know (its role, the schema, the rules) has to be in the prompt.

| Part of a request | Who writes it | Example from class |
|---|---|---|
| System prompt | The developer | "You are an expert Amazon Redshift SQL developer… use only the tables and columns in the supplied schema… generate only a single read-only SQL statement" |
| Context | The application | The contents of `redshift_schema.txt` |
| User message | The end user | "Which 20 stations have the most available bikes?" |

---

Q. What is RAG (retrieval-augmented generation)?

A. (From class) "RAG stands for retrieval augmented generation … you have a directory which contains data, and the AI is given access to that data, and it uses it to inform its response."

Expanded: The canonical RAG / vector database entry is in Training 22; this section adds the LlamaIndex demo. The model wasn't trained on your documents, so RAG **retrieves** the relevant passages at question time and pastes them into the prompt. The model then **generates** an answer grounded in them. Steps: split documents into chunks → turn each chunk into an embedding (a vector of numbers) → store them → at question time, embed the question, find the most similar chunks, and send those chunks along with the question.

**Evan's demo:** LlamaIndex (a Python RAG library) over a PDF of *The Data Warehouse Toolkit*, using the OpenAI API.
- The first version answered vaguely ("it likely covers…") and was retrieving table-of-contents pages.
- ChatGPT diagnosed it as "almost certainly retrieval quality and not the language model itself." The fix: a proper retriever, a sentence splitter, an embedding model, and a system prompt saying "use only the provided context … never speculate."
- Version 2 loaded all 447 pages and correctly said Chapter 2 is retail sales and Chapter 3 is inventory (bus architecture, conformed dimensions).

---

Q. What is a vector database?

A. (From class) "A vector database is a database of tokenized information." … "The difference between that and a vector database is basically that in a vector database it's saved in a type of database rather than just being kept in memory."

Expanded (correction): a vector database stores **embeddings**, not tokens. Tokens are the word pieces a tokenizer splits text into before a model reads it. Embeddings are fixed-length lists of numbers that an *embedding model* produces from a whole chunk of text, and similar meanings end up close together.

Models work on numbers, not words. Text is converted into **vectors** (embeddings), lists of numbers where similar meanings land close together. A vector database stores those vectors and answers "which stored chunks are most similar to this question?" In Evan's LlamaIndex demo the vectors were only held in memory (`VectorStoreIndex`). A vector database (Evan's chat planned **Amazon S3 Vectors**) keeps them persistently so they don't have to be rebuilt every run.

| | RAG pipeline | Vector database |
|---|---|---|
| What it is | A *process*: retrieve, then generate | A *storage system* for embeddings |
| Role | Feeds relevant context to the model | Where RAG looks things up |
| Class example | LlamaIndex over the Toolkit PDF | S3 Vectors (planned, not built) |

**What Evan chose instead (and why):** a vector DB of Redshift results would mean querying Redshift regularly, embedding the results and storing them. That was too much for one class, so he built the "simplest and most straightforward" version: **text-to-SQL**. His chat noted that if RAG is added later, **S3 Vectors should hold knowledge documents, not the raw station rows**. Redshift stays the source of truth for structured data.

---

Q. What is an "AI genie"?

A. (From class) "Probably the most common of the corporate AI products … what's called an AI genie. We're going to see something that's literally called AI Genie when we start working with Databricks." It's "an AI that has had some kind of combination of a RAG pipeline and vector database provided to it," so you can ask questions about the data in your environment.

Expanded: Today's chatbot is a minimal version of that: ask about your data in plain English, get SQL, results and an explanation. Databricks' product is called **AI/BI Genie**. It is grounded in Unity Catalog metadata (table and column descriptions) plus curated example queries and instructions, the same idea as our schema file in the prompt (see the semantic views in Training 15).

---

Q. Can a Bedrock model understand images? (student question)

A. (From class) A plain LLM can't see images. "The image needs to first get processed by an AI model that is purpose-built for looking at images and returning a text-based description," and then that text goes to the LLM. ChatGPT is multimodal because the app combines those models.

Expanded (correction): that was true of older pipelines, but modern **multimodal** models (Claude, GPT-4o-class models, Amazon Nova Lite and Pro) take images **natively**. A vision encoder inside the model turns the image into embeddings, with no separate captioning model. Text-only models (e.g. Nova Micro) still can't.

On Bedrock, choose a model that is explicitly **multimodal** (it accepts image input) if you need images. A text-only model can't do it, even if the same company's chat app can.

---

# Amazon Bedrock

Q. What is Amazon Bedrock?

A. (From class) Evan ran `aws bedrock list-foundation-models` to show "a bunch of AI models" from many providers. "If you've worked with the OpenAI API before, then the Amazon Bedrock API should be basically the same thing, except that … you can specify models that are not OpenAI models."

Expanded: Bedrock is AWS's managed service for calling foundation models through one API. You don't host the model. You call `bedrock-runtime` (in boto3) and pay per token. The models Evan saw listed included Amazon Nova (Micro, Lite), Anthropic Claude, DeepSeek, xAI Grok and OpenAI models. Students got `AccessDenied` at first, and Evan granted Bedrock access during the first break.

| Model choice | Why |
|---|---|
| **Amazon Nova Micro** (used) | Cheapest model with acceptable quality for a narrow job: generating SQL |
| Amazon Nova Lite | The fallback "if the generated SQL isn't reliable enough" |
| Big flagship models | Too expensive for testing |

**Cost math from class:** Nova Micro is about $0.035 per million input tokens and $0.14 per million output tokens. A request with 2,000 input tokens and 300 output tokens costs about 0.011 cents, or "roughly 11 cents versus 19 cents per thousand requests" for Nova Micro vs. Nova Lite. A narrowly scoped task keeps tokens, and therefore cost, low.

**Student permission changes (from Evan's chat):** add `bedrock:*`, `s3vectors:*` and `ssm:*` to the student group policy, plus `bedrock.amazonaws.com` to the PassRole service list. Note that `s3:*` does **not** cover S3 Vectors, which has its own IAM prefix.

---

# The Text-to-SQL Chatbot (main demo)

## Workflow

| Step | What happens | Where |
|---|---|---|
| 1 | User asks a question in plain English | Streamlit page `pages/2_AI_SQL_Generator.py` |
| 2 | Bedrock (Nova Micro) generates **one read-only SQL** query from the question + schema | `bedrock_sql.py` → `generate_sql()` |
| 3 | **Human reviews** the SQL and clicks **Query Redshift** | Streamlit button |
| 4 | Redshift runs it through the Redshift Data API | `redshift_query.py` |
| 5 | Bedrock gets the question + SQL + returned rows and writes a plain-language answer | `bedrock_sql.py` → `explain_results()` |
| 6 | Streamlit shows the SQL, the result table and the AI answer | Streamlit |

Why the approval step: "We don't want to just let the AI execute whatever SQL it wants to," because it could run SQL "that costs money" and that leads to questions from management, or to a bill if it's your own account.

---

## Files added to the dashboard

| File | Purpose |
|---|---|
| `bedrock_sql.py` | boto3 `bedrock-runtime` client, model ID from env var (default Nova Micro), `SYSTEM_PROMPT`, `generate_sql(question, schema)`, later `explain_results()` and `repair_sql()` |
| `redshift_schema.txt` | Real schema exported from Redshift (`information_schema.columns`: schema, table, column, type, position), saved as text and sent to the model as context |
| `pages/2_AI_SQL_Generator.py` | The Streamlit page. Streamlit automatically discovers files in `pages/`, so no registration is needed |
| `redshift_query.py` | Validates the SQL (uses `sqlglot` to parse), runs it via `redshift-data` `execute_statement`, polls `describe_statement` until done, caps rows returned, and cancels after 90 s |
| `deploy_chatbot.sh` | Copies files from S3 to the EC2 instance through SSM and restarts the service |

Evan's take on generated code: "Does it actually ever invoke anything? No, it doesn't." The first `bedrock_sql.py` only defined `generate_sql`, so running it did nothing until the page called it with a question and the schema.

---

## Infrastructure changes (Terraform + deployment)

- **IAM:** added `aws_iam_role_policy.dashboard_bedrock` (`bedrock:InvokeModel`) to the existing dashboard role in `dashboard.tf`. Later he added `redshift-data:CancelStatement` next to ExecuteStatement, DescribeStatement and GetStatementResult, plus an S3 read policy for deployment.
- **Near-miss:** `terraform plan` wanted to **destroy and recreate** the EC2 instance, because the AMI was looked up with `most_recent`, which picks the newest AMI on every plan. Evan: "I want to be very, very careful about this." Fixes:
  - a **targeted apply** of only the IAM policy
  - **pinning the AMI ID** so the instance stays put
  - the idiomatic Terraform fix: `lifecycle { ignore_changes = [ami] }` on the `aws_instance`, so a newer AMI no longer forces a replacement
  - note: `-target` is meant for exceptional cases, not routine applies
- **Credentials:** a command failed with "AWS was not able to validate the provided credentials." That's an *authentication* problem (wrong or missing profile), not a permission problem. The fix was to pass the company `--profile` explicitly.
- **Terraform manages the infrastructure, not the app code:** "you shouldn't have to rebuild an EC2 instance every time you change a Python file." Code is deployed by:
  1. `aws s3 cp` the files to `s3://<bucket>/scripts/dashboard/`
  2. **SSM Run Command** (`aws ssm send-command`) tells the instance to copy them and restart `citibike-dashboard.service` (systemd)
  3. `aws ssm wait command-executed` / `get-command-invocation` to check the result
- First deployment failed with an S3 access error. After the policy apply it still looked failed, but he was reading the *old* command's result. The new command ID showed success.
- **Students couldn't open the dashboard** (infinite loading). The security group only allows Evan's IP. The simplest safe fix is adding each student's public IP as `/32` to the security group (never `0.0.0.0/0`). He postponed it to save class time.
- Student question: does Terraform need anything special for AI? No. "Terraform isn't actually touching the AI itself at all." It deploys EC2 and manages the permissions around it. The Python app makes the Bedrock calls.

---

## Debugging the generated SQL (the most useful part for homework)

**1. A first smoke test:** the prompt "Write a Redshift SQL query returning the current date. Return SQL only" returned `SELECT CURRENT_DATE AS today_date`, which ran in Redshift and returned Oct 15. "That proves that the model is capable of at least generating basically functional SQL."

**2. The missing semicolon:** "Which 10 stations have the lowest average bike availability?" produced SQL without a semicolon. It still ran.

**3. Duplicate stations (grain problem):** "Which 20 stations have the most available bikes?" returned E 40 St & Park Ave (122 bikes) many times. The SQL joined `fact_station_snapshot` to `dim_station` and ordered **raw snapshot rows**. The fact table has many rows per station (one per snapshot), so it returned the 20 highest *observations*, not the 20 highest *stations*. The fix went into the system prompt:

| Rule added to the system prompt | Why |
|---|---|
| fact_station_snapshot grain = (station_id, snapshot_timestamp) | Tells the model a station appears many times |
| Rankings of stations return **one row per station** | Stops ranking raw snapshot rows |
| Latest availability → `ROW_NUMBER()` per station, newest first, keep rn = 1 | The "latest record per entity" pattern |
| Historical averages → `AVG()` + `GROUP BY station_id` | Correct aggregation |
| **Don't use DISTINCT to hide duplicates** caused by bad joins or wrong grain | DISTINCT masks the real bug |

**4. A window function in WHERE:** the next SQL put `ROW_NUMBER() OVER (…) = 1` in a `WHERE` clause, so Redshift returned "Window function is not allowed in where clause." Evan guessed HAVING, but ChatGPT corrected that: window functions are evaluated *after* WHERE, and HAVING doesn't filter them either. Redshift's answer is **`QUALIFY`**:

```sql
SELECT ds.station_id, ds.station_name, fss.bikes_available
FROM gold.fact_station_snapshot AS fss
JOIN gold.dim_station AS ds ON fss.station_id = ds.station_id
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY fss.station_id
    ORDER BY fss.snapshot_timestamp DESC
) = 1
ORDER BY fss.bikes_available DESC
LIMIT 20;
```

The alternative is to compute `ROW_NUMBER()` in a CTE and filter on its alias in the outer `WHERE`. He also added an **editable SQL box** and a **repair SQL** button that sends the error back to Bedrock. The first redeploy appeared to do nothing because he hadn't finished the deployment step. After deploying properly, it returned correct results: 122 at E 40 St & Park Ave, then 119 at FDR Dr & E 35 St.

**5. A hallucinated column:** "I'm at 46th St and 55th Ave (Queens). What's the closest bike station?" produced SQL using `ds.latitude`, which doesn't exist. `dim_station` has only `station_id`, `station_name` and `capacity`. Evan: "It should know that that column doesn't exist, but this is a lightweight model and we can't expect incredible performance out of lightweight models." The chat's fix is **mandatory schema validation** at the top of the prompt. Before writing SQL, list every column needed. If any is missing, return `INSUFFICIENT_SCHEMA` instead of SQL. It also noted that minimizing lat and long differences separately isn't a real distance calculation.

**6. Questions it can answer:** Evan asked for "a list of questions that the database can reasonably answer" (35, in levels). Examples: the 20 largest stations by capacity, stations with capacity > 50, average availability per station, % of observations empty or full. It **can't** answer anything about location, trips, riders or revenue, because those aren't in the data model. "Capacity greater than 50" gave the answer Evan wanted: a summary with useful details, not just the rows read back.

| Error type | Example | Fix |
|---|---|---|
| Wrong grain | Same station 5 times | Grain rules in the system prompt |
| Syntax | Window function in WHERE | QUALIFY, or a CTE |
| Hallucinated column | `ds.latitude` | Schema validation + refusal (`INSUFFICIENT_SCHEMA`) |
| Missing data | "Nearest station" | Add lat/long to the data model (Silver → Gold) |

(QUALIFY and the ROW_NUMBER ranking functions are covered in full in Training 21.)

**Interview line (hallucinated columns):** "Ground the model in the real schema, make it list the columns it needs before writing SQL, and give it a refusal token like `INSUFFICIENT_SCHEMA` when a column doesn't exist. Then validate the SQL with a parser before running it."

---

Q. How would you secure an LLM that writes and runs SQL?

A. (Not covered in class beyond the human approval step and the `sqlglot` check.)

Expanded:

| Control | Why |
|---|---|
| Run the SQL as a **read-only database user** (`GRANT SELECT` only, on the Gold schema) | Even if the model writes `DROP` or `DELETE`, the database refuses. A parser check alone can be bypassed |
| Parse and allow only one `SELECT` statement (`sqlglot`) | Blocks multi-statement and DDL output early |
| Row limits and a statement timeout (we cancel after 90 s) | Caps cost |
| Human approval before execution | The class design |
| Treat the user's question as untrusted (**prompt injection**) | A question can say "ignore your rules". The read-only user is the real safety net |

**Interview line:** "Defense in depth: a read-only role with SELECT on curated tables, a parser that allows one SELECT, row and time limits, and the assumption that the prompt can be injected."

---

Q. What does a Bedrock call with a system prompt look like?

A. (Shape of the call in `bedrock_sql.py`; written from the boto3 `converse` API, not an exact copy.)

```python
import boto3
client = boto3.client("bedrock-runtime", region_name="us-east-2")
response = client.converse(
    modelId=MODEL_ID,                                    # Nova Micro by default
    system=[{"text": SYSTEM_PROMPT}],                     # role, rules, output format
    messages=[{"role": "user",
               "content": [{"text": f"Schema:\n{schema}\n\nQuestion: {question}"}]}],
    inferenceConfig={"maxTokens": 500, "temperature": 0}, # deterministic SQL
)
sql = response["output"]["message"]["content"][0]["text"]
```

---

# Terraform Fundamentals (roadmap topic for this day, not taught in class)

Q. What are Terraform variables, outputs and locals?

A. (Not covered in class.) Inputs, return values and named intermediate values for a configuration.

Expanded:

| Block | Purpose | Example |
|---|---|---|
| `variable` | An input, set by `terraform.tfvars`, `-var` or `TF_VAR_` env vars | `variable "instance_type" { default = "t3.small" }` |
| `output` | A value printed after apply, readable with `terraform output` | `dashboard_url` in Training 24 |
| `locals` | A computed value reused inside the config | `locals { prefix = "alexjackson-citibike" }` |

---

Q. What is Terraform state, and how do teams share it?

A. (Not covered in class; Training 24 shows what happens when state is lost.) `terraform.tfstate` is Terraform's map from each block in your code to the real resource ID in the cloud, plus the attributes it last saw.

Expanded:
- **Never commit it to Git.** It can contain secrets in plain text (database passwords, keys).
- Teams use **remote state**: an S3 backend (`backend "s3" { bucket = …, key = …, region = … }`) with **locking**, so two people can't apply at once. Locking used a DynamoDB table; recent Terraform versions can lock with a lock file in S3 itself (`use_lockfile = true`).
- If state is lost, Terraform thinks nothing exists and plans to create duplicates (Training 24). Fix with `terraform import`, not `apply`.

**Interview line:** "State is how Terraform knows what it manages. We keep it in an encrypted, versioned S3 bucket with locking, never in Git."

---

Q. What is a Terraform module, and how do you separate dev and prod?

A. (Not covered in class.) A module is a reusable folder of `.tf` files called with `module "name" { source = "./modules/glue_job" … }` and its own variables and outputs.

Expanded: a Glue job, its IAM role and its CloudWatch log group always come together, so they make a good module, called once per job with different variables. For environments, the common approaches are a separate folder and state per environment (each calling the same modules with different `tfvars`), or Terraform **workspaces** (one config, several states). In CI: `terraform fmt -check` and `terraform validate` on every PR, `plan` posted on the PR, `apply` only after merge.

---

# Evan's Takeaways

- "Ultimately it is me that tells the AI what to do, not the other way around." He relies on AI a lot but keeps human control. "AI is not going to have good creative innovative ideas most of the time."
- An AI model "will never ever do anything without being told to." It's prompt and response. "AI hacking" stories involve frameworks built to give it tools and automate the prompts.
- Companies rarely build their own models (the chip alone can be about $20,000, which is HPC territory). Most call hosted models, and the choice depends on company policy.
- **Why AI is in a data engineering course:** the company wants MLOps added to the program. Data engineers routinely get pulled into adjacent work (DevOps, Terraform, orchestration). Today's work was the *deployment* side of AI: "we're not training models … we're taking a model someone else has developed, making an API call, passing data through a prompt." Statistics like regression should stay with data science.
- "I see the use of data in AI, and AI's ability to talk about the data, as the natural conclusion of what all of this is for." A better data model (e.g. adding lat/long) makes the AI more capable.

---

# Homework (due Fri Oct 16)

`homework/assignment/Homework - Training 25 (Assignment).md`. Priority one is **progress on your existing pipeline**; the Bedrock chatbot is **not required**.

| Part | Work |
|---|---|
| 1 | Pipeline progress + be ready to explain what works, what's next, blockers, evidence |
| 2 | Reading: fact/dimension grain, window functions + QUALIFY, aggregation (~20 min) |
| 3 | Reading: Bedrock, prompts, schema grounding, hallucinations, human approval (~15 min) |
| 4 | 4 SQL exercises: aggregation, latest-per-entity, duplicate detection, one analytical question |
| 5 | 7 short conceptual AI questions |
| 6 | Optional: design an AI interface for your own pipeline |

The debugging section above maps directly onto Parts 2, 4 and 5: grain, QUALIFY, duplicates, hallucinated columns, and read-only credentials.
