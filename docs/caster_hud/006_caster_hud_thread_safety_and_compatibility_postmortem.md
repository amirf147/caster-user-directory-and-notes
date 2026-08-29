[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](001_caster_hud_architecture_and_threading_primer.md) › **006: Thread Safety, Event Loop Deadlocks & Port Collision Post-Mortem**

---

# 006 — Caster Heads-Up Display: Thread Safety, Event Loop Deadlocks & Port Collision Post-Mortem

**Document ID**: `CASTER-DOC-HUD-006`  
**Status**: Comprehensive Root Cause Analysis & Post-Mortem Engineering Report  
**Target Subsystem**: `castervoice/asynch/hud.py`, `castervoice/asynch/hud/ui/main_window.py`, `castervoice/asynch/hud/core/constants.py`  
**Authors**: Antigravity Principal Architecture Team (Pair Programming with Amir Farhadi)  

---

## 1. Executive Summary

During hands-on live voice testing of the HUD subsystem:
1. **Symptom 1**: Uttering `"show caster help"` or `"show caster rules"` did not display the expected dialog and caused the entire speech engine / HUD to lock up. Subsequent voice commands (`"caster on"`, `"caster sleep"`) failed to update the visual border color.
2. **Symptom 2**: Pressing `'D'` on the keyboard did not activate Drag Mode or change the border to Amber.
3. **Symptom 3**: The right-click context menu on the floating HUD window was missing.

This post-mortem report documents the **deep root cause analysis (RCA)**, the underlying protocol and threading mechanics, the engineering solutions implemented, and verification steps.

---

## 2. Deep Root Cause Analysis (RCA)

### RCA-1: Dual Protocol Port Collision (ndjson Socket vs. XML-RPC Server)
* **The Collision**:
  - In `castervoice/lib/settings.py` and `communication.py`, Caster's legacy XML-RPC communication registry designates port `8338` for the HUD communicator (`Communicator().com_registry["hud"] = 8338`).
  - In our initial implementation, `DEFAULT_HUD_PORT` was also set to `8338` for the new high-performance asynchronous ndjson telemetry stream.
  - In `castervoice/asynch/hud.py`, the launcher contained the guard `if rpc_port != ipc_port:`. Because both resolved to `8338`, the condition evaluated to `False`, and **the XML-RPC server was never started**.
  - Instead, the raw `IpcServerThread` bound port `8338` directly.
* **The Freeze Mechanism**:
  - When the user uttered `"show caster help"`, Dragonfly's `Function(show_hud_help)` in `caster_rule.py` executed `hud = control.nexus().comm.get_com("hud")` and called `hud.show_help()`.
  - Python's standard `xmlrpc.client.ServerProxy` connected to `http://127.0.0.1:8338` and transmitted an HTTP POST request (`POST /RPC2 HTTP/1.1\r\nContent-Type: text/xml...`).
  - `IpcServerThread`, expecting newline-delimited JSON (`ndjson`), received the raw HTTP headers, failed to parse them as JSON, and held the TCP connection open without returning an HTTP XML-RPC response.
  - Because XML-RPC calls in Dragonfly rules are synchronous, **Dragonfly's main speech recognition thread blocked indefinitely on `socket.recv()`**, freezing Caster's speech engine and stopping all subsequent speech processing (`"caster sleep"`, `"caster on"`).

### RCA-2: Background Thread QWidget Instantiation
* **The Thread Invariant Violation**:
  - In XML-RPC methods, functions were invoking `window.show_help_dialog()` and `window.show_rules_dialog()` directly from the background XML-RPC server thread.
  - In Qt/PySide, instantiating or showing `QWidget` instances from a non-GUI thread violates the single-threaded GUI invariant, causing deadlocks in the Qt event pump and silent GUI freezes.

### RCA-3: Keyboard Focus Interception & Key Delegation
* **The Focus Mechanism**:
  - `TelemetryLogWidget` had `setFocusPolicy(Qt.NoFocus)`, preventing keyboard events like `'D'` (Toggle Drag) or `'T'` (Toggle Frameless) from reaching `MainWindow.keyPressEvent()`.
  - Additionally, `DragHandler` toggled its internal state without triggering a state reduction or notifying `BorderController`, preventing the border from transitioning to Amber.

---

## 3. Engineering Solutions Implemented

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Dedicated Dual-Port Architecture                                         │
│    • Port 8338: Legacy XML-RPC Server (SimpleXMLRPCServer)                  │
│      Handles: show_hud, hide_hud, show_help, show_rules, set_theme, ping   │
│    • Port 8339: Async ndjson Telemetry Stream (IpcServerThread)             │
│      Handles: High-cadence recognition events & telemetry stream            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. Thread-Safe Qt SignalBridge                                              │
│    • All XML-RPC endpoints emit typed Qt Signals on SignalBridge            │
│    • Qt automatically marshals calls onto the GUI thread via QueuedConn     │
│    • 100% of widget creation occurs safely on the Qt main GUI thread        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. ClickFocus & Key Forwarding                                              │
│    • TelemetryLogWidget uses ClickFocus and forwards keys to MainWindow     │
│    • Pressing 'D' toggles DragModeEvent and turns border AMBER (#f39c12)    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. Unified Right-Click Context Menu                                         │
│    • CustomContextMenu on log_widget provides: Active Rules, Help, Themes,  │
│      Profiles, Border Toggle [T], Drag Mode [D], Clear, and Exit           │
├─────────────────────────────────────────────────────────────────────────────┤
│ 5. Python 2.7 / 3.x Syntax & Inheritance Compatibility                      │
│    • Replaced all raw f-strings with .format()                              │
│    • Used explicit super(ClassName, self).__init__() throughout             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Verification & Testing

1. **In-Process XML-RPC Command Verification (`scratch/test_hud_run.py`)**:
   - Tested 8 consecutive XML-RPC calls (`ping`, `show_help`, `show_rules`, `toggle_drag`, `set_theme`, `send`, `hide_rules`, `hide_help`) against live running HUD process:
   - **Result**: All 8 operations completed successfully in $< 5\text{ seconds}$ with zero exceptions, zero freezes, and clean termination.
2. **Automated Unit Test Suite (`tests/test_hud_core.py`, `tests/test_hud_ipc.py`, `tests/test_hud_ui.py`)**:
   - 13 automated tests covering state transitions, priority border hierarchy, ndjson framing, queue drop-oldest eviction, and Qt dialog lifecycle:
   - **Result**: 13/13 Passed (100% OK).

*Recorded in `docs/caster_hud/006_caster_hud_thread_safety_and_compatibility_postmortem.md`.*
