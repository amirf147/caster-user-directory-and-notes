# Ticket 032: Execute Desktop Pilot MCP Integration Test

**Type**: `wayfinder:test` (Integration & Performance Benchmarking)
**Status**: Open
**Blocks**: Final Architecture Proposal

## Objective
Build, launch, and benchmark the `desktop-pilot-mcp` C# server (`winapp-mcp`) via stdio JSON-RPC using a standalone Python test script. Verify its startup latency, tool call execution speed, process lifecycle, and compare its behavior directly against the results from Ticket 029/030 (`Windows-MCP`).

## Tasks
1. **Server Launch Mechanism**: Verify launch options (`npx -y winapp-mcp` vs. local `dotnet run` / `WinAppMCP.exe`).
2. **Standalone Test Script**: Create `test_desktop_pilot_mcp_standalone.py` in `caster_user_content/rules/global/` to test stdio JSON-RPC initialization and tool execution.
3. **Graceful Teardown**: Wrap process invocation in `try...finally` to ensure the server child process terminates cleanly and leaves no orphaned background processes on `KeyboardInterrupt`.
4. **Benchmark Execution**: Measure startup latency and warm tool call execution latency.
5. **Analyze Window Switching Behavior**: Investigate why the test script failed to switch windows and determine if `desktop-pilot-mcp` has native capabilities to focus windows without adding new tools.

## Verification
- Test script runs without errors and prints JSON-RPC responses and timing benchmarks.
- Clean process termination verified (no orphaned `WinAppMCP.exe` or `node` processes left running).
- Window focusing mechanism is clearly identified and documented.
