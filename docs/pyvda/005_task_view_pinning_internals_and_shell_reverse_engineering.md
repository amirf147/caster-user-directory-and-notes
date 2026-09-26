# Task View Pinning Internals & Windows Shell Reverse Engineering

## 1. Overview & Problem Definition

This document records the reverse engineering of Windows Shell's virtual desktop pinning subsystem within `twinui.pcshell.dll` (Windows 11 Build 26200). It establishes the native mechanics of Task View, examines why `IVirtualDesktopPinnedApps::PinAppID` fails on modern applications, and validates the multi-window synchronization model implemented in `pyvda` Pull Request #59.

The investigation answers two specific architectural questions:
1. Does Windows provide an undocumented public or private API that natively handles multi-window XAML Island pinning without view enumeration?
2. How does Windows Task View ("Show windows from this app on all desktops") handle these windows internally?

---

## 2. API Surface & Vtable Analysis

Public Win32 documentation specifies `IVirtualDesktopManager` (`shobjidl_core.h`) as the sole virtual desktop interface. This interface exposes only three methods:
* `IsWindowOnCurrentVirtualDesktop`
* `GetWindowDesktopId`
* `MoveWindowToDesktop`

All pinning behavior is relegated to internal COM interfaces hosted within `explorer.exe`. Inspection of the Microsoft symbol database (`twinui.pcshell.pdb`) for class `VirtualPinnedAppsHandler` reveals the full runtime vtable:

### Table 1: VirtualPinnedAppsHandler Vtable Layout

| Slot | Offset | Interface | Method Symbol | Description |
| :--- | :--- | :--- | :--- | :--- |
| 0 | `0x00` | `IUnknown` | `QueryInterface` | Standard COM interface query |
| 1 | `0x08` | `IUnknown` | `AddRef` | Reference counter increment |
| 2 | `0x10` | `IUnknown` | `Release` | Reference counter decrement |
| 3 | `0x18` | `IVirtualDesktopPinnedApps` | `IsAppIdPinned` | Checks registry/vector for exact string match |
| 4 | `0x20` | `IVirtualDesktopPinnedApps` | `PinAppID` | Writes ID to registry, queries views, calls `PinViewInternal` |
| 5 | `0x28` | `IVirtualDesktopPinnedApps` | `UnpinAppID` | Deletes ID from registry, unpins views |
| 6 | `0x30` | `IVirtualDesktopPinnedApps` | `IsViewPinned` | Queries in-memory view pinned state |
| 7 | `0x38` | `IVirtualDesktopPinnedApps` | `PinView` | Sets per-window in-memory pinned flag |
| 8 | `0x40` | `IVirtualDesktopPinnedApps` | `UnpinView` | Clears per-window in-memory pinned flag |
| 9 | `0x48` | `IVirtualDesktopPinnedAppsPrivate` | `SetViewCollectionInternal` | Injects `IApplicationViewCollection` pointer |
| 10 | `0x50` | `IVirtualDesktopPinnedAppsPrivate` | `ViewAddedInternal` | Evaluates new views on creation against pinned list |
| 11 | `0x58` | `IVirtualDesktopPinnedAppsPrivate` | `ViewAppIdChangedInternal` | Re-evaluates views when Application ID changes |

No auxiliary pinning methods or wildcard interfaces exist on this class or within the `twinui.pcshell.dll` service provider registry.

---

## 3. Disassembly: Native Task View Execution Path

When an application thumbnail is right-clicked in Task View and "Show windows from this app on all desktops" is selected, the shell dispatches to `DesktopTaskGroupsSwitchItemController::PinUnpinToAllDesktops` (`RVA 0x1805bfb74`):

```x86asm
; Locate window handles belonging to the task group
0x1805bfbef: call SnapAssistSnappedWindows
0x1805bfbf5: mov  r15, qword ptr [rbp - 0x10] ; Pointer to window list
0x1805bfc03: cmp  r15, r12                   ; Bounds check
0x1805bfc06: je   0x1805bfc91

; Iteration loop across all HWND instances
0x1805bfc10: mov  ebx, dword ptr [r14]        ; Current HWND
0x1805bfc2c: mov  edx, ebx
0x1805bfc2e: lea  r8, [rbp + 0x40]
0x1805bfc35: call qword ptr [rax + 0x30]      ; GetViewForHwnd
0x1805bfc5b: mov  rcx, qword ptr [r13 + 0x28] ; PinnedAppsHandler pointer
0x1805bfc66: test r15b, r15b                  ; IsTaskGroupPinned evaluation
0x1805bfc69: je   0x1805bfc71
0x1805bfc6b: mov  rax, qword ptr [rax + 0x40] ; Slot 8: UnpinView
0x1805bfc6f: jmp  0x1805bfc75
0x1805bfc71: mov  rax, qword ptr [rax + 0x38] ; Slot 7: PinView
0x1805bfc75: call rax                         ; Invoke PinView on view
0x1805bfc84: add  r14, 4                      ; Advance to next HWND
0x1805bfc88: cmp  r14, r12
0x1805bfc8b: jne  0x1805bfc10                 ; Repeat for all group windows
```

### Architectural Takeaway
Task View does not rely on `PinAppID` to propagate state to open windows. Instead, it enumerates the window collection belonging to the application or task group and invokes `PinView` individually on each view.

---

## 4. Disassembly: String Comparison Failure in `PinAppID`

`VirtualPinnedAppsHandler::PinAppID` (`RVA 0x180598c90`) persists the AppID string to `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VirtualDesktops\PinnedApps` and queries the view manager:

```x86asm
0x180598e14: mov  rcx, qword ptr [rdi + 0x50] ; IApplicationViewCollection
0x180598e29: mov  rax, qword ptr [rax + 0x28] ; Slot 5: GetViewsByAppUserModelId
0x180598e2d: call rax
```

`GetViewsByAppUserModelId` routes to `CApplicationViewManager::GetApplicationViewsById`, which iterates all active views and calls `IApplicationView::IsEqualByAppUserModelId` (`RVA 0x180130ba0`):

```x86asm
0x180130bd4: mov  rcx, qword ptr [rcx + 0xd8] ; Stored view AUMID
0x180130c37: mov  dword ptr [rsp + 0x20], 1   ; Case-insensitive flag
0x180130c3f: mov  r8, rbx                     ; Target AppID argument
0x180130c42: call CompareStringOrdinal        ; Kernel string comparison
0x180130c50: cmp  eax, 2                      ; CSTR_EQUAL == 2
0x180130c53: sete cl                          ; Set boolean match result
```

`CompareStringOrdinal` is invoked with length parameters `-1` and `-1`. It requires full character equality across the entire string length.

### The Sub-AUMID Collision
Modern hosted applications (Windows Terminal, WinUI 3, Chromium/Electron) append a window-hosting token containing the window handle:
```
Microsoft.WindowsTerminal_8wekyb3d8bbwe!App~Wh~w010E0A34
```

Because `CompareStringOrdinal` tests strict equality:
1. Passing the canonical AppID (`Microsoft.WindowsTerminal_8wekyb3d8bbwe!App`) causes `CompareStringOrdinal` to return `CSTR_NOTEQUAL` against every view carrying a `~Wh~` suffix. `GetViewsByAppUserModelId` returns zero items, leaving all active windows unpinned.
2. Passing the raw AppID (`...~Wh~w010E0A34`) records a transient window handle in the registry. It matches only that specific window. Sibling windows are ignored, and stale entries persist in the registry after process termination.

---

## 5. Disassembly: New View Lifecycle Isolation

When a new window is created, Windows Shell calls `VirtualPinnedAppsHandler::ViewAddedInternal` (`RVA 0x1801b91c0`):

```x86asm
0x1801b91ff: mov  rax, qword ptr [rax + 0x88] ; Slot 17: GetAppUserModelId
0x1801b9206: call rax                         ; Retrieve newly created view ID
0x1801b9221: mov  rbp, qword ptr [rsi + 0x60] ; Pinned vector end
0x1801b9225: mov  rdi, qword ptr [rsi + 0x58] ; Pinned vector start
; Vector search loop
0x1801b924c: call CompareStringOrdinal        ; Compare with -1, -1 length
0x1801b9258: cmp  eax, 2                      ; Test CSTR_EQUAL
0x1801b925b: je   0x1801b92cf                 ; If equal, invoke PinViewInternal
0x1801b925d: add  rdi, 0x20                   ; Advance to next pinned ID
0x1801b9261: jmp  0x1801b9229
```

Because `CompareStringOrdinal` operates on exact string lengths without prefix matching, a newly created window with suffix `~Wh~w<NEW_HWND>` never matches a stored canonical ID. Windows Shell provides no native auto-pinning for new instances of hosted applications.

---

## 6. External Corroboration

The shell's failure to handle `~Wh~` sub-identifiers affects multiple independent subsystems:

1. **Windhawk Taskbar Grouping Mod (`taskbar-grouping.wh.cpp`):**
   Developers modifying Windows taskbar behavior encountered this identical mismatch. The author implemented a runtime hook on `CompareStringOrdinal` inside `explorer.exe` to explicitly strip `~Wh~%c%08X` suffixes, noting that the Windows Shell breaks grouping logic when these tokens are present.
2. **Open-Source Virtual Desktop Implementations:**
   * `MScholtes/VirtualDesktop`: Invocations of `PinApplication` route directly to `PinAppID(view.GetAppUserModelId())`. Modern hosted applications fail to pin across sibling windows and generate transient registry values.
   * `Ciantic/VirtualDesktopAccessor`: Historically maintained the same naive `PinAppID` implementation without sub-AUMID normalization. *(Resolved in 2026 via upstream PR [#115](https://github.com/Ciantic/VirtualDesktopAccessor/pull/115) and branch `fix/xaml-island-multi-window-pinning` with `APPIDPWSTR` RAII wrapper, base AppUserModelID normalization, Task View parity view-loop synchronization, and `SyncPinnedApps`; see [Document 008](008_virtual_desktop_accessor_com_heap_hardening_and_raii_breakdown.md))*

---

## 7. Conclusions & Validation of PR #59 Architecture

The reverse-engineering findings confirm that the implementation in `pyvda` PR #59 represents the correct architectural approach:

1. **Canonical AppID Registration:** `PinAppID(base_app_id)` registers the base application package in the registry, preventing transient HWND pollution.
2. **Explicit Multi-View Pinning:** Looping through active views sharing `base_app_id` and calling `view.pin()` matches the exact execution path used by Task View (`DesktopTaskGroupsSwitchItemController::PinUnpinToAllDesktops`).
3. **Desktop Transition Reconciliation:** Because `ViewAddedInternal` cannot match new sub-AUMIDs due to strict `CompareStringOrdinal` execution, calling `sync_pinned_apps()` during desktop transitions is strictly necessary to maintain multi-desktop parity for newly opened windows.
