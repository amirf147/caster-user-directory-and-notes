# Ticket 029: Execute Windows-MCP Integration Test

**Type**: `wayfinder:execution` (Coding & Testing)
**Status**: Open / Unclaimed
**Blocks**: Final Architecture Proposal

## Objective
Write and execute a small Caster rule to directly invoke the `Windows-MCP` Python server via `subprocess.Popen` and JSON-RPC. This will give us hard data on its latency, overhead, and reliability in a real-world dictation scenario without relying on LLMs.

## Required Tasks
1. **Create the Hook**: Write a Python script (`test_windows_mcp.py`) inside `caster_user_content` that spawns `windows-mcp` using `subprocess.Popen(..., stdin=subprocess.PIPE, stdout=subprocess.PIPE)`.
2. **Execute a Command**: Send a hardcoded JSON-RPC request to switch focus to a specific window.
3. **Measure**: Log the startup latency, the execution latency, and whether the focus switch succeeded or deadlocked.

## Outcome Management
The results and logs of this execution ticket will be synthesized into a new Research Breakdown document. If the latency is unacceptably high due to Python dependencies, or if it still deadlocks, that document will serve as the definitive proof required to authorize the creation of a native C# `.NET MCP Server`. If it succeeds brilliantly, we will pivot to adapting it.
