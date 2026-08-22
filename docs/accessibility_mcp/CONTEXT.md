[ 🏠 Docs Home ](../README.md) › [ 📁 Accessibility MCP ](CONTEXT.md) › **ADCE Living Context Hub**

---

# Active Desktop Context Engine (ADCE) & Accessibility MCP — Evolving Context

This document serves as the **living single source of truth** for the Desktop Context Engine / Accessibility MCP project. It aggregates domain knowledge, architectural decisions, observed behaviors, and roadmap goals from all exploratory research (`001`–`008`).

---

## 1. Project Mission & Core Architecture

The goal of the **Active Desktop Context Engine (ADCE)** is to maintain a live, in-memory semantic graph of the user's active desktop state (active Virtual Desktop, foreground window, open tabs, focused controls, text snippets, and UI coordinates) and expose it to local AI agents and voice grammars (Caster) via the **Model Context Protocol (MCP)** with sub-millisecond query latency and near-zero idle CPU usage.

### Key Architectural Tenets:
1. **Event-Driven Over Polling:** Use native Windows Event Hooks (`SetWinEventHook`) to wake up only on genuine state changes (`EVENT_SYSTEM_FOREGROUND`, `EVENT_OBJECT_FOCUS`), keeping idle CPU at 0%.
2. **Virtual Desktop & Workspace Awareness:** Query Windows Virtual Desktops (`pyvda`) to identify active workspace envelopes; handle COM lifecycle resiliency during desktop transitions.
3. **Observation / Action Decoupling:** The Context Engine is strictly a read-only observer that caches state. Action execution (clicking, typing) happens via a separate Action Server validating against the live context before committing actions.
4. **MTA COM Threading & Async Worker Queues:** Event handlers push tokens to a queue; background workers perform any needed UIA property queries, preventing message loop deadlocks.
5. **Tiered Hybrid Ingestion:** Pair direct browser/editor IPC bridges (WebExtensions Native Messaging / CDP / VS Code Extension API) with universal UIA fallback scraping.

---

## 2. Key Insights & Lessons Learned

| Category | Observation / Finding | Architectural Rule / Solution | Reference Doc |
| :--- | :--- | :--- | :--- |
| **Virtual Desktops** | Virtual desktops provide macro-workspace context (e.g. workspace labels); COM pointers can become stale across Explorer restarts. | Adopt `pyvda`'s `@_com_retry` + `_refresh()` re-hydration pattern; extract desktop names as high-level context envelopes. | [`docs/pyvda/001`](../pyvda/001_pyvda_rpc_and_com_lifecycle_analysis.md), [`008`](008_real_world_observations_and_caching_architecture.md) |
| **UI Threading & HUD** | Caster HUD uses out-of-process Qt + XML-RPC + `postEvent` to guarantee zero freezes on main speech recognition. | Decouple GUI/Observer processes from main engine; use asynchronous thread-safe message queues. | [`docs/caster_hud/001`](../caster_hud/001_caster_hud_architecture_and_threading_primer.md) |
| **Vision Grounding** | VLMs (GPT-4o, Claude) have <10% accuracy on UI element spatial grounding. | Must feed programmatic structural truth (UIA/JSON), not raw screenshots. | [`001`](001_exploration_analysis_planning.md), [`004`](004_deep_research_metaprompt.md) |
| **App SDK vs Scraping** | Windows Recall / App SDK is an opt-in model that ignores legacy apps. | Must maintain a direct UIA scraper fallback for universal coverage. | [`005`](005_semantic_index_and_app_sdk.md) |
| **Pruning Traps** | Electron & Gecko wrap their entire UI in a `DocumentControl`. | Never prune `DocumentControl` near the top of the tree; anchor search to true root `HWND`. | [`007`](007_tab_extraction_and_context_representation.md), [`008`](008_real_world_observations_and_caching_architecture.md) |
| **Multi-Tabstrip & F1** | Sidebars (Tree Style Tab, Sidebery) create multiple active tabs; collapsing with `F1` unmounts them from UIA. | Group tabs by parent container; consider Native Messaging bridges for persistent background tab states. | [`008`](008_real_world_observations_and_caching_architecture.md) |
| **Console QuickEdit** | Clicking inside Windows command prompt pauses `stdout` draining at the OS level. | Disable QuickEdit or decouple human terminal rendering from the core background data pipeline. | [`008`](008_real_world_observations_and_caching_architecture.md) |
| **Terminal Overflow** | Large tab sets (40+ tabs) push hierarchy and element details off-screen. | Implement compact summaries for human monitor; stream full arrays via JSON/MCP. | [`008`](008_real_world_observations_and_caching_architecture.md) |
| **Multi-App Container Bleed** | When focused on an overlay (e.g. record button), `GetParentControl()` climbs to root shell, flattening 42 tabs across background windows (Waterfox + Explorer instances) into one list. | Anchor `top_window` strictly to Win32 `GetForegroundWindow()`; group discovered tabs by `HWND` and parent container. | [`009`](009_live_telemetry_and_tab_diagnostics.md) |

---

## 3. Directory Index & Document Map

### Accessibility MCP & Context Engine (`docs/accessibility_mcp/`)
- [`001_exploration_analysis_planning.md`](001_exploration_analysis_planning.md): Initial problem exploration, UIA vs WinEvents, and performance goals.
- [`002_epistemology_patterns_and_observability.md`](002_epistemology_patterns_and_observability.md): Deep architectural patterns, COM apartments, and RPC error recovery.
- [`003_strategic_analysis_cross_platform_and_context.md`](003_strategic_analysis_cross_platform_and_context.md): Cross-platform comparisons (Windows UIA vs macOS AX vs Linux AT-SPI).
- [`004_deep_research_metaprompt.md`](004_deep_research_metaprompt.md): Metaprompts for investigating enterprise RPA and OS-level trackers.
- [`005_semantic_index_and_app_sdk.md`](005_semantic_index_and_app_sdk.md): Analysis of Windows Recall, Semantic Index, and App SDK context donation.
- [`006_poc_architecture.md`](006_poc_architecture.md): Blueprint for the Python event-driven Proof of Concept.
- [`007_tab_extraction_and_context_representation.md`](007_tab_extraction_and_context_representation.md): Technical mechanics of tab extraction, selection bitmasks, and node highlighting.
- [`008_real_world_observations_and_caching_architecture.md`](008_real_world_observations_and_caching_architecture.md): Live diagnostics, multi-tabstrip findings, QuickEdit stalls, and non-UIA direct process bridges.
- [`009_live_telemetry_and_tab_diagnostics.md`](009_live_telemetry_and_tab_diagnostics.md): Multi-app container bleed diagnostics, latency post-mortem, rolling observability stream, and time-series telemetry architecture.
- [`010_telemetry_benchmarks_and_live_findings.md`](010_telemetry_benchmarks_and_live_findings.md): Empirical telemetry benchmarks, 6,800-node browser traversal costs, and File Explorer dual-tabstrip resolution.

### PyVDA Analysis (`docs/pyvda/`)
- [`001_pyvda_rpc_and_com_lifecycle_analysis.md`](../pyvda/001_pyvda_rpc_and_com_lifecycle_analysis.md): Deep analysis of `pyvda` commit `d2c6f2b`, COM lifecycle, RPC errors, and STA/MTA threading.
- [`002_pyvda_core_architecture_and_threading_critique.md`](../pyvda/002_pyvda_core_architecture_and_threading_critique.md): Core architectural critique of PyVDA threading, apartment boundaries, and stateless design alternatives.

### Caster HUD Primer (`docs/caster_hud/`)
- [`001_caster_hud_architecture_and_threading_primer.md`](../caster_hud/001_caster_hud_architecture_and_threading_primer.md): Educational primer on Caster HUD process isolation, XML-RPC IPC, and Qt `postEvent` architecture.

---

## 4. Current Status & Next Milestones

- `[x]` **Phase 1: Foundations & PoC** — Event-driven Win32 hooks, UIA focus extraction, and Caster voice launcher (`scripts/context_poc.py`).
- `[x]` **Phase 2: Tab Extraction** — Basic tab discovery and active tab marking across browsers and editors.
- `[ ]` **Phase 3: Two-Tier Caching Engine (v3)** — Transition to HWND-level tab caching, Virtual Desktop tracking (`pyvda`), and async worker queue.
- `[ ]` **Phase 4: Direct Process Bridges** — Explore WebExtensions Native Messaging & VS Code extension hooks.
- `[ ]` **Phase 5: MCP Server Bridge** — Expose live state as a Streamable HTTP MCP Resource for local AI agents.
