# Ticket 023: Feasibility Analysis - UIA Performance vs Window Focus Failures

**Type**: `wayfinder:research` (Feasibility & Root Cause Analysis)
**Status**: Open / Unclaimed
**Blocks**: Final Architecture Proposal

## Question
While UIA COM deadlocks are a known issue, is the freezing we observe *strictly* a UIA problem, or is it fundamentally a Window Switching/Focus issue exacerbated by speech recognition dynamics?

Specifically:
1. **Focus Failures vs UIA**: Often, window switching (Tier 2/Fallback) fails because a single-syllable alias is misheard. When this happens, the system fails to switch windows but background threads continue running (potentially attaching to the wrong thread). Are these focus-stealing failures the true root cause of the system slowdowns, rather than UIA itself?
2. **Thread Jumbling**: Does the mere presence of a constantly running, background UIA thread (even when not actively queried) jumble up the main thread's performance or memory, contributing to the lag?
3. **The Synchronous Dilemma**: Caster and Dragonfly appear to operate synchronously, where dictation pauses to see the immediate result of an action before speaking the next command. Is this synchronous nature an intentional, strict design requirement? If so, does this fundamental requirement clash with *any* form of UIA or Window Focus manipulation that inherently takes longer than a few milliseconds to resolve? 

## Next Steps
- Analyze the performance impact of failed window-switching events (`SetForegroundWindow` / `AttachThreadInput` failures) versus pure UIA property queries.
- Evaluate if a non-blocking UIA architecture (like MCP) can even solve the problem if the voice engine still inherently requires a synchronous wait for the UI to visually update before processing the next word.
- Document whether the existing Python UIA threads leak memory or CPU cycles simply by existing in the background.
