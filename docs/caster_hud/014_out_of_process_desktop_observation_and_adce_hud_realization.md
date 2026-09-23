[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](005_caster_hud_requirements_and_specifications.md) › **014: Out-of-Process Desktop Observation, ADCE HUD Realization, & Window Tracker Retirement**

---

> [!NOTE]
> **Document Status**: *Active Production Architecture & Living Canonical Reference (NOT SUPERSEDED)*.  
> Defines the active production architecture for out-of-process desktop context observation, the complete retirement of in-process window hooks, and authoritative rule filtering across Caster HUD and Taskbar HUD.

# 014: Out-of-Process Desktop Observation, ADCE HUD Realization, & Window Tracker Retirement

**Document ID**: `CASTER-DOC-HUD-014`  
**Status**: Active Production Architecture & Living Canonical Reference (NOT SUPERSEDED)  
**Target Subsystems**: `active-desktop-context-engine`, `castervoice/asynch/hud_support.py`, `castervoice/asynch/hud/`, `mods/caster-taskbar-hud.wh.cpp`, `caster_user_content/util/taskbar_hud_bridge.py`  
**Authors**: Amir Farhadi & Antigravity Principal Systems Architecture  

---

## 1. Executive Summary & Non-Supersession Invariant

This document establishes the authoritative production architecture for desktop context observation and heads-up telemetry across Caster. It codifies the permanent architectural transition from duplicate in-process Win32 hooks to a single out-of-process desktop observer.

### Non-Supersession Guarantee
Earlier documents in `docs/caster_hud/` detailed transitional implementations:
- Docs 001, 004, 008, 010, and 011 analyzed exploratory designs, initial in-process focus hooks, or preliminary active rule heuristics.
- Doc 005 remains the active specification for Qt HUD UI layouts, themes, and mouse interactions, but its window tracking specification (REQ-15) is superseded by this document.
- Doc 013 established the architectural decision record (ADR) recommending the elimination of duplicate observers.

This document represents the finalized, verified realization of that decision. It is the active, non-superseded reference for how desktop focus, window titles, micro-zones, and active rules are observed and dispatched.

---

## 2. Problem Analysis: The Failure of In-Process Window Tracking

The previous architecture maintained an in-process Win32 focus hook in `castervoice/asynch/hud/core/window_tracker.py`. This design introduced three structural bottlenecks:

1. **Duplicate Desktop Observers**:
   Two separate systems independently monitored OS focus shifts via `SetWinEventHook(EVENT_SYSTEM_FOREGROUND)`. The external .NET 10 ADCE daemon performed deep UI Automation inspection, while Caster ran a parallel Win32 message pump thread (`Win32-Focus-Hook`) in Python. Both systems reacted to the same OS events, consuming redundant CPU cycles and creating race conditions.

2. **CPython GIL Lock Contention**:
   The in-process hook thread executed Win32 message pump loops (`GetMessageW`, `TranslateMessage`, `DispatchMessageW`) under CPython. When window focus shifted rapidly during Alt-Tab or mouse clicks, the hook thread contended for the Python Global Interpreter Lock (GIL) against the real-time speech engine audio loop.

3. **Shallow Context & Elevation Limits**:
   The in-process Python hook could only read top-level window handles (`HWND`) and process names via `QueryFullProcessImageNameW`. It had zero visibility into sub-window elements, editor tabs, Monaco buffers, or integrated terminals. Furthermore, Windows User Interface Privilege Isolation (UIPI) prevented the unprivileged Python hook from inspecting elevated windows.

---

## 3. The Target Architecture: Pure Out-of-Process Desktop Observation

All desktop observation is outsourced to the standalone **Active Desktop Context Engine (ADCE)**. Caster maintains zero in-process window hooks.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        UNIFIED DESKTOP CONTEXT PIPELINE                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [ OUT-OF-PROCESS OBSERVER: ADCE.Daemon.exe (.NET 10 x64) ]                            │
│  ├── Native STA Thread: SetWinEventHook (Foreground & Focus)                           │
│  ├── Extraction Engine: FlaUI.UIA3 cache requests (sub-window zones & editor tabs)     │
│  └── HTTP Kestrel Server: Streams NDJSON events over http://127.0.0.1:8424/sse         │
│                                                                                        │
│                                           │                                            │
│                                           │ HTTP Server-Sent Events (SSE)              │
│                                           ▼                                            │
│  [ CASTER VOICE HOST: pythonw.exe ]                                                    │
│  ├── AdceTracker (hud/core/adce_tracker.py): Background SSE streaming thread           │
│  ├── _on_adce_context_changed(): Syncs adce_bridge RAM cache (< 0.001 ms access)       │
│  ├── get_active_contextual_rules(): Validates matching rules against rules.toml        │
│  │                                                                                     │
│  ├── Output Channel A (Local IPC Port 8339):                                           │
│  │   └── DesktopContextEvent & ActiveRulesEvent -> Caster Heads-Up Display (Qt GUI)   │
│  │                                                                                     │
│  └── Output Channel B (Named Pipe \\.\pipe\CasterTaskbarHud):                          │
│      └── printer.out tap -> Windows 11 Taskbar HUD (Windhawk Mod in explorer.exe)     │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Operational Contracts
- **Transport**: Standard HTTP/1.1 Server-Sent Events on `http://127.0.0.1:8424/sse`.
- **Latency**: ADCE emits context envelopes within 10ms to 25ms of physical focus change.
- **Immediate State Push**: When Caster establishes an SSE connection, ADCE immediately pushes the current active window snapshot in the opening event, ensuring zero initialization lag.
- **Fail-Soft Offline Mode**: If ADCE is not running, Caster's `AdceTracker` applies exponential backoff reconnection. The HUD displays `⚪ ADCE [ADCE is not connected]`, and active rules default cleanly to `[Global Context]` without throwing exceptions or blocking speech threads.

---

## 4. Complete Excision of In-Process Window Tracking

The file `castervoice/asynch/hud/core/window_tracker.py` has been completely deleted from the Caster codebase.

### Removed Win32 API Calls
The following native Win32 calls were excised from Caster:
- `user32.SetWinEventHook`
- `user32.UnhookWinEvent`
- `user32.GetForegroundWindow`
- `user32.GetWindowTextW`
- `user32.GetWindowTextLengthW`
- `user32.GetWindowThreadProcessId`
- `user32.GetMessageW`
- `user32.PostThreadMessageW`
- `kernel32.QueryFullProcessImageNameW`

### Refactored Focus Tracker Entry Point
In `castervoice/asynch/hud_support.py`, `get_focus_tracker()` now instantiates only `AdceTracker`:
```python
def get_focus_tracker():
    """Returns the global desktop context tracker instance (ADCE SSE listener)."""
    global _FOCUS_TRACKER
    if _FOCUS_TRACKER is None:
        with _FOCUS_TRACKER_LOCK:
            if _FOCUS_TRACKER is None:
                from castervoice.asynch.hud.core.adce_tracker import get_adce_tracker
                try:
                    _FOCUS_TRACKER = get_adce_tracker(on_context_changed=_on_adce_context_changed)
                except Exception:
                    pass
    return _FOCUS_TRACKER
```

The callback `_on_window_focus_changed()` was reduced to a no-op for backward compatibility. Inspecting active threads confirms that the `Win32-Focus-Hook` thread no longer exists. Only `ADCE-HUD-Tracker` runs in the background.

---

## 5. Dual HUD Telemetry Ingestion

Both the floating Qt HUD and the Windows 11 Taskbar HUD receive identical, synchronized context without performing independent OS polling.

### Subsystem 1: Floating Caster Heads-Up Display (Qt GUI)
1. **Event Reception**: The Qt GUI process (`hud.py`) listens on local TCP port 8339 for NDJSON telemetry frames.
2. **State Reduction**: Incoming `DesktopContextEvent` payloads update `state.desktop_context` through the pure `reduce_event()` function.
3. **UI Rendering**:
   - `StatusBarWidget`: Renders `ctx.window_title` or `ctx.process_name` in the top header.
   - `AdceBarWidget`: Renders the micro-zone badge (e.g. `{IntegratedTerminal}`, `{EditorCodeBuffer}`) and active file name.
   - `ActiveRulesBarWidget`: Renders active rule pills calculated from the ADCE process and window title.
4. **Zero OS Calls**: The GUI process makes zero calls to Win32 window APIs.

### Subsystem 2: Windows 11 Taskbar HUD (Windhawk Mod)
1. **Injection Point**: The C++ mod (`caster-taskbar-hud.wh.cpp`) runs in-process inside `explorer.exe`, injecting a XAML container into `SystemTrayFrameGrid`.
2. **IPC Pipe**: An asynchronous named pipe server on `\\.\pipe\CasterTaskbarHud` ingests telemetry packets from Caster's `printer.out` dispatcher (`TaskbarHudPrintHandler`).
3. **Display Modes**: Supports single compact command strip mode (~160px width to avoid encroaching on taskbar window buttons) and rotational carousel mode (`rotate`).

---

## 6. Authoritative Rule Evaluation & Context Matching

Previous iterations suffered from false active rule indications. For example, focusing Firefox displayed `Firefox` even when `FirefoxRule` was disabled in `rules.toml`. Focusing Antigravity IDE displayed `Vscodium`.

### Root Cause: The Executable String Heuristic
In Dragonfly, merged Continuous Command Recognition (CCR) rules receive generic names such as `Repeater1`. To provide a readable label, `hud_support.py` previously extracted the first executable from the rule's target list and capitalized it:
```python
# PREVIOUS HEURISTIC (REMOVED)
execs = getattr(ctx, "_executable", None)
if execs and len(execs) > 0:
    r_name = str(list(execs)[0]).capitalize()
```
Because `FirefoxCcrRule` declared `executable=["firefox", "waterfox"]`, the HUD displayed `"Firefox"`, masquerading as the disabled `FirefoxRule`. Because `CustomVSCodeCcrRule` declared `executable=["VSCodium", "code", ...]`, the HUD displayed `"Vscodium"`.

### The Deterministic Solution
The heuristic was completely removed and replaced with a three-stage validation pipeline in `hud_support.py`:

1. **Explicit Rule Class Name Propagation**:
   Dynamic CCR rules carry their source Rule Class Name (e.g. `CustomVSCodeCcrRule`, `FirefoxCcrRule`). `_format_rcn_display_name()` deterministically formats these into user-facing names (`CustomVSCode CCR`, `Firefox CCR`).

2. **Authoritative `rules.toml` Enablement Filtering**:
   `_is_rule_enabled_in_config()` validates rules against Caster's active configuration:
   - Rules with `rule.active == False` are suppressed.
   - Rules present in `[whitelisted]` but absent from `_enabled_ordered` are filtered out.
   - Dynamic CCR rules check their underlying `ccr_rule_class_name` against `_enabled_ordered`.

3. **Universal Precision Executable Matching**:
   `_match_executable_precision()` tests candidate processes against declared rule executables using exact string boundaries and extension equivalence. This prevents false prefix matches (e.g. `antigravity` matching `antigravity ide`, or `notepad` matching `notepad++`).

4. **Dynamic `AppContext.matches()` Protection**:
   When no target process is supplied by ADCE, Dragonfly's `AppContext.matches()` is skipped, preventing Dragonfly from executing internal Win32 `GetForegroundWindow()` calls.

---

## 7. Verification & Automated Test Suite

The architecture was verified through automated test suites and live process inspection.

### Test Execution
Run with 64-bit Python 3.10 and user configuration path:
```pwsh
$env:PYTHONPATH="$env:LOCALAPPDATA\caster"
py -3.10 -m unittest tests/test_antigravity_context_resolution.py tests/test_focus_transition_sequence.py scratch/test_hud_components.py
```
**Result**: 26/26 tests passed (100%).

### Empirical Test Cases Verified

| Test Case | Target Process | Expected Result | Verified Telemetry |
| :--- | :--- | :--- | :--- |
| **Standalone Antigravity** | `Antigravity.exe` | `['Antigravity Standalone']` | Activates standalone rule; excludes `Antigravity IDE` and `CustomVSCode`. |
| **Antigravity IDE** | `Antigravity IDE.exe` | `['Antigravity IDE', 'CustomVSCode']` | Activates IDE rules; excludes standalone rule. |
| **Disabled Firefox Rule** | `firefox.exe` | `[]` (or active CCR) | Filters out disabled `FirefoxRule`; prevents false `"Firefox"` display. |
| **CCR Display Naming** | `Antigravity IDE.exe` | `'CustomVSCode CCR'` | Formats display name cleanly; zero leakage of `"Vscodium"`. |
| **Thread Inspection** | Any | Zero Win32 hook threads | Active threads: `['MainThread', 'ADCE-HUD-Tracker']`. `Win32-Focus-Hook` is absent. |
| **ADCE Fallback** | Unspecified | Ingests from ADCE bridge | Falls back to `adce.get_current_process()` without querying Win32 window APIs. |

---

## 8. Summary of Architectural Invariants

1. **Zero In-Process Window Hooks**: Caster core and user content must never instantiate `SetWinEventHook` or call Win32 foreground window APIs for background context tracking.
2. **ADCE as Single Authority**: The out-of-process ADCE daemon is the sole authority for desktop focus, window titles, micro-zones, and active file paths.
3. **Authoritative Configuration**: Rules displayed on any HUD must be validated against `rules.toml` (`_enabled_ordered`).
4. **Clean Core Separation**: Upstream Caster grammar compilation and merger pipelines remain unmodified. All context routing occurs through external ingestion interfaces.
