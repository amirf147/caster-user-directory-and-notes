---
description: Automated pre-flight validation and conventional commit message generation workflow for the Caster User Directory repository.
---

# Commit Workflow

Follow this deterministic 5-step sequence whenever executing `/commit`:

## Step 1: Pre-Flight Safety & Path Validation
Run the automated repository validation checks:
1. Execute the repository path and link audit:
   ```pwsh
   py -3.10 scripts/check_absolute_paths.py
   ```
2. If any Python rule files under `caster_user_content/rules/` were created or modified, execute the voice command uniqueness audit:
   ```pwsh
   py -3.10 scripts/check_command_uniqueness.py
   ```
3. **Gate**: If any check fails or reports absolute path leaks (`file:///`, `C:/Users/`, etc.), STOP immediately. Fix the violations and re-run until all checks pass with exit code 0.

## Step 2: Stage Verified Changes
Stage only the verified repository files:
```pwsh
git add <modified_files>
```
*Note*: Never stage untracked personal settings (`settings/`, `data/`, or `environment_variables.py`).

## Step 3: Inspect Staged Diff
Inspect the staged changes to verify completeness:
```pwsh
git status
git diff --cached --stat
```

## Step 4: Format Conventional Commit Message
Construct a conventional commit message following this format:
- **Title Line**: `type(scope): imperative title`
  - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `perf`.
  - Multi-file changes: Use the highest-impact type (e.g., `feat` overrides `docs`).
  - Formatting: All lowercase imperative mood without trailing period.
- **Body Paragraph**: 1 to 2 sentences explaining why the change was needed and the architectural context.
- **Bulleted Changes**: An itemized list of concrete changes.
- **Exclusions**: No diff metadata, line numbers, or section labels (e.g., "Summary:").

## Step 5: Output Copy-Paste Ready Message
- **NEVER execute `git commit` or `git push` autonomously.**
- Output the final formatted message in a single markdown code block so it can be pasted directly into the IDE Source Control commit box.