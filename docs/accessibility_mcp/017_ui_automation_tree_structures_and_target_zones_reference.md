<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2024-2026 Amir Farhadi -->

[ 🏠 Docs Home ](../README.md) › [ 📁 Accessibility MCP ](CONTEXT.md) › **017: UI Automation Tree Structures & Target Zones Reference (SSOT)**

---

# Single Source of Truth: UI Automation Tree Structures & Target Zones Reference (017)

> **Document Status:** Active / Master Architecture Reference  
> **Target Systems:** Active Desktop Context Engine (ADCE) & Caster Accessibility Engine  
> **Engines Tested:** C# .NET 10 (`FlaUI.UIA3 5.0.0`) & Python 3.10 (`uiautomation` / `ctypes`)  
> **Related Documents:** [010: Traversal Telemetry](010_telemetry_benchmarks_and_live_findings.md) | [014: C# Daemon Handover](014_csharp_daemon_handover_and_skill_spec.md) | [015: Epistemic Recalibration](015_recalibration_and_adversarial_architecture_review.md) | [016: Micro-Spike 2 Telemetry](016_micro_spike_2_win32_shallow_python_telemetry.md)

---

## 1. Master Desktop Target Matrix

This single source of truth details the exact UIA3 accessibility node hierarchies, control types, class names, automation IDs, depth offsets, and extraction rules discovered and empirically verified across the Windows desktop.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                             MASTER UI AUTOMATION DIRECTORY                                             │
├──────────────────────┬──────────────────────┬─────────────────────────┬──────────────────────┬─────────┬───────────────┤
│ Target Application   │ Window Class         │ Target Zone             │ Key Identifier       │ Depth   │ Latency       │
├──────────────────────┼──────────────────────┼─────────────────────────┼──────────────────────┼─────────┼───────────────┤
│ **Antigravity IDE /**│ `Chrome_WidgetWin_1` │ **Open Editor Tabs**    │ `Class:tabs-container│ D7 – D8 │ **~8–15 ms**  │
│ **VS Code / Monaco** │ (Electron)           │ **Activity Bar / View** │ `Class:actions-cont` │ D6 – D7 │ **~5–10 ms**  │
│                      │                      │ **File Breadcrumbs**    │ `Class:monaco-breadc`│ D7 – D8 │ **~5–8 ms**   │
│                      │                      │ **Active Code Buffer**  │ `Class:native-edit-c`│ D8 – D9 │ **~3–5 ms**   │
│                      │                      │ **Git Commit Box**      │ `Name:Message (Ctrl+`│ D8 – D9 │ **~3–5 ms**   │
│                      │                      │ **Status Bar & Branch** │ `AutoId:workbench...`│ D6 – D7 │ **~3–6 ms**   │
├──────────────────────┼──────────────────────┼─────────────────────────┼──────────────────────┼─────────┼───────────────┤
│ **Waterfox / Firefox**│ `MozillaWindowClass`│ **Tree Style Tabs**     │ `Class:tabs normal`  │ D6 – D8 │ **~8–12 ms**  │
│ *(Gecko)*            │                      │ **Pinned Sidebar Tabs** │ `Class:tabs pinned`  │ D6 – D8 │ **~3–5 ms**   │
│                      │                      │ **Native Tabstrip**     │ `Class:tabbrowser...`│ D5 – D7 │ **~5–10 ms**  │
│                      │                      │ **URL Address Bar**     │ `AutoId:urlbar-input`│ D6 – D7 │ **~2–4 ms**   │
│                      │                      │ **Page DOM Viewport**   │ `ControlType:Document│ D10–D25 │ **DO NOT SCAN │
├──────────────────────┼──────────────────────┼─────────────────────────┼──────────────────────┼─────────┼───────────────┤
│ **File Explorer**    │ `CabinetWClass`      │ **Win11 Tabstrip**      │ `AutoId:TabView`     │ D3 – D4 │ **~3–6 ms**   │
│ *(WinUI 3 / XAML)*   │                      │ **Address & Path**      │ `AutoId:PART_Breadc` │ D3 – D4 │ **~2–4 ms**   │
│                      │                      │ **Command Bar Actions** │ `AutoId:FileExplorer`│ D3 – D4 │ **~2–4 ms**   │
│                      │                      │ **Shell File List**     │ `AutoId:Items View`  │ D5 – D7 │ **~5–12 ms**  │
├──────────────────────┼──────────────────────┼─────────────────────────┼──────────────────────┼─────────┼───────────────┤
│ **Windows Terminal** │ `CASCADIA_HOSTING_..`│ **Terminal Tabs**       │ `ControlType:Tab`    │ D3 – D4 │ **~2–5 ms**   │
│ **& Command Prompt** │ `ConsoleWindowClass` │ **Active Buffer**       │ `ControlType:Document│ D1 – D2 │ **< 1 ms**    │
└──────────────────────┴──────────────────────┴─────────────────────────┴──────────────────────┴─────────┴───────────────┘
```

---

## 2. Antigravity IDE & VS Code (`Chrome_WidgetWin_1`)

Electron / Monaco IDEs structure the user interface into distinct workbench parts inside a top-level `Document` (`RootWebArea`).

### Root Hierarchy Anatomy:
```
[D0] Window: 0x00DB083E (Class: 'Chrome_WidgetWin_1', Title: 'caster - Antigravity IDE')
 └── [D1] Pane: (Class: 'RootView')
      └── [D2] Pane: (Class: 'NonClientView')
           └── [D3] Pane: (Class: 'ClientView')
                └── [D4] Document: AutoId='RootWebArea' (Class: '')
                     ├── [D5] Tab: AutoId='' Class='actions-container' Name='Active View Switcher'  ◄ (Activity Bar)
                     ├── [D5] Group: AutoId='workbench.parts.sidebar' Class='part sidebar'         ◄ (Sidebar / File Tree)
                     ├── [D5] Group: AutoId='workbench.parts.editor' Class='part editor'           ◄ (Editor Area)
                     │    ├── [D6] Group: AutoId='' Class='editor-group-container'
                     │    │    ├── [D7] Tab: AutoId='' Class='tabs-container'                      ◄ (OPEN TABS STRIP)
                     │    │    │    ├── [D8] TabItem: Class='tab ... active selected'              ◄ (Active Tab)
                     │    │    │    └── [D8] TabItem: Class='tab ...'                              ◄ (Open Inactive Tabs)
                     │    │    ├── [D7] List: AutoId='' Class='monaco-breadcrumbs'                 ◄ (ACTIVE FILE DISK PATH)
                     │    │    │    └── [D8] ListItem: Class='folder / file monaco-breadcrumb-item'
                     │    │    └── [D7] Group: AutoId='' Class='editor-instance'
                     │    │         └── [D8] Text: AutoId='' Class='monaco-editor'
                     │    │              └── [D9] Edit: Class='native-edit-context'                ◄ (CODE BUFFER / CARET)
                     ├── [D5] Group: AutoId='workbench.parts.panel' Class='part panel'             ◄ (Terminal / Output)
                     └── [D5] StatusBar: AutoId='workbench.parts.statusbar' Class='part statusbar' ◄ (Git Branch / Mode)
```

### Zone Breakdown & Query Rules:

#### 1. Open Editor Tabstrip
* **Target Container:** `ControlType: Tab` with `ClassName: "tabs-container"` (Depth 7).
* **Pitfall Warning:** Never query `FindFirstDescendant(ByControlType(ControlType.Tab))` directly without checking `ClassName`. In VS Code, the first `Tab` control is the Activity Bar (`actions-container`), NOT the editor tabs!
* **Child Tab Nodes:** Direct children of `tabs-container` are `ControlType.TabItem`.
  * **Tab Title:** `tab.Properties.Name` (e.g. `'CacheRequest.cs'`, `'016_micro_spike_2...md'`).
  * **Active Status:** `tab.Properties.ClassName` contains `"active selected"` (or `SelectionItem.IsSelected == true`).
  * **Preview / Dirty Flag:** Title suffix contains `", preview"` or tab label prefix contains `"● "`.

#### 2. Active Sidebar View & Activity Bar
* **Target Container:** `ControlType: Tab` with `ClassName: "actions-container"` and `Name: "Active View Switcher"` (Depth 5–6).
* **Active View Detection:** Enumerate child `TabItem` elements. The active sidebar has `ClassName` containing `"checked"`:
  * `'Explorer (Ctrl+Shift+E)'`
  * `'Source Control (Ctrl+Shift+G) - X pending changes'`
  * `'Code Search (Ctrl+Shift+F)'`
  * `'Run and Debug (Ctrl+Shift+D)'`

#### 3. Active File Disk Breadcrumbs
* **Target Container:** `ControlType: List` with `ClassName: "monaco-breadcrumbs"` (Depth 7).
* **Path Reconstruction:** Children are `ControlType.ListItem` nodes with `ClassName: "... monaco-breadcrumb-item"`. Joining their names with `\` reconstructs the full workspace-relative or absolute file path (e.g. `C:\Users\<User>\Documents\repos\FlaUI\src\FlaUI.Core\CacheRequest.cs`).

#### 4. Monaco Text Editor & Edit Context
* **Target Container:** `ControlType.Edit` with `ClassName: "native-edit-context"` (Depth 8–9).
* **Capabilities:**
  * `Name`: Active file name and buffer status (`"CacheRequest.cs, preview"`).
  * `ValuePattern` / `TextPattern`: Exposes active editor text buffer and caret position.

#### 5. Git Commit Box & Focus Detection
* When user focus is in the Source Control commit box, the active `Edit` control has:
  * `Name`: `'Message (Ctrl+Enter to commit on "branch-name"), Use Alt+F1 to open Source Control Accessibility Help.'`
  * `ControlType`: `ControlType.Edit`

---

## 3. Waterfox & Firefox (`MozillaWindowClass`)

Modern Firefox-family browsers isolate browser chrome from web page content. When using sidebar extensions (e.g. Tree Style Tab), tabs live in an isolated iframe.

### Root Hierarchy Anatomy:
```
[D0] Window: 0x02860F44 (Class: 'MozillaWindowClass', Title: 'UIA Fallback - Google Gemini — Waterfox')
 └── [D1] Pane: AutoId='' Class='MozillaCompositorInitialParentClass'
      └── [D2] Pane: AutoId='main-window'
           ├── [D3] ToolBar: AutoId='nav-bar' Class='toolbar'
           │    └── [D4] Edit: AutoId='urlbar-input' Class='' Name='Search with Google or enter address' ◄ (URL INPUT)
           ├── [D3] Pane: AutoId='sidebar-box' Class='chromeclass-extrachrome' ◄ (SIDEBAR EXTENSION CONTAINER)
           │    └── [D4] Document: AutoId='' Class='' Name='Tree Style Tab'
           │         ├── [D5] List: AutoId='window-7-pinned' Class='tabs pinned' ◄ (PINNED TABS)
           │         │    └── [D6] ListItem: ...
           │         └── [D5] List: AutoId='window-7' Class='tabs normal'       ◄ (OPEN TABS LIST)
           │              ├── [D6] ListItem: Name='UIA Fallback - Google Gemini 1' [ACTIVE]
           │              ├── [D6] ListItem: Name='AI Enhances Job Application 2'
           │              └── [D6] ListItem: Name='Extracting truth from LLM 3'
           └── [D3] Document: AutoId='' Class='' Name='UIA Fallback...'         ◄ (WEB PAGE DOM VIEWPORT)
                └── [D4..D25] 6,800+ DOM Nodes (HTML, DIV, SVG, BUTTON...)      ◄ (THE DOM TRAP: PRUNE!)
```

### Zone Breakdown & Query Rules:

#### 1. Tree Style Tab Normal Tabs
* **Target Container:** `ControlType: List` with `ClassName: "tabs normal"` (or `AutomationId: "window-*"`).
* **Child Tab Nodes:** Direct children are `ControlType.ListItem` (Depth 6–8).
* **Active Status:** `item.Patterns.SelectionItem.PatternOrDefault.IsSelected == true`.
* **Title:** Direct `item.Properties.Name.Value` (e.g. `'UIA Fallback and Win32 Focus - Google Gemini 1'`).

#### 2. Tree Style Tab Pinned Tabs
* **Target Container:** `ControlType: List` with `ClassName: "tabs pinned"` (or `AutomationId: "window-*-pinned"`).

#### 3. Standard Native Firefox Tabstrip (Without Sidebar)
* **Target Container:** `ControlType: Tab` with `ClassName: "tabbrowser-tabs"` (or `AutomationId: "TabsToolbar"`).
* **Child Tab Nodes:** Direct children are `ControlType.TabItem`.

#### 4. The Browser DOM Trap (Pruning Rule)
> [!CAUTION]
> **Never Traverse Web Page Viewports:**  
> The web page content viewport is represented as a top-level `ControlType.Document` sibling of `nav-bar` and `sidebar-box`. Descending into this `Document` crawls all 6,800+ HTML DOM elements across cross-process COM LPC, triggering **5,800 ms** freezes.  
> **Rule:** Prune any `ControlType.Document` that is NOT named `"Tree Style Tab"` or inside `sidebar-box`.

---

## 4. Windows 11 File Explorer (`CabinetWClass`)

Windows 11 File Explorer is rendered via WinUI 3 XAML Islands hosted inside the classic `CabinetWClass` frame.

### Root Hierarchy Anatomy:
```
[D0] Window: 0x013A04E2 (Class: 'CabinetWClass', Title: 'Caster - File Explorer')
 └── [D1] Pane: Class='ShellTabWindowClass'
      └── [D2] Pane: Class='InputSiteWindowClass'
           ├── [D3] Tab: AutoId='TabView' Class='Microsoft.UI.Xaml.Controls.TabView' ◄ (WIN11 TABS)
           │    └── [D4] List: AutoId='TabListView' Class='ListView'
           │         ├── [D5] TabItem: Class='ListViewItem' Name='Caster' [ACTIVE]
           │         └── [D5] TabItem: Class='ListViewItem' Name='repos'
           ├── [D3] Group: AutoId='PART_AutoSuggestBox' Class='AutoSuggestBox'
           │    └── [D4] Edit: AutoId='TextBox' Name='Address Bar'                   ◄ (RAW PATH EDIT BOX)
           ├── [D3] Group: AutoId='PART_BreadcrumbBar' Class='LandmarkTarget'        ◄ (PATH BREADCRUMBS)
           │    ├── [D4] SplitButton: Name='This PC'
           │    ├── [D4] SplitButton: Name='Windows (C:)'
           │    ├── [D4] SplitButton: Name='Users'
           │    ├── [D4] SplitButton: Name='<User>'
           │    └── [D4] SplitButton: Name='Documents'
           ├── [D3] AppBar: AutoId='FileExplorerCommandBar' Class='ApplicationBar'  ◄ (RIBBON ACTIONS)
           │    ├── [D4] Button: Name='New'
           │    ├── [D4] Button: Name='Cut'
           │    ├── [D4] Button: Name='Copy'
           │    └── [D4] Button: Name='Delete'
           └── [D3] Pane: AutoId='ExplorerBrowserControl' Class='ExplorerBrowserControl'
                └── [D4] List: AutoId='Items View' Class='UIItemsView'               ◄ (FILE/FOLDER LIST)
                     ├── [D5] ListItem: Name='rules'
                     ├── [D5] ListItem: Name='scripts'
                     └── [D5] ListItem: Name='README.md'
```

### Zone Breakdown & Query Rules:

#### 1. Win11 Explorer Tabs
* **Target Container:** `ControlType: Tab` with `AutomationId: "TabView"` (Depth 3).
* **Items List:** `tabContainer.FindFirstDescendant(cf.ByAutomationId("TabListView"))`.
* **Child Nodes:** `ControlType.TabItem` with `ClassName: "ListViewItem"`.

#### 2. Address & Breadcrumb Path
* **Direct Path String:** Read `AutoId: "TextBox"` inside `PART_AutoSuggestBox`.
* **Path Hierarchy:** Enumerate child `SplitButton` elements under `AutoId: "PART_BreadcrumbBar"`.

#### 3. Selected / Visible Files
* **Target Container:** `ControlType: List` with `AutomationId: "Items View"`.
* **Selected Items:** Check `SelectionItem.IsSelected` on child `ListItem` elements to know exactly what file or directory the user is focused on.

---

## 5. Summary of Recommended Query Recipes

### C# FlaUI 5 Query Patterns:

```csharp
// 1. Antigravity / VS Code Editor Tabs
public static List<string> GetVSCodeTabs(AutomationElement window)
{
    var cf = window.Automation.ConditionFactory;
    var tabstrip = window.FindFirstDescendant(cf.ByClassName("tabs-container"));
    if (tabstrip == null) return new();

    return tabstrip.FindAllChildren(cf.ByControlType(ControlType.TabItem))
                   .Select(t => t.Properties.Name.ValueOrDefault)
                   .Where(name => !string.IsNullOrEmpty(name))
                   .ToList();
}

// 2. Waterfox Tree Style Tab Extraction
public static List<string> GetWaterfoxTabs(AutomationElement window)
{
    var cf = window.Automation.ConditionFactory;
    var tabList = window.FindFirstDescendant(cf.ByClassName("tabs normal"));
    if (tabList == null) return new();

    return tabList.FindAllChildren(cf.ByControlType(ControlType.ListItem))
                  .Select(t => t.Properties.Name.ValueOrDefault)
                  .Where(name => !string.IsNullOrEmpty(name))
                  .ToList();
}

// 3. Windows 11 File Explorer Tabs
public static List<string> GetExplorerTabs(AutomationElement window)
{
    var cf = window.Automation.ConditionFactory;
    var tabView = window.FindFirstDescendant(cf.ByAutomationId("TabListView"));
    if (tabView == null) return new();

    return tabView.FindAllChildren(cf.ByControlType(ControlType.TabItem))
                  .Select(t => t.Properties.Name.ValueOrDefault)
                  .ToList();
}
```

---

## 6. Document History & Lineage
* **Document 010:** Discovered 5,800 ms DOM crawling traps over recursive COM walks.
* **Document 015:** Formulated the 4-gate epistemic protocol to prevent unverified solutions.
* **Document 016:** Empirically verified that shallow context executes in **0.66 ms** in Python 3.10.
* **Document 017 (This Document):** Codified the definitive, ground-truth structural maps and container queries for Antigravity IDE, Waterfox, and File Explorer.
