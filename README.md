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

* **[Active Desktop Context Engine (ADCE) & MCP Hub](docs/accessibility_mcp/CONTEXT.md)**: Real-time, event-driven OS state tracking (`scripts/context_poc.py`), tab discovery across browsers and IDEs, Virtual Desktop awareness, and Model Context Protocol (MCP) integration.
* **[App & Window Switcher v3](docs/features/app_switcher.md)**: Sub-millisecond direct Win32 window switching, workspace isolation, guarded keystate context managers, and automated tab navigation.
* **[App Switcher Evolution Timeline](docs/history/app_switcher_timeline.md)**: 2-year retrospective tracing the 5 evolution eras of window switching from Windhawk taskbar macros to native Win32 v3.
* **[App Switcher Architectural Blueprint (v3)](docs/architecture/app_switcher_architectural_blueprint.md)**: Authoritative technical specification, focus tier state machines, and sequence diagrams.
* **[PyVDA COM Lifecycle & Threading Analysis](docs/pyvda/001_pyvda_rpc_and_com_lifecycle_analysis.md)**: Deep analysis of Windows Virtual Desktop COM interfaces, RPC error recovery (`@_com_retry`), and STA/MTA threading rules.
* **[Caster HUD Architecture & Threading Primer](docs/caster_hud/001_caster_hud_architecture_and_threading_primer.md)**: Educational breakdown of out-of-process Qt rendering, XML-RPC IPC, and asynchronous `postEvent` dispatching.
* **[Foot Pedal & XML-RPC IPC Bridge](docs/features/foot_pedal.md)**: Hardware debouncing, smart tap/drag/scroll control for the Olympus RS31H foot pedal, paired with a local XML-RPC IPC bridge for thread-safe microphone toggling.
* **[Top Voice Automations Showcase](docs/features/top_voice_automations.md)**: Curated showcase of desktop, editor, and system voice workflows.
* **[LexiconCode Window Switching PR #881 Analysis](docs/features/lexicon_code_window_switching_functionality.md)**: Dynamic grammar (`DictList`) background polling architecture and diagnostic review.

---

## 🧭 Technical Journey & Recent Focus

Our ongoing work focuses on real-time desktop context tracking, window switching, and accessibility mechanics:

### 1. Active Focus: Dragonfly Recognition Observers, `FuncContext` & ADCE Dynamic Grammar Spiking
* **Status (Active Exploration & Prototyping)**: Nothing is finalized or locked in yet; we are actively exploring and testing dynamic, fine-grained sub-window grammar activation (e.g. dynamically activating terminal rules when focused in VS Code's integrated terminal vs code editing rules in Monaco) without introducing speech recognition latency.
* **Core Architecture Under Test**:
  * **Dragonfly `FuncContext` & Recognition Observers**: Investigating how Dragonfly evaluates `FuncContext` synchronously on `process_begin` and evaluating engine-wide `RecognitionObserver` lifecycle hooks (`on_begin`, `on_recognition`, `on_failure`) for telemetry and HUD state synchronization.
  * **Decoupled Telemetry Architecture**: Testing a dual-plane design where the standalone [Active Desktop Context Engine (ADCE)](https://github.com/amirf147/active-desktop-context-engine) resolves element-level interaction zones in the background and streams snapshots over HTTP/SSE, allowing `FuncContext` to execute sub-microsecond O(1) RAM checks (< 0.0001 ms) on the speech thread.
  * **Race Condition Verification**: Testing the empirical race condition window identified in discussions with upstream maintainer LexiconCode (comparing human vocal onset latency of ~250–450 ms against ADCE's 5–15 ms FlaUI `CacheRequest` background extractions).
* **Key Documentation**:
  * 🔬 **[Dragonfly Recognition Observers & Functional Contexts](docs/framework_explainers/dragonfly_recognition_observers_and_functional_contexts.md)** *(Master Explainer & Blueprint)*
  * 🧠 **[ADCE Living Context Hub](docs/accessibility_mcp/CONTEXT.md)**
  * 📑 **[UI Automation Structures Reference (017)](docs/accessibility_mcp/017_ui_automation_tree_structures_and_target_zones_reference.md)**
  * 🚀 **[Active Desktop Context Engine Repository](https://github.com/amirf147/active-desktop-context-engine)**

### 2. Sub-Millisecond Native Win32 App Switcher Refactor (Active Production v3)
* **Status (Active Production)**: Running with the **v3 production architecture** for [`caster_user_content/util/app_switcher.py`](caster_user_content/util/app_switcher.py) (commit `8397b0c`).
* **Highlights**: Instant 0–10ms focus transitions via direct Win32 APIs (`SetForegroundWindow`), guarded keystate context managers (`_alt_key_bypass`, `_attached_threads`), and encapsulated `AliasRegistry` persistence.
* **Key Docs**: [App Switcher Blueprint v3](docs/architecture/app_switcher_architectural_blueprint.md) | [App Switcher Evolution Timeline](docs/history/app_switcher_timeline.md) | [App Switcher Feature Guide](docs/features/app_switcher.md).

### 3. LexiconCode Window Switching Investigation
* **Active Evaluation**: Documenting the historical pull request by LexiconCode using dynamic grammar (`DictList`) background polling.
* **Reference**: [Caster PR #881](https://github.com/dictation-toolbox/Caster/pull/881) | [Feature Guide](docs/features/lexicon_code_window_switching_functionality.md).

### 4. Historical Status & Archived Investigations
* **[Status Update History](status-update-history.md)**: Full archive of previous status updates (including the Wayfinder session, Dragonfly BPC Fork Kaldi race condition fixes, and 2024 development logs).
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
