[ 🏠 Docs Home ](../README.md) › [ 📁 Features ](../README.md#features) › **Antigravity Editor Insights & System Prompt Ove...**

---

# Antigravity Editor Insights & System Prompt Overrides

This document summarizes the internal system prompt instructions, default behavioral guidelines, and conflict points between base system defaults and repository workspace rules (`AGENTS.md`). It also outlines strategies and protocol checks to ensure project rules are strictly enforced without regression.

---

## 1. Base System Prompt Default Guidelines

The Antigravity AI engine operates under default system instructions that dictate tool usage, formatting, and behavioral constraints. Key default guidelines include:

### File Links & Media Formatting
* **Default System Instruction**: The base system prompt instructs the AI to format clickable links to files and symbols using absolute URIs with the `file://` scheme: `[link text](file:///absolute/path/to/file)`.
* **The Conflict**: Workspace-specific rules in `.agents/AGENTS.md` explicitly override this, requiring **relative markdown links** (e.g., `./doc.md` or `../../util/script.py`) to prevent local file system metadata leaks (such as leaking user directory paths like `C:/Users/Username/...`).

### Tool Usage & Command Constraints
* **Dedicated Tool Priority**: The AI is instructed to always prioritize specialized tools (`view_file`, `grep_search`, `list_dir`, `replace_file_content`) over shell commands.
* **Prohibited Shell Utilities**: The AI is explicitly forbidden from running `cat` (for viewing/creating files), `grep` (for searching), `ls` (for listing), `sed` (for replacing), or `cd` in terminal commands.
*(Note: The constraint to use `py -3.10` for Python execution is **not** a base system rule; it is a custom rule injected by your `.agents/AGENTS.md` file, which successfully overrides the standard Windows Python execution behavior.)*

### Communication & Formatting Rules
* **LaTeX Math**: Inline math uses `\(...\)` or `$...$`; display math uses `\[...\]` or `$$...$$`. Literal dollar signs must be escaped as `\$` or enclosed in backticks to prevent triggering LaTeX mode.
* **No Re-Summarizing**: When updating or creating markdown artifacts, the AI is instructed not to re-summarize the full document in chat text, but rather point the user to the file.

---

## 2. Rule Hierarchy & Conflict Analysis

### Order of Precedence
1. **User Global & Workspace Rules** (`.agents/AGENTS.md` and `~/.gemini/config/AGENTS.md`): **Highest Priority**. These rules explicitly state that they override all other instructions.
2. **System Prompt Guidelines**: Standard baseline behaviors and tool definitions.
3. **General Model Defaults**: Default LLM behavior.

### Why Workspace Rule Overlooks Happen
Despite the explicit hierarchy, LLMs can experience "instruction bleed" or "default bias" when a baseline prompt guideline (e.g., "Use `file:///` URLs for links") is heavily reinforced in system context. If the model generates link text without explicitly running a verification check against `AGENTS.md`, it defaults to the system prompt pattern.

---

## 3. Ideas for Improving Compliance

Because LLMs can never be guaranteed to flawlessly follow rules 100% of the time, the following are some potential strategies and protocol ideas that could help reduce or prevent regressions (such as absolute `file:///` path leaks):

### Strategy A: Pre-Commit Link Audit Checklist
Before finalizing any markdown file edit, the AI must run a mental or scripted audit against link syntax:
1. Scan for `file:///` or absolute drive letters (`C:\`, `C:/`).
2. Convert any found absolute paths to relative paths relative to the current file location.

### Strategy B: Explicit Negative Constraints in `AGENTS.md`
LLMs respond more reliably to explicit negative constraints ("NEVER do X") paired with the rationale.
* **Recommended `AGENTS.md` Addition**:
  ```markdown
  ## Mandatory Link Formatting
  - NEVER output absolute file URIs (`file:///...` or `C:/...`) in markdown links or documentation.
  - ALWAYS calculate and output relative paths (e.g., `./other_doc.md` or `../../util/script.py`).
  ```

### Strategy C: Task Verification Protocol
When completing markdown documentation updates:
1. Perform file replacement/creation.
2. Run a `grep_search` query for `file:///` across `docs/` to catch any accidental absolute link insertions before concluding the task.


