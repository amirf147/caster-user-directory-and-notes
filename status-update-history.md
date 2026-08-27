## Archived Status Update: Initial Exploration of Dragonfly Recognition Observers & ADCE Spiking (August 2026)

### Initial Exploration & Architecture Formulation
Explored dynamic, fine-grained sub-window grammar activation using Dragonfly `FuncContext` and `RecognitionObserver` connected to the standalone Active Desktop Context Engine (ADCE). Formulated the decoupled dual-plane architecture and analyzed the race condition window identified by upstream maintainer LexiconCode.

#### Related Documentation:
* 🔬 **[Dragonfly Recognition Observers & Functional Contexts](docs/framework_explainers/dragonfly_recognition_observers_and_functional_contexts.md)**
* 🧠 **[ADCE Living Context Hub](docs/accessibility_mcp/CONTEXT.md)**
* 📑 **[UI Automation Structures Reference (017)](docs/accessibility_mcp/017_ui_automation_tree_structures_and_target_zones_reference.md)**
* 🚀 **[Active Desktop Context Engine Repository](https://github.com/amirf147/active-desktop-context-engine)**

---

## Archived Status Update: ADCE Research Completion & Standalone Engine Handover (August 2026)

### Handover to Standalone ADCE Repository
Foundational accessibility research in Caster concluded with the completion of Gate 3 empirical micro-spikes (Docs `016`–`017`) and epistemic gap analysis (Doc `018`). Active engine development officially transitioned to the standalone **[`active-desktop-context-engine`](https://github.com/amirf147/active-desktop-context-engine)** repository.

* **Empirical Validation Complete (Docs 016 & 017)**: Disproved the hypothesis that UIA cannot extract tabs/focus in real-time; demonstrated that targeted container queries (e.g. `tabs-container` for Antigravity, `tabs normal` for Waterfox) execute in **10–15 ms** with zero recursive DOM crawling.
* **Single Source of Truth (SSOT)**: Codified exact UIA node hierarchies, class names, and target zones for Antigravity IDE, Waterfox, and Windows 11 File Explorer in [Doc 017](docs/accessibility_mcp/017_ui_automation_tree_structures_and_target_zones_reference.md).
* **Epistemic Gaps & Requirements (Doc 018)**: Defined the 5 Universal Desktop Framework Archetypes, dynamic heuristic discovery pipeline, time-series storage options (SQLite WAL vs DuckDB), and engine performance SLAs.
* **Caster Integration Role**: Caster acts as a high-speed MCP consumer querying the local C# ADCE daemon rather than running a duplicate scraping loop.

#### Related Documentation:
* 🧠 **[ADCE Living Context Hub](docs/accessibility_mcp/CONTEXT.md)**
* 📋 **[Epistemic Gaps, Dynamic Discovery & Engine PRS (018)](docs/accessibility_mcp/018_epistemic_gaps_dynamic_app_discovery_and_requirements.md)**
* 📑 **[UI Automation SSOT & Target Zones Reference (017)](docs/accessibility_mcp/017_ui_automation_tree_structures_and_target_zones_reference.md)**
* 📊 **[Micro-Spike 2 Telemetry & Comparative Analysis (016)](docs/accessibility_mcp/016_micro_spike_2_win32_shallow_python_telemetry.md)**
* 🛡️ **[Epistemic Recalibration & Adversarial Review (015)](docs/accessibility_mcp/015_recalibration_and_adversarial_architecture_review.md)**
* 🚀 **[Standalone ADCE Repository (GitHub)](https://github.com/amirf147/active-desktop-context-engine)**

---

## Archived Status Update: ADCE Epistemic Recalibration & Gate 3 Micro-Spikes (August 2026)

### Epistemic Circuit Breaker & Gate 3 Micro-Spikes Execution
In accordance with **[015: Epistemic Recalibration](docs/accessibility_mcp/015_recalibration_and_adversarial_architecture_review.md)**, we paused premature solution lock-in and executed empirical micro-spikes comparing pure Win32/Python shallow context (< 1 ms) against C# FlaUI 5 container-scoped tab extraction (~10 ms):

* **Micro-Spike 1 (`ADCE.Spikes` / C# .NET 10 + FlaUI 5)**: Validated direct container targeting and batch UIA3 extraction across running Gecko / Electron instances (30 tabs in 10.17 ms).
* **Micro-Spike 2 (`spike_win32_shallow_python.py` / Python 3.10)**: Measured pure Win32 C-call envelope extraction (0.8 µs) and shallow UIA focus retrieval (0.66 ms) with zero recursive tree traversal.
* **UI Automation Hierarchy SSOT (Doc 017)**: Codified the definitive structural maps and container queries for Antigravity IDE (`tabs-container`, `monaco-breadcrumbs`, `actions-container`), Waterfox (`tabs normal`), and Windows 11 File Explorer (`TabView`, `PART_BreadcrumbBar`).
* **Epistemic Gaps & Requirements (Doc 018)**: Interrogated knowledge gaps regarding dynamic application adaptation, multi-window topologies, and time-series persistence (SQLite vs DuckDB), transitioning active engine implementation to the standalone [`active-desktop-context-engine`](https://github.com/amirf147/active-desktop-context-engine) repository.

#### Related Documentation:
* 🧠 **[ADCE Living Context Hub](docs/accessibility_mcp/CONTEXT.md)**
* 🛡️ **[Epistemic Recalibration & Adversarial Review (015)](docs/accessibility_mcp/015_recalibration_and_adversarial_architecture_review.md)**
* 📊 **[Micro-Spike 2 Python Telemetry & Comparative Analysis (016)](docs/accessibility_mcp/016_micro_spike_2_win32_shallow_python_telemetry.md)**
* 📑 **[UI Automation SSOT & Target Zones Reference (017)](docs/accessibility_mcp/017_ui_automation_tree_structures_and_target_zones_reference.md)**
* 📋 **[Epistemic Gaps, Dynamic Discovery & Engine PRS (018)](docs/accessibility_mcp/018_epistemic_gaps_dynamic_app_discovery_and_requirements.md)**

---

## Archived Status Update: Active Desktop Context Engine (ADCE) & Accessibility MCP (v2.2–v2.3 Exploratory PoC & Empirical Post-Mortem - August 2026)

### Exploratory Python Prototype & Empirical Benchmarks
We conducted comprehensive empirical testing of the **Active Desktop Context Engine (ADCE v2.2–v2.3)** live monitor (`scripts/context_poc.py`), benchmark test harness (`scripts/test_tab_benchmark.py`), and voice launcher (`caster_user_content/rules/global/context_engine_launcher.py`).

* **High-Resolution Execution Telemetry**: Integrated microsecond performance timers (`time.perf_counter()`) and live traversal metrics (`nodes_scanned`, `max_depth_reached`, `hwnd_class`), logging structured telemetry events to `data/adce_telemetry.jsonl`.
* **Console QuickEdit Protection**: Automatically cleared `ENABLE_QUICK_EDIT_MODE` via `kernel32.SetConsoleMode` at startup to eliminate click-to-pause terminal freezes.
* **Empirical Traversal Benchmarks & Pruning Analysis**: Quantified real-world traversal latencies across Electron (62 nodes, 120ms), Gecko/Waterfox (6,806 nodes, 5.9s unpruned vs 107 nodes, 113ms pruned), and Windows 11 File Explorer (618 nodes, 723ms).
* **Multi-Container & Tree Style Tab Findings**: Uncovered the structural tension between blanket `DocumentControl` pruning and WebExtension sidebar containers (Tree Style Tab), proving that manual recursive crawling in Python leads to fragile heuristic debt.
* **WinEvent Message Pump & COM Concurrency Limits**: Diagnosed console self-monitoring feedback loops and leading-edge debounce drop races, establishing the empirical foundation for transitioning to a compiled native C# UIA 3 engine.

#### Related Documentation:
* 🧠 **[ADCE Living Context Hub](docs/accessibility_mcp/CONTEXT.md)**
* 📑 **[Empirical Post-Mortem & WinEvent Diagnostics (013)](docs/accessibility_mcp/013_v23_empirical_postmortem_and_event_diagnostics.md)**
* 📊 **[Live Empirical Tab Extraction Report (012)](docs/accessibility_mcp/012_empirical_tab_extraction_report.md)**
* 🔬 **[Landscape Review, FlaUI & Dual-Plane Architecture (011)](docs/accessibility_mcp/011_flaui_evaluation_and_dual_plane_architecture.md)**
* 📈 **[Live Telemetry Benchmarks & Multi-Container Diagnostics (010)](docs/accessibility_mcp/010_telemetry_benchmarks_and_live_findings.md)**
* 🔭 **[Live Telemetry, Observability & Tab Diagnostics (009)](docs/accessibility_mcp/009_live_telemetry_and_tab_diagnostics.md)**
* 🗂️ **[Real-World Observations & Caching Architecture (008)](docs/accessibility_mcp/008_real_world_observations_and_caching_architecture.md)**
* 📑 **[Tab Extraction & Context Representation (007)](docs/accessibility_mcp/007_tab_extraction_and_context_representation.md)**

---

## Archived Status Update: Active Desktop Context Engine (ADCE) & Accessibility MCP (v2.1 PoC & v3 Caching Architecture - August 2026)

### Initial Prototype & Foundations

We built and validated the **Active Desktop Context Engine (ADCE)** live monitor (`scripts/context_poc.py`), launched via the voice rule `"launch context engine"` (`caster_user_content/rules/global/context_engine_launcher.py`).

* **Event-Driven OS Hooks**: Zero-polling Win32 event hooks (`SetWinEventHook` listening to `EVENT_SYSTEM_FOREGROUND` and `EVENT_OBJECT_FOCUS`), running in a COM Multithreaded Apartment (MTA) with 0% idle CPU usage.
* **Deep Tab Discovery & Active Item Marking**: Comprehensive tab extraction traversing top-level windows down to depth 14 across Waterfox, Chrome, Firefox, and VS Code/Antigravity IDE, with active tab identification via `SelectionItemPattern`, legacy MSAA state bitmasks, and focus heuristics.
* **Root Window Anchoring**: Fixed Electron/Gecko `DocumentControl` trapping by anchoring to top-level Win32 `GetForegroundWindow()` handles.
* **PyVDA COM Resiliency**: Documented and verified `pyvda`'s `@_com_retry` and `_refresh()` mechanisms for recovering from `RPC_S_SERVER_UNAVAILABLE` and `RPC_E_DISCONNECTED` errors when `explorer.exe` restarts.
* **Two-Tier State Caching Blueprint**: Designed the v3 caching architecture (Macro Sync on window change, Micro Mutation on focus change) to eliminate redundant deep UIA tree traversals.

#### Related Documentation:
* 🧠 **[ADCE Living Context Hub](docs/accessibility_mcp/CONTEXT.md)**
* 🔬 **[Real-World Observations & Caching Architecture (008)](docs/accessibility_mcp/008_real_world_observations_and_caching_architecture.md)**
* 🗂️ **[Tab Extraction & Context Representation (007)](docs/accessibility_mcp/007_tab_extraction_and_context_representation.md)**
* ⚙️ **[PyVDA COM Lifecycle Analysis (001)](docs/pyvda/001_pyvda_rpc_and_com_lifecycle_analysis.md)**
* 🖥️ **[Caster HUD Threading Primer (001)](docs/caster_hud/001_caster_hud_architecture_and_threading_primer.md)**

---

## Archived Status Update: Sub-Millisecond Native Win32 App Switcher v3 (August 2026)

### Production Deployment & Architectural Breakthroughs

We successfully implemented and deployed the **v3 production architecture** for [`caster_user_content/util/app_switcher.py`](caster_user_content/util/app_switcher.py) (commit `8397b0c`).

* **Direct Win32 Hot Path**: Replaced pywinauto wrapper overhead in the critical focus path with direct Win32 APIs (`SetForegroundWindow`, `BringWindowToTop`, `AllowSetForegroundWindow`), achieving instant 0–10ms focus transitions.
* **Guarded Keystate Safety**: Wrapped foreground-lock bypasses and thread input attachments in guarded context managers (`_alt_key_bypass`, `_attached_threads`) with guaranteed nested `finally` release of `VK_NONE` (`0xFF`) and `VK_MENU`, eliminating sticky Alt keys, menu bar lockups, and thread queue deadlocks.
* **Encapsulated `AliasRegistry`**: Refactored alias dictionary persistence and stale handle pruning into an encapsulated `AliasRegistry` class managing `caster_user_content/window_aliases.json`.
* **10ms Micro-Polling**: Replaced coarse sleep intervals with non-blocking 10ms micro-polling in `verify_focus(target_hwnd)`.
* **Elimination of Brittle Macros**: Completely removed legacy `Win+T` taskbar keyboard traversal macros.

#### Related Architectural Documents:
* 🏗️ **[App Switcher Architectural Blueprint (v3)](docs/architecture/app_switcher_architectural_blueprint.md)**
* 📜 **[App Switcher Evolution Timeline](docs/history/app_switcher_timeline.md)**
* 📖 **[App Switcher Feature Guide](docs/features/app_switcher.md)**

---

## Archived Status Update: Wayfinder Session & Dragonfly BPC Fork (August 2026)

### App Switching & UIA Threading Investigation (Wayfinder Session)

We recently investigated window switching and responsiveness in Caster (`app_switcher.py`). During this research, we explored COM threading mechanics (STA vs. MTA), UIA fallback mechanisms, and multi-process architectures across screen readers (NVDA), automation frameworks (Terminator, UFO), Dragonfly, and Caster core.

**Key Finding (App Switcher):** Our empirical testing of `app_switcher.py` revealed that perceived "hard freezes" during app switching were not caused by COM deadlocks or threading issues, but rather by Windows PowerShell **QuickEdit mode** pausing standard output (`stdout`) when Caster logged messages. 

*Note on Text Editing:* While `text_editing.py` and UIA-based text selection remain an interest for future exploration to build better grammars and extract value, our empirical investigation and findings so far pertain specifically to `app_switcher.py`.

We left open the possibility of building a custom out-of-process C# MCP server for experimental tool development and future AI agent compatibility. However, our next step was to conduct further empirical testing on `app_switcher.py` in-process to thoroughly double-check its real-world robustness and evaluate whether an out-of-process architecture is truly required.

#### Key Session Synthesis Documents
The research and analysis from this session have been synthesized into primary reference documents:
- **[Claude Critique: Verified Takeaways & Fact-Checked Corpus](docs/wayfinder-uia-threading/claude-critique-verified-takeaways.md)**: A fact-checked evaluation by Claude 3.5 Sonnet distilling load-bearing findings, verified Win32/UIA technical facts, and unconfirmed hypotheses across the 71-file Wayfinder corpus.
- **[Codex Context Extract: Operational Baseline](docs/wayfinder-uia-threading/codex-context-extract.md)**: A structured context synthesis by Codex mapping active constraints, core requirements, and benchmark data.
- **[Wayfinder UIA & Threading Session Directory](docs/wayfinder-uia-threading/map.md)**: Active decision tracking map, tickets, and deep-dive educational research breakdowns.
- **[ADR_001_Background_Worker_Pool.md](docs/architecture/ADR_001_Background_Worker_Pool.md)**: *(Deprecated)* Initial decision record for generic thread pool approach.
- **[Speech Stack Thread Architecture & Diagnostic Report](docs/architecture/Speech_Stack_Thread_Architecture_and_Diagnostic_Report.md)**: Initial thread architecture diagnostic report.

---

### Dragonfly BPC Fork & Kaldi Investigation

Tracing and resolving the Kaldi engine race condition in the `dragonfly-bpc-oss` fork (v1.0.0rc2) to enable testing of the UIA accessibility features.

Detailed documentation from Antigravity agent sessions:
- [kaldi_crash_explanation.md](docs/troubleshooting/kaldi_crash_explanation.md): Explains the `destroy()` use-after-free root cause and the queue-safety patch.
- [kaldi_race_condition_answers.md](docs/troubleshooting/kaldi_race_condition_answers.md): Explains the rule key identity, synchronous C++ allocations, and git history behind the race condition.
- [dragonfly_rule_deepdive.md](docs/framework_explainers/dragonfly_rule_deepdive.md): A step-by-step roadmap for print-tracing how Dragonfly rules enable and disable.

---

## Current Status (25 July 2024, see status-updates-history.md for previous status updates) 
Still using this full time, adding or modifying rules as needs arise. Switched to using the talon alphabet except a few letters, see words.txt in transformers directory. I've noticed that a lot of the transforms that I did in words.txt had to slowly be undone because they made sense in windows speech recognition because of poor recognition accuracy but as smy capabilities increased in using Caster and hs I've been increasing my command vocabulary, I've noticed that a lot of the specs are the words they are for good reason, for example because ofnot colliding with other specs or maybe just less voice straining. I'm thinking I might soon  
revert to the default spec, "bird", for jumping back one word (control + left arrow), as I have currently been using "blush" which was less misrecognized in windows speech recognition. I've noticed that it can take up to a week and sometimes longer to get used to a new spec that replaces one that you've been used to saying for a long time. It is however worth the struggle in the long run if it is an improvement in either reducing complexity or reducing voice strain. 

## Current Status (30 May 2024) 
I have added a significant portion of the core customizations that I require for enabling my full time usage of this accessibility tool. I am still switching between usage of kaldi-dragonfly-grammars, wsrmacros and this. I have noticed that there is a little noticeable latency increase when using caster as opposed to just using bare-bones dragonfly but I believe the benefits of using caster will ultimately outweigh this latency increase.

## 12 May 2024
I am still using and developing https://github.com/amirf147/kaldi-dragonfly-gammars for full handsfree computer control. I just created this repository to document/store my Caster user directory (https://caster.readthedocs.io/en/latest/readthedocs/User_Dir/Caster_User_Dir/) as I begin learning and using Caster. It may be that I eventually switch to just using Caster for my computer control needs.
