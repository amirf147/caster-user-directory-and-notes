# Ticket 034: Determine Implementation Path for Micro Accessibility MCP Server

**Type**: `wayfinder:research` (Planning & Architecture)
**Status**: Open / Unclaimed
**Depends on**: Ticket 033 (Trajectory Pivot)
**Blocks**: Server Scaffolding (Execution Phase)

## Objective
Based on the pivot defined in Ticket 033, we must plan the exact implementation path for scaffolding our own bespoke C# "Micro MCP Server" before writing any actual code. We need to decide exactly what tools, transport layers, and project structures will be used.

## Questions to Resolve
1. **Transport Layer Selection**: Standard MCP uses `stdio` (stdin/stdout). However, `stdio` is a 1-to-1 pipe. If we want Caster *and* a background LLM Agent to connect to this server simultaneously in the future, should we configure the C# server to use **Named Pipes** or a local **HTTP/SSE** server instead?
2. **C# SDK vs Raw JSON**: Should we use an emerging open-source C# MCP SDK to handle the protocol boilerplate, or should we just write a raw JSON-RPC 2.0 parser to keep dependencies as close to zero as possible?
3. **Tool Definition**: What are the exact schemas for the initial three tools we will build? (e.g., What exact arguments will `FocusWindow` take, and what exact JSON structure will `GetWindowTree` return?)
4. **Python Client Integration**: Where exactly in the Caster lifecycle should the Python `mcp_client` spawn this server? (e.g., During engine boot alongside XML-RPC grids?)

## Next Steps
- Research available C# MCP SDKs (if any are stable for .NET).
- Define the JSON schemas for the MVP tools.
- Document the finalized implementation plan to serve as the blueprint for the coding phase. *(No server implementation will begin until this is defined).*
