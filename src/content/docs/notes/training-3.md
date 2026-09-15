---
title: Training 3 - Git Workflow
description: Branching, commits, pull requests, merge conflicts, code review, repository discipline, and release basics
---

Teacher: Evan Flint

Syllabus Day 4: Git Workflow
Coverage: Branching, commits, PRs, merge conflicts, code review, repository discipline and release basics.

## Video Resources

## References

# Git Background

Q. What are the major Git hosting platforms?

A. (Shared by the teacher) GitHub, GitLab, and Bitbucket - the three most widely used platforms for hosting Git repositories remotely and collaborating on them.

| | GitHub | GitLab | Bitbucket |
|---|---|---|---|
| Owned by | Microsoft | GitLab Inc. (self-hosted or SaaS) | Atlassian |
| Best known for | Largest developer community, open source hub | Built-in CI/CD (GitLab CI), strong self-hosting/DevOps focus | Deep integration with Jira and other Atlassian tools |
| CI/CD | GitHub Actions | GitLab CI/CD (native, tightly integrated) | Bitbucket Pipelines |
| Free private repos | Yes | Yes | Yes (small teams) |
| Common use case | Open source projects, most popular choice overall | Enterprises wanting an all-in-one DevOps platform | Teams already using Jira/Confluence |

**GitHub**
- Pros: by far the largest community and ecosystem - most open source projects, tutorials, and third-party integrations assume GitHub. GitHub Actions has a huge marketplace of pre-built automation steps. Most likely platform a future employer already uses.
- Cons: CI/CD (Actions) was added later and is somewhat less deeply integrated than GitLab's native pipelines. Advanced enterprise/self-hosting features are less mature than GitLab's.
- Differentiator: default choice for open source and general industry-wide familiarity.

**GitLab**
- Pros: CI/CD is built into the core product from the ground up (not bolted on) - widely considered the most complete "all-in-one DevOps platform" (repo + CI/CD + issue tracking + container registry in one place). Strong self-hosted option (can run entirely on a company's own servers) for organizations with strict data/compliance requirements.
- Cons: smaller open source community than GitHub - fewer public projects, tutorials, and casual contributors. Self-hosted setup/maintenance adds operational overhead if not using their SaaS version.
- Differentiator: best choice when an organization wants one unified platform end-to-end, or needs to self-host for compliance reasons.

**Bitbucket**
- Pros: seamless integration with other Atlassian tools (Jira for issue tracking, Confluence for documentation) - a natural fit for teams already inside that ecosystem. Good free tier for small teams.
- Cons: smallest developer community/mindshare of the three - fewer public repos, less common in tutorials and open source. Bitbucket Pipelines (its CI/CD) is less feature-rich than GitHub Actions or GitLab CI.
- Differentiator: makes the most sense specifically for teams already committed to Jira/Confluence, less compelling as a standalone choice otherwise.

**Bottom line:** Git itself (branching, commits, merging - the actual version control mechanics covered in the rest of this training) is identical no matter which of these hosts it - GitHub/GitLab/Bitbucket are hosting services built *around* Git, adding remote storage, pull/merge request workflows, CI/CD pipelines, issue tracking, and access control on top of the core tool. The real decision between them comes down to team/organizational context: existing tool ecosystem (Atlassian shop -> Bitbucket), CI/CD philosophy (want it built-in and native -> GitLab), or default/most-common choice with the largest community (GitHub). This project's own site (`training-notes-site`) is hosted on GitHub via GitHub Pages.

# Branching

Q. What is Git Flow, and what are the standard branch types?

A. (Foundation review - already covered in more depth in `Training 0.md`'s "Git Flow / Branching Strategy" entry) Git Flow is a branching strategy for teams working on the same codebase without stepping on each other's work. The four core branch types:

| Branch | Purpose |
|---|---|
| `main` | The stable, deployable/production-accurate version of the project |
| `develop` | The integration branch every feature branches off of and merges back into |
| `feature/*` | Created from `develop` for one specific piece of work; merged back into `develop` via a pull request once approved |
| `release/*` | Cut from `develop` when preparing a new release - allows final testing/bug fixes without blocking new feature work on `develop` |

A `hotfix/*` branch is a common fifth type not always covered as core Git Flow: branched directly from `main` to patch an urgent production bug, then merged into both `main` and `develop` so the fix isn't lost on the next regular release.

Core branching commands:

```bash
git branch                     # list local branches
git branch feature/my-work     # create a new branch (doesn't switch to it)
git checkout feature/my-work   # switch to an existing branch
git checkout -b feature/my-work   # create AND switch in one step (older syntax)
git switch -c feature/my-work     # create AND switch in one step (newer, clearer syntax)
git switch develop                # switch to an existing branch (newer syntax)
git merge feature/my-work         # merge that branch into the current branch
git branch -d feature/my-work     # delete a branch (only if already merged)
git branch -D feature/my-work     # force-delete a branch (even if unmerged - use with caution)
```

`checkout` is the older, multi-purpose command (also used for restoring files); `switch` and `restore` were introduced later specifically to split those two responsibilities apart and reduce confusion - both are seen in real codebases, so it's worth recognizing both.

Q. What is `git worktree`, and why use it instead of just switching branches?

A. (Shared by the teacher) `git worktree` lets you have multiple branches from the same Git repository checked out into **different directories at the same time**.

Normally, one repository directory can only have one branch checked out:
```text
project/
└── currently on: main
```
Switching to another branch (`git switch feature/login`) changes the files in that same directory - only one branch's files exist on disk at once.

With worktrees, you can instead have:
```text
projects/
├── myapp/             -> main
├── myapp-feature/      -> feature/login
└── myapp-hotfix/       -> hotfix/security
```
All three share the same underlying Git repository/history, but each has its own working directory, checked-out branch, and staging area.

**Basic commands** (assuming you're currently in `myapp` on `main`):

Create a new worktree AND a new branch in one step:
```bash
git worktree add -b feature/login ../myapp-feature
```
Breaking that down: `-b feature/login` creates the branch, `../myapp-feature` is where its files get checked out. `cd ../myapp-feature` afterward drops you into a folder already on `feature/login` - no separate `git switch` needed.

If the branch already exists, drop the `-b` flag:
```bash
git worktree add ../myapp-feature feature/login
```

See all worktrees for this repo:
```bash
git worktree list
```
```text
/home/evan/myapp          a1b2c3d [main]
/home/evan/myapp-feature  d4e5f6a [feature/login]
```

Remove one, and clean up references to any manually-deleted worktree folders:
```bash
git worktree remove ../myapp-feature
git worktree prune
```

**Why it's useful:** imagine you're halfway through substantial work on `feature/new-pipeline`, with unfinished, uncommitted changes - and someone says "production is broken, fix `main` immediately." Without worktrees, you'd have to commit or stash your unfinished work just to switch branches. With worktrees:
```bash
git worktree add -b hotfix/production ../production-fix main
cd ../production-fix
```
Now `myapp/` still has `feature/new-pipeline` with all its unfinished changes completely undisturbed, while `production-fix/` is a clean, separate checkout of `main` ready for the urgent fix - both exist on disk simultaneously.

**The core insight worktrees make visible:** a branch is not a separate copy of the repository. Multiple worktrees have separate checked-out files on disk, but they all share the exact same Git object database and commit history underneath - proven by the fact that a commit made in one worktree is immediately visible to `git log` in the others, since there's only ever one actual repository.

| | Regular branch switching | Worktrees | A second clone |
|---|---|---|---|
| Working directories | One at a time | Multiple, simultaneously | Multiple, simultaneously |
| Shares commit history/objects | N/A (same folder) | Yes - one shared `.git` | No - fully separate copy |
| Disk usage | Minimal | Small (shares objects) | Full duplicate |
| Common use case | Everyday single-branch work | Quick parallel work without disturbing in-progress changes | Rare - usually worktrees are preferred now |

# Commits

Q. What are the core Git commands for tracking and saving changes?

A. Foundation review of the everyday Git command set:

```bash
git init                  # turn the current folder into a new Git repository
git status                # show what's changed, staged, or untracked
git add <file>             # stage a specific file's changes
git add .                  # stage everything changed in the current directory
git commit -m "message"    # save the staged changes as a new commit, with a message
git log                    # view commit history
git log --oneline          # condensed one-line-per-commit view
git diff                   # show unstaged changes compared to the last commit
git diff --staged          # show staged changes compared to the last commit
```

Key concept - the staging area: `git add` doesn't commit anything yet - it moves changes into a middle "staging" step. This lets you build a commit out of only *some* of your changed files/lines, rather than being forced to commit everything you've touched at once. `git commit` then saves whatever is currently staged as a permanent snapshot in the project's history.

Commit message convention: a short, present-tense summary line (e.g. "Add user authentication" not "Added" or "Adding"), optionally followed by a blank line and a longer explanation of *why* the change was made if it's not obvious from the diff itself - this mirrors the "explain the why, not the what" principle, since the diff already shows what changed.

# Pull Requests

Q. What is a pull request (PR), and why use one instead of merging directly?

A. (Foundation review) A pull request is a request to merge one branch's changes into another (typically a `feature/*` branch into `develop`, or `develop` into `main`), opened on a hosting platform (GitHub/GitLab/Bitbucket - see Git Background above) rather than done as a plain local `git merge`. A PR isn't a Git concept itself - Git has no idea what a "pull request" is - it's a workflow feature the hosting platforms layer on top of Git.

**Typical PR workflow:**
```text
1. Create a branch, commit work, push it to the remote
   git push -u origin feature/my-work

2. Open a PR on the hosting platform (feature/my-work -> develop)

3. Automated checks run (CI: linting, tests, build) - see Training 0's CI/CD notes

4. Reviewers read the diff, leave comments, request changes or approve

5. Author pushes more commits addressing feedback (the same PR updates automatically)

6. Once approved + CI passes, the PR is merged
```

**Why PRs exist instead of merging directly:** they create a mandatory checkpoint before code reaches a shared branch - a place for automated checks to run and for a second set of human eyes to catch bugs, design issues, or missed edge cases before they affect the rest of the team. This is the same underlying idea as the "protected branch" concept covered in Repository Discipline below.

**Good PR description practices:**
- A clear title describing *what* changed, not just "fix bug" or "updates"
- A short description of *why* the change was made (the motivation/problem), since the diff already shows *what* changed
- Screenshots or example output for anything visual or hard to verify by reading code alone
- Linking to a related issue/ticket if one exists

**Draft PRs:** most platforms support opening a PR as a "draft" - visible to teammates and eligible for early feedback, but explicitly marked as not ready to merge yet. Useful for work-in-progress that benefits from early visibility or a sanity check before it's finished.

**Merge strategies - what actually happens to the commit history when a PR merges:**

| Strategy | What it does | When it's used |
|---|---|---|
| Merge commit | Keeps all of the branch's individual commits, plus adds one new "merge commit" tying them together | Preserves full history/context of how the work evolved |
| Squash and merge | Combines every commit on the branch into a single new commit on the target branch | Keeps the target branch's history clean - one commit per feature/PR, hides messy "wip" or "fix typo" commits |
| Rebase and merge | Replays the branch's individual commits on top of the target branch, with no separate merge commit at all | Keeps a fully linear history (no merge commits anywhere), while still preserving each individual commit |

There's no universally "correct" choice - teams pick one convention and stick with it consistently across the whole repository.

# Merge Conflicts

Q. What do Git's merge conflict markers mean, and how do you resolve one?

A. (Shared by the teacher) When Git can't automatically combine two branches' changes to the same lines of a file, it inserts conflict markers directly into the file and pauses the merge for a human to resolve.

```text
<<<<<<< HEAD
your current branch's version
=======
the other branch's version
>>>>>>> feature-branch
```

| Marker | Meaning |
|---|---|
| `<<<<<<< HEAD` | Start of the version from the branch you're currently on |
| `=======` | Separator between the two conflicting versions |
| `>>>>>>> feature-branch` | End of the incoming branch's version (labeled with that branch's name) |

**To resolve:** edit the file to contain whatever you actually want the final result to be, delete all three marker lines entirely, then stage and commit as normal:

```bash
git add <file>
git commit
```

**Worked example:**
```text
<<<<<<< HEAD
VERSION = "1.1.0"
=======
VERSION = "2.0.0"
>>>>>>> feature/version-update
```
Resolved (choosing the incoming branch's version here):
```python
VERSION = "2.0.0"
```
The resolution doesn't have to be strictly "pick one side" - it's also valid to write something that combines or replaces both sides entirely, as long as every marker line is removed and the file is left in a valid, working state before committing.

# Code Review

Q. What do reviewers actually look for in a code review, and how should feedback be given/received?

A. (Foundation review) Code review is the practice of having at least one other person read a PR's changes before they merge. It's a quality gate that catches problems a single author, deep in their own work, is prone to miss.

**What reviewers typically check for:**

| Category | Example questions a reviewer asks |
|---|---|
| Correctness | Does this actually do what it's supposed to? Are there edge cases (empty input, zero, negative numbers, missing data) that aren't handled? |
| Readability | Could someone unfamiliar with this change understand it? Are names clear? Is anything needlessly complicated? |
| Test coverage | Are there tests for the new behavior, especially edge cases? Do existing tests still pass? |
| Security | Are secrets/credentials hardcoded? Is user input trusted without validation? Any injection risks? |
| Scope | Does this PR do one coherent thing, or is it mixing unrelated changes together, making it harder to review and to revert later if needed? |

**Review states**, common across GitHub/GitLab/Bitbucket:

| State | Meaning |
|---|---|
| Approve | The reviewer is satisfied - this can be merged as-is |
| Request changes | The reviewer found something that must be fixed before merging (usually blocks the merge until resolved) |
| Comment | Feedback or questions that don't block merging - suggestions, curiosity, non-critical nitpicks |

**Giving good review comments:** be specific (point to the exact line and explain the concern, don't just say "this is wrong"), explain *why* something is a problem rather than just asserting a preference, and distinguish "this must change" from "this is just a suggestion" so the author isn't left guessing what's actually blocking. Framing feedback around the code itself ("this function could raise a ZeroDivisionError here") rather than the person ("you forgot to handle...") keeps it collaborative rather than personal.

**Receiving review feedback:** it's about the code, not a judgment of the author - the goal on both sides is a better final result, not defending the original approach. Responding to every comment (even just "done" or "good point, fixed in the latest commit") helps the reviewer know what's been addressed without re-reading the whole diff from scratch.

**Why code review matters as a practice:** beyond catching bugs, it spreads knowledge of the codebase across the team (so no single person is the only one who understands a given piece of code), and it keeps a consistent style/quality bar across contributions from different people over time.

# Repository Discipline

Q. What are the everyday habits that keep a shared Git repository healthy?

A. (Foundation review) A handful of practices, mostly about reducing the chance of mistakes reaching the rest of the team:

**`.gitignore`:** a file listing patterns Git should never track, so things like build output, dependency folders, and local environment files don't get committed by accident.
```text
# Common .gitignore patterns
node_modules/
__pycache__/
*.pyc
.env
.venv/
dist/
.DS_Store
```
Once a file is already tracked, adding it to `.gitignore` alone doesn't untrack it - it has to be removed from tracking explicitly (`git rm --cached <file>`) first.

**Never commit secrets:** API keys, passwords, tokens, and `.env` files should never be committed - even a since-deleted commit still exists in the repository's history and can be recovered by anyone with access to it. Environment variables, secret managers, or CI/CD platform secrets (see Training 0's CI/CD notes) are the correct place for that kind of data instead.

**Meaningful commit messages:** ties directly back to the Commits section above - a commit history made of clear, descriptive messages is what makes `git log` and `git blame` actually useful later, when someone (possibly future-you) needs to understand why a specific line exists.

**Keep branches short-lived:** a `feature/*` branch that stays open for weeks drifts further and further from `develop`/`main`, making its eventual merge more likely to hit conflicts. Small, frequent PRs are easier to review and merge than one enormous branch built over a long stretch of time.

**Protected branches:** a setting on the hosting platform that prevents direct pushes to important branches (typically `main`, sometimes `develop`) - changes can only get in through a PR, usually requiring at least one approval and passing CI checks first. This is what actually enforces the "PRs are a mandatory checkpoint" idea from the Pull Requests section - without branch protection, a PR is only a suggestion, since anyone could still push straight to `main` and skip it entirely.

**Branch naming conventions:** a consistent prefix makes a branch's purpose obvious at a glance, and lets some CI/CD pipelines trigger different behavior based on the prefix:

| Prefix | Purpose |
|---|---|
| `feature/*` | New functionality |
| `bugfix/*` | Fixing a non-urgent bug |
| `hotfix/*` | Urgent production fix (see Branching section above) |
| `chore/*` | Maintenance work with no functional change (dependency bumps, config, cleanup) |
| `docs/*` | Documentation-only changes |

# Release Basics

Q. How does a team actually cut and track a new release?

A. (Foundation review) Once code on `develop` (or a `release/*` branch - see Branching above) is considered ready to ship, it typically gets merged into `main` and marked with a **tag** - a permanent, named pointer to that exact commit.

**Git tags:**
```bash
git tag v1.2.0                                  # lightweight tag - just a name pointing at a commit
git tag -a v1.2.0 -m "Release 1.2.0"            # annotated tag - includes a message, author, and date
git push origin v1.2.0                           # tags aren't pushed automatically - must be pushed explicitly
git tag                                          # list all tags
```
Annotated tags are generally preferred for actual releases, since they carry metadata (who tagged it, when, and why) the way a real release should be documented - lightweight tags are more often used for quick, temporary bookmarks.

**Semantic versioning (SemVer):** the near-universal convention for version numbers, in the form `MAJOR.MINOR.PATCH` (e.g. `2.1.4`):

| Segment | Increases when... | Example |
|---|---|---|
| MAJOR | A breaking change is introduced (existing usage may stop working) | `1.x.x` -> `2.0.0` |
| MINOR | New functionality is added, but everything existing still works (backward-compatible) | `2.1.x` -> `2.2.0` |
| PATCH | A bug fix with no new functionality and no breaking changes | `2.1.4` -> `2.1.5` |

**CHANGELOG basics:** a `CHANGELOG.md` file in the repository root listing what changed in each version, newest first, usually grouped under headings like "Added," "Changed," and "Fixed." It gives anyone upgrading (or a future teammate) a human-readable summary of what happened release to release, without having to read raw commit history or diff two tags against each other.

**How this connects to the rest of the pipeline:** a `release/*` branch (from Branching) is where final testing and bug-fixing for an upcoming version happens; once it's ready, it merges into `main`, gets tagged with its SemVer number, and - per the CI/CD three-environments concept from `Training 0.md` - that tagged commit is what actually gets deployed through Testing/QA and out to Production, with the tag serving as the permanent record of exactly which snapshot of the code is live.
