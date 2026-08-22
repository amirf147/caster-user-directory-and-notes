# Tab Extraction and Real-Time Context Representation (v2.1)

This document explains the architecture, mechanics, and terminal representation of **Version 2.1** of the Active Desktop Context Engine (ADCE) Proof of Concept.

---

## 1. Root Cause of Missing Tabs in VS Code & Waterfox

In initial testing, tabs were not appearing for VS Code (Electron) or Waterfox/Firefox due to two architectural traps in accessibility tree traversal:

1. **The Premature Pruning Trap:**
   - In VS Code (Electron) and Waterfox (Gecko), the entire application window UI is wrapped inside a top-level `DocumentControl` or `PaneControl`.
   - The initial version stopped recursing whenever it hit any `DocumentControl`, inadvertently aborting the search at depth 1 or 2 before ever reaching the tab bar.
2. **The Shallow Depth Limit & Root Window Anchor:**
   - In modern multi-pane applications, tabs are nested 6 to 10 layers deep under window panes and workbench containers.
   - If `GetForegroundControl()` returned an inner sub-element (like the editor text box), searching from that sub-element missed sibling tab bars.
   - **Fix:** In v2.1, the engine explicitly walks *up* to the true root application window first, and then traverses down with an expanded search depth (`max_depth=14`) using `auto.WalkControl()`.

---

## 2. Visual Terminal Representation

When running `scripts/context_poc.py` (or via voice with `"launch context engine"`), the terminal automatically updates into a clean dashboard:

```text
============================================================================
  ACTIVE DESKTOP CONTEXT ENGINE (ADCE) - LIVE MONITOR (v2.1)
============================================================================
 Timestamp    : 2026-08-22 03:08:00
 Event Trigger: FOCUS_CHANGED
 Active App   : Visual Studio Code (PID: 14820)
----------------------------------------------------------------------------
 WINDOW TABS:
  ► [ACTIVE] Tab 1: context_poc.py
    [      ] Tab 2: global_nonccr_extended.py
    [      ] Tab 3: 007_tab_extraction_and_context_representation.md
----------------------------------------------------------------------------
 ACTIVE CONTROL HIERARCHY TREE:
  ┌── [Window] Visual Studio Code
    └── [Pane] Workbench
      └── [Pane] Editor Group 1
        └── [Document] context_poc.py
          └── [Edit] Text Area  ◄ [FOCUSED NODE]
----------------------------------------------------------------------------
 FOCUSED ELEMENT DETAILS:
  • Control Type  : EditControl
  • Element Name  : Text Area
  • Automation ID : MonacoEditor
  • Bounding Box  : (Left=420, Top=120, Width=1500, Height=860)
  • Value Snippet : "def extract_window_tabs(top_window, focused_element=None):"
============================================================================

 [Listening for OS events... Press Ctrl+C in this terminal to exit]
```

---

## 3. Technical Mechanics in v2.1

### A. True Top-Level Window Anchor
```python
def get_top_level_window(ctrl):
    """Walk up from any control to find the true top-level application window."""
    root = auto.GetRootControl()
    curr = ctrl
    top = curr
    while curr:
        parent = curr.GetParentControl()
        if not parent or parent == root:
            top = curr
            break
        if curr.ControlType == auto.ControlType.WindowControl and (not parent or parent == root):
            top = curr
            break
        curr = parent
        top = curr
    return top
```

### B. Multi-Pattern Tab Detection
1. Checks for `ControlType.TabItemControl` or `ControlTypeName == "TabItem"`.
2. Inspects `SelectionItemPattern.IsSelected`, legacy accessible state (`STATE_SYSTEM_SELECTED = 0x4`), and `HasKeyboardFocus`.
3. Cleans application-specific noise (e.g. stripping VS Code's `, Editor Group 1` suffix and modified dot markers `● `).
4. Deduplicates adjacent proxy nodes.
