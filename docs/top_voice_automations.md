# Top Desktop Voice Automations

A curated showcase of top-tier desktop, web, and system voice automations built for high-efficiency voice computing. This document serves as a reference catalog for workflow demonstrations, YouTube showcase videos, and ongoing feature expansion.

---

## 1. Firefox & Web Search Automations

Defined in `caster_user_content/rules/apps/firefox/firefox_extended_rule.py`.

### Smart Search & Query Triggers
Execute searches across multiple targets and window layout modes using single-utterance voice triggers:

- **Web Search**:
  - `netzer <query>`: Instant web search in the active tab. ([L127](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L127))
  - `netzer tab <query>`: Open search in a new tab. ([L128](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L128))
  - `netzer window <query>`: Open search in a fresh window. ([L129](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L129))
  - `netzer sprite <query>`: Open search in a new window and automatically snap it side-by-side with the active window. ([L130](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L130))
- **History & Bookmark Querying**:
  - `hister <query>`: Instantly query Firefox browser history (injects `^`). ([L146](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L146))
  - `bookzer <query>`: Instantly query Firefox bookmarks (injects `*`). ([L155](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L155))
- **Targeted Platform Searches**:
  - `reddit <query>`: Append "reddit" and search immediately. ([L137](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L137))
  - `git search <query>`: Search GitHub repositories directly. ([L192](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L192))
  - `you search <query>`: Search YouTube videos directly. ([L196](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L196))
- **AI Automation**:
  - `gemzer <query>`: Automates navigation to Gemini (`https://gemini.google.com/app`), waits for load, types the query into the chat prompt, and submits automatically. ([L207](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L207))

### Advanced Tab & Window Layouts
- `pop out page`: Copies the active tab URL, closes the tab, opens a new window, pastes, and navigates. ([L117](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L117))
- `split right with <n>`: Snaps the active browser window left, grabs tab number `<n>`, detaches it to a new window, and snaps it right. ([L118](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L118))
- `go sprite <website>` / `go sprite clipboard`: Navigates to a domain or clipboard URL in a side-by-side split window. ([L169](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L169))

### Job Search & Content Processing
- `text to job postings`: One-shot action (`Store() + Function(_save_to_job_postings)`). Copies selected text and spawns a background Python process (`save_to_text.py`) to prompt for a filename and archive job descriptions. ([L237](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L237))
- `cover letter prompt`: Automates cover letter generation by pairing stored resume context (`RESUME`) with copied job posting text on the clipboard. ([L243](../caster_user_content/rules/apps/firefox/firefox_extended_rule.py#L243))

---

## 2. Excel Automations

Defined in `caster_user_content/rules/apps/office/excel/excel.py`.

### Rapid Grid Navigation & Selection
Eliminates mouse dependence in spreadsheet workflows:
- `fly <column> <row>`: Fast jump to any cell coordinate. ([L22](../caster_user_content/rules/apps/office/excel/excel.py#L22))
- `select <col1> <row1> through <col2> <row2>`: One-shot range selection (e.g., A1 through D50). ([L23](../caster_user_content/rules/apps/office/excel/excel.py#L23))

### Cell Utility & Quick Access
- `match above` / `match below`: Fill contents from adjacent cells. ([L26](../caster_user_content/rules/apps/office/excel/excel.py#L26))
- `fit width` / `fit height` / `word wrap` / `insert column`: Keyboard accelerator macros for common formatting. ([L39](../caster_user_content/rules/apps/office/excel/excel.py#L39))
- `queen <text>`: Accesses Microsoft Office Search (`Alt+Q`) to quickly query and execute Excel ribbon commands by voice. ([L43](../caster_user_content/rules/apps/office/excel/excel.py#L43))

---

## 3. App & Window Switching

Defined in `caster_user_content/util/app_switcher.py`, `window_switching.py`, and `window_switching_ccr.py`.

### Multi-Tier Failsafe Switcher
Switch between applications and window instances with robust multi-tier fallback ([switch_to_app](../caster_user_content/util/app_switcher.py#L380)):
1. **Tier 1 (Win32 / Pywinauto)**: Attempts standard window activation and focus restore.
2. **Tier 2 (Taskbar UIA)**: Performs a UI Automation click directly on the application's taskbar button.
3. **Tier 3 (Keyboard Macro)**: Falls back to taskbar key navigation (`Win+T`, arrow keys, `Enter`).

### Workspace Awareness & Alias Management
- **Virtual Desktop Tracking**: Uses `pyvda` to verify window desktop IDs, prioritizing windows on the active virtual desktop.
- **Window & Tab Aliasing**: Set custom voice aliases for windows or browser/editor tabs and instantly return to them using `switch to <alias>`.

---

## 4. System Controls, Hardware & Utility Macros

Defined in `caster_user_content/rules/global/global_nonccr_extended.py` and `docs/foot_pedal.md`.

### Hardware & IPC Integration
- **Foot Pedal & XML-RPC IPC Bridge**: Hardware debouncing and tap/drag/scroll handling for the Olympus RS31H foot pedal, linked to a local XML-RPC server for thread-safe hands-free Caster microphone toggling.

### Display & System Toggles
- `toggle night` / `toggle bed` / `toggle day`: Controls Windows 11 Quick Settings night mode and brightness levels. ([L65](../caster_user_content/rules/global/global_nonccr_extended.py#L65))
- `brightness <level>`: Sets display brightness. ([L66](../caster_user_content/rules/global/global_nonccr_extended.py#L66))
- System Utilities: `show network connections`, `show device manager`, `show add remove programs`. ([L75](../caster_user_content/rules/global/global_nonccr_extended.py#L75))

### Window Snapping & Desktop Management
- `window split <direction> <n>`: Snaps the active window in `<direction>` and snaps taskbar item `<n>` on the opposite side. ([L108](../caster_user_content/rules/global/global_nonccr_extended.py#L108))
- `start screen copy`: Spawns Android screen mirroring (`scrcpy`) and snaps it to the side of the screen. ([L182](../caster_user_content/rules/global/global_nonccr_extended.py#L182))

### Text & Cursor Manipulation
- `bling`: Triple-clicks mouse to copy the entire line under cursor. ([L167](../caster_user_content/rules/global/global_nonccr_extended.py#L167))
- `cling`: Triple-clicks mouse to cut the line under cursor. ([L169](../caster_user_content/rules/global/global_nonccr_extended.py#L169))
- `slacks <n>` / `slubs <n>` / `garbs <n>`: Double-clicks to cut, select, or copy words. ([L172](../caster_user_content/rules/global/global_nonccr_extended.py#L172))

### LLM & Productivity Helpers
- `grammar check clipboard`: Prepares a prompt asking for a grammar check of the clipboard content. ([L142](../caster_user_content/rules/global/global_nonccr_extended.py#L142))
- `width adjust`: Formats copied text for easy spreadsheet pasting with 40-character width constraints. ([L143](../caster_user_content/rules/global/global_nonccr_extended.py#L143))

---

## 5. Candidate Automations for Future Expansion

*The following voice rules are implemented across the user content directory and can be further documented or featured:*

- **IDE & Development**:
  - VSCode rules (`rules/apps/vscode/`): Editor navigation, terminal management, debugging shortcuts.
  - Custom Git Bash (`custom_gitbash.py`) & GitHub Desktop (`custom_githubdesktop.py`).
- **Media & Screen Capture**:
  - OBS Studio (`obs_studio.py`), Quick Picture Viewer (`quick_picture_viewer.py`), Clipchamp (`clipchamp.py`), VLC (`vlc.py`).
- **Communication & Productivity**:
  - Microsoft Teams (`msteams.py`), Zoom (`zoom.py`), Telegram (`telegram.py`), Element (`element.py`), Anki (`anki.py`).
- **Document & Office Apps**:
  - Outlook (`custom_outlook.py`), PowerPoint (`powerpoint.py`), Word (`word/`), LibreOffice (`libre_office/`), Sumatra PDF (`sumatra.py`), Gnumeric (`gnumeric.py`).
- **Task & Content Management**:
  - Task management rules (`task_management.py`), Markdown formatting (`markdown.py`), Taskbar interaction (`taskbar.py`).
