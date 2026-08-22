---
Status: Active
Last verified: 2026-08-22
Canonical/Related code: caster_user_content/
Supersedes: docs/wayfinder-uia-threading/codex-context-extract.md, docs/legacy_notes/*
---

[ 🏠 Docs Home ](../README.md) › [ 📁 Context ](../README.md#context) › **Repository Brain**

---

# Repository Brain

**Purpose:** This document is the canonical project memory and the central source of truth for the repository's architecture, verified facts, decisions, and risks. It is designed to be concise and context-rich for both human developers and AI agents.

**Requirement:** You MUST update this document whenever a confirmed finding changes, an experiment becomes a direction, or a new Architectural Decision Record (ADR) is logged.

## 1. Truth Hierarchy

When resolving conflicting information within this repository, adhere to the following order of precedence:

1. **Source Code & Empirical Tests** (Highest priority)
2. **ADR / Current Context** (This document & [ADCE Context Hub](../accessibility_mcp/CONTEXT.md))
3. **Canonical Feature Guides**
4. **Research Documents / Open Tickets**
5. **Archive / Old History** (Lowest priority)

*Note: The Wayfinder corpus has evolved theories alongside later empirical corrections. Rely on the facts consolidated here rather than older research documents.*

## 2. Mission and Runtime Boundaries

**Mission:** Maintain a highly reliable, deterministic, Windows-only personal Caster/Dragonfly configuration for voice-driven productivity, paired with high-performance real-time desktop context tracking for AI agents.

**Runtime Boundaries:**
- The active, loadable Caster rules live strictly in `caster_user_content/`.
- Local configuration (`settings/`, `data/`, environment variables) must remain untracked. They are needed for a functioning local setup but are not part of the distributable code payload.
- Experimental prototypes and LLM "computer use" explorations (e.g., standalone MCP servers and ADCE monitors in `scripts/`) must not interfere with the deterministic voice execution path. They are triggered explicitly or run as isolated background processes.

## 3. Active Component Map

| Feature / Component | Code Location | Canonical Documentation | Maturity |
| :--- | :--- | :--- | :--- |
| **Global Rules** | [`caster_user_content/rules/global/`](../../caster_user_content/rules/global/) | - | Stable / Production |
| **App-Specific Rules** | [`caster_user_content/rules/apps/`](../../caster_user_content/rules/apps/) | - | Evolving |
| **App Switcher & Window Focus** | [`caster_user_content/util/app_switcher.py`](../../caster_user_content/util/app_switcher.py) | [`docs/features/app_switcher.md`](../features/app_switcher.md) | Active / Production v3 |
| **Active Desktop Context Engine (ADCE)** | [`scripts/context_poc.py`](../../scripts/context_poc.py) & [`caster_user_content/rules/global/context_engine_launcher.py`](../../caster_user_content/rules/global/context_engine_launcher.py) | [`docs/accessibility_mcp/CONTEXT.md`](../accessibility_mcp/CONTEXT.md) | Active Prototype (v2.1) |
| **PyVDA Virtual Desktop Tracking** | Local library dependency (`pyvda`) | [`docs/pyvda/001_pyvda_rpc_and_com_lifecycle_analysis.md`](../pyvda/001_pyvda_rpc_and_com_lifecycle_analysis.md) | Integrated / Resilient |
| **Caster HUD Overlay & IPC** | [`castervoice/asynch/hud.py`](https://github.com/dictation-toolbox/Caster) | [`docs/caster_hud/001_caster_hud_architecture_and_threading_primer.md`](../caster_hud/001_caster_hud_architecture_and_threading_primer.md) | Core Architecture Primer |
| **Foot Pedal Integration** | [`caster_user_content/util/foot_pedal.py`](../../caster_user_content/util/foot_pedal.py) | [`docs/features/foot_pedal.md`](../features/foot_pedal.md) | Active / Production |
| **LexiconCode Window Switching** | [`caster_user_content/rules/global/window_switching.py`](../../caster_user_content/rules/global/window_switching.py) | [`docs/features/lexicon_code_window_switching_functionality.md`](../features/lexicon_code_window_switching_functionality.md) | Evaluating / Active |
| **Numeric CCR Integration** | [`caster_user_content/rules/global/numeric.py`](../../caster_user_content/rules/global/numeric.py) | [`docs/features/number-series-ccr-analysis.md`](../features/number-series-ccr-analysis.md) | Custom Setup Fork / Pending Upstream PR |

## 4. Current Facts & Architecture

### A. Window Management & App Switching (Production v3)
- Production window switching is actively performed by [`app_switcher.py`](../../caster_user_content/util/app_switcher.py) using the **v3 progressive Win32 focus architecture** ([Blueprint v3](../architecture/app_switcher_architectural_blueprint.md), [Evolution Timeline](../history/app_switcher_timeline.md)). Focus transitions operate on a sub-millisecond hot path (0–10ms) via direct Win32 APIs (`SetForegroundWindow`, `BringWindowToTop`), backed by guarded context managers (`_alt_key_bypass`, `_attached_threads`) with `VK_NONE` (`0xFF`) dummy key injection to prevent menu bar lockup.
- Alias persistence is strictly encapsulated within the `AliasRegistry` class managing `caster_user_content/window_aliases.json`.
- Focus confirmation uses a 10ms micro-polling loop (`verify_focus`), eliminating coarse static sleep delays.
- The only observed hard "freezes" during testing were traced to Windows PowerShell QuickEdit mode pausing console `stdout` when Caster attempted to log messages.
- A Python COM deadlock is **disproven/unsupported** by empirical logs. Do not reintroduce the disproven causal chain "PowerShell/QuickEdit freeze = Python COM deadlock."
- `win32gui.GetForegroundWindow()` is the preferred lightweight way to read the active HWND. Avoid heavy UIA active-window traversal when only the HWND is needed.
- Browser tabs are not top-level windows; tab switching is handled via hotkey cycling (`Ctrl+Tab`, `Ctrl+PgDn`).

### B. Active Desktop Context Engine (ADCE) & Accessibility MCP
- **Event-Driven Interception:** The ADCE monitor (`scripts/context_poc.py`) uses native Win32 `SetWinEventHook` listening for `EVENT_SYSTEM_FOREGROUND` (window switches) and `EVENT_OBJECT_FOCUS` (micro-focus changes) initialized in a COM Multithreaded Apartment (MTA). It achieves 0% idle CPU usage.
- **Root Window Anchoring:** Resolves the true top-level application window by anchoring to Win32 `GetForegroundWindow()` rather than climbing up from child Chromium/Gecko render panes (`Chrome Legacy Window` / `DocumentControl`).
- **Deep Tab Extraction:** Walks top-level windows down to depth 14 across Waterfox, Chrome, Firefox, and VS Code/Antigravity, identifying active tabs via `SelectionItemPattern`, legacy MSAA state bitmasks, and focus heuristics.
- **Two-Tier Caching Blueprint:** Tier 1 (Macro Sync on window switch) caches the full tab array; Tier 2 (Micro Mutation on focus change) matches the active tab via $O(1)$ window title comparisons, eliminating deep recursive tree walks on every mouse click.
- **PyVDA COM Lifecycle:** Undocumented Windows Virtual Desktop COM interfaces hosted in `explorer.exe` can become invalid if Explorer restarts. `pyvda`'s `@_com_retry` decorator with exponential backoff and GUID re-hydration (`_refresh()`) is the verified pattern for preventing `RPC_S_SERVER_UNAVAILABLE` (`0x800706BA`) and `RPC_E_DISCONNECTED` (`0x80010108`) crashes.
- **Caster HUD Architecture:** The Caster HUD runs as an isolated OS process with a background `SimpleXMLRPCServer` daemon. It avoids UI thread freezes by using thread-safe, non-blocking `QtCore.QCoreApplication.postEvent` calls to dispatch HTML updates directly to the main Qt GUI event queue.

### C. Exploratory Research (Wayfinder Session)
- Wayfinder was an AI agent research session investigating whether an out-of-process C#/.NET Micro MCP Server using FlaUI.UIA3 could offload accessibility and UIA queries.
- The tickets and findings are archived in [`docs/wayfinder-uia-threading/`](../wayfinder-uia-threading/map.md).
- If an external accessibility server is explored in the future:
  - It must remain an isolated process communicating over local `stdio` or named pipes without blocking the core speech recognition engine.
  - COM objects and UIA event handling remain inside the external process; return serialized snapshots only.
  - The runtime voice path must be deterministic and use one pre-planned tool call, not open-ended LLM exploration loops.
  - The client must own process lifecycle and always terminate/await child processes in `try`/`finally`.

## 5. Local Configuration Contract

- **Ignored files:** `settings/`, `data/`, `sikuli/`, aliases, and environment variables are local and git-ignored.
- **Templates:** Use tracked, safe starter configs (e.g., `config/examples/`) rather than checking in personal state.
- **Secrets:** Never commit absolute paths or API keys. Store them in the untracked `caster_user_content/environment_variables.py`.

## 6. "Do Not Regress" Constraints

- **Python Version:** Always use `py -3.10`.
- **Relative Markdown Links:** All documentation links must be relative to prevent local metadata leaks.
- **Synchronous Execution:** Brief synchronous blocking during a focus command is correct. Later voice input must not be sent to a window whose focus transition is still in flight. Execution must be bounded, observable, and recoverable.
- **Process Lifecycle:** The client owns the child-process lifecycle for MCP servers and must always terminate/await the server in `try`/`finally` to avoid orphan processes.
- **UIA Traversal:** Do not add unbounded UIA traversals, busy waits, or unsafely shared COM objects. Use `CacheRequest` for narrow properties.
- **Focus Verification:** After every focus attempt, verify that the target became foreground within a finite timeout. Return a clear failure rather than spinning or sleeping indefinitely.
