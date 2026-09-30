---
name: rule-generation
description: Guidelines, constraints, and validation protocols for authoring, modifying, or refactoring Caster voice rules, CCR rules, and RuleDetails specifications.
---

# Caster Rule Generation & Authoring Guide

This skill governs the creation, modification, and architectural verification of Caster voice rules in `caster_user_content/rules/`.

## 1. Continuous Command Recognition (CCR) Rules

CCR rules inherit from `MergeRule` (or `SelfModifyingRule`) and merge dynamically with other active CCR grammars.

### Critical RuleDetails Constraints
- **Forbidden `name` and `grammar_name`**: `RuleDetails` for any CCR rule (`ccrtype` is not `None`) must **never** set `name` or `grammar_name`.
  - Caster's internal validator (`CCRDetailsValidator`) explicitly rejects any CCR rule that specifies `name` or `grammar_name`:
    ```python
    # Correct App CCR:
    details = RuleDetails(
        executable=["powershell", "pwsh", "windowsterminal", "wt"],
        function_context=is_powershell_active,
        ccrtype=CCRType.APP,
    )

    # INCORRECT (causes silent registration rejection):
    details = RuleDetails(
        name="PowerShell CCR",  # REJECTED BY CASTER CORE
        executable=[...],
        ccrtype=CCRType.APP,
    )
    ```
- **Rejection Behavior**: When validation fails, `GrammarManager.register_rule()` logs a rejection message to printer output and aborts registration. The rule is never added to `_managed_rules`, never appears in Dragonfly's grammar containers, and fails to respond to voice commands.

### CCR Type Constraints
- `CCRType.APP`:
  - Must define `executable` (string or list of strings).
  - May optionally define `function_context` (predicate receiving `executable`, `title`, `handle`).
  - Merged context becomes `AppContext(executable, title) & FuncContext(function_context)`.
- `CCRType.GLOBAL`:
  - Applies universally across the desktop.
  - Must not define `function_context` (`RuleFamilyValidator` rejects global rules with function context).
- `CCRType.SELFMOD`:
  - Reserved for self-modifying rules.
  - Must not define `function_context`.

---

## 2. Non-CCR (Mapping) Rules

Non-CCR rules inherit from `MappingRule` and operate as discrete Dragonfly grammars.

- **Mandatory `name`**: Non-CCR rules require a descriptive `name` string in `RuleDetails`.
- **Forbidden `ccrtype`**: Non-CCR rules must not define `ccrtype` (`RuleFamilyValidator` rejects mapping rules with a declared `ccrtype`).
- Example:
  ```python
  details = RuleDetails(
      name="Windows Terminal Rule",
      executable="windowsterminal",
      function_context=None,
  )
  ```

---

## 3. Plugin Imports and Singleton Preservation

- When a rule or utility context predicate references a Caster plugin (such as the ADCE client in `caster_user_content/plugins/adce/`), prefer top-level imports first:
  ```python
  try:
      from adce import adce
  except ImportError:
      from caster_user_content.plugins.adce import adce
  ```
- **Rationale**: Caster adds `caster_user_content/plugins/` to `sys.path` during initialization. Importing directly from `caster_user_content.plugins.<name>` can create duplicate singleton instances with divergent in-memory state.

---

## 4. Verification Protocol for Rule Changes

Always verify grammar registration before concluding rule changes:

1. **Pre-Flight Details Validation**:
   Validate that `GrammarManager._get_invalidation(rule_cls, details)` returns `None` for modified rules:
   ```pwsh
   py -3.10 -c "..." # Or via a temporary script in scratch/
   ```
2. **Repository Path Audit**:
   Ensure no absolute local paths or leaked metadata exist in source files or docstrings:
   ```pwsh
   py -3.10 scripts/check_absolute_paths.py
   ```
3. **Command Uniqueness Audit**:
   Verify that newly added voice command specs do not inadvertently collide:
   ```pwsh
   py -3.10 scripts/check_command_uniqueness.py
   ```

---

## 5. Reserved Scaffolding for Future Considerations

The following sections serve as reserved placeholders for future additions:

### Transformers Integration
<!-- Reserved for rules consuming or registering text transformers and word replacements -->

### Companion Rules
<!-- Reserved for companion rule pairs and activation sync protocols -->

### Self-Modifying Rules
<!-- Reserved for dynamic self-modifying vocabularies and rule state persistence -->

### Asynchronous IPC & Hotkey Triggers
<!-- Reserved for rules bridging external events, HTTP endpoints, or named pipes -->
