---
Status: Active
Last verified: 2026-09-23
Canonical/Related code: caster_user_content/
Supersedes: docs/wayfinder-uia-threading/codex-context-extract.md, docs/legacy_notes/*
---

[ 🏠 Docs Home ](../README.md) › [ 📁 Context ](../README.md#context) › **Repository Brain**

---

# Repository Brain: Empirical Baseline & Working Constraints

**Purpose:** This document captures the current working understanding, empirically observed behaviors, verified architectural constraints, and operational boundaries of the repository as of **September 2026**. It serves as an orienting baseline for both human developers and AI agents.

**Epistemic Posture & Falsifiability:**
- **Empirical Baseline, Not Immutable Dogma:** Findings recorded here reflect concrete telemetry and code state at the time of verification. They should guide decisions, but they remain open to falsification whenever new runtime behavior, OS updates, or empirical benchmarks contradict them.
- **Verify Before Concluding:** Future models and contributors should not treat past notes as unquestionable dogma. When an anomaly arises, verify against active code and live OS telemetry rather than assuming past conclusions are permanently infallible.

## 1. Truth Hierarchy

When resolving conflicting information within this repository, adhere to the following order of precedence:

1. **Source Code & Live Empirical Tests** (Highest priority — physical reality always trumps documentation)
2. **Current Baseline & Active Architecture Specs** (This document & living subsystem blueprints)
3. **Canonical Feature Guides & Runbooks**
4. **Research Tickets & Exploratory Logs**
5. **Archived / Incubator Notes** (Lowest priority — e.g., superseded Wayfinder tickets or incubation drafts)

## 2. Mission and Runtime Boundaries

**Mission:** Maintain a highly reliable, deterministic, Windows-only personal Caster/Dragonfly configuration for voice-driven productivity, paired with high-performance desktop context awareness for AI agents.

**Runtime Boundaries:**
- The active, loadable Caster rules live strictly in `caster_user_content/rules/`.
- Official Caster infrastructure, external service bridges, and visual interfaces reside in Caster source under `castervoice/plugins/` or `castervoice/lib/`.
- Never place background daemons, Named Pipe bridges, or SSE stream listeners in `caster_user_content/` disguised as Dragonfly `MappingRule` pseudo-rules. All integrations must implement `PluginBase` and be registered in `settings.toml [plugins]`.
- Never commit secrets or absolute file paths; store local environment references in the untracked `caster_user_content/environment_variables.py`.
- Experimental tools or test scripts must not interfere with the deterministic voice execution path.

## 3. Subsystem & Component Map

### A. Active Voice Productivity Stack (Daily Personal Use)

| Feature / Component | Code Location | Canonical Documentation | Status / Role |
| :--- | :--- | :--- | :--- |
| **Plugin Infrastructure** | [`castervoice/lib/plugin.py`](https://github.com/dictation-toolbox/Caster), [`castervoice/lib/ctrl/mgr/plugin_manager.py`](https://github.com/dictation-toolbox/Caster) | [`docs/caster_hud/015`](../caster_hud/015_foundational_plugin_system_and_hud_modularization.md) | Active / Production (`PluginBase`, `PluginManager`, Failure Isolation) |
| **Global Rules** | [`caster_user_content/rules/global/`](../../caster_user_content/rules/global/) | - | Active / Production |
| **App-Specific Rules** | [`caster_user_content/rules/apps/`](../../caster_user_content/rules/apps/) | - | Evolving / Active |
| **App Switcher & Window Focus** | [`caster_user_content/util/app_switcher.py`](../../caster_user_content/util/app_switcher.py) | [`docs/features/app_switcher.md`](../features/app_switcher.md) | Active / Production v3.1 (Sub-millisecond Win32 + Tier 4 Shell Hotkey Fail-Safe) |
| **Virtual Desktop Management & Pinning** | `castervoice/lib/windows_virtual_desktops.py` & `window_mgmt_rule.py` | [`docs/pyvda/006`](../pyvda/006_winvda_clean_room_engine_realization_and_caster_migration.md), [`docs/features`](../features/virtual_desktop_pinning_and_grammar_ergonomics.md) | Active / Production (Migrated to **WinVDA**) |
| **Modular HUD Plugins** | `caster_user_content/plugins/themed_hud/`, `castervoice/plugins/standard_hud/`, `caster_user_content/plugins/taskbar_hud/` | [`docs/caster_hud/015`](../caster_hud/015_foundational_plugin_system_and_hud_modularization.md), [`docs/caster_hud/014`](../caster_hud/014_out_of_process_desktop_observation_and_adce_hud_realization.md), [`docs/caster_hud/005`](../caster_hud/005_caster_hud_requirements_and_specifications.md) | Active / Production (HUD Taxonomy: Themed, Standard, and Taskbar Plugins) |
| **Native HUD Process Lifecycle** | `castervoice/asynch/hud_support.py`, `castervoice/asynch/process_lifecycle.py` | [`docs/caster_hud/017`](../caster_hud/017_native_hud_process_lifecycle_and_plugin_decoupling.md) | Active / Production (`ProcessStrategy`, Win32 Job Objects, Auto-Recovery) |
| **Engine Mic Observer Pattern** | `castervoice/lib/ctrl/mgr/engine_manager.py` | [`docs/caster_hud/017`](../caster_hud/017_native_hud_process_lifecycle_and_plugin_decoupling.md) | Active / Production (`register_mic_mode_listener` observer callbacks) |
| **Foot Pedal Integration** | [`caster_user_content/rules/caster_toggle_mic_key.py`](../../caster_user_content/rules/caster_toggle_mic_key.py) | [`docs/features/foot_pedal.md`](../features/foot_pedal.md) | Active / Production |

### B. External Subsystem Integrations

| Subsystem | Integration Point in Caster | External Authority / Repository | Status / Relationship |
| :--- | :--- | :--- | :--- |
| **Active Desktop Context Engine (ADCE)** | `caster_user_content/plugins/adce/` (`AdcePlugin`, SSE client on port 8424, atomic cache, `FuncContext` predicates) | [`amirf147/active-desktop-context-engine`](https://github.com/amirf147/active-desktop-context-engine) | External Authority & Single Source of Truth for Desktop Window Focus, Titles, Process Identity, and Sub-Window Semantic Interaction Zones |
| **Taskbar HUD Windhawk Mod** | `caster_user_content/plugins/taskbar_hud/` (`TaskbarHudPlugin`, Named Pipe `\\.\pipe\CasterTaskbarHud`) | [`amirf147/caster-taskbar-hud`](https://github.com/amirf147/caster-taskbar-hud) & [`windhawk-mods`](https://github.com/ramensoftware/windhawk-mods) (`caster-taskbar-hud.wh.cpp`) | Published Native Taskbar XAML In-Process Shell Mod |
| **Modular Plugin Distribution** | `caster_user_content/plugins/` | [`amirf147/caster-plugins`](https://github.com/amirf147/caster-plugins) | Standalone Plugin Distribution Catalog (`themed_hud`, `taskbar_hud`) |
| **WinVDA Engine** | `winvda` package import in Caster Virtual Desktops | [`amirf147/winvda`](https://github.com/amirf147/winvda) | Upstream Clean-Room Engine |

### C. Evaluated Experiments & In-Flight Research

| Feature / Exploration | Code Location | Documentation | Status / Note |
| :--- | :--- | :--- | :--- |
| **LexiconCode Window Switching** | [`caster_user_content/rules/global/window_switching.py`](../../caster_user_content/rules/global/window_switching.py) | [`docs/features/lexicon_code_window_switching_functionality.md`](../features/lexicon_code_window_switching_functionality.md) | Evaluated / Alternative switcher experiment |
| **Numeric CCR Integration** | `castervoice/rules/core/numbers_rules/numeric.py` | [`docs/features/number-series-ccr-analysis.md`](../features/number-series-ccr-analysis.md) | Custom Setup Fork / Upstream PR evaluation |
| **ADCE Python PoC & Spikes** | `attic/adce_spikes/` | [`docs/accessibility_mcp/CONTEXT.md`](../accessibility_mcp/CONTEXT.md) | Archived incubation research |

## 4. Current Empirical Baseline & Architectural Facts

### A. Window Management & App Switching (Production v3.1)
- Production window switching is actively performed by [`app_switcher.py`](../../caster_user_content/util/app_switcher.py) using the **v3.1 progressive 4-tier focus architecture** ([Blueprint v3.1](../architecture/app_switcher_architectural_blueprint.md), [Evolution Timeline](../history/app_switcher_timeline.md)):
  1. **Tier 1 (Direct Win32)**: Sub-millisecond hot path (0–10ms) executing `SetForegroundWindow` and `BringWindowToTop`.
  2. **Tier 2 (Alt-Key Bypass)**: Overcomes `ForegroundLockTimeout` via the guarded `_alt_key_bypass()` context manager with `VK_NONE` (`0xFF`) dummy key injection (80–120ms).
  3. **Tier 3 (Thread Attachment)**: Synchronizes calling and foreground input queues via `_attached_threads()` with shell `SwitchToThisWindow` (120–200ms).
  4. **Tier 4 (Taskbar Shell Hotkey Navigation)**: Resolves the target application's slot index via read-only Windows 11 XAML Island discovery (`TaskListButton` in `Shell_TrayWnd`) and delegates window activation to `explorer.exe` via `Win+<N>` or `Win+T` traversal, completely replacing obsolete Windows 10 UIA mouse clicks.
- **UIPI Security Boundaries & Elevation Delineation**:
  - When an elevated process (High Integrity Level / Administrator, such as Windhawk, Task Manager, or elevated terminals) holds foreground focus, Windows User Interface Privilege Isolation (UIPI) blocks unprivileged processes (Caster, Medium Integrity) from calling `SetForegroundWindow` (Error 5) or `AttachThreadInput` (Error 5).
  - Furthermore, Windows UIPI silently drops all synthetic keyboard events (`keybd_event`, `SendInput`) emitted while an elevated window has focus. Under pure Medium Integrity execution without user interaction, Tiers 1 through 4 are dropped by the OS kernel.
  - The Caster Heads-Up Display overlay (`Caster HUD v 1.7.0`) and the Windows Taskbar (`Shell_TrayWnd`) run at Medium Integrity. A physical hardware mouse click on the HUD or taskbar acts as an "integrity airlock", releasing the elevated foreground lock. Once the foreground process drops to Medium Integrity, Caster regains full Win32 focus rights, allowing the subsequent voice command to succeed immediately on Tier 1 in 25ms.
  - Hands-free voice operation against elevated windows without physical mouse intervention requires running the speech recognition host elevated (Run as Administrator) or compiling with `uiAccess="true"` in a signed application manifest installed in `Program Files`.
  - Detailed telemetry and post-mortems are maintained in [`docs/troubleshooting/app_switcher_findings.md`](../troubleshooting/app_switcher_findings.md) and [`docs/architecture/app_switcher_focus_analysis.md`](../architecture/app_switcher_focus_analysis.md).
- Alias persistence is strictly encapsulated within the `AliasRegistry` class managing `caster_user_content/window_aliases.json`.
- Focus confirmation uses a 10ms micro-polling loop (`verify_focus`), eliminating coarse static sleep delays.
- Observed hard freezes during past testing were traced to Windows PowerShell QuickEdit mode pausing console `stdout` when Caster logged messages.
- A Python COM deadlock hypothesis was disproven by empirical logs; avoid re-attributing console pauses to COM deadlocks.
- `win32gui.GetForegroundWindow()` is the preferred lightweight way to read the active HWND. Avoid heavy UIA active-window traversal when only the HWND is needed.
- Browser tabs are not top-level windows; tab switching is handled via hotkey cycling (`Ctrl+Tab`, `Ctrl+PgDn`).

### B. Virtual Desktop Subsystem (WinVDA Migration)
- Windows Virtual Desktop tracking and application pinning have been migrated to the clean-room native engine **[WinVDA](https://github.com/amirf147/winvda)** ([`docs/pyvda/006`](../pyvda/006_winvda_clean_room_engine_realization_and_caster_migration.md)), resolving upstream PyVDA COM proxy invalidation and multi-window Sub-AUMID blind spots.
- Caster provides voice grammars `([toggle] pin | unpin) window [all work [spaces]]` and `([toggle] pin | unpin) app [all work [spaces]]` in `window_mgmt_rule.py`, routing transitions through `printer.out` for HUD feedback.

### C. Active Desktop Context Engine (ADCE) External Ingestion
- Active engine architecture, C# background daemons, SQLite/DuckDB persistence, and MCP server streaming live in the standalone repository [`amirf147/active-desktop-context-engine`](https://github.com/amirf147/active-desktop-context-engine).
- Caster functions strictly as an **external client consumer**: the standalone ADCE service is the single source of truth for desktop window context (HWND, window titles, process names, and sub-window semantic interaction zones).
- The official ADCE plugin (`castervoice/plugins/adce/`) ingests window events directly from ADCE via SSE (port 8424), caching the state atomically in memory and exposing high-speed `FuncContext` predicates (`is_ide_terminal_focused`, `is_ide_editor_focused`) to Dragonfly grammars.
- All in-process Win32 window focus hooks (`SetWinEventHook`) and polling loops have been completely excised from Caster (`window_tracker.py` is deleted).
- Incubation research tickets (`001`–`018` in [`docs/accessibility_mcp/`](../accessibility_mcp/CONTEXT.md)) are preserved in Caster as historical research references.

### D. Caster HUD Architecture & Ecosystem
- Heads-Up Display interfaces are fully modularized as independent plugins managed by `PluginManager` and toggled via `settings.toml [plugins]`.
- **Themed HUD (`themed_hud`)**: Runs as an isolated Qt process with a background `SimpleXMLRPCServer` daemon. Communicates with Caster core via XML-RPC (port 8338) and ndjson telemetry (port 8339). Avoids UI thread freezes by using thread-safe, non-blocking `QtCore.QCoreApplication.postEvent` calls. Features 10+ accessible themes, opacity controls, status header, sub-window ADCE context strip, active rules tag bar, and frameless drag mode ([`005`](../caster_hud/005_caster_hud_requirements_and_specifications.md), [`014`](../caster_hud/014_out_of_process_desktop_observation_and_adce_hud_realization.md)).
- **Standard HUD (`standard_hud`)**: Encapsulates the upstream master monolithic HUD (`dictation-toolbox/Caster`) as an official plugin, retained for minimal resource environments.
- **Taskbar HUD (`taskbar_hud`)**: Injects real-time speech telemetry directly into the Windows 11 Shell taskbar via Named Pipe (`\\.\pipe\CasterTaskbarHud`), providing hands-free feedback with zero desktop window footprint ([`012`](../caster_hud/012_taskbar_hud_windhawk_mod_and_caster_bridge_explainer.md)).
- Active contextual rules resolution is authoritatively filtered against `_enabled_ordered` and `rules.toml` (via the `context_resolver.py` AST catalog in `taskbar_hud` and `hud_support.py` in the Qt HUD), suppressing disabled companions and inactive application rules ([`016`](../caster_hud/016_automated_rule_catalog_and_adce_context_resolution.md)).
- **Native HUD Process Strategy & Containment**: The core HUD process lifecycle (`hud_support.py`) utilizes the cross-platform Strategy Pattern (`process_lifecycle.py`) to bind child processes to OS-level containment (Win32 Job Objects with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, Linux `prctl(PR_SET_PDEATHSIG)` process groups, and macOS session isolation), preventing orphaned background instances. `HudPrintMessageHandler` uses an asynchronous in-memory queue (`queue.Queue`) and background worker to decouple speech recognition from network latency ([`017`](../caster_hud/017_native_hud_process_lifecycle_and_plugin_decoupling.md)).
- **Engine Microphone Listener Observer Pattern**: `EngineModesManager` (`engine_manager.py`) exposes synchronous observer callbacks (`register_mic_mode_listener`, `unregister_mic_mode_listener`), eliminating polling and monkey-patching for mic status indicators.

### E. Foundational Plugin Architecture & Repository Boundaries
- Caster Core provides a first-class plugin system driven by `PluginBase` (`castervoice/lib/plugin.py`) and `PluginManager` (`castervoice/lib/ctrl/mgr/plugin_manager.py`).
- **Lifecycle Phases**:
  1. `initialize(nexus, config)`: Pre-engine phase for registering print message handlers and microphone listeners.
  2. `start()`: Post-engine phase for launching background threads, Named Pipe workers, and GUI processes.
  3. `stop()`: Termination phase for releasing system resources in reverse initialization order.
- **Failure Isolation**: `PluginManager` wraps plugin initialization in try-except handlers. A failure in an individual plugin logs a traceback without crashing Caster core or preventing speech engine startup.
- **Elimination of Pseudo-Rules**: Background daemons and IPC bridges are no longer wrapped in dummy `MappingRule` instances (`taskbar_hud_rule.py` is deleted). All service lifecycles are governed by `PluginManager`.
- **Repository Boundaries**: Official plugins reside in `castervoice/plugins/`. User space in `caster_user_content/` contains only personal voice grammars, custom macros, and private configurations.

### F. Exploratory Research (Wayfinder Archive)
- Wayfinder was an AI agent research session investigating whether an out-of-process C#/.NET Micro MCP Server using FlaUI.UIA3 could offload accessibility and UIA queries.
- The tickets and findings are archived in [`docs/wayfinder-uia-threading/`](../wayfinder-uia-threading/map.md).

## 5. "Do Not Regress" Constraints

- **Python Version:** Always use `py -3.10`.
- **Plugin Architecture Enforcement:** All background bridges, Named Pipe clients, external IPC listeners, and visual overlays must implement `PluginBase` and be managed by `PluginManager`. Do not create dummy `MappingRule` voice grammars or hardcode service initialization into `_caster.py`.
- **User Content Isolation:** Do not place core infrastructure drivers or Caster library dependencies in `caster_user_content/util/`. Keep `caster_user_content/` strictly reserved for personal voice grammars, custom macros, and private settings.
- **Zero In-Process Window Hooks in Caster:** Do not introduce in-process Win32 window focus hooks (`SetWinEventHook`), foreground window polling loops, or internal ctypes foreground inspection into Caster core or HUD libraries. All desktop window telemetry must originate from the out-of-process ADCE daemon.
- **Authoritative Rule Resolution:** Do not determine active CCR rules based solely on executable regex matches or naive capitalized process names. Rule activity must be validated against `_enabled_ordered` and the user's `rules.toml`.
- **Relative Markdown Links:** All documentation links must be relative to prevent local metadata leaks.
- **Epistemic Discipline & Falsification Spikes:** Do not propose multi-file architectural rewrites or cross-runtime pivots based on theoretical advantages alone. Every major proposal must pass the 4-gate protocol (Telemetry → Adversarial Red-Team → <50-line Micro-Spike → Blueprint).
- **Synchronous Execution:** Brief synchronous blocking during a focus command is correct. Later voice input must not be sent to a window whose focus transition is still in flight. Execution must be bounded, observable, and recoverable.
- **UIA Traversal:** Do not add unbounded UIA traversals, busy waits, or unsafely shared COM objects. Use `CacheRequest` for narrow properties.
- **Focus Verification:** After every focus attempt, verify that the target became foreground within a finite timeout. Return a clear failure rather than spinning or sleeping indefinitely.
