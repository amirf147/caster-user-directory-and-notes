# Caster User Directory

A high-performance, Windows-only personal voice computing and automation toolkit built on Caster and Dragonfly. 

This repository houses custom voice grammars, low-latency window switching utilities, hardware IPC bridges, and in-depth engineering research into Windows UI Automation, speech engine threading, and real-time desktop context tracking.

> 📜 **[Repository Timeline & 2-Year Technical Journey](docs/history/repository_timeline.md)**  
> Explore the 27-month, 969-commit retrospective covering 4 distinct architectural eras (Kaldi ASR migration, desktop automation, AI IDE workflows, and 3-tier window switching).

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
* **[PyVDA COM Lifecycle & Threading Analysis](docs/pyvda/001_pyvda_rpc_and_com_lifecycle_analysis.md)**: Deep analysis of Windows Virtual Desktop COM interfaces, RPC error recovery (`@_com_retry`), and STA/MTA threading rules.
* **[Foot Pedal & XML-RPC IPC Bridge](docs/features/foot_pedal.md)**: Hardware debouncing, smart tap/drag/scroll control for the Olympus RS31H foot pedal, paired with a local XML-RPC IPC bridge for thread-safe microphone toggling.
* **[Top Voice Automations Showcase](docs/features/top_voice_automations.md)**: Curated showcase of desktop, editor, and system voice workflows.

---

## 🧭 Technical Journey & Recent Focus

Our ongoing work focuses on real-time desktop context tracking, window switching, accessibility mechanics, and speech engine responsiveness:

### 1. Active Focus: Next-Iteration Modular Caster HUD & Real-Time Context Integration
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

### 2. Sub-Millisecond Native Win32 App Switcher Refactor (Active Production v3)
* **Status (Active Production)**: Running with the **v3 production architecture** for [`caster_user_content/util/app_switcher.py`](caster_user_content/util/app_switcher.py) (commit `8397b0c`).
* **Highlights**: Instant 0–10ms focus transitions via direct Win32 APIs (`SetForegroundWindow`), guarded keystate context managers (`_alt_key_bypass`, `_attached_threads`), and encapsulated `AliasRegistry` persistence.
* **Key Docs**: [App Switcher Blueprint v3](docs/architecture/app_switcher_architectural_blueprint.md) | [App Switcher Evolution Timeline](docs/history/app_switcher_timeline.md) | [App Switcher Feature Guide](docs/features/app_switcher.md).

### 3. Historical Status & Archived Investigations
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
