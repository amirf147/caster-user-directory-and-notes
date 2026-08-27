<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2024-2026 Amir Farhadi -->

[ 🏠 Docs Home ](../README.md) › [ 📁 Features ](../README.md#features) › **ADCE Dynamic IDE Terminal Context Guide**

---

# ADCE Dynamic IDE Terminal Context & Spiking Guide

> **Document Status:** Active Feature Guide & Empirical Test Runbook  
> **Target Applications:** Antigravity IDE, Visual Studio Code, Cursor, Windsurf, VSCodium  
> **Backend Engine:** [Active Desktop Context Engine (ADCE)](https://github.com/amirf147/active-desktop-context-engine)  
> **Related Documents:** [Dragonfly Recognition Observers & Functional Contexts](../framework_explainers/dragonfly_recognition_observers_and_functional_contexts.md) | [017: UI Automation Structures](../accessibility_mcp/017_ui_automation_tree_structures_and_target_zones_reference.md)

---

## 1. Overview & Architecture

This solution enables **fine-grained sub-window voice grammar activation** without stalling the Dragonfly speech recognition loop. 

When you focus the integrated terminal inside Antigravity IDE / VS Code, the specialized terminal voice grammar (`IDETerminalRule`) activates dynamically. When you click back into the code editor buffer, the terminal grammar sleeps and standard editor commands take over.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ADCE Background Daemon                          │
│  • Listens to Win32 focus events (EVENT_OBJECT_FOCUS)                  │
│  • Resolves focused zone (IntegratedTerminal vs EditorCodeBuffer)      │
│  • Streams snapshots over local HTTP/SSE (port 8424)                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Asynchronous Push / SSE)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  Caster Background Thread (Python)                     │
│  • `adce_bridge.py` updates local memory state:                        │
│    ADCE_STATE["zone"] = "IntegratedTerminal"                           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Zero-latency RAM read: < 0.0001 ms)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  Dragonfly Speech Recognition Loop                     │
│  • You speak "git status" ──► FuncContext.matches()                    │
│  • `is_ide_terminal_focused()` returns True instantly                  │
│  • Terminal Rule: ACTIVE! Executes without audio lag                   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. File Topology & Created Artifacts

All components live cleanly inside `caster_user_content`—**zero modifications to Caster core are required**:

| Component | File Path | Purpose |
| :--- | :--- | :--- |
| **ADCE Bridge Client** | [`caster_user_content/util/adce_bridge.py`](../../caster_user_content/util/adce_bridge.py) | Background thread listening to ADCE's SSE endpoint (`http://127.0.0.1:8424/sse`), maintaining atomic in-memory state. |
| **IDE Terminal Rule** | [`caster_user_content/rules/apps/vscode/ide_terminal.py`](../../caster_user_content/rules/apps/vscode/ide_terminal.py) | Dragonfly `MappingRule` gated with `function_context=is_ide_terminal_focused`. |
| **Configuration** | [`settings/rules.toml`](../../settings/rules.toml) | Whitelists and enables `IDETerminalRule = true`. |

---

## 3. Step-by-Step Live Test & Run Guide

### Step 1: Launch the ADCE Background Daemon

Open a terminal in the `active-desktop-context-engine` repository:

```powershell
# Run in HUD mode (shows floating diagnostic overlay) or headless mode:
dotnet run --project src/ADCE.Daemon -- --hud
```

> **Alternative Headless Mode:**  
> `dotnet run --project src/ADCE.Daemon -- --headless --port 8424`

* The daemon will initialize the Win32 `WinEvent` hooks and start the HTTP/SSE streaming server on `http://127.0.0.1:8424/sse`.

---

### Step 2: Launch Caster

Launch Caster using your standard launcher script or preferred engine environment.

* `adce_bridge.py` will automatically connect to the local ADCE stream in the background on startup.

---

### Step 3: Live Voice Verification

1. Open **Antigravity IDE** (or VS Code).
2. Click into the **Monaco Code Editor Buffer**.
   * Speak: `"terminal voice ping"`
   * **Result:** Nothing executes (rule is inactive because context is `EditorCodeBuffer`).
3. Click or press `Ctrl + \`` to focus the **Integrated Terminal Pane**.
   * Speak: `"terminal voice ping"`
   * **Result:** Terminal outputs: `>>> ADCE TERMINAL CONTEXT VERIFIED <<<`
4. Try fast CLI commands:
   * Speak: `"git status"` $\rightarrow$ Runs `git status`
   * Speak: `"git branch"` $\rightarrow$ Runs `git branch -a`
   * Speak: `"clear terminal"` $\rightarrow$ Sends `Ctrl+L`

---

## 4. Voice Commands Available in `IDETerminalRule`

### Shell & Flow Navigation
| Voice Trigger | Action / Shortcut |
| :--- | :--- |
| `"clear [terminal]"` | `Ctrl + L` (Clear terminal screen) |
| `"kill terminal"` | `Ctrl + Shift + W` (Close terminal pane) |
| `"cancel command"` | `Ctrl + C` (SIGINT break) |
| `"exit shell"` | Types `exit` + `Enter` |
| `"line up"` / `"line down"` | `Up` / `Down` arrow (Shell history navigation) |
| `"scroll up [<n>]"` | `Shift + PageUp` (Scroll terminal buffer up $n$ times) |
| `"scroll down [<n>]"` | `Shift + PageDown` (Scroll terminal buffer down $n$ times) |

### Git Workflow Commands
| Voice Trigger | Shell Execution |
| :--- | :--- |
| `"git status"` | `git status` + `Enter` |
| `"git diff"` | `git diff` + `Enter` |
| `"git diff cached"` | `git diff --cached` + `Enter` |
| `"git branch"` | `git branch -a` + `Enter` |
| `"git log"` | `git log -n 5 --oneline` + `Enter` |
| `"git pull"` | `git pull` + `Enter` |
| `"git push"` | `git push` + `Enter` |
| `"git fetch"` | `git fetch --all` + `Enter` |
| `"git stash"` | `git stash` + `Enter` |
| `"git stash pop"` | `git stash pop` + `Enter` |
| `"git add all"` | `git add -A` + `Enter` |

### Build, Test & Runtime
| Voice Trigger | Shell Execution |
| :--- | :--- |
| `"run tests"` | `npm test` + `Enter` |
| `"run build"` | `npm run build` + `Enter` |
| `"run dev"` | `npm run dev` + `Enter` |
| `"cargo check"` | `cargo check` + `Enter` |
| `"cargo test"` | `cargo test` + `Enter` |
| `"cargo build"` | `cargo build` + `Enter` |
| `"python run"` | Types `py -3.10 ` + `Tab` |

---

## 5. Diagnostic & Health Checks

You can verify that the ADCE bridge and predicate logic are functioning directly in Python without speaking:

```powershell
py -3.10 -c "from caster_user_content.util.adce_bridge import adce, is_ide_terminal_focused; print('Connected:', adce.is_connected()); print('Active Zone:', adce.get_current_zone()); print('Terminal Focused:', is_ide_terminal_focused())"
```

* If ADCE is running, `Connected:` will be `True` and `Active Zone:` will display the real-time zone (e.g. `IntegratedTerminal`, `EditorCodeBuffer`, `SidebarExplorer`).
