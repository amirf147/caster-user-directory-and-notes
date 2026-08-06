# Wayfinder Map: Non-Blocking UIA Server Architecture

## Destination
Design and implement a safe, non-blocking UIA integration architecture for user space rules that strictly obeys Microsoft's COM threading constraints, and refactor `caster_user_content/util/app_switcher.py` and `text_editing.py` to use it so the main speech thread never freezes.

## Notes
- **Domain**: Windows UI Automation (UIA), COM Threading (STA vs MTA), Python concurrent architectures, NVDA screen reader codebase.
- **Standing Preferences**: Use local markdown tracking for tickets (`docs/wayfinder-uia-threading/tickets/`).

## Decisions so far
- [Ticket 001: Research NVDA UIA Threading Architecture](tickets/001_nvda_uia_threading_research.md) ([Breakdown](research/001_nvda_uia_threading_educational_breakdown.md)) — NVDA uses a dedicated In-Process MTA Thread communicating via Queue, with C++ extensions for event rate-limiting.
- [Ticket 002: Research Terminator UIA Architecture](tickets/002_terminator_uia_research.md) ([Breakdown](research/002_terminator_uia_threading_educational_breakdown.md)) — Terminator uses a dedicated thread but forces STA with a message pump to maintain responsiveness when mixing UIA with active window focus injection.
- [Ticket 003: Research UIA Fallback Strategies in NVDA and Terminator](tickets/003_uia_fallback_strategies.md) ([Breakdown](research/003_uia_fallback_strategies_educational_breakdown.md)) — NVDA cascades through older APIs (IAccessible2, MSAA), while Terminator falls back to raw Win32 APIs for robust window manipulation.
- [Ticket 004: Research UFO UIA Architecture and Fallback Strategies](tickets/004_ufo_uia_research.md) ([Breakdown](research/004_ufo_uia_architecture_educational_breakdown.md)) — UFO uses `pywinauto` natively but introduces an ultimate fallback of AI Vision (OmniParser) and OCR to literally "look" at the screen when UIA fails.
- [Ticket 005: Research Dragonfly UIA and Threading Architecture](tickets/005_dragonfly_uia_research.md) ([Breakdown](research/005_dragonfly_uia_and_threading_educational_breakdown.md)) — Dragonfly uses an STA daemon thread but lacks a message pump, making it highly susceptible to COM deadlocks. It uses a ctrl-key injection hack for reliable window focus.
- [Ticket 006: Research Caster's Current UIA Usage](tickets/006_caster_uia_research.md) ([Breakdown](research/006_caster_uia_usage_educational_breakdown.md)) — Caster runs pywinauto synchronously on the main voice thread, which causes severe deadlocks. All new UIA features must be moved off the main thread.
- [Ticket 008: Research Caster Source Core UIA/Threading Usage](tickets/008_caster_core_uia_research.md) ([Breakdown](research/008_caster_core_uia_usage_educational_breakdown.md)) — Caster Core contains absolutely zero UIA handling, COM threading (MTA/STA), or advanced focus stealing. All current UI traversal lives exclusively in the user-space directory.
- [Ticket 009: Research Caster Core Asynch Threading & UI Overlays](tickets/009_caster_core_asynch_research.md) ([Breakdown](research/009_caster_core_asynch_threading_breakdown.md)) — Explains Homunculus and Grids. They are isolated GUI subprocesses using XML-RPC on daemon threads. They fail silently in modern setups due to environment launcher mismatches (`pythonw.exe` vs `py -3.10`) and port zombie locks.
- [Ticket 010: Research hunt-and-peck UIA Architecture](tickets/010_hunt_and_peck_uia_research.md) ([Breakdown](research/010_hunt_and_peck_uia_educational_breakdown.md)) — Uses COM Interop via STA thread with a WinForms message pump, and an `AttachThreadInput` hack to bypass OS focus-stealing protections.
- [Ticket 011: Research neru UIA Architecture](tickets/011_neru_uia_research.md) ([Breakdown](research/011_neru_uia_educational_breakdown.md)) — Uses MTA threading to avoid message pump deadlocks, raw COM vtable syscalls (no CGO), and aggressively copies UIA properties to offline Go structs to eliminate COM pointer memory leaks.
- [Ticket 012: Research Python-UIAutomation-for-Windows UIA Architecture](tickets/012_python_uia_for_windows_research.md) ([Breakdown](research/012_python_uia_for_windows_educational_breakdown.md)) — Uses `comtypes` singleton with explicit `CoInitializeEx()` and issues strict STA cross-thread sharing warnings. Uses a Win32/UIA hybrid approach for window focus.
- [Ticket 013: Research UIAutomationClient UIA Architecture](tickets/013_uiautomationclient_uia_research.md) ([Breakdown](research/013_uiautomationclient_uia_educational_breakdown.md)) — Bypasses actual UIA logic; is simply a C++ auxiliary DLL wrapping GDI+ for screen captures and DPI scaling to support a Python parent library.
- [Ticket 014: Research warpd UIA Architecture](tickets/014_warpd_uia_research.md) ([Breakdown](research/014_warpd_uia_educational_breakdown.md)) — Completely bypasses UIA and COM threading, relying entirely on low-level keyboard hooks (`WH_KEYBOARD_LL`) and simulated geometric mouse clicks via `SendInput`.
- [Ticket 015: Research OS Accessibility APIs (Issue #814)](tickets/015_os_accessibility_apis_issue_814_research.md) ([Breakdown](research/015_os_accessibility_apis_issue_814_educational_breakdown.md)) — Discusses the historical goal of implementing Select-and-Say via UIA/MSAA and plans to migrate OS actions to the `dtactions` library, though lacking discussion on COM threading deadlocks.
- [Ticket 016: Research dtactions UIA Architecture](tickets/016_dtactions_uia_research.md) ([Breakdown](research/016_dtactions_uia_usage_educational_breakdown.md)) — Despite historical plans, `dtactions` contains zero UIA implementation, relying entirely on synchronous Win32 syscalls (`win32gui`, `SendInput`) and AutoHotkey. It lacks any COM threading logic.
- [Ticket 017: Research UIAutomation MCP Server](tickets/017_uiautomation_mcp_research.md) ([Breakdown](research/017_uiautomation_mcp_educational_breakdown.md)) — Investigates shifting the UIA paradigm entirely out of Python. By using an external .NET MCP server with isolated subprocesses, Caster avoids Python COM deadlocks entirely and becomes instantly AI-agent ready.
- [Ticket 018: Research UIAutomation Microsoft Documentation](tickets/018_uia_microsoft_documentation_research.md) ([Breakdown](research/018_uia_microsoft_documentation_educational_breakdown.md)) — Summarizes Microsoft's official guidance on COM apartment threading constraints, CacheRequests, and proper Navigation vs Pattern implementation for UIAutomation.
- [Ticket 019: Evaluate uiautomation-mcp Implementation Against Microsoft Standards](tickets/019_uiautomation_mcp_evaluation_research.md) ([Breakdown](research/019_uiautomation_mcp_evaluation_educational_breakdown.md)) — Evaluates the `uiautomation-mcp` repo. Finds that it securely isolates COM threading in MTA subprocesses but misses a performance optimization by defaulting all CacheRequests to `AutomationElementMode.Full`.

## Frontier (Open Tickets)
- [Ticket 007: Architecture Placement Analysis (Dragonfly vs Caster)](tickets/007_architecture_placement_analysis.md)
- [Ticket 020: Research MCP Server Internals vs. XML-RPC](tickets/020_mcp_vs_xmlrpc_research.md)
- [Ticket 021: Design the MCP Server Interface (Tools vs Fallbacks)](tickets/021_mcp_interface_and_tool_design_research.md)
- [Ticket 022: Evaluate Fixing Dragonfly's UIA vs Adopting External MCP Architecture](tickets/022_dragonfly_uia_vs_mcp_research.md)
- [Ticket 023: Feasibility Analysis - UIA Performance vs Window Focus Failures](tickets/023_feasibility_analysis_uia_vs_focus_research.md)
- [Ticket 024: Research Summary and Maintainer Q&A Proposal](tickets/024_maintainer_proposal_and_summary_research.md)

## Not yet specified
- **Architecture Placement**: Should the UIA Server be built in Dragonfly or Caster?
- **IPC Mechanism**: If out-of-process, how does Caster communicate with the UIA Server (e.g., XML-RPC, local sockets, named pipes)?
- **Tab Selection Strategy**: How will we safely execute Tier 1 (UIA Tab Selection) and fallback to Tier 2 (Hotkey Cycling) without deadlocks?
- **UIA Wrapper API**: What will the asynchronous UIA wrapper (replacing `os_controller.run_sync`) look like for `text_editing.py`?

## Out of scope
- Generic `ThreadPoolExecutor` implementations (deprecated, violates COM STA/MTA rules).
