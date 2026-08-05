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

## Frontier (Open Tickets)
- [Ticket 007: Architecture Placement Analysis (Dragonfly vs Caster)](tickets/007_architecture_placement_analysis.md)

## Not yet specified
- **Architecture Placement**: Should the UIA Server be built in Dragonfly or Caster?
- **IPC Mechanism**: If out-of-process, how does Caster communicate with the UIA Server (e.g., XML-RPC, local sockets, named pipes)?
- **Tab Selection Strategy**: How will we safely execute Tier 1 (UIA Tab Selection) and fallback to Tier 2 (Hotkey Cycling) without deadlocks?
- **UIA Wrapper API**: What will the asynchronous UIA wrapper (replacing `os_controller.run_sync`) look like for `text_editing.py`?

## Out of scope
- Generic `ThreadPoolExecutor` implementations (deprecated, violates COM STA/MTA rules).
