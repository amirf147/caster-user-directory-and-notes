[ 🏠 Docs Home ](../README.md) › [ 📁 Accessibility MCP ](CONTEXT.md) › **013: Empirical Post-Mortem & Event Diagnostics**

---

# ADCE v2.3 Empirical Post-Mortem & WinEvent Diagnostics (013)

> **Document Status:** Active / Diagnostic Analysis  
> **Target System:** Active Desktop Context Engine (ADCE v2.3 POC)  
> **Related Documents:** [007: Tab Extraction](007_tab_extraction_and_context_representation.md) | [010: Telemetry Benchmarks](010_telemetry_benchmarks_and_live_findings.md) | [012: Tab Extraction Benchmark](012_empirical_tab_extraction_report.md)

---

## 1. Executive Summary & Core Diagnosis

During live interactive testing of **ADCE v2.3**, several critical regressions and behavioral anomalies were observed:
1. **Tree Style Tab / Waterfox Regression:** Waterfox with Tree Style Tab (26+ tabs open) only reported **2 false tabs** (`"Add tab to taskbar"` and `"Tree Style Tab"`), whereas v2.2 discovered all 41 tabs.
2. **Terminal Self-Monitoring & Feedback Loops:** Clicking or focusing the console caused ADCE to capture its own terminal window (`"ADCE Live Context Monitor"`) and trigger rapid redraw loops.
3. **Transition Freezes & Dropped Focus Events:** Switching into Microsoft Edge or Waterfox caused the monitor to freeze or take a stale snapshot, failing to update as the user navigated.
4. **Test Harness Blind Spots:** The non-interactive test harness (`test_tab_benchmark.py`) passed superficial checks by measuring only latency and non-zero counts, masking the fact that 5 Antigravity IDE windows returned 0 tabs and Waterfox returned toolbar buttons rather than browser tabs.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                ADCE EVOLUTION & REGRESSION MATRIX                      │
├─────────┬──────────────────────┬─────────────┬─────────────┬───────────────────────────┤
│ Version │ Strategy             │ Latency     │ Tabs Found  │ Failure Modes             │
├─────────┼──────────────────────┼─────────────┼─────────────┼───────────────────────────┤
│ **v2.1**│ Top-Down Unbounded   │ 120-750 ms  │ Incomplete  │ Missed Electron editors   │
│ **v2.2**│ Deep Unpruned Walk   │ 5,897 ms    │ 41 tabs     │ Severe DOM traversal lag  │
│ **v2.3**│ Blanket DOM Pruning  │ 113 ms      │ 2 tabs ❌   │ Cut off Tree Style Tab    │
│ **v2.4**│ Container-Targeted   │ < 50 ms     │ All tabs ✅ │ Dual-plane async pipeline │
└─────────┴──────────────────────┴─────────────┴─────────────┴───────────────────────────┘
```

---

## 2. Why Waterfox Dropped from 41 Tabs to 2 (The Pruning Paradox)

### The Underlying Tree Style Tab Architecture
In Firefox/Waterfox with the **Tree Style Tab (TST)** or **Sidebery** extension:
* The default horizontal XUL tabstrip is typically hidden.
* All open tabs (e.g., *Documentation Portal*, *Web Search*, *Technical Specifications*, etc.) are rendered inside a WebExtension sidebar panel.
* Windows UI Automation exposes this sidebar panel as a **`DocumentControl`** embedded inside an internal browser iframe.

### The v2.2 vs v2.3 Structural Divergence

```
                   [MozillaWindowClass: Waterfox]
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼                                               ▼
 [Top Navigation Chrome]                    [Web Viewport & Extension Sidebars]
 • "Add tab to taskbar" (Button)            • Main Page (DocumentControl)
 • "Tree Style Tab" (Sidebar Toggle)        • Tree Style Tab Sidebar (DocumentControl)
        │                                               │
        │                                   ┌───────────┴───────────┐
        │                                   ▼                       ▼
        │                            [Page Content]          [26+ Tab Elements]
        │                            (1000s of DOM nodes)    (Tab 1, Tab 2, ... Tab 26)
        │                                   │                       │
        │                                   ▼                       ▼
   v2.3 Scanned:                     v2.3 Blanket Prune:     v2.3 Blanket Prune:
   Captured 2 Buttons ❌             Pruned ✅ (Good)        Pruned ❌ (Tab Loss)
   (113 ms latency)                  (Saved 5.7s)            (Reported 2 false tabs)
```

1. **In v2.2 (Unpruned Deep Walk):**
   * The tree walker traversed recursively through all nodes.
   * It descended into the `DocumentControl` of the Tree Style Tab sidebar, successfully discovering all **41 tabs**.
   * **Cost:** It also traversed the active web page's DOM, crawling **6,806 nodes** and taking **5,897 ms** (~5.9 seconds).

2. **In v2.3 (Blanket `DocumentControl` Pruning):**
   * To solve the 5.9-second latency, `walk_control_pruned` introduced a blanket rule:
     ```python
     prune_types = (auto.ControlType.DocumentControl,) if ("Mozilla" in hwnd_class or is_electron) else ()
     ```
   * The instant the walker encountered any `DocumentControl`, it severed that subtree entirely.
   * **Result:** It avoided crawling the web page DOM (reducing scan count to 107 nodes and latency to 113 ms), but **it completely severed the Tree Style Tab sidebar**.
   * The only elements matching the name `"tab"` in the remaining top-level chrome were:
     1. `Tab 1: Add tab to taskbar` (a toolbar action button)
     2. `Tab 2: Tree Style Tab` (the sidebar toggle button)
   * The benchmark erroneously reported `"Tabs Found: 2"` as a working extraction.

---

## 3. Educational Breakdown: The 4 Root Causes of Flashing, Freezing & Self-Monitoring

### Bug 1: Console Self-Monitoring & Process Boundary Leaks
* **Mechanism:** `context_poc.py` initializes WinEvent hooks with `WINEVENT_SKIPOWNPROCESS`.
* **The Leak:** When executed inside Windows Terminal (`WindowsTerminal.exe`), PowerShell Console Host (`conhost.exe`), or VS Code's integrated terminal, the UI belongs to the **terminal host process**, not the child Python interpreter (`python.exe`).
* **Symptom:** Clicking the console, resizing it, or interacting with its title bar fires `EVENT_SYSTEM_FOREGROUND` and `EVENT_OBJECT_FOCUS`. ADCE captures its own terminal window, clears the screen, redraws itself, and enters a self-monitoring cycle.

### Bug 2: Synchronous UIA Blocking on the OS WinEvent Thread
* **Mechanism:** `win_event_handler` executes directly on the Windows message pump thread (`GetMessageW`).
* **The Stall:** Inside the callback, `auto.GetFocusedControl()` makes cross-process COM calls (`IUIAutomation::GetFocusedElement()`).
* **Symptom:** When clicking into Edge or Waterfox, the browser's UI thread is actively switching rendering contexts. The synchronous COM call blocks until the target application yields, causing the terminal to freeze or stutter during transitions.

### Bug 3: Leading-Edge Debounce Dropping Valid Focus Events
* **Mechanism:** `context_poc.py` implements a simple time-delta gate:
  ```python
  now = time.time()
  if now - last_event_time < 0.05:
      return
  last_event_time = now
  ```
* **The Race:** When switching from the terminal to Edge:
  1. At $t = 0\text{ ms}$, the OS fires `EVENT_SYSTEM_FOREGROUND` (Edge window activates).
  2. At $t = 15\text{ ms}$, the OS fires `EVENT_OBJECT_FOCUS` on Edge's internal document / tab canvas.
* **The Failure:** The first event ($t = 0$) executes during the transition (often reading incomplete or intermediate state). The second event ($t = 15\text{ ms}$) is **silently dropped** by the 50 ms debounce gate.
* **Symptom:** The monitor remains frozen with the initial partial snapshot and never updates to the focused document.

### Bug 4: HWND Resolution Fallback to Foreground Window
* **Mechanism:** In Chromium and Gecko, internal accessibility nodes often return `NativeWindowHandle = 0`.
* **The Fallback:** When `NativeWindowHandle` is 0, `get_top_level_window_info()` falls back to `user32.GetForegroundWindow()`.
* **Symptom:** If a focus event fires while the foreground window transition is still settling, `GetForegroundWindow()` returns the previous active window (the Console). The engine attributes the focus event to the wrong application.

---

## 4. Re-Evaluating the Test Harness Methodology

The previous test script (`test_tab_benchmark.py`) exhibited four structural flaws:

| Flaw | Test Harness Implementation | Real-World Impact |
| :--- | :--- | :--- |
| **Static Snapshots** | Iterated `EnumDesktopWindows` in a background thread without user interaction. | Never exercised `EVENT_OBJECT_FOCUS`, debounce timing, or cross-process message pumps. |
| **Bypassed Bottom-Up Extraction** | Passed `focused_element=None` to `extract_window_tabs()`. | Masked that **5 out of 5 Antigravity IDE windows returned 0 tabs**. |
| **Superficial Success Metric** | Asserted `tabs_found > 0` without validating tab identity. | Counted toolbar buttons (`"Add tab to taskbar"`) as successful browser tabs. |
| **No Ground-Truth Baseline** | No validation against known open documents or active browser URLs. | Reported false positives as architectural breakthroughs. |

---

## 5. Architectural Remediation Plan (v2.4)

### 1. Targeted Container Walk (Dual-Plane Pruning)
Instead of blanket pruning all `DocumentControl` elements:
* **For Standard Browsers (Chrome / Edge / Firefox Default):** Locate the dedicated tabstrip container (`TabControl` / `PaneControl` with class `Chrome_RenderWidgetHostHWND` or `browser-tabs`) and walk only that subtree.
* **For Sidebar Extensions (Tree Style Tab / Sidebery):** Identify the sidebar container by its automation ID or role, and restrict the walk strictly to the sidebar list while pruning the main page viewport `DocumentControl`.

### 2. Terminal Self-Filtering
* Filter out `GetConsoleWindow()` and the parent process tree (`WindowsTerminal.exe`, `conhost.exe`) explicitly in `win_event_handler`.

### 3. Decoupled Asynchronous Queue & Trailing-Edge Debounce
* Move all UIA inspection and tree walking off the WinEvent callback thread into a dedicated worker thread.
* Replace the leading-edge drop with a **trailing-edge debounce timer** (e.g. 75 ms), ensuring the engine always evaluates the *final settled state* rather than the initial transition event.

### 4. Ground-Truth Test Harness
* Upgrade `test_tab_benchmark.py` to assert expected tab counts against known open workspaces and validate tab names against active window titles.
