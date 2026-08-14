---
Status: Active
Last verified: 2026-08-14
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

1.  **Source Code & Empirical Tests** (Highest priority)
2.  **ADR / Current Context** (This document)
3.  **Canonical Feature Guides**
4.  **Research Documents / Open Tickets**
5.  **Archive / Old History** (Lowest priority)

*Note: The Wayfinder corpus has evolved theories alongside later empirical corrections. Rely on the facts consolidated here rather than older research documents.*

## 2. Mission and Runtime Boundaries

**Mission:** Maintain a highly reliable, deterministic, Windows-only personal Caster/Dragonfly configuration for voice-driven productivity.

**Runtime Boundaries:**
- The active, loadable Caster rules live strictly in `caster_user_content/`.
- Local configuration (`settings/`, `data/`, environment variables) must remain untracked. They are needed for a functioning local setup but are not part of the distributable code payload.
- Experimental prototypes and LLM "computer use" explorations (e.g., standalone MCP servers) must not interfere with the deterministic voice execution path. They belong in experiments or a gated experimental folder.

## 3. Active Component Map

| Feature / Component | Code Location | Canonical Documentation | Maturity |
| :--- | :--- | :--- | :--- |
| **Global Rules** | `caster_user_content/rules/global/` | - | Stable / Production |
| **App-Specific Rules** | `caster_user_content/rules/apps/` | - | Evolving |
| **App Switcher & Window Focus** | `caster_user_content/util/app_switcher.py` | [`docs/features/app_switcher.md`](../features/app_switcher.md) | Active / Production |
| **Foot Pedal Integration** | `caster_user_content/util/foot_pedal.py` | [`docs/features/foot_pedal.md`](../features/foot_pedal.md) | Active / Production |
| **LexiconCode Dynamic Window Switching** | `caster_user_content/rules/global/window_switching.py` | [`docs/features/lexicon_code_window_switching_functionality.md`](../features/lexicon_code_window_switching_functionality.md) | Evaluating / Active |
| **Numeric CCR Integration** | `caster_user_content/rules/global/numeric.py` | [`docs/features/number-series-ccr-analysis.md`](../features/number-series-ccr-analysis.md) | Active / Production |

## 4. Current Facts & Architecture: Window Management & UIA Research

Findings and operational facts synthesized from empirical stress testing and the Wayfinder research session on Windows UI Automation (UIA) and COM apartment threading:

**Empirical Facts regarding App Switching & Threading:**
- Production window switching is actively performed by [`app_switcher.py`](../../caster_user_content/util/app_switcher.py) using Win32 focus APIs with an OS bypass fallback (`AttachThreadInput` + Alt key injection) to overcome Windows foreground locks.
- The only observed hard "freezes" during testing were traced to Windows PowerShell QuickEdit mode pausing console `stdout` when Caster attempted to log messages.
- A Python COM deadlock is **disproven/unsupported** by empirical logs. Do not reintroduce the disproven causal chain "PowerShell/QuickEdit freeze = Python COM deadlock."
- `win32gui.GetForegroundWindow()` is the preferred lightweight way to read the active HWND. Avoid heavy UIA active-window traversal when only the HWND is needed.
- A measured 10.44-second switch delay occurred during window title resolution, not during a successful focus attempt (which took ~201 ms).
- Browser tabs are not top-level windows; tab switching is handled via hotkey cycling (`Ctrl+Tab`, `Ctrl+PgDn`).

**Exploratory Research & Prototypes (Wayfinder Session):**
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
- **Synchronous Execution:** Brief synchronous blocking during a focus command is correct. Later voice input must not be sent to a window whose focus transition is still in flight. Execution must be bounded, observable, and recoverable.
- **Process Lifecycle:** The client owns the child-process lifecycle for MCP servers and must always terminate/await the server in `try`/`finally` to avoid orphan processes.
- **UIA Traversal:** Do not add unbounded UIA traversals, busy waits, or unsafely shared COM objects. Use `CacheRequest` for narrow properties.
- **Focus Verification:** After every focus attempt, verify that the target became foreground within a finite timeout. Return a clear failure rather than spinning or sleeping indefinitely.
