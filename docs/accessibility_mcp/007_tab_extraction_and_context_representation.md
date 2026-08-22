[ 🏠 Docs Home ](../README.md) › [ 📁 Accessibility MCP ](CONTEXT.md) › **007: Tab Extraction & Context Representation**

---

# Tab Extraction and Real-Time Context Representation (v2.1)

This document explains the architecture, mechanics, and terminal representation of **Version 2.1** of the Active Desktop Context Engine (ADCE) Proof of Concept.

---

## 1. Root Cause of Missing Tabs in VS Code & Waterfox

In initial testing, tabs were not appearing for VS Code (Electron) or Waterfox/Firefox due to two architectural traps in accessibility tree traversal:

1. **Premature `DocumentControl` Pruning:**
   * Electron (VS Code) and Gecko (Waterfox) wrap their entire editor or browser viewport inside a `DocumentControl`.
   * When previous traversals encountered `DocumentControl`, they aggressively pruned all of its children to avoid crawling millions of DOM elements inside web pages.
   * However, in VS Code, the top editor tab strip (`TabItemControl`s for `test_mcp_standalone.py`, `context_poc.py`, etc.) is embedded *inside or alongside* the document wrapper.
   * **Fix in v2.1:** Prune `DocumentControl` elements only at depths greater than 4, or prune non-tab children instead of short-circuiting the entire branch.

2. **Top-Level Window Resolution (`get_top_level_window`):**
   * Focused events inside Chromium/Electron often originate on an inner Win32 control class (`Intermediate D3D Window` or `Chrome_RenderWidgetHostHWND`).
   * If `auto.GetForegroundControl()` returns this inner widget, a shallow tree walk will not see the sibling title bar or tab strip.
   * **Fix in v2.1:** `get_top_level_window(element)` climbs `GetParentControl()` until it reaches a control with a valid top-level Win32 `NativeWindowHandle` matching `GetForegroundWindow()`.

---

## 2. Technical Mechanics of Tab Extraction

The `extract_window_tabs(top_window, focused_element=None, max_depth=14)` function performs deep, multi-heuristic extraction:

```
                  ┌─────────────────────────────────────────┐
                  │    Top-Level Application HWND Window    │
                  └────────────────────┬────────────────────┘
                                       │
                         auto.WalkControl(maxDepth=14)
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
 [TabItemControl]              [ListItemControl]              [CustomControl]
 (Standard Tab Item)          ("tab" in AutomationId)        ("tab" in AutomationId)
        │                              │                              │
        └──────────────────────────────┼──────────────────────────────┘
                                       │
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
             [Active Tab Check]                 [VS Code Cleanup]
             • SelectionItemPattern             • Strip ", Editor Group"
             • Legacy IAccessible (0x4)         • Strip dirty "● " prefix
             • HasKeyboardFocus                 • Deduplicate BoundingRect
```

### Multi-Heuristic Selection Detection:
Different frameworks signal the "active" tab through different accessibility interfaces:
1. **UI Automation `SelectionItemPattern`:** Standard UIA controls expose `sel.IsSelected == True`.
2. **MSAA Legacy Accessible Bitmask (`0x00000004`):** For Win32 legacy tab controls, `GetLegacyIAccessiblePattern().State & STATE_SYSTEM_SELECTED (0x4)` flags the active tab.
3. **`HasKeyboardFocus`:** When a tab header is explicitly focused with keyboard navigation.
4. **Window Caption Fallback:** If the accessibility tree reports no selected item, the engine compares tab names against the top-level window title and the focused document name.

---

## 3. Terminal Representation & Highlighting

The live terminal dashboard in `context_poc.py` outputs a structured, colorized 3-tier view:

```text
============================================================================
  ACTIVE DESKTOP CONTEXT ENGINE (ADCE) - LIVE MONITOR (v2.1)
============================================================================
 Timestamp    : 2026-08-21 17:35:12
 Event Trigger: FOCUS_CHANGE
 Active App   : Waterfox (PID: 1968)
----------------------------------------------------------------------------
 WINDOW TABS:
  [      ] Tab 1: Dashboard
  ► [ACTIVE] Tab 2: Documentation
  [      ] Tab 3: Settings
----------------------------------------------------------------------------
 ACTIVE CONTROL HIERARCHY TREE:
  ┌── [WindowControl] Waterfox
    └── [PaneControl] Tab Browser
      └── [DocumentControl] Documentation  ◄ [FOCUSED NODE]
----------------------------------------------------------------------------
 FOCUSED ELEMENT DETAILS:
  • Control Type  : DocumentControl
  • Element Name  : Documentation
  • Class Name    : Gecko
  • Automation ID : 
  • Bounding Box  : (0, 78, 1920, 1002)
============================================================================
```

---

## 4. Next Steps & Evolution

* **Group by Tabstrip Container:** Separate top tab bars from sidebar extensions (e.g. Tree Style Tab / Sidebery).
* **Two-Tier Caching:** Avoid re-walking the tree on micro-focus events by updating the active tab via $O(1)$ window title matching against cached tab arrays.
