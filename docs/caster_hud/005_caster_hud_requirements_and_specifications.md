[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](001_caster_hud_architecture_and_threading_primer.md) › **005: Requirements, Feature Matrix & Technical Specifications**

---

# 005 — Caster Heads-Up Display: Requirements, Feature Matrix & Technical Specifications

**Document ID**: `CASTER-DOC-HUD-005`  
**Status**: Definitive Single Source of Truth (SSoT) & Technical Specifications  
**Target Subsystem**: `castervoice/asynch/hud/`, `castervoice/asynch/hud_support.py`, `castervoice/lib/settings.py`  
**Authors**: Antigravity Principal Architecture Team (Pair Programming with Amir Farhadi)  

---

## 1. Purpose & Scope

This document serves as the **Single Source of Truth (SSoT)** for the Caster Heads-Up Display (HUD). It defines the functional requirements, architectural invariants, visual indicators, user interactions, keyboard shortcuts, context menus, and backward compatibility contracts across all supported operating systems and Python environments.

---

## 2. Master Feature Matrix

| ID | Capability / Feature | Default | Description & Specifications |
| :--- | :--- | :--- | :--- |
| **REQ-01** | **Dynamic Border Status Glow** | `true` | Reactive outer border: 🟢 **Green** (Listening/Awake), 🔴 **Red** (Sleeping/Off), 🟡 **Amber** (Drag Mode 'D'), 🔵 **Blue** (Window Focus). |
| **REQ-02** | **Safety State Priority** | `Enforced` | $\text{Mic State (Red/Green)} \succ \text{Drag Mode (Amber)} \succ \text{Window Focus (Blue)}$. Focus never conceals a sleeping microphone. |
| **REQ-03** | **Ultra-Compact Overlay Mode** | Supported | Supports slim 25px–40px heights above the taskbar with descender-safe (`g`, `y`, `p`, `q`) typography and zero line clipping. |
| **REQ-04** | **Title Bar / Frameless Toggle** | `frameless=true` | Press `'T'` or utter `"caster hud border toggle"` to switch between framed window and borderless floating overlay. |
| **REQ-05** | **Drag Mode & Arrow Nudging** | `'D'` Hotkey | Press `'D'` or utter `"caster hud drag toggle"` to enable click-anywhere dragging and 1px (10px with Shift) arrow-key nudging. Amber border indication. |
| **REQ-06** | **Right-Click Context Menu** | Supported | Right-clicking anywhere on the HUD opens a complete context menu: Verbose Mode, Rules Strip, ADCE Strip, Themes, Profiles, Clear, Help, Exit. |
| **REQ-07** | **Active Rules Tree Inspector** | Voice/Menu | Uttering `"show caster rules"` or menu action displays a modal window with active Dragonfly grammars, rules, and command specs. |
| **REQ-08** | **Commands Reference Dialog** | Voice/Menu | Uttering `"show caster help"` or menu action displays a styled command reference table with keyboard navigation (`[Esc]`). |
| **REQ-09** | **System Tray Docking** | Configurable | If `system_tray=true`, closing or hiding the HUD minimizes it to the Windows Notification Area with a dynamic 2D vector badge icon. |
| **REQ-10** | **Modular Theming & Profiles** | Supported | Preset themes (`classic`, `frosted-dark`, `minimal-transparent`, `high-contrast`), user `.qss` loading, and named layout persistence (`[Enter]`, `[L]`, `[Del]`). |
| **REQ-11** | **Zero Recognition Latency IPC** | `< 0.001 ms` | `AsyncTelemetryPublisher` with drop-oldest eviction policy (`queue.Queue(maxsize=1024)`) guarantees zero speech thread blocking. |
| **REQ-12** | **Hardware DWM Resizing** | `WM_NCHITTEST` | Native Win32 hardware border resizing with 3px vertical margin (optimized for ultra-slim containers) and 6px horizontal margin. |
| **REQ-13** | **Contextual Rules Scoping & Global Fallback** | Enforced | Prevents active rules flood (30+ global rules). Displays only application-specific contextual rules (e.g. `[VS Code]`, `[IDE Terminal]`) when active, or `[Global Context]` when in a generic app/desktop. Excludes internal merger artifacts (`Repeater1`, `PreparedRule`). |
| **REQ-14** | **ADCE Dynamic Context Strip & Verbose Hierarchy** | Supported | Displays real-time ADCE telemetry (`🟢 ADCE`, `{Zone}`, `[Process]`, `📄 File`). Toggled via `"caster hud adce"`. `"caster hud verbose"` toggles Status Header + Rules Strip without modifying ADCE. |
| **REQ-15** | **Zero-Polling Event-Driven Focus Tracking** | `IFocusTracker` | Uses native `SetWinEventHook` (`EVENT_SYSTEM_FOREGROUND`, `EVENT_OBJECT_NAMECHANGE`) to update HUD on mouse clicks and Alt+Tab ($< 1\text{ ms}$) without waiting for speech. Modular abstract design for cross-platform extensibility. |

---

## 3. Keyboard Shortcuts & User Interactions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ HUD Direct Keyboard Shortcuts & Interactivity                                │
├──────────────┬──────────────────────────────────────────────────────────────┤
│ Key          │ Action / Functionality                                       │
├──────────────┼──────────────────────────────────────────────────────────────┤
│ 'T'          │ Toggle Title Bar vs. Frameless Floating Overlay              │
│ 'D'          │ Toggle Drag Mode (Window turns Amber, click & drag anywhere) │
│ Arrow Keys   │ Nudge window by 1px (or 10px with Shift) while in Drag Mode │
│ Escape       │ Exit Drag Mode / Close Modal Dialogs (Help, Rules, Profiles) │
│ Right-Click  │ Open HUD Context Menu (Verbose, Rules, ADCE, Themes, etc.)   │
│ [Enter]      │ Save Profile (when Profile Dialog is active)                 │
│ [L]          │ Load Selected Profile (when Profile Dialog is active)        │
│ [Del]        │ Delete Selected Profile (when Profile Dialog is active)      │
└──────────────┴──────────────────────────────────────────────────────────────┘
```

---

## 4. Voice Command Matrix

| Voice Command Phrase | Action / Subsystem Trigger |
| :--- | :--- |
| `"show caster hud"` | Display or raise HUD window without stealing OS focus |
| `"hide caster hud"` | Hide HUD window (or minimize to system tray if enabled) |
| `"clear caster hud"` | Flush current recognition and telemetry log history |
| `"caster hud verbose [toggle]"` | Toggle diagnostic panels (**Status Header** + **Active Rules Strip**) |
| `"caster hud (status \| header \| status bar) [toggle]"` | Toggle top status banner independently |
| `"caster hud (rules strip \| active rules \| rules) [toggle]"` | Toggle active contextual rules strip independently |
| `"caster hud (adce \| a d c e \| context engine) [toggle]"` | Toggle ADCE Dynamic Context strip independently |
| `"caster hud (border \| title bar \| frame) [toggle]"` | Toggle frameless floating overlay mode vs framed window |
| `"caster hud (drag \| move) [toggle]"` | Toggle interactive mouse and keyboard arrow drag mode |
| `"caster hud scroll [toggle]"` | Toggle log scrollbar visibility |
| `"caster hud font (increase \| bigger \| up)"` | Increase HUD font size by 1pt |
| `"caster hud font (decrease \| smaller \| down)"` | Decrease HUD font size by 1pt |
| `"caster hud font reset"` | Reset HUD font size to default (9pt) |
| `"caster hud theme [<theme_name>]"` | Set or cycle themes (`classic`, `frosted`, `minimal`, `high contrast`) |
| `"caster hud save profile"` | Open interactive Profile Manager dialog in Save mode |
| `"caster hud (load profile \| show profile)"` | Open interactive Profile Manager dialog in Load mode |
| `"show caster [hud] help"` | Open standalone commands reference modal dialog |
| `"show caster rules"` | Open active rules tree inspector modal dialog |

---

## 5. Cross-Version & Backward Compatibility Invariants

1. **Python Compatibility**:
   - Python 2.7 (Legacy NatLink / Dragon 15 compatibility).
   - Python 3.8 – 3.12+ (Modern standalone engines: Kaldi, Vosk, WSR).
   - *Rule*: Core libraries must use `.format()` and avoid Python 3.7+ exclusive syntax (bare `f-strings`, unpolyfilled `dataclass`, raw type annotations).
2. **Strict Qt Thread Boundary Isolation**:
   - Background threads (XML-RPC, socket listeners) must **NEVER** instantiate or manipulate `QWidget` instances directly.
   - All cross-thread invocations must use `QtCore.QCoreApplication.postEvent()` or Qt Signals (`QtCore.Signal(object)`).
