[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Research ](../../README.md#wayfinder-uia--threading-research) › **Research: App Switcher MCP Investigation & Tool...**

---

# Research: App Switcher MCP Investigation & Tool Design

**Ticket:** 036
**Author:** Wayfinder Agent
**Target:** `app_switcher.py` & C# Micro MCP Server Tool Design

## 1. Executive Summary

This investigation analyzes the existing Python `app_switcher.py` utility to extract requirements for the initial "App Switcher" functionality in the bespoke C# Micro MCP Server. The goal is to determine the optimal data structures, identify necessary fail-safes (edge cases), and design atomic tool schemas that can be effectively utilized by both voice-driven grammar engines (Caster) and eventual LLM Agents, without succumbing to feature bloat.

---

## 2. Data Structure Transformation

Currently, Caster relies on a mutable `aliases` dict mapped to a `WindowInfo` NamedTuple. To transition this to a stateless C# MCP server, the server must own the "source of truth" regarding window state.

### 2.1 The Ideal C# MCP Window Object
Instead of hardcoding complex concepts like `is_tab` or application-specific hotkeys (e.g., `ctrl_pgdn` for IDEs vs `ctrl_tab` for browsers) into the server, the server should return a generic, serialized representation of open windows. 

**Proposed `WindowContext` Schema (Returned to LLM/Caster):**
```json
{
  "ProcessName": "Code",
  "WindowTitle": "app_switcher.py - Caster - Visual Studio Code",
  "Handle": 123456,
  "IsActive": true,
  "BoundingRect": {"X": 0, "Y": 0, "Width": 1920, "Height": 1080}
}
```

*Note on "Tabs":* The C# server **does not need to know** if an application uses tabs natively. The logic of "this is a tabbed app, so I must press Ctrl+Tab to cycle" should remain a client-side (or Agent-side) concern for now. Exposing raw window titles gives the LLM enough context to infer tab state (e.g., "app_switcher.py" inside "Visual Studio Code").

---

## 3. Designing atomic LLM/MCP Tools

To prevent LLM confusion and ensure snappy execution for voice commands, the server should expose atomic, distinct tools rather than a massive "do everything" god function.

### 3.1 Initial Tool Schemas (Immediate Implementation)
1. **`ListWindows` Tool (Exploration)**
   - *Purpose:* Allows the LLM or Caster to query what is open.
   - *Arguments:* `process_name` (optional filter).
   - *Returns:* Array of `WindowContext` objects.

2. **`FocusWindow` Tool (Execution)**
   - *Purpose:* Brings a specific window to the foreground.
   - *Arguments:* `process_name` (string), `window_title` (string, fuzzy match).
   - *Fail-safe Behavior:* If the window doesn't exist, it should return a clear string error (`"Error: Window not found"`) rather than throwing a hard exception, allowing an LLM to gracefully recover or create a new instance.

### 3.2 Deferred Features (Out of Scope for Initial MVP)
1. **Virtual Desktop Manipulation:** `app_switcher.py` heavily uses `pyvda` to filter and move windows across desktops. We will defer Virtual Desktop APIs in the C# server until basic focus reliability is proven.
2. **Taskbar UIA Clicks:** The Python "Tier 2" fallback clicks the Taskbar. We will defer this. The C# server's primary OS bypass (`AttachThreadInput` + Alt key injection) is usually sufficient and faster.
3. **Alias Persistence:** The C# server should be stateless. Alias resolution should remain in the Python client or be handled by the LLM's active memory context.

---

## 4. Edge Cases & Fail-Safes

A robust LLM tool must handle ambiguity gracefully:

- **Ambiguous Matches:** If `FocusWindow(process_name="Code")` is called but 3 VS Code windows are open, the server should *not* arbitrarily focus one. It should return a soft error: `"Error: Multiple windows match 'Code'. Please refine query with window_title. Available titles: [...]"`.
- **Ghost Windows:** The server must rigorously filter out background daemon windows (e.g., `ApplicationFrameHost`, `TextInputHost`) during `ListWindows` to prevent LLM hallucination.
- **Dead Handles:** The server must verify a window `Handle` is still valid (`IsWindow(hwnd)`) immediately prior to calling `SetForegroundWindow`, as windows can be closed asynchronously between the LLM's thought process and tool execution.
