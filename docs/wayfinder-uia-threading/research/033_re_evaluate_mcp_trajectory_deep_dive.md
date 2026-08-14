[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Research ](../../README.md#wayfinder-uia--threading-research) › **Educational Breakdown: Re-evaluating the MCP Tr...**

---

# Educational Breakdown: Re-evaluating the MCP Trajectory (Ticket 033)

This document captures a critical architectural pivot regarding how Caster should interact with Model Context Protocol (MCP) servers, distinguishing between "LLM Bloat" and being "LLM-Ready."

## 1. The Initial Misstep: Adopting LLM Bloatware
Our previous research heavily investigated pre-built MCP servers (`Windows-MCP` in Python, `desktop-pilot-mcp` in C#). While the underlying technology (C# and FlaUI) proved to be the ultimate solution to our Python COM deadlocks, the repositories themselves were fundamentally flawed for our use case.

They were designed as generic "Computer Use" agents for LLMs like Claude. As a result, they included heavy dependencies (OCR, DirectX screen capture, visual diffing) and exposed upwards of 55 granular tools. When a voice engine attempts to use them for a simple task (like focusing a window), it often requires chaining multiple RPC calls together, introducing unnecessary failure points and latency. Furthermore, tools like `desktop-pilot-mcp` failed silently when focus-stealing was blocked by Windows, lacking the robust Win32 fail-safes historically found in Caster's `app_switcher.py`.

## 2. The Paradigm Shift: The Hybrid Voice/LLM Ecosystem
The question arose: *Are we going in the wrong direction by using LLM tech for a voice engine?*

The answer is no, provided we understand the difference between **Design Time** and **Run Time**.
- **Design Time (LLM Exploration)**: An LLM can connect to our MCP server, use tools to "look" at the UI tree of a banking website, figure out the `AutomationId` of a button, and dynamically generate a permanent Python Caster rule for the user.
- **Run Time (Voice Execution)**: The user speaks a command. Caster executes the generated Python rule, sending a *single, instantaneous JSON-RPC command* to the MCP server to click that specific button. No LLM exploration happens here.

Because MCP (JSON-RPC over `stdio` or named pipes) has sub-5ms overhead, it is perfectly suited for real-time voice execution, provided the tools are pre-chained and optimized.

## 3. The Pivot: The C# "Micro" MCP Server
To achieve this hybrid ecosystem, we must abandon third-party bloated servers and build a **Micro MCP Server**. 

### Core Tenets of the Micro Server:
1. **Language**: C# .NET (to natively handle COM MTA thread lifecycles and avoid Python deadlocks).
2. **Library**: `FlaUI.UIA3` (for deep, cached UI tree traversal).
3. **Protocol**: Official Anthropic MCP JSON-RPC (implementing `tools/list` and `tools/call` so it is universally readable by both Caster and LLMs).
4. **Tool Scope**: Expose only highly optimized, macro-level tools (e.g., `FocusWindow`, `GetTabs`, `ClickElement`).
5. **Fail-safes Embedded**: Move Caster's legacy Python focus fail-safes (Win32 `AttachThreadInput`, `ShowWindow`, Alt-key injection) directly into the C# `FocusWindow` tool, isolating the dangerous OS hooks away from the synchronous voice engine.

By adhering to this design, Caster gains deadlock-free accessibility, while remaining 100% "LLM-Ready" for future AI agents.
