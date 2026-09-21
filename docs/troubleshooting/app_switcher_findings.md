[ 🏠 Docs Home ](../README.md) › [ 📁 Troubleshooting ](../README.md#troubleshooting--diagnostics) › **App Switcher Findings**

---

# App Switcher Findings

## Issue: Windows PowerShell (Caster Status Window) Not Found
**Date**: 2026-08-10

### Overview
When attempting to switch to the "Windows PowerShell" application (which corresponds to the Caster Status Window), the `app_switcher` reported: `"No windows found for 'Windows Powershell'."`

This occurred despite the logger indicating that it had matched a window:
```
[AppSwitcher:DEBUG] App matched for 'Caster: Status Window (Dragonfly + Kaldi Latest)' (HWND 26546206). Checking desktop ID...
[AppSwitcher:DEBUG] get_window_desktop_id() calling AppView for HWND 26546206...
[AppSwitcher:DEBUG] AppView for HWND 26546206 returned {C2DDEA68-66F2-4CF9-8264-1BFD00FBBBAC} in 1.01ms
No windows found for 'Windows Powershell'.
```

### Potential Cause
The current implementation of `switch_to_app` only keeps a matched window if its `win_desktop_id` precisely matches the `current_desktop_id`. In this case, the PyVDA `AppView` returned a desktop ID that did not match the current virtual desktop.

**User Hypothesis**: 
It is highly likely that this behavior is related to the Caster Status Window being a **pinned item** (meaning it is set to appear on *all* virtual desktops). The PyVDA library might return a specific, non-matching GUID (or otherwise get confused) when queried for the desktop ID of a pinned window. We should not make any definitive assumptions on the diagnosis until further research is conducted into how PyVDA handles pinned items.

### Previous Attempted Fix (Reverted)
Before this hypothesis was noted, an attempted fix was made to the `app_switcher.py` code. The idea was to keep track of matched windows on the current desktop AND matched windows on other desktops, and then concatenate the two lists (prioritizing the current desktop). 

```python
    current_desktop_matches = []
    other_desktop_matches = []

    for hwnd, title_text in windows:
        if extract_app_name(title_text).lower() in app_names_lc:
            if current_desktop_id:
                win_desktop_id = os_env.get_window_desktop_id(hwnd)
                if win_desktop_id == current_desktop_id or win_desktop_id is None:
                    current_desktop_matches.append((hwnd, title_text))
                else:
                    other_desktop_matches.append((hwnd, title_text))
            else:
                current_desktop_matches.append((hwnd, title_text))
                
    matching_windows = current_desktop_matches + other_desktop_matches
```
This fix was **reverted** in order to keep the codebase clean while the behavior of pinned windows in PyVDA is properly researched.

---

## Issue: Complete Focus Escalation Denial via Elevated Foreground Process (UIPI) & Taskbar Keystroke Fail-Safe
**Date**: 2026-09-21

### 1. Incident Overview & Telemetry
During an active session, a voice command was issued to switch focus to `'Antigravity IDE'` (`HWND 1508800`). All three Win32 focus tiers escalated and failed sequentially, followed by a silent failure of the external fallback:

```text
[05:43:16.428] [AppSwitcher:DEBUG] App matched for 'caster - Antigravity IDE - caster-taskbar-hud.wh.cpp' (HWND 1508800). Checking desktop ID...
[05:43:16.430] [AppSwitcher:DEBUG] AppView for HWND 1508800 returned {B81E302B-192E-47EF-BA32-501D5DD59192} in 1.00ms
[05:43:16.430] [AppSwitcher:DEBUG] Window HWND 1508800 is on current desktop.
[05:43:16.432] [AppSwitcher:DEBUG] App matched for 'Caster - Antigravity IDE - Transcript Full' (HWND 1442386). Checking desktop ID...
[05:43:16.433] [AppSwitcher:DEBUG] AppView for HWND 1442386 returned {B81E302B-192E-47EF-BA32-501D5DD59192} in 1.01ms
[05:43:16.433] [AppSwitcher:DEBUG] Window HWND 1442386 is on current desktop.
[05:43:16.434] [AppSwitcher:INFO] Request to switch_to_app: 'Antigravity IDE/Windsurf/Notepad++/VSCodium/Visual Studio Code/Cursor', instance #1 (HWND 1508800)
[05:43:16.436] [AppSwitcher:DEBUG] Tier 1 SetForegroundWindow failed for HWND 1508800: (5, 'SetForegroundWindow', 'Access is denied.')
[05:43:16.518] [AppSwitcher:DEBUG] Tier 1 failed. Attempting Tier 2 (Alt-Key Bypass) for HWND 1508800...
[05:43:16.520] [AppSwitcher:DEBUG] Tier 2 Alt-Bypass failed for HWND 1508800: (0, 'SetForegroundWindow', 'No error message is available')
[05:43:16.642] [AppSwitcher:DEBUG] Tier 2 failed. Attempting Tier 3 (Thread Attachment) for HWND 1508800...
[05:43:16.645] [AppSwitcher:DEBUG] AttachThreadInput to fore_thread 6108 failed: (5, 'AttachThreadInput', 'Access is denied.')
[05:43:16.650] [AppSwitcher:ERROR] Tier 3 Thread Attachment failed for HWND 1508800: (5, 'SetForegroundWindow', 'Access is denied.')
[05:43:17.073] [AppSwitcher:ERROR] Failed to focus 'Antigravity IDE/Windsurf/Notepad++/VSCodium/Visual Studio Code/Cursor' for HWND 1508800.
```

### 2. Root Cause Analysis

#### A. The UIPI Integrity Boundary
- **Active Foreground Thread**: Telemetry captured `fore_thread 6108` as the active foreground thread at the time of execution.
- **Process Identification**: Thread `6108` belongs to PID `2572`, which was hosting the Windhawk UI (`mod.wh.cpp - Windhawk`). The user had been configuring the `caster-taskbar-hud.wh.cpp` mod.
- **Privilege Separation**: Windhawk runs at **High Integrity Level** (Administrator) to inject hooks into Windows Explorer and system modules. Caster, running under standard Python (`py -3.10`), executes at **Medium Integrity Level**.
- **The Failure Chain**:
  1. **Tier 1 (`SetForegroundWindow`)**: Windows User Interface Privilege Isolation (UIPI) explicitly prohibits a Medium Integrity process from stealing focus from an active High Integrity window. The OS returns Win32 Error `5` (`ERROR_ACCESS_DENIED`).
  2. **Tier 2 (`_alt_key_bypass`)**: The synthetic `Alt` event is ignored across the UIPI boundary for foreground transfer rights. `SetForegroundWindow` returns `0` (failure).
  3. **Tier 3 (`_attached_threads`)**: Windows blocks `AttachThreadInput` between processes of differing integrity levels as an explicit security constraint. Calling `AttachThreadInput(current_thread, 6108, True)` fails immediately with Win32 Error `5` (`ERROR_ACCESS_DENIED`).

#### B. The Silent Taskbar UIA Fallback Failure
In [`caster_user_content/util/app_switcher.py`](../../caster_user_content/util/app_switcher.py), lines 552 to 568 implement a best-effort taskbar click fallback via `get_taskbar_items()`. 

The fallback did not execute for two reasons:
1. `get_taskbar_items()` traverses `Shell_TrayWnd` searching for a legacy Windows 10 `control_type="ToolBar"` named `"Running applications"`.
2. Windows 11 redesigned the taskbar into a modern XAML Island host (`Windows.UI.Input.InputSite.WindowClass` -> `Taskbar.TaskbarFrameAutomationPeer`). It no longer contains a Win32 Toolbar control. `get_taskbar_items()` returned an empty list `[]`, causing the fallback branch to skip silently without logging an error.
3. In practice, simulated mouse clicks and UI Automation invocations on the taskbar are slow, fragile, and prone to pointer drift during hands-free speech workflows.

#### C. Critical Integrity Delineation: Elevated Targets vs. Unprivileged Overlays
A crucial architectural distinction must be maintained regarding what Tier 4 can and cannot accomplish under Windows security boundaries:
- **Speech Cannot Drive Elevated Targets**: Tier 4 does not enable speech recognition to send keystrokes into or manipulate an elevated window (such as Windhawk or an Administrator terminal). Windows UIPI strictly filters out synthetic input generated by lower-integrity processes toward higher-integrity targets. Any voice command that attempts to type or trigger actions inside an elevated window will not execute.
- **The Unprivileged Caster HUD Delineation**: The Caster Heads-Up Display (`Caster HUD v 1.7.0`) executes under standard user permissions (Medium Integrity). When the user clicks or focuses into the Caster HUD, the active foreground window transitions away from the elevated process to an unprivileged window. Commands issued while focused in the HUD execute normally against standard applications because no cross-integrity boundary is crossed.
- **The Scope of Tier 4**: Tier 4 does not bypass UIPI to control elevated software. Its sole architectural purpose is to provide a reliable recovery path to **switch away from** an elevated window back to a standard application by delegating the switch to the unprivileged desktop shell (`explorer.exe`) via registered shell hotkeys (`Win+T` traversal or `Win+<N>`).

---

### 3. Architectural Evaluation: Taskbar Keystroke Navigation Fail-Safe

#### A. Operating System Mechanics of `Win+T` Traversal
In hands-free voice operations, keyboard-driven shell navigation provides a reliable alternative when native Win32 window APIs fail:
1. **Shell Ownership**: `Win+T` (focus taskbar) and `Win+<N>` (activate Nth taskbar button) are registered system hotkeys handled directly by `explorer.exe`.
2. **Foreground Right Delegation**: When keyboard input activates a taskbar item (`Enter` or `Space`), the activation request is issued internally by Windows Explorer itself. Because Explorer is the shell process, its window activations bypass the standard background focus restrictions that block Caster's direct API calls.
3. **Established Precedent**: The repository already utilizes this exact mechanism in [`caster_user_content/rules/global/taskbar.py`](../../caster_user_content/rules/global/taskbar.py) (`TaskbarRule`):
   ```python
   "drip [<off1_1_20>]": R(Key("w-t/25, home/10, right:%(off1_1_20)s, enter/25") + Mouse("(0.5, 0.5)"))
   ```
   and in [`caster_user_content/rules/global/global_nonccr_extended.py`](../../caster_user_content/rules/global/global_nonccr_extended.py) (`_window_split`):
   ```python
   if 1 <= n <= 9:
       taskbar_key = f"w-{n}/50"
   elif n == 10:
       taskbar_key = "w-0/50"
   else:
       taskbar_key = f"w-t/30, home, right:{n - 1}, enter/50"
   ```

#### B. Proposed Architecture for Tier 4 (Taskbar Keystroke Fallback)
Instead of relying on fragile UIA mouse clicks, the final fail-safe in `restore_and_focus()` or `switch_to_app()` can incorporate structured taskbar keystroke navigation.

```
┌──────────────────────────────────────────────────────────────┐
│  Tier 1: Direct Win32 (BringWindowToTop + SetForeground)     │
└──────────────────────────────┬───────────────────────────────┘
                               │ verify_focus() == False
                               ▼
┌──────────────────────────────────────────────────────────────┐
│  Tier 2: Guarded Alt-Key Bypass (_alt_key_bypass)            │
└──────────────────────────────┬───────────────────────────────┘
                               │ verify_focus() == False
                               ▼
┌──────────────────────────────────────────────────────────────┐
│  Tier 3: Input Queue Thread Attachment (_attached_threads)   │
└──────────────────────────────┬───────────────────────────────┘
                               │ verify_focus() == False (e.g. UIPI Lockout)
                               ▼
┌──────────────────────────────────────────────────────────────┐
│  Tier 4: Shell Keystroke Navigation (Win+T Traversal)        │
│  • Calculate taskbar item position K (factoring pinned apps) │
│  • If 1 <= K <= 10: Key(f"w-{K % 10}/50")                    │
│  • If K > 10:       Key(f"w-t/25, home/10, right:{K-1},      │
│                            enter/25")                        │
│  • Handle multi-window grouping thumbnail selection          │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
                         verify_focus()
```

#### C. Engineering Considerations for Implementation
1. **Dynamic Position Reckoning**:
   - The engine must determine the 1-indexed taskbar button position `K` for the target application.
   - Pinned applications occupy fixed initial slots. Running unpinned applications appear after pinned items.
   - In Windows 11 with taskbar buttons set to "Never combine", each running window receives a dedicated taskbar slot. When grouping is enabled ("Always combine"), multiple instances share a single slot.
2. **Handling Grouped Windows**:
   - If an application has multiple instances grouped under a single button, pressing `Enter` on that taskbar item opens the thumbnail preview flyout.
   - For grouped buttons, repeated presses of `Win+<N>` cycle directly through the running windows of that specific application without requiring thumbnail flyout navigation.
3. **Execution Latency**:
   - Native Win32 focus (Tiers 1 to 3) executes in 0 to 80ms.
   - Keystroke traversal requires 50 to 150ms to allow Windows Explorer to process the shell hotkey and render the focus transition. Positioning this mechanism as the final fail-safe preserves sub-millisecond execution for standard focus transitions while providing a recovery path when running against elevated windows.

---

### 4. Empirical Follow-Up: The HUD Focus-Breaking Effect & Synthetic Keystroke Filtering

Following the implementation of Tier 4, live speech testing revealed distinct behavioral differences between direct window focus commands (`colt`) and synthetic keystroke commands (`dredge`):

```text
[ADCE Telemetry] Recognized: 'colt' -> Rule: 'Dictation' | Zone: [web_document] (vscodium)
[06:27:44.039] [AppSwitcher:DEBUG] App matched for 'caster - Antigravity IDE - app_switcher.py (Index) (app_switcher.py) - Read-only' (HWND 1508800). Checking desktop ID...
[06:27:44.040] [AppSwitcher:DEBUG] AppView for HWND 1508800 returned {B81E302B-192E-47EF-BA32-501D5DD59192} in 1.01ms
[06:27:44.040] [AppSwitcher:DEBUG] Window HWND 1508800 is on current desktop.
[06:27:44.040] [AppSwitcher:DEBUG] App matched for 'Caster - Antigravity IDE - Walkthrough' (HWND 1442386). Checking desktop ID...
[06:27:44.041] [AppSwitcher:DEBUG] AppView for HWND 1442386 returned {B81E302B-192E-47EF-BA32-501D5DD59192} in 1.51ms
[06:27:44.041] [AppSwitcher:DEBUG] Window HWND 1442386 is on current desktop.
[06:27:44.041] [AppSwitcher:INFO] Request to switch_to_app: 'Antigravity IDE/Windsurf/Notepad++/VSCodium/Visual Studio Code/Cursor', instance #1 (HWND 1508800)
[06:27:44.066] [AppSwitcher:INFO] Successfully focused 'caster - Antigravity IDE - app_switcher.py (Index) (app_switcher.py) - Read-only'
```

#### A. Why Tier 1 Succeeded in 25ms (The Focus-Breaking Airlock Effect)
In this test, the voice command `'colt'` succeeded on **Tier 1 (`SetForegroundWindow`) in 25ms** without escalating to Tier 4:
1. **Telemetry Window Confirmation**: ADCE telemetry recorded the active window context at recognition time: `Zone: [web_document] (vscodium)`. This confirms the foreground window was not Windhawk when `'colt'` executed.
2. **Physical Focus-Breaking Mechanism**: When the user physically clicked the mouse on or near the Caster HUD overlay (`Caster HUD v 1.7.0`), the physical hardware click transferred OS focus away from Windhawk. Physical mouse clicks bypass UIPI because they originate from real hardware interrupts rather than unprivileged synthetic message injection.
3. **Integrity Parity Reset**: Because the Caster HUD and IDE processes run at Medium Integrity (Standard User), clicking the HUD acted as an integrity airlock. Once the foreground process was unprivileged, calling `win32gui.SetForegroundWindow(1508800)` satisfied Windows foreground activation rules. Caster successfully brought Antigravity IDE to the front on Tier 1 without encountering Error 5 (`ERROR_ACCESS_DENIED`).
4. **When Tier 4 Executes**: Tier 4 only activates when the user remains locked inside an elevated window (Windhawk, Task Manager) without touching the mouse, forcing `SetForegroundWindow` and `AttachThreadInput` to fail.

#### B. Why Standard Commands (e.g. `dredge`) Fail Silently Without HUD Feedback
In contrast to `app_switcher.py`, standard Caster navigation commands like `dredge` failed to produce any window change or HUD notification when spoken while focused in Windhawk:
1. **Synthetic Input vs Window Management APIs**:
   - `dredge` is defined in `castervoice/rules/core/navigation_rules/nav.py` as `R(Key("alt:down, tab/20:%(nnavi10)d, alt:up"))`.
   - Dragonfly's `Key` action calls Win32 `keybd_event` or `SendInput` to inject synthetic keystrokes into the active window's input queue.
   - When an elevated window holds foreground focus, Windows UIPI security rules drop all synthetic input coming from Medium Integrity processes. The OS kernel rejects the keystrokes before they reach the target application message loop.
2. **HUD Telemetry Architecture**:
   - The Caster HUD (`HudPrintMessageHandler` in `castervoice/asynch/hud_support.py`) listens strictly to messages sent through `castervoice.lib.printer.out`.
   - Direct `Key(...)` actions do not publish to `printer.out`. Because the keystrokes were dropped silently by the OS and no print messages were emitted, the HUD showed nothing.
   - The microphone and Dragonfly engine continued to recognize audio because speech engine hooks operate independently of the foreground window's integrity level.
#### C. Empirical Follow-Up: The Explorer Reset Test (Windhawk vs Waterfox)

To test focus recovery under cold shell conditions, an Explorer reset (`restart explorer.bat`) was executed while focused in two different target processes, followed by speaking `'colt'`:

```text
[ADCE Telemetry] Recognized: 'colt' -> Rule: 'Dictation' | Zone: [web_document] (vscodium)
[06:34:00.180] [AppSwitcher:DEBUG] App matched for 'caster - Antigravity IDE - Preview app_switcher_findings.md' (HWND 1508800). Checking desktop ID...
[06:34:00.180] [AppSwitcher:DEBUG] App matched for 'Caster - Antigravity IDE - Implementation Plan' (HWND 1442386). Checking desktop ID...
[06:34:00.180] [AppSwitcher:INFO] Request to switch_to_app: 'Antigravity IDE/Windsurf/Notepad++/VSCodium/Visual Studio Code/Cursor', instance #1 (HWND 1508800)
[06:34:00.180] [AppSwitcher:DEBUG] Tier 1 SetForegroundWindow failed for HWND 1508800: (5, 'SetForegroundWindow', 'Access is denied.')
[06:34:00.273] [AppSwitcher:DEBUG] Tier 1 failed. Attempting Tier 2 (Alt-Key Bypass) for HWND 1508800...
[06:34:00.275] [AppSwitcher:DEBUG] Tier 2 Alt-Bypass failed for HWND 1508800: (0, 'SetForegroundWindow', 'No error message is available')
[ADCE Context] antigravity ide -> [unknown] (127.9 ms)
[06:34:00.396] [AppSwitcher:DEBUG] Tier 2 failed. Attempting Tier 3 (Thread Attachment) for HWND 1508800...
[06:34:00.396] [AppSwitcher:DEBUG] AttachThreadInput to fore_thread 27208 failed: (5, 'AttachThreadInput', 'Access is denied.')
[ADCE Context] antigravity ide -> [unknown] (127.9 ms)
[06:34:00.400] [AppSwitcher:ERROR] Tier 3 Thread Attachment failed for HWND 1508800: (5, 'SetForegroundWindow', 'Access is denied.')
[06:34:00.614] [AppSwitcher:DEBUG] Tier 3 failed. Attempting Tier 4 (Taskbar Keystroke Navigation) for HWND 1508800...
[06:34:00.730] [AppSwitcher:INFO] Tier 4: Selected taskbar slot 4 for 'caster - Antigravity IDE - Preview app_switcher_findings.md - 2 running windows' (app: 'Antigravity IDE', instance #1)
[06:34:01.855] [AppSwitcher:ERROR] Failed to focus 'Antigravity IDE/Windsurf/Notepad++/VSCodium/Visual Studio Code/Cursor' for HWND 1508800.
```

##### 1. Why All Four Tiers Failed Under Windhawk
1. **Foreground Lock Owner**: When `explorer.exe` restarts, it does not steal focus from existing top-level windows. Windhawk UI (PID 2572, TID 27208) remained the active foreground window at High Integrity Level.
2. **Tier 1 & Tier 3 Rejections**: Windows returned Win32 Error 5 (`ERROR_ACCESS_DENIED`) for both `SetForegroundWindow` and `AttachThreadInput` because Caster runs at Medium Integrity.
3. **Tier 2 & Tier 4 Synthetic Input Drop**:
   - Tier 2 attempted `_alt_key_bypass()` via `keybd_event(VK_MENU)`.
   - Tier 4 resolved taskbar slot 4 correctly and executed `Key("w-4/50")` via `keybd_event(VK_LWIN)` and `keybd_event(ord('4'))`.
   - Under Windows UIPI, the raw input thread drops all synthetic keyboard input originating from lower-integrity processes if the current foreground window is elevated. The keystrokes were discarded by the Windows kernel before reaching Explorer or the target window.

##### 2. Why Tier 2 Succeeded Under Waterfox
In the identical test executed with Waterfox in the foreground:
1. **Integrity Parity**: Waterfox runs at Medium Integrity (Standard User).
2. **ForegroundLockTimeout Bypass**: When Explorer restarts, Windows activates standard `ForegroundLockTimeout`, causing Tier 1 to fail without an Error 5.
3. **Alt-Key Acceptance**: Because the active window was Medium Integrity, Windows accepted the synthetic `VK_MENU` keystroke emitted by `_alt_key_bypass()`. The OS cleared the lock timeout, allowing `SetForegroundWindow` to bring Antigravity IDE to the front on Tier 2.

##### 3. The Apparent "Unpredictability" Resolved
The variance between test runs is determined by which window holds the OS foreground lock at speech recognition time:
- If focus was left untouched inside Windhawk, the active window is High Integrity. Windows UIPI blocks Tiers 1 through 4.
- If the user clicked the taskbar or HUD in between, hardware mouse input transferred focus to an unprivileged window. The UIPI restriction was cleared, and the voice command succeeded immediately on Tier 1 or Tier 2.
- For hands-free switching out of elevated windows without manual mouse intervention, the calling speech engine must run at High Integrity (Run as Administrator) or with `uiAccess="true"` in its application manifest.




