# Ticket 038: Empirical Investigation & Data Gathering for App Switcher Failures, Hangs, and Recovery

**Type:** `wayfinder:investigation` (Empirical Testing & Data Gathering)  
**Status:** In Progress / Claimed  
**Depends on:** Ticket 036  
**Blocks:** C# Micro MCP Server Refactoring  

## Objective

Conduct real-world, empirical testing of [app_switcher.py](../../caster_user_content/util/app_switcher.py) during regular Caster voice usage to observe failure modes, hang mechanisms, and recovery behavior. The goal is to stress-test window switching, tab search loops, alias creation (`set window`, `set page`), and clearing operations to capture concrete timing diagnostics, thread state snapshots, and error tracebacks.

## Key Areas to Investigate & Monitor

1. **Alias Management & State Persistence:**
   - Test setting window aliases (`set window <alias>`) and tab/page aliases (`set page <alias>`).
   - Monitor `window_aliases.json` persistence across Caster restarts and window handle invalidations (e.g. when an app closes or changes HWND).
   - Evaluate behavior when switching to stale or destroyed window handles (`switch_to_alias`).

2. **Execution Tier Latency & Hang Tracing:**
   - **Tier 1 (Pywinauto Focus / Win32 Thread Input Bypass):** Monitor calls to `restore_and_focus`. Identify when `pywinauto` hangs or blocks standard execution during COM apartment deadlocks or when target windows are minimized/locked.
   - **Tier 2 (Taskbar UIA Click):** Track taskbar UIA tree traversal latency (`get_taskbar_items`) and `click_input()` failures when UIPI or Shell_TrayWnd restrictions interfere.
   - **Tier 3 (Keyboard Macro Fallback):** Observe keyboard macro execution (`w-t/3, home, right:...`) latency and failure cases when focus is stolen mid-macro.

3. **Tab Switching Loop Resilience:**
   - Observe `find_tab` loop execution (`Key("c-tab")` / `Key("c-pgdown")`) across supported browsers (Waterfox, Firefox) and IDEs (Cursor, Windsurf, VSCodium).
   - Capture maximum retry limits, target title comparison mismatches, and potential loop hangs.

4. **Enhanced Diagnostic Verbosity & Logging Integration:**
   - Implement detailed, timestamped logging (`[HH:MM:SS.mmm] [AppSwitcher:<LEVEL>]`) in `app_switcher.py` to immediately surface timing durations, active HWNDs, thread IDs, tier transitions, and stack traces when hangs occur.

## Expected Deliverables & Next Steps

- **Empirical Log & Data Collection:** Gather runtime console logs with high-precision timing to isolate exact bottleneck lines in `app_switcher.py`.
- **Failure Taxonomy:** Document recurring failure mechanisms (e.g., stale HWNDs, thread input attachment refusal, pywinauto STA thread blocking).
- **Informed MCP Server Design:** Use empirical findings to refine tool schemas and fail-safe order in the upcoming C# Micro MCP Server.

---

## Findings & Observations Log

### Incident 1: The 10-Second `switch_to_app` Delay
- **Symptom:** A normal voice command to switch to an application successfully focused the window, but the total operation took 10.44 seconds.
- **Investigation:** The delay occurred prior to the target window being resolved, implying a bottleneck during window enumeration. Calling `pyvda.AppView(hwnd).desktop_id` to filter windows by virtual desktop can sporadically block for extended periods on certain window handles due to underlying `IVirtualDesktopManager` COM hangs.
- **Action Taken:** Added telemetry warnings to isolate the exact HWNDs causing these COM slowdowns during the window iteration loop.

### Incident 2: The Assumed "COM Deadlock" (Debunked)
- **Symptom:** The user focused LibreOffice Calc on a secondary workspace and said "set window spreading". Caster completely froze. No output was generated. The user recovered by pressing Ctrl+C in the terminal, at which point a flood of delayed logs appeared.
- **Initial Investigation:** It was originally assumed that `pywinauto.Desktop(backend="uia").get_active()` initiated a cross-workspace COM tree walk that deadlocked indefinitely due to the lack of an STA message pump on the Python main thread.
- **Critical Correction (The QuickEdit Freeze):** The user noted they frequently click into the PowerShell window to focus it. Clicking into a Windows PowerShell terminal activates **"QuickEdit" mode**, which completely pauses the standard output (`stdout`) stream. Because the app switcher logs heavily, the moment the command was recognized, the Python thread attempted to `print()` and was hard-blocked by the paused console.
- **Proof:** Pressing `Ctrl+C` instantly un-paused the terminal, dumping the buffered logs and resuming the script. Furthermore, the user observed that during these "freezes", regular voice commands (e.g., "dredge") that don't print to the console continue to execute successfully, proving the engine is not deadlocked. A subsequent test of the exact same LibreOffice command did not freeze but instantly threw a Pywinauto exception (`Neither GUI element...`), proving UIA fails cleanly rather than hanging.
- **Action Taken:** The hypothesis that Python's UIA bindings are actively causing hard deadlocks on the main thread is currently **unsubstantiated**. All observed "hard freezes" so far are attributed to the PowerShell QuickEdit `stdout` block. Documented to prevent misdiagnosing this console lockup as a COM deadlock in the future.

### Edge Case: Tab Switching Loop (`find_tab`) Exception Spam
- **Scenario:** When using `switch_to_alias` for a tab (e.g., "switch tiny") that exists on a secondary workspace, the `find_tab` while-loop executes.
- **Behavior:** The while-loop constantly polls `get_active_window()`. Because UIA struggles to resolve active elements on background/secondary workspaces, it rapidly spams the `Exception during _desktop_uia.get_active()` error in the logs.
- **Action Taken:** The loop still successfully completes because the exception is caught. It reinforces that UIA is unpredictable when querying cross-workspace elements.

### Observation: Tier 1 Sub-Phases & OS Focus Bypassing
- **Scenario:** The user issued the "webs" command to switch to a Waterfox window. The logs showed a Pywinauto `SetForegroundWindow` error, followed by "Attempting Thread Attachment and Alt-key bypass", and finally reported "Tier 1: Successfully focused".
- **Behavior:** This is expected and correct behavior. "Tier 1" encompasses all direct `HWND` (window handle) manipulations. It is split into two internal phases:
  1. **Standard Pywinauto Focus:** Attempts to focus the window gracefully. If Windows blocks this (e.g., to prevent focus stealing), it throws a `SetForegroundWindow` error.
  2. **OS Bypass (Thread Attachment):** When standard focus fails, Tier 1 immediately falls back to a low-level OS bypass (attaching the current thread to the target thread's input and injecting a dummy Alt-key press). 
- **Result:** The OS bypass successfully forced Windows to hand over focus. Because this was still achieved using direct OS window APIs, `switch_to_app` correctly reported it as a "Tier 1 success". "Tier 2" is only invoked if the OS bypass also fails, requiring a physical UIA click on the taskbar.
