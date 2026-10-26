---
title: Study Guide - Day 25
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 25: Local AI, Amazon Bedrock, and a Text-to-SQL Chatbot"
sidebar:
  order: 250
---

Study Guide - Day 25 (source: notes/Training 25.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Class Logistics.** Evan wants evidence of progress each day and short runtimes ("processing the data in the smallest possible amount of time" is a professional goal). If behind, start from the Training 24 incremental scripts and skip the backfill. Next week: Azure, with the same endpoints.

**Local AI.** Running models on your own hardware with **Ollama** (`ollama list`, `ollama serve`, `ollama run qwen2.5:7b-instruct`, API on `127.0.0.1:11434`). Free per request but needs expensive GPU hardware, and the models are smaller and weaker. Data never leaves your network.

**System Prompt.** Instructions sent with every request that set the model's role, rules and output format ("You are an expert Amazon Redshift SQL developer… use only the supplied schema… generate only a single read-only SQL statement"). A model **has no memory**; apps like ChatGPT pass your profile in each time. Request = system prompt (developer) + context (application, e.g. the schema) + user message.

**RAG and Vector Databases.** RAG: chunk documents, embed them, store them, retrieve the most similar chunks for a question and send them with the prompt. Evan's LlamaIndex demo over *The Data Warehouse Toolkit* answered vaguely until retrieval was fixed (sentence splitter, embedding model, "use only the provided context" prompt): bad answers were retrieval quality, not the LLM. A **vector database** stores embeddings persistently instead of in memory (Amazon S3 Vectors was planned). If added later, S3 Vectors should hold knowledge documents, not raw rows; Redshift stays the source of truth. An **AI genie** (Databricks AI/BI Genie) is a corporate AI that answers questions about your data. Plain LLMs can't see images; choose a multimodal model.

**Amazon Bedrock.** AWS's managed API for foundation models from many providers (Amazon Nova, Claude, DeepSeek, Grok, OpenAI), called with boto3 `bedrock-runtime`, billed per token. Like the OpenAI API but with non-OpenAI models. **Nova Micro** was used as the cheapest model good enough for SQL (~$0.035/M input, $0.14/M output tokens; ~11 cents per thousand requests); Nova Lite is the fallback. `s3:*` doesn't cover S3 Vectors (`s3vectors:*`).

**Text-to-SQL Chatbot.** User asks in plain English → Bedrock generates one read-only SQL from the question + schema → **human reviews and clicks Query Redshift** → Redshift Data API runs it → Bedrock explains the rows → Streamlit shows SQL, table and answer. The approval step stops AI from running expensive SQL. Files: `bedrock_sql.py`, `redshift_schema.txt` (exported from `information_schema.columns`), `pages/2_AI_SQL_Generator.py` (auto-discovered page), `redshift_query.py` (sqlglot validation, row cap, 90 s cancel), `deploy_chatbot.sh`.

**Infrastructure.** Added `bedrock:InvokeModel` to the dashboard role. **Near-miss:** `plan` wanted to destroy and recreate the EC2 instance because the AMI lookup used `most_recent`; fixed with a targeted apply and a **pinned AMI ID**. "Not able to validate credentials" = authentication (wrong profile), not permissions. Terraform manages infrastructure, not app code: deploy code with `aws s3 cp` + **SSM Run Command** to copy and restart the systemd service. Students' access needs their IP as `/32` in the security group, never `0.0.0.0/0`.

**Debugging Generated SQL.** (1) Smoke test `SELECT CURRENT_DATE` proves basic function. (2) Missing semicolon still ran. (3) **Wrong grain**: ranking raw snapshot rows returned the same station many times; system prompt rules for grain, one row per station, `ROW_NUMBER()` for latest, `AVG ... GROUP BY` for averages, and no `DISTINCT` to hide bad joins. (4) **Window function in WHERE** fails; use **`QUALIFY`** (or a CTE); HAVING doesn't work either. Added an editable SQL box and a repair button. (5) **Hallucinated column** `ds.latitude`: add mandatory schema validation and return `INSUFFICIENT_SCHEMA` instead. (6) The model can only answer what the data model contains (no location, trips, riders, revenue).

**Takeaways.** Humans tell the AI what to do. Models only act when prompted. Companies call hosted models rather than build them. Data engineers handle the **deployment** side of AI (MLOps): call a model API, pass data through a prompt. A better data model makes the AI more capable.

---

# Part 2: Cheat Sheet

## AI Concepts
- Local (Ollama) vs hosted (Bedrock): electricity vs per token · weak vs strong · private vs not
- System prompt = role + rules + format · models have no memory
- RAG: chunk → embed → store → retrieve → generate · bad answers often = bad retrieval
- Vector DB = persistent embeddings (S3 Vectors) · AI genie · multimodal for images

## Bedrock
- `bedrock-runtime` via boto3 · pay per token · many providers
- Nova Micro (cheap, narrow tasks) · Nova Lite (fallback) · `s3vectors:*` separate

## Chatbot Flow
- Question → SQL (Bedrock) → human approves → Redshift Data API → explanation (Bedrock) → Streamlit
- Schema file from `information_schema.columns` · sqlglot validation · row cap · timeout

## Infra Lessons
- Pin AMI IDs (avoid `most_recent` replacement) · targeted apply
- "Can't validate credentials" = auth/profile · deploy code via S3 + SSM, not Terraform
- SG: add `/32` per user, never `0.0.0.0/0`

## SQL Fixes
- Grain rules · one row per entity · `ROW_NUMBER()` latest · `AVG` + `GROUP BY` · no DISTINCT band-aid
- Window filter → `QUALIFY` or CTE
- Hallucinated columns → schema validation + `INSUFFICIENT_SCHEMA`

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What are the trade-offs of local AI versus hosted AI?
A: Local AI costs only electricity per request and keeps data on your network, but needs expensive hardware and runs smaller, weaker models. Hosted AI like Bedrock charges per token but gives you the strongest models with no hardware.

Q: What is a system prompt?
A: Instructions the developer sends with every request that set the model's role, rules and output format, like "you are a Redshift SQL expert, use only this schema, return one read-only query."

Q: Why does everything the model needs have to be in the prompt?
A: The model has no memory. It starts blank on every request, so the role, the schema and the rules all have to be sent each time.

Q: In the RAG demo, why were the first answers vague?
A: Retrieval was poor, pulling table-of-contents pages. Fixing the retriever, chunking and embeddings, and telling the model to use only the provided context, fixed the answers.

Q: What's the difference between RAG with an in-memory index and a vector database?
A: An in-memory index has to be rebuilt every run. A vector database stores the embeddings persistently so they can be searched again without rebuilding.

Q: What is Amazon Bedrock?
A: AWS's managed service for calling foundation models from many providers through one API. You don't host the model; you call bedrock-runtime and pay per token.

Q: Why use Nova Micro for the chatbot?
A: It's the cheapest model that was good enough for a narrow job like writing SQL, which keeps cost very low. Nova Lite was the fallback if quality wasn't enough.

Q: Walk through the text-to-SQL chatbot.
A: The user asks a question in English. Bedrock turns it plus the schema into one read-only SQL query. A person reviews it and clicks to run it on Redshift. Then Bedrock explains the returned rows in plain language.

Q: Why have a human approve the SQL before running it?
A: So the AI can't run whatever it wants, like an expensive or wrong query that costs money or causes problems.

Q: Why did terraform plan want to recreate the EC2 instance?
A: The AMI was looked up with most_recent, so a newer image made Terraform think the instance had to be replaced. Pinning the AMI ID stops that.

Q: How should application code be deployed if Terraform only manages infrastructure?
A: Copy the files to S3, then use SSM Run Command to have the instance pull them and restart its service. You shouldn't rebuild the instance for a Python change.

Q: Why did the chatbot return the same station many times?
A: The fact table has one row per station per snapshot, and the SQL ranked raw snapshot rows. The fix was adding grain rules so rankings return one row per station.

Q: Why shouldn't you use DISTINCT to fix duplicate rows?
A: It hides the real problem, a bad join or wrong grain, instead of fixing it.

Q: How do you filter on a window function in Redshift?
A: Use QUALIFY, or compute it in a CTE and filter on its alias in the outer query. WHERE and HAVING can't filter window functions.

Q: The model used a latitude column that doesn't exist. How do you guard against that?
A: Make the prompt require checking every needed column against the schema first, and return INSUFFICIENT_SCHEMA instead of SQL if something is missing.

Q: What part of AI does a data engineer usually handle?
A: The deployment side: taking a model someone else built, calling its API, and passing data through prompts. Building and training models belongs to researchers and data scientists.
