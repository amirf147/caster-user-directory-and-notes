[ 🏠 Docs Home ](../README.md) › [ 📁 History ](../README.md#history) › **Technical Journey & Recent Focus**

---

# Technical Journey & Recent Focus

Our ongoing work focuses on real-time desktop context tracking, window switching, accessibility mechanics, and speech engine responsiveness. Below is a structured summary of our journey, ordered from active production focus back to foundational milestones:

### 1. Active Production: WinVDA Zero-Cached-State Virtual Desktop Engine (Published & Caster Production Migration)
- **Status (Active Production - Deployed & Published)**: Following the adversarial audit and 5 failure modes in legacy `pyvda`, designed, built, validated, and published **[WinVDA](https://github.com/amirf147/winvda)** (Apache-2.0) as an independent clean-room library. Deployed `winvda` across Caster production (`custom-setup` branch, commit `85feab8e`), completely replacing `pyvda` across all virtual desktop switching and window pinning workflows.
- **Core Engineering Breakthroughs**:
  - **Zero-Cached-State COM Invocation**: Eliminated long-lived remote interface proxies. Every operation acquires fresh pointers directly from `explorer.exe` ALPC endpoints, executes via direct `ctypes` vtable offsets, and safely releases pointers inside `finally` blocks, guaranteeing immunity to Explorer crashes.
  - **Apartment Threading Resilience**: Joins MTA (`COINIT_MULTITHREADED`), detects `RPC_E_CHANGED_MODE` (`0x80010106`) if the caller thread is already initialized in STA, executes safely without crashing, and preserves caller apartment state on exit.
  - **Task View Parity Application Pinning**: Normalizes application identities by stripping synthetic `~Wh~w<HEX_HWND>` sub-AUMIDs, registers canonical base package identities via `PinAppID`, and iterates active views to pin sibling windows (`PinView`).
  - **Dual-Mode Automation & Diagnostic CLI**: Extended `python -m winvda` with `pin-window`, `unpin-window`, `pin-app`, and `unpin-app` supporting explicit `--hwnd` for scripts, `--delay` for interactive terminal use, and active foreground window capture for background hotkey daemons.
  - **Cross-Framework Validation**: Empirically verified across heterogeneous application archetypes: Gecko (Waterfox profile-hash AUMIDs), Chromium/Electron (Antigravity IDE), and XAML Islands (Windows Terminal).
  - **HUD Voice Integration**: Bound `([toggle] pin | unpin) window [all work [spaces]]` and `([toggle] pin | unpin) app [all work [spaces]]` in `window_mgmt_rule.py` with immediate visual feedback via `printer.out`.
- **Key Documentation**:
  * 🌐 **[WinVDA Public Repository](https://github.com/amirf147/winvda)** *(Independent Clean-Room Engine)*
  * 🪟 **[WinVDA Realization & Caster Migration (006)](../pyvda/006_winvda_clean_room_engine_realization_and_caster_migration.md)** *(Production Milestone)*
  * 🪟 **[PyVDA Multi-Window & XAML Island Pinning Architecture (003)](../pyvda/003_pyvda_multi_window_xaml_island_pinning_architecture.md)**
  * 🪟 **[Adversarial Audit & Resilient Client Design (004)](../pyvda/004_adversarial_audit_and_hardened_com_architecture.md)**
  * 🪟 **[Task View Pinning Internals & Shell Reverse Engineering (005)](../pyvda/005_task_view_pinning_internals_and_shell_reverse_engineering.md)**
  * 🎙️ **[Virtual Desktop Pinning Architecture, Phonetic Misrecognition & Grammar Ergonomics](../features/virtual_desktop_pinning_and_grammar_ergonomics.md)**
  * 🧠 **[Repository Brain (Canonical SSOT)](../context/repository-brain.md)**
  * 📜 **[Status Update History](../../status-update-history.md)**

---

### 2. Next-Iteration Modular Caster HUD & Real-Time Context Integration
- **Status (Active Exploration & Production Blueprint - Complete)**: Refactored and modernized the Caster Heads-Up Display (HUD) into a high-performance, modular 5-layer Clean Architecture overlay that provides instant visual feedback for speech recognition, microphone safety states, native OS window tracking, active contextual voice rules, and sub-window semantic interaction zones from the Active Desktop Context Engine (ADCE).
- **Core Architecture & Breakthroughs**:
  - **5-Layer Clean Architecture & Unidirectional Data Flow**: Decoupled presentation (`MainWindow`, `StatusBarWidget`, `ActiveRulesBarWidget`, `AdceBarWidget`), immutable domain state & pure reducers (`HudState`, `reduce_event`), cross-thread IPC (`SignalBridge`, Qt Signals), OS/context observers (`IFocusTracker`, `AdceTracker`), and speech engine integration.
  - **Zero-Polling Win32 Window Focus Tracking (`IFocusTracker`)**: Native `SetWinEventHook` (`EVENT_SYSTEM_FOREGROUND`, `EVENT_OBJECT_NAMECHANGE`) provides instantaneous (< 1 ms) window title and process tracking on mouse clicks and Alt+Tab without waiting for speech recognition.
  - **Decoupled ADCE Micro-Context & SSE Ingestion**: Dedicated `AdceTracker` ingests real-time semantic interaction zones (`{IntegratedTerminal}`, `{EditorCodeBuffer}`) over Server-Sent Events (SSE on port 8424), updating sub-pane clicks in ~10–20 ms. Stale context across process switches is actively guarded, and disconnected states cleanly render `⚪ ADCE [ADCE is not connected]`.
  - **Contextual Active Rules Resolution & Engine Noise Suppression**: Dynamically resolves active application rules (e.g. `[VS Code]`, `[IDE Terminal]`, `[PowerShell]`) with terminal host fuzzy matching, CCR companion rule resolution, and automatic suppression of engine merger artifacts (`Repeater1`, `PreparedRule`, `dictation_sink_rule`), providing clean `[Global Context]` and `[Microphone Sleeping]` states.
  - **Multi-Theme System & Dynamic Safety Glow**: 4 preset themes (`classic`, `frosted-dark`, `minimal-transparent`, `high-contrast`), custom `.qss` loading, multi-window stylesheet propagation, full `QMenu` styling, and priority border status glow (🟢 Listening $\succ$ 🔴 Sleeping $\succ$ 🟡 Drag Mode $\succ$ 🔵 Window Focus).
  - **Zero-Latency IPC Isolation**: Dedicated port allocation (Port 8338 for XML-RPC, Port 8339 for ndjson telemetry) with non-blocking drop-oldest queues (`queue.Queue(maxsize=1024)`) guaranteeing `< 0.001 ms` speech thread overhead.
  - **Ergonomics & Controls**: Direct header click-and-drag window movement, 'D' drag mode with arrow nudging, 'T' frameless toggle, system tray docking, font scaling, modal help/rules dialogs, and comprehensive voice/context-menu controls.
- **Key Documentation**:
  * 📋 **[Caster HUD Master Requirements & Specifications (005)](../caster_hud/005_caster_hud_requirements_and_specifications.md)** *(Authoritative SSoT)*
  * 🏛️ **[Caster HUD Clean Architecture Synthesis (009)](../caster_hud/009_caster_hud_architectural_review_and_clean_architecture_synthesis.md)**
  * 📜 **[Caster HUD Continuous Lessons Learned Timeline (007)](../caster_hud/007_caster_hud_lessons_learned_timeline.md)**
  * 🔄 **[ADCE Realtime Stream & Native Focus Decoupling (011)](../caster_hud/011_adce_realtime_stream_and_native_focus_decoupling_deep_dive.md)**
  * 🔬 **[Fine-Grained Context: Native OS vs ADCE Explainer (010)](../caster_hud/010_fine_grained_context_recognition_native_vs_adce_explainer.md)**
  * 🚀 **[Active Desktop Context Engine Repository](https://github.com/amirf147/active-desktop-context-engine)**

---

### 3. Sub-Millisecond Native Win32 App Switcher Refactor (Active Production v3.1)
- **Active Production Status**: We have refactored and deployed the **v3.1 production architecture** for [`caster_user_content/util/app_switcher.py`](../../caster_user_content/util/app_switcher.py).
- **Core Engineering Breakthroughs**:
  - **4-Tier Progressive Focus Escalation**: Fast path operates on direct Win32 APIs (Tier 1 `SetForegroundWindow` in 0–10ms), escalating upon `ForegroundLockTimeout` to guarded `_alt_key_bypass()` (Tier 2 in 80–120ms), dual-thread input queue synchronization via `_attached_threads()` (Tier 3 in 120–200ms), and finally Tier 4 taskbar hotkeys (50–150ms).
  - **Tier 4 Taskbar Shell Hotkey Traversal**: Pure read-only inspection of Windows 11 XAML Island taskbar buttons (`TaskListButton` in `Shell_TrayWnd`) and Windows 10 Toolbars (`MSTaskListWClass`) resolves the target application's 1-based slot index `K`, dispatching native shell hotkeys `Win+<K % 10>` or `Win+T` traversal directly through `explorer.exe`.
  - **UIPI Security Boundaries & HUD Airlock Pattern**: Codified the strict security boundary where elevated windows (High Integrity Level / Administrator) block programmatic focus and cause the Windows raw input thread to silently discard synthetic keystrokes from unprivileged callers. Demonstrated that a physical click on the Medium-Integrity Caster HUD or taskbar acts as an integrity airlock, resetting foreground ownership and enabling instant Tier 1 switching in 25ms.
  - **Retirement of Legacy UIA Mouse Clicks**: Formally deprecated and retired invasive taskbar UIA mouse-click fallbacks in favor of deterministic shell hotkey delegation.
  - **Guarded Keystate Context Managers**: Eliminated sticky modifier keys and thread deadlocks using `_alt_key_bypass()` (with guaranteed nested `finally` release of `VK_NONE` 0xFF and `VK_MENU` 0x12) and `_attached_threads(target_hwnd)` for deterministic `AttachThreadInput` queue pairing and detachment.
  - **Encapsulated Persistence**: Refactored alias dictionary mutations and JSON serialization into a clean, thread-safe `AliasRegistry` class.
  - **Micro-Polling Verification**: Replaced coarse sleep intervals with non-blocking 10ms micro-polling loops in `verify_focus(target_hwnd)`.
- **Key Documentation**:
  - 🏗️ **[App Switcher Architectural Blueprint (v3.1)](../architecture/app_switcher_architectural_blueprint.md)**
  - 📜 **[App Switcher Evolution Timeline (2-Year Retrospective)](app_switcher_timeline.md)**
  - 📖 **[App Switcher Feature Guide](../features/app_switcher.md)**
  - 🛠️ **[App Switcher Findings & UIPI Post-Mortem](../troubleshooting/app_switcher_findings.md)**

---

### 4. Wayfinder Session: App Switching & UIA Threading Investigation
- **Condensed Summary**: Investigated perceived freezes in `app_switcher.py` and UIA/COM threading performance across speech stacks. Discovered through empirical telemetry (`ca5dc70`) that apparent hangs were caused by Windows PowerShell QuickEdit mode pausing standard output (`stdout`) during console logging.
- **Key Docs & Code**:
  - Feature Guide: **[App Switcher Documentation](../features/app_switcher.md)**
  - Session Index: **[Wayfinder UIA & Threading Directory](../wayfinder-uia-threading/map.md)**
  - Rule & Utility Code: **[window_switching.py](../../caster_user_content/rules/global/window_switching.py)** & **[app_switcher.py](../../caster_user_content/util/app_switcher.py)**

---

### 5. Historical Status & Archived Investigations
- Archive of past status updates with deep dives into Dynamic Sub-Window Grammar Activation, LexiconCode PR #881 investigation, the Dragonfly BPC Fork Kaldi race condition fixes, and UIA threading synthesis:
  👉 **[Status Update History](../../status-update-history.md)**

---

### 6. Git Evolution & Subsystem Timelines
For complete historical retrospectives spanning our 27-month, 969-commit repository evolution:
- 📜 **[App Switcher Evolution Timeline](app_switcher_timeline.md)**: 2-year journey across 6 eras of window switching.
- 📜 **[Caster Printer & HUD Timeline](caster_printer_hud_timeline.md)**: Evolution of status messaging and async HUD overlays.
- 📜 **[Repository Master Timeline](repository_timeline.md)**: Comprehensive 4-era narrative covering 27 months of hands-free Voice OS engineering.
- 🌐 **[Interactive Timeline Visualizer](timeline.html)**: Interactive web timeline application.
