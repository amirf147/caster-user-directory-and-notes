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
| **Global Rules** | `caster_user_content/rules/global/` | - | Stable |
| **App-Specific Rules** | `caster_user_content/rules/apps/` | - | Evolving |
| **App Switcher** | `caster_user_content/util/app_switcher.py` | `docs/features/window-management.md` (Planned) | Legacy / Redesigning |
| **Wayfinder (Micro MCP)** | `experiments/mcp/` (Planned) | `docs/research/wayfinder/` | Exploratory |

## 4. Current Facts & Architecture: Window Management (Wayfinder)

The Wayfinder initiative investigates dependable Windows window management, tab discovery, and element actions for Caster.

**Current Facts regarding App Switching & Deadlocks:**
- This is an exploration and potential architectural improvement, **not an emergency fix for a proven COM deadlock**.
- The only observed hard "freezes" have been traced to PowerShell QuickEdit pausing `stdout` while the app switcher tried to log.
- A Python COM deadlock is **not proven**. Do not reintroduce the disproven causal chain "PowerShell/QuickEdit freeze = Python COM deadlock."
- `win32gui.GetForegroundWindow()` is the preferred lightweight way to read the active HWND. Avoid UIA active-window traversal when only the HWND is needed.
- A measured 10.44-second switch delay occurred before target resolution, not during a successful focus attempt (which took ~201 ms).
- Browser tabs are not top-level windows. A design based only on `EnumWindows` and fuzzy title matching cannot locate a background tab reliably.

**Decided Direction (Wayfinder):**
- The current direction is an **experimental C#/.NET Micro MCP Server** using **FlaUI.UIA3**.
- It exposes a small set of macro-level capabilities (window discovery/focus, tab discovery, element action) to Caster via JSON-RPC/MCP over local `stdio`.
- Keep COM objects and UIA event handling inside the C# process. Do not send COM proxies across threads or into Python; return serialized snapshots only.
- The runtime voice path must be deterministic and use one pre-planned tool call, not LLM exploration.
- Make the server stateless for the MVP. Aliases and rule-specific tab hotkey knowledge remain client-side.

**Unresolved Questions (Do not silently decide):**
- The final transport for potential simultaneous Caster and LLM clients (`stdio` versus named pipes/local HTTP).
- The exact tool schemas and the Caster process-lifecycle owner.
- The final server name and whether it eventually grows into a broader accessibility server.
- Virtual-desktop manipulation and taskbar-UIA fallback (deferred from MVP).

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
