[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Tickets ](../../README.md#wayfinder-uia--threading-research) › **Ticket 020: Research MCP Server Internals vs. X...**

---

# Ticket 020: Research MCP Server Internals vs. XML-RPC

**Type**: `wayfinder:research` (AFK)
**Status**: [CLOSED]
**Blocks**: Deep evaluation of `uiautomation-mcp` (Ticket 019)

## Question
Before fully committing to an MCP-based architecture, we need a foundational understanding of what an MCP (Model Context Protocol) server is and how it functions under the hood. How does it compare to our existing XML-RPC implementation used for the foot pedal?

Specifically:
1. **Protocol Differences**: What is the Model Context Protocol? How does its transport layer (often JSON-RPC over stdio or HTTP) compare to XML-RPC?
2. **Threading & Concurrency**: Does the MCP specification dictate how a server handles threading, or is that left entirely to the implementation? How does a typical MCP server handle concurrent requests compared to Python's `SimpleXMLRPCServer` used in our foot pedal bridge?
3. **Caster Integration Context**: How similar is the foot pedal XML-RPC IPC bridge to a potential MCP client implementation in Caster? What are the architectural similarities and differences?
4. **Internal Mechanics**: How do MCP internals work (e.g., capabilities negotiation, tool registration, resources, and prompts)?

## Resolution
- **Protocol**: MCP is an RPC protocol built on JSON-RPC 2.0, primarily utilizing OS pipes (`stdio`) for local communication, thereby eliminating the TCP port conflicts and security risks inherent to the foot pedal's XML-RPC `localhost:9999` approach.
- **Threading**: MCP is inherently asynchronous due to JSON-RPC request `id` tracking. While the spec doesn't dictate threading, modern MCP servers (.NET, Node) use robust async/await thread pools, entirely bypassing the single-thread blocking limitations of Python's `SimpleXMLRPCServer`.
- **Conclusion**: Caster acting as an MCP Client is architecturally similar to the foot pedal IPC bridge (process boundary separation), but vastly superior in stability, thread safety, and AI readiness.

**Full Educational Breakdown**: [020_mcp_vs_xmlrpc_educational_breakdown.md](../research/020_mcp_vs_xmlrpc_educational_breakdown.md)
