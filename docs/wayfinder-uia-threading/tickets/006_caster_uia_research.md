# Ticket 006: Research Caster User Directory's Current UIA Usage

**Type**: `wayfinder:research` (AFK)
**Status**: [CLOSED]
**Blocks**: Architecture Placement Decision

## Question
Does the `caster_user_content` (Caster User Directory) currently use any UIA or related accessibility APIs?

Specifically:
1. What existing UIA implementations or accessibility wrappers exist within the Caster User Directory?
2. Are they currently causing any threading issues or deadlocks?
3. How do they compare to the needs of the `app_switcher` and `text_editing` refactor?

## Resolution
1. **Existing UIA Usage**: The Caster User Directory heavily utilizes `pywinauto` (which wraps UIA) primarily in `app_switcher.py` to inspect and focus windows.
2. **Threading Issues (Deadlocks)**: Yes, this causes severe deadlocks. User-space rules execute `pywinauto` calls **synchronously on the main voice engine thread**. Because this thread is an STA without a dedicated message pump, calling UIA on unresponsive target applications freezes the entire Caster engine. 
3. **Comparison to Refactor Needs**: The current synchronous design is fundamentally unsafe for the new UIA Tab Switching logic. Tab switching requires reading complex UI trees. To do this safely without hanging the voice engine, all UIA calls must be moved off the main thread into an MTA thread or Out-of-Process Server. The Caster User Directory does utilize similar Win32 focus hacks (`AttachThreadInput`, Alt key injection) as Dragonfly and Terminator to bypass OS focus restrictions.

**Full Educational Breakdown**: [006_caster_uia_usage_educational_breakdown.md](../research/006_caster_uia_usage_educational_breakdown.md)
