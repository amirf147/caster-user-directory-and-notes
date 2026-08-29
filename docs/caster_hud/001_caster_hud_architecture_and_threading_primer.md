[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](005_caster_hud_requirements_and_specifications.md) › **001: Architecture & Threading Primer**

---

> [!NOTE]
> **Document Status**: *Foundational Baseline & Historical Architecture Primer*.  
> For the authoritative, active specifications and runtime contracts, refer to **[005: Requirements, Feature Matrix & Technical Specifications](005_caster_hud_requirements_and_specifications.md)**.

# 001 — Caster Heads-Up Display: Architecture, Threading & IPC Primer

**Document ID**: `CASTER-DOC-HUD-001`  
**Status**: Foundational Baseline Architecture  
**Target Subsystem**: `castervoice/asynch/hud.py`, `castervoice/asynch/hud/`  

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
                    │ XML-RPC / ndjson Socket (Localhost)                         │
                    ▼                                                             │
        ┌───────────────────────┐                                                 │
        │ AsyncTelemetryPublisher│                                                │
        └───────────┬───────────┘                                                 │
                    │                                                             │
                    └─────────────────────► ┌───────────────────────────┐         │
                                            │ Background Thread (Daemon)│         │
                                            │   IpcServer / XML-RPC     │         │
                                            └─────────────┬─────────────┘         │
                                                          │                       │
                                                          │ `SignalBridge.emit()` │
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

### Pillar 2: Background Network Dispatch
* Inside the HUD process, background worker threads run the `IpcServerThread` (`port 8339`) and `SimpleXMLRPCServer` (`port 8338`).
* When Caster finishes recognizing a command, it fires non-blocking packets over localhost sockets.
