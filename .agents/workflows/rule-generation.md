---
description: Workflow and validation protocol for authoring and verifying Caster voice rules and RuleDetails specifications.
---

# Rule Generation & Authoring Workflow

Use this workflow when creating, refactoring, or modifying Caster voice rules in `caster_user_content/rules/`.

## 1. Class Selection & Architecture
- **Continuous Command Recognition**: If the rule needs to chain or combine with other commands, inherit from `MergeRule` and declare `ccrtype` (`CCRType.APP`, `CCRType.GLOBAL`, or `CCRType.SELFMOD`).
- **Discrete / Standalone**: If the rule executes discrete commands without chaining, inherit from `MappingRule` and leave `ccrtype=None`.

## 2. RuleDetails Specification Check
- **For CCR Rules**:
  - Do **not** pass `name` or `grammar_name`. Caster core rejects CCR rules that specify `name`.
  - For `CCRType.APP`, supply `executable` (e.g., list of target process names) and optional `function_context`.
  - For `CCRType.GLOBAL` or `CCRType.SELFMOD`, do **not** supply `function_context`.
- **For Non-CCR Rules**:
  - Supply a descriptive `name` string.
  - Do not pass `ccrtype`.

For detailed constraints and nuances, refer to skill `rule-generation` in [`.agents/skills/rule-generation/SKILL.md`](../skills/rule-generation/SKILL.md).

## 3. Pre-Flight Validation
1. Verify rule detail validation:
   - Ensure `GrammarManager._get_invalidation(rule_class, details)` returns `None`.
2. Check for absolute path leaks:
   ```pwsh
   py -3.10 scripts/check_absolute_paths.py
   ```
3. Check for voice command spec collisions:
   ```pwsh
   py -3.10 scripts/check_command_uniqueness.py
   ```
