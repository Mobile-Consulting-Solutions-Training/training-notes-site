# Big Data Handbook

**Live site: https://mobile-consulting-solutions-training.github.io/training-notes-site/**

A shared study handbook for the 45-day Data Engineering bootcamp: class notes, study guides, vocabulary, walkthroughs and interview prep, all in one searchable site.

## What's inside

| Section | What you'll find |
|---|---|
| **Notes** | One page per training day: definitions, expanded explanations, comparison tables and demo code |
| **Study Guides** | Per-day summary, cheat sheet and spoken-quiz flashcards |
| **Vocabulary** | Per-day glossary of every term covered |
| **Walkthroughs** | Step-by-step rebuilds of the class pipelines (AWS, Hive/Spark, star schemas, and more) |
| **Homework** | Assignment prompts only, never answers |
| **Final Project** | Capstone requirements and timeline |
| **Reference** | Cheat sheets, AWS/Azure/GCP comparison, pipeline diagrams, code library (Python, SQL, Scala, shell), errors and fixes, tool index, videos |
| **Interview Prep** | Question bank for big data, cloud/DevOps, programming, platforms and behavioral rounds |
| **Practice** | Interactive flashcards and SQL practice problems |
| **What's New** | Recent additions |

## Topics covered

Python and SQL foundations → Hadoop, Hive and Spark → data modeling and star schemas → AWS (S3, Glue, Redshift, EMR, Lambda) → Databricks, Delta Lake and MLflow → Azure (ADLS, Data Factory, Synapse, Event Hubs, Fabric) → GCP (BigQuery, Dataflow, Pub/Sub, Looker Studio) → capstone project.

## Notes on content

- Code is reconstructed from class demos, not copied exactly. Check it before you rely on it.
- Pages are updated as the course goes on. See **What's New** for the latest.

## Running locally

```bash
npm install
npm run dev      # http://localhost:4321/training-notes-site/
npm run build    # static output in dist/
```

Built with [Astro Starlight](https://starlight.astro.build). Pushing to `main` deploys to GitHub Pages.
