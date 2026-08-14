[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Research ](../../README.md#wayfinder-uia--threading-research) › **Ticket 027 Deep Dive: Research Windows-MCP Repo...**

---

# Ticket 027 Deep Dive: Research Windows-MCP Repository

This document analyzes the `~/Documents/repos/Windows-MCP` repository to determine if it is a viable pre-built Accessibility Server for Caster.

## 1. Robustness and Threading Architecture
The `Windows-MCP` repository is remarkably robust in how it handles Windows threading. 
Because it is written in Python, it faces the exact same COM/GIL deadlock dangers we analyzed in Dragonfly. However, it elegantly solves them:
- **Sequential STA:** In `src/windows_mcp/tree/service.py`, the author explicitly notes that using `ThreadPoolExecutor` for UIA creates cross-apartment marshaling deadlocks. Instead, it sequentially processes UIA calls in the main thread's STA apartment to keep it safe. 
- **Robust Win32 Fallbacks:** In `src/windows_mcp/desktop/service.py`, its window focusing logic is battle-tested. It doesn't just call `SetForegroundWindow`; it uses `GetWindowThreadProcessId` and `AttachThreadInput` to explicitly attach the MCP thread's input state to the target window's thread, guaranteeing Windows grants the focus switch. It even catches "Access Denied" errors gracefully when trying to attach to elevated processes (like Task Manager).

## 2. Is it Overkill?
**Yes, it is massive overkill for a real-time Voice Engine.**
While robust, this server is designed to be a full "Computer Use Agent" for an LLM (like Claude). It includes massive dependencies that Caster doesn't need:
- `dxcam` (DirectX high-speed screen capture)
- `Pillow` (Image processing)
- Network scraping tools, Registry editing, Shell execution.

Furthermore, because it is written in Python (`pywin32` and `comtypes`), it is inherently heavier and slower than a natively compiled C# or Rust server. While its thread safety is excellent, Python's garbage collection and object marshaling still add micro-latency that isn't ideal for real-time dictation. 

## 3. Hooking into it WITHOUT an LLM
You asked if it is possible to hook into this server using standard speech grammars (without an LLM).
**Absolutely, 100%.**
MCP (Model Context Protocol) is nothing more than standard **JSON-RPC over `stdio`**. Caster doesn't need an LLM to use it. Caster can simply spawn the server using `subprocess.Popen` and send raw JSON strings directly to it when you speak a command.

For example, to switch to Firefox, Caster would just write this JSON string to the server's standard input stream:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "App",
    "arguments": {
      "mode": "switch",
      "name": "firefox"
    }
  },
  "id": 1
}
```
The server receives it, executes the robust `AttachThreadInput` focus logic, and returns a JSON success response. No LLM required.

## Conclusion
`Windows-MCP` is a phenomenal reference for how to write thread-safe UIA and robust Win32 focus hacks. However, it is too bloated (screen capture, registry tools) and built in the wrong language (Python) for a high-performance voice accessibility server.

**Recommendation:** We should not use `Windows-MCP` directly. Instead, we should extract its genius `AttachThreadInput` logic and build our own lightweight, lightning-fast C# `.NET MCP Server` that strictly focuses on Accessibility (UIA/Win32) without the LLM bloatware.
