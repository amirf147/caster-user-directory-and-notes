# Ticket 001: Research NVDA UIA Threading Architecture

**Type**: `wayfinder:research` (AFK)
**Status**: Open / Unclaimed
**Blocks**: Architecture Decision (In-Process vs Out-of-Process)

## Question
How does the NVDA screen reader handle Microsoft UI Automation (UIA) COM threading and lifecycle management in Python?

Specifically:
1. Does NVDA use an MTA thread or an isolated process for UIA interaction?
2. How does NVDA's `UIAHandler` batch or proxy UIA COM calls to avoid blocking the main input thread?
3. What Python libraries (e.g., `comtypes`) or C-extensions does NVDA rely on for UIA?

This research is critical to deciding whether our new UIA Server should be an In-Process Thread or an Out-of-Process Server.
