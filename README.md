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

* **[Foundational Plugin Architecture & Modular HUDs](docs/caster_hud/015_foundational_plugin_system_and_hud_modularization.md)**: Standardized plugin lifecycle contract (`PluginBase`, `PluginManager`), centralized `settings.toml [plugins]` controls, formal HUD taxonomy (`themed_hud`, `standard_hud`, `taskbar_hud`), complete elimination of pseudo-rules, and strict separation between core infrastructure and user voice configurations.
* **[Modular Caster HUD Overlay](docs/caster_hud/014_out_of_process_desktop_observation_and_adce_hud_realization.md)**: Active production architecture ([014](docs/caster_hud/014_out_of_process_desktop_observation_and_adce_hud_realization.md)), UI/UX specifications ([005](docs/caster_hud/005_caster_hud_requirements_and_specifications.md)), 5-layer Clean Architecture, out-of-process ADCE desktop context observation, zero in-process Win32 hooks, authoritative `rules.toml` configuration filtering, and dual Qt/Taskbar HUD synchronization.
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

### 1. Active Production: Foundational Plugin Architecture, HUD Modularization, & User Content Separation
* **Status (Active Production - Deployed & Verified)**: Built and deployed the foundational Caster Plugin Architecture (`PluginBase`, `PluginManager`), replacing hardcoded startup hooks in `_caster.py` and eliminating pseudo-rules disguised as voice grammars. Modularized the Heads-Up Display into discrete plugins (`standard_hud`, `themed_hud`, `taskbar_hud`), establishing clean separation between upstream legacy interfaces and custom setups. Relocated all official bridges into `castervoice/plugins/`, restoring `caster_user_content/` strictly to user voice rules and personal configurations.
* **Core Architecture & Breakthroughs**:
  * **Elimination of Pseudo-Rules and Splicing Anti-Patterns**: Diagnosed the architectural limitation of Caster's legacy grammar loader (`ContentLoader`), which recognized only `get_rule`, `get_transformer`, and `get_hook`. Prior to this architecture, non-grammar integrations were forced into dummy `MappingRule` instances (`taskbar_hud_rule.py`) or hardcoded imports in `_caster.py`. The new `PluginManager` discovers, initializes, and starts all optional subsystems cleanly via standard lifecycle phases.
  * **PluginBase Lifecycle Contract**: Implemented `PluginBase` in `castervoice/lib/plugin.py` with deterministic `initialize(nexus, config)`, `start()`, and `stop()` phases. Pre-engine registration hooks print message handlers and microphone listeners; post-engine startup launches background threads, Named Pipe workers, and GUI processes.
  * **Failure Isolation & Non-Fatal Execution**: Hardened `PluginManager` against plugin initialization exceptions. If a third-party or optional plugin raises an unhandled error, `PluginManager` logs a traceback without interrupting Caster core startup or blocking speech recognition.
  * **HUD Taxonomy Formalization**:
    * `standard_hud`: Preserves the upstream master monolithic HUD (`dictation-toolbox/Caster`) for minimal memory environments.
    * `themed_hud`: Packages the advanced modular PyQt HUD developed in `custom-setup` (10+ QSS themes, opacity controls, status header, rules tag bar, ADCE strip, frameless drag mode).
    * `taskbar_hud`: Integrates the Windows 11 Taskbar Windhawk mod Named Pipe bridge (`\\.\pipe\CasterTaskbarHud`), delivering hands-free feedback directly inside the Windows shell with zero desktop window footprint.
  * **Centralized Configuration in `settings.toml`**: Added the `[plugins]` table to `settings/settings.toml`, allowing declarative toggling of all subsystems (`themed_hud = true`, `standard_hud = false`, `taskbar_hud = true`, `adce = true`, `sikuli = false`).
  * **Repository Boundary Enforcement**: Cleaned up `caster_user_content/util/` by removing redundant bridge drivers (`taskbar_hud_bridge.py`, `taskbar_hud_printer_handler.py`) and deleting `taskbar_hud_rule.py`. Retained backward-compatible re-exports in `adce_bridge.py` for legacy user scripts.
  * **Automated Regression Testing**: Created `test_plugin_manager.py` (4 unit tests) and updated `test_taskbar_hud_decoupled.py` (4 unit tests). All 54 tests across 10 modules passed in 5.90 seconds.
* **Key Documentation**:
  * 🏛️ **[Foundational Plugin System & HUD Modularization (015)](docs/caster_hud/015_foundational_plugin_system_and_hud_modularization.md)** *(Active Production Architecture & Canonical Reference)*
  * 🏛️ **[Out-of-Process Desktop Observation & ADCE HUD Realization (014)](docs/caster_hud/014_out_of_process_desktop_observation_and_adce_hud_realization.md)**
  * 📋 **[Caster HUD Master Requirements & Specifications (005)](docs/caster_hud/005_caster_hud_requirements_and_specifications.md)**
  * 🧠 **[Repository Brain (Canonical SSOT)](docs/context/repository-brain.md)**
  * 📜 **[Status Update History](status-update-history.md)**

### 2. Active Production: WinVDA Zero-Cached-State Virtual Desktop Engine (Published & Caster Production Migration)
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

### 3. Active Production: Out-of-Process Desktop Context Observation & ADCE HUD Realization
* **Status (Active Production - Deployed & Verified)**: Completed the architectural transition from in-process Win32 window focus hooks to out-of-process desktop context observation driven by the Active Desktop Context Engine (ADCE). Deleted `window_tracker.py` from Caster core without leaving orphaned hooks or polling loops. Refactored `hud_support.py` to filter active CCR rules authoritatively against `_enabled_ordered` and `rules.toml`. Empirically verified end-to-end synchronization across both the Qt HUD overlay and the Windows 11 Taskbar HUD.
* **Core Architecture & Breakthroughs**:
  - **Elimination of In-Process Win32 Window Hooks**: Diagnosed architectural redundancy between Caster's internal `window_tracker.py` and the standalone ADCE daemon. Removed `SetWinEventHook` (`EVENT_SYSTEM_FOREGROUND`, `EVENT_OBJECT_NAMECHANGE`), `GetForegroundWindow`, `GetWindowTextW`, and `QueryFullProcessImageNameW` from Caster. Caster core and HUD libraries now run with zero native window hooks or foreground inspection calls.
  - **Out-of-Process ADCE Authority**: Established the .NET 10 ADCE service as the single source of truth for desktop window context (HWND, window titles, process names, and sub-window semantic interaction zones). Context is ingested asynchronously via Server-Sent Events (`http://127.0.0.1:8424/sse`) by `AdceTracker` in the Qt HUD and forwarded across UI widgets via `SignalBridge`.
  - **Authoritative Configuration Filtering**: Diagnosed false positive active rules in the HUD (such as `Firefox` showing as active when `FirefoxRule` was disabled, or `Vscodium` displaying when focusing Antigravity IDE). Traced the bug to naive display heuristics using `str(list(rule_spec.get("executables"))[0]).capitalize()`. Implemented `_is_rule_enabled_in_config()`, validating matching rules against `_enabled_ordered` and the user's `rules.toml`.
  - **Dual HUD Ecosystem Synchronization**: Both the standalone Qt HUD (`StatusBarWidget` and `AdceBarWidget`) and the Windows 11 Taskbar HUD (`caster-taskbar-hud.wh.cpp` via `\\.\pipe\CasterTaskbarHud`) receive identical, verified desktop telemetry directly from ADCE and Caster core without in-process scraping.
  - **Zero-Latency IPC Isolation**: Dedicated port allocation (Port 8338 for XML-RPC, Port 8339 for ndjson telemetry) with non-blocking drop-oldest queues (`queue.Queue(maxsize=1024)`) guaranteeing `< 0.001 ms` speech thread overhead.
  - **Ergonomics & Controls**: Direct header click-and-drag window movement, 'D' drag mode with arrow nudging, 'T' frameless toggle, system tray docking, font scaling, modal help/rules dialogs, and comprehensive voice/context-menu controls.
* **Key Documentation**:
  * 🏛️ **[Out-of-Process Desktop Observation & ADCE HUD Realization (014)](docs/caster_hud/014_out_of_process_desktop_observation_and_adce_hud_realization.md)** *(Active Production Architecture & Canonical Reference - NOT SUPERSEDED)*
  * 📋 **[Caster HUD Master Requirements & Specifications (005)](docs/caster_hud/005_caster_hud_requirements_and_specifications.md)** *(Active UI/UX SSoT)*
  * 🖥️ **[Taskbar HUD Windhawk Injection & Telemetry Explainer (012)](docs/caster_hud/012_taskbar_hud_windhawk_mod_and_caster_bridge_explainer.md)** *(Active Subsystem Spec)*
  * 🏛️ **[Multi-Process Topology, ADCE Gating, & Unified Telemetry ADR (013)](docs/caster_hud/013_multiprocess_topology_adce_gating_and_unified_telemetry_architecture.md)** *(Foundational Decision)*
  * 📜 **[Caster HUD Continuous Lessons Learned Timeline (007)](docs/caster_hud/007_caster_hud_lessons_learned_timeline.md)** *(Milestone 17)*
  * 🚀 **[Active Desktop Context Engine Repository](https://github.com/amirf147/active-desktop-context-engine)**

### 4. Native Taskbar HUD Windhawk Injection & Real-Time Telemetry Bridge (Active Exploration)
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

### 5. Native Win32 App Switcher & Tier 4 Taskbar Fail-Safe (Active Production v3.1)
* **Status (Active Production)**: Upgraded the **production focus engine** in [`caster_user_content/util/app_switcher.py`](caster_user_content/util/app_switcher.py) with a deterministic **Tier 4 Taskbar Keystroke Fail-Safe** (`Win+T` traversal / `Win+<N>`) to bypass Windows UIPI foreground locks when switching away from elevated windows.
* **Core Architecture & UIPI Delineation**:
  * **0–10ms Direct Fast Path (Tiers 1–3)**: Preserves sub-millisecond Win32 focus transitions via `SetForegroundWindow`, guarded `_alt_key_bypass()`, and `_attached_threads()` input queue attachment.
  * **UIPI Elevation Boundary & Tier 4 Fail-Safe**: Diagnosed complete focus escalation denial (Win32 Error 5: `Access is denied`) when an elevated process (e.g. Windhawk, Task Manager) owns the foreground. Lower-integrity speech processes cannot inject input or attach threads to higher-integrity windows. Replaced the obsolete Windows 10 UIA click fallback with read-only taskbar discovery (`get_taskbar_order`) and deterministic shell hotkey delegation (`Win+<N>` or `Win+T, home, right:..., enter`), allowing `explorer.exe` to execute the window switch.
  * **Critical Integrity Delineation**: While speech commands cannot drive or inject keystrokes into elevated windows (which Windows UIPI strictly forbids), focusing the unprivileged Caster HUD (`Caster HUD v 1.7.0`) or using Tier 4 shell traversal safely restores command execution for all standard user applications.
* **Key Docs**: [App Switcher Blueprint v3](docs/architecture/app_switcher_architectural_blueprint.md) | [Troubleshooting Findings & UIPI Post-Mortem](docs/troubleshooting/app_switcher_findings.md) | [App Switcher Focus Analysis](docs/architecture/app_switcher_focus_analysis.md) | [App Switcher Evolution Timeline](docs/history/app_switcher_timeline.md).

### 6. Historical Status & Archived Investigations
* **[Repository Timeline & 2-Year Technical Journey](docs/history/repository_timeline.md)**: Historical retrospective covering early repository foundations through mid-2026 (Kaldi ASR migration, desktop automation, AI IDE workflows, and initial window switching). *(Note on Scope: Captures foundations up to mid-2026; consult [Key Engineering](#-key-engineering--voice-automations) and [Recent Focus](#-technical-journey--recent-focus) above for current sub-millisecond Win32 v3, ADCE, and HUD systems).*
* **[Status Update History](status-update-history.md)**: Full archive of previous status updates (including Dynamic Sub-Window Grammar Activation, LexiconCode PR #881 investigation, Wayfinder session, Dragonfly BPC Fork Kaldi race condition fixes, and 2024 development logs).
* **[Kaldi Compiler & Engine Race Condition Post-Mortem](docs/troubleshooting/kaldi_crash_explanation.md)**: Root-cause debugging of Caster speech compiler crashes.
* **[Speech Stack Thread Architecture Report](docs/architecture/Speech_Stack_Thread_Architecture_and_Diagnostic_Report.md)**: Thread interaction models and execution boundaries.
* **[Technical Journey Log](docs/history/technical_journey.md)**: Active and archived engineering focus roadmap.

---

## 📂 Repository Structure

* `caster_user_content/rules/`: Live voice grammars, application-specific rules, and global macros.
* `caster_user_content/util/`: User runtime helpers (e.g., `app_switcher.py`, backward-compatible `adce_bridge.py` re-exports).
* `settings/`: User configuration including `settings.toml` (`[plugins]` toggles) and `rules.toml`.
* `scripts/`: Development prototypes, test runners, and validation utilities (e.g., `context_poc.py`, `check_absolute_paths.py`).
* `docs/`: Comprehensive [Documentation Hub](docs/README.md) and [Repository Brain](docs/context/repository-brain.md).
* `.agents/`: Workflows and workspace rules for the Antigravity editor.
* `config/examples/`: Sanitized environment and settings templates. (Personal local configurations in `settings/` and `data/` are strictly untracked).
