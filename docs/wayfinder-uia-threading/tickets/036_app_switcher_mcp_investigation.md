[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Tickets ](../../README.md#wayfinder-uia--threading-research) › **Ticket 036: Investigate App Switcher Functional...**

---

# Ticket 036: Investigate App Switcher Functionality for C# MCP Server

**Type**: `wayfinder:research` (Planning & Architecture)
**Status**: Open / Unclaimed
**Depends on**: N/A
**Blocks**: C# MCP App Switcher Implementation

## Objective
Investigate the existing App Switcher functionality in Caster to determine the requirements and data structures for building an initial, minimal App Switcher tool inside the new C# MCP Server. The investigation should dive deep into the existing blueprints and code, but maintain a critical perspective to avoid jumping to conclusions prematurely. 

## Key Areas to Investigate
1. **Data Structures:** What information must the C# MCP server expose about a window to enable LLMs (and speech grammars) to switch to it? (e.g., AppName, Window Title, IsTabbed, etc.).
2. **Fail-Safes & Edge Cases:** How should the system handle scenarios where an application or alias doesn't exist? What are the tiered fail-safes?
3. **LLM Utility Design:** Since an LLM will eventually use this, we need to design the MCP tools as atomic utilities (and potentially exploration tools) that provide necessary context without overwhelming the grammar/LLM.
4. **Pattern Extraction:** Identify which patterns from the current App Switcher should be migrated immediately and which can be deferred (we don't want to add everything at once).

## Next Steps
- Execute this ticket by conducting deep research into `app_switcher.md`, the architectural blueprints, and the actual python implementation (`window_switching.py`).
- Produce a corresponding deep-dive research document outlining the C# MCP App Switcher data structures and tool schemas.
- Update `map.md` to formally mark vision-based UI automation as out of scope due to latency constraints for real-time voice commands.
