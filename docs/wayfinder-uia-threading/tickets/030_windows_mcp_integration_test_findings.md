# Ticket 030: Windows-MCP Integration Test Findings & Next Steps

**Type**: `wayfinder:research` (Investigation & Analysis)
**Status**: Open
**Blocks**: Final Architecture Proposal

## Objective
Analyze the results from the `Windows-MCP` persistent integration test and determine the root causes of the observed bugs. Decide whether these issues necessitate abandoning the Python server in favor of a C# rewrite, or if they can be patched.

## Findings from Integration Test
During the persistent background test cycling through specific window titles, several critical flaws were observed in `Windows-MCP`:

1. **Inaccurate Tab/Window Matching (Fuzzy Matching Flaw)**:
   When attempting to switch to a specific browser tab, the server failed to accurately match the exact tab title. Instead, it randomly picked any available window for that browser (e.g., Waterfox). This indicates that its window enumeration or fuzzy matching logic is either ignoring specific tab titles or failing to traverse the UI Automation tree deep enough to distinguish tabs.

2. **Workspace / Virtual Desktop Isolation**:
   The server only successfully matched and switched to windows that were located on the *current* active workspace (virtual desktop). It failed to find or switch to windows located on other workspaces. This limits its utility as a global window management tool.

3. **Thread Hanging and Process Teardown Failures**:
   During the test, the process frequently froze and hung. It required the user to send multiple `Ctrl+C` interrupt signals to the terminal to force close it. 
   
## Required Investigations (Next Steps)
To move forward, we must investigate the root causes of these failures:

- **Investigate the Hanging Issue**: 
  Is the freeze occurring on *our* end (e.g., `test_mcp_standalone.py` not closing pipes/threads properly when breaking the loop)? Or is it on the *server's* end (e.g., `windows-mcp` failing to cleanly tear down its STA threads, async loops, or UIA COM objects during exit)?
- **Investigate Window Matching Logic**:
  Review the `windows-mcp` source code (specifically the `App` tool in `service.py`) to understand why it fails to match specific tab titles and why it cannot detect windows across Windows virtual desktops. 

These findings will directly inform whether we patch `windows-mcp` or proceed with a custom C# `.NET MCP Server`.
