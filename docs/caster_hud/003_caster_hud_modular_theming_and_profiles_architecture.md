[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](001_caster_hud_architecture_and_threading_primer.md) › **003: Modular Architecture, Themes, Profiles, Drag Mode & Frameless Resizing**

---

# 003 — Caster Heads-Up Display: Modular Architecture, Themes, Profiles, Drag Mode & Frameless Resizing

**Document ID**: `CASTER-DOC-HUD-003`  
**Status**: Implemented & Verified on `feat/hud-modular-theming`  
**Target Upstream Branch**: `dictation-toolbox/Caster:master`  

---

## 1. Executive Summary & Design Vision

This document details the architectural evolution of the Caster Heads-Up Display (HUD) from a rigid, monolithic GUI into a **modular, object-oriented subsystem** featuring:
1. **QSS Theming Engine**: Preset themes (`classic`, `frosted-dark`, `minimal-transparent`, `high-contrast`) and user theme loader (`~/.caster/themes/*.qss`).
2. **Interactive Profile Manager Dialog (`ProfileDialog`)**: Accessible GUI dialog for saving, loading, and deleting named profiles with intuitive hotkeys (`[Enter]`, `[L]`, `[Del]`, `[Esc]`).
3. **Dedicated Drag Mode**: Accidental-click protection with hotkey (`'D'`), voice toggling (`"caster hud drag toggle"`), and **keyboard arrow key nudging** (`Left`, `Right`, `Up`, `Down` with `Shift` 10px step).
4. **Frameless Edge Resizability**: Dynamic edge and corner resize grips with bidirectional resize cursors (`SizeHorCursor`, `SizeVerCursor`, `SizeFDiagCursor`, `SizeBDiagCursor`) when frameless.
5. **Geometry Stabilization**: Exact dimension preservation across dynamic title bar (`'T'`) and theme switching.
6. **Taskbar & Multi-Monitor Compatibility**: Zero-margin compact frameless overlay support (e.g. `311x39` over transparent taskbars) with periodic stay-on-top keepalive.

---

## 2. Object-Oriented Subsystem Architecture

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                         CASTER HUD SUBSYSTEM                                │
 └─────────────────────────────────────────────────────────────────────────────┘
                                        │
     ┌─────────────────┬────────────────┼────────────────┬─────────────────┐
     ▼                 ▼                ▼                ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ HUDWindow    │ │ ThemeEngine  │ │ ProfileMgr   │ │ HelpWindow   │ │ ProfileDlg   │
├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│ • Main GUI   │ │ • Classic    │ │ • Named      │ │ • Standalone │ │ • Save [Ent] │
│ • Tray Icon  │ │ • Frosted    │ │   profiles   │ │ • Styled     │ │ • Load [L]   │
│ • Drag Mode  │ │ • Minimal    │ │ • TOML store │ │ • Tables     │ │ • Del [Del]  │
│ • Edge Resize│ │ • Contrast   │ │ • Geometry   │ │ • Searchable │ │ • Close [Esc]│
│ • Keepalive  │ │ • User .qss  │ │              │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 3. Voice & Hotkey Command Reference

### Window & Visibility Controls
- **`"show caster hud"`** &mdash; Opens or raises the HUD window.
- **`"hide caster hud"`** &mdash; Docks HUD into the system tray or hides the window.
- **`"clear caster hud"`** &mdash; Clears the HUD text history.
- **`"caster hud (border | title bar | frame) toggle"`** *(or press **'T'**)* &mdash; Toggles between framed (title bar) and frameless overlay while strictly locking position & size.
- **`"caster hud (drag | move) toggle"`** *(or press **'D'**)* &mdash; Toggles **Drag Mode**.
  - Click and drag **anywhere** inside the HUD to move it.
  - Use **Arrow Keys** (`Left`, `Right`, `Up`, `Down`) to nudge the window (hold `Shift` for 10px steps).
  - Press **`'D'`** or **`Esc`** to lock the HUD in place.
- **`"caster hud scroll toggle"`** &mdash; Toggles the vertical scrollbar.

### Themes & Appearance
- **`"caster hud theme"`** &mdash; Cycles sequentially through all available themes.
- **`"caster hud theme classic"`** &mdash; Applies the upstream classic theme.
- **`"caster hud theme (frosted | dark)"`** &mdash; Applies modern frosted dark acrylic theme.
- **`"caster hud theme (minimal | transparent)"`** &mdash; Applies floating semi-transparent text theme.
- **`"caster hud theme (high contrast | contrast)"`** &mdash; Applies pure black high-contrast theme.

### Font Controls
- **`"caster hud font (increase | bigger | up)"`** &mdash; Increases HUD font size by 1pt.
- **`"caster hud font (decrease | smaller | down)"`** &mdash; Decreases HUD font size by 1pt.
- **`"caster hud font reset"`** &mdash; Resets font size to default compact 9pt.

### Profiles & Layouts
- **`"caster hud save profile"`** &mdash; Opens the interactive **Profile Manager** dialog focused on saving the current layout (`[Enter]` to save).
- **`"caster hud (load profile | show profile | profile)"`** / **`"show caster [hud] profiles"`** &mdash; Opens the **Profile Manager** dialog to select and load a saved profile (`[L]` to load).

### Help & Documentation
- **`"show caster [hud] help"`** / **`"caster hud help"`** &mdash; Opens the standalone styled Help dialog (`[Esc]` to close).
- **`"hide caster [hud] help"`** &mdash; Closes the Help dialog.

---

## 4. Technical Gotchas & Edge Cases Solved

### A. Frameless Edge & Corner Resizability
* **Problem**: Setting `Qt.FramelessWindowHint` disables native OS window borders, making windows non-resizable unless custom mouse hit-testing is implemented.
* **Solution**: Implemented an edge margin hit-test (`_detect_edge`) in `HUDWindow` and an `eventFilter` on `output.viewport()`. Hovering within 6px of any border changes the cursor to `SizeHorCursor`, `SizeVerCursor`, `SizeFDiagCursor`, or `SizeBDiagCursor`, allowing resizing from all 8 directions even without a title bar.

### B. Drag Mode with Keyboard Nudging
* **Problem**: In standard frameless windows, clicking on text selects text instead of dragging, and taskbar overlays can be moved accidentally by random clicks.
* **Solution**: When Drag Mode is enabled (`'D'`), the event filter captures mouse presses across the entire viewport. Furthermore, Arrow Keys (`Left`, `Right`, `Up`, `Down`) allow precise pixel-by-pixel positioning with keyboard navigation.

### C. Confirmation-Driven Profile Management
* **Problem**: Dynamic voice dictation for profile names was error-prone due to background noise/misrecognitions inadvertently overwriting layouts.
* **Solution**: Saying `"caster hud save profile"` or `"caster hud load profile"` opens the graphical `ProfileDialog` with explicit `[Enter]` and `[L]` shortcuts, eliminating accidental overwrites.
