[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](001_caster_hud_architecture_and_threading_primer.md) › **007: Continuous Lessons Learned Timeline & Engineering Trail**

---

# 007 — Caster Heads-Up Display: Continuous Lessons Learned Timeline & Engineering Trail

**Document ID**: `CASTER-DOC-HUD-007`  
**Status**: Living Engineering Log & Lessons Learned Trail  
**Target Subsystem**: `castervoice/asynch/hud/`  
**Authors**: Antigravity Principal Architecture Team (Pair Programming with Amir Farhadi)  

---

## 1. Overview

This document provides a continuous, chronological timeline of architectural challenges encountered during the design, implementation, and refinement of the Modular Caster HUD, the root cause identified, the lesson learned, and the permanent architectural solution enacted.

---

## 2. Chronological Timeline & Trail

### Milestone 1: Settings Schema Discovery & Default Fallbacks
* **Encountered Issue**: Launching Caster from batch files loaded factory defaults (framed 300x200 classic white window) instead of the user's slim high-contrast layout.
* **Root Cause**: `hud.py` called `settings.settings("hud")` (which did not exist), silently falling back to `{}`.
* **Lesson Learned**: Always verify whether configuration subsystems export helper functions or a global module dictionary (`settings.SETTINGS`).
* **Solution**: Updated `hud.py` to read `settings.SETTINGS.get("hud", {})` and added `merge_hud_config()` fallback merger.

---

### Milestone 2: Dual-Protocol Port Collision (Freeze on "show caster help")
* **Encountered Issue**: Uttering `"show caster help"` or `"show caster rules"` failed to show the dialog, froze the speech recognition loop, and stopped all subsequent border color updates.
* **Root Cause**: Both the raw `ndjson` telemetry socket and the legacy XML-RPC server were configured to use port `8338`. The XML-RPC server never started; instead, the raw ndjson socket bound port 8338. Synchronous XML-RPC calls from Dragonfly sent HTTP POST headers, which the socket listener could not parse, hanging the speech thread indefinitely on `socket.recv()`.
* **Lesson Learned**: Never multiplex raw binary/ndjson streaming sockets and HTTP-based XML-RPC on the same default port number.
* **Solution**: Assigned dedicated ports: **Port 8338** for XML-RPC and **Port 8339** for high-performance `ndjson` telemetry streams.

---

### Milestone 3: Cross-Thread Widget Instantiation & Event Loop Deadlocks
* **Encountered Issue**: Background XML-RPC handler threads directly called `window.show_help_dialog()` and `window.show_rules_dialog()`, creating GUI dialogs outside the main Qt thread.
* **Root Cause**: In Qt/PySide, manipulating or creating `QWidget` instances from non-GUI threads violates the single-threaded GUI invariant, causing silent event pump deadlocks.
* **Lesson Learned**: All cross-thread invocations must strictly use `QtCore.Signal` or `QtCore.QCoreApplication.postEvent()`.
* **Solution**: Implemented `SignalBridge` with typed signals (`show_help_requested`, `show_rules_requested`, `clear_hud_requested`, etc.), ensuring 100% of widget creation occurs on the Qt main GUI thread.

---

### Milestone 4: Endpoint Parity & Method "toggle_scrollbars" Not Supported
* **Encountered Issue**: Uttering `"caster hud scroll"` produced `<Fault 1: method 'toggle_scrollbars' is not supported>`.
* **Root Cause**: `hud_support.py` defined `toggle_scrollbars()` and font methods, but they were omitted from `_setup_xmlrpc_methods()` in `hud.py`.
* **Lesson Learned**: Maintain 100% method parity between client voice rule callers in `hud_support.py` and the server registration matrix.
* **Solution**: Registered `toggle_scrollbars`, `font_increase`, `font_decrease`, and `font_reset` in `hud.py` and implemented corresponding handlers in `MainWindow`.

---

### Milestone 5: Window Flag Mutation & Focus Loss on Title Bar Toggle ('T')
* **Encountered Issue**: Toggling the title bar / frameless overlay with `'T'` caused the HUD to lose OS keyboard focus.
* **Root Cause**: In Qt, `setWindowFlags()` destroys and recreates the underlying Windows `HWND`, causing the OS to shift focus to the background application.
* **Lesson Learned**: Re-activate and claim keyboard focus explicitly whenever native window chrome flags are modified.
* **Solution**: Called `self.showNormal()`, `self.show()`, `self.raise_()`, `self.activateWindow()`, `self.setFocus()`, and `self.log_widget.setFocus()` immediately following `setWindowFlags()`.

---

### Milestone 6: Multi-Window Theme Propagation
* **Encountered Issue**: Changing HUD themes (`classic`, `frosted`, `minimal`, `high-contrast`) did not update standalone modal dialogs (Rules tree, Help dialog).
* **Root Cause**: `apply_theme()` applied QSS stylesheets only to `MainWindow` and did not propagate to top-level child dialogs.
* **Lesson Learned**: Central theme managers in desktop applications must actively broadcast theme updates to all active child views.
* **Solution**: `MainWindow.apply_theme()` now normalizes aliases via `ThemeManager.normalize_theme_name()` and propagates the stylesheet to all open dialogs (`help_dialog`, `rules_dialog`, `profile_dialog`).

---

### Milestone 7: Active Rules Explosion vs Focused Contextual Scoping & ADCE Integration
* **Encountered Issue**: Enabling the Active Rules tag strip displayed 30+ always-active global rules (navigation, alphabet, numbers, punctuation, etc.), cluttering the compact overlay with excessive noise.
* **Root Cause**: `get_active_rule_names()` enumerated all grammars without distinguishing between global grammars (`grammar.context is None`) and application-scoped contextual grammars (`grammar.context is not None`).
* **Lesson Learned**: Persistent status overlays should display high-signal context (the active application/contextual rules or `[Global Context]` fallback) rather than exhaustive global grammar dumps.
* **Solution**:
  1. Implemented `get_active_contextual_rules()` to filter rules to only active scoped grammars.
  2. Updated `ActiveRulesBarWidget` to render `[Global Context]` cleanly when in generic windows, and active application badges (e.g. `[VS Code]`, `[IDE Terminal]`) when contextual rules match.
  3. Created `AdceBarWidget` for dedicated, independent Active Desktop Context Engine telemetry (`🟢 ADCE`, `{Zone}`, `[Process]`, `📄 File`).
  4. Structured `"caster hud verbose [toggle]"` to control diagnostic panels (Status Header + Rules Strip) without affecting the independently toggled ADCE strip.

---

### Milestone 8: CCR Internal Merger Artifacts & Zero-Polling Window Focus Tracking
* **Encountered Issue**:
  1. The Active Rules strip displayed internal merger artifact names `[Repeater1]` and `[PreparedRule]`.
  2. The HUD did not dynamically update when clicking between applications or Alt+Tabbing without speaking.
* **Root Cause**:
  1. `CCRMerger2` wraps merged companion rules in classes named `Repeater1` and `PreparedRule` and sets a `negation_context` (`FuncContext`) on the global CCR grammar. Our check treated any non-None context as an app rule.
  2. Dragonfly only evaluates grammar contexts during speech recognition events. When the user silently clicks or switches windows, Dragonfly remains idle.
* **Lesson Learned**:
  1. Internal engine merger artifacts must be explicitly filtered out (`is_internal_rule_name`).
  2. Instant, zero-latency desktop updates require event-driven OS focus hooks rather than relying solely on the speech recognition loop.
* **Solution**:
  1. Filtered out all merger artifacts (`Repeater\d+`, `PreparedRule`, `RepeatRule`, `ccr`, `_.*`) in `get_active_contextual_rules()`.
  2. Implemented `Win32WindowFocusTracker` via `SetWinEventHook` (`EVENT_SYSTEM_FOREGROUND`, `EVENT_OBJECT_NAMECHANGE`) behind an abstract `IFocusTracker` interface, immediately pushing `DesktopContextEvent` and `ActiveRulesEvent` over IPC on every click/switch with zero CPU polling overhead.

---

### Milestone 9: Window Activation Race Condition & Synchronous Target Matching
* **Encountered Issue**: When switching rapidly between apps (e.g. Waterfox & PowerShell), the HUD displayed the active rules from the *previous* window (lagging behind by one window switch).
* **Root Cause**:
  1. During `EVENT_SYSTEM_FOREGROUND`, calling `user32.GetForegroundWindow()` had a race condition where the OS activation message had not yet settled, returning the previous window handle.
  2. An unconditional sub-30ms event debounce dropped the second/final settled event.
  3. `get_active_contextual_rules()` called `ctx.matches()` with zero arguments, which fell back to the speech thread's cached `r.active` state.
* **Lesson Learned**:
  1. WinEventHook callbacks must query the event `hwnd` parameter and its `GA_ROOT` ancestor directly, rather than polling `GetForegroundWindow()`.
  2. Rule contexts must be evaluated synchronously against the target window: `ctx.matches(target_process, target_title, target_hwnd)`.
* **Solution**:
  1. Updated `Win32WindowFocusTracker` to resolve `target = GetAncestor(hwnd, GA_ROOT)` directly from the callback and removed the unconditional event drop.
  2. Updated `_on_window_focus_changed` to pass `(process_name, window_title, hwnd)` directly into `get_active_contextual_rules()`, evaluating `ctx.matches(target_process, target_title, target_hwnd)` instantly with zero lag.

---

### Milestone 10: Spurious WinEvent Range Jitter, Sleeping Rule Suppression & Widget Memoization
* **Encountered Issue**: The Active Rules bar constantly flashed/jittered when speech occurred, and application rules remained visible when the microphone was sleeping.
* **Root Cause**:
  1. `SetWinEventHook` was initialized with a wide range (`0x0003` to `0x800C`), capturing hundreds of spurious OS internal events (mouse hovers, cursor blinks, UI redraws, text additions to HUD log).
  2. `ActiveRulesBarWidget` re-allocated child widgets on every event without state memoization.
  3. `ActiveRulesBarWidget` was unaware of the microphone sleeping state (`mic_state`).
* **Lesson Learned**:
  1. WinEventHooks must target exact single-event IDs (`EVENT_SYSTEM_FOREGROUND` and `EVENT_OBJECT_NAMECHANGE` with `OBJID_WINDOW = 0`).
  2. UI widgets must strictly memoize previous render tuples to avoid visual redraw thrashing.
  3. The Active Rules strip must dynamically reflect sleep state by displaying `[Microphone Sleeping]` and suppressing application badges when sleeping.
* **Solution**:
  1. Split `SetWinEventHook` into two pinpoint hooks (`EVENT_SYSTEM_FOREGROUND` only, and `EVENT_OBJECT_NAMECHANGE` filtered by `idObject == OBJID_WINDOW`).
  2. Added strict memoization (`rule_tuple == self._current_rules and state_clean == self._current_mic_state`) in `ActiveRulesBarWidget`.
  3. Updated `ActiveRulesBarWidget` to render `[Microphone Sleeping]` and suppress application rules when sleeping, restoring them immediately upon wake.

---

### Milestone 11: Background Daemon Filtering, Transient Alt+Tab Isolation & ADCE Offline State Cleansing
* **Encountered Issue**:
  1. Background daemons (`ADCE.Daemon`, `ADCE.Monitor`) appeared as the active application in HUD.
  2. Alt+Tab window switching got stuck on `"Task Switching"`.
  3. Turning on the ADCE strip when ADCE was offline showed stale context from previous sessions.
  4. Saying `"active rules strip"` failed to toggle unless already in verbose mode.
* **Root Cause**:
  1. `Win32WindowFocusTracker` did not filter background helper process names or transient Windows shell switcher titles (`Task Switching`, `Task View`).
  2. `AdceBarWidget` did not clear previous in-memory context properties when disconnected (`is_connected=False`).
  3. `caster_rule.py` required the strict prefix `"caster hud"`, failing on `"active rules strip"` or `"toggle active rules"`.
* **Lesson Learned**:
  1. OS focus trackers must maintain explicit exclusion sets for background support daemons and transient OS task switchers (`IGNORED_PROCESS_NAMES`, `IGNORED_WINDOW_TITLES`).
  2. Offline status strips must proactively wipe cached process/zone/file context.
  3. Voice grammar specifications must support natural short forms (`"[caster hud] active rules strip"`, `"toggle active rules"`).
* **Solution**:
  1. Added `IGNORED_PROCESS_NAMES` and `IGNORED_WINDOW_TITLES` in `window_tracker.py`.
  2. Updated `AdceBarWidget.update_context` to clear all context and render `[ADCE is off / inactive]` in gray when `is_connected=False`.
  3. Added flexible voice specs in `caster_rule.py`.

---

### Milestone 12: Contextual Rules Strict Scoping & Dictation Sink Exclusion
* **Encountered Issue**: Switching to generic desktop apps (e.g. Element) or Desktop displayed a massive list of global rules (`+15 more`, `navigation`, `caster rule`, `dictation sink rule`).
* **Root Cause**: Returning global rules on generic windows overwhelmed the compact UI with 15+ always-active global rules instead of maintaining a clean, minimal status.
* **Lesson Learned**: On persistent status overlays, global context should be represented cleanly as `[Global Context]` rather than dumping exhaustive grammar lists. Application-specific rules should only appear when actually scoped to the focused application.
* **Solution**:
  1. Updated `get_active_contextual_rules()` to return only genuine contextual application rules when scoped, and return `[]` for generic/desktop windows.
  2. Added `dictationsinkrule`, `dictation_sink_rule`, and `dictationsink` to `INTERNAL_RULE_EXCLUSIONS`.
  3. When `[]` is returned, `ActiveRulesBarWidget` renders a clean `[Global Context]` pill with zero clutter.

---

### Milestone 13: PowerShell / Windows Terminal Fuzzy Context Resolution & Dynamic QFrame Border Container
* **Encountered Issue**:
  1. Focusing PowerShell (e.g. inside Windows Terminal or pwsh) did not display PowerShell rules.
  2. The HUD border remained a static white border and stopped changing colors between Green (Listening) and Red (Sleeping).
* **Root Cause**:
  1. When PowerShell runs inside Windows Terminal (`windowsterminal.exe`), `target_process` is `"windowsterminal"`, causing strict `AppContext(executable="powershell")` checks to evaluate to `False`. Furthermore, `get_active_contextual_rules()` unconditionally skipped all `ccr-*` grammars, dropping app-specific CCR rules like `powershell_ccr.py`.
  2. `container` was a plain `QWidget`, which ignores stylesheet borders unless `setAttribute(WA_StyledBackground, True)` is set or `QFrame` is used. Furthermore, themes had `QTextEdit { border: 2px solid #ffffff; }`, painting an internal white border. Finally, `BorderController` had an unnecessary guard `if not self._is_frameless: return` that suppressed borders when running in framed mode.
* **Lesson Learned**:
  1. Terminal shells (PowerShell, pwsh, cmd, git bash) frequently run inside multiplexing container hosts (`WindowsTerminal`, `wt`, `conhost`). Context evaluation must perform candidate alias expansion based on process and window title.
  2. App-specific CCR grammars (`ccr-*` with non-None `grammar.context`) must be evaluated alongside standard grammars, extracting the executable name when rule name is a `Repeater` wrapper.
  3. Dynamic border controllers must target styled `QFrame` containers with `WA_StyledBackground`, remove internal `QTextEdit` borders, and operate consistently across both framed and frameless modes.
* **Solution**:
  1. Added terminal host process candidate normalization (`powershell`, `pwsh`, `windowsterminal`, `conhost`) in `get_active_contextual_rules()`.
  2. Evaluated app-specific `ccr-*` grammars and extracted clean rule names from `ctx._executable`.
  3. Switched `MainWindow` container to `QtWidgets.QFrame` with `WA_StyledBackground`, set `QTextEdit { border: none; }` across all themes, and updated `BorderController` to style the outer frame in both framed and frameless modes.

---

### Milestone 14: QMenu Interactive Hover Styling, Python/Pythonw Focus Exclusion & ADCE Sub-Window Zone Sync
* **Encountered Issue**:
  1. Context menu items lacked hover/selection highlights (remaining plain black/white with no visual feedback).
  2. Opening the HUD context menu replaced the active window title/process with `pythonw`.
  3. ADCE strip was showing only process and title without live sub-window semantic zones (`{IntegratedTerminal}`, `{EditorCodeBuffer}`).
* **Root Cause**:
  1. Theme stylesheets lacked explicit `QMenu`, `QMenu::item`, and `QMenu::item:selected` CSS definitions.
  2. `window_tracker.py` did not include `python` and `pythonw` in `IGNORED_PROCESS_NAMES`, causing context menu popup activation to be registered as an OS window switch.
  3. `_on_window_focus_changed` and `toggle_hud_adce` did not query ADCE bridge properties (`semantic_zone`, `active_file`) when publishing `DesktopContextEvent`.
* **Lesson Learned**:
  1. Comprehensive desktop overlay themes must explicitly style all popup elements (`QMenu`, `QMenu::item:selected`, `QMenu::separator`) for high-contrast accessibility and hover feedback.
  2. Internal speech engine helper processes (`python`, `pythonw`) and HUD popup titles must be strictly excluded from foreground window tracking.
  3. OS focus events must enrich telemetry with ADCE micro-context (`get_adce_context()`) whenever the ADCE bridge is connected.
* **Solution**:
  1. Added explicit `QMenu`, `QMenu::item:selected` hover rules across all 4 theme stylesheets in `theme_manager.py`.
  2. Added `python` and `pythonw` to `IGNORED_PROCESS_NAMES` and `"caster hud context menu"`, `"caster"` to `IGNORED_WINDOW_TITLES` in `window_tracker.py`.
  3. Added `get_adce_context()` in `hud_support.py` and populated `semantic_zone` and `active_file` in all `DesktopContextEvent` dispatches.

---

### Milestone 15: Decoupling StatusBarWidget from ADCE Micro-Zones & Sub-Pane Click Instant Updates via AdceTracker
* **Encountered Issue**:
  1. `{IntegratedTerminal}` was showing in the top status bar header beside the window title instead of strictly in the ADCE Bar.
  2. Clicking between editor, terminal, chat, or commit box inside the same IDE window failed to update the HUD until clicking the taskbar.
  3. User was confused why closing ADCE still allowed window title tracking.
* **Root Cause**:
  1. `StatusBarWidget` contained an extraneous `_zone_label` that displayed `ctx.semantic_zone` in the top header.
  2. Clicking inside the same Electron window does not change the top-level `HWND` or window title, so OS `SetWinEventHook` emitted zero events. ADCE detected the change via UIA, but Caster HUD had no dedicated SSE listener for internal sub-pane events.
  3. Top-level window tracking is handled 100% natively by `Win32WindowFocusTracker` (`SetWinEventHook`) and is completely independent of ADCE.
* **Lesson Learned**:
  1. `StatusBarWidget` must strictly display native OS and speech metadata (`[LISTENING] [code] [title] [rule]`), while `AdceBarWidget` exclusively manages `{Zone}`, `[Process]`, and `📄 File`.
  2. Sub-window clicks inside Electron apps require a persistent SSE listener (`AdceTracker` on port 8424) to dispatch `DesktopContextEvent` and `ActiveRulesEvent` in real time (<10 ms).
  3. When ADCE is disconnected, `AdceBarWidget` must explicitly display `⚪ ADCE [ADCE is not connected]`.
* **Solution**:
  1. Decoupled `StatusBarWidget` by removing `_zone_label` from the top header.
  2. Implemented `AdceTracker` in `castervoice/asynch/hud/core/adce_tracker.py`, connecting to ADCE SSE stream and dispatching `DesktopContextEvent` and `ActiveRulesEvent` immediately on sub-pane clicks.
  3. Updated `AdceBarWidget` to render `[ADCE is not connected]` when offline.

---

### Milestone 16: ADCE Disconnected State SSoT Styling, {Unknown} Fallback, and Direct Header Click-and-Drag Architecture
* **Encountered Issue**:
  1. When closing ADCE, `toggle_adce_bar()` and `dispatch_event()` hardcoded `is_connected=True`, causing `AdceBarWidget` to render a green `ADCE` badge with `[Ready]`.
  2. Users had to manually toggle drag mode (`'D'`) to move the HUD instead of clicking and dragging directly on the header strips.
  3. Unclassified zones rendered as empty pills instead of displaying `{Unknown}`.
* **Root Cause**:
  1. `DesktopContextState` and `DesktopContextEvent` did not track `is_connected` as a reactive state variable, causing the HUD to default to online rendering even when ADCE was closed.
  2. Mouse events were only filtered on `log_widget.viewport()`, requiring whole-window drag mode (`'D'`) to move the window.
* **Lesson Learned**:
  1. Connection state (`is_connected`) must be a first-class citizen in the reactive event/state architecture (`DesktopContextEvent` $\to$ `reducer` $\to$ `state.desktop_context.is_connected`).
  2. Overlay title strips (`StatusBarWidget`, `ActiveRulesBarWidget`, `AdceBarWidget`) should act as native caption bars that support immediate left-click dragging without requiring dedicated modes.
* **Solution**:
  1. Added `is_connected` to `DesktopContextState`, `DesktopContextEvent`, and `reducer.py`.
  2. Updated `AdceBarWidget` to render muted gray `⚪ ADCE` `[ADCE is not connected]` when offline, green `🟢 ADCE` when online, and `{Unknown}` for unclassified zones.
  3. Installed event filters on all header strips (`StatusBarWidget`, `ActiveRulesBarWidget`, `AdceBarWidget`, `_container`), enabling seamless direct left-click window dragging.









