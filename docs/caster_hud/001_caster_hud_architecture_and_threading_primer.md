# Caster Heads-Up Display (HUD): Architecture, Threading, and IPC Primer

This document provides an educational primer on the **Caster Heads-Up Display (HUD)**, explaining its process isolation, threading model, and Qt event architecture, and exploring how it achieves high performance in Python without hanging or blocking Caster's recognition loop.

---

## 1. Overview & Purpose of the Caster HUD

The Caster HUD (`castervoice/asynch/hud.py`) is an on-screen, translucent, always-on-top GUI overlay. It provides speech recognition users with instant visual feedback:
* Recently recognized voice commands and execution history.
* Engine status and microphone sleeping/active modes.
* Interactive rule hints and command reference popups (`RulesWindow`).

---

## 2. Why the HUD Never Hangs or Blocks Caster

A common concern when building desktop overlays in Python is: *Will a heavy GUI or slow rendering loop freeze speech recognition or make the UI sluggish?*

The Caster HUD avoids all threading deadlocks and speech stalls through a **three-tier decoupled architecture**:

```
 ┌──────────────────────────────────────┐             ┌────────────────────────────────────────────────────────┐
 │      Caster Main Engine Process      │             │                    Caster HUD Process                  │
 │   (Dragonfly / Kaldi / Recognition)  │             │               (PySide2 / Qt GUI Application)           │
 └──────────────────┬───────────────────┘             └───────────────────────────┬────────────────────────────┘
                    │                                                             │
                    │ XML-RPC Call (Localhost)                                    │
                    ▼                                                             │
        ┌───────────────────────┐                                                 │
        │ `Communicator().send` │                                                 │
        └───────────┬───────────┘                                                 │
                    │                                                             │
                    └─────────────────────► ┌───────────────────────────┐         │
                                            │ Background Thread (Daemon)│         │
                                            │   SimpleXMLRPCServer      │         │
                                            └─────────────┬─────────────┘         │
                                                          │                       │
                                                          │ `postEvent(...)`      │
                                                          ▼                       │
                                            ┌───────────────────────────┐         │
                                            │   Main GUI Thread (Qt)    │◄────────┘
                                            │     `QApplication`        │
                                            │   (Event Loop / Paint)    │
                                            └───────────────────────────┘
```

### Pillar 1: Full OS Process Isolation
* The HUD does **not** run as a thread inside the speech recognition engine.
* It is launched as a completely separate OS process (`py -3.10 castervoice/asynch/hud.py`).
* If the HUD encounters a graphical delay, garbage collection pause, or crash, Caster's core voice recognition engine is completely isolated and continues executing uninterrupted.

### Pillar 2: Background XML-RPC Server
* Inside the HUD process, a background thread runs `SimpleXMLRPCServer` (`server_thread.daemon = True`) listening on a local port.
* When Caster finishes recognizing a command, it fires a lightweight, non-blocking network packet to `http://127.0.0.1:<port>`.

### Pillar 3: Asynchronous Qt Event Posting (`postEvent`)
In GUI programming (Qt, WPF, Win32), modifying UI widgets directly from a background thread causes crashes and race conditions.
* The XML-RPC background thread **never touches Qt widgets directly**.
* Instead, it encapsulates the message in an `RPCEvent` and calls:
  ```python
  QtCore.QCoreApplication.postEvent(self, RPCEvent(SEND_COMMAND_EVENT, text))
  ```
* `postEvent` is thread-safe and non-blocking: it appends the message to Qt's event queue and returns instantly.
* The main Qt GUI thread processes the event during its next frame paint, appending the HTML-formatted text to `self.output`.

---

## 3. Window Attributes & Desktop Focus Management

To serve as an unobtrusive heads-up display, the HUD configures specific Qt window flags:

1. **`WindowStaysOnTopHint` (`0x00040000`):** Ensures the HUD remains visible above full-screen browsers, IDEs, and office tools.
2. **`FramelessWindowHint` (`0x00000800`):** Strips standard OS window borders, title bars, and minimize buttons for a clean HUD aesthetic (press `Key_T` to toggle borders for moving/resizing).
3. **`NoFocus` (`0x00000000`):** Crucially prevents mouse clicks or text renders on the HUD from stealing active keyboard focus away from the application you are actively dictating into.

---

## 4. Performance: Why Python + Qt is Extremely Fast

Even though Caster is written in Python, the HUD uses near-zero CPU:
* **C++ Engine:** PySide2 / PyQt is a Python wrapper around native C++ Qt. All text layout, geometry calculation, and GPU window composition are executed in compiled C++/DirectX/OpenGL.
* **Event-Driven Sleep:** When no new speech commands are received, the Qt event loop enters a native OS wait state (`GetMessage` / `MsgWaitForMultipleObjectsEx`), consuming **0.0% CPU**.

---

## 5. Future Opportunities & Architectural Integration

As we advance the **Active Desktop Context Engine (ADCE)**, the HUD architecture offers exciting evolution points:

1. **System Tray Integration (`QSystemTrayIcon`):**
   * Embed a persistent tray icon with right-click menus to quickly toggle HUD visibility, switch recognition engines, or view active context streams.
2. **Real-Time Context Indicator:**
   * The HUD can subscribe to the ADCE state stream (via MCP or local IPC) to display a subtle header badge:
     `[Workspace: Main | Active Tab: Documentation]`.
3. **Translucent Modern Styling (QML / CSS):**
   * Upgrading the HUD to modern frosted-glass aesthetics (Windows 11 Acrylic / Mica materials) using Qt stylesheets.
