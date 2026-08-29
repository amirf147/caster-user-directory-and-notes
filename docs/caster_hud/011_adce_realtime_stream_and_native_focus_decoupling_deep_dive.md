[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](005_caster_hud_requirements_and_specifications.md) › **011: ADCE Real-Time Stream & Native Focus Decoupling Deep Dive**

---

# 011 — ADCE Real-Time Stream & Native Focus Decoupling Deep Dive

**Document ID**: `CASTER-DOC-HUD-011`  
**Status**: Real-Time Micro-Context Integration & SSoT Architecture Specification  
**Target Subsystem**: `castervoice/asynch/hud/core/adce_tracker.py`, `castervoice/asynch/hud/ui/widgets/`  
**Authors**: Antigravity Principal Architecture Team (Pair Programming with Amir Farhadi)  

---

## 1. Executive Summary & Problem Diagnosis

When developing with voice controls across IDEs, developers frequently switch focus between sub-elements inside the **same** application window:
- Code Editor Buffer (`monaco-editor`)
- Integrated Terminal (`xterm-screen`)
- AI Chat / Composer Panel
- Git Commit Message Box (`scm-editor`)

### The "Taskbar Click" Phenomenon
Previously, clicking between the editor and terminal inside VS Code/Antigravity failed to update the HUD until the user clicked the Windows taskbar or switched to another application.

**Why did this happen?**
1. **The Native OS Window Hook (`Win32WindowFocusTracker`)**: Listens to OS `EVENT_SYSTEM_FOREGROUND` and `EVENT_OBJECT_NAMECHANGE`. Because clicking between panes inside the same Electron window does not change the top-level `HWND` or window title, Windows emits **zero** OS window events.
2. **Missing Real-Time Telemetry Link**: ADCE daemon detected the sub-window zone change via UI Automation (UIA), but Caster HUD was only publishing updates when the OS window hook fired. Clicking the taskbar forced an OS window switch, which flushed the pending ADCE zone update to the HUD.

---

## 2. The Architectural Solution: Decoupled Dual-Observer Pipeline

To achieve instant (<10 ms) updates for both top-level window switches and internal sub-pane clicks:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OBSERVER 1: NATIVE OS WINDOW HOOKS                       │
│  • Component: Win32WindowFocusTracker (SetWinEventHook 0x0003 & 0x800C)     │
│  • Target Scope: Top-Level Foreground Process & Window Title                │
│  • Primary Consumer: StatusBarWidget (Top Header)                            │
│  • Visual Display: [LISTENING] [code] [VS Code - main_window.py]            │
│  • Decoupling Invariant: ZERO dependency on ADCE; operates natively.         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    OBSERVER 2: REAL-TIME ADCE SSE STREAM                    │
│  • Component: AdceTracker (Persistent SSE Client on Port 8424)               │
│  • Target Scope: Sub-Window Zones ({IntegratedTerminal}, {EditorCodeBuffer}) │
│  • Primary Consumer: AdceBarWidget (ADCE Dynamic Context Strip)             │
│  • Visual Display:                                                          │
│    - When Connected: 🟢 ADCE {IntegratedTerminal} [code] 📄 main_window.py │
│    - When Offline:   ⚪ ADCE [ADCE is not connected] (in muted gray)        │
│  • Real-Time Dispatch: Emits DesktopContextEvent & ActiveRulesEvent on       │
│    EVERY sub-pane click inside the same IDE window with zero delay.         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Clear Panel Role Matrix

| UI Panel | Scope & Data Source | Online Rendering | Offline Rendering |
| :--- | :--- | :--- | :--- |
| **Status Bar Header** (`StatusBarWidget`) | **Native OS & Speech Engine** (`SetWinEventHook`) | `[LISTENING]` `[code]` `[main.py]` | Same (Independent of ADCE) |
| **ADCE Dynamic Strip** (`AdceBarWidget`) | **ADCE Micro-Context** (`AdceTracker` on port 8424) | `🟢 ADCE` `{IntegratedTerminal}` `[code]` `📄 main.py` | `⚪ ADCE` `[ADCE is not connected]` (Gray) |
| **Active Rules Strip** (`ActiveRulesBarWidget`) | **Dragonfly Grammar Context** (`AppContext` & `FuncContext`) | `[VS Code]`, `[IDETerminal]` | `[VS Code]` (or `[Global Context]` on Desktop) |

---

## 4. Implementation Details

1. **`AdceTracker` (`castervoice/asynch/hud/core/adce_tracker.py`)**:
   - Maintains non-blocking HTTP SSE connection to `http://127.0.0.1:8424/sse`.
   - Ingests JSON snapshots and triggers `_on_adce_context_changed` whenever `zone`, `file`, `process`, or `title` changes.
   - Pushes `DesktopContextEvent` and `ActiveRulesEvent` over async IPC instantly.
2. **`StatusBarWidget` (`castervoice/asynch/hud/ui/widgets/status_bar.py`)**:
   - Removed `{SemanticZone}` from the top status header to prevent polluting the native OS title bar.
3. **`AdceBarWidget` (`castervoice/asynch/hud/ui/widgets/adce_bar.py`)**:
   - Explicitly displays `⚪ ADCE` `[ADCE is not connected]` when the ADCE daemon is closed or stopped.

---

*Recorded in `docs/caster_hud/011_adce_realtime_stream_and_native_focus_decoupling_deep_dive.md`.*
