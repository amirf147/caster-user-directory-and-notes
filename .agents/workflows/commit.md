---
description: Automated pre-flight validation and conventional commit message generation workflow for the Caster User Directory repository.
---

# Commit Workflow

Follow this deterministic 5-step sequence whenever executing `/commit`:

## Step 1: Pre-Flight Safety & Hook Delegation
Safety, syntax, and path validation are fully delegated to the repository's Git pre-commit hooks (`.pre-commit-config.yaml`), which execute automatically upon commit:
- `Check Hardcoded Absolute Paths` (`scripts/check_absolute_paths.py`)
- `Check Voice Command Uniqueness` (`scripts/check_command_uniqueness.py`)
- `ruff` & `ruff-format`

To avoid context token bloat and redundant execution cycles, **do not execute these scripts in the chat**. If a pre-commit hook aborts a commit, the terminal or IDE output will surface the exact violation to resolve.

## Step 2: Inspect Staged Diff
Inspect the staged changes to verify completeness:
```pwsh
git status
git diff --cached --stat
```

## Step 3: Format Conventional Commit Message
Construct a conventional commit message following this format:
- **Title Line**: `type(scope): imperative title`
  - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `perf`.
  - Multi-file changes: Use the highest-impact type (e.g., `feat` overrides `docs`).
  - Formatting: All lowercase imperative mood without trailing period.
- **Body Paragraph**: 1 to 2 sentences explaining why the change was needed and the architectural context.
- **Bulleted Changes**: An itemized list of concrete changes.
- **Exclusions**: No diff metadata, line numbers, or section labels (e.g., "Summary:").

## Step 4: Output Copy-Paste Ready Message
- **NEVER execute `git commit` or `git push` autonomously.**
- Output the final formatted message in a single markdown code block so it can be pasted directly into the IDE Source Control commit box.