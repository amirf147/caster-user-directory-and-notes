# Caster UIA Usage (Educational Breakdown)

This document explores how the `caster` repository currently utilizes Microsoft UI Automation (UIA) and accessibility APIs, and why this design leads to instability in the main voice engine.

## 1. Existing UIA and Pywinauto Integration

Caster relies heavily on the `pywinauto` library (which wraps UIA and Win32 APIs) as its primary bridge to the OS. This is most prominent in `caster_user_content/util/app_switcher.py`.

Unlike NVDA, Terminator, or Dragonfly (which offload COM/UIA calls to dedicated background threads), **Caster executes all `pywinauto` calls synchronously on the main voice engine thread.**

When a voice command triggers an app switch, Caster executes:
```python
app = Application().connect(handle=handle)
app.window(handle=handle).set_focus()
```

## 2. The Core Problem: Synchronous STA Execution

Because Caster does not explicitly initialize its main thread as an MTA (Multi-Threaded Apartment) or manage a dedicated COM thread, it defaults to an **STA (Single-Threaded Apartment)**. 

When `pywinauto` makes a UIA COM call on an STA thread, it must cross process boundaries to communicate with the target application. If that target application is slow, unresponsive, or hanging, the COM call blocks. 

In a properly designed STA, a Windows Message Pump (`PumpMessages`) runs constantly to keep the COM channel alive and handle callbacks. However, Caster's main voice thread is busy processing audio and executing Python code—it is not spinning a dedicated Win32 message pump. 

**The Result:** The `pywinauto` call deadlocks. Because it is executing synchronously on the main thread, the entire Caster voice engine freezes and stops responding to voice commands until the target application recovers or the OS forcibly times out the COM call (which can take minutes).

## 3. Focus Stealing Hacks

Similar to Dragonfly, Caster has implemented aggressive workarounds for Windows focus-stealing prevention. In `app_switcher.py`, if `pywinauto` fails to set focus, Caster falls back to an "OS Bypass" using `AttachThreadInput` and Alt-key injection:

```python
# 5. OS Bypass: Thread Attachment + Alt Key Injection
fore_hwnd = win32gui.GetForegroundWindow()
fore_thread, _ = win32process.GetWindowThreadProcessId(fore_hwnd)
current_thread = win32api.GetCurrentThreadId()

win32process.AttachThreadInput(fore_thread, current_thread, True)
# Inject Alt key to bypass focus restrictions...
```

## 4. Conclusions for the Architecture Placement

Because Caster currently executes UIA synchronously on its main STA thread without a message pump, any new UIA features (like Tab Switching) will dramatically increase the frequency of deadlocks. 

To safely build UIA tab selection, we MUST move all UIA calls off the main Caster thread. This requires either:
1. Building an Out-of-Process UIA Server.
2. Building an In-Process MTA Daemon Thread (similar to NVDA's approach) that communicates with Caster asynchronously.

*(Research conducted under Wayfinder Ticket 006)*
