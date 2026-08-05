# Caster Core Engine UIA Usage (Educational Breakdown)

This document explores whether the `Caster` core source repository implements any hidden UIA, threading management, or advanced focus handling that differs from what we found in the Caster User Directory (`caster_user_content`).

## 1. Findings on UIA and Accessibility APIs
After thoroughly scanning the core Caster repository for libraries such as `pywinauto`, `uiautomation`, `comtypes`, and `IAccessible`, **we found zero results.**

The core Caster engine does not natively use UIA or manage COM threading apartments (STA/MTA). All UIA automation, UI tree traversal, and complex OS interactions currently exist exclusively in user-space scripts (like `app_switcher.py`).

## 2. Findings on Threading
The core engine makes heavy use of Python's `threading` library, but specifically within its `asynch` module (which handles separate RPC servers for asynchronous UI overlays like Homunculus, Grids, and Legion). It does not dedicate any threads to OS-level accessibility polling or COM interactions.

## 3. Findings on Focus Stealing
While the user directory `app_switcher.py` has a massive 65-line function dedicated to OS bypasses and focus stealing (`AttachThreadInput` + Alt key injection), the core Caster repository has almost nothing. 

The only minor Win32 focus handling is a single call to `AllowSetForegroundWindow(ASFW_ANY)` in `windows_virtual_desktops.py`, and a commented-out call to `win32gui.SystemParametersInfo(win32con.SPI_SETFOREGROUNDLOCKTIMEOUT, 0, 1)`.

## Conclusion for Architecture Placement
The Caster core engine is completely devoid of UIA or advanced focus management. If we build the UIA Server into Caster, we will be introducing a completely new paradigm (COM MTA threading or an out-of-process UIA server) to the codebase, rather than hooking into an existing core system.

*(Research conducted under Wayfinder Ticket 008)*
