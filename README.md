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

* **[Native HUD Process Lifecycle & Strategy Pattern](docs/caster_hud/017_native_hud_process_lifecycle_and_plugin_decoupling.md)**: Resilient cross-platform process containment using the Strategy Pattern (`WindowsProcessStrategy` with Win32 Job Objects, `LinuxProcessStrategy` with `prctl(PR_SET_PDEATHSIG)` process groups, and `DarwinProcessStrategy`). Self-healing auto-recovery on `show_hud()`, graceful termination `stop_hud()`, clean `restart_hud()`, asynchronous queuing in `HudPrintMessageHandler`, and versatile voice controls.
* **[Core Engine Microphone Listener Observer Pattern](docs/caster_hud/017_native_hud_process_lifecycle_and_plugin_decoupling.md)**: First-class observer pattern in `EngineModesManager` (`engine_manager.py`) replacing polling and monkey-patching with thread-safe, synchronous notification of microphone state transitions (`sleeping`, `listening`, `off`) to overlays and bridges.
* **[Extensible Plugin Architecture & Distribution Catalog](docs/caster_hud/015_foundational_plugin_system_and_hud_modularization.md)**: Standardized plugin lifecycle contract (`PluginBase`, `PluginManager`), centralized `settings.toml [plugins]` controls, formal HUD taxonomy (`themed_hud`, `standard_hud`, `taskbar_hud`), complete elimination of pseudo-rules, and standalone distribution via **[caster-plugins](https://github.com/amirf147/caster-plugins)**.
* **[Native Taskbar HUD Windhawk Mod](https://github.com/amirf147/caster-taskbar-hud)**: Native C++ Windhawk modification (`caster-taskbar-hud.wh.cpp`) packaged and distributed as a native Windhawk mod at **[caster-taskbar-hud](https://github.com/amirf147/caster-taskbar-hud)**. Injects real-time speech telemetry, active Dragonfly rules, and ADCE semantic zones into Windows 11 taskbar XAML via Named Pipe (`\\.\pipe\CasterTaskbarHud`).
* **[Automated Rule Catalog & Context Resolver](docs/caster_hud/016_automated_rule_catalog_and_adce_context_resolution.md)**: Automated AST-based voice rule discovery, elimination of static dictionary anti-patterns, dynamic synchronization with `rules.toml` via file modification monitoring, and decoupled ADCE telemetry resolution for the Windows 11 Taskbar HUD.
* **[Modular Caster HUD Overlay](docs/caster_hud/014_out_of_process_desktop_observation_and_adce_hud_realization.md)**: Active production architecture ([014](docs/caster_hud/014_out_of_process_desktop_observation_and_adce_hud_realization.md)), UI/UX specifications ([005](docs/caster_hud/005_caster_hud_requirements_and_specifications.md)), 5-layer Clean Architecture, out-of-process ADCE desktop context observation, zero in-process Win32 hooks, authoritative `rules.toml` configuration filtering, and dual Qt/Taskbar HUD synchronization.
* **[Active Desktop Context Engine (ADCE) & MCP Hub](docs/accessibility_mcp/CONTEXT.md)**: Real-time, event-driven OS state tracking (`scripts/context_poc.py`), tab discovery across browsers and IDEs, Virtual Desktop awareness, and Model Context Protocol (MCP) integration.
* **[App & Window Switcher v3](docs/features/app_switcher.md)**: Sub-millisecond direct Win32 window switching, workspace isolation, guarded keystate context managers, and automated tab navigation.
* **[App Switcher Evolution Timeline](docs/history/app_switcher_timeline.md)**: 2-year retrospective tracing the 5 evolution eras of window switching from Windhawk taskbar macros to native Win32 v3.
* **[App Switcher Architectural Blueprint (v3)](docs/architecture/app_switcher_architectural_blueprint.md)**: Authoritative technical specification, focus tier state machines, and sequence diagrams.
* **[WinVDA Virtual Desktop Subsystem](https://github.com/amirf147/winvda)**: Clean-room, zero-cached-state Windows Virtual Desktop engine ([006](docs/pyvda/006_winvda_clean_room_engine_realization_and_caster_migration.md)) replacing legacy `pyvda` in Caster production. Built on direct ctypes vtable dispatch, transient MTA sessions immune to Explorer restarts, exact-match sub-AUMID normalization ([003](docs/pyvda/003_pyvda_multi_window_xaml_island_pinning_architecture.md)), and native Task View parity ([005](docs/pyvda/005_task_view_pinning_internals_and_shell_reverse_engineering.md)).
* **[Upstream VirtualDesktopAccessor COM Hardening & Multi-Window Pinning Engine](https://github.com/Ciantic/VirtualDesktopAccessor/pull/115)**: Resolution of unmanaged COM heap leakage in `IApplicationView::GetAppUserModelId` within the native C-ABI DLL underpinning virtual desktop automation. Refactored into a zero-overhead Rust RAII wrapper struct (`APPIDPWSTR`) with deterministic `CoTaskMemFree` deallocation and zero-touch calling site preservation. Extended to resolve modern XAML Island sub-AUMID pinning disparity with Task View parity and dynamic switch reconciliation ([008](docs/pyvda/008_virtual_desktop_accessor_com_heap_hardening_and_raii_breakdown.md)).
* **[Virtual Desktop Pinning Architecture, Phonetic Misrecognition & Grammar Ergonomics](docs/features/virtual_desktop_pinning_and_grammar_ergonomics.md)**: Voice-driven pinning and unpinning across virtual workspaces, phonetic coarticulation failure analysis (`pin window` -> `new window`), Kaldi decoder language model priors, Caster noun-first syntactic alignment, and upstream PR coordination.
* **[Foot Pedal & XML-RPC IPC Bridge](docs/features/foot_pedal.md)**: Hardware debouncing, smart tap/drag/scroll control for the Olympus RS31H foot pedal, paired with a local XML-RPC IPC bridge for thread-safe microphone toggling.
* **[Top Voice Automations Showcase](docs/features/top_voice_automations.md)**: Curated showcase of desktop, editor, and system voice workflows.

---

## 🧭 Technical Journey & Recent Focus

Our ongoing work focuses on real-time desktop context tracking, window switching, accessibility mechanics, and speech engine responsiveness:

### 1. Active Production: Cross-Platform Native HUD Process Lifecycle, Engine Mic Observer, & Plugin Architecture
* **Status (Active Production - Deployed & Verified)**: Upgraded Caster's display and extensibility foundation across three major core subsystems:
  1. **Native HUD Process Hardening & Strategy Pattern ([017](docs/caster_hud/017_native_hud_process_lifecycle_and_plugin_decoupling.md))**: Encapsulated OS-specific process containment using the Strategy Pattern (`process_lifecycle.py`), implementing native Windows Job Objects (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`), Linux `prctl(PR_SET_PDEATHSIG)` process groups, and macOS session isolation. Prevents orphaned background processes, adds self-healing auto-recovery on `show_hud()`, graceful termination `stop_hud()`, clean `restart_hud()`, asynchronous queuing in `HudPrintMessageHandler` via background daemon worker, and expanded voice commands in `caster_rule.py`. Isolated cleanly into upstream candidate branch `feat/hud-process-hardening`.
  2. **Core Engine Microphone Listener Observer Pattern**: Added clean `register_mic_mode_listener` / `unregister_mic_mode_listener` APIs to `EngineModesManager` (`engine_manager.py`), broadcasting microphone mode transitions (`sleeping`, `listening`, `off`) synchronously to registered overlays and bridges without polling loops or monkey-patching. Isolated into upstream branch `feat/engine-mic-listener`.
  3. **Extensible Plugin Architecture ([015](docs/caster_hud/015_foundational_plugin_system_and_hud_modularization.md))**: Deployed `PluginBase` and `PluginManager`, formalizing plugin lifecycles (`initialize`, `start`, `stop`), non-fatal failure isolation, dynamic rule export, CLI management (`plugin_cli.py`), and `settings.toml [plugins]` controls. User space (`caster_user_content/`) is strictly dedicated to personal rules; official plugins reside in `castervoice/plugins/` or standalone distribution.
* **Key Documentation**:
  * 🏛️ **[Native HUD Process Lifecycle & Plugin Decoupling (017)](docs/caster_hud/017_native_hud_process_lifecycle_and_plugin_decoupling.md)** *(Active Production Architecture & Canonical Reference)*
  * 🏛️ **[Foundational Plugin System & HUD Modularization (015)](docs/caster_hud/015_foundational_plugin_system_and_hud_modularization.md)**
  * 🧠 **[Repository Brain (Canonical SSOT)](docs/context/repository-brain.md)**
  * 📜 **[Status Update History](status-update-history.md)**

### 2. Active Production: Automated Rule Catalog & Decoupled ADCE Context Resolution
* **Status (Active Production - Deployed & Verified)**: Replaced static process lookup tables and fragile IDE terminal heuristics in `taskbar_hud/context_resolver.py` with an automated AST-based rule catalog. Automatically scans user and core rule directories on startup without initializing the speech engine or executing module code. Synchronizes active rule resolution with `rules.toml` via file modification monitoring, providing accurate contextual rule reporting on the Windows 11 Taskbar HUD.
* **Core Architecture & Breakthroughs**:
  * **Elimination of Static Mapping Anti-Patterns**: Diagnosed the root cause of false negative and false positive rule reporting in the Taskbar HUD. The previous implementation maintained a hand-typed dictionary (`PROCESS_RULES_MAP`) that omitted companion rules (such as `CustomMSWordRule` and `ExcelRule`) and ignored custom rules added to `caster_user_content/rules/`. The automated catalog parses `get_rule()` AST nodes directly from source files, indexing target executables, window titles, and CCR markers dynamically.
  * **Strict Separation Between Sensor and Resolver**: Clarified the boundary between out-of-process OS context observation (ADCE daemon on port 8424) and in-process rule interpretation (`context_resolver.py`). ADCE observes physical window focus, titles, and zones; `context_resolver.py` maps those observations to active Dragonfly rules.
  * **Dynamic Configuration Synchronization**: Implemented `refresh_enabled()` in `RuleCatalog`, monitoring the timestamp of `rules.toml`. Changes to active rules reload automatically without requiring a Caster process restart.
  * **Terminal Sub-Zone Simplification**: Removed brittle heuristics that attempted to guess `IDETerminalRule` activation from unstandardized zone strings and process lists. ADCE continues to provide the `semantic_zone` string directly to the HUD for visual zone labeling.
  * **Sub-Millisecond Resolution**: Verified catalog construction completes in 98 ms across 164 rule modules at startup, while per-focus resolution executes in 0.03 ms from in-memory index tables.
* **Key Documentation**:
  * 🏛️ **[Automated Rule Catalog & ADCE Context Resolution (016)](docs/caster_hud/016_automated_rule_catalog_and_adce_context_resolution.md)** *(Active Production Architecture & Canonical Reference)*
  * 🏛️ **[Foundational Plugin System & HUD Modularization (015)](docs/caster_hud/015_foundational_plugin_system_and_hud_modularization.md)**
  * 🏛️ **[Out-of-Process Desktop Observation & ADCE HUD Realization (014)](docs/caster_hud/014_out_of_process_desktop_observation_and_adce_hud_realization.md)**
  * 📋 **[Caster HUD Master Requirements & Specifications (005)](docs/caster_hud/005_caster_hud_requirements_and_specifications.md)**
  * 🧠 **[Repository Brain (Canonical SSOT)](docs/context/repository-brain.md)**
  * 📜 **[Status Update History](status-update-history.md)**

### 3. Active Production: Native Taskbar HUD Windhawk Mod & Standalone Plugin Catalog (Published)
* **Status (Active Production - Published & Deployed)**: Implemented, verified, and published the native C++ Windhawk modification (`caster-taskbar-hud.wh.cpp`, 1612 lines) in its dedicated standalone distribution repository at **[`amirf147/caster-taskbar-hud`](https://github.com/amirf147/caster-taskbar-hud)**, and launched the modular plugin distribution repository at **[`amirf147/caster-plugins`](https://github.com/amirf147/caster-plugins)**.
* **Core Architecture & Breakthroughs**:
  * **In-Process Shell XAML Injection**: Hooks `taskbar.dll` symbols (`CTaskBand::GetTaskbarHost`, `TaskbarHost::FrameHeight`, `TrayUI::StartTaskbar`) in `explorer.exe` to mount native WinRT XAML controls within `SystemTrayFrameGrid` across primary and secondary taskbars.
  * **Asynchronous Overlapped Named Pipe IPC**: Listens on `\\.\pipe\CasterTaskbarHud`, ingesting JSON telemetry asynchronously with `<0.5ms` deserialization marshaled to the UI thread via `WH_CALLWNDPROC`.
  * **Unified Single Command Strip Pivot**: Diagnosed horizontal button panel encroachment where multi-pill layouts clipped running application buttons in `TaskListButtonPanel`. Pivoted to a compact, unified command strip (~160px) displaying dynamic contextual telemetry strings (e.g., `Ready (VS Code)`, `Terminal | VS Code`).
  * **In-Situ Context Menu & Registry Persistence**: Hooked XAML `RightTapped` on the taskbar container to render a native Win32 popup menu (`TrackPopupMenuEx`), enabling live mode toggling (single strip, rotating carousel, multi-box) persisted to `HKCU\Software\Caster\TaskbarHud`.
  * **Standalone Plugin Catalog (`caster-plugins`)**: Decoupled the HUD plugins from core Caster, establishing `amirf147/caster-plugins` as the independent distribution catalog with automated GitHub Actions CI safety checks and live telemetry showcase animations.
* **Key Documentation**:
  * 🌐 **[Caster Taskbar HUD Repository](https://github.com/amirf147/caster-taskbar-hud)** *(Dedicated Windhawk Mod Distribution)*
  * 📦 **[Caster Plugins Distribution Repository](https://github.com/amirf147/caster-plugins)** *(Independent Plugin Catalog)*
  * 🖥️ **[Taskbar HUD Windhawk Injection & Telemetry Explainer (012)](docs/caster_hud/012_taskbar_hud_windhawk_mod_and_caster_bridge_explainer.md)** *(Subsystem Architecture & Unified Strip Pivot)*
  * 📋 **[Caster HUD Master Requirements & Specifications (005)](docs/caster_hud/005_caster_hud_requirements_and_specifications.md)**
  * 📜 **[Status Update History](status-update-history.md)**

### 4. Active Production: WinVDA Zero-Cached-State Virtual Desktop Engine (Published & Caster Production Migration)
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

### 5. Active Production: Out-of-Process Desktop Context Observation & ADCE HUD Realization
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

### 6. Active Production: Upstream VirtualDesktopAccessor COM Hardening, RAII Architecture, & Multi-Window Pinning Engine
* **Status (Active Production - Upstream PR #115 & Branch `fix/xaml-island-multi-window-pinning`)**: Diagnosed and resolved two chronic architectural limitations in `Ciantic/VirtualDesktopAccessor` (`src/comobjects.rs`, `src/interfaces.rs`), the native C-ABI DLL underpinning virtual desktop switching and window pinning across Caster, AutoHotkey, and Windows automation utilities: (1) an unmanaged COM task memory leak in `GetAppUserModelId`, and (2) multi-window application pinning disparity in modern Windows Shell environments.
* **Core Architecture & Breakthroughs**:
  * **COM Task Memory Leak Diagnosis & RAII Architecture (PR #115)**: Uncovered unmanaged heap leakage in `IApplicationView::GetAppUserModelId`. The Windows Shell allocates UTF-16 AUMID buffers on the process COM task heap via `CoTaskMemAlloc`. In the upstream library, `get_iapplication_id_for_view` discarded the returned pointer without calling `CoTaskMemFree`, leaking unmanaged memory on every pinning query or modification (`is_pinned_app`, `pin_app`, `unpin_app`). Following architectural alignment with upstream repository owner Jari Pennanen (`Ciantic`), refactored raw pointer aliasing into an idiomatic Rust RAII wrapper: `#[repr(transparent)] struct APPIDPWSTR(pub PWSTR)` with `impl Drop` calling `CoTaskMemFree`. Transferring `APPIDPWSTR` by value across the COM vtable boundary guarantees zero-touch calling site preservation with deterministic cleanup on return and error unwinding.
  * **Multi-Window XAML Island Application Pinning (`fix/xaml-island-multi-window-pinning`)**: Modern packaged applications and WinUI 3 / XAML Island architectures (such as Windows Terminal and tabbed Windows Notepad) generate synthetic sub-AUMIDs suffixed with `~Wh~w<HEX_HWND>`. Naive `pin_app` calls passed these transient sub-AUMIDs directly to `IVirtualDesktopPinnedApps::PinAppID`, pinning only the single active window instance while leaving sibling windows unpinned on other desktops. Resolved by extracting the canonical base package identifier (`split_once("~Wh~")`), registering the base package in the registry, and iterating active shell views to synchronize sibling instances via `IVirtualDesktopPinnedApps::PinView` (achieving 100% parity with native Windows Task View).
  * **FFI Signature Hardening**: Corrected a critical COM FFI signature bug in `IApplicationViewCollection::get_views` and related methods in `src/interfaces.rs` (`*mut IObjectArray` -> `*mut Option<IObjectArray>`), preventing invalid pointer initialization and potential access violations during shell enumeration.
  * **Dynamic Transition Reconciliation (`SyncPinnedApps`)**: Added `sync_pinned_apps()` (exported via C-ABI and Rust wrapper `desktop::sync_pinned_apps`), which dynamically reconciles newly opened or desynchronized sibling windows across virtual desktop switches.
  * **Automated Interactive & Headless Verification Suite**: Authored `tests/test_pinning_suite.py` to empirically validate the distinction between `PinWindow` (individual window isolation) and `PinApp` (application package propagation), testing multi-window propagation, dynamic desktop-switch reconciliation, and clean workspace teardown across live Windows Terminal and Notepad instances.
* **Key Documentation**:
  * 🪟 **[Upstream VirtualDesktopAccessor PR #115](https://github.com/Ciantic/VirtualDesktopAccessor/pull/115)**
  * 🪟 **[VirtualDesktopAccessor COM Heap Hardening & RAII Architecture (008)](docs/pyvda/008_virtual_desktop_accessor_com_heap_hardening_and_raii_breakdown.md)** *(Active PR #115 & Multi-Window Breakdown)*
  * 🪟 **[WinVDA Engine Realization & Caster Migration (006)](docs/pyvda/006_winvda_clean_room_engine_realization_and_caster_migration.md)**
  * 🪟 **[Task View Pinning Internals & Shell Reverse Engineering (005)](docs/pyvda/005_task_view_pinning_internals_and_shell_reverse_engineering.md)**
  * 🪟 **[Adversarial Audit & Hardened COM Architecture (004)](docs/pyvda/004_adversarial_audit_and_hardened_com_architecture.md)**
  * 🧠 **[Repository Brain (Canonical SSOT)](docs/context/repository-brain.md)**

### 7. Native Win32 App Switcher & Tier 4 Taskbar Fail-Safe (Active Production v3.1)
* **Status (Active Production)**: Upgraded the **production focus engine** in [`caster_user_content/util/app_switcher.py`](caster_user_content/util/app_switcher.py) with a deterministic **Tier 4 Taskbar Keystroke Fail-Safe** (`Win+T` traversal / `Win+<N>`) to bypass Windows UIPI foreground locks when switching away from elevated windows.
* **Core Architecture & UIPI Delineation**:
  * **0–10ms Direct Fast Path (Tiers 1–3)**: Preserves sub-millisecond Win32 focus transitions via `SetForegroundWindow`, guarded `_alt_key_bypass()`, and `_attached_threads()` input queue attachment.
  * **UIPI Elevation Boundary & Tier 4 Fail-Safe**: Diagnosed complete focus escalation denial (Win32 Error 5: `Access is denied`) when an elevated process (e.g. Windhawk, Task Manager) owns the foreground. Lower-integrity speech processes cannot inject input or attach threads to higher-integrity windows. Replaced the obsolete Windows 10 UIA click fallback with read-only taskbar discovery (`get_taskbar_order`) and deterministic shell hotkey delegation (`Win+<N>` or `Win+T, home, right:..., enter`), allowing `explorer.exe` to execute the window switch.
  * **Critical Integrity Delineation**: While speech commands cannot drive or inject keystrokes into elevated windows (which Windows UIPI strictly forbids), focusing the unprivileged Caster HUD (`Caster HUD v 1.7.0`) or using Tier 4 shell traversal safely restores command execution for all standard user applications.
* **Key Docs**: [App Switcher Blueprint v3](docs/architecture/app_switcher_architectural_blueprint.md) | [Troubleshooting Findings & UIPI Post-Mortem](docs/troubleshooting/app_switcher_findings.md) | [App Switcher Focus Analysis](docs/architecture/app_switcher_focus_analysis.md) | [App Switcher Evolution Timeline](docs/history/app_switcher_timeline.md).

### 8. Historical Status & Archived Investigations
* **[Repository Timeline & 2-Year Technical Journey](docs/history/repository_timeline.md)**: Historical retrospective covering early repository foundations through mid-2026 (Kaldi ASR migration, desktop automation, AI IDE workflows, and initial window switching). *(Note on Scope: Captures foundations up to mid-2026; consult [Key Engineering](#-key-engineering--voice-automations) and [Recent Focus](#-technical-journey--recent-focus) above for current sub-millisecond Win32 v3, ADCE, and HUD systems).*
* **[Status Update History](status-update-history.md)**: Full archive of previous status updates (including Dynamic Sub-Window Grammar Activation, LexiconCode PR #881 investigation, Wayfinder session, Dragonfly BPC Fork Kaldi race condition fixes, and 2024 development logs).
* **[Kaldi Compiler & Engine Race Condition Post-Mortem](docs/troubleshooting/kaldi_crash_explanation.md)**: Root-cause debugging of Caster speech compiler crashes.
* **[Speech Stack Thread Architecture Report](docs/architecture/Speech_Stack_Thread_Architecture_and_Diagnostic_Report.md)**: Thread interaction models and execution boundaries.
* **[Technical Journey Log](docs/history/technical_journey.md)**: Active and archived engineering focus roadmap.

---

## 📂 Repository Structure

* `caster_user_content/rules/`: Live voice grammars, application-specific rules, and global macros.
* `caster_user_content/util/`: User runtime helpers (e.g., `app_switcher.py`, display scaling utilities).
* `settings/`: User configuration including `settings.toml` (`[plugins]` toggles) and `rules.toml`.
* `scripts/`: Development prototypes, test runners, and validation utilities (e.g., `context_poc.py`, `check_absolute_paths.py`).
* `docs/`: Comprehensive [Documentation Hub](docs/README.md) and [Repository Brain](docs/context/repository-brain.md).
* `.agents/`: Workflows and workspace rules for the Antigravity editor.
* `config/examples/`: Sanitized environment and settings templates. (Personal local configurations in `settings/` and `data/` are strictly untracked).
