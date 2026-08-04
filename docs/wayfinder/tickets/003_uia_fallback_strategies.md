# Ticket 003: Research UIA Fallback Strategies in NVDA and Terminator

**Type**: `wayfinder:research` (AFK)
**Status**: [CLOSED]
**Blocks**: Tab Selection Strategy, UIA Wrapper API

## Question
How do both NVDA and Terminator handle desktop applications that do not support or properly expose their UI via Microsoft UI Automation (UIA)?

Specifically:
1. What fallback mechanisms (e.g., MSAA / IAccessible, Win32 APIs, Hotkey Injection, OCR, Image Recognition) do these professional tools rely on when UIA fails?
2. How do they detect that UIA is unavailable or unresponsive for a given window?
3. How can we incorporate these fallback patterns into Caster's `app_switcher.py` (for tab selection) and `text_editing.py`?

## Resolution
1. **NVDA** uses an API cascade (`findBestAPIClass`), falling back from UIA to IAccessible2, Java Access Bridge, and MSAA. 
2. **Terminator** relies on raw Win32 APIs (`SetForegroundWindow`, `BringWindowToTop`) to guarantee window focus when UIA focusing fails or causes deadlocks. 
3. **Caster Strategy**: For Caster, falling back to legacy accessibility APIs (like MSAA) is too complex. We should adopt Terminator's pattern: use UIA purely for *reading* the tab structure, but use robust Win32 APIs for *focusing* the window. If UIA cannot read the tabs, we must fallback to Tier 2 (Hotkey Injection).

**Full Educational Breakdown**: [UIA_Fallback_Strategies_Educational_Breakdown.md](../../UIA_Fallback_Strategies_Educational_Breakdown.md)
