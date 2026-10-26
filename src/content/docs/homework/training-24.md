---
title: "Training 24 Homework"
description: "Homework assignment for Training 24: Incremental Pipelines."
sidebar:
  order: 24
---

:::note
The assignment prompt as given in class. Related notes: [Training 24](/training-notes-site/notes/training-24/).
:::

Homework Assignment: Building an Automated Incremental AWS Data Pipeline
AWS Data Engineering — Advanced Practical Assignment
Objective: Design and implement a working, automated, incremental data pipeline using AWS services, following the architectural principles demonstrated in our Citi Bike project.
Estimated effort: 6–10 hours, plus independent reading Deliverables: Working AWS pipeline, architecture diagram, source code, SQL scripts, execution evidence, and a short technical report.
Important: You are not required to perform a historical backfill. Your pipeline may begin collecting data from the time you deploy it. However, it must process new data incrementally rather than reprocessing the entire dataset on every execution.
Part 1 — Theory and required reading
Before implementing the project, you should understand the following concepts. These are not simply definitions to memorize; you must be able to explain how each concept influences the design of your pipeline.
1. The medallion architecture
Our class pipeline follows the Bronze, Silver, and Gold pattern.
Layer
    
Purpose
    
Expected characteristics


Bronze
    
Preserve source data
    
Raw, timestamped, minimally modified


Silver
    
Clean and standardize
    
Typed, validated, deduplicated, enriched


Gold
    
Support analytics
    
Fact tables, dimensions, business-ready data
Study why it is preferable to preserve raw source data rather than directly transforming incoming API responses into analytical tables.
Consider how the architecture supports debugging, reprocessing, schema changes, and data quality.
Required reading: Medallion lakehouse architecture.
2. Incremental processing and checkpoints
This is the most important theoretical component of the assignment.
A full refresh processes the entire dataset each time. An incremental pipeline processes only data that has not already been successfully incorporated, potentially including a controlled overlap for late-arriving records.
Our Citi Bike pipeline maintains a checkpoint in Redshift, recording the last successfully completed processing boundary.
For example:
Example: Incremental processing windows
Illustrative processing windows. An overlap helps recover late data, while deduplication prevents repeated observations from appearing in final tables.
Understand:
The difference between event time, ingestion time, and processing time.
Why checkpoints advance only after successful downstream processing.
Why a failed batch must not be marked complete.
How inclusive and exclusive boundaries avoid missing records.
Why a two-hour overlap can improve reliability, but requires deduplication.
The distinction between at-least-once processing and exactly-once results.
Required reading: AWS Glue job bookmarks.
You may use Glue bookmarks or implement your own checkpoint mechanism. If you use bookmarks, explain their limitations and how they interact with your input source.
3. Idempotency and deduplication
An idempotent operation produces the same intended final state when repeated with the same input.
For example, suppose a station observation has:
station_id = 123
snapshot_timestamp = 2026-10-14 12:00:00
available_bikes = 8
If the same observation is loaded three times, the canonical table should still contain only one logical observation for that station and timestamp.
You must understand how to achieve this using stable business keys, staging tables, MERGE, NOT EXISTS, or other appropriate SQL techniques.
Required reading: Amazon Redshift MERGE command.
4. Orchestration with Step Functions
AWS Step Functions coordinates multiple tasks and tracks their outcomes.
Understand the difference between starting a Glue job asynchronously and waiting for it to complete.
Our class pipeline uses the synchronous Glue integration, ensuring the Silver-to-Redshift job does not begin until Bronze-to-Silver has completed successfully.
Study Task, Choice, Wait, Succeed, and Fail states; retries and catches; state inputs and outputs; and execution history.
Required reading: AWS Step Functions integration with AWS Glue.
5. Redshift dimensional modeling
Your Gold layer must support analytical queries, not simply duplicate the Silver data.
Review:
Fact tables versus dimension tables.
Grain: what one row in a fact table represents.
Natural keys versus surrogate keys.
Referential integrity and orphan detection.
Slowly changing dimensions, particularly Type 1 and Type 2.
Why dimensions are commonly populated before facts.
Required reading: Review the relevant chapters of The Data Warehouse Toolkit by Ralph Kimball and Margy Ross.
6. IAM and database authorization
AWS IAM permissions and Redshift database permissions are different.
In our class project, the coordinator Lambda initially had AWS permission to execute Redshift Data API statements but lacked database-level SELECT privileges on the checkpoint and landing tables.
Study how IAM roles, trust policies, service permissions, schema privileges, table privileges, and stored-procedure permissions interact.
Required reading: Amazon Redshift GRANT documentation.
7. Infrastructure as code and recovery
Terraform describes and manages AWS infrastructure. Its state records which existing resources belong to a configuration.
Understand why Terraform state must be preserved, why importing existing resources differs from creating them, and why a plan showing unexpected replacements or destruction must be investigated before applying.
Required reading: Terraform state documentation.
Part 2 — Implementation requirements
You may use the Citi Bike API or select another source with regularly changing data, such as weather observations, transit activity, or public operational data.
Your project must meet the following standards.
Required architecture
Data source → Scheduled ingestion → S3 Bronze
AWS Glue → S3 Silver (Parquet)
AWS Glue → Redshift landing
Redshift canonical → Gold fact and dimensions
Step Functions must orchestrate the processing stages and coordinate checkpoint advancement.
Phase A — Data ingestion
Build a Lambda function that retrieves data from your source and writes it into your own S3 bucket.
Acceptance standards:
New data is ingested automatically at a documented interval.
Raw records are preserved in Bronze.
Each source file can be associated with an ingestion timestamp.
New files do not overwrite earlier raw files unintentionally.
Failures are recorded in CloudWatch Logs.
Your Lambda does not require manual execution for normal ingestion.
Phase B — Incremental Bronze-to-Silver
Create a Glue job that processes only the records eligible for the current batch.
Acceptance standards:
The job receives or determines a processing boundary.
It avoids scanning and transforming all historical data unnecessarily.
It applies explicit schemas and appropriate data types.
It removes duplicates using a documented logical key.
It writes Parquet data into Silver.
It produces identifiable batch output.
It fails visibly when a required input or transformation is invalid.
An acceptable batch directory might look like:
silver/observations/batch_id=20261014T120000Z/
Phase C — Incremental Silver-to-Redshift
Create a second Glue job that loads the current Silver batch into a Redshift landing table.
Acceptance standards:
The job loads the intended batch rather than the entire Silver history.
Every loaded record can be associated with its batch ID.
Redshift credentials are handled through an approved connection or IAM mechanism, not hardcoded in scripts.
Loading failures cause the job to fail.
Repeated staging loads cannot cause duplicate canonical or Gold records.
Phase D — Canonical and Gold modeling
Create a canonical table and a small star schema.
Minimum requirements:
One fact table.
Two dimension tables.
At least three useful analytical SQL queries.
Documented fact-table grain.
A deduplication strategy.
Checks for duplicate business keys and orphan dimension references.
For Citi Bike, appropriate analyses include station utilization, availability by hour, and stations frequently reporting low availability.
For another dataset, select equivalent business questions.
Phase E — Checkpoint management
Implement a mechanism that records successful processing progress.
You may use a Redshift checkpoint table, DynamoDB, or another justified approach.
Acceptance standards:
A batch reads the prior completed checkpoint.
Its input window is deterministic once the batch begins.
A failed batch does not advance the checkpoint.
A successful batch advances it only after the required downstream writes and checks complete.
A retry can safely recover without duplicating final records.
The pipeline has a documented policy for late-arriving data.
You do not need to backfill historical data. You may initialize the checkpoint when your pipeline first begins collecting data, provided you explain how that initial boundary is chosen.
Phase F — Orchestration and scheduling
Implement a Step Functions state machine that runs the processing stages in order.
Acceptance standards:
Each Glue job runs only after its predecessor succeeds.
Task failures are visible in execution history.
The workflow reaches a Succeed state only after Gold processing and checkpoint completion.
A schedule starts the workflow automatically.
The schedule interval is documented; 30 minutes is recommended for this assignment.
Overlapping executions are prevented or safely handled through an explicit concurrency strategy.
Retries are configured only where safe, and their behavior is explained.
Phase G — Terraform
Use Terraform to manage at least the Step Functions state machine, scheduling resources, and the IAM roles and policies created for them.
You may also manage Lambda and Glue resources through Terraform.
Acceptance standards:
terraform fmt succeeds.
terraform validate succeeds.
terraform plan is reviewed before applying.
Terraform state is preserved between deployments.
Existing resources are imported when appropriate rather than recreated.
No unexpected resource destruction is present in the plan.
Secrets and AWS credentials are not committed to source control.
Part 3 — Required testing
Your project will not be considered complete merely because all AWS resources exist. You must demonstrate that the pipeline behaves correctly.
Student validation checklist
0 / 8 completed
 
Initial successful run
A batch moves through every stage and reaches Gold.
Second incremental run
Only newly eligible data, plus any documented overlap, is processed.
Idempotency
Reprocessing the same logical observations does not create duplicate canonical or Gold records.
Failure recovery
A controlled failure prevents checkpoint advancement; after correction, processing resumes safely.
Checkpoint verification
The recorded completion boundary matches the successfully processed batch.
Scheduling
At least two automatic executions are observed, with no unsafe overlap.
Data quality
Duplicate and orphan checks pass, and analytical queries return meaningful results.
Cost and cleanup
Unneeded resources are stopped or removed, and recurring charges are identified.
Part 4 — Written questions
Answer the following in your own words. Each answer should generally be one or two paragraphs, with a diagram or SQL example where useful.
Why is incremental processing generally more efficient than full refreshes, and under what circumstances might a full refresh still be appropriate?
Why should a checkpoint advance only after the Gold layer has been successfully updated?
Explain the difference between Glue bookmarks and an application-managed checkpoint.
How does overlapping processing help with late-arriving records? What new problem does it introduce?
Explain the difference between an idempotent pipeline and one that guarantees each physical operation executes exactly once.
Why is a landing table useful between Glue and the canonical Redshift table?
Why should a fact table have a clearly defined grain before its schema is designed?
What happens if two Step Functions executions read the same checkpoint simultaneously? How would you prevent incorrect results?
Explain why a Lambda might have redshift-data:ExecuteStatement permission but still receive a database permission denied error.
Why does a successful Terraform apply not prove that a pipeline is operationally correct?
Part 5 — Submission requirements
Submit one Git repository containing the implementation and documentation, together with screenshots or exported logs demonstrating successful execution.
The repository should include:
aws-incremental-pipeline/
├── README.md
├── architecture/
│   └── pipeline-diagram.png
├── terraform/
│   ├── main.tf
│   ├── iam.tf
│   └── scheduler.tf
├── lambda/
│   └── ingest.py
├── glue/
│   ├── bronze_to_silver.py
│   └── silver_to_redshift.py
├── sql/
│   ├── create_tables.sql
│   ├── process_batch.sql
│   ├── data_quality_checks.sql
│   └── analytics.sql
├── evidence/
│   ├── successful-execution.png
│   ├── checkpoint.png
│   └── query-results.png
└── homework-answers.md
This structure is illustrative; equivalent organization is acceptable. Do not include Terraform state files, credentials, passwords, or private keys in the repository.
The README.md must explain how the pipeline works, how it is deployed, how it is scheduled, how to recover from failure, and how to stop recurring AWS costs.
Part 6 — Grading rubric
Category
    
Weight


Understanding of incremental processing and checkpoints
    
20%


Bronze and Silver implementation
    
15%


Redshift landing, canonical, and Gold modeling
    
20%


Step Functions orchestration and scheduling
    
15%


Idempotency, failure recovery, and data quality
    
15%


Terraform, IAM, documentation, and cost awareness
    
15%


Total
    
100%
Minimum passing standard: 70%. However, a pipeline that only performs full refreshes cannot receive more than 60%, regardless of how well its infrastructure is configured. A pipeline that has never completed a successful end-to-end execution cannot receive more than 65%.
A score of 90% or higher requires a demonstrably repeatable incremental process, successful recovery from at least one controlled failure, and clear evidence that retries do not corrupt final analytical data.
Definition of done
A completed assignment must demonstrate this behavior:
New data arrives automatically, is preserved in Bronze, processed incrementally into Silver, loaded into Redshift, transformed into analytical Gold tables, and recorded as successfully completed in a checkpoint. Subsequent scheduled executions process the next eligible data without duplicating prior observations, and failures can be recovered without rebuilding the pipeline.
The central lesson is that a production-oriented data pipeline is not merely a sequence of successful ETL jobs. It is a coordinated system that tracks what has been processed, knows when work is complete, handles retries safely, and produces trustworthy analytical data.
What is the medallion lakehouse architecture? | Databricks on AWS
Learn how to use the medallion architecture to create a reliable and optimized data architecture and maximize the usability of data in a lakehouse.
 
main homework ^
 
Optional Extra Credit Assignment: Deploy a Real-Time Data Dashboard on AWS
Course: AWS Data Engineering
Assignment Type: Optional Extra Credit
Estimated Time: 3–5 hours
Difficulty: Intermediate
Total Available: 100 points + 20 bonus points
Objective
In this assignment, you will design, develop, and deploy an interactive data dashboard using Python, Streamlit, Terraform, and AWS EC2.
The dashboard should visualize data from the Citi Bike pipeline we developed in class, or from a comparable public dataset of your choosing.
Your goal is to demonstrate that you can take data from an external source or existing data pipeline and make it available to end users through a functional, cloud-hosted analytics application.
You are not required to recreate the entire pipeline from class. Focus on building the dashboard, provisioning the necessary AWS infrastructure, and connecting the application to a data source.
Part 1: Design Your Dashboard (15 points)
Create a basic design for an interactive dashboard.
Your application must include:
A descriptive title and explanation of the dataset.
At least three summary metrics, such as total stations, available bikes, and available docks.
At least one interactive chart.
At least two user-selectable filters or visualization options.
A data table displaying selected records.
Recommended dataset: Citi Bike's publicly available GBFS station information and station status feeds.
You may alternatively use public transportation, weather, traffic, or another dataset containing frequently updated information.
Deliverable: A short description of your dashboard's purpose, its intended users, and the metrics you plan to display.
Part 2: Build the Streamlit Application (25 points)
Develop a working Streamlit application in Python.
Required functionality
Retrieve data from your selected source using Python.
Process the data using Pandas.
Display summary metrics using st.metric().
Create an interactive visualization using Plotly, PyDeck, or Streamlit's built-in chart components.
Provide interactive filters using Streamlit widgets.
Handle unavailable data sources or API errors without crashing the application.
Map visualization
If you use Citi Bike data, create an interactive map displaying station locations.
Markers should be color-coded according to a selected metric, such as:
Number of available bikes.
Number of available docks.
Station utilization percentage.
Number of available electric bikes, if supported by the source.
Users should be able to select the metric used for coloring the map.
For other datasets, a comparable interactive visualization is acceptable.
Suggested application structure
citibike-dashboard/
├── app.py
├── requirements.txt
├── dashboard.tf
├── dashboard-user-data.sh.tftpl
└── README.md
You may organize your project differently if you can explain your design decisions.
Deliverable: A functional Streamlit application that runs locally before deployment.
Part 3: Provision AWS Infrastructure Using Terraform (25 points)
Deploy your application to AWS EC2 using Terraform.
Your Terraform configuration must provision:
An EC2 instance running Amazon Linux or Ubuntu.
A security group allowing access to the Streamlit application on port 8501.
An IAM instance role with the permissions required by your application.
An EC2 instance profile attaching the role.
An automated initialization script that installs dependencies and starts Streamlit.
Terraform outputs displaying the instance ID and application URL.
Security requirements
Do not hardcode AWS access keys in your Python application.
Use IAM roles when AWS services require authentication.
Restrict inbound traffic to your own IP address or another explicitly authorized range.
Do not open SSH access to the entire internet.
Do not place database passwords in your Git repository.
You should be able to deploy your dashboard using:
terraform init
terraform validate
terraform plan
terraform apply
Before applying, inspect the Terraform plan and verify which resources will be created, modified, or destroyed.
Deliverable: Terraform configuration files and evidence of a successful deployment.
Part 4: Demonstrate a Working Dashboard (20 points)
Once deployed, access your Streamlit application through the EC2 instance's public IP address.
Verify that:
The dashboard loads successfully in a web browser.
Summary metrics display meaningful values.
Charts and filters respond to user interaction.
Data can be refreshed without redeploying the application.
The application recovers from a simulated page refresh or browser reconnection.
If your dataset updates frequently, demonstrate that the dashboard can retrieve newer observations.
Explain the difference between the frequency at which your dashboard refreshes and the frequency at which the underlying data source updates.
Deliverable: Two or three screenshots showing the dashboard and its interactive functionality.
Part 5: Documentation and Cost Management (15 points)
Create a README.md explaining:
The purpose and architecture of your dashboard.
The source of your data.
How to install and run the application locally.
How to deploy it using Terraform.
How IAM permissions are used.
How to access the dashboard.
How to stop the EC2 instance when it is not needed.
How to clean up the infrastructure safely.
Required cost-management exercise
Use the AWS CLI to identify and stop your dashboard EC2 instance:
aws ec2 stop-instances \
  --instance-ids <YOUR_INSTANCE_ID>
Verify that it has stopped:
aws ec2 describe-instances \
  --instance-ids <YOUR_INSTANCE_ID> \
  --query 'Reservations[*].Instances[*].State.Name'
Explain which AWS charges stop when EC2 is stopped and which may continue.
Important: If you are using the shared classroom AWS account, do not modify or destroy infrastructure belonging to other students or the instructor. Use uniquely named resources and isolate your Terraform state.
Bonus Challenges (Up to 20 Additional Points)
Bonus A: Redshift Integration (10 points)
Connect your dashboard to your existing Amazon Redshift data warehouse.
Use the Redshift Data API to query historical observations and display at least one time-series visualization.
Your implementation should:
Authenticate through the EC2 instance's IAM role.
Use a read-only Redshift database identity.
Query an existing fact or canonical observation table.
Display historical trends alongside the live dashboard.
Handle database permission errors gracefully.
Explain why IAM permissions and Redshift database privileges are separate authorization mechanisms.
Bonus B: Advanced Dashboard Features (5 points)
Implement at least two enhancements:
Automatic refresh with a configurable interval.
Station search by name.
Additional map color schemes or metric selection.
A time-range filter for historical data.
Downloadable CSV data.
Station-level historical comparisons.
Bonus C: Operational Automation (5 points)
Implement one operational improvement through Terraform:
CloudWatch monitoring for the EC2 instance.
A scheduled EC2 shutdown.
Application health monitoring.
An automated recovery or restart mechanism.
Explain how your improvement increases reliability or reduces costs.
Submission Requirements
Submit a GitHub repository or ZIP archive containing your application source code, Terraform files, dependency list, and README.
Also include:
Screenshots of the running dashboard.
A short description of the AWS resources deployed.
Evidence that terraform validate succeeds.
A brief explanation of one technical challenge you encountered and how you resolved it.
Do not submit AWS credentials, private keys, .tfstate files, or other sensitive configuration.
Grading Rubric
Category    Points
Dashboard design and metrics    15
Streamlit application functionality    25
Terraform infrastructure and security    25
Successful deployment and demonstration    20
Documentation and cost management    15
Base total    100
Optional bonus challenges    +20
Maximum    120
Questions to Consider
Be prepared to explain the following during a brief demonstration or discussion:
Why did you choose Streamlit rather than building a traditional web application?
What is the difference between Terraform provisioning and EC2 user-data initialization?
How does your application authenticate to AWS without storing credentials?
What happens when the external data source becomes unavailable?
How would you support 100 simultaneous dashboard users?
What changes would you make to deploy this application in a production environment?
Why might a dashboard displaying data from Redshift not be truly real-time?
What is the difference between stopping an EC2 instance and destroying it through Terraform?
Final Expectations
The objective is not to create a production-ready analytics platform. It is to demonstrate your ability to integrate several important data engineering concepts:
Data ingestion → Data processing → Cloud infrastructure → Application deployment → Interactive analytics
A relatively simple dashboard that is functional, secure, reproducible, and well documented will receive more credit than an elaborate dashboard that cannot be reliably deployed.
This is an optional assignment. You may use the classroom implementation as a reference, but your submitted application should demonstrate your own understanding of the architecture and code.
Remember to stop your EC2 instance when you finish testing to avoid unnecessary AWS charges.
 
^ optional extra homework - focus on the previous post for the main assignment
