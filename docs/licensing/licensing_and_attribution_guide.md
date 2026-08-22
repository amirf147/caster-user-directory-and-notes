# Comprehensive Licensing & Attribution Guide

## 1. Executive Summary

This repository contains two distinct categories of source code:
1. **Original Proprietary & Custom Utilities/Rules authored by Amir Farhadi**: Including high-value standalone subsystems like the Win32 Focus Engine (`util/app_switcher.py`), Multi-Monitor DPI Engine (`util/display_scaling.py`), AST Variable Tracking (`util/variable_tracker.py`), Out-of-Process MCP Server integrations, and custom application/AI grammar rules.
2. **Derivative Works based on Upstream Caster & Dragonfly Source Code**: Rules originally authored by the Caster open source project (`synkarius`, `LexiconCode`, `Casper`, and other contributors) that were imported into this user directory and modified or extended.

This guide provides an authoritative legal breakdown, repository multi-licensing strategy, a complete file-by-file audit of all 88 Python files, and concrete steps to ensure proper attribution and license compliance.

---

## 2. Legal Architecture: How Caster & Dragonfly Licensing Works

### 2.1 Upstream Licenses
- **Caster Core (`castervoice`)**: Licensed under **GNU Lesser General Public License v3.0 or later (LGPL-3.0-or-later)**.
- **Dragonfly (`dragonfly2`)**: Licensed under **LGPL-3.0-or-later**.

### 2.2 The LGPLv3 "Application" vs. "Library" Boundary
Under Section 0 and Section 4 of LGPLv3:
- **An "Application"** is any work that makes use of an interface provided by the Library, but is not otherwise based on it. Simply importing Dragonfly classes (`MappingRule`, `CompoundRule`) or Caster classes (`MergeRule`, `Key`, `Text`, `R`) in newly written files **does not** infect your original code with copyleft.
- **A "Combined Work"** allows you to license your original application code and custom tools under **any license of your choice** (e.g., **MIT**, **Apache 2.0**, or **BSD 3-Clause**), as long as users can replace/relink the underlying LGPL libraries.
- **A "Modified Library / Derivative Work"** occurs when you copy and modify existing Caster source files (e.g., `python.py`, `markdown.py`, `githubdesktop.py`, `winword.py`). These derivative files must remain under **LGPL-3.0-or-later**, retain upstream copyright notices, and state that modifications were made.

### 2.3 Guaranteeing Attribution for Your Original Code
To ensure that anyone copying your original utilities (`app_switcher.py`, Micro-MCP servers, etc.) **must credit you**, the **MIT License** or **Apache 2.0 License** is ideal:
- **MIT License**: Simple, universally adopted, and explicitly requires that the copyright notice and permission notice be included in all copies or substantial portions of the software.
- **Apache 2.0 License**: Includes explicit patent grants and strict trademark/attribution protection.

---

## 3. Repository Multi-Licensing Strategy

In modern open source development (and in Caster itself), hosting multiple licenses in a single repository is standard practice.

### Recommended Multi-License Structure
1. **Root `LICENSE` (Umbrella License)**: Defines the primary license (e.g., MIT) for all original work, and specifies LGPL-3.0-or-later for upstream Caster derivatives. (This follows Caster's own `LICENSE` model).
2. **SPDX Headers**: Every source file includes an unambiguous machine-readable SPDX identifier.
3. **`CREDITS.md` or `NOTICE`**: A central acknowledgments file giving prominent credit to the Caster project and individual contributors.
4. **`LICENSES/` Directory (Optional / REUSE Standard)**:
   - `LICENSES/MIT.txt`
   - `LICENSES/LGPL-3.0-or-later.txt`

---

## 4. File-by-File Classification & Attribution Audit

Below is the complete audit of all modules in `caster_user_content/` and `scripts/`.

### Category A: Direct Upstream Caster Derivatives
*Files copied directly or with minor modifications from Caster core. Must carry LGPL-3.0-or-later + Upstream Author Attribution + Modification Notice.*

| File Path | Upstream Origin in Caster | Current Attribution Status | License & Status |
| :--- | :--- | :--- | :--- |
| `rules/programming/Python/standard.py` | `castervoice/rules/ccr/standard.py` | ✅ Attributed (`synkarius`, Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/programming/Python/python_ccr.py` | `castervoice/rules/ccr/python_rules/python.py` | ✅ Attributed (`synkarius`, Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/programming/Python/python.py` | `castervoice/rules/ccr/python_rules/python2.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/global/markdown.py` | `castervoice/rules/ccr/markdown_rules/markdown.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/custom_githubdesktop.py` | `castervoice/rules/apps/git_clients/githubdesktop.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/msteams.py` | `castervoice/rules/apps/chat/MSTeamsRule.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/custom_gitbash.py` | `castervoice/rules/apps/terminal/gitbash.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/global/custom_mouse_alts_rules.py` | `castervoice/rules/core/utility_rules/mouse_alts_rules.py` | ✅ Attributed (`LexiconCode`, Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/explorer/file_dialog.py` | `castervoice/rules/apps/windows_os/file_dialogue.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/explorer/custom_explorer_ccr.py` | `castervoice/rules/apps/windows_os/explorer.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/explorer/file_explorer.py` | `castervoice/rules/apps/windows_os/explorer.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |

---

### Category B: Substantial Derivatives & Extended Upstream Rules
*Files originally derived from Caster rules but heavily rewritten, refactored, or expanded with custom command suites.*

| File Path | Upstream Reference in Caster | Current Attribution Status | License & Status |
| :--- | :--- | :--- | :--- |
| `rules/apps/vscode/vscode.py` | `castervoice/rules/apps/editor/vscode_rules/vscode2.py` & `vscode.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/vscode/vscode_ccr.py` | `castervoice/rules/apps/editor/vscode_rules/vscode.py` | ✅ Attributed (`Casper`, Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/office/excel/excel.py` | `castervoice/rules/apps/microsoft_office/excel.py` | ✅ Attributed (`Alex Boche`, Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/office/excel/excel_ccr.py` | `castervoice/rules/apps/microsoft_office/excel.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/office/word/ms_word.py` | `castervoice/rules/apps/windows_os/winword.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/office/word/ms_word_ccr.py` | `castervoice/rules/apps/windows_os/winword.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/office/custom_outlook.py` | `castervoice/rules/apps/microsoft_office/outlook.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/office/powerpoint.py` | `castervoice/rules/apps/microsoft_office/` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/notepadplusplus/notepadplusplus.py` | `castervoice/rules/apps/editor/notepadplusplus.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/firefox/firefox_extended_rule.py` | `castervoice/rules/apps/browser/firefox.py` / `chrome.py` | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |
| `rules/apps/firefox/firefox_extended_ccr_rule.py`| Upstream browser CCR patterns | ✅ Attributed (Caster Contributors + Amir Farhadi) | `LGPL-3.0-or-later` |

---

### Category C: Original High-Value Tools, Infrastructure & Architecture
*Original works authored by Amir Farhadi. Protected under Apache-2.0 to mandate attribution.*

| Module / Path | Description & Architecture | Copyright & License |
| :--- | :--- | :--- |
| `util/app_switcher.py` | 622-line Sub-millisecond Win32 Focus & Window Manager | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |
| `util/display_scaling.py` | 218-line DPI & Multi-Monitor Geometry Scaling Engine | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |
| `util/variable_tracker.py` | AST/Regex Persistent Config Tracker | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |
| `rules/global/text_editing.py` | 469-line Custom Text Selection & Manipulation Engine | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |
| `rules/caster_toggle_mic_key.py` | XML-RPC Hotkey Daemon & Bridge | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |
| `rules/global/test_desktop_pilot_mcp_standalone.py` | MCP Desktop Pilot Client / Server Suite | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |
| `rules/global/test_mcp_rule.py` & `test_mcp_standalone.py` | MCP Protocol Harness & Stasis Testing Suite | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |
| `rules/global/context_engine_launcher.py` & `scripts/context_poc.py` | ADCE Context Architecture & Daemon Engine | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |
| `scripts/check_absolute_paths.py` & `scripts/check_command_uniqueness.py` | Workspace QA & Linting Architecture | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |
| `docs/` (Architecture Blueprints & Research Tickets) | Complete Technical & Design Documentation Suite | `Copyright (c) 2024-2026 Amir Farhadi` — **CC BY 4.0 / Apache-2.0** |

---

### Category D: Original Custom Application & Website Grammar Rules
*Grammar rules written from scratch for applications and web platforms not present in upstream Caster.*

| Category | Modules | Copyright & License |
| :--- | :--- | :--- |
| **Next-Gen IDE Rules** | `rules/apps/vscode/antigravity.py`, `antigravity_ccr.py`, `cursor.py`, `cursor_ccr.py`, `windsurf.py`, `windsurf_ccr.py`, `ide/intellij.py` | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |
| **AI Assistant Rules** | `rules/apps/chat/claude/global_claude_desktop.py`, `copilot/copilot_desktop.py`, `copilot/global_copilot_desktop.py`, `rules/websites/chatgpt.py`, `copilot.py`, `gemini.py` | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |
| **CLI & Terminal Rules** | `rules/apps/cli/powershell/powershell.py`, `powershell_ccr.py`, `rules/apps/cli/cli.py`, `cli_ccr.py`, `cli_support.py`, `windows_terminal.py` | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |
| **Web & Productivity Rules**| `rules/websites/leetcode.py`, `outlier_playground.py`, `trello.py`, `youtube.py`, `rules/apps/figma/figma.py`, `figma_ccr.py`, `rules/global/task_management.py`, `taskbar.py`, `window_switching.py`, `window_switching_ccr.py` | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |
| **Media & Remote Tools** | `rules/apps/scrcpy/scrcpy.py`, `tightvnc/tightvnc.py`, `quick_picture_viewer.py`, `obs_studio.py`, `zoom.py`, `element.py`, `telegram.py`, `vlc.py`, `gnumeric.py`, `google_meet.py`, `clipchamp.py`, `sumatra.py`, `anki.py` | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |
| **LibreOffice Suites** | `rules/apps/libre_office/writer/writer.py`, `rules/apps/libre_office/writer/writer_ccr.py` | `Copyright (c) 2024-2026 Amir Farhadi` — **Apache-2.0** |

---

## 5. Header Templates & Implementation Examples

### Template 1: For Original Work & Utilities (Enforcing Attribution to You under Apache-2.0)
```python
"""
[Module Name / Description]

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""
```

### Template 2: For Upstream Caster Derivative Rules (LGPL-3.0-or-later)
```python
"""
[Rule Name / Description]

Derived from [Upstream Rule Path / Origin]
Copyright (c) 2015-2026 [Author / Caster Contributors]

[Customizations Description]:
Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: LGPL-3.0-or-later
"""
---

## 6. Root `LICENSE` File Content

```markdown
# Software Licenses & Attribution Notice

This repository contains both original work and derivative works based on upstream open source projects.

---

## 1. License for Original Code & Custom Utilities

All original code, custom tools, utilities, architectural documentation, and independent application/website grammar rules authored by **Amir Farhadi** are licensed under the **Apache License, Version 2.0**:

Copyright 2024-2026 Amir Farhadi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

## 2. License for Derivative Works from Upstream Caster & Dragonfly

Portions of the rules in `caster_user_content/rules/` are modified versions of rules originally distributed with **Caster** (https://github.com/dictation-toolbox/Caster), Copyright (c) 2015-2026 Caster contributors (including `synkarius`, `LexiconCode`, `Alex Boche`, `Casper`, and other contributors).

In accordance with the **GNU Lesser General Public License Version 3 (LGPLv3)**:
- These derivative files are licensed under the **GNU Lesser General Public License v3.0 or later (LGPL-3.0-or-later)**.
- Upstream copyright notices, individual author credits, and modification notices are preserved in the header of each derivative source file.
- Anyone modifying or distributing these specific derivative files must comply with the terms of LGPLv3 / GPLv3.
```

