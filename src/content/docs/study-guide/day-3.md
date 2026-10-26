---
title: Study Guide - Day 3
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 3: Git Workflow"
sidebar:
  order: 30
---

Study Guide - Day 3 (source: notes/Training 3.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Git Hosting Platforms.** GitHub (Microsoft, largest community, GitHub Actions), GitLab (built-in CI/CD, strong self-hosting, all-in-one DevOps), Bitbucket (Atlassian, Jira/Confluence integration, Bitbucket Pipelines). Git itself works the same on all three; the platforms add remote storage, pull requests, CI/CD, issues and access control. Choice depends on the team's ecosystem.

**Branching (Git Flow).** `main` = stable/production, `develop` = integration branch, `feature/*` = one piece of work branched from `develop` and merged back through a PR, `release/*` = cut from `develop` for final testing, `hotfix/*` = branched from `main` for urgent production fixes, merged into both `main` and `develop`. `git switch -c` (newer) and `git checkout -b` (older) both create and switch.

**Git Worktree.** Checks out several branches of one repository into separate directories at the same time. All worktrees share one `.git` object database and history. Use case: fix production on `main` without stashing or committing unfinished feature work. `git worktree add -b <branch> <path>`, `list`, `remove`, `prune`.

**Commits and the Staging Area.** `git add` stages changes; `git commit` saves what's staged as a permanent snapshot. Staging lets you build a commit from only some changes. Messages: short present-tense summary ("Add user authentication"), then optionally *why*.

**Pull Requests.** A request to merge one branch into another, opened on the hosting platform (not a Git feature). Flow: push branch → open PR → CI runs → review → address feedback → merge. Draft PRs signal work in progress. Merge strategies: merge commit (keeps all commits plus a merge commit), squash and merge (one commit per PR), rebase and merge (linear history, no merge commit).

**Merge Conflicts.** Git inserts `<<<<<<< HEAD` (your branch), `=======` (separator), `>>>>>>> branch` (incoming). Resolve by editing to the final content you want, deleting all marker lines, then `git add` and `git commit`. The result can combine both sides.

**Code Review.** Reviewers check correctness, readability, test coverage, security and scope. States: Approve, Request changes (blocks), Comment (non-blocking). Good comments are specific, explain why, separate must-fix from suggestion, and talk about the code, not the person. Review also spreads knowledge across the team.

**Repository Discipline.** `.gitignore` for build output, dependencies, `.env` (already-tracked files need `git rm --cached`). Never commit secrets: history keeps them. Keep branches short-lived. Protected branches force changes through PRs with approval and passing CI. Branch prefixes: `feature/`, `bugfix/`, `hotfix/`, `chore/`, `docs/`.

**Release Basics.** Ready code merges to `main` and gets a **tag**. Annotated tags (`git tag -a v1.2.0 -m ...`) carry author, date and message; lightweight tags are just names. Tags must be pushed explicitly. **SemVer** `MAJOR.MINOR.PATCH`: major = breaking, minor = backward-compatible feature, patch = bug fix. `CHANGELOG.md` lists changes per version, newest first.

**CI/CD Pipeline Stages.** Checkout → Build → Lint → Unit Test → Integration Test → Security Scan → Artifact Creation. Cheap, fast checks run first so the pipeline fails fast.

**Testing in Python.** `pytest` (third-party, plain `assert`, most used) and `unittest` (built in, class-based, `self.assertEqual`). Runners auto-discover `test_*.py` files, `test_` functions and `Test` classes. Unit test = one piece in isolation; integration test = pieces working together (for example a real test database).

**Jenkins.** Open-source automation server. Controller schedules and serves the UI; agents run the work (like Spark's driver/executors). The `Jenkinsfile` defines the pipeline as code in the repo, written in Groovy: Declarative (structured `pipeline { stages { } }`, recommended) or Scripted (full Groovy). Steps run any shell command (`sh 'pytest'`). Triggers: webhook, poll SCM, cron schedule, manual. Most features come from plugins.

**Docker Hub.** A registry for container images (like GitHub for images). Repository `username/repo`, tags like `1.0.0` or `latest` (just a convention). Workflow: `docker login` → `docker build -t user/app:1.0.0 .` → `docker push` → elsewhere `docker pull` and `docker run`. `docker tag` re-labels an existing image. Alternatives: GHCR, AWS ECR, Google Artifact Registry, GitLab Container Registry.

---

# Part 2: Cheat Sheet

## Hosting Platforms
- **GitHub** → biggest community, Actions · **GitLab** → native CI/CD, self-host · **Bitbucket** → Jira/Confluence
- Git is identical underneath; PRs, CI/CD and issues are platform features

## Git Flow Branches
- `main` (production) · `develop` (integration) · `feature/*` · `release/*` · `hotfix/*` (from `main`, merge to both)
- `git switch -c name` = `git checkout -b name` · `git branch -d` (merged) / `-D` (force)

## Worktree
- Many branches checked out at once, one shared `.git`
- `git worktree add -b feature/x ../dir` · `list` · `remove` · `prune`

## Commits
- `git add` → staging · `git commit -m` → snapshot · `git diff` (unstaged) / `--staged`
- Present-tense summary, explain *why*

## Pull Requests
- Push → PR → CI → review → fix → merge · Draft = not ready
- Merge commit (all history) · Squash (one commit) · Rebase (linear)

## Merge Conflicts
- `<<<<<<< HEAD` mine · `=======` · `>>>>>>> branch` theirs
- Edit → delete markers → `git add` → `git commit`

## Code Review
- Correctness · Readability · Tests · Security · Scope
- Approve · Request changes (blocks) · Comment

## Repository Discipline
- `.gitignore` (+ `git rm --cached` if already tracked) · no secrets · short-lived branches
- Protected branches = PR + approval + CI required

## Releases
- Annotated tag `git tag -a v1.2.0 -m "..."` · `git push origin v1.2.0`
- SemVer: MAJOR breaking · MINOR feature · PATCH fix · `CHANGELOG.md`

## CI/CD Stages
- Checkout → Build → Lint → Unit → Integration → Security → Artifact (fail fast)

## Python Tests
- `pytest` + `assert` · `unittest.TestCase` + `assertEqual`
- Discovery: `test_*.py`, `test_` functions, `Test` classes

## Jenkins
- Controller (coordinates) + agents (execute)
- `Jenkinsfile` in repo, Groovy · Declarative vs Scripted · `agent any` · `sh '...'`
- Triggers: webhook · poll SCM · cron · manual

## Docker Hub
- `docker login` → `build -t user/app:1.0.0 .` → `push` → `pull` → `run`
- `latest` is only a convention · alternatives: GHCR, ECR, Artifact Registry

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What's the difference between Git and GitHub?
A: Git is the version control tool that tracks commits, branches and merges. GitHub is a hosting service built around Git that adds remote storage, pull requests, CI/CD and issue tracking. GitLab and Bitbucket do the same job.

Q: How would you choose between GitHub, GitLab and Bitbucket?
A: By the team's context. Bitbucket if the team already lives in Jira and Confluence, GitLab if they want CI/CD built in or need to self-host, and GitHub as the default with the largest community.

Q: Walk me through the Git Flow branches.
A: main holds production code, develop is where work gets integrated, feature branches come off develop and go back through a PR, release branches are cut from develop for final testing, and hotfix branches come off main for urgent fixes and merge into both main and develop.

Q: Why does a hotfix merge into both main and develop?
A: So the fix reaches production now and isn't lost the next time develop is released.

Q: What problem does git worktree solve?
A: It lets you check out another branch in a separate folder without touching your current one. If production breaks mid-feature, you open a worktree on main and fix it without stashing or committing your unfinished work.

Q: Is a branch a copy of the repository?
A: No. A branch is just a pointer to a commit. Worktrees make this visible: several folders with different branches all share one .git history, and a commit in one shows up in the others.

Q: What is the staging area for?
A: It's the step between editing and committing. You choose exactly which changes go into the next commit, so one commit can hold only part of what you've changed.

Q: What makes a good commit message?
A: A short present-tense summary like "Add user authentication", and, if it isn't obvious, a line explaining why. The diff already shows what changed.

Q: Why use a pull request instead of merging directly?
A: It's a mandatory checkpoint. CI runs automatically, and another person reviews the code before it reaches a shared branch, so bugs get caught before they affect the team.

Q: Compare merge commit, squash and merge, and rebase and merge.
A: A merge commit keeps every commit plus a merge commit. Squash combines the whole PR into one commit for a clean history. Rebase replays each commit on top of the target for a linear history with no merge commits.

Q: How do you resolve a merge conflict?
A: Open the file, decide what the final code should be, which can be one side, the other or a mix, delete the three marker lines, then git add and git commit.

Q: What does a reviewer look for?
A: Correctness and edge cases, readability, tests, security issues like hardcoded secrets, and whether the PR does one coherent thing.

Q: Why is deleting a secret in a later commit not enough?
A: Git keeps history, so the old commit with the secret can still be recovered. Secrets belong in environment variables, a secret manager or CI secrets, and a leaked one should be rotated.

Q: What does a protected branch do?
A: It blocks direct pushes, so changes only get in through a PR that has approval and passing CI. Without it, a PR is just a suggestion.

Q: Explain semantic versioning.
A: MAJOR.MINOR.PATCH. Major goes up for a breaking change, minor for a new backward-compatible feature, and patch for a bug fix.

Q: Why are annotated tags preferred for releases?
A: They record who tagged it, when, and a message, which is the documentation a release should have. Lightweight tags are just names.

Q: List the CI/CD stages in order and explain why that order.
A: Checkout, build, lint, unit test, integration test, security scan, artifact creation. Cheap fast checks run first so the pipeline fails fast instead of running slow tests on code with a lint error.

Q: What's the difference between a unit test and an integration test?
A: A unit test checks one function in isolation with no outside systems. An integration test checks several real pieces together, like code actually writing to a test database.

Q: pytest or unittest?
A: unittest is built into Python and class-based. pytest is a separate install with plain assert statements, and it's the more common choice today.

Q: What is a Jenkinsfile and why keep it in the repo?
A: It's the pipeline defined as code, written in Groovy. Keeping it in the repo means pipeline changes get versioned and reviewed through PRs like everything else.

Q: What's the difference between the Jenkins controller and an agent?
A: The controller schedules jobs and serves the UI. Agents are the machines that actually run the build and test steps, so work can run in parallel on dedicated hardware.

Q: Declarative or scripted Jenkinsfile?
A: Declarative is a fixed, readable structure that covers most pipelines and is recommended. Scripted is full Groovy for unusual, complex logic.

Q: How does a Jenkins pipeline get triggered?
A: Usually a webhook from GitHub on each push. Other options are polling the repo on a schedule, a cron schedule like a nightly run, or clicking Build Now.

Q: How do you publish an image to Docker Hub?
A: docker login, docker build with a tag like username/app:1.0.0, then docker push. Any other machine can then docker pull and docker run it.

Q: Does the latest tag always mean the newest image?
A: No. It's only a naming convention. It points at whatever was last pushed with that tag, which is why releases use version tags.
