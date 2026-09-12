---
description: Create a spec file and feature branch for the next CircularCarbon AI step
argument-hint: "Step number and feature name e.g. 04 calculation-engine"
allowed-tools: Read, Write, Glob, Bash(git:*)
---

You are a senior developer spinning up a new feature for CircularCarbon AI. Always follow the rules in CLAUDE.md and `.claude/rules/`.

User input: $ARGUMENTS

## Step 1 — Check working directory is clean

Run `git status` and check for uncommitted, unstaged, or untracked files.

If any exist, stop immediately and tell the user to commit or stash changes.

DO NOT CONTINUE until the working directory is clean.

## Step 2 — Parse the arguments

From $ARGUMENTS extract:

1. `step_number` — zero-padded to 2 digits: 4 → 04, 11 → 11
2. `feature_title` — human readable title in Title Case
3. `feature_slug` — lowercase, kebab-case, git/file safe
4. `branch_name` — `feature/<step_number>-<feature_slug>`

If you cannot infer these, ask the user to clarify.

## Step 3 — Check branch name

Run `git branch`.

If `branch_name` already exists, append `-01`, `-02`, etc.

## Step 4 — Switch to main

Run:

`git checkout main`

If `origin` exists, pull the latest changes:

`git pull origin main`

## Step 5 — Create feature branch

Run:

`git checkout -b <branch_name>`

## Step 6 — Research the codebase

Before writing the spec:

- Read `CLAUDE.md`
- Read relevant `.claude/rules/`
- Inspect relevant existing implementation files
- Read all files in `.claude/specs/`
- Check that the requested step is not already marked complete

If already complete, warn the user and stop.

Do not modify implementation files.

## Step 7 — Write the spec

Generate a concise specification using this exact structure:

# Spec: <feature_title>

## Overview

One paragraph describing what this feature does and why it exists at this stage of the CircularCarbon AI roadmap.

## Depends on

Previous steps required for this feature.

## API Endpoints / Routes

Every new endpoint needed:

- `METHOD /path` — description — access/auth requirement

If none: `No new routes`.

## Database changes

New tables, columns, constraints, or migrations.

If none: `No database changes`.

## Component & UI changes

- **Create:** new components and paths
- **Modify:** existing components and required changes

If none: state that.

## Files to change

Every existing file that will be modified.

## Files to create

Every new file that will be created.

## New dependencies

Any new packages.

If none: `No new dependencies`.

## Rules for implementation

Always follow:

- Backend is the sole source of numerical truth
- Deterministic calculations only
- Gemini must never calculate or invent numerical emission values
- Gemini is used only for explanation/contextualization
- Strict input validation and type safety
- Follow `CLAUDE.md` and applicable `.claude/rules/`
- Do not modify unrelated functionality

## Definition of done

A specific, testable checklist verified through unit tests, API tests, or the application UI.

---

## Step 8 — Save the spec

Save to:

`.claude/specs/<step_number>-<feature_slug>.md`

## Step 9 — Report

Print only:

Branch:    <branch_name>
Spec file: .claude/specs/<step_number>-<feature_slug>.md
Title:     <feature_title>

Then say:

"Review the spec at `.claude/specs/<step_number>-<feature_slug>.md` then enter Plan Mode to begin implementation."

Do not print the full spec unless explicitly asked.