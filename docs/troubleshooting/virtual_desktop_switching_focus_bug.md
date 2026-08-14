[ 🏠 Docs Home ](../README.md) › [ 📁 Troubleshooting ](../README.md#troubleshooting--diagnostics) › **Virtual Desktop Switching Focus Bug**

---

# Virtual Desktop Switching Focus Bug

## Overview
This document tracks a known focus bug encountered when switching between virtual desktops. This issue is entirely separate from the LexiconCode window switching functionality.

It primarily occurs when using `pyvda` in conjunction with the standard window management rules (not the LexiconCode fork) to switch virtual desktops and focus an application simultaneously.

## The Bug
When attempting to switch to a different virtual desktop and focus on a specific application, the focus mechanism sometimes fails.

**Observed Behavior:**
1. The user is on Workspace A.
2. The user has an application (e.g., LibreOffice Calc) open on Workspace B.
3. The user issues a command to switch to Workspace B
4. The system switches to Workspace B.
5. However, instead of the previously focused application (LibreOffice Calc) receiving focus, its taskbar icon begins flashing orange. 
6. Nothing appears to be actively focused on the new workspace.

## Details
* **Trigger:** Switching virtual workspaces.
* **Symptoms:** The previously focused application fails to pull to the foreground, resulting in a flashing taskbar icon instead.
* **Suspected Components:** This may be a race condition or interaction quirk between the Windows `SetForegroundWindow` API, virtual desktop transitions (via `pyvda`), and the timing of the window management rule execution.

This issue requires further investigation to determine a reliable workaround or fix for cross-workspace focus transitions.
