# Caster User Directory

A high-performance, Windows-only personal voice computing and automation toolkit built on Caster and Dragonfly. 

This repository houses custom voice grammars, low-latency window switching utilities, hardware IPC bridges, and in-depth engineering research into Windows UI Automation, speech engine threading, and real-time desktop context tracking.

> 📚 **[Documentation Hub](docs/README.md)**  
> Master navigation, architectural blueprints, subsystem deep dives, and technical specifications for all repository subsystems.

---

## 🤖 .agents Folder

Contains workflows (such as `/commit`, `/relative-paths`, and `/adversarial-architecture-review`) and workspace configuration rules specifically for the **Antigravity** editor.

---

## ⚡ Key Engineering & Voice Automations

* **[Modular Caster HUD Overlay](docs/caster_hud/005_caster_hud_requirements_and_specifications.md)**: Educational breakdown, Single Source of Truth (SSoT), 5-layer Clean Architecture, zero-polling native Win32 window focus hooks, decoupled ADCE SSE stream ingestion, and multi-theme layout persistence.
* **[Active Desktop Context Engine (ADCE) & MCP Hub](docs/accessibility_mcp/CONTEXT.md)**: Real-time, event-driven OS state tracking (`scripts/context_poc.py`), tab discovery across browsers and IDEs, Virtual Desktop awareness, and Model Context Protocol (MCP) integration.
* **[App & Window Switcher v3](docs/features/app_switcher.md)**: Sub-millisecond direct Win32 window switching, workspace isolation, guarded keystate context managers, and automated tab navigation.
* **[App Switcher Evolution Timeline](docs/history/app_switcher_timeline.md)**: 2-year retrospective tracing the 5 evolution eras of window switching from Windhawk taskbar macros to native Win32 v3.
* **[App Switcher Architectural Blueprint (v3)](docs/architecture/app_switcher_architectural_blueprint.md)**: Authoritative technical specification, focus tier state machines, and sequence diagrams.
* **[WinVDA Virtual Desktop Subsystem](https://github.com/amirf147/winvda)**: Clean-room, zero-cached-state Windows Virtual Desktop engine ([006](docs/pyvda/006_winvda_clean_room_engine_realization_and_caster_migration.md)) replacing legacy `pyvda` in Caster production. Built on direct ctypes vtable dispatch, transient MTA sessions immune to Explorer restarts, exact-match sub-AUMID normalization ([003](docs/pyvda/003_pyvda_multi_window_xaml_island_pinning_architecture.md)), and native Task View parity ([005](docs/pyvda/005_task_view_pinning_internals_and_shell_reverse_engineering.md)).
* **[Virtual Desktop Pinning Architecture, Phonetic Misrecognition & Grammar Ergonomics](docs/features/virtual_desktop_pinning_and_grammar_ergonomics.md)**: Voice-driven pinning and unpinning across virtual workspaces, phonetic coarticulation failure analysis (`pin window` -> `new window`), Kaldi decoder language model priors, Caster noun-first syntactic alignment, and upstream PR coordination.
* **[Foot Pedal & XML-RPC IPC Bridge](docs/features/foot_pedal.md)**: Hardware debouncing, smart tap/drag/scroll control for the Olympus RS31H foot pedal, paired with a local XML-RPC IPC bridge for thread-safe microphone toggling.
* **[Top Voice Automations Showcase](docs/features/top_voice_automations.md)**: Curated showcase of desktop, editor, and system voice workflows.

---

## 🧭 Technical Journey & Recent Focus

Our ongoing work focuses on real-time desktop context tracking, window switching, accessibility mechanics, and speech engine responsiveness:

### 1. Active Production: WinVDA Zero-Cached-State Virtual Desktop Engine (Published & Caster Production Migration)
* **Status (Active Production - Deployed & Published)**: Designed, validated, and published **[WinVDA](https://github.com/amirf147/winvda)** (Apache-2.0) as an independent clean-room library, completely replacing legacy `pyvda` across Caster production (`custom-setup` branch, commit `85feab8e`). Eliminates explorer restart crashes, apartment threading collisions, and synthetic sub-AUMID isolation.
* **Core Architecture & Breakthroughs**:
  * **Caster Voice Grammar & HUD Integration**: Bound commands `([toggle] pin | unpin) window [all work [spaces]]` and `([toggle] pin | unpin) app [all work [spaces]]` in `window_mgmt_rule.py`, routing user-facing state transitions through `printer.out` for instantaneous Caster HUD feedback.
  * **Root Cause Diagnosis of App Pinning Failure**: Diagnosed why `pin app` previously pinned only isolated secondary windows of Windows Terminal. Modern Windows Shell assigns hosted/XAML Island windows unique sub-AUMIDs suffixed with `~Wh~w<HEX_HWND>`, while Windows COM `IVirtualDesktopPinnedApps::PinAppID` performs exact string matching (`wcscmp`) against a flat registry table. Naive pass-through in `pyvda` caused secondary windows to pin their transient handle while leaving primary windows unpinned (and vice-versa).
  * **Zero Technical Debt / Upstream Library Refactor**: Kept Caster 100% free of band-aid workarounds. Implemented canonical `base_app_id` resolution in `pyvda.AppView`, pinned persistent application identities via `PinAppID(base_id)`, and pinned active sub-views in-memory via `PinView()` (preventing transient registry pollution and orphaned dead HWND keys).
  * **Active Window Synchronization (`sync_pinned_apps`)**: Added sub-millisecond synchronization into `VirtualDesktop.go()`, ensuring newly opened windows of pinned applications carry over across workspace transitions automatically.
  * **Cross-Framework Validation**: Empirically verified across heterogeneous application archetypes: Gecko (Waterfox profile-hash AUMIDs), Chromium/Electron (Antigravity IDE), and XAML Islands (Windows Terminal).
* **Key Documentation**:
  * 🌐 **[WinVDA Public Repository](https://github.com/amirf147/winvda)** *(Independent Clean-Room Engine)*
  * 🪟 **[WinVDA Realization & Caster Migration (006)](docs/pyvda/006_winvda_clean_room_engine_realization_and_caster_migration.md)** *(Production Milestone)*
  * 🪟 **[PyVDA Multi-Window & XAML Island Pinning Architecture (003)](docs/pyvda/003_pyvda_multi_window_xaml_island_pinning_architecture.md)**
  * 🪟 **[Adversarial Audit & Resilient Client Design (004)](docs/pyvda/004_adversarial_audit_and_hardened_com_architecture.md)** *(Native Shell Analysis, 4-Repo Benchmark & Zero-Cached-State Architecture)*
  * 🪟 **[Task View Pinning Internals (005)](docs/pyvda/005_task_view_pinning_internals_and_shell_reverse_engineering.md)**
  * 🎙️ **[Virtual Desktop Pinning & Grammar Ergonomics](docs/features/virtual_desktop_pinning_and_grammar_ergonomics.md)** *(Phonetic Misrecognition, Kaldi Trellis Priors & Syntactic Design)*
  * 🧠 **[Repository Brain (Canonical SSOT)](docs/context/repository-brain.md)**
  * 📜 **[Status Update History](status-update-history.md)**

### 2. Next-Iteration Modular Caster HUD & Real-Time Context Integration
* **Status (Active Exploration & Production Blueprint - Complete)**: Refactored and modernized the Caster Heads-Up Display (HUD) into a high-performance, modular 5-layer Clean Architecture overlay that provides instant visual feedback for speech recognition, microphone safety states, native OS window tracking, active contextual voice rules, and sub-window semantic interaction zones from the Active Desktop Context Engine (ADCE).
* **Core Architecture & Breakthroughs**:
  * **5-Layer Clean Architecture & Unidirectional Data Flow**: Decoupled presentation (`MainWindow`, `StatusBarWidget`, `ActiveRulesBarWidget`, `AdceBarWidget`), immutable domain state & pure reducers (`HudState`, `reduce_event`), cross-thread IPC (`SignalBridge`, Qt Signals), OS/context observers (`IFocusTracker`, `AdceTracker`), and speech engine integration.
  * **Zero-Polling Win32 Window Focus Tracking (`IFocusTracker`)**: Native `SetWinEventHook` (`EVENT_SYSTEM_FOREGROUND`, `EVENT_OBJECT_NAMECHANGE`) provides instantaneous (< 1 ms) window title and process tracking on mouse clicks and Alt+Tab without waiting for speech recognition.
  * **Decoupled ADCE Micro-Context & SSE Ingestion**: Dedicated `AdceTracker` ingests real-time semantic interaction zones (`{IntegratedTerminal}`, `{EditorCodeBuffer}`) over Server-Sent Events (SSE on port 8424), updating sub-pane clicks in ~10–20 ms. Stale context across process switches is actively guarded, and disconnected states cleanly render `⚪ ADCE [ADCE is not connected]`.
  * **Contextual Active Rules Resolution & Engine Noise Suppression**: Dynamically resolves active application rules (e.g. `[VS Code]`, `[IDE Terminal]`, `[PowerShell]`) with terminal host fuzzy matching, CCR companion rule resolution, and automatic suppression of engine merger artifacts (`Repeater1`, `PreparedRule`, `dictation_sink_rule`), providing clean `[Global Context]` and `[Microphone Sleeping]` states.
  * **Multi-Theme System & Dynamic Safety Glow**: 4 preset themes (`classic`, `frosted-dark`, `minimal-transparent`, `high-contrast`), custom `.qss` loading, multi-window stylesheet propagation, full `QMenu` styling, and priority border status glow (🟢 Listening $\succ$ 🔴 Sleeping $\succ$ 🟡 Drag Mode $\succ$ 🔵 Window Focus).
  * **Zero-Latency IPC Isolation**: Dedicated port allocation (Port 8338 for XML-RPC, Port 8339 for ndjson telemetry) with non-blocking drop-oldest queues (`queue.Queue(maxsize=1024)`) guaranteeing `< 0.001 ms` speech thread overhead.
  * **Ergonomics & Controls**: Direct header click-and-drag window movement, 'D' drag mode with arrow nudging, 'T' frameless toggle, system tray docking, font scaling, modal help/rules dialogs, and comprehensive voice/context-menu controls.
* **Key Documentation**:
  * 📋 **[Caster HUD Master Requirements & Specifications (005)](docs/caster_hud/005_caster_hud_requirements_and_specifications.md)** *(Authoritative SSoT)*
  * 🏛️ **[Caster HUD Clean Architecture Synthesis (009)](docs/caster_hud/009_caster_hud_architectural_review_and_clean_architecture_synthesis.md)**
  * 📜 **[Caster HUD Continuous Lessons Learned Timeline (007)](docs/caster_hud/007_caster_hud_lessons_learned_timeline.md)**
  * 🔄 **[ADCE Realtime Stream & Native Focus Decoupling (011)](docs/caster_hud/011_adce_realtime_stream_and_native_focus_decoupling_deep_dive.md)**
  * 🔬 **[Fine-Grained Context: Native OS vs ADCE Explainer (010)](docs/caster_hud/010_fine_grained_context_recognition_native_vs_adce_explainer.md)**
  * 🚀 **[Active Desktop Context Engine Repository](https://github.com/amirf147/active-desktop-context-engine)**

### 3. Native Taskbar HUD Windhawk Injection & Real-Time Telemetry Bridge (Active Exploration)
* **Status (Active Exploration & Prototype Diagnosis)**: Prototyping an in-process Windows 11 taskbar HUD extension via Windhawk (`caster-taskbar-hud.wh.cpp`), projecting real-time speech command feedback, ADCE semantic interaction zones, and active contextual rules directly into the Windows Shell adjacent to the system tray.
* **Core Architecture & Breakthroughs**:
  * **In-Process Shell XAML Injection**: Hooks `taskbar.dll` symbols (`CTaskBand::GetTaskbarHost`, `TaskbarHost::FrameHeight`, `TrayUI::StartTaskbar`) to acquire the root `FrameworkElement` XAML Island inside `Shell_TrayWnd`, dynamically hosting controls inside `SystemTrayFrameGrid`.
  * **Asynchronous Overlapped Named Pipe IPC**: Integrates an inbound pipe server (`\\.\pipe\CasterTaskbarHud`) consuming JSON telemetry in `< 0.5 ms`, marshaled to the taskbar UI thread via `WH_CALLWNDPROC` message hooks.
  * **Taskbar Button Collision Diagnosis & Unified Strip Pivot**: Diagnosed horizontal space starvation where three discrete pill boxes (`[Z: --]`, `[Rules: Global]`, `[Ready]`) consumed ~260–370px of width, causing direct overlap with open window buttons in `TaskListButtonPanel` (`WorkerW`). Formulated the architectural pivot to a single, compact command strip (~160px) displaying dynamic contextual telemetry strings.
  * **Telemetry Pipeline Diagnosis & Caster Printer Output Tap**: Identified why the initial prototype remained static on default fallback text. Caster's module loader discards non-standard hook files in `caster_user_content/hooks/` that lack `def get_hook():`. Formulated the alignment plan to tap directly into Caster's primary `printer.out` dispatcher (`DelegatingMessageHandler` / `HudPrintMessageHandler`), streaming live voice commands, ADCE zone transitions, and active rules to the taskbar HUD.
* **Key Documentation**:
  * 🖥️ **[Taskbar HUD Windhawk Injection & Telemetry Explainer (012)](docs/caster_hud/012_taskbar_hud_windhawk_mod_and_caster_bridge_explainer.md)** *(Architecture, RCA & Unified Strip Pivot)*
  * 📋 **[Caster HUD Master Requirements & Specifications (005)](docs/caster_hud/005_caster_hud_requirements_and_specifications.md)**
  * 📜 **[Status Update History](status-update-history.md)**

### 4. Native Win32 App Switcher & Tier 4 Taskbar Fail-Safe (Active Production v3.1)
* **Status (Active Production)**: Upgraded the **production focus engine** in [`caster_user_content/util/app_switcher.py`](caster_user_content/util/app_switcher.py) with a deterministic **Tier 4 Taskbar Keystroke Fail-Safe** (`Win+T` traversal / `Win+<N>`) to bypass Windows UIPI foreground locks when switching away from elevated windows.
* **Core Architecture & UIPI Delineation**:
  * **0–10ms Direct Fast Path (Tiers 1–3)**: Preserves sub-millisecond Win32 focus transitions via `SetForegroundWindow`, guarded `_alt_key_bypass()`, and `_attached_threads()` input queue attachment.
  * **UIPI Elevation Boundary & Tier 4 Fail-Safe**: Diagnosed complete focus escalation denial (Win32 Error 5: `Access is denied`) when an elevated process (e.g. Windhawk, Task Manager) owns the foreground. Lower-integrity speech processes cannot inject input or attach threads to higher-integrity windows. Replaced the obsolete Windows 10 UIA click fallback with read-only taskbar discovery (`get_taskbar_order`) and deterministic shell hotkey delegation (`Win+<N>` or `Win+T, home, right:..., enter`), allowing `explorer.exe` to execute the window switch.
  * **Critical Integrity Delineation**: While speech commands cannot drive or inject keystrokes into elevated windows (which Windows UIPI strictly forbids), focusing the unprivileged Caster HUD (`Caster HUD v 1.7.0`) or using Tier 4 shell traversal safely restores command execution for all standard user applications.
* **Key Docs**: [App Switcher Blueprint v3](docs/architecture/app_switcher_architectural_blueprint.md) | [Troubleshooting Findings & UIPI Post-Mortem](docs/troubleshooting/app_switcher_findings.md) | [App Switcher Focus Analysis](docs/architecture/app_switcher_focus_analysis.md) | [App Switcher Evolution Timeline](docs/history/app_switcher_timeline.md).

### 5. Historical Status & Archived Investigations
* **[Repository Timeline & 2-Year Technical Journey](docs/history/repository_timeline.md)**: Historical retrospective covering early repository foundations through mid-2026 (Kaldi ASR migration, desktop automation, AI IDE workflows, and initial window switching). *(Note on Scope: Captures foundations up to mid-2026; consult [Key Engineering](#-key-engineering--voice-automations) and [Recent Focus](#-technical-journey--recent-focus) above for current sub-millisecond Win32 v3, ADCE, and HUD systems).*
* **[Status Update History](status-update-history.md)**: Full archive of previous status updates (including Dynamic Sub-Window Grammar Activation, LexiconCode PR #881 investigation, Wayfinder session, Dragonfly BPC Fork Kaldi race condition fixes, and 2024 development logs).
* **[Kaldi Compiler & Engine Race Condition Post-Mortem](docs/troubleshooting/kaldi_crash_explanation.md)**: Root-cause debugging of Caster speech compiler crashes.
* **[Speech Stack Thread Architecture Report](docs/architecture/Speech_Stack_Thread_Architecture_and_Diagnostic_Report.md)**: Thread interaction models and execution boundaries.
* **[Technical Journey Log](docs/history/technical_journey.md)**: Active and archived engineering focus roadmap.

---

## 📂 Repository Structure

* `caster_user_content/rules/`: Live voice grammars, application-specific rules, and global macros.
* `caster_user_content/util/`: Supporting Python runtime utilities (e.g., `app_switcher.py`).
* `scripts/`: Development prototypes, test runners, and validation utilities (e.g., `context_poc.py`, `check_absolute_paths.py`).
* `docs/`: Comprehensive [Documentation Hub](docs/README.md) and [Repository Brain](docs/context/repository-brain.md).
* `.agents/`: Workflows and workspace rules for the Antigravity editor.
* `config/examples/`: Sanitized environment and settings templates. (Personal local configurations in `settings/` and `data/` are strictly untracked).
