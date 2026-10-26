---
title: "Training 13 Homework"
description: "Homework assignment for Training 13: Open Table Formats and NoSQL."
sidebar:
  order: 13
---

:::note
The assignment prompt as given in class. Related notes: [Training 13](/training-notes-site/notes/training-13/).
:::

## Homework: Schema Evolution, MongoDB, Kafka, and Real-Time Dashboards

### Objective

This assignment reinforces the topics covered in class:

- Schema evolution
- Delta Lake schema evolution
- Avro schemas and serialization
- Protocol Buffers (Protobuf)
- NoSQL database concepts
- MongoDB
- Kafka consumers
- Spark Structured Streaming
- Writing streaming data to MongoDB
- Querying MongoDB
- Building a real-time Streamlit dashboard

You will complete both a **reading/research assignment** and a **technical assignment**.

---

## Part 1 – Reading and Research

Research the following topics. You should be prepared to discuss your answers in class.

#### 1. Schema Evolution

Explain what **schema evolution** means and why it is important in a production data pipeline.

Research:

- Adding a new field
- Removing a field
- Changing a field's data type
- Renaming a field
- Backward compatibility
- Forward compatibility

Consider what might happen when a producer begins sending a new version of a schema while consumers are still expecting the old version.

#### 2. Delta Lake

Research how Delta Lake handles schema changes.

In particular, explain:

- Schema enforcement
- Schema evolution
- `mergeSchema`
- `overwriteSchema`

What is the difference between **schema enforcement** and **schema evolution**?

#### 3. Avro

Research how Avro stores and manages schemas.

Answer the following:

- Where is the Avro schema stored?
- What is an `.avsc` file?
- Does Avro require generated/compiled classes?
- How does Avro handle adding a new optional field?
- What are default values used for?
- Why is Avro commonly used with Kafka?

#### 4. Protocol Buffers

Research Protocol Buffers and `.proto` files.

Answer:

- What information is contained in a `.proto` file?
- What does `protoc` do?
- Why are Protobuf schemas normally compiled?
- What are field numbers?
- Why should an existing field number not be reused?
- How can Protobuf support schema evolution even though generated code may need to be regenerated?

#### 5. Avro vs. Protobuf

Create a small comparison covering:

| Feature | Avro | Protobuf |
|---|---|---|
| Schema definition | | |
| Compilation required | | |
| Schema evolution | | |
| Human-readable data | | |
| Typical Kafka usage | | |
| Advantages | | |
| Disadvantages | | |

Be prepared to explain which format you would choose for a data engineering pipeline and **why**.

There is not necessarily one correct choice.

---

## Part 2 – NoSQL and MongoDB

Research the difference between relational and NoSQL databases.

Understand the following NoSQL categories:

- Document databases
- Key-value databases
- Wide-column databases
- Graph databases

For MongoDB specifically, explain:

- Database
- Collection
- Document
- `_id`
- BSON
- Index
- Compound index

Answer the following question:

> Why might a streaming application store processed events in MongoDB instead of immediately inserting them into a traditional relational database?

Consider scalability, schema flexibility, query patterns, and application requirements.

---

## Part 3 – Technical Assignment

### Scenario

You have been asked to build a small real-time monitoring system.

Your architecture will be:

```text
Data Producer
      |
      v
    Kafka
      |
      v
Spark Structured Streaming
      |
      v
   MongoDB
      |
      v
  Streamlit
```

You may use the code from class as a starting point, but your final solution must make changes to the data being processed and the dashboard.

---

### Task 1 – Produce Streaming Data

Create or modify a Kafka producer that continuously sends JSON events.

You may use:

- A public API
- Weather data
- Financial/market data
- Transportation data
- Sports data
- Simulated IoT data
- Simulated application activity
- Another instructor-approved source

Real data is preferred where practical.

Each event must contain **at least five fields**.

For example:

```json
{
    "device_id": "machine-04",
    "temperature": 84.2,
    "pressure": 1013.4,
    "status": "running",
    "event_time": "2026-09-29T15:42:10"
}
```

At least one field should be useful as the **Kafka message key**.

---

### Task 2 – Kafka → Spark → MongoDB

Create a Spark Structured Streaming consumer.

Your program must:

1. Connect to Kafka.
2. Subscribe to your topic.
3. Parse the JSON message using a defined Spark schema.
4. Perform at least **one transformation** on the data.
5. Add a processing timestamp.
6. Write the processed records to MongoDB.

Examples of transformations include:

- Celsius → Fahrenheit
- Calculate total price
- Categorize a measurement
- Calculate message length
- Normalize a string
- Create an alert/status field
- Filter invalid records

Your MongoDB documents should retain the following Kafka information:

```text
key
partition
offset
```

along with the actual event data.

---

### Task 3 – Query MongoDB

Using `mongosh`, demonstrate that your streaming data was successfully stored.

Perform at least **three different queries**.

Your queries must include:

1. Retrieve recent documents.
2. Filter documents based on one of your fields.
3. Sort or limit the results.

Create at least **one index** appropriate for one of your queries.

Use:

```javascript
db.collection.getIndexes()
```

to verify that the index exists.

#### Bonus

Use:

```javascript
.explain("executionStats")
```

to demonstrate whether MongoDB performs a:

```text
COLLSCAN
```

or:

```text
IXSCAN
```

for one of your queries.

---

## Part 4 – Real-Time Streamlit Dashboard

Create a Streamlit dashboard that reads from your MongoDB collection.

The dashboard must automatically refresh so that new Kafka events become visible without manually restarting the application.

Your dashboard must contain:

#### Metrics

At least **three current metrics**.

Examples:

- Total events
- Average temperature
- Current price
- Number of active devices
- Average response time
- Maximum measurement

#### Visualization

At least **two charts**.

At least one chart must show a measurement changing **over time**.

Examples:

```text
Temperature over time
Events per minute
Price over time
CPU utilization over time
Requests per minute
```

#### Recent Events

Include a table showing recent events.

The table should contain relevant application data plus at least one Kafka field such as:

```text
partition
offset
```

---

## Part 5 – Schema Evolution Exercise

After your pipeline is working, modify the schema.

Add **one new field** to the events produced by your Kafka producer.

For example, change:

```json
{
    "device_id": "machine-04",
    "temperature": 84.2
}
```

to:

```json
{
    "device_id": "machine-04",
    "temperature": 84.2,
    "battery_level": 87
}
```

Update your consumer so the new field is recognized.

Then answer:

1. What happened to MongoDB documents created before the field existed?
2. Did MongoDB require you to alter the collection schema?
3. What would happen if the Spark schema were **not** updated?
4. How would this change be handled differently with Avro?
5. How would this change be handled differently with Protobuf?
6. How would a similar schema change be handled when writing to a Delta table?

---

## Deliverables

Submit **one ZIP file** containing:

```text
lastname_streaming_homework.zip

├── producer.py
├── consumer.py
├── dashboard.py
├── README.md
└── screenshots/
    ├── mongodb.png
    └── dashboard.png
```

#### `README.md`

Include:

- Your Kafka topic name
- Description of your data source
- Description of your Kafka key
- Description of your Spark transformation
- MongoDB database and collection names
- Index you created and why
- Answers to the six schema-evolution questions from Part 5
- Your Avro vs. Protobuf comparison from Part 1

#### `mongodb.png`

Provide a screenshot showing `mongosh` successfully querying records written by your Kafka/Spark pipeline.

The screenshot should clearly show multiple documents.

#### `dashboard.png`

Provide a screenshot of your running Streamlit dashboard showing:

- At least three metrics
- At least two charts
- Recent event data

The screenshot must contain actual data produced by your pipeline.

---

## Minimum Success Criteria

A successful submission demonstrates the complete flow:

```text
Producer
   ↓
Kafka
   ↓
Spark Structured Streaming
   ↓
MongoDB
   ↓
Streamlit Dashboard
```

Your code does not need to be production-ready. The goal is to demonstrate that you understand how the components interact and can modify the examples from class rather than simply running them unchanged.
