---
title: "Issue: Synthetic Win+Ctrl+F4 Focus Deadzone on Empty Workspaces and Native WinVDA Migration"
tags: [caster, winvda, pyvda, virtual-desktops, bug-report, proposal]
status: Backlog / Proposed Solution
date: 2026-09-24
---

# Issue: Synthetic Win+Ctrl+F4 Focus Deadzone on Empty Workspaces and Native WinVDA Migration

## Metadata
* **Issue Type:** Bug Report and Architecture Proposal
* **Tags:** `caster`, `winvda`, `pyvda`, `virtual-desktops`
* **Affected Grammar:** `castervoice/rules/core/navigation_rules/window_mgmt_rule.py` (`close work [space]`)
* **Underlying Libraries:** `winvda`, `pyvda`, `dragonfly`

---

## 1. Problem Description

When navigating virtual desktops via voice commands, invoking `close work` fails under a reproducible edge case:

1. User creates or switches to a secondary workspace (e.g., Desktop 2).
2. User launches a single application window (e.g., a web browser) on that workspace.
3. User closes the application window. The workspace is now empty, containing zero top-level application windows.
4. User speaks the command `close work`. Nothing happens. The desktop remains open.
5. If the user navigates away to Desktop 1 (which has active application windows) and returns to Desktop 2, speaking `close work` succeeds.

---

## 2. Root Cause Analysis

### 2.1 The Focus Deadzone on Empty Desktops
In `castervoice/rules/core/navigation_rules/window_mgmt_rule.py`, `close work [space]` is defined as a static keystroke action:

```python
"close work [space]":
    R(Key("wc-f4")),
```

The command does not invoke any Python API or virtual desktop library. It dispatches a synthetic `Win + Ctrl + F4` shortcut via Dragonfly's Win32 `SendInput` backend.

When the last application window on Desktop 2 closes:
1. The Win32 API function `GetForegroundWindow()` returns `0` (`NULL`) or points to an orphaned thread of the exiting application process.
2. In `dragonfly/actions/keyboard/_win32.py`, keyboard layout resolution attempts to query the thread owner of the foreground window:
   ```python
   thread_id = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[0]
   return win32api.GetKeyboardLayout(thread_id)
   ```
3. Windows Explorer (`explorer.exe`) manages the global registration and processing of `Win + Ctrl + F4`. When there is no active window context belonging to the current desktop, Explorer's internal shell input router fails to attribute the synthetic keystroke to an active virtual desktop, silently discarding the keystroke.

### 2.2 Why Navigating Away and Back Restores Functionality
When the user switches to Desktop 1 (`go work 1`), an active window on Desktop 1 receives foreground focus. When the user switches back to Desktop 2 (`go work 2`), the desktop switch routine calls `windll.user32.AllowSetForegroundWindow(ASFW_ANY)` and invokes the virtual desktop manager. This action informs the shell of the active desktop state. Subsequent `SendInput` events for `Win + Ctrl + F4` are then processed by Explorer as expected.

### 2.3 Cross-Library Evaluation: PyVDA vs WinVDA
This limitation is not unique to `winvda`. The identical behavior occurs under `pyvda` because:
* `close work` in Caster has never executed library code. It relied entirely on synthetic keystrokes.
* Neither `pyvda` nor `winvda` is invoked during `Key("wc-f4")`.
* Both libraries wrap the underlying Windows COM interface `IVirtualDesktopManagerInternal`.
* Both libraries expose a programmatic desktop removal method:
  * `pyvda`: `VirtualDesktop.remove(fallback=None)`
  * `winvda`: `winvda.remove_desktop(target, fallback=None)`

Relying on synthetic keystrokes (`Key("wc-f4")`) introduces an inherent race condition whenever the desktop has zero application windows.

---

## 3. Proposed Solution

Replace the synthetic keystroke simulation with direct COM desktop destruction via `winvda.remove_desktop()`. 

Direct COM invocation on `IVirtualDesktopManagerInternal::RemoveDesktop(p_destroy, p_fallback)` operates out-of-band:
* It does not depend on window focus, keyboard layout, or `SendInput`.
* It removes the current desktop deterministically even when zero windows exist.
* It routes through `castervoice.lib.printer.out` to provide feedback in the console and HUD.

### 3.1 Implementation Steps

#### Step 1: Add programmatic removal to `windows_virtual_desktops.py`
In `castervoice/lib/windows_virtual_desktops.py`, implement `close_current_workspace()`:

```python
def close_current_workspace():
    """Remove the active virtual desktop and fall back to the adjacent desktop."""
    try:
        desktops = winvda.get_desktops()
        if len(desktops) <= 1:
            printer.out("Only one workspace exists; cannot close.")
            return

        cur = winvda.get_current_desktop()
        fallback_number = cur.number - 1 if cur.number > 1 else 2
        printer.out(f"Closing workspace {cur.number} ('{cur.name}'), switching to {fallback_number}")
        winvda.remove_desktop(cur.id, fallback_number)
    except Exception as e:
        printer.out(f"Failed to close workspace: {e}")
```

Also modernize `close_all_workspaces()` to use `winvda.remove_desktop()` instead of looping `Key("wc-f4")`:

```python
def close_all_workspaces():
    """Remove all auxiliary virtual desktops, keeping only desktop 1."""
    try:
        desktops = winvda.get_desktops()
        if len(desktops) <= 1:
            printer.out("Only one desktop exists; nothing to close.")
            return

        primary = desktops[0]
        for d in reversed(desktops[1:]):
            winvda.remove_desktop(d.id, primary.id)
        winvda.switch_desktop(primary.id)
        printer.out("Closed all auxiliary workspaces.")
    except Exception as e:
        printer.out(f"Failed to close all workspaces: {e}")
```

#### Step 2: Expose in `virtual_desktops.py`
In `castervoice/lib/virtual_desktops.py`, export `close_current_workspace()`:

```python
if sys.platform == "win32":
    from .windows_virtual_desktops import (
        close_current_workspace,
        ...
    )
else:
    def close_current_workspace():
        _not_implemented()
```

#### Step 3: Update `window_mgmt_rule.py`
In `castervoice/rules/core/navigation_rules/window_mgmt_rule.py`, bind the rule to the Python function:

```python
# Workspace management
"show work [spaces]":
    R(Key("w-tab")),
"(create | new) work [space]":
    R(Key("wc-d")),
"close work [space]":
    R(Function(virtual_desktops.close_current_workspace)),
"close all work [spaces]":
    R(Function(virtual_desktops.close_all_workspaces)),
```

---

## 4. Verification Plan

1. **Empty Desktop Test:**
   * Create workspace 2 via `new work`.
   * Open Waterfox or Chrome on workspace 2.
   * Close the browser window.
   * Speak `close work`.
   * Verify that workspace 2 closes immediately, focus returns to workspace 1, and HUD logs: `Closing workspace 2 ('Desktop 2'), switching to 1`.

2. **Sole Remaining Desktop Guard:**
   * On workspace 1 with no other desktops, speak `close work`.
   * Verify that the desktop is preserved and HUD displays: `Only one workspace exists; cannot close.`

3. **Close All Desktops Test:**
   * Create 3 workspaces.
   * Speak `close all work`.
   * Verify that desktops 3 and 2 are removed cleanly, returning the user to desktop 1 without dropped keystrokes.
