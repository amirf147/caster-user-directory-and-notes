# Caster User Directory

A high-performance, Windows-only personal voice computing and automation toolkit built on Caster and Dragonfly. 

This repository houses custom voice grammars, low-latency window switching utilities, hardware IPC bridges, and in-depth engineering research into Windows UI Automation and speech engine threading.

> 📜 **[Repository Timeline & 2-Year Technical Journey](docs/history/repository_timeline.md)**  
> Explore the 27-month, 969-commit retrospective covering 4 distinct architectural eras (Kaldi ASR migration, desktop automation, AI IDE workflows, and 3-tier window switching).

---

## 🤖 .agents Folder

Contains workflows (such as `/commit`) and workspace configuration rules specifically for the **Antigravity** editor.

---

## ⚡ Key Engineering & Voice Automations

* **[App & Window Switcher v3](docs/features/app_switcher.md)**: Sub-millisecond direct Win32 window switching, workspace isolation, guarded keystate context managers, and automated tab navigation.
* **[App Switcher Evolution Timeline](docs/history/app_switcher_timeline.md)**: 2-year retrospective tracing the 5 evolution eras of window switching from Windhawk taskbar macros to native Win32 v3.
* **[App Switcher Architectural Blueprint (v3)](docs/architecture/app_switcher_architectural_blueprint.md)**: Authoritative technical specification, focus tier state machines, and sequence diagrams.
* **[Repository Timeline (2024–2026)](docs/history/repository_timeline.md)**: 27-month, 969-commit narrative breakdown and landmark commit history across 4 development eras.
* **[Foot Pedal & XML-RPC IPC Bridge](docs/features/foot_pedal.md)**: Hardware debouncing, smart tap/drag/scroll control for the Olympus RS31H foot pedal, paired with a local XML-RPC IPC bridge for thread-safe microphone toggling.
* **[Top Voice Automations Showcase](docs/features/top_voice_automations.md)**: Curated showcase of desktop, editor, and system voice workflows.
* **[LexiconCode Window Switching PR #881 Analysis](docs/features/lexicon_code_window_switching_functionality.md)**: Dynamic grammar (`DictList`) background polling architecture and diagnostic review.

---

## 🧭 Technical Journey & Recent Focus

Our ongoing work focuses on window switching, accessibility mechanics, and speech engine responsiveness:

### 1. Current Focus & Active Production: Sub-Millisecond Win32 App Switcher Refactor (v3)
* **Status Update (Currently Running in Production)**: We have just implemented and are actively running with the **v3 production architecture** for [`caster_user_content/util/app_switcher.py`](caster_user_content/util/app_switcher.py) (commit `8397b0c`).
* **What Was Implemented**:
  * **Direct Win32 Hot Path**: Replaced pywinauto wrapper overhead in the critical focus path with direct Win32 APIs (`SetForegroundWindow`, `BringWindowToTop`, `AllowSetForegroundWindow`), achieving instant 0–10ms focus transitions.
  * **Guarded Keystate Safety**: Wrapped foreground-lock bypasses and thread input attachments in guarded context managers (`_alt_key_bypass`, `_attached_threads`) with guaranteed nested `finally` release of `VK_NONE` (`0xFF`) and `VK_MENU`, eliminating sticky Alt keys, menu bar lockups, and thread queue deadlocks.
  * **Encapsulated `AliasRegistry`**: Refactored alias dictionary persistence and stale handle pruning into an encapsulated `AliasRegistry` class.
  * **10ms Micro-Polling**: Replaced coarse sleep intervals with non-blocking 10ms micro-polling in `verify_focus(target_hwnd)`.
  * **Elimination of Brittle Macros**: Completely removed legacy `Win+T` taskbar keyboard traversal macros.
* **Key Documentation**:
  * 🏗️ **[App Switcher Architectural Blueprint (v3)](docs/architecture/app_switcher_architectural_blueprint.md)**
  * 📜 **[App Switcher Evolution Timeline](docs/history/app_switcher_timeline.md)**
  * 📖 **[App Switcher Feature Guide](docs/features/app_switcher.md)**

### 2. LexiconCode Window Switching Investigation
* **Active Evaluation**: Evaluating and documenting the historical window management pull request developed by LexiconCode, which used dynamic grammar (`DictList`) background polling to continuously index open window titles for voice switching.
* **PR Reference**: [Caster PR #881 (LexiconCode Window Switching)](https://github.com/dictation-toolbox/Caster/pull/881)
* **Technical Feature Guide**: [LexiconCode Window Switching Functionality](docs/features/lexicon_code_window_switching_functionality.md)

### 3. Wayfinder Research Session: App Switching & UIA Threading Investigation
* **Research Context**: A structured research session (using the Wayfinder agentic research method) investigating perceived freezes in `app_switcher.py` and UIA/COM threading performance across speech stacks.
* **Empirical Findings**: Discovered through empirical telemetry (`ca5dc70`) that perceived hangs were caused by Windows PowerShell QuickEdit mode pausing standard output (`stdout`) during console logging, alongside deep mapping of COM threading apartments (STA vs. MTA).
* **Key Docs & Code**:
  * Feature Guide: [App & Window Switcher Documentation](docs/features/app_switcher.md)
  * Session Index: [Wayfinder UIA & Threading Research Directory](docs/wayfinder-uia-threading/map.md)
  * Rule & Utility Code: [window_switching.py](caster_user_content/rules/global/window_switching.py) & [app_switcher.py](caster_user_content/util/app_switcher.py)

### 4. Historical Status & Archived Investigations
* **[Kaldi Compiler & Engine Race Condition Post-Mortem](docs/troubleshooting/kaldi_crash_explanation.md)**: Root-cause debugging of Caster speech compiler crashes and synchronization issues.
* **[Speech Stack Thread Architecture Report](docs/architecture/Speech_Stack_Thread_Architecture_and_Diagnostic_Report.md)**: Diagnostic breakdown of Dragonfly/Kaldi thread interaction models and execution boundaries.
* **[Repository Timeline & 2-Year Git History](docs/history/repository_timeline.md)**: Complete chronological engineering log and architectural evolution across 4 distinct eras.
* **[Technical Journey Log](docs/history/technical_journey.md)**: Active and archived engineering focus roadmap.

---

## 📂 Repository Structure

* `caster_user_content/rules/`: Live voice grammars, application-specific rules, and global macros.
* `caster_user_content/util/`: Supporting Python runtime utilities (e.g., `app_switcher.py`).
* `docs/`: Comprehensive [Documentation Hub](docs/README.md) and [Repository Brain](docs/context/repository-brain.md).
* `.agents/`: Workflows and workspace rules for the Antigravity editor.
* `config/examples/`: Sanitized environment and settings templates. (Personal local configurations in `settings/` and `data/` are strictly untracked).
