---
title: Day 25 Vocabulary
description: Glossary of terms and definitions from the Training 25 notes.
sidebar:
  order: 25
---

Vocabulary — Study Guide Day 25

Source: notes/Training 25.md

## Local AI
- **Local AI** — Running AI models on your own hardware; free per request but needs expensive hardware and gives weaker models.
- **Hosted AI** — Calling a provider's models over an API (e.g. Bedrock, OpenAI API) and paying per token.
- **Ollama** — A tool for downloading and running models locally, with commands like `ollama list`, `ollama serve` and `ollama run`.
- **Ollama API** — Ollama's local HTTP API, served by default at `127.0.0.1:11434` under the `/api` path.
- **Qwen** — An open-weight model family, e.g. `qwen2.5:7b-instruct`, run locally in the demo.
- **GPU (Graphics Processing Unit)** — Hardware that makes running larger AI models practical.
- **SSH (Secure Shell)** — Encrypted remote login; after `ssh`, every command runs on the remote machine.
- **HPC (High-Performance Computing)** — Specialized expensive compute hardware, the territory of building your own models.

## AI Concepts
- **LLM (Large Language Model)** — A text model with no memory between requests; everything it must know has to be in the prompt.
- **System prompt** — Developer-written instructions sent with every request that set the model's role, rules and output format.
- **Context** — Information the application adds to a request, such as the database schema.
- **User message** — The end user's question in a request.
- **Token** — A unit of text a model reads or writes; hosted models are billed per input and output token.
- **RAG (Retrieval-Augmented Generation)** — Giving the AI access to a directory of data that it retrieves at question time and uses to inform its response.
- **Chunking** — Splitting documents into small pieces before embedding them.
- **Embedding** — A vector of numbers representing text where similar meanings land close together.
- **Vector** — A list of numbers representing the meaning of text.
- **Vector database** — A database of tokenized (embedded) information saved persistently rather than kept in memory, queried for the chunks most similar to a question.
- **Retriever** — The RAG component that finds the most relevant chunks for a question.
- **Sentence splitter** — A chunker that splits documents on sentence boundaries.
- **Embedding model** — A model that converts text into embeddings.
- **LlamaIndex** — A Python RAG library used in the demo over a PDF.
- **VectorStoreIndex** — LlamaIndex's index that held vectors in memory in the demo.
- **Amazon S3 Vectors** — AWS storage for embeddings with its own IAM prefix (`s3vectors:*`, not covered by `s3:*`); planned for knowledge documents, not raw rows.
- **Retrieval quality** — How well the right chunks are found; the usual cause of vague RAG answers.
- **Source of truth** — The authoritative store for data; Redshift remains it for structured data.
- **AI genie** — A common corporate AI product combining a RAG pipeline and vector database so users can ask questions about their data.
- **AI/BI Genie** — Databricks' product of that name.
- **Multimodal model** — A model that accepts inputs beyond text, such as images.
- **Hallucination** — A model inventing something that doesn't exist, such as a nonexistent column.
- **Text-to-SQL** — Using an LLM to turn a plain-English question into a SQL query.
- **Schema grounding** — Giving the model the real schema so it only uses existing tables and columns.
- **Schema validation (INSUFFICIENT_SCHEMA)** — A prompt rule that the model must check every needed column exists and return `INSUFFICIENT_SCHEMA` instead of SQL if not.
- **Human approval (human-in-the-loop)** — A person reviews generated SQL before it runs, so the AI can't execute costly or unsafe queries.
- **Read-only SQL** — Queries that only read data, the only kind the chatbot may generate.
- **MLOps** — Deploying and managing ML/AI pipelines, the deployment side of AI rather than model training.
- **MLflow** — An open-source MLOps platform for tracking, registering and deploying models.

## Amazon Bedrock
- **Amazon Bedrock** — AWS's managed service for calling foundation models from many providers through one API, much like the OpenAI API.
- **Foundation model** — A large pre-trained model offered for general use through an API.
- **bedrock-runtime** — The boto3 client used to invoke Bedrock models.
- **list-foundation-models** — AWS CLI command listing available Bedrock models.
- **bedrock:InvokeModel** — The IAM action allowing a role to call a Bedrock model.
- **Amazon Nova Micro** — The cheapest Amazon model with acceptable quality for narrow tasks like generating SQL.
- **Amazon Nova Lite** — A slightly stronger, pricier Nova model used as the fallback.
- **PassRole (iam:PassRole)** — Permission to hand an IAM role to a service such as Bedrock.

## Text-to-SQL Chatbot
- **Streamlit pages/** — A folder whose files Streamlit automatically discovers as extra app pages.
- **information_schema.columns** — System view listing every column's schema, table, name, type and position; exported as the model's schema context.
- **sqlglot** — A Python SQL parser used to validate generated SQL.
- **Redshift Data API** — API that runs SQL against Redshift via `execute_statement`, `describe_statement`, `get_statement_result` and `cancel_statement`.
- **Polling** — Repeatedly checking a statement's status until it finishes.
- **Smoke test** — A minimal first test proving the basic path works.
- **Repair SQL** — Sending a failed query's error back to the model to get corrected SQL.
- **Grain** — What one row of a table represents; the fact table's grain is one row per station per snapshot.
- **Fact table** — A table of measurements with many rows per entity, e.g. `fact_station_snapshot`.
- **Dimension table** — A table of descriptive attributes, e.g. `dim_station`.
- **ROW_NUMBER()** — Window function that numbers rows within a partition; keep `rn = 1` for the latest record per entity.
- **Latest-per-entity pattern** — Using `ROW_NUMBER()` per entity ordered newest first and keeping the first row.
- **Window function** — A function computed over a set of related rows, evaluated after WHERE so it can't be filtered there.
- **PARTITION BY** — Window clause that splits rows into groups, e.g. per station.
- **QUALIFY** — Redshift clause that filters on window function results.
- **HAVING** — Filters groups after aggregation; it does not filter window functions.
- **CTE (Common Table Expression)** — A named subquery in a `WITH` clause; an alternative way to filter a window result in an outer `WHERE`.
- **DISTINCT** — Removes duplicate rows; shouldn't be used to hide duplicates from bad joins or wrong grain.
- **AVG() with GROUP BY** — Aggregation that computes one average per group, e.g. per station.

## Deployment and Infrastructure
- **Targeted apply** — Running `terraform apply` on only specific resources.
- **most_recent (AMI lookup)** — A data-source option that picks the newest AMI on every plan, which can force EC2 replacement.
- **Pinning the AMI ID** — Hard-coding an AMI so Terraform doesn't replace the instance.
- **Authentication vs authorization error** — "Could not validate credentials" is authentication (wrong or missing profile), not a permission problem.
- **--profile** — AWS CLI flag selecting a named credential profile.
- **SSM (AWS Systems Manager)** — AWS service for managing instances remotely.
- **SSM Run Command (send-command)** — Runs commands on an EC2 instance remotely, used to deploy code and restart the service.
- **get-command-invocation** — Checks the result of an SSM command on an instance.
- **systemd service** — A Linux service that runs the Streamlit app and restarts it.
- **Security group /32 rule** — An inbound rule allowing exactly one IP address; never open to `0.0.0.0/0`.
- **0.0.0.0/0** — A CIDR meaning every IP address on the internet.
- **Azure** — Microsoft's cloud, the class's next topic in place of AWS services.
- **Databricks** — A data and AI platform the course covers later.
