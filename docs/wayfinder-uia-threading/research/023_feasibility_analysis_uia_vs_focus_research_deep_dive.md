[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Research ](../../README.md#wayfinder-uia--threading-research) › **Ticket 023 Deep Dive: Feasibility Analysis - UI...**

---

# Ticket 023 Deep Dive: Feasibility Analysis - UIA Performance vs Window Focus

This document gathers the critical context requested in Ticket 023, specifically analyzing window focus failures, thread safety, and architecture scoping.

## 1. Focus Failures and Thread Jumbling
In Caster and Dragonfly, switching windows (e.g., using a fallback command) relies heavily on two mechanisms: `FocusWindow` and `WaitWindow`.

**The Root Cause of Freezing during Focus:**
I analyzed Dragonfly's `WaitWindow` action (`dragonfly/actions/action_waitwindow.py`). When it waits for a window to come into focus, it enters a "tight spin-lock":
```python
while 1:
    foreground = Window.get_foreground()
    # ... checks if title matches
    if not mismatch:
        return
    if time.time() - start_time > self._timeout:
        raise ActionError("Timeout...")
```
Notice that there is **no `time.sleep()`** in this loop. It literally spins as fast as the CPU allows, completely locking up the main Python thread until the window appears or the timeout is reached. If Windows takes 2 seconds to bring the window forward, the voice engine is 100% frozen for 2 seconds.

**Thread Safety & Jumbling:**
When `SetForegroundWindow` is called, Windows requires the calling thread to already have focus rights. If it doesn't, Windows silently ignores the request or flashes the taskbar icon. If this happens, `WaitWindow` will spin furiously until its timeout is reached, making the entire voice engine feel frozen. It is not necessarily "thread jumbling," but rather a brutal blocking mechanism inherent to how Dragonfly handles asynchronous OS events on a synchronous thread.

**Acceptable Blocking:**
Because the voice engine runs synchronously, it *must* block while waiting for a window to focus. If it didn't, it would execute the user's next keystrokes into the wrong window. Therefore, brief blocking is correct, but it desperately needs a more graceful, non-CPU-pegging wait mechanism.

**The Custom `app_switcher.py` Failures:**
In the Caster user directory's `app_switcher.py`, a robust 3-tier fallback system is used. Unlike Dragonfly, its custom `verify_focus` loop properly uses `time.sleep(0.05)` to avoid pegging the CPU. However, if Tier 1 (Win32 Focus APIs) fails, it falls back to Tier 2: using `pywinauto` to click the Windows Taskbar. 
Because `pywinauto` executes UIA calls synchronously on the main thread (without a message pump), if that UIA call to the taskbar hangs or takes too long, the voice engine completely deadlocks. Therefore, the "focus failures" experienced in the complex app switcher are directly caused by UIA COM deadlocks triggering during the Tier 2 fallback.

## 2. Terminator vs MCP Server Overhead
A crucial question was raised: **Why doesn't Terminator use an MCP Server? Is there unnecessary overhead?**

Terminator is actually written natively in **Rust** (not C#), and it avoids an MCP server by using **FFI (Foreign Function Interface) bindings** (e.g., `terminator-python`). FFI allows the Python host to load the compiled Rust library directly into its own memory space and call its functions as if they were native Python code. 

Because Terminator shares the memory space via FFI, it doesn't need Inter-Process Communication (IPC). 

Caster *could* theoretically build a Rust library and use FFI, but building an out-of-process MCP Server (in C# or Rust) is often preferred for accessibility because if a UIA query permanently hangs (deadlocks), an MCP Server can simply be killed and restarted without crashing the main Caster/Dragonfly voice engine. With FFI, a deadlock in the Rust library permanently freezes the Python host. 

**The Overhead:**
To talk to an external process (like an MCP server), Caster needs an IPC protocol. 
- MCP (Model Context Protocol) is simply JSON-RPC over `stdio`. 
- Yes, JSON serialization has a microsecond overhead compared to direct FFI memory calls.
- However, Caster *already* uses XML-RPC for Grids and Homunculus, which is significantly slower and heavier than JSON-RPC. The overhead of MCP is completely negligible for UI tasks, and it buys us the safety of process-isolation (if UIA deadlocks, we don't crash).

## 3. Architecture Scope: UIA vs Accessibility Server
To answer your final question: the architecture absolutely should **not** just be a "UIA Server." 
Because window switching, text editing, and button pressing require a mix of UIA, MSAA, and Win32, we should scope this as an **"Accessibility MCP Server."** 

This server would expose generic "Tools" to Caster (e.g., `FocusApplication`, `ClickElement`, `GetText`). Internally, the MCP server would intelligently decide whether to use UIA, MSAA, or native Win32 `SetForegroundWindow` to accomplish the goal. This completely shields Caster from the fragility of Windows APIs.
