[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](001_caster_hud_architecture_and_threading_primer.md) › **002: System Tray Integration, Architectural Audit & Upstream PR Strategy**

---

# Caster Heads-Up Display (HUD): System Tray Integration, Architectural Audit & Upstream Contribution Strategy

This document provides a comprehensive architectural audit and engineering guide for adding **Opt-in System Tray (Taskbar Notification Area) Minimization**, **Zero-Taskbar Tool Window Styling**, and **Voice vs. GUI Lifecycle Management** to the Caster Heads-Up Display (`castervoice/asynch/hud.py`). It covers historical context, built-in voice commands, window manager behavior, resource footprint on low-spec machines, and the isolated development workflow required to protect live accessibility environments.

---

## 1. Executive Summary & Objectives

The primary goal is to provide a non-breaking, **opt-in setting in `settings.toml`** that allows the Caster HUD to exist as a clean heads-up overlay with **zero footprint on the Windows taskbar**, docking cleanly into the Windows System Tray (Taskbar Notification Area).

### Core Requirements
1. **100% Backward Compatible (Opt-In Toggle)**:
   * By default (`[hud] system_tray = false`), Caster HUD runs in standard window mode with standard taskbar behavior.
   * When enabled (`[hud] system_tray = true`), the HUD switches to `Qt.Tool` (zero taskbar clutter) and activates the `QSystemTrayIcon`.
2. **System Tray Integration (`QSystemTrayIcon`)**: Provides visual status and convenient mouse controls (Show/Hide, Clear, Exit) in the notification area.
3. **Clean Process Termination**: Clicking the window's `X` button or selecting **"Exit"** from the tray menu terminates the process completely, leaving zero ghost processes in memory.
4. **Reliable Auto-Scrolling**: Fixed cursor tracking so new voice recognitions always scroll to the bottom (`TEXT_CURSOR_END`) regardless of mouse clicks.
5. **Zero Impact on Active Accessibility Setup**: Developed on an isolated branch branched strictly off `upstream/master` (`dictation-toolbox/Caster`), without leaking personal modifications, local rules, or custom batch scripts.
6. **Cross-Platform & Multi-Qt Compatibility**: Works seamlessly with both `PySide2` (Qt5) and `PySide6` (Qt6) via `castervoice.lib.qt`.
7. **Low Resource Footprint**: Negligible memory/CPU overhead to ensure responsiveness on older (2007–2009 Core 2 Duo) hardware.
8. **Self-Contained 2D Vector Badge Icon**: High-DPI icon generated dynamically via `QPainter` without external asset dependencies or emoji reliance.

---

## 2. Built-in Voice Commands & Window State (Where Does it Go When Hidden?)

In `castervoice/rules/core/utility_rules/caster_rule.py`, Caster defines five built-in voice commands:

```python
"show caster hud":   R(Function(show_hud), rdescript="Show the HUD window"),
"hide caster hud":   R(Function(hide_hud), rdescript="Hide the HUD window"),
"clear caster hud":  R(Function(clear_hud), rdescript="Clear output the HUD window"),
"show caster rules": R(Function(show_rules), rdescript="Open HUD frame with active rules"),
"hide caster rules": R(Function(hide_rules), rdescript="Hide the list of active rules"),
```

### What Happens When You Say `"hide caster hud"`?

1. **In Original Master (Without System Tray)**:
   * `hide_hud()` sends an XML-RPC message to the HUD process (`self.hide()`).
   * In the Windows Desktop Window Manager (DWM), hiding a window removes it from the screen **and** removes its taskbar button.
   * **Where did it go?** The process is still running invisibly in the background on port 8338. However, because there is no system tray icon, there is **zero visual indication** on your computer that the HUD exists, and **zero mouse control** to restore it. If speech recognition fails, the user cannot bring it back without re-opening Caster.

2. **In New System Tray Version (With `QSystemTrayIcon`)**:
   * Saying `"hide caster hud"` still calls `self.hide()` (identical voice behavior).
   * But now, it docks cleanly into the **System Tray** (the blue `"C"` badge).
   * **You now have multi-modal control**:
     * Voice: `"show caster hud"` / `"hide caster hud"`.
     * Mouse: Left-click tray icon to restore; right-click for context menu (Show/Hide, Clear, Exit).

---

## 3. Configuration Schema (`settings.toml`)

In `settings.toml` (under `castervoice/lib/settings.py`):

```toml
[hud]
system_tray = false  # Set to true to dock HUD into system tray with zero taskbar presence
```

When `hud.py` starts:
* `use_tray = settings.settings(["hud", "system_tray"], default_value=False)`
* If `False`: `flags = WINDOW_STAYS_ON_TOP_HINT` (exact original master behavior).
* If `True`: `flags = WINDOW_STAYS_ON_TOP_HINT | TOOL_WINDOW_HINT` and `setup_tray_icon()` is called.

---

## 4. Window Manager Architecture & Lifecycle

```
                                    User Interaction
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    │                                             │
             Click Tray / Say "hide"                        Click Close `X`
                    │                                     (or Tray -> "Exit")
                    ▼                                             │
       ┌──────────────────────────┐                               ▼
       │     `self.hide()`        │                  ┌──────────────────────────┐
       │                          │                  │    `closeEvent(...)`     │
       │ • Hides overlay          │                  │    `xmlrpc_kill()`       │
       │ • Zero taskbar presence  │                  └────────────┬─────────────┘
       │ • Docks into Tray        │                               │
       └──────────────────────────┘                               ▼
                                                     ┌──────────────────────────┐
                                                     │   `self.tray_icon.hide()`│
                                                     │   `QApplication.quit()`  │
                                                     │   `server.shutdown()`    │
                                                     │                          │
                                                     │ • Kills Process Cleanly  │
                                                     └──────────────────────────┘
```

---

## 5. Text Scrolling Hardening

In Qt's `QTextEdit`:
* If regular speech messages arrive, resetting `cursor.movePosition(TEXT_CURSOR_END)` on every append ensures the view never stays anchored on a previous mouse-click location:

```python
self.output.append(formatted_text)
cursor = self.output.textCursor()
cursor.movePosition(TEXT_CURSOR_END)
self.output.setTextCursor(cursor)
self.output.ensureCursorVisible()
```

---

*Document compiled for Caster Accessibility Architecture Ledger.*