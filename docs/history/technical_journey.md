[ 🏠 Docs Home ](../README.md) › [ 📁 History ](../README.md#history) › **Technical Journey & Recent Focus**

---

# Technical Journey & Recent Focus

Our ongoing work focuses on real-time desktop context tracking, window switching, accessibility mechanics, and speech engine responsiveness. Below is a structured summary of our journey, ordered from active production focus back to foundational milestones:

### 1. Active Production: Cross-Platform Native HUD Process Hardening & Strategy Pattern
- **Status (Active Production - Deployed & Verified)**: Refactored and hardened Caster's native Heads-Up Display process lifecycle (`castervoice/asynch/hud_support.py`), eliminating orphaned processes, process-launch race conditions, and unhandled socket errors. Encapsulated OS-specific process containment using the **Strategy Pattern** (`process_lifecycle.py`), implementing native Windows Job Objects (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`), Linux `prctl(PR_SET_PDEATHSIG)` process groups, and macOS session isolation. Built self-healing auto-recovery on `show_hud()`, graceful termination `stop_hud()`, port-release verification, clean `restart_hud()`, and asynchronous queuing in `HudPrintMessageHandler`. Added comprehensive voice commands in `caster_rule.py` and prepared a standalone upstream branch (`feat/hud-process-hardening`, commits `08d6aae3`, `06355d4e`) decoupled from the plugin system.
- **Key Documentation**:
  * 🏛️ **[Native HUD Process Lifecycle & Plugin Decoupling (017)](../caster_hud/017_native_hud_process_lifecycle_and_plugin_decoupling.md)** *(Active Production Architecture & Canonical Reference)*
  * 📋 **[Caster HUD Master Requirements & Specifications (005)](../caster_hud/005_caster_hud_requirements_and_specifications.md)**
  * 🧠 **[Repository Brain (Canonical SSOT)](../context/repository-brain.md)**
  * 📜 **[Status Update History](../../status-update-history.md)**

---

### 2. Active Production: Core Engine Microphone Listener Observer Pattern
- **Status (Active Production - Deployed & Verified)**: Implemented a first-class observer pattern in Caster core (`castervoice/lib/ctrl/mgr/engine_manager.py`, commit `698de89a`, branch `feat/engine-mic-listener`) for tracking microphone state transitions (`sleeping`, `listening`, `off`). Eliminates polling and monkey-patching across UI overlays, foot pedal hardware bridges, and external telemetry streams. Synchronously and deterministically delivers state transitions to registered observers with isolated exception boundaries.
- **Key Documentation**:
  * 🏛️ **[Native HUD Process Lifecycle & Plugin Decoupling (017)](../caster_hud/017_native_hud_process_lifecycle_and_plugin_decoupling.md)**
  * 🧠 **[Repository Brain (Canonical SSOT)](../context/repository-brain.md)**

---

### 3. Active Production: Native Taskbar HUD Windhawk Mod & Standalone Plugin Catalog (Published)
- **Status (Active Production - Published & Deployed)**: Implemented, verified, and published the native C++ Windhawk modification (`caster-taskbar-hud.wh.cpp`, 1612 lines) in its dedicated standalone distribution repository at **[`amirf147/caster-taskbar-hud`](https://github.com/amirf147/caster-taskbar-hud)**, and launched the modular plugin distribution repository at **[`amirf147/caster-plugins`](https://github.com/amirf147/caster-plugins)**.
- **Core Architecture & Breakthroughs**:
  - **In-Process Shell XAML Injection**: Hooks `taskbar.dll` symbols (`CTaskBand::GetTaskbarHost`, `TaskbarHost::FrameHeight`, `TrayUI::StartTaskbar`) in `explorer.exe` to mount native WinRT XAML controls within `SystemTrayFrameGrid` across primary and secondary taskbars.
  - **Asynchronous Overlapped Named Pipe IPC**: Listens on `\\.\pipe\CasterTaskbarHud`, ingesting JSON telemetry asynchronously with `<0.5ms` deserialization marshaled to the UI thread via `WH_CALLWNDPROC`.
  - **Unified Single Command Strip Pivot**: Diagnosed horizontal button panel encroachment where multi-pill layouts clipped running application buttons in `TaskListButtonPanel`. Pivoted to a compact, unified command strip (~160px) displaying dynamic contextual telemetry strings (e.g., `Ready (VS Code)`, `Terminal | VS Code`).
  - **In-Situ Context Menu & Registry Persistence**: Hooked XAML `RightTapped` on the taskbar container to render a native Win32 popup menu (`TrackPopupMenuEx`), enabling live mode toggling (single strip, rotating carousel, multi-box) persisted to `HKCU\Software\Caster\TaskbarHud`.
  - **Standalone Plugin Catalog (`caster-plugins`)**: Decoupled the HUD plugins from core Caster, establishing `amirf147/caster-plugins` as the independent distribution catalog with automated GitHub Actions CI safety checks and live telemetry showcase animations.
- **Key Documentation**:
  * 🌐 **[Caster Taskbar HUD Repository](https://github.com/amirf147/caster-taskbar-hud)** *(Dedicated Windhawk Mod Distribution)*
  * 📦 **[Caster Plugins Distribution Repository](https://github.com/amirf147/caster-plugins)** *(Independent Plugin Catalog)*
  * 🖥️ **[Taskbar HUD Windhawk Injection & Telemetry Explainer (012)](../caster_hud/012_taskbar_hud_windhawk_mod_and_caster_bridge_explainer.md)** *(Subsystem Architecture & Unified Strip Pivot)*
  * 📋 **[Caster HUD Master Requirements & Specifications (005)](../caster_hud/005_caster_hud_requirements_and_specifications.md)**
  * 📜 **[Status Update History](../../status-update-history.md)**

---

### 4. Active Production: Automated Rule Catalog & Decoupled ADCE Context Resolution
- **Status (Active Production - Deployed & Verified)**: Replaced static process lookup tables and fragile IDE terminal heuristics in `taskbar_hud/context_resolver.py` with an automated AST-based rule catalog. Automatically scans user and core rule directories on startup without initializing the speech engine or executing module code. Synchronizes active rule resolution with `rules.toml` via file modification monitoring, providing accurate contextual rule reporting on the Windows 11 Taskbar HUD.
- **Key Documentation**:
  * 🏛️ **[Automated Rule Catalog & ADCE Context Resolution (016)](../caster_hud/016_automated_rule_catalog_and_adce_context_resolution.md)** *(Active Production Architecture & Canonical Reference)*
  * 🏛️ **[Foundational Plugin System & HUD Modularization (015)](../caster_hud/015_foundational_plugin_system_and_hud_modularization.md)**
  * 🧠 **[Repository Brain (Canonical SSOT)](../context/repository-brain.md)**
  * 📜 **[Status Update History](../../status-update-history.md)**

---

### 5. Active Production: Foundational Plugin Architecture, HUD Modularization, & User Content Separation
- **Status (Active Production - Deployed & Verified)**: Built and deployed the foundational Caster Plugin Architecture (`PluginBase`, `PluginManager`), replacing hardcoded startup hooks in `_caster.py` and eliminating pseudo-rules disguised as voice grammars. Modularized the Heads-Up Display into discrete plugins (`standard_hud`, `themed_hud`, `taskbar_hud`), establishing clean separation between upstream legacy interfaces and custom setups. Relocated all official bridges into `castervoice/plugins/`, restoring `caster_user_content/` strictly to user voice rules and personal configurations.
- **Core Engineering Breakthroughs**:
  - **Elimination of Pseudo-Rules and Splicing Anti-Patterns**: Diagnosed the architectural limitation of Caster's legacy grammar loader (`ContentLoader`), which recognized only `get_rule`, `get_transformer`, and `get_hook`. Prior to this architecture, non-grammar integrations were forced into dummy `MappingRule` instances (`taskbar_hud_rule.py`) or hardcoded imports in `_caster.py`. The new `PluginManager` discovers, initializes, and starts all optional subsystems cleanly via standard lifecycle phases.
  - **PluginBase Lifecycle Contract**: Implemented `PluginBase` in `castervoice/lib/plugin.py` with deterministic `initialize(nexus, config)`, `start()`, and `stop()` phases. Pre-engine registration hooks print message handlers and microphone listeners; post-engine startup launches background threads, Named Pipe workers, and GUI processes.
  - **Failure Isolation & Non-Fatal Execution**: Hardened `PluginManager` against plugin initialization exceptions. If a third-party or optional plugin raises an unhandled error, `PluginManager` logs a traceback without interrupting Caster core startup or blocking speech recognition.
  - **HUD Taxonomy Formalization**:
    - `standard_hud`: Preserves the upstream master monolithic HUD (`dictation-toolbox/Caster`) for minimal memory environments.
    - `themed_hud`: Packages the advanced modular PyQt HUD developed in `custom-setup` (10+ QSS themes, opacity controls, status header, rules tag bar, ADCE strip, frameless drag mode).
    - `taskbar_hud`: Integrates the Windows 11 Taskbar Windhawk mod Named Pipe bridge (`\\.\pipe\CasterTaskbarHud`), delivering hands-free feedback directly inside the Windows shell with zero desktop window footprint.
  - **Repository Boundary Enforcement**: Cleaned up `caster_user_content/util/` by removing redundant bridge drivers (`taskbar_hud_bridge.py`, `taskbar_hud_printer_handler.py`) and deleting `taskbar_hud_rule.py`. Standardized on direct bare module imports (`from adce import ...`) across user rules and tests, completely deleting transitional shims (`adce_bridge.py`).
  - **Automated Regression Testing**: Created `test_plugin_manager.py` (5 unit tests), `test_plugin_cli.py` (3 unit tests), and updated `test_taskbar_hud_decoupled.py` (4 unit tests) and `test_focus_transition_sequence.py`. All 58 tests across 11 modules passed in 3.56 seconds with zero failures and zero regressions.
- **Key Documentation**:
  * 🏛️ **[Foundational Plugin System & HUD Modularization (015)](../caster_hud/015_foundational_plugin_system_and_hud_modularization.md)** *(Active Production Architecture & Canonical Reference)*
  * 🏛️ **[Out-of-Process Desktop Observation & ADCE HUD Realization (014)](../caster_hud/014_out_of_process_desktop_observation_and_adce_hud_realization.md)**
  * 📋 **[Caster HUD Master Requirements & Specifications (005)](../caster_hud/005_caster_hud_requirements_and_specifications.md)**
  * 🧠 **[Repository Brain (Canonical SSOT)](../context/repository-brain.md)**
  * 📜 **[Status Update History](../../status-update-history.md)**

---

### 6. Active Production: WinVDA Zero-Cached-State Virtual Desktop Engine (Published & Caster Production Migration)
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

### 7. Active Production: Upstream VirtualDesktopAccessor COM Hardening, RAII Architecture, & Multi-Window Pinning Engine
- **Status (Active Production - Upstream PR #115 & Branch `fix/xaml-island-multi-window-pinning`)**: Diagnosed and resolved two chronic architectural limitations in `Ciantic/VirtualDesktopAccessor` (`src/comobjects.rs`, `src/interfaces.rs`), the native C-ABI DLL underpinning virtual desktop switching and window pinning across Caster, AutoHotkey, and Windows automation utilities: (1) an unmanaged COM task memory leak in `GetAppUserModelId`, and (2) multi-window application pinning disparity in modern Windows Shell environments.
- **Core Engineering Breakthroughs**:
  - **COM Task Memory Leak Diagnosis & RAII Architecture (PR #115)**: Uncovered unmanaged heap leakage in `IApplicationView::GetAppUserModelId`. The Windows Shell allocates UTF-16 AUMID buffers on the process COM task heap via `CoTaskMemAlloc`. In the upstream library, `get_iapplication_id_for_view` discarded the returned pointer without calling `CoTaskMemFree`, leaking unmanaged memory on every pinning query or modification (`is_pinned_app`, `pin_app`, `unpin_app`). Following architectural alignment with upstream repository owner Jari Pennanen (`Ciantic`), refactored raw pointer aliasing into an idiomatic Rust RAII wrapper: `#[repr(transparent)] struct APPIDPWSTR(pub PWSTR)` with `impl Drop` calling `CoTaskMemFree`. Transferring `APPIDPWSTR` by value across the COM vtable boundary guarantees zero-touch calling site preservation with deterministic cleanup on return and error unwinding.
  - **Multi-Window XAML Island Application Pinning (`fix/xaml-island-multi-window-pinning`)**: Modern packaged applications and WinUI 3 / XAML Island architectures (such as Windows Terminal and tabbed Windows Notepad) generate synthetic sub-AUMIDs suffixed with `~Wh~w<HEX_HWND>`. Naive `pin_app` calls passed these transient sub-AUMIDs directly to `IVirtualDesktopPinnedApps::PinAppID`, pinning only the single active window instance while leaving sibling windows unpinned on other desktops. Resolved by extracting the canonical base package identifier (`split_once("~Wh~")`), registering the base package in the registry, and iterating active shell views to synchronize sibling instances via `IVirtualDesktopPinnedApps::PinView` (achieving 100% parity with native Windows Task View).
  - **FFI Signature Hardening**: Corrected a critical COM FFI signature bug in `IApplicationViewCollection::get_views` and related methods in `src/interfaces.rs` (`*mut IObjectArray` -> `*mut Option<IObjectArray>`), preventing invalid pointer initialization and potential access violations during shell enumeration.
  - **Dynamic Transition Reconciliation (`SyncPinnedApps`)**: Added `sync_pinned_apps()` (exported via C-ABI and Rust wrapper `desktop::sync_pinned_apps`), which dynamically reconciles newly opened or desynchronized sibling windows across virtual desktop switches.
  - **Automated Interactive & Headless Verification Suite**: Authored `tests/test_pinning_suite.py` to empirically validate the distinction between `PinWindow` (individual window isolation) and `PinApp` (application package propagation), testing multi-window propagation, dynamic desktop-switch reconciliation, and clean workspace teardown across live Windows Terminal and Notepad instances.
- **Key Documentation**:
  * 🪟 **[Upstream VirtualDesktopAccessor PR #115](https://github.com/Ciantic/VirtualDesktopAccessor/pull/115)**
  * 🪟 **[VirtualDesktopAccessor COM Heap Hardening & RAII Architecture (008)](../pyvda/008_virtual_desktop_accessor_com_heap_hardening_and_raii_breakdown.md)** *(Active PR #115 & Multi-Window Breakdown)*
  * 🪟 **[WinVDA Engine Realization & Caster Migration (006)](../pyvda/006_winvda_clean_room_engine_realization_and_caster_migration.md)**
  * 🪟 **[Task View Pinning Internals & Shell Reverse Engineering (005)](../pyvda/005_task_view_pinning_internals_and_shell_reverse_engineering.md)**
  * 🪟 **[Adversarial Audit & Hardened COM Architecture (004)](../pyvda/004_adversarial_audit_and_hardened_com_architecture.md)**
  * 🧠 **[Repository Brain (Canonical SSOT)](../context/repository-brain.md)**

---

### 8. Active Production: Out-of-Process Desktop Context Observation & ADCE HUD Realization
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

### 9. Sub-Millisecond Native Win32 App Switcher Refactor (Active Production v3.1)
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

### 10. Wayfinder Session: App Switching & UIA Threading Investigation
- **Condensed Summary**: Investigated perceived freezes in `app_switcher.py` and UIA/COM threading performance across speech stacks. Discovered through empirical telemetry (`ca5dc70`) that apparent hangs were caused by Windows PowerShell QuickEdit mode pausing standard output (`stdout`) during console logging.
- **Key Docs & Code**:
  - Feature Guide: **[App Switcher Documentation](../features/app_switcher.md)**
  - Session Index: **[Wayfinder UIA & Threading Directory](../wayfinder-uia-threading/map.md)**
  - Rule & Utility Code: **[window_switching.py](../../caster_user_content/rules/global/window_switching.py)** & **[app_switcher.py](../../caster_user_content/util/app_switcher.py)**

---

### 11. Historical Status & Archived Investigations
- Archive of past status updates with deep dives into Dynamic Sub-Window Grammar Activation, LexiconCode PR #881 investigation, the Dragonfly BPC Fork Kaldi race condition fixes, and UIA threading synthesis:
  👉 **[Status Update History](../../status-update-history.md)**

---

### 12. Git Evolution & Subsystem Timelines
For complete historical retrospectives spanning our 27-month, 969-commit repository evolution:
- 📜 **[App Switcher Evolution Timeline](app_switcher_timeline.md)**: 2-year journey across 6 eras of window switching.
- 📜 **[Caster Printer & HUD Timeline](caster_printer_hud_timeline.md)**: Evolution of status messaging and async HUD overlays.
- 📜 **[Repository Master Timeline](repository_timeline.md)**: Comprehensive 4-era narrative covering 27 months of hands-free Voice OS engineering.
- 🌐 **[Interactive Timeline Visualizer](timeline.html)**: Interactive web timeline application.

