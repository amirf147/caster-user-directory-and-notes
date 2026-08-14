[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Tickets ](../../README.md#wayfinder-uia--threading-research) › **Ticket 037: Research FlaUI.UIA3 Implementation ...**

---

# Ticket 037: Research FlaUI.UIA3 Implementation Patterns & Best Practices

**Type:** `wayfinder:research` (Prototyping & Investigation)
**Status:** Open / Unclaimed
**Depends on:** Ticket 036
**Blocks:** C# Micro MCP Server Scaffolding (Ticket 033)

## Objective

Before scaffolding the core C# MCP server, we must definitively map out how to safely and performantly use the FlaUI.UIA3 library. The agent needs to define the exact C# implementation patterns for COM threading, tree traversal, caching, and fallback focusing. This ensures we do not introduce UIA performance bottlenecks (leaky COM proxies) into the new modular architecture.

## Directives for the Agent (Areas to Investigate)

1. **The COM Lifecycle:**
   Document the exact C# boilerplate required to initialize `UIA3Automation` safely. How do we ensure the C# console application runs strictly in a Multi-Threaded Apartment (MTA) to prevent message-pump deadlocks?

2. **Win32 to FlaUI Handoff:**
   How do we take a raw Win32 HWND (discovered via `EnumWindows`) and instantly convert it into a FlaUI `AutomationElement` (e.g., `automation.FromHandle(hwnd)`)?

3. **Deep Traversal & Caching (The Scalpel):**
   Traversing UI trees synchronously is slow. Investigate how FlaUI implements `CacheRequest` (or `AutomationElementMode.None`). How do we fetch the Name, AutomationId, and ControlType of 50 browser tabs in a single cross-process call without freezing?

4. **Action Patterns & The Illusion of Reliability:**
   Document how to trigger actions on found elements (e.g., `InvokePattern.Invoke()`, `element.Focus()`).
   *CRITICAL CONSTRAINT:* Do not be blinded by the documentation. In the real world, `.Focus()` and `.Invoke()` frequently fail or are ignored by Windows OS protections. The agent MUST investigate how FlaUI surfaces these failures (e.g., does it throw an exception, or fail silently?).

5. **Fail-Safe Handoffs:**
   Based on the unreliability noted in Directive 4, map out how FlaUI actions will tie back into the Win32 fail-safes researched in `app_switcher.py`. If `element.Focus()` fails, how do we immediately detect that and fall back to Win32 `AttachThreadInput` or physical mouse/keyboard injection?

## Next Steps

- The agent should perform this research and produce a corresponding deep-dive document (`037_flaui_implementation_patterns_research.md`).
- The document MUST include short, concrete C# code snippets demonstrating the optimal way to handle the areas above, specifically including try/catch blocks for UIA action failures.
- Once these patterns are proven, they will serve as the strict reference guide for building the Adapters in the new MCP repository.
