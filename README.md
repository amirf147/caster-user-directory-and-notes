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

### 1. Current Focus: Epistemic Recalibration & Adversarial Review (Phase 3 Gate 3 Micro-Spikes)
* **Status Update (Epistemic Circuit Breaker & Falsification Spikes)**: In accordance with **[015: Epistemic Recalibration](docs/accessibility_mcp/015_recalibration_and_adversarial_architecture_review.md)**, we have paused the premature compiled C# daemon handover (`014`) to prevent solution bias. We have established a permanent **4-Gate Epistemic Gating Protocol** and are executing empirical micro-spikes to falsify core physical assumptions before committing to any architecture.
* **What Was Concluded & Synthesized**:
  * **The Jumping-the-Gun Post-Mortem**: Acknowledged teleological solution bias where multi-second browser DOM traversal latencies (6,800 nodes) triggered an immediate leap to a multi-runtime C# rewrite (`014`) without empirical proof that UIA 3 caching avoids underlying browser IPC stalls.
  * **Adversarial Critique & 3 Mutually Exclusive Options**: Evaluated three distinct architectural paths with fatal flaws and hidden operational assumptions: (A) Direct Browser Extension / Native Messaging, (B) Standalone C# .NET 10 FlaUI 5 Daemon, and (C) Pruned In-Process Python Win32/UIA.
  * **4-Gate Epistemic Protocol**: Codified workspace rules and an automated workflow (`.agents/workflows/adversarial-architecture-review.md`) enforcing: (1) Physical logs only → (2) Adversarial red-team → (3) <50-line micro-spike → (4) Architectural blueprint.
  * **Next Empirical Step (Gate 3 Micro-Spikes)**: Measuring raw latency across two minimal scripts: compiled C# FlaUI 5 `CacheRequest` (`spike_csharp_flaui_cache.cs`) vs shallow Win32 top-level caching in Python (`spike_win32_shallow_python.py`).
* **Key Documentation**:
  * 🧠 **[ADCE Living Context Hub](docs/accessibility_mcp/CONTEXT.md)**
  * 🛡️ **[Epistemic Recalibration & Adversarial Review (015)](docs/accessibility_mcp/015_recalibration_and_adversarial_architecture_review.md)**
  * 🚀 **[C# Context Daemon Handover Blueprint (014)](docs/accessibility_mcp/014_csharp_daemon_handover_and_skill_spec.md)** *(Exploratory Blueprint - Paused)*
  * 📑 **[Empirical Post-Mortem & WinEvent Diagnostics (013)](docs/accessibility_mcp/013_v23_empirical_postmortem_and_event_diagnostics.md)**
  * 📊 **[Live Empirical Tab Extraction Report (012)](docs/accessibility_mcp/012_empirical_tab_extraction_report.md)**
  * 🔬 **[Landscape Review, FlaUI & Dual-Plane Architecture (011)](docs/accessibility_mcp/011_flaui_evaluation_and_dual_plane_architecture.md)**
  * 📈 **[Live Telemetry Benchmarks & Multi-Container Diagnostics (010)](docs/accessibility_mcp/010_telemetry_benchmarks_and_live_findings.md)**
  * ⚙️ **[PyVDA COM Lifecycle Analysis (001)](docs/pyvda/001_pyvda_rpc_and_com_lifecycle_analysis.md)** | **[Core Architecture Critique (002)](docs/pyvda/002_pyvda_core_architecture_and_threading_critique.md)**

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
