# Ticket 028: Windows-MCP Integration Test & Threading Critique

**Type**: `wayfinder:execution` (Prototyping & Testing)
**Status**: Open / Unclaimed
**Blocks**: Final Architecture Proposal

## Question
Before we propose building a custom C# Accessibility Server, should we first test the existing `Windows-MCP` Python server in the real world? 
Furthermore, was our previous assumption that `Windows-MCP` safely handles STA threads accurate, or does Python fundamentally lack the required message pumps to prevent cross-process COM deadlocks?

## Next Steps
1. **Thread Critique**: Document the specific flaws in `Windows-MCP`'s Python STA implementation compared to a native C# implementation.
2. **Integration Test Plan**: Outline a plan to hook `Windows-MCP` up to a rudimentary Caster rule using `subprocess.Popen` and standard JSON-RPC.
3. **Execution**: Actually run the test to measure the overhead of its Python dependencies and evaluate its focus-stealing robustness before committing to building our own C# server.

## Research Breakdown
- [Windows-MCP Integration Test & Threading Critique Deep Dive](../research/028_windows_mcp_integration_test_deep_dive.md)
