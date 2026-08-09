# Wayfinder Map: Out-of-Process Window Management & UIA Architecture

## Quick Executive Summaries & Session Takeaways

- **[Claude Critique: Verified Takeaways & Fact-Checked Corpus](claude-critique-verified-takeaways.md)**: Fact-checked distillation by Claude 5 Sonnet max evaluating load-bearing technical claims, verified facts vs unconfirmed hypotheses, and what can be discarded from the 71-file Wayfinder corpus.
- **[Codex Context Extract: Operational Baseline](codex-context-extract.md)**: Structured context synthesis by Codex outlining core requirements, operational facts, and reference benchmarks.
- **[Testing Suggestions & Layered Test Strategy](tickets/testing-suggestions.md)**: Layered testing strategy covering pure string logic, disposable Tkinter test targets, and Dragonfly text engine harness for app switcher validation.

## Current Status & Architectural Evolution

### Where We Started
We initially investigated responsiveness issues during window switching and app management. Our working hypothesis assumed that window operations had to be made entirely non-blocking (asynchronous) to prevent freezing Dragonfly's main speech loop. We assumed that synchronous blocking was the primary issue to solve.

### How Our Understanding Evolved
Through deep-dive research into COM threading (STA vs MTA) and empirical server benchmarking, our understanding fundamentally evolved:

1. **Synchronous Blocking is Desirable for Window Operations**: We realized that blocking execution during a window switch or app navigation command is actually acceptable and desirable from a command synchronization perspective. When a user issues a voice command to switch applications, blocking synchronously until the window is fully focused ensures that subsequent voice commands are not executed against an out-of-date or in-flight window state.
2. **The Assumed Issue: In-Process COM Apartment Deadlocks**: Our initial hypothesis was that executing Python COM wrappers (`pywinauto`, `comtypes`) *in-process* on Dragonfly's main engine thread without a dedicated Win32 message pump was causing engine instability. In-process COM calls in Python are theoretically prone to deadlocks or hangs when Windows sessions lock, minimize, or switch window stations.
3. **The QuickEdit Revelation (No Evidence of Deadlocks)**: During empirical testing, we initially attributed all observed "hard freezes" to these theoretical COM deadlocks. However, we discovered a critical nuance: interacting with the Caster PowerShell terminal enables Windows "QuickEdit" mode, which completely pauses the `stdout` stream. Because the app switcher logs heavily, the Python thread instantly froze when attempting to `print()`. **Crucially, we currently have zero empirical evidence that true COM deadlocks are actually occurring.** The QuickEdit console lockup is the proven cause of all "freezes" observed thus far.
4. **The Out-of-Process Isolation Pattern (Experimental Exploration)**: Rather than a definitive or proven solution, exploring out-of-process execution via an MCP server is primarily an **experimental investigation**. It is driven by the author's desire to gain hands-on experience authoring custom C# MCP tools, alongside speculative ideas that standardized tool interfaces could be useful for future AI agent interactions. Given that root-cause problem definitions and exact requirements remain foggy, this architecture is being approached as an exploratory learning endeavor rather than a guaranteed fix.

### Where We Are Going
Following the retrospective in [Ticket 033: Re-Evaluate UIA Architecture Trajectory (Voice vs. LLM)](tickets/033_re_evaluate_mcp_trajectory_research.md), we have pivoted away from adopting generic, third-party "computer use" MCP servers. Instead, we are entering an exploratory design phase for a experimental bespoke C# `.NET` **"Micro MCP Server"** utilizing `FlaUI.UIA3`. This prototype aims to explore exposing a small set (3-5) of macro-level tools (window focusing with embedded Win32 thread attachment fail-safes, tab querying, element clicking) via the Anthropic MCP JSON-RPC protocol to evaluate low-latency execution for Caster rules while experimenting with LLM agent compatibility.

---

## Destination
Design and implement a robust out-of-process window management and app switching architecture for Caster user-space rules (offloading functionality currently in `caster_user_content/util/app_switcher.py` into an external server), isolating COM apartment rules and maintaining speech engine stability.

## Notes
- **Domain**: Windows UI Automation (UIA), Win32 API Window Management, COM Threading (STA vs MTA), Python concurrent architectures, Model Context Protocol (MCP).
- **Standing Preferences**: Use local markdown tracking for tickets (`docs/wayfinder-uia-threading/tickets/`).
- **Fail-Safe Hierarchy**: The exact fail-safe tiers are actively being explored. The current working theory relies on: UIA Patterns $\rightarrow$ Win32 `AttachThreadInput` + `Alt` Key Injection (Most Reliable) $\rightarrow$ Command-Line Execution (e.g., `Process.Start`) $\rightarrow$ Taskbar Macros (`Win+T`) for UIPI-blocked windows.

## Decisions & Research Findings so far
- [Ticket 001: Research NVDA UIA Threading Architecture](tickets/001_nvda_uia_threading_research.md) ([Breakdown](research/001_nvda_uia_threading_educational_breakdown.md)) — NVDA uses a dedicated In-Process MTA Thread communicating via Queue, with C++ extensions for event rate-limiting.
- [Ticket 002: Research Terminator UIA Architecture](tickets/002_terminator_uia_research.md) ([Breakdown](research/002_terminator_uia_threading_educational_breakdown.md)) — Terminator uses a dedicated thread but forces STA with a message pump to maintain responsiveness when mixing UIA with active window focus injection.
- [Ticket 003: Research UIA Fallback Strategies in NVDA and Terminator](tickets/003_uia_fallback_strategies.md) ([Breakdown](research/003_uia_fallback_strategies_educational_breakdown.md)) — NVDA cascades through older APIs (IAccessible2, MSAA), while Terminator falls back to raw Win32 APIs for robust window manipulation.
- [Ticket 004: Research UFO UIA Architecture and Fallback Strategies](tickets/004_ufo_uia_research.md) ([Breakdown](research/004_ufo_uia_architecture_educational_breakdown.md)) — UFO uses `pywinauto` natively but introduces an ultimate fallback of AI Vision (OmniParser) and OCR to literally "look" at the screen when UIA fails.
- [Ticket 005: Research Dragonfly UIA and Threading Architecture](tickets/005_dragonfly_uia_research.md) ([Breakdown](research/005_dragonfly_uia_and_threading_educational_breakdown.md)) — Dragonfly uses an STA daemon thread but lacks a message pump, making it susceptible to COM deadlocks. It uses a ctrl-key injection hack for reliable window focus.
- [Ticket 006: Research Caster User Directory's Current UIA Usage](tickets/006_caster_uia_research.md) ([Breakdown](research/006_caster_uia_usage_educational_breakdown.md)) — Evaluates the Caster User Directory's synchronous pywinauto calls on the main voice thread, highlighting the need to offload UI operations.
- [Ticket 008: Research Caster Source Core UIA/Threading Usage](tickets/008_caster_core_uia_research.md) ([Breakdown](research/008_caster_core_uia_usage_educational_breakdown.md)) — Caster Core contains zero UIA handling or COM threading logic. UI traversal lives exclusively in the user-space directory.
- [Ticket 009: Research Caster Core Asynch Threading & UI Overlays](tickets/009_caster_core_asynch_research.md) ([Breakdown](research/009_caster_core_asynch_threading_breakdown.md)) — Explains Homunculus and Grids as isolated GUI subprocesses using XML-RPC on daemon threads.
- [Ticket 010: Research hunt-and-peck UIA Architecture](tickets/010_hunt_and_peck_uia_research.md) ([Breakdown](research/010_hunt_and_peck_uia_educational_breakdown.md)) — Uses COM Interop via STA thread with a WinForms message pump and `AttachThreadInput` for window focus.
- [Ticket 011: Research neru UIA Architecture](tickets/011_neru_uia_research.md) ([Breakdown](research/011_neru_uia_educational_breakdown.md)) — Uses MTA threading to avoid message pump deadlocks and raw COM vtable syscalls in Go.
- [Ticket 012: Research Python-UIAutomation-for-Windows UIA Architecture](tickets/012_python_uia_for_windows_research.md) ([Breakdown](research/012_python_uia_for_windows_educational_breakdown.md)) — Uses `comtypes` singleton with explicit `CoInitializeEx()` and Win32/UIA hybrid window focus.
- [Ticket 013: Research UIAutomationClient UIA Architecture](tickets/013_uiautomationclient_uia_research.md) ([Breakdown](research/013_uiautomationclient_uia_educational_breakdown.md)) — C++ auxiliary DLL wrapping GDI+ for screen captures and DPI scaling.
- [Ticket 014: Research warpd UIA Architecture](tickets/014_warpd_uia_research.md) ([Breakdown](research/014_warpd_uia_educational_breakdown.md)) — Bypasses UIA entirely, relying on low-level keyboard hooks (`WH_KEYBOARD_LL`) and `SendInput`.
- [Ticket 015: Research OS Accessibility APIs (Issue #814)](tickets/015_os_accessibility_apis_issue_814_research.md) ([Breakdown](research/015_os_accessibility_apis_issue_814_educational_breakdown.md)) — Discusses historical goals for Select-and-Say via UIA/MSAA.
- [Ticket 016: Research dtactions UIA Architecture](tickets/016_dtactions_uia_research.md) ([Breakdown](research/016_dtactions_uia_usage_educational_breakdown.md)) — Relies on synchronous Win32 syscalls (`win32gui`, `SendInput`) and AutoHotkey.
- [Ticket 017: Research UIAutomation MCP Server](tickets/017_uiautomation_mcp_research.md) ([Breakdown](research/017_uiautomation_mcp_educational_breakdown.md)) — Evaluates shifting UIA execution out-of-process via an MCP server architecture.
- [Ticket 018: Research UIAutomation Microsoft Documentation](tickets/018_uia_microsoft_documentation_research.md) ([Breakdown](research/018_uia_microsoft_documentation_educational_breakdown.md)) — Summarizes Microsoft's official guidance on COM apartment threading constraints and CacheRequests.
- [Ticket 019: Evaluate uiautomation-mcp Implementation Against Microsoft Standards](tickets/019_uiautomation_mcp_evaluation_research.md) ([Breakdown](research/019_uiautomation_mcp_evaluation_educational_breakdown.md)) — Evaluates COM threading isolation in MTA subprocesses.
- [Ticket 023: Feasibility Analysis — UIA vs Focus Steering](tickets/023_feasibility_analysis_uia_vs_focus_research.md) ([Breakdown](research/023_feasibility_analysis_uia_vs_focus_research_deep_dive.md)) — Analyzed UIA pattern invocation vs OS window focus steering policies (`SetForegroundWindow`).
- [Ticket 025: Dragonfly Process and Thread Management Deep Dive](tickets/025_dragonfly_process_thread_management_research.md) ([Breakdown](research/025_dragonfly_process_and_thread_management_deep_dive.md)) — Confirmed Dragonfly single-threaded engine loop constraints and STA/MTA threading boundaries.
- [Ticket 026: Caster Process and Thread Management Deep Dive](tickets/026_caster_process_thread_management_research.md) ([Breakdown](research/026_caster_process_thread_management_deep_dive.md)) — Analyzed thread execution in Caster user-space rules and process boundaries.
- [Ticket 027: Research Windows-MCP Repository](tickets/027_windows_mcp_research.md) ([Breakdown](research/027_windows_mcp_deep_dive.md)) — Evaluated the Python `Windows-MCP` server prototype.
- [Ticket 028: Windows-MCP Integration Test & Threading Critique](tickets/028_windows_mcp_integration_test_research.md) ([Breakdown](research/028_windows_mcp_integration_test_deep_dive.md)) — Critiqued Python `Windows-MCP` COM thread behavior and latency.
- [Ticket 029: Execute Windows-MCP Integration Test](tickets/029_execute_windows_mcp_integration_test.md) — Executed standalone benchmark test for Python `Windows-MCP`.
- [Ticket 030: Windows-MCP Integration Test Findings](tickets/030_windows_mcp_integration_test_findings.md) ([Breakdown](research/030_windows_mcp_integration_test_findings_deep_dive.md)) — Documented empirical performance metrics from Python `Windows-MCP` testing.
- [Ticket 031: Research Desktop Pilot MCP Repository](tickets/031_desktop_pilot_mcp_research.md) ([Breakdown](research/031_desktop_pilot_mcp_deep_dive.md)) — Evaluated C# `.NET` `desktop-pilot-mcp` (`winapp-mcp`) server, FlaUI UIA3 caching, and multi-step window restoration patterns.
- [Ticket 032: Execute Desktop Pilot MCP Integration Test](tickets/032_execute_desktop_pilot_mcp_integration_test.md) ([Breakdown](research/032_execute_desktop_pilot_mcp_integration_test_deep_dive.md)) — Benchmarked C# `winapp-mcp` server startup/tool latency, process teardown, and verified window focus / tab cycling via Python test script & Dragonfly rule.
- [Ticket 033: Re-Evaluate UIA Architecture Trajectory (Voice vs. LLM)](tickets/033_re_evaluate_mcp_trajectory_research.md) ([Breakdown](research/033_re_evaluate_mcp_trajectory_deep_dive.md)) — Pivoted from bloated third-party LLM agent servers to a bespoke C# Micro MCP Server architecture.
- [Ticket 035: WinStasis Architecture Review and Refactoring Strategy](tickets/035_winstasis_architecture_review.md) ([Breakdown](research/035_winstasis_architecture_review_research.md)) — Analyzed WinStasis to extract hybrid window matching, boundary clamping, and modular data structures.
- [Ticket 036: App Switcher MCP Investigation & Tool Design](tickets/036_app_switcher_mcp_investigation.md) ([Breakdown](research/036_app_switcher_mcp_investigation_research.md)) — Designed stateless C# `WindowContext` schemas and atomic MCP tools for the app switcher MVP.
- [Ticket 037: Research FlaUI.UIA3 Implementation Patterns & Best Practices](tickets/037_flaui_implementation_patterns.md) ([Breakdown](research/037_flaui_implementation_patterns_research.md)) — Documented FlaUI COM lifecycle, MTA threading, `CacheRequest` usage, and UIPI Taskbar macro fail-safes.
- [Ticket 038: Empirical Investigation & Data Gathering for App Switcher Failures, Hangs, and Recovery](tickets/038_app_switcher_empirical_hang_investigation.md) ([Breakdown](research/038_app_switcher_empirical_hang_investigation_research.md)) — Real-world stress testing. **Key Finding:** Many assumed "COM deadlocks" were actually stdout freezes caused by Windows PowerShell QuickEdit mode pausing the Python process.
- [Testing Suggestions & Layered Test Strategy](tickets/testing-suggestions.md) — Layered test architecture distinguishing direct function calls from speech grammar dispatching, introducing disposable Tkinter test fixtures and Dragonfly text engine testing.

## Frontier (Open Tickets)
- [Ticket 007: Architecture Placement Analysis (Dragonfly vs Caster)](tickets/007_architecture_placement_analysis.md)
- [Ticket 020: Research MCP Server Internals vs. XML-RPC](tickets/020_mcp_vs_xmlrpc_research.md)
- [Ticket 021: Design the MCP Server Interface (Tools vs Fallbacks)](tickets/021_mcp_interface_and_tool_design_research.md)
- [Ticket 022: Evaluate Fixing Dragonfly's UIA vs Adopting External MCP Architecture](tickets/022_dragonfly_uia_vs_mcp_research.md)
- [Ticket 024: Research Summary and Maintainer Q&A Proposal](tickets/024_maintainer_proposal_and_summary_research.md)
- [Ticket 034: Determine Implementation Path for Micro Accessibility MCP Server](tickets/034_determine_mcp_implementation_path_research.md)
- [Ticket 038: Empirical Investigation & Data Gathering for App Switcher Failures, Hangs, and Recovery](tickets/038_app_switcher_empirical_hang_investigation.md)

## Next Steps & Research Roadmap
1. **Server Architecture Evaluation**: Compare prototype architectures (Python `Windows-MCP` vs C# `desktop-pilot-mcp`) to decide whether to fork, extend, or build a tailored out-of-process window management server.
2. **IPC Integration & Client Library**: Design a lean Python IPC client to communicate with the chosen server background process.
3. **App Switcher Offloading**: Prototype refactoring `caster_user_content/util/app_switcher.py` to route window switching operations to the external server interface.

## Out of Scope
- In-process `ThreadPoolExecutor` UIA implementations (deprecated, violates COM STA/MTA rules).
- **Vision-based UI Automation (OCR, Screen Parsing, OmniParser)**: While powerful for LLM agents, capturing, serializing, and processing visual data is too slow and high-latency for real-time, snappy voice command interaction. We rely strictly on deterministic, underlying OS APIs (Win32, UIA3).
