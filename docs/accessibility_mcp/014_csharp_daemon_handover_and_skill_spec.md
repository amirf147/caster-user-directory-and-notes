[ 🏠 Docs Home ](../README.md) › [ 📁 Accessibility MCP ](CONTEXT.md) › **014: C# Daemon Handover & Skill Specification**

---

# C# Context Daemon Handover Blueprint & Skill Specification (014)

> **Document Status:** Exploratory Blueprint (Paused / Under Review)  
> **Target Framework:** `.NET 10 (LTS)` (`net10.0-windows`)  
> **Core Library:** `FlaUI.UIA3 5.0.0` (Native Windows UI Automation 3)  
> **Architecture:** Out-of-Process Background Context Daemon + MCP Server Bridge  
> **Related Documents:** [008: Real-World Observations](008_real_world_observations_and_caching_architecture.md) | [010: Traversal Telemetry](010_telemetry_benchmarks_and_live_findings.md) | [011: FlaUI Evaluation](011_flaui_evaluation_and_dual_plane_architecture.md) | [013: Empirical Post-Mortem](013_v23_empirical_postmortem_and_event_diagnostics.md) | [015: Epistemic Recalibration](015_recalibration_and_adversarial_architecture_review.md)

> [!CAUTION]
> **Wait, Hold On a Second — Epistemic Pause & Architectural Freeze:**  
> This specification represents an exploratory architectural concept developed during rapid prototyping. We identified that we moved too quickly into prescribing a multi-tier C# daemon before empirically validating underlying OS physics (such as whether UIA 3 caching actually resolves WebExtension DOM traversal stalls).  
> **This blueprint is temporarily paused and held as a candidate design.** Before treating this as definitive or executing implementation, refer to [015: Epistemic Recalibration & Adversarial Architecture Review](015_recalibration_and_adversarial_architecture_review.md) for the adversarial red-team audit and 4-gate verification requirements.

---

## 1. Executive Summary: The Python-to-C# Evolutionary Leap

The **Active Desktop Context Engine (ADCE)** maintains a real-time, in-memory semantic graph of the active Windows desktop (active Virtual Desktop, foreground application, open browser/editor tabs, focused element, and value snippets) and streams it to local AI agents and voice tools via the **Model Context Protocol (MCP)**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               ARCHITECTURAL EVOLUTION                                 │
├────────────────────────────────┬───────────────────────────────────────────────────────┤
│ **Python PoC (Exploratory)**    │ **C# Standalone Daemon (Production)**                 │
├────────────────────────────────┼───────────────────────────────────────────────────────┤
│ • Synchronous COM IPC over GIL │ • Native compiled .NET 10 / FlaUI 5 runtime           │
│ • Manual recursive tree walks  │ • UIA 3 `CacheRequest` batch pre-fetching (< 5ms)     │
│ • Prone to DOM traversal lag   │ • Scoped `TreeScope.Children` (Zero DOM crawling)     │
│ • Message pump transition deadlocks │ • Native async thread pools & event handlers     │
│ • Fragile heuristic pruning    │ • Direct container targeting & WebExtension support   │
└────────────────────────────────┴───────────────────────────────────────────────────────┘
```

The Python prototype (`scripts/context_poc.py`) fulfilled its exploratory mission: it mapped the Windows accessibility landscape, isolated cross-process COM constraints, and documented critical browser/DOM edge cases. The standalone C# daemon provides a robust, compiled, zero-heuristic implementation.

---

## 2. Synthesized Domain Knowledge & Critical Rules

An AI agent or developer building the C# engine must adhere to the following verified technical truths:

### A. The Browser DOM Trap & UIA3 `CacheRequest` Solution
* **The Trap:** Modern web browsers (Gecko/Waterfox, Chromium/Edge/Chrome) contain 5,000–50,000+ accessibility nodes. Doing a recursive tree walk queries thousands of COM pointers, resulting in **5–10 second latency**.
* **The C# Solution:** Never execute recursive tree walks on browser windows. Instead, query the **Tabstrip Container** directly and activate a `CacheRequest` scoped to `TreeScope.Children`:
  ```csharp
  var cacheRequest = new CacheRequest {
      TreeScope = TreeScope.Children
  };
  cacheRequest.AddProperty(AutomationObjectIds.NameProperty);
  cacheRequest.AddProperty(AutomationObjectIds.AutomationIdProperty);
  cacheRequest.AddPattern(AutomationObjectIds.SelectionItemPatternId);

  using (cacheRequest.Activate())
  {
      // Executes in a single batch IPC round-trip inside the target process (< 5ms)
      var tabItems = tabContainer.FindAllChildren(cf => cf.ByControlType(ControlType.TabItem));
      foreach (var tab in tabItems)
      {
          var isSelected = tab.Patterns.SelectionItem.PatternOrDefault?.IsSelected.Value ?? false;
          var tabName = tab.Properties.Name.Value;
      }
  }
  ```

### B. WebExtension Sidebars (Tree Style Tab / Sidebery)
* In browsers using sidebar extensions (e.g. Waterfox/Firefox with Tree Style Tab), tabs live inside a sidebar iframe (`DocumentControl`).
* **Rule:** Do not blanket-prune all `DocumentControl` elements. Identify the sidebar container by its parent pane / automation ID (`"sidebar-box"` / `"sidebar"`), and inspect its immediate child tab list while bypassing the main web page viewport.

### C. Electron / Monaco IDEs (VS Code & Antigravity)
* Electron defers creating accessibility nodes for outer workbench controls while focus is inside Monaco's editor canvas (`Chrome_RenderWidgetHostHWND`).
* **Rule:** Use **Bottom-Up Sibling Traversal**: climb from the focused `EditControl` up to the editor group container and inspect the adjacent tabstrip header container (`workbench.parts.editor`).

### D. Concurrency & Message Pump Isolation
* Never execute UIA COM queries synchronously inside WinEvent / Windows Message callbacks (`GetMessageW`).
* **Rule:** Native WinEvent hooks must only post lightweight event tokens (`HWND`, `EventType`, `Timestamp`) into an asynchronous `Channel<T>` worker queue. Trailing-edge debouncing (50–75ms) guarantees that only the final settled focus state is queried.

### E. Terminal / Self-Monitoring Immunity
* **Rule:** The daemon must ignore its own process ID, its own window handle (`GetConsoleWindow()`), and the hosting terminal process tree (`WindowsTerminal.exe`, `conhost.exe`).

---

## 3. High-Level Architecture of the C# Daemon

```
                                  [Windows OS]
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
     [WinEvent Hook Thread]                       [Virtual Desktop Manager]
     • EVENT_SYSTEM_FOREGROUND                    • IVirtualDesktopManagerInternal
     • EVENT_OBJECT_FOCUS                         • Desktop GUID & Workspace Name
                │                                             │
                └───────────────┬─────────────────────────────┘
                                ▼
                   [Async Channel<DesktopEvent>]
                                │
                                ▼
                  [Desktop Context Worker Engine]
                  • Trailing-Edge Debounce (75ms)
                  • HWND Classification & Cache
                  • FlaUI UIA3 CacheRequest Batching
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
     [In-Memory Semantic Graph]       [MCP Server Endpoint]
     • Active Workspace & Desktop     • Streamable SSE / HTTP
     • Top Window & Class             • Tool: get_desktop_context
     • Tab Array (Active & Open)      • Resource: desktop://current
     • Focused Node & Value Snippet
```

---

## 4. MCP JSON Context Schema

The C# daemon exposes the live desktop state conforming to this standardized JSON schema:

```json
{
  "timestamp": "2026-08-23T02:30:00.000Z",
  "workspace": {
    "virtual_desktop_id": "3f2a1b0c-...",
    "virtual_desktop_name": "Development",
    "desktop_index": 1
  },
  "window": {
    "hwnd": "0x002A0B42",
    "title": "Waterfox - Technical Documentation",
    "process_name": "waterfox.exe",
    "pid": 35572,
    "class_name": "MozillaWindowClass"
  },
  "tabs": {
    "container_type": "TreeStyleTab",
    "total_count": 26,
    "active_tab": "Technical Documentation",
    "items": [
      { "index": 1, "title": "Developer Portal", "is_active": false },
      { "index": 2, "title": "Technical Documentation", "is_active": true },
      { "index": 3, "title": "Issue Tracker", "is_active": false }
    ]
  },
  "focus": {
    "control_type": "DocumentControl",
    "element_name": "Technical Documentation",
    "automation_id": "",
    "bounding_box": { "left": 1031, "top": 36, "width": 888, "height": 1131 },
    "value_snippet": "https://docs.example.org/spec"
  }
}
```

---

## 5. Portable Skill Specification (`adce-core`)

To bootstrap an AI agent in the new C# repository, copy the text block below into `.agents/skills/adce-core/SKILL.md` (or `~/.gemini/config/skills/adce-core/SKILL.md`):

````markdown
---
name: adce-core
description: Core architectural reference, UIA 3 caching patterns, and MCP schemas for building the Active Desktop Context Engine (ADCE) in .NET 10 and FlaUI 5.
---

# Active Desktop Context Engine (ADCE) — Core Architectural Skill

Use this skill when developing, refactoring, or testing the C# desktop context engine and MCP daemon.

## 1. Technical Stack & Dependencies
* **Framework:** `.NET 10 (LTS)` (`<TargetFramework>net10.0-windows</TargetFramework>`)
* **UIA Library:** `FlaUI.UIA3` (v5.0.0+)
* **IPC/Server:** Model Context Protocol (MCP) C# SDK / ASP.NET Minimal API SSE

## 2. Core Operational Constraints
1. **Never Crawl Browser DOMs:** Never use recursive unpruned tree walks on `MozillaWindowClass` or `Chrome_WidgetWin_1`. Always use `CacheRequest` scoped to `TreeScope.Children` on the tabstrip container.
2. **Decouple Event Hooks from UIA:** All OS WinEvent callbacks must push tokens to a `Channel<T>` and exit immediately. UIA inspection runs on an MTA background worker.
3. **Trailing-Edge Debouncing:** Wait 50–75ms after the latest focus event before querying UIA to ensure the target window has settled.
4. **Self-Monitoring Filtering:** Ignore `GetConsoleWindow()`, own PID, and terminal processes (`WindowsTerminal.exe`, `conhost.exe`).

## 3. High-Performance FlaUI Tab Extraction Pattern
```csharp
public static List<TabItemModel> ExtractTabs(AutomationElement topWindow, string className)
{
    var tabs = new List<TabItemModel>();
    if (topWindow == null) return tabs;

    var cacheRequest = new CacheRequest { TreeScope = TreeScope.Children };
    cacheRequest.AddProperty(AutomationObjectIds.NameProperty);
    cacheRequest.AddPattern(AutomationObjectIds.SelectionItemPatternId);

    // Locate Tab Container directly
    var tabContainer = topWindow.FindFirstDescendant(cf => cf.ByControlType(ControlType.Tab));
    if (tabContainer == null) return tabs;

    using (cacheRequest.Activate())
    {
        var tabElements = tabContainer.FindAllChildren(cf => cf.ByControlType(ControlType.TabItem));
        foreach (var tab in tabElements)
        {
            var isSelected = tab.Patterns.SelectionItem.PatternOrDefault?.IsSelected.Value ?? false;
            tabs.Add(new TabItemModel {
                Title = tab.Properties.Name.Value,
                IsSelected = isSelected
            });
        }
    }
    return tabs;
}
```

## 4. Documentation Strategy & Path Portability
* **Self-Contained:** This skill contains all necessary domain rules and patterns.
* **Local Reference (Optional):** If referencing historical research locally, reference the relative path `../caster/docs/accessibility_mcp/` or the environment variable `%CASTER_REPO_PATH%`. Do not hardcode absolute user directory paths.
````

---

## 6. Path Portability & Zero-Leakage Publishing

When initializing the new C# repository:
1. **Zero External Dependency:** The new repository and its `.agents/` workflows rely entirely on this self-contained handover specification (`014`) and `adce-core` skill.
2. **No Absolute Paths:** All documentation, code references, and test files use clean relative paths or environment variables (`%CASTER_DOCS_PATH%`).
3. **No Web Request Friction:** Local AI pair programmers have immediate, high-velocity access to all architectural patterns directly within the repository workspace.
