# Ticket 023: Context Gathering - Window Focus, Reliability, and Accessibility Architecture

**Type**: `wayfinder:research` (Context Gathering & Requirements)
**Status**: Open / Unclaimed
**Blocks**: Final Architecture Proposal

## Question
Before we propose any specific architecture (like a unified server vs independent tools), we must ensure we are asking the right questions and gathering the correct context about how our system currently behaves and fails, particularly regarding window focus and UIA. 

Specifically, we need to gather context on:

1. **Acceptable Blocking and Robust Failures**: When we switch windows, it is acceptable to block the voice engine briefly (since we don't want to execute dictation in the wrong window anyway). However, it should not freeze for a *long* time. How can we ensure thread safety and implement a robust failure mechanism so it never permanently hangs and doesn't interfere with other processes?
2. **Reliability of Focus Switching**: Switching applications shouldn't be hard. It should succeed every single time, failing only for obvious reasons (e.g., an undefined alias or a non-existent page). Why does it currently fail, and how can we guarantee reliability?
3. **Architectural Scope of Accessibility**: App switching relies on UIA. Text editing relies on UIA. Button pressing relies on UIA. But sometimes UIA isn't enough, and fallbacks (like MSAA or Win32) are required. Given this broad scope, should our future architecture be a single "UIA Server", or a broader "Accessibility Server" with distinct components? 

## Next Steps
- **Gather Context on Focus Mechanisms**: Investigate exactly how window switching is currently implemented and why it lacks a robust timeout/failure mechanism, leading to long freezes.
- **Analyze Thread Safety**: Document the current thread safety (or lack thereof) during window switching and UIA queries to understand how it interferes with other processes.
- **Map Accessibility Requirements**: Map out all features that require accessibility APIs (text editing, app switching, button pressing) and their necessary fallbacks to determine the required scope of any future architectural proposal.
- *Note: Do not propose a final architecture yet. The goal here is strictly to gather context and ask the right questions to inform the design.*
