# Caster User Directory

A high-performance, Windows-only personal voice computing and automation toolkit built on Caster and Dragonfly. 

This repository houses custom voice grammars, low-latency window switching utilities, hardware IPC bridges, and in-depth engineering research into Windows UI Automation, speech engine threading, and real-time desktop context tracking.

> 📜 **[Repository Timeline & 2-Year Technical Journey](docs/history/repository_timeline.md)**  
> Explore the 27-month, 969-commit retrospective covering 4 distinct architectural eras (Kaldi ASR migration, desktop automation, AI IDE workflows, and 3-tier window switching).

---

## 🤖 .agents Folder

Contains workflows (such as `/commit`) and workspace configuration rules specifically for the **Antigravity** editor.

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

### 1. Current Focus: Active Desktop Context Engine (ADCE) & Accessibility MCP (v2.1 PoC & v3 Caching Architecture)
* **Status Update (Active Prototype & Architecture)**: We have built and are actively validating the **Active Desktop Context Engine (ADCE)** live monitor (`scripts/context_poc.py`), launched via the voice rule `"launch context engine"` (`caster_user_content/rules/global/context_engine_launcher.py`).
* **What Was Implemented & Discovered**:
  * **Event-Driven OS Hooks**: Zero-polling Win32 event hooks (`SetWinEventHook` listening to `EVENT_SYSTEM_FOREGROUND` and `EVENT_OBJECT_FOCUS`), running in a COM Multithreaded Apartment (MTA) with 0% idle CPU usage.
  * **Deep Tab Discovery & Active Item Marking**: Comprehensive tab extraction traversing top-level windows down to depth 14 across Waterfox, Chrome, Firefox, and VS Code/Antigravity IDE, with active tab identification via `SelectionItemPattern`, legacy MSAA state bitmasks, and focus heuristics.
  * **Root Window Anchoring**: Fixed Electron/Gecko `DocumentControl` trapping by anchoring to top-level Win32 `GetForegroundWindow()` handles.
  * **PyVDA COM Resiliency**: Documented and verified `pyvda`'s `@_com_retry` and `_refresh()` mechanisms for recovering from `RPC_S_SERVER_UNAVAILABLE` and `RPC_E_DISCONNECTED` errors when `explorer.exe` restarts.
  * **Two-Tier State Caching Blueprint**: Designed the v3 caching architecture (Macro Sync on window change, Micro Mutation on focus change) to eliminate redundant deep UIA tree traversals.
* **Key Documentation**:
  * 🧠 **[ADCE Living Context Hub](docs/accessibility_mcp/CONTEXT.md)**
  * 🔬 **[Real-World Observations & Caching Architecture (008)](docs/accessibility_mcp/008_real_world_observations_and_caching_architecture.md)**
  * 🗂️ **[Tab Extraction & Context Representation (007)](docs/accessibility_mcp/007_tab_extraction_and_context_representation.md)**
  * ⚙️ **[PyVDA COM Lifecycle Analysis (001)](docs/pyvda/001_pyvda_rpc_and_com_lifecycle_analysis.md)**
  * 🖥️ **[Caster HUD Threading Primer (001)](docs/caster_hud/001_caster_hud_architecture_and_threading_primer.md)**

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
