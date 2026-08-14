[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Tickets ](../../README.md#wayfinder-uia--threading-research) › **Ticket 021: Design the MCP Server Interface (To...**

---

# Ticket 021: Design the MCP Server Interface (Tools vs Fallbacks)

**Type**: `wayfinder:research` (Communication & Architecture)
**Status**: Open / Unclaimed
**Blocks**: Proposing a unified architecture to Caster and Dragonfly maintainers

## Question
Before proposing an architecture to the upstream maintainers, we need to clearly define the boundary between Caster (the Client) and the Accessibility subsystem. How should the MCP Server expose its capabilities, and how should it handle the fragmentation of Windows Accessibility APIs (UIA, MSAA, Win32 COM)?

Specifically:
1. **Server vs. Tool Boundary**: What constitutes the "Server", and what constitutes a "Tool"? 
2. **API Fragmentation**: Should we have separate MCP Servers for UIA, MSAA, and raw Win32 APIs, or a single unified "Accessibility Server"?
3. **Abstraction Level**: Should the MCP Tools expose raw, granular API calls (e.g., `uia_get_property`, `msaa_get_acc_child`), or should they expose high-level, intent-based actions (e.g., `click_element(id)`) that handle the API fallback logic internally, similar to how Terminator and NVDA operate?

## Next Steps
- Define the distinction between an MCP Server (the host process) and MCP Tools (the exposed capabilities).
- Research the pros and cons of abstracting the fallback logic (UIA -> MSAA -> Win32) behind a single set of MCP Tools.
- Draft a high-level proposal of the ideal MCP Tool schemas that Caster would consume, ensuring Caster's codebase remains completely agnostic to the underlying Windows API quirks.
