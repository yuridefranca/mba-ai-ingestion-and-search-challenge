---
applyTo: '**'
---

# Git Instructions - Conventional Commits & GitFlow

This document defines commit message conventions and branching strategies for this project.

---

## Commit Message Format

Follow the **Angular Conventional Commits** specification for all commit messages.

### Structure

```
<type>(<scope>): <subject>

<body>

<footer>
```

-   **Header** (mandatory): `<type>(<scope>): <subject>`
    -   Must not exceed 100 characters
    -   Scope is optional but recommended
-   **Body** (optional): Detailed explanation of the change
-   **Footer** (optional): Breaking changes and issue references

### Type

Must be one of the following:

-   **feat**: A new feature
-   **fix**: A bug fix
-   **docs**: Documentation only changes
-   **style**: Code style changes (formatting, missing semicolons, etc.) that don't affect logic
-   **refactor**: Code changes that neither fix a bug nor add a feature
-   **perf**: Performance improvements
-   **test**: Adding or updating tests
-   **build**: Changes to build system or dependencies (pip, docker, requirements.txt)
-   **ci**: Changes to CI configuration files and scripts
-   **chore**: Other changes that don't modify src or test files

### Scope

The scope should identify the affected module or component:

-   **ingest**: Changes to `src/ingest.py` or PDF ingestion logic
-   **search**: Changes to `src/search.py` or search/retrieval logic
-   **chat**: Changes to `src/chat.py` or CLI interface
-   **utils**: Changes to `src/utils.py` (embedding model utilities)
-   **db**: Database schema, pgVector, or PostgreSQL configuration
-   **docker**: Docker compose or container configuration
-   **deps**: Dependency updates in `requirements.txt`

Use empty scope for cross-cutting changes (e.g., `style: format all files with 2 spaces`).

### Subject

-   Use **imperative, present tense**: "add" not "added" or "adds"
-   Don't capitalize first letter
-   No period (.) at the end
-   Be concise but descriptive

### Body

-   Use imperative, present tense
-   Include motivation for the change
-   Explain what changed and why (not how)

### Footer

-   Reference issues: `Closes #123` or `Fixes #456`
-   Breaking changes: Start with `BREAKING CHANGE:` followed by description

### Examples

```
feat(ingest): add support for multiple PDF ingestion

Implement batch processing to ingest multiple PDFs in a single run.
Each PDF is processed sequentially and stored with unique collection prefix.

Closes #42
```

```
fix(search): prevent empty context error when no results found

Add validation to check if similarity_search returns results before
building context string. Return helpful message when no relevant
documents are found.

Fixes #38
```

```
docs(readme): update setup instructions with venv activation

Clarify that users must activate virtual environment before running
scripts to avoid "module not found" errors.
```

```
refactor(utils): extract embedding model selection to factory function

Move model switching logic from ingest.py and search.py to utils.py
to ensure consistent embedding model usage across the pipeline.
```

```
chore(deps): upgrade langchain-postgres to 0.0.16

Update to fix compatibility issue with PostgreSQL 17 connection pooling.
```

---

## GitFlow Branching Strategy

This project follows the **GitFlow workflow** for managing branches and releases.

### Branch Structure

#### Permanent Branches

1. **`main`** - Production-ready code

    - Contains official release history
    - All commits should be tagged with version numbers
    - Only merge from `release/*` or `hotfix/*` branches

2. **`develop`** - Integration branch for features
    - Contains complete project history
    - Base branch for feature development
    - Always reflects latest delivered changes for next release

#### Temporary Branches

3. **`feature/*`** - New features and non-emergency fixes

    - Branch from: `develop`
    - Merge to: `develop`
    - Naming: `feature/<short-description>` (e.g., `feature/multi-pdf-support`)

4. **`release/*`** - Release preparation

    - Branch from: `develop`
    - Merge to: `develop` AND `main`
    - Naming: `release/<version>` (e.g., `release/1.0.0`)
    - Only bug fixes, documentation, and release tasks allowed

5. **`hotfix/*`** - Emergency production fixes
    - Branch from: `main`
    - Merge to: `develop` AND `main`
    - Naming: `hotfix/<short-description>` (e.g., `hotfix/connection-pool-leak`)

### Workflow Examples

#### Feature Development

```bash
# Start feature
git checkout develop
git checkout -b feature/openai-embeddings

# Work on feature (make commits)
git add .
git commit -m "feat(utils): add OpenAI embedding support"

# Finish feature
git checkout develop
git merge feature/openai-embeddings
git branch -d feature/openai-embeddings
git push origin develop
```

#### Release

```bash
# Start release
git checkout develop
git checkout -b release/1.0.0

# Bump version, update docs, fix bugs
git commit -m "chore(release): bump version to 1.0.0"

# Finish release
git checkout main
git merge release/1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main --tags

git checkout develop
git merge release/1.0.0
git branch -d release/1.0.0
```

#### Hotfix

```bash
# Start hotfix
git checkout main
git checkout -b hotfix/vector-dimension-error

# Fix the issue
git commit -m "fix(search): correct embedding dimension mismatch"

# Finish hotfix
git checkout main
git merge hotfix/vector-dimension-error
git tag -a v1.0.1 -m "Hotfix: vector dimension error"
git push origin main --tags

git checkout develop
git merge hotfix/vector-dimension-error
git branch -d hotfix/vector-dimension-error
```

### Initial Setup

```bash
# Create develop branch if it doesn't exist
git checkout -b develop main
git push -u origin develop
```

---

## Commit Guidelines Summary

✅ **Do:**

-   Write clear, descriptive commit messages
-   Use conventional commit format consistently
-   Keep commits focused on single logical changes
-   Reference issues in footer when applicable

❌ **Don't:**

-   Mix unrelated changes in one commit
-   Use vague messages like "fix bug" or "update code"
-   Commit broken or untested code to `develop` or `main`
-   Force push to `main` or `develop` branches

---

## Additional Notes

-   **Model changes require re-ingestion**: When switching embedding models (via `MODEL_TYPE`), always commit the model change separately and note in the commit body that database re-ingestion is required.
-   **Environment variables**: Never commit `.env` file. Changes to `.env.example` should use scope `chore(config)`.
-   **Dependencies**: When updating `requirements.txt`, always test installation in clean venv before committing.
