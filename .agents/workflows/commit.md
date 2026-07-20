---
description: Generates a copy-paste ready commit message for Caster User Directory repository updates.
---

# Instructions
1. **Analyze Staged Changes**: Run `git --no-pager diff --cached` to see exactly what is being committed.
2. **Focus**: Look specifically for new voice command definitions, grammar updates, or macro logic.
3. **Exclusions**: 
   - No diff metadata, line numbers, or syntax discussion.
   - No commit IDs.
4. **Formatting**:
   - Format the message as a standard git commit message: a concise, imperative title line, an empty line, a 1-2 sentence paragraph explaining why the change was needed, and a bulleted list of specific changes.
   - **Do NOT** explicitly label the sections (e.g., do not write "Summary:", "Bullet Points:", "Conclusion:", or any section headers). Simply separate the title, paragraph, and bullet list with empty lines.

# Execution
- Generate the message in a single code block without markdown formatting for easy copying.
- Do NOT run the `git commit` command.