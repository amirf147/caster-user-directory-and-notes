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
   - **Title**: Concise, imperative (e.g., "Add 'Search Web' command to Chrome grammar").
   - **Summary**: 1-2 sentences on why this change was needed for your voice workflow.
   - **Bullet Points**: List the specific commands or logic added/removed.
   - **Conclusion**: State the benefit to your speed or accessibility.

# Execution
- Generate the message in a single markdown code block for easy copying.
- Do NOT run the `git commit` command. 