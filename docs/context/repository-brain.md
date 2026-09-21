---
Status: Active
Last verified: 2026-09-21
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
- The active, loadable Caster rules live strictly in `caster_user_content/`.
- Never commit secrets or absolute file paths; store local environment references in the untracked `caster_user_content/environment_variables.py`.
- Experimental tools or test scripts must not interfere with the deterministic voice execution path.

## 3. Subsystem & Component Map

### A. Active Voice Productivity Stack (Daily Personal Use)

| Feature / Component | Code Location | Canonical Documentation | Status / Role |
| :--- | :--- | :--- | :--- |
| **Global Rules** | [`caster_user_content/rules/global/`](../../caster_user_content/rules/global/) | - | Active / Production |
| **App-Specific Rules** | [`caster_user_content/rules/apps/`](../../caster_user_content/rules/apps/) | - | Evolving / Active |
| **App Switcher & Window Focus** | [`caster_user_content/util/app_switcher.py`](../../caster_user_content/util/app_switcher.py) | [`docs/features/app_switcher.md`](../features/app_switcher.md) | Active / Production v3.1 (Sub-millisecond Win32 + Tier 4 Shell Hotkey Fail-Safe) |
| **Virtual Desktop Management & Pinning** | `castervoice/lib/windows_virtual_desktops.py` & `window_mgmt_rule.py` | [`docs/pyvda/006`](../pyvda/006_winvda_clean_room_engine_realization_and_caster_migration.md), [`docs/features`](../features/virtual_desktop_pinning_and_grammar_ergonomics.md) | Active / Production (Migrated to **WinVDA**) |
| **Caster HUD Overlay & IPC** | [`castervoice/asynch/hud.py`](https://github.com/dictation-toolbox/Caster) | [`docs/caster_hud/005`](../caster_hud/005_caster_hud_requirements_and_specifications.md) | Active / Production (5-layer Clean Architecture) |
| **Foot Pedal Integration** | [`caster_user_content/rules/caster_toggle_mic_key.py`](../../caster_user_content/rules/caster_toggle_mic_key.py) | [`docs/features/foot_pedal.md`](../features/foot_pedal.md) | Active / Production |

### B. External Subsystem Integrations

| Subsystem | Integration Point in Caster | External Authority / Repository | Status / Relationship |
| :--- | :--- | :--- | :--- |
| **Active Desktop Context Engine (ADCE)** | `AdceTracker` in Caster HUD (SSE port 8424) | [`amirf147/active-desktop-context-engine`](https://github.com/amirf147/active-desktop-context-engine) | External Daemon / Client Ingestion |
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
- Caster functions strictly as an **external client consumer**: the Caster HUD (`AdceTracker`) connects to the local ADCE daemon via Server-Sent Events (SSE on port 8424) to ingest element-level micro-zones (`{IntegratedTerminal}`, `{EditorCodeBuffer}`) in ~10–20 ms without running internal scrapers.
- Incubation research tickets (`001`–`018` in [`docs/accessibility_mcp/`](../accessibility_mcp/CONTEXT.md)) are preserved in Caster as historical research references.

### D. Caster HUD Architecture
- The Caster HUD runs as an isolated OS process with a background `SimpleXMLRPCServer` daemon. It avoids UI thread freezes by using thread-safe, non-blocking `QtCore.QCoreApplication.postEvent` calls to dispatch HTML updates directly to the main Qt GUI event queue.
- Features opt-in system tray docking (`QSystemTrayIcon`), modular QSS theme switching, interactive profile management (`ProfileDialog`), and 8-direction frameless edge resizing ([`001`](../caster_hud/001_caster_hud_architecture_and_threading_primer.md), [`005`](../caster_hud/005_caster_hud_requirements_and_specifications.md)).

### E. Exploratory Research (Wayfinder Archive)
- Wayfinder was an AI agent research session investigating whether an out-of-process C#/.NET Micro MCP Server using FlaUI.UIA3 could offload accessibility and UIA queries.
- The tickets and findings are archived in [`docs/wayfinder-uia-threading/`](../wayfinder-uia-threading/map.md).

## 5. "Do Not Regress" Constraints

- **Python Version:** Always use `py -3.10`.
- **Relative Markdown Links:** All documentation links must be relative to prevent local metadata leaks.
- **Epistemic Discipline & Falsification Spikes:** Do not propose multi-file architectural rewrites or cross-runtime pivots based on theoretical advantages alone. Every major proposal must pass the 4-gate protocol (Telemetry → Adversarial Red-Team → <50-line Micro-Spike → Blueprint).
- **Synchronous Execution:** Brief synchronous blocking during a focus command is correct. Later voice input must not be sent to a window whose focus transition is still in flight. Execution must be bounded, observable, and recoverable.
- **UIA Traversal:** Do not add unbounded UIA traversals, busy waits, or unsafely shared COM objects. Use `CacheRequest` for narrow properties.
- **Focus Verification:** After every focus attempt, verify that the target became foreground within a finite timeout. Return a clear failure rather than spinning or sleeping indefinitely.
