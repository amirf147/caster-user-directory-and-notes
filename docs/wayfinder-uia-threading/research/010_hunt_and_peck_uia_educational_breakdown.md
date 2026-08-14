[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Research ](../../README.md#wayfinder-uia--threading-research) › **Hunt and Peck: UIA Educational Breakdown**

---

# Hunt and Peck: UIA Educational Breakdown

This document provides a detailed architectural breakdown of the **Hunt and Peck** codebase, specifically focusing on its approach to Windows UI Automation (UIA), COM threading, window focus mechanisms, and fallback strategies.

## 1. Architectural Approach to UI Automation (UIA)
Hunt and Peck uses the **native COM-based `UIAutomationClient` API** via COM Interop (instantiating `CUIAutomation`) rather than the managed `System.Windows.Automation` namespace. This is generally preferred for performance and reliability across newer UI frameworks.

- **Querying the Tree**: 
  When a hotkey is triggered, the app grabs the handle of the active window using `GetForegroundWindow()`.
  It sets up a condition to find elements that are `IsOffscreen == false` and `IsEnabled == true` and match the `ControlViewCondition`.
  It uses `FindAll(TreeScope.TreeScope_Descendants, ...)` to aggressively fetch all actionable elements in one synchronous call.
- **Coordinate Mapping**: 
  For each returned element, its physical `CurrentBoundingRectangle` is mapped to logical coordinates (to support DPI scaling) and translated to the overlay window's coordinates so the hint labels can be positioned accurately.

## 2. COM Threading and Lifecycle (STA vs MTA)
The application handles COM threading using the **Single-Threaded Apartment (STA)** model, which is standard for WPF and WinForms applications.
- The `UiAutomationHintProviderService` initializes the `CUIAutomation` COM object natively on the application's main STA thread.
- **Message Pump**: The global hotkeys are registered (`RegisterHotKey`) using a hidden WinForms `Form` (`KeyListenerService`). When the hotkey message (`WM_HOTKEY`) is received in the `WndProc` loop on the main STA thread, it directly calls `EnumHints()`.
- Because the hotkey is processed on the main UI thread, UIA querying is entirely synchronous. The STA model guarantees thread safety for UI elements but risks blocking the main UI thread during heavy `FindAll` operations.

## 3. Window Focus Mechanisms
A major challenge in Windows is that background applications cannot simply steal focus or pop to the foreground without user interaction. Hunt and Peck implements a robust workaround in `ForegroundWindow.cs`:
- It first attempts a standard `User32.SetForegroundWindow()`.
- **Thread Attachment Hack**: If standard foregrounding fails, it relies on the `AttachThreadInput` trick:
  1. It gets the thread ID of the current foreground window (`User32.GetWindowThreadProcessId`).
  2. It gets its own thread ID (`Kernel32.GetCurrentThreadId`).
  3. It temporarily links its thread's input processing to the target window's thread via `User32.AttachThreadInput(targetThread, appThread, true)`.
  4. With shared input state, it can now successfully call `User32.BringWindowToTop()` and `User32.SetFocus()` on its own handle, successfully circumventing OS anti-focus-stealing protections.
  5. It immediately un-attaches the threads.

## 4. Fallback Strategies (UIA Patterns)
Not all UI elements support a simple "Click" action. To ensure broad compatibility, the codebase uses a factory pattern (`CreateHint` in `UiAutomationHintProviderService`) to test UIA elements against multiple patterns in a strict priority order. When an element is matched, a specific `Hint` subclass is returned that encapsulates the correct execution method:
1. **`InvokePattern`**: The most direct mapping to a click. Returns `UiAutomationInvokeHint`.
2. **`TogglePattern`**: Commonly used for checkboxes/switches. Returns `UiAutomationToggleHint` (calls `.Toggle()`).
3. **`SelectionItemPattern`**: For lists and dropdowns. Returns `UiAutomationSelectHint` (calls `.Select()`).
4. **`ExpandCollapsePattern`**: For accordions or tree nodes. Returns `UiAutomationExpandCollapseHint` (calls `.Expand()` or `.Collapse()` based on current state).
5. **`ValuePattern` / `RangeValuePattern`**: If none of the above are matched, but the element supports values and is **not read-only** (`CurrentIsReadOnly == 0`), it falls back to creating a `UiAutomationFocusHint`, which simply calls `.SetFocus()` on the element to let the user type into it.
