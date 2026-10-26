---
title: Day 3 Vocabulary
description: Glossary of terms and definitions from the Training 3 study guide.
sidebar:
  order: 3
---

Vocabulary — Study Guide Day 3

## Git and Hosting
- **Git** — The version control tool that tracks commits, branches and merges.
- **GitHub** — Microsoft's Git hosting platform; largest community; CI/CD through GitHub Actions.
- **GitLab** — Git hosting platform with native built-in CI/CD and a strong self-hosted option.
- **Bitbucket** — Atlassian's Git hosting platform; integrates with Jira and Confluence.
- **Remote** — A copy of the repository on a hosting platform, e.g. `origin`.

## Branching
- **Branch** — A movable pointer to a commit, used to work on changes in isolation.
- **Git Flow** — Branching strategy using `main`, `develop`, `feature/*`, `release/*` and `hotfix/*`.
- **main** — The stable, production-ready branch.
- **develop** — The integration branch features branch from and merge back into.
- **feature branch** — A branch for one piece of work, merged back through a pull request.
- **release branch** — Cut from `develop` for final testing before a release.
- **hotfix branch** — Branched from `main` for an urgent production fix; merged into `main` and `develop`.
- **git switch / git checkout** — Commands to change branches; `switch` is the newer, clearer one.
- **git worktree** — Checks out several branches into separate directories at once, sharing one repository.

## Commits
- **Commit** — A permanent snapshot of staged changes with a message.
- **Staging area** — The middle step where `git add` collects changes for the next commit.
- **git diff** — Shows unstaged changes; `--staged` shows staged changes.
- **git log** — Shows commit history; `--oneline` condenses it.

## Pull Requests and Merging
- **Pull request (PR)** — A platform request to merge one branch into another, with CI and review.
- **Draft PR** — A PR visible for early feedback but marked not ready to merge.
- **Merge commit** — Merge strategy keeping all branch commits plus a commit joining them.
- **Squash and merge** — Merge strategy combining a PR's commits into one.
- **Rebase and merge** — Merge strategy replaying commits on the target for linear history.
- **Merge conflict** — When Git can't automatically combine changes to the same lines.
- **Conflict markers** — `<<<<<<< HEAD`, `=======`, `>>>>>>> branch` lines Git inserts around conflicting versions.

## Code Review
- **Code review** — Another person reading a PR's changes before merging.
- **Approve** — Review state: ready to merge.
- **Request changes** — Review state: must be fixed before merging.
- **Comment** — Review state: non-blocking feedback.

## Repository Discipline
- **.gitignore** — File of patterns Git should never track.
- **git rm --cached** — Stops tracking a file without deleting it locally.
- **Secret** — A key, password or token that must never be committed.
- **Protected branch** — A branch that only accepts changes through approved PRs with passing CI.
- **Branch naming convention** — Prefixes like `feature/`, `bugfix/`, `hotfix/`, `chore/`, `docs/`.

## Releases
- **Tag** — A permanent named pointer to a commit, used to mark releases.
- **Lightweight tag** — A tag that is only a name.
- **Annotated tag** — A tag with author, date and message; preferred for releases.
- **Semantic versioning (SemVer)** — `MAJOR.MINOR.PATCH` version numbers.
- **MAJOR** — Increases for breaking changes.
- **MINOR** — Increases for new backward-compatible features.
- **PATCH** — Increases for bug fixes.
- **CHANGELOG.md** — Human-readable list of changes per version, newest first.

## CI/CD
- **CI/CD** — Continuous integration and continuous delivery/deployment: automated build, test and release.
- **Checkout** — Stage that pulls the code at the commit being built.
- **Build** — Stage that compiles or installs dependencies and packages the code.
- **Lint** — Automated style and quality checks.
- **Unit test** — Tests one isolated piece of code.
- **Integration test** — Tests several real pieces working together.
- **Security scan** — Checks code and dependencies for known vulnerabilities.
- **Artifact** — The packaged, deployable output (Docker image, `.jar`, `.whl`).
- **Fail fast** — Running cheap checks first so problems stop the pipeline early.
- **pytest** — Third-party Python test tool using plain `assert`.
- **unittest** — Python's built-in, class-based test module.

## Jenkins
- **Jenkins** — Open-source automation server for CI/CD pipelines.
- **Controller** — Central Jenkins server that schedules jobs and serves the UI.
- **Agent** — Machine that executes pipeline steps.
- **Jenkinsfile** — Pipeline-as-code file in the repository, written in Groovy.
- **Groovy** — JVM scripting language Jenkinsfiles are written in.
- **Declarative pipeline** — Structured Jenkinsfile style (`pipeline { stages { } }`).
- **Scripted pipeline** — Full-Groovy Jenkinsfile style for complex logic.
- **Webhook** — The hosting platform notifying Jenkins immediately on a push or PR.
- **Poll SCM** — Jenkins checking the repository for changes on a schedule.
- **Plugin** — Add-on supplying most Jenkins features (Git, Docker, notifications).

## Docker Registries
- **Docker Hub** — The default public registry for Docker images.
- **Registry** — A service that stores and serves container images.
- **Image repository** — Named collection of an image's versions, `username/repo`.
- **Image tag** — Label on an image version, e.g. `1.0.0` or `latest`.
- **docker push / docker pull** — Upload an image to / download an image from a registry.
- **docker tag** — Gives an existing image a new name or tag.
- **GHCR / ECR / Artifact Registry** — GitHub, AWS and Google alternatives to Docker Hub.
