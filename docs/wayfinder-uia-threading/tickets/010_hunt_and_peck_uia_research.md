# Ticket 010: Research hunt-and-peck UIA Architecture

**Type**: `wayfinder:research` (AFK)
**Status**: [CLOSED]
**Blocks**: Architecture Placement Decision

## Question
How does `hunt-and-peck` handle UIA threading, window focus, and COM lifecycle in Windows?

Specifically:
1. What library/API does it use to interact with UIA?
2. Does it use STA or MTA threading, and how does it prevent deadlocks?
3. How does it handle focus stealing when rendering its hint overlays?

## Resolution
1. **API**: Uses native COM-based `UIAutomationClient` (`CUIAutomation`) via COM Interop rather than managed `System.Windows.Automation`.
2. **COM Threading**: Runs on an STA thread with a WinForms message pump handling `WM_HOTKEY` events. Uses `FindAll(TreeScope_Descendants)` to fetch actionable elements synchronously.
3. **Focus Management**: Circumvents Windows anti-focus-stealing protections using `AttachThreadInput` to temporarily link input threads before calling `BringWindowToTop()` and `SetFocus()`.

**Full Educational Breakdown**: [010_hunt_and_peck_uia_educational_breakdown.md](../research/010_hunt_and_peck_uia_educational_breakdown.md)
