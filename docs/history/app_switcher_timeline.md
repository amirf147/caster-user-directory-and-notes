---
Status: Active
Last Updated: 2026-08-14
Canonical Blueprint: docs/architecture/app_switcher_architectural_blueprint.md
Canonical Feature Guide: docs/features/app_switcher.md
---

[ 🏠 Docs Home ](../README.md) › [ 📁 History ](../README.md#history) › **App Switcher Evolution Timeline & Commit History**

---

# App Switcher Evolution Timeline & Commit History

This document chronicles the 27-month engineering journey of desktop window switching, application focus orchestration, and workspace isolation in this repository—from early 2024 taskbar macros to the modern sub-millisecond native Win32 architecture with guarded keystate context managers.

---

## Executive Summary

Window switching is a deceptively difficult challenge in hands-free voice computing. On Windows 10 and 11, the operating system enforces strict foreground-lock policies (`ForegroundLockTimeout`) to prevent background processes from stealing focus. Furthermore, speech recognition engines (Dragonfly/Kaldi) run inside a continuous recognition loop that cannot afford long synchronous pauses, COM apartment deadlocks, or modifier keystate corruption (such as sticky `Alt` keys locking out voice dictation).

Over more than two years, the window switching subsystem evolved through **five distinct architectural eras**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Era 1: Windhawk Taskbar Indexing & Keyboard Macros (May – Sep 2024)        │
│   • taskbar.py rule, Windhawk vertical taskbars, Win+T traversal macros     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ Era 2: Dynamic Aliasing & Foreground Lock Mitigations (Apr – Aug 2025)       │
│   • switch_application.py, window_aliases.json, raw Alt-key tap bypass     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ Era 3: Deep App Switcher & Virtual Desktops (May – Jun 2026)                │
│   • app_switcher.py, pywinauto UIA wrappers, pyvda workspace isolation     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ Era 4: Wayfinder Telemetry & Menu Lockout Prevention (Jul – Early Aug 2026) │
│   • QuickEdit freeze discovery, VK_NONE dummy key, Caster HUD feedback      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ Era 5: Sub-Millisecond Native Win32 & Keystate Guards (Aug 14, 2026 - v3)   │
│   • 8397b0c: Direct Win32 tiers, _alt_key_bypass & _attached_threads        │
│     context managers, AliasRegistry, 10ms micro-polling, Win+T eliminated   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The 5 Evolution Eras

### Era 1: Windhawk Taskbar Indexing & Keyboard Macros (May 2024 – Sep 2024)
- **Problem**: Moving away from Windows Speech Recognition (WSR) required a quick way to switch applications without touching the mouse.
- **Approach**: Used numeric taskbar position commands (`"switch <n>"`). Leveraged Windhawk mods for vertical taskbar numbering and simulated `Win+<n>` or `Win+T` traversal keyboard sequences.
- **Limitations**: Inflexible when application positions shifted; broke whenever windows were opened or closed dynamically.

### Era 2: Dynamic Aliasing & Tab Switching (Apr 2025 – Aug 2025)
- **Problem**: Voice users needed mnemonic aliases (`"switch to leets"`, `"switch to paper"`) bound to specific windows and browser/editor tabs.
- **Approach**: Introduced `switch_application.py` and persistent storage via `window_aliases.json`. First introduced synthetic Alt keydown injection (`97c10b7`) to bypass Windows 11 foreground lockouts. An ambitious object-oriented `WindowBackend` abstraction was attempted but subsequently archived to `attic/` (`b2a2015`) to keep the voice execution path simple and fast.
- **Limitations**: Naked Win32 API calls frequently left Alt keys stuck down; tab cycling lacked fine-grained focus verification.

### Era 3: Deep `app_switcher.py` Consolidation & Virtual Desktops (May 2026 – Jun 2026)
- **Problem**: Fragmented scripts across `taskbar.py` and `switch_application.py` caused maintenance divergence. Windows across multiple virtual desktops caused unexpected cross-workspace focus jumps.
- **Approach**: Consolidated all switching logic into a deep, modular `caster_user_content/util/app_switcher.py` utility with `WindowsOSAdapter`. Added `pyvda` integration (`9dad043`) to enforce virtual desktop boundaries. Engineered a 3-tier failsafe pipeline (`afb6f63`): (1) `pywinauto` focus, (2) Taskbar UIA button click, (3) `Win+T` keyboard macro.
- **Limitations**: `pywinauto` wrapper overhead introduced noticeable latency (200–400ms) on hot focus paths; naked `AttachThreadInput` lacked guaranteed detachment during unhandled exceptions.

### Era 4: Wayfinder Telemetry, Caster HUD & Menu Lockout Fixes (Jul 2026 – Early Aug 2026)
- **Problem**: Mysterious voice hangs during window switching were initially suspected to be Python COM apartment deadlocks. Additionally, Alt-key bypass occasionally highlighted the window menu bar, swallowing subsequent voice commands.
- **Approach**: The 38-ticket Socratic Wayfinder research initiative ran empirical telemetry (`ca5dc70`), conclusively proving that hangs were caused by Windows PowerShell QuickEdit mode pausing console `stdout` upon mouse selection. Solved menu bar activation (`004af07`) by injecting a dummy key `VK_NONE` (`0xFF`) before releasing Alt. Integrated feedback notifications with the modern asynchronous Caster HUD (`castervoice.lib.printer`).

### Era 5: Sub-Millisecond Native Win32 Focus Tiers & Keystate Deadlock Elimination (Aug 14, 2026 — Present)
- **Problem**: Legacy anti-patterns remained in `app_switcher.py`: global mutable dictionary state, coarse `time.sleep` delays, unhandled exception vulnerability during thread input attachment, and pywinauto wrapper latency.
- **Approach (Commit `8397b0c`)**:
  1. **Direct Win32 Focus Tiers**: Replaced slow pywinauto wrappers with direct `SetForegroundWindow`, `BringWindowToTop`, and `AllowSetForegroundWindow` calls (0–10ms latency).
  2. **Guarded Context Managers**: Created `_alt_key_bypass()` and `_attached_threads(target_hwnd)` with nested `try-finally` blocks ensuring deterministic keyup and thread detachment.
  3. **Encapsulated Persistence**: Built `AliasRegistry` class for atomic loading, saving, and stale handle pruning.
  4. **Micro-Polling Verification**: Replaced static sleeps with 10ms micro-polling loops in `verify_focus()`.
  5. **Macro Elimination**: Removed brittle `Win+T` keyboard traversal macros entirely.

---

## Landmark Git Commit History

Below is the chronological commit table tracing every major evolutionary milestone in window switching:

| Date | Commit Hash | Author | Scope & Description |
| :--- | :--- | :--- | :--- |
| **2024-05-28** | `a4978fd` | Amir | **Initial Rule**: Created custom Dragonfly rule for window switching supporting 1-indexed and negative taskbar positions. |
| **2024-06-08** | `d525fab` | Amir | **Taskbar Expansion**: Added negative numbered switching and documentation for vertical taskbars with Windhawk. |
| **2024-09-30** | `e9ef954` | Amir | **Modular Extraction**: Moved window switching into dedicated `caster_user_content/rules/global/taskbar.py`. |
| **2025-04-18** | `5d42ffd` | Amir | **Window Aliasing**: Introduced `switch_application.py` enabling custom mnemonic voice aliases. |
| **2025-04-20** | `48f66b7` | Amir | **Tab Management**: Added tab cycling (`Ctrl+Tab` / `Ctrl+PgDn`) to match target window captions. |
| **2025-06-28** | `97c10b7` | Amir | **OS Foreground Bypass**: Implemented initial Alt-key injection workaround to overcome Windows 11 foreground locks. |
| **2025-07-15** | `e136ec0` | Amir | **JSON Persistence**: Created `window_aliases.json` for persistent cross-session alias storage. |
| **2025-08-08** | `b2a2015` | Amir | **Attic Migration**: Archived complex abstract `WindowBackend` to `attic/` in favor of streamlined UIA routines. |
| **2026-05-03** | `1848edc` | Amir | **App Switcher Genesis**: Created `caster_user_content/util/app_switcher.py` replacing `taskbar.py`. |
| **2026-05-03** | `b03e52c` | Amir | **Pywinauto Evaluation**: Evaluated `pywinauto.Application().window().set_focus()` with Win32 fallbacks. |
| **2026-05-05** | `9dad043` | Amir | **Workspace Awareness**: Integrated `pyvda` to enforce Virtual Desktop isolation and eliminate cross-desktop focus jumping. |
| **2026-05-20** | `3322e0e` | Amir | **App Name Matching**: Added Antigravity IDE support and descending-length caption matching in `extract_app_name()`. |
| **2026-05-31** | `afb6f63` | Amir | **Consolidated 3-Tier Pipeline**: Unified window switching under `app_switcher.py` with pywinauto, taskbar UIA, and Win+T macros. |
| **2026-06-02** | `75522dd` | Amir | **OS Adapter Modularization**: Structured `WindowsOSAdapter` and verified multi-tier focus escalation. |
| **2026-07-08** | `c4335d1` | Amir | **Caster HUD Routing**: Replaced raw terminal prints with `castervoice.lib.printer` and Caster HUD notifications. |
| **2026-07-16** | `2588603` | Amir | **Dynamic Dictation Aliases**: Enabled voice-driven alias creation on the fly with CI validation checks. |
| **2026-07-28** | `004af07` | Amir | **VK_NONE Menu Fix**: Injected dummy key `0xFF` during Alt release to prevent window menu bar lockup. |
| **2026-08-08** | `ca5dc70` | Amir | **Wayfinder Empirical Telemetry**: Proved focus freezes were caused by PowerShell QuickEdit console pause, debunking COM deadlocks. |
| **2026-08-14** | `8397b0c` | Amir | **Production v3 Architecture**: Direct sub-millisecond Win32 focus tiers, `_alt_key_bypass` and `_attached_threads` context managers, `AliasRegistry` class, 10ms micro-polling, and elimination of `Win+T` macro. |

---

## Architectural Comparison Across Eras

| Capability / Metric | Era 1 (Mid 2024) | Era 2 (Mid 2025) | Era 3 (May 2026) | Era 4 (Jul 2026) | Era 5 (Aug 2026 - Modern v3) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Primary Execution Path** | Synthetic `Win+<n>` key sequence | Win32 `SetForegroundWindow` | Pywinauto `set_focus()` wrapper | Pywinauto + `AttachThreadInput` | **Direct native Win32 APIs** (`BringWindowToTop` + `SetForegroundWindow`) |
| **Foreground Lock Bypass** | None (Relied on OS shell shortcut) | Raw `keybd_event(VK_MENU)` tap | `AttachThreadInput` + Alt key | Alt tap + `VK_NONE` (`0xFF`) dummy key | **Guarded `_alt_key_bypass()` context manager** with guaranteed nested `finally` |
| **Thread Queue Safety** | N/A | None (No thread attachment) | Naked `AttachThreadInput` | Naked `AttachThreadInput` | **Guarded `_attached_threads()` context manager** (guaranteed detachment) |
| **Alias State Architecture** | None (Position-only) | Global dict in `switch_application.py` | Global `aliases` dict in `app_switcher.py` | Global `aliases` dict + HUD feedback | **Encapsulated `AliasRegistry` class** with thread-safe persistence & pruning |
| **Focus Verification** | None | Static sleep (`0.1s`) | Coarse polling (`0.3s`–`0.5s`) | Telemetry-instrumented sleeps | **10ms non-blocking micro-polling** (`verify_focus`) |
| **Virtual Desktop Handling** | None (Flipped across desktops) | None | `pyvda.VirtualDesktop` filter | `pyvda` + pinned item tracking | **Integrated `pyvda` workspace isolation** |
| **Fallback Strategy** | Fail silently | Fail silently | Taskbar UIA + `Win+T` macro | Taskbar UIA + `Win+T` macro | **Targeted Taskbar UIA Button Click** (`Win+T` macro eliminated) |
| **Typical Activation Latency**| 300ms – 800ms | 100ms – 300ms | 200ms – 500ms | 150ms – 400ms | **0ms – 10ms (Fast Path) / 80ms (Bypass)** |

---

## Code Evolution: Before and After

### 1. Focus Invocation: Pywinauto Wrapper (Era 3) vs. Direct Win32 Hot Path (Era 5)

#### Legacy Era 3/4 Implementation
```python
# Legacy: Slow pywinauto UI tree traversal in hot execution path
try:
    app = self._desktop_win32.window(handle=handle)
    app.set_focus()
except Exception as e:
    _log("DEBUG", f"Pywinauto set_focus failed: {e}")
```

#### Modern Era 5 Implementation (`8397b0c`)
```python
# Modern: Direct, sub-millisecond native Win32 calls
win32gui.AllowSetForegroundWindow(-1)
self._ensure_window_shown(handle)
win32gui.BringWindowToTop(handle)
win32gui.SetForegroundWindow(handle)
```

---

### 2. Foreground Lock Bypass: Naked Calls (Era 3) vs. Guarded Context Managers (Era 5)

#### Legacy Era 3/4 Implementation
```python
# Legacy: Naked thread attachment vulnerable to unhandled exception deadlocks
win32process.AttachThreadInput(target_thread, current_thread, True)
win32gui.BringWindowToTop(handle)
win32api.keybd_event(0x12, 0, 0, 0) # Alt down
win32gui.SetForegroundWindow(handle)
win32api.keybd_event(0xFF, 0, 0, 0) # VK_NONE
win32api.keybd_event(0xFF, 0, 2, 0)
win32api.keybd_event(0x12, 0, 2, 0) # Alt up
win32process.AttachThreadInput(target_thread, current_thread, False) # Skipped if exception!
```

#### Modern Era 5 Implementation (`8397b0c`)
```python
# Modern: Guaranteed detachment and keystate release via nested context managers
@contextmanager
def _alt_key_bypass():
    win32api.keybd_event(VK_MENU, 0, 0, 0)
    try:
        yield
    finally:
        try:
            win32api.keybd_event(VK_NONE, 0, 0, 0)
            win32api.keybd_event(VK_NONE, 0, KEYEVENTF_KEYUP, 0)
        finally:
            win32api.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)

@contextmanager
def _attached_threads(target_hwnd):
    # Attaches calling thread to foreground thread & target thread
    try:
        yield
    finally:
        # Guaranteed detachment in reverse order even during unhandled exceptions
```

---

## Related Documentation

- **Current Architecture**: [App Switcher Architectural Blueprint (v3)](../architecture/app_switcher_architectural_blueprint.md)
- **Feature Guide**: [App Switcher Feature Guide](../features/app_switcher.md)
- **Master Repository Timeline**: [Repository Timeline & Technical Journey](repository_timeline.md)
- **HUD Evolution**: [Caster Printer & HUD Architectural Timeline](caster_printer_hud_timeline.md)
- **Wayfinder Research Corpus**: [Wayfinder UIA Threading Map](../wayfinder-uia-threading/map.md)
