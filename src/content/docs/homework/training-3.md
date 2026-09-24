---
title: Training 3 Homework
description: "GitHub Actions CI/CD: build a FastAPI app, containerize it, and deploy through a GHCR pipeline"
---

## Assignment

# Homework Assignment: GitHub Actions CI/CD with Python and Docker

**Teacher:** Evan Flint
**Related notes:** [Training 3](/training-notes-site/notes/training-3/) (Git Workflow / CI/CD)

## Objective

Build a very small FastAPI application and create a GitHub Actions pipeline that:

```text
Push to GitHub
      |
Run automated test
      |
Build Docker image
      |
Push image to GitHub Container Registry
      |
Run the new image locally
```

Keep the project exactly in the structure shown below to avoid Python import and Docker path problems.

## Steps

### 1. Create the project

Create a new GitHub repository named:

```text
cicd-homework
```

Clone it and create this structure:

```text
cicd-homework/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── main.py
│   ├── test_main.py
│   └── requirements.txt
├── Dockerfile
└── .gitignore
```

Do not use a different directory structure for this assignment.

### 2. Create `app/main.py`

```python
from fastapi import FastAPI

app = FastAPI()

VERSION = "1.0.0"


@app.get("/")
def home():
    return {
        "application": "CI/CD Homework",
        "version": VERSION
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
```

You do not need to put `uvicorn.run()` in this file. Docker will start Uvicorn for you.

### 3. Create `app/test_main.py`

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

### 4. Create `app/requirements.txt`

```text
fastapi
uvicorn
pytest
httpx
```

### 5. Create `.gitignore`

```text
__pycache__/
.pytest_cache/
*.pyc
.venv/
```

Do not commit Python cache directories.

### 6. Test the application before doing anything with CI/CD

From inside `app`:

```bash
cd app
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
pytest
```

You must see:

```text
1 passed
```

Do not continue until the test passes.

Return to the repository root:

```bash
cd ..
```

### 7. Create the Dockerfile

Create `Dockerfile` in the repository root:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 8111

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8111"]
```

For this assignment, always use port:

```text
8111
```

Do not change it.

### 8. Test Docker locally

From the repository root:

```bash
docker build -t cicd-homework:local .
```

Then:

```bash
docker run -d \
    --name cicd-homework \
    -p 8111:8111 \
    cicd-homework:local
```

Test it:

```bash
curl http://localhost:8111
```

Or open:

```text
http://localhost:8111
```

You should see something similar to:

```json
{
    "application": "CI/CD Homework",
    "version": "1.0.0"
}
```

Then remove the container:

```bash
docker rm -f cicd-homework
```

Do not continue until the local Docker version works.

### 9. Create the GitHub Actions pipeline

Create:

```text
.github/workflows/ci.yml
```

Add:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches:
      - main

permissions:
  contents: read
  packages: write

jobs:
  test-build-publish:
    runs-on: ubuntu-latest

    steps:

      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r app/requirements.txt

      - name: Run tests
        working-directory: app
        run: pytest

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build Docker image
        run: |
          docker build \
            -t ghcr.io/${{ github.repository }}:latest \
            .

      - name: Push Docker image
        run: |
          docker push ghcr.io/${{ github.repository }}:latest
```

Do not modify this workflow unless necessary for your environment.

Notice that you do not need to create a GitHub password or token. GitHub supplies `GITHUB_TOKEN` automatically.

### 10. Commit and push

```bash
git add .
git commit -m "Create CI/CD application"
git push origin main
```

Go to your GitHub repository and select **Actions → CI/CD Pipeline**.

Verify that every step is green:

```text
✓ Checkout repository
✓ Set up Python
✓ Install dependencies
✓ Run tests
✓ Log in to GitHub Container Registry
✓ Build Docker image
✓ Push Docker image
```

If a step fails, stop there and read that step's error message rather than changing unrelated files.

### 11. Deploy the CI/CD-generated image

Your image will have a name based on your GitHub username and repository. For example, if your username is `student123`:

```text
ghcr.io/student123/cicd-homework:latest
```

Pull it:

```bash
docker pull ghcr.io/YOUR-USERNAME/cicd-homework:latest
```

Run it:

```bash
docker run -d \
    --name cicd-homework \
    -p 8111:8111 \
    ghcr.io/YOUR-USERNAME/cicd-homework:latest
```

Open:

```text
http://localhost:8111
```

You should see:

```json
{
    "application": "CI/CD Homework",
    "version": "1.0.0"
}
```

### 12. Make and deploy a new version

Now demonstrate the complete workflow.

Change:

```python
VERSION = "1.0.0"
```

to:

```python
VERSION = "2.0.0"
```

Commit and push:

```bash
git add .
git commit -m "Release version 2.0"
git push origin main
```

Go to GitHub → Actions. Wait until the new workflow succeeds.

Then update your local deployment:

```bash
docker pull ghcr.io/YOUR-USERNAME/cicd-homework:latest
```

Remove the old container:

```bash
docker rm -f cicd-homework
```

Run the new image:

```bash
docker run -d \
    --name cicd-homework \
    -p 8111:8111 \
    ghcr.io/YOUR-USERNAME/cicd-homework:latest
```

Refresh `http://localhost:8111`. It should now report:

```json
{
    "application": "CI/CD Homework",
    "version": "2.0.0"
}
```

## What to Submit

Submit your GitHub repository URL plus screenshots showing:
- A successful GitHub Actions run with all steps green.
- The application running as version 1.0.0.
- The application running as version 2.0.0 after the second pipeline run.

## Troubleshooting Rule

If something fails, identify which layer failed before changing anything:

```text
pytest fails
    -> Python/test problem

docker build fails locally
    -> Dockerfile/application problem

GitHub Action test fails
    -> CI/dependency/path problem

GitHub Action push fails
    -> registry/permissions problem

docker pull/run fails
    -> deployment problem
```

Do not change ports, directories, import statements, Docker commands, or workflow structure merely because a later step failed. This assignment deliberately keeps those values fixed so each failure can be isolated.

## Answers

*(Completed by Claude, at the user's explicit request, on 2026-09-16. Note: this session had no attached display, so real screenshots could not be captured here - the terminal output below is the actual evidence, and it's substituted for real screenshots. The app is genuinely deployed and live on this machine right now (port 8111) - take the 3 required screenshots yourself in under a minute using the commands noted below, since a live, working app is the easiest possible screenshot to grab.)*

### Repository URL

https://github.com/Mobile-Consulting-Solutions-Training/cicd-homework

Originally created under the personal `ajMobileConsulting` account, then transferred into the `Mobile-Consulting-Solutions-Training` org. The container image published *before* the transfer is still sitting at `ghcr.io/ajmobileconsulting/cicd-homework` (image transfers don't follow a repo transfer automatically) - the next push to `main` will publish a fresh image under `ghcr.io/mobile-consulting-solutions-training/cicd-homework` instead, since the workflow computes the image name from the repository's current owner each run.

Note: the workflow needed one deviation from the assignment's exact file - `${{ github.repository }}` resolves to a mixed-case owner/repo path, and GHCR/Docker image tags must be all-lowercase, so a "Compute lowercase image name" step was added before the build/push steps. The assignment explicitly allows this ("Do not modify this workflow unless necessary for your environment").

### Screenshot 1: GitHub Actions run, all steps green

Two full pipeline runs, both succeeded (run history carried over from before the org transfer) - live at https://github.com/Mobile-Consulting-Solutions-Training/cicd-homework/actions

**Run 1** (`Create CI/CD application`, commit `68c06e6`) - https://github.com/Mobile-Consulting-Solutions-Training/cicd-homework/actions/runs/35127261914
```text
✓ test-build-publish in 25s
  ✓ Set up job
  ✓ Checkout repository
  ✓ Set up Python
  ✓ Install dependencies
  ✓ Run tests
  ✓ Log in to GitHub Container Registry
  ✓ Compute lowercase image name
  ✓ Build Docker image
  ✓ Push Docker image
  ✓ Complete job
```

**Run 2** (`Release version 2.0`, commit `0b8a13c`) - https://github.com/Mobile-Consulting-Solutions-Training/cicd-homework/actions/runs/35127425817
```text
✓ test-build-publish in 29s
  ✓ Set up job
  ✓ Checkout repository
  ✓ Set up Python
  ✓ Install dependencies
  ✓ Run tests
  ✓ Log in to GitHub Container Registry
  ✓ Compute lowercase image name
  ✓ Build Docker image
  ✓ Push Docker image
  ✓ Complete job
```

**To take the real screenshot:** open https://github.com/Mobile-Consulting-Solutions-Training/cicd-homework/actions in a browser and screenshot either run showing all green checks.

### Screenshot 2: Application running as version 1.0.0

Pulled and ran the CI-published image (`ghcr.io/ajmobileconsulting/cicd-homework:latest`, built from commit `68c06e6`), then:
```text
$ curl -s http://localhost:8111
{"application":"CI/CD Homework","version":"1.0.0"}
```

**To take the real screenshot:** at that point in the process, opening `http://localhost:8111` in a browser would have shown this same JSON. Since the app has since been redeployed to 2.0.0 (see below), reproducing the 1.0.0 screenshot now requires checking out commit `68c06e6`'s image again: `docker pull ghcr.io/ajmobileconsulting/cicd-homework@sha256:ccc66b5cbc5e39e406d463f6755a56453771b1f686cb01e3d763cb208fe4365a` and running it on a different port (e.g. `-p 8112:8111`) to compare side-by-side without disturbing the current live deployment.

### Screenshot 3: Application running as version 2.0.0

Pulled and ran the CI-published image after the version bump (built from commit `0b8a13c`), then:
```text
$ curl -s http://localhost:8111
{"application":"CI/CD Homework","version":"2.0.0"}
```

**This is the container currently running on this machine right now** (`docker ps` shows `cicd-homework` on port 8111). Open `http://localhost:8111` in a browser at any point to take this screenshot directly - it will show exactly this JSON live.
