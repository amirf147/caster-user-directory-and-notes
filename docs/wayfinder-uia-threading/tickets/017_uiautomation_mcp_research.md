# Ticket 017: Research UIAutomation MCP Server Architecture

**Type**: `wayfinder:research` (AFK)
**Status**: [CLOSED]
**Blocks**: Core Engine Threading Understanding / Non-blocking UIA

## Question
How does the `uiautomation-mcp` repository implement UI Automation? 
Could shifting our architecture to use an MCP (Model Context Protocol) server—rather than wrestling with custom out-of-process Python threading—provide a better solution for Caster? How does this project handle the notorious COM threading (STA/MTA) deadlocks?

## Resolution
1. **The MCP Server Paradigm**: Instead of Caster spinning up its own background Python threads (which lead to COM crashes), Caster could act as an MCP client and offload UIA calls entirely to a dedicated, language-optimized MCP server. This also makes the Windows UI instantly accessible to future AI agents (which natively speak MCP).
2. **Implementation Language (.NET C#)**: The `uiautomation-mcp` repository is built in .NET 9.0. C# has first-class native integration with Windows UI Automation, completely sidestepping the overhead and instability of Python's `comtypes` and `pywinauto`.
3. **Multi-Process Architecture**: The repository splits the workload to guarantee stability. It features a main `UIAutomationMCP.Server` (handling JSON-RPC MCP requests) and separate subprocesses (`UIAutomationMCP.Subprocess.Worker`, `UIAutomationMCP.Subprocess.Monitor`) that do the actual UIA COM interop. This isolates the server from COM hangs or memory leaks.
4. **Caching & Performance**: The repo implements a sophisticated `CacheRequest` strategy for bulk element reads (e.g., `GetElementTree`), optimizing the heavy cross-process COM calls inherently required by UIA.

**Full Educational Breakdown**: [017_uiautomation_mcp_educational_breakdown.md](../research/017_uiautomation_mcp_educational_breakdown.md)
