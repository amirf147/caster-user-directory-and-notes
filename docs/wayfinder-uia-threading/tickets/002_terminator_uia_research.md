# Ticket 002: Research Terminator UIA Architecture

**Type**: `wayfinder:research` (AFK)
**Status**: [CLOSED]
**Blocks**: Architecture Decision (In-Process vs Out-of-Process)

## Question
How does the `terminator` repository handle UIA interactions and threading for its desktop automation agents? 

Specifically:
1. Does it use a dedicated thread, process, or a generic thread pool for UIA?
2. What libraries does it use for UIA (e.g., `uiautomation`, `pywinauto`, `comtypes`)?
3. Are there architectural patterns in its MCP tools or agent integration that we can learn from or adopt for Caster's UIA Server?

## Resolution
1. **Dedicated Thread:** Terminator uses a dedicated OS thread for UIA events. It explicitly avoids random thread pools for COM stability.
2. **Threading Model (STA vs MTA):** Interestingly, Terminator defaults to **STA (Single-Threaded Apartment)** on its background thread (running a custom message pump) because it claims it provides better system responsiveness when mixing UIA with aggressive window focus and input injection.
3. **Libraries:** It is written in Rust, utilizing `windows-rs` and `uiautomation-rs`. It bypasses the library's default MTA initialization to force STA.
4. **Pattern to Adopt:** We must definitively use an isolated thread/server for UIA. Furthermore, because Caster injects input (like Terminator) rather than just reading (like NVDA), we must carefully consider if our UIA server needs an STA message pump to handle `win32gui` focus APIs alongside UIA.

**Full Educational Breakdown**: [002_terminator_uia_threading_educational_breakdown.md](../research/002_terminator_uia_threading_educational_breakdown.md)
