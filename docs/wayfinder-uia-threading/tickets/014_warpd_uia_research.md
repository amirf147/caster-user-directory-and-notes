[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Tickets ](../../README.md#wayfinder-uia--threading-research) › **Ticket 014: Research warpd UIA Architecture**

---

# Ticket 014: Research warpd UIA Architecture

**Type**: `wayfinder:research` (AFK)
**Status**: [CLOSED]
**Blocks**: Architecture Placement Decision

## Question
How does `warpd` handle UIA threading, window focus, and COM lifecycle in Windows?

Specifically:
1. Does `warpd` use UIA or COM for element navigation?
2. How does it structure its dual-thread architecture for keyboard hooks and rendering?
3. How does it display overlays without stealing focus from active applications?

## Resolution
1. **Complete Bypass**: Completely circumvents UIA and COM interfaces in favor of a purely geometric spatial grid.
2. **Dual-Thread Architecture**: Uses an Input Thread with low-level keyboard hooks (`WH_KEYBOARD_LL`) communicating via Win32 messages (`WM_USER`) with a separate UI Rendering Thread.
3. **Non-Invasive Focus**: Creates transparent, click-through overlay windows using extended styles (`WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_TOPMOST`), sending input via `SendInput` without stealing window activation.

**Full Educational Breakdown**: [014_warpd_uia_educational_breakdown.md](../research/014_warpd_uia_educational_breakdown.md)
