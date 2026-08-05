# Ticket 008: Research Caster Source Core UIA/Threading Usage

**Type**: `wayfinder:research` (AFK)
**Status**: [CLOSED]
**Blocks**: Architecture Placement Decision

## Question
Does the `Caster` core source repository implement any low-level UIA, threading management, or advanced focus handling that differs from what we found in the Caster User Directory?

Specifically:
1. Are there any dedicated background threads or COM apartment initializations (MTA/STA) hidden in the core engine?
2. Does the core provide any UIA wrappers we should be aware of?
3. How does the core handle window focusing (e.g., via `win32gui`) compared to the user directory's OS bypass methods?

## Resolution
1. **Threading & COM**: The core engine uses Python `threading` heavily for asynchronous UI overlays (Grids, Homunculus), but does NOT initialize any COM apartments (MTA/STA) or maintain a dedicated accessibility thread.
2. **UIA Wrappers**: There are absolutely zero UIA wrappers or accessibility libraries (`pywinauto`, `comtypes`, etc.) in the core Caster engine. All UIA logic resides in user-space scripts (like `app_switcher.py`).
3. **Focus Handling**: The core engine is surprisingly barren of advanced focus stealing mechanics. It does not replicate the complex OS bypasses (like `AttachThreadInput` or Alt-key injection) found in the user directory.

**Full Educational Breakdown**: [008_caster_core_uia_usage_educational_breakdown.md](../research/008_caster_core_uia_usage_educational_breakdown.md)
