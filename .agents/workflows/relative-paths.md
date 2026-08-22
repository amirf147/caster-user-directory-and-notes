---
description: Audits repository files and documentation for absolute paths or system metadata leaks, converting them to clean relative paths.
---

# Instructions

1. **Scan Tracked Files**:
   - Search across `docs/`, `scripts/`, and `caster_user_content/` for absolute path patterns:
     - `file:///`
     - Drive letters: `C:/`, `C:\`, `c:/`, `c:\`
     - User directory markers: `/Users/`, `\Users\`, `AppData`
2. **Convert to Relative Links**:
   - In Markdown documentation, replace any absolute file URIs (`file:///...`) with standard relative links (e.g., `[Doc Name](./sibling_doc.md)` or `[Script](../scripts/context_poc.py)`).
   - In Python code, ensure all repository paths are constructed relative to `__file__` or reference untracked `caster_user_content/environment_variables.py`.
3. **Run Validation**:
   - Execute the path validation script:
     ```pwsh
     py -3.10 scripts/check_absolute_paths.py
     ```
4. **Report**:
   - List any files that were sanitized and confirm clean validation status.
