[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Research ](../../README.md#wayfinder-uia--threading-research) › **Educational Breakdown: Windows UIA, Threading, ...**

---

# Educational Breakdown: Windows UIA, Threading, and Focus in Neru

This document breaks down how the `neru` repository approaches Windows UI Automation (UIA), COM threading, and window focus management, referencing specific implementation patterns found in the codebase.

## 1. UIA Threading and COM Lifecycle

The UIA implementation is found primarily in `internal/adapter/accessibility/native/windows/automation.go`.

### Raw VTable Calls (No CGO)
To avoid the overhead and complexity of CGO on Windows, the project drives UI Automation through raw COM vtable syscalls. It defines vtable slot indices corresponding to `IUnknown`, `IUIAutomation`, `IUIAutomationElement`, and `IUIAutomationElementArray` and uses `syscall.SyscallN` to execute them.

### Multi-Threaded Apartment (MTA)
The code explicitly initializes COM in the Multi-Threaded Apartment (MTA).
`const coinitMultithreaded = 0x0`
**Why MTA?** The repository notes that UIA enumeration runs on background worker goroutines that do not pump Windows messages. Using a Single-Threaded Apartment (STA) without a message pump would lead to cross-process marshaling deadlocks. Microsoft officially recommends MTA for UIA calls made off the main UI thread.

### Thread Locking and Initialization
Because goroutines are multiplexed onto OS threads, the UIA enumeration strictly binds the current goroutine to its OS thread to keep the COM initialization stable:
```go
runtime.LockOSThread()
defer runtime.UnlockOSThread()

hresult, _, _ := procCoInitializeEx.Call(0, coinitMultithreaded)
if uint32(hresult) == hresultSOK || uint32(hresult) == hresultSFalse {
    defer func() { discardCall(procCoUninitialize.Call()) }()
}
```

### Encapsulation and Offline Trees
COM lifecycle is tightly contained. Objects are queried, their simple properties (like bounding rectangles and names) are copied into standard Go structs (`winElement`), and the COM objects are released immediately. No COM pointers ever escape `automation.go`. Consequently, `internal/adapter/accessibility/native/windows/tree.go` builds a "shallow" tree of structs with no live COM references. `ReleaseTree` is explicitly a no-op on Windows, completely avoiding memory leak risks associated with lingering COM references.

## 2. Window Focus Mechanisms

Window focus and layout properties are retrieved using standard `user32.dll` and `kernel32.dll` API calls, primarily encapsulated in `internal/adapter/platform/windows/win32.go`.

### Foreground Window Strategy
The adapter relies on `GetForegroundWindow()` to determine what the user is currently interacting with.

```go
func foregroundWindowHandle() (windows.HWND, error) {
    hwnd := windows.GetForegroundWindow()
    // ... validation checks ...
    desktop := windows.GetDesktopWindow()
    if hwnd == desktop {
        return 0, derrors.New(derrors.CodeElementNotFound, "desktop is focused")
    }
    return hwnd, nil
}
```
**Fallback & Validation Strategy:**
1. It validates that the handle actually exists (`hwnd == 0`).
2. It verifies the handle is still a valid window using `IsWindow(hwnd)`.
3. Crucially, it detects if the shell/desktop itself is focused (`GetDesktopWindow()`) and bubbles up a specific "element not found" domain error, avoiding attempts to draw hints over the desktop background.

### App Identity (PID and Image Path)
Once the foreground handle is obtained, the application PID is resolved via `GetWindowThreadProcessId`. 

To get the actual executable path (`bundleID`), the codebase uses a modern, robust fallback strategy:
```go
handle, err := windows.OpenProcess(processQueryLimitedInformation, false, uint32(pid))
```
Using `PROCESS_QUERY_LIMITED_INFORMATION` (0x1000) instead of full query rights allows the tool to successfully resolve the image name (via `QueryFullProcessImageName`) even for processes running at higher integrity levels, maximizing compatibility without requiring the agent itself to be run as Administrator.
