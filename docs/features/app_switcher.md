---
Status: Active / Production
Architecture Version: v3 (August 2026 Refactor)
Canonical Code: caster_user_content/util/app_switcher.py
Canonical Blueprint: docs/architecture/app_switcher_architectural_blueprint.md
Evolution Timeline: docs/history/app_switcher_timeline.md
---

[ 🏠 Docs Home ](../README.md) › [ 📁 Features ](../README.md#features) › **App & Window Switcher**

---

# App & Window Switcher

The [`caster_user_content/util/app_switcher.py`](../../caster_user_content/util/app_switcher.py) utility provides high-performance, deterministic desktop window switching, application focusing, tab navigation, and workspace isolation for the Caster voice recognition framework.

---

## Key Capabilities

- **Sub-Millisecond Direct Win32 Focus Tiers**:
  1. **Tier 1 (Fast Path)**: Direct native Win32 `SetForegroundWindow` + `BringWindowToTop` (0–10ms execution).
  2. **Tier 2 (Alt-Key Bypass)**: Bypasses Windows `ForegroundLockTimeout` via the guarded `_alt_key_bypass()` context manager.
  3. **Tier 3 (Dual-Thread Attachment)**: Synchronizes calling and target thread input queues via `_attached_threads()` with shell `SwitchToThisWindow`.
  4. **Taskbar UIA Fallback**: Direct UI Automation button click in `Shell_TrayWnd` if all Win32 tiers fail.
- **Guarded Keystate Safety**: Eliminates stuck modifier keys and thread deadlocks through nested `try-finally` context managers and `VK_NONE` (`0xFF`) dummy key injection.
- **Micro-Polling Focus Verification**: Uses a fast 10ms polling loop (`verify_focus`) to confirm foreground transitions immediately (typically 10–80ms).
- **Workspace & Virtual Desktop Isolation**: Enforces workspace boundaries via `pyvda`, preventing cross-desktop focus contamination.
- **Dynamic Window & Tab Aliasing**: Binds custom spoken names (`"switch to leets"`, `"set page docs"`) to windows and browser/editor tabs, managed atomically by the `AliasRegistry`.
- **Automated Tab Navigation**: Automatically cycles tabs (`Ctrl+Tab` for browsers/terminals, `Ctrl+PgDn` for IDEs) until the active window caption matches the target.

---

## Voice Commands Reference

Window switching commands are exposed through [window_switching.py](../../caster_user_content/rules/global/window_switching.py) and [window_switching_ccr.py](../../caster_user_content/rules/global/window_switching_ccr.py):

| Voice Command Pattern | Action | Underlying Function |
| :--- | :--- | :--- |
| `"switch <app_name>"` | Switches to the primary instance of an application on the active virtual desktop | `switch_to_app(app_name, 1)` |
| `"switch <app_name> <n>"` | Switches to the *n*-th instance of an application | `switch_to_app(app_name, n)` |
| `"switch [to] <alias>"` | Switches directly to an aliased window or tab | `switch_to_alias(alias)` |
| `"set window <alias>"` | Binds the current active window to a spoken alias | `set_window(alias)` |
| `"set page <alias>"` | Binds the current tab (browser or IDE) to a spoken alias | `set_page(alias)` |
| `"alias reset"` | Clears the alias bound to the currently focused window | `clear_alias()` |
| `"alias clear all"` | Clears all registered window and tab aliases | `clear_all_aliases()` |
| `"title <window_title>"` | Switches to a window matching a specific title substring | `title(window_title)` |
| `"show window info"` | Prints detailed diagnostic info (HWND, title, app name, PID) | `show_window_info()` |

---

## Architectural Documentation & Blueprints

For complete technical specifications, state machines, sequence diagrams, and evolution history, refer to:

- 🏗️ **[App Switcher Architectural Blueprint (v3)](../architecture/app_switcher_architectural_blueprint.md)**: The authoritative production blueprint detailing structural layers, Win32 focus tiers, guarded context managers, and sequence diagrams.
- 📜 **[App Switcher Evolution Timeline](../history/app_switcher_timeline.md)**: Comprehensive 2-year retrospective tracing window switching across 5 eras (Windhawk taskbar macros → Pywinauto → Native Win32 v3).
- 🔍 **[App Switcher Focus Analysis](../architecture/app_switcher_focus_analysis.md)**: Empirical analysis of Windows foreground-lock bypasses during Explorer shell restarts.
- 📝 **[Code Review & Historical Critique](../architecture/app_switcher_code_review.md)**: Historical critique analyzing pre-refactor anti-patterns resolved in the August 2026 refactor.
- 🗄️ **Archived Blueprints**: [Blueprint v1 (Archived)](../architecture/archive/app_switcher_architectural_blueprint_v1.md) & [Blueprint v2 (Archived)](../architecture/archive/app_switcher_architectural_blueprint_v2.md).

---

## Architecture & Subsystems

[`app_switcher.py`](../../caster_user_content/util/app_switcher.py) is structured into five cohesive modules:

### 1. Platform Abstraction Layer (`WindowsOSAdapter`)
- Encapsulates direct Win32 APIs (`win32gui`, `win32process`, `win32api`, `ctypes.windll.user32`).
- Implements `restore_and_focus(handle)` with progressive 3-tier Win32 escalation.
- Manages virtual desktop queries via `pyvda.VirtualDesktop` and `pyvda.AppView`.
- Houses lazy `_desktop_uia` / `_desktop_win32` pywinauto backends for taskbar fallback queries.

### 2. Guarded Context Managers
- **`_alt_key_bypass()`**: Injects Alt down to satisfy OS user-interaction requirements, followed by guaranteed `VK_NONE` (`0xFF`) and Alt release in nested `finally` blocks to prevent menu bar lockup.
- **`_attached_threads(target_hwnd)`**: Attaches calling thread input queues to the target and foreground threads with guaranteed detachment.

### 3. Persistence Layer (`AliasRegistry`)
- Encapsulates all alias JSON serialization to `caster_user_content/window_aliases.json`.
- Provides atomic `get`, `set`, `remove`, `remove_by_handle`, and `clear` operations with automatic stale handle pruning.

### 4. Public Command APIs
- Voice-facing orchestrators (`switch_to_app`, `switch_to_alias`, `set_window`, `set_page`, `clear_alias`, `title`, `show_window_info`).

### 5. Domain Logic & Tab Navigation
- `extract_app_name()` with descending length matching against configured application names.
- `find_tab()` for automated tab title polling and keystroke cycling (`Ctrl+Tab` or `Ctrl+PgDn`).
- `verify_focus()` non-blocking 10ms micro-polling loop.

---

## Dual Focus Execution Pipelines

```
                                  Voice Trigger Received
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
         [ switch_to_alias(alias) ]                     [ switch_to_app(app, inst) ]
                    │                                               │
          Resolve WindowInfo from                               Enumerate Windows on
               AliasRegistry                                  Current Virtual Desktop
                    │                                               │
          Target HWND Validated                               Resolve Target HWND
                    │                                               │
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
                        ┌───────────────────────────────────────┐
                        │   restore_and_focus(target_hwnd)      │
                        │   Tier 1: Direct Win32 (0-10ms)       │
                        │   Tier 2: Alt-Key Bypass (80-120ms)   │
                        │   Tier 3: Thread Attachment (120ms)   │
                        └───────────────────┬───────────────────┘
                                            │
                                 verify_focus() == True?
                                 ├── Yes
                                 │    │
                                 │    ▼
                                 │  is_tab == True?
                                 │   ├── Yes ──► find_tab() Title Cycling ──► [ Success ]
                                 │   └── No ────────────────────────────────► [ Success ]
                                 │
                                 └── No
                                      │
                                      ▼
                        ┌───────────────────────────────────────┐
                        │ Fallback: Taskbar UIA Button Click    │
                        │ (Shell_TrayWnd control.click_input()) │
                        └───────────────────┬───────────────────┘
                                            │
                                 verify_focus() == True?
                                 ├── Yes ──► [ Success ]
                                 └── No  ──► [ Report Failure / Prune Alias ]
```
