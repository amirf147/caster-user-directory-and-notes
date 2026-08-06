# Ticket 028 Deep Dive: Windows-MCP Integration Test & Threading Critique

This document addresses two critical points regarding the `Windows-MCP` repository: critiquing my previous assessment of its thread safety, and proposing a real-world integration test.

## 1. Threading Critique: Was I Naive?
In my previous analysis, I praised `Windows-MCP` for running UIA calls sequentially on an STA thread to avoid cross-apartment deadlocks. **You were absolutely right to question this.** My assessment was naive.

While running sequentially on an STA thread protects the Python script from deadlocking *itself* (cross-apartment marshaling), it does **not** protect it from cross-process COM deadlocks. 

Here is the fundamental flaw with Python and UIA:
When a UIA client (like `Windows-MCP`) makes a COM call to a target application (like Firefox), the Windows COM subsystem requires the calling STA thread to continuously pump Windows messages (via `GetMessage` / `DispatchMessage`). If the target application takes 2 seconds to respond, the COM subsystem pumps messages in the background to keep the OS responsive and handle incoming COM callbacks. 

If you do not run a message pump, and the target process hangs, your STA thread deadlocks. 

I searched the `Windows-MCP` codebase for `PumpMessages` and `DispatchMessage`. I found a message pump, but it is strictly used for a global hotkey registration overlay, **not** for the main UIA traversal loop in `tree/service.py`. 

### Python vs C# for UIA
This proves exactly why a C# implementation is fundamentally superior:
- **In C#**: If you build a WPF or WinForms UI Automation tool, the .NET runtime automatically handles the message pumping on the main thread for you. Even in a console app, you can easily wrap UIA calls in `Dispatcher.Run()` to guarantee COM safety.
- **In Python**: `comtypes` does not implicitly pump messages during synchronous loops. Writing a robust message pump around every single UIA property request in Python is incredibly tedious and prone to breaking.

So, while `Windows-MCP` is well-written for Python, it is still a Python UIA script, meaning it is still vulnerable to catastrophic cross-process deadlocks that C# is immune to.

## 2. Integration Test Plan
Despite its flaws, jumping straight into a massive C# architectural rewrite without testing what we have is a mistake. We should absolutely test `Windows-MCP` as-is to see what it gets right (like the `AttachThreadInput` focus hacks) and what it gets wrong (like Python bloat/latency).

**The Test Plan:**
1. **No LLMs Required**: We will write a tiny Caster rule (e.g., in your `caster_user_content` folder).
2. **The Hook**: The rule will use `subprocess.Popen` to launch the `windows-mcp` Python process with `stdin=PIPE` and `stdout=PIPE`.
3. **The Execution**: When you say "Test Focus Firefox", the Caster rule will write a hardcoded JSON-RPC string to the MCP server's standard input:
   ```json
   {
     "jsonrpc": "2.0",
     "method": "tools/call",
     "params": {
       "name": "App",
       "arguments": { "mode": "switch", "name": "firefox" }
     },
     "id": 1
   }
   ```
4. **Observation**: We will measure exactly how many milliseconds it takes for the server to parse the JSON and execute the Win32 focus hack, and whether the Python dependencies (`psutil`, `Pillow`, `dxcam`) cause unacceptable startup lag. 

This test will give us the hard data we need before we write a single line of C#.
