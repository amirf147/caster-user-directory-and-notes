[ 🏠 Docs Home ](../README.md) › [ 📁 History ](../README.md#history) › **Technical Journey & Recent Focus**

---

# Technical Journey & Recent Focus

Our ongoing work focuses on real-time desktop context tracking, window switching, accessibility mechanics, and speech engine responsiveness. Below is a structured summary of our journey, ordered from active production focus back to foundational milestones:

### 1. Active Production: Foundational Plugin Architecture, HUD Modularization, & User Content Separation
- **Status (Active Production - Deployed & Verified)**: Built and deployed the foundational Caster Plugin Architecture (`PluginBase`, `PluginManager`), replacing hardcoded startup hooks in `_caster.py` and eliminating pseudo-rules disguised as voice grammars. Modularized the Heads-Up Display into discrete plugins (`standard_hud`, `themed_hud`, `taskbar_hud`), establishing clean separation between upstream legacy interfaces and custom setups. Relocated all official bridges into `castervoice/plugins/`, restoring `caster_user_content/` strictly to user voice rules and personal configurations.
- **Core Engineering Breakthroughs**:
  - **Elimination of Pseudo-Rules and Splicing Anti-Patterns**: Diagnosed the architectural limitation of Caster's legacy grammar loader (`ContentLoader`), which recognized only `get_rule`, `get_transformer`, and `get_hook`. Prior to this architecture, non-grammar integrations were forced into dummy `MappingRule` instances (`taskbar_hud_rule.py`) or hardcoded imports in `_caster.py`. The new `PluginManager` discovers, initializes, and starts all optional subsystems cleanly via standard lifecycle phases.
  - **PluginBase Lifecycle Contract**: Implemented `PluginBase` in `castervoice/lib/plugin.py` with deterministic `initialize(nexus, config)`, `start()`, and `stop()` phases. Pre-engine registration hooks print message handlers and microphone listeners; post-engine startup launches background threads, Named Pipe workers, and GUI processes.
  - **Failure Isolation & Non-Fatal Execution**: Hardened `PluginManager` against plugin initialization exceptions. If a third-party or optional plugin raises an unhandled error, `PluginManager` logs a traceback without interrupting Caster core startup or blocking speech recognition.
  - **HUD Taxonomy Formalization**:
    - `standard_hud`: Preserves the upstream master monolithic HUD (`dictation-toolbox/Caster`) for minimal memory environments.
    - `themed_hud`: Packages the advanced modular PyQt HUD developed in `custom-setup` (10+ QSS themes, opacity controls, status header, rules tag bar, ADCE strip, frameless drag mode).
    - `taskbar_hud`: Integrates the Windows 11 Taskbar Windhawk mod Named Pipe bridge (`\\.\pipe\CasterTaskbarHud`), delivering hands-free feedback directly inside the Windows shell with zero desktop window footprint.
  - **Centralized Configuration in `settings.toml`**: Added the `[plugins]` table to `settings/settings.toml`, allowing declarative toggling of all subsystems (`themed_hud = true`, `standard_hud = false`, `taskbar_hud = true`, `adce = true`, `sikuli = false`).
  - **Repository Boundary Enforcement**: Cleaned up `caster_user_content/util/` by removing redundant bridge drivers (`taskbar_hud_bridge.py`, `taskbar_hud_printer_handler.py`) and deleting `taskbar_hud_rule.py`. Retained backward-compatible re-exports in `adce_bridge.py` for legacy user scripts.
  - **Automated Regression Testing**: Created `test_plugin_manager.py` (4 unit tests) and updated `test_taskbar_hud_decoupled.py` (4 unit tests). All 54 tests across 10 modules passed in 5.90 seconds.
- **Key Documentation**:
  * 🏛️ **[Foundational Plugin System & HUD Modularization (015)](../caster_hud/015_foundational_plugin_system_and_hud_modularization.md)** *(Active Production Architecture & Canonical Reference)*
  * 🏛️ **[Out-of-Process Desktop Observation & ADCE HUD Realization (014)](../caster_hud/014_out_of_process_desktop_observation_and_adce_hud_realization.md)**
  * 📋 **[Caster HUD Master Requirements & Specifications (005)](../caster_hud/005_caster_hud_requirements_and_specifications.md)**
  * 🧠 **[Repository Brain (Canonical SSOT)](../context/repository-brain.md)**
  * 📜 **[Status Update History](../../status-update-history.md)**

---

### 2. Active Production: WinVDA Zero-Cached-State Virtual Desktop Engine (Published & Caster Production Migration)
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

### 3. Active Production: Out-of-Process Desktop Context Observation & ADCE HUD Realization
- **Status (Active Production - Deployed & Verified)**: Completed the architectural transition from in-process Win32 window focus hooks to out-of-process desktop context observation driven by the Active Desktop Context Engine (ADCE). Deleted `window_tracker.py` from Caster core without leaving orphaned hooks or polling loops. Refactored `hud_support.py` to filter active CCR rules authoritatively against `_enabled_ordered` and `rules.toml`. Empirically verified end-to-end synchronization across both the Qt HUD overlay and the Windows 11 Taskbar HUD.
- **Core Architecture & Breakthroughs**:
  - **Elimination of In-Process Win32 Window Hooks**: Diagnosed architectural redundancy between Caster's internal `window_tracker.py` and the standalone ADCE daemon. Removed `SetWinEventHook` (`EVENT_SYSTEM_FOREGROUND`, `EVENT_OBJECT_NAMECHANGE`), `GetForegroundWindow`, `GetWindowTextW`, and `QueryFullProcessImageNameW` from Caster. Caster core and HUD libraries now run with zero native window hooks or foreground inspection calls.
  - **Out-of-Process ADCE Authority**: Established the .NET 10 ADCE service as the single source of truth for desktop window context (HWND, window titles, process names, and sub-window semantic interaction zones). Context is ingested asynchronously via Server-Sent Events (`http://127.0.0.1:8424/sse`) by `AdceTracker` in the Qt HUD and forwarded across UI widgets via `SignalBridge`.
  - **Authoritative Configuration Filtering**: Diagnosed false positive active rules in the HUD (such as `Firefox` showing as active when `FirefoxRule` was disabled, or `Vscodium` displaying when focusing Antigravity IDE). Traced the bug to naive display heuristics using `str(list(rule_spec.get("executables"))[0]).capitalize()`. Implemented `_is_rule_enabled_in_config()`, validating matching rules against `_enabled_ordered` and the user's `rules.toml`.
  - **Dual HUD Ecosystem Synchronization**: Both the standalone Qt HUD (`StatusBarWidget` and `AdceBarWidget`) and the Windows 11 Taskbar HUD (`caster-taskbar-hud.wh.cpp` via `\\.\pipe\CasterTaskbarHud`) receive identical, verified desktop telemetry directly from ADCE and Caster core without in-process scraping.
  - **Zero-Latency IPC Isolation**: Dedicated port allocation (Port 8338 for XML-RPC, Port 8339 for ndjson telemetry) with non-blocking drop-oldest queues (`queue.Queue(maxsize=1024)`) guaranteeing `< 0.001 ms` speech thread overhead.
  - **Ergonomics & Controls**: Direct header click-and-drag window movement, 'D' drag mode with arrow nudging, 'T' frameless toggle, system tray docking, font scaling, modal help/rules dialogs, and comprehensive voice/context-menu controls.
- **Key Documentation**:
  * 🏛️ **[Out-of-Process Desktop Observation & ADCE HUD Realization (014)](../caster_hud/014_out_of_process_desktop_observation_and_adce_hud_realization.md)** *(Active Production Architecture & Canonical Reference - NOT SUPERSEDED)*
  * 📋 **[Caster HUD Master Requirements & Specifications (005)](../caster_hud/005_caster_hud_requirements_and_specifications.md)** *(Active UI/UX SSoT)*
  * 🖥️ **[Taskbar HUD Windhawk Injection & Telemetry Explainer (012)](../caster_hud/012_taskbar_hud_windhawk_mod_and_caster_bridge_explainer.md)** *(Active Subsystem Spec)*
  * 🏛️ **[Multi-Process Topology, ADCE Gating, & Unified Telemetry ADR (013)](../caster_hud/013_multiprocess_topology_adce_gating_and_unified_telemetry_architecture.md)** *(Foundational Decision)*
  * 📜 **[Caster HUD Continuous Lessons Learned Timeline (007)](../caster_hud/007_caster_hud_lessons_learned_timeline.md)** *(Milestone 17)*
  * 🚀 **[Active Desktop Context Engine Repository](https://github.com/amirf147/active-desktop-context-engine)**

---

### 4. Sub-Millisecond Native Win32 App Switcher Refactor (Active Production v3.1)
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

### 5. Wayfinder Session: App Switching & UIA Threading Investigation
- **Condensed Summary**: Investigated perceived freezes in `app_switcher.py` and UIA/COM threading performance across speech stacks. Discovered through empirical telemetry (`ca5dc70`) that apparent hangs were caused by Windows PowerShell QuickEdit mode pausing standard output (`stdout`) during console logging.
- **Key Docs & Code**:
  - Feature Guide: **[App Switcher Documentation](../features/app_switcher.md)**
  - Session Index: **[Wayfinder UIA & Threading Directory](../wayfinder-uia-threading/map.md)**
  - Rule & Utility Code: **[window_switching.py](../../caster_user_content/rules/global/window_switching.py)** & **[app_switcher.py](../../caster_user_content/util/app_switcher.py)**

---

### 6. Historical Status & Archived Investigations
- Archive of past status updates with deep dives into Dynamic Sub-Window Grammar Activation, LexiconCode PR #881 investigation, the Dragonfly BPC Fork Kaldi race condition fixes, and UIA threading synthesis:
  👉 **[Status Update History](../../status-update-history.md)**

---

### 7. Git Evolution & Subsystem Timelines
For complete historical retrospectives spanning our 27-month, 969-commit repository evolution:
- 📜 **[App Switcher Evolution Timeline](app_switcher_timeline.md)**: 2-year journey across 6 eras of window switching.
- 📜 **[Caster Printer & HUD Timeline](caster_printer_hud_timeline.md)**: Evolution of status messaging and async HUD overlays.
- 📜 **[Repository Master Timeline](repository_timeline.md)**: Comprehensive 4-era narrative covering 27 months of hands-free Voice OS engineering.
- 🌐 **[Interactive Timeline Visualizer](timeline.html)**: Interactive web timeline application.
