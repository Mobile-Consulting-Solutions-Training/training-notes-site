---
title: "Training 26 Homework"
description: "Homework assignment for Training 26: Kinesis Streaming Ingestion."
sidebar:
  order: 26
---

:::note
The assignment prompt as given in class. Related notes: [Training 26](/training-notes-site/notes/training-26/).
:::

## Homework - Training 26 (Assignment)

Weekend Homework: Building an End-to-End AWS Data Pipeline with AI

**Topic:** Terraform, AWS Lambda, Step Functions, Glue, Redshift, Streamlit, Amazon Bedrock, and RAG
**Estimated time:** 4–6 hours, depending on your current pipeline progress
**Due:** Next class session
**Format:** Hands-on development, short theoretical reading, and written questions

### Assignment Objective

This week, we built an end-to-end AWS data engineering pipeline that ingests Citi Bike station data, transforms it, loads it into an analytics database, and makes the results accessible through a Streamlit dashboard with AI-powered natural-language querying.

Your main assignment is to bring your own AWS pipeline as close as possible to the instructor's completed implementation.

You should also understand how the different AWS services work together, particularly how Retrieval-Augmented Generation (RAG), embeddings, vector databases, and Amazon Bedrock can extend a traditional data pipeline into an AI-powered analytics application.

**Important:** Our AWS resources have been shut down for the weekend. Do not restart scheduled ingestion, compute resources, or other chargeable infrastructure without authorization. Complete the infrastructure work in Terraform and your local code where possible. You can perform cloud testing when access is restored.

---

### Part 1 — Complete Your AWS Pipeline

**Priority:** High | **Suggested time:** 2.5–3.5 hours

Review the pipeline you have built during class and identify which components are missing, incomplete, or not functioning correctly.

Your goal is to achieve the following architecture:

```
External Citi Bike API
         |
         v
    AWS Lambda
         |
         v
    Amazon S3
    Bronze Layer
         |
         v
  AWS Step Functions
         |
         v
      AWS Glue
  Incremental ETL
         |
         v
    Amazon S3
    Silver Layer
         |
         v
    Amazon Redshift
    Gold / Analytics
         |
         v
 Streamlit Dashboard
         |
         v
 Amazon Bedrock
 Natural Language SQL
```

Terraform should be used to provision and manage the appropriate AWS resources.

#### Required components

- **Terraform:** Organize infrastructure into reusable configuration files, variables, outputs, and resource dependencies. Verify that `terraform validate` succeeds.
- **Lambda and S3:** Implement ingestion of Citi Bike station information and station status into the Bronze layer, using an appropriate S3 folder structure.
- **Step Functions:** Define a workflow that orchestrates your ETL processing, including success and failure handling.
- **AWS Glue:** Implement incremental Bronze-to-Silver processing, with schema handling, deduplication, and an appropriate strategy for avoiding duplicate processing.
- **Redshift:** Prepare an analytics model with station, date, and station-snapshot information. Use fact and dimension tables where appropriate.
- **Streamlit:** Build or improve a dashboard capable of displaying useful results from your Redshift data.

You do not need to reproduce every feature of the instructor's implementation exactly. However, your pipeline should follow the same general architecture and demonstrate that you understand each component.

#### Required validation

Where your pipeline has already been deployed and tested, document the results. Otherwise, prepare the code and configuration for testing on Monday.

At minimum, complete:

- `terraform fmt` and `terraform validate`.
- A review of your IAM roles and permissions.
- A review of your Glue transformation logic.
- At least three analytical SQL queries that your Redshift model should support.
- A short description of how your pipeline handles failures and avoids duplicate records.

**Deliverable:** Your updated project repository, with a README identifying completed components, outstanding work, and any known blockers.

---

### Part 2 — Understanding the End-to-End Architecture

**Suggested time:** 20–30 minutes

Review the following concepts:

- **Infrastructure as Code:** How Terraform manages AWS infrastructure and why state files matter.
- **Data ingestion:** Why Lambda is appropriate for lightweight API ingestion.
- **Orchestration versus transformation:** Why Step Functions coordinates the workflow while Glue performs the data processing.
- **Incremental processing:** Why production pipelines should not reprocess all historical data every time.
- **Medallion architecture:** The purpose of Bronze, Silver, and Gold data layers.
- **Dimensional modeling:** Why analytical systems use fact and dimension tables.
- **Analytics presentation:** How Streamlit connects the underlying data platform to its users.

#### Written questions

Answer each in approximately 2–4 sentences.

1. What is the difference between Terraform and Step Functions? Why do we need both?
2. Why do we store raw data in S3 before transforming it?
3. What happens if a Glue job fails halfway through processing? How should the pipeline recover?
4. What is the difference between a fact table and a dimension table?
5. Why might a Streamlit dashboard be preferable to giving business users direct access to Redshift?

---

### Part 3 — AI Concepts: Embeddings, Vector Databases, and RAG

**Suggested time:** 30–40 minutes

Our Streamlit application introduced an additional capability: users can ask questions in natural language instead of writing SQL manually.

To understand how this works, study these five concepts.

#### 1. Large Language Models (LLMs)

An LLM generates responses based on its training and the context provided in a request.

An LLM does not automatically know the structure of your Redshift database. We must provide the necessary schema information and instructions.

#### 2. Embeddings

An embedding is a numerical representation of text or other content.

Embeddings allow applications to compare the semantic similarity of questions and documents. For example, a question about station utilization may be semantically similar to documentation describing how utilization is calculated.

#### 3. Vector databases

A vector database stores embeddings and supports similarity searches.

Instead of looking only for exact keyword matches, a vector search can retrieve documents that are conceptually related to a user's question.

In our AWS architecture, we explored Amazon S3 Vectors as a way to store and retrieve embeddings.

#### 4. Retrieval-Augmented Generation (RAG)

RAG combines information retrieval with an LLM.

A typical RAG workflow is:

```
User Question
      |
      v
Create Question Embedding
      |
      v
Search Vector Database
      |
      v
Retrieve Relevant Documentation
      |
      v
Add Documentation to LLM Prompt
      |
      v
Generate Context-Aware Answer
```

RAG helps the model work with information that was not necessarily included in its original training data.

Our classroom application also explored local document retrieval as an alternative to embedding-based retrieval.

#### 5. Amazon Bedrock

Amazon Bedrock provides managed access to foundation models through AWS APIs.

Our application uses Amazon Nova to generate Redshift SQL and explain query results. We also experimented with Amazon Titan embeddings for document retrieval.

Bedrock provides model inference; it does not replace Redshift, Glue, or Step Functions.

#### Written questions

Answer each in approximately 2–4 sentences.

1. What is an embedding, and why is it useful for searching documentation?
2. How does a vector database differ from a traditional relational database?
3. What is RAG, and how can it improve the accuracy of an LLM's response?
4. What is the difference between Amazon Titan Embeddings and Amazon Nova?
5. Why is it important to provide the actual Redshift schema to the LLM before asking it to generate SQL?

---

### Part 4 — Integrating AI with Streamlit

**Suggested time:** 20–30 minutes

Review how our AI-powered Streamlit application works.

```
User asks a question
         |
         v
    Streamlit UI
         |
         v
Retrieve schema and
relevant documentation
         |
         v
   Amazon Bedrock
   Generates SQL
         |
         v
 User reviews SQL
         |
         v
    Amazon Redshift
    Executes query
         |
         v
   Query results
         |
         v
   Amazon Bedrock
   Explains results
         |
         v
    Streamlit UI
 Displays AI Answer
```

Pay particular attention to the fact that the application performs two distinct LLM tasks:

- **SQL generation:** Convert the user's question into a valid Redshift query.
- **Result explanation:** Interpret the actual returned data in natural language.

The application must not assume that the model's output is always correct.

#### Written questions

Answer each in approximately 2–4 sentences.

1. Why should generated SQL be validated before execution?
2. Why should the application restrict AI-generated SQL to read-only queries?
3. Why is the final explanation generated from actual Redshift results instead of asking the LLM to answer directly?
4. What is the purpose of `st.session_state` in a Streamlit application?
5. What should happen when Bedrock generates SQL that references a nonexistent column?

---

### Part 5 — Short Practical AI Exercise

**Suggested time:** 20–30 minutes

You are not required to deploy your own Bedrock or vector database infrastructure this weekend.

Instead, write a small Python function that constructs the prompt you would send to an LLM to generate SQL.

Your function should accept three inputs:

```python
def build_sql_prompt(question, schema, documentation):
    # Your implementation
    pass
```

It should return a string containing:

- The user's natural-language question.
- The available database schema.
- Relevant documentation.
- Instructions to generate only valid Amazon Redshift SQL.
- Instructions not to invent tables or columns.
- Instructions to generate read-only SQL.

Test your function with this question:

> Which 10 Citi Bike stations have the highest number of available bicycles?

You may use a sample schema based on the station data we worked with during class.

**Deliverable:** One Python file containing the function and an example of its output.

---

### Submission Requirements

Submit the following:

- **Updated AWS pipeline repository:** Terraform configuration, Lambda code, Glue scripts, Step Functions definition, SQL scripts, and Streamlit code where available.
- **README.md:** A brief status report explaining what works, what remains incomplete, and what needs to be tested on Monday.
- **Written answers:** Answers to the 15 theoretical questions. Keep them concise.
- **AI prompt exercise:** Your `build_sql_prompt()` function and example output.

### Evaluation Rubric

| Category | Weight |
|---|---|
| Pipeline completeness and architecture | 45% |
| Terraform configuration and code quality | 15% |
| Understanding of AWS pipeline concepts | 15% |
| Understanding of AI, RAG, and Bedrock | 15% |
| Python prompt-building exercise | 10% |
| **Total** | **100%** |

### Final expectations

The most important objective is to make meaningful progress toward a complete, functioning AWS pipeline.

You should understand the responsibilities of each service and how data moves through the architecture. You are not expected to become an expert in RAG or large language models over one weekend.

Focus on completing your existing pipeline, understanding the AI integration, and preparing your work for testing and demonstration during the next class.

**Do not start AWS resources or re-enable weekend schedules. We will resume cloud testing during class on Monday.**
