# Wayfinder Map: Non-Blocking UIA Server Architecture

## Destination
Design and implement a safe, non-blocking UIA integration architecture for user space rules that strictly obeys Microsoft's COM threading constraints, and refactor `caster_user_content/util/app_switcher.py` and `text_editing.py` to use it so the main speech thread never freezes.

## Notes
- **Domain**: Windows UI Automation (UIA), COM Threading (STA vs MTA), Python concurrent architectures, NVDA screen reader codebase.
- **Standing Preferences**: Use local markdown tracking for tickets (`docs/wayfinder/tickets/`).

## Decisions so far

## Not yet specified
- **Architecture**: Will the UIA service run as an In-Process MTA Thread or an Out-of-Process Server? (Waiting on research).
- **IPC Mechanism**: If out-of-process, how does Caster communicate with the UIA Server (e.g., XML-RPC, local sockets, named pipes)?
- **Tab Selection Strategy**: How will we safely execute Tier 1 (UIA Tab Selection) and fallback to Tier 2 (Hotkey Cycling) without deadlocks?
- **UIA Wrapper API**: What will the asynchronous UIA wrapper (replacing `os_controller.run_sync`) look like for `text_editing.py`?

## Out of scope
- Generic `ThreadPoolExecutor` implementations (deprecated, violates COM STA/MTA rules).
