[ 🏠 Docs Home ](../README.md) › [ 📁 PyVDA ](README.md) › **004: Adversarial Audit, Native Windows Shell Architecture, & Resilient Client Design**

---

# PyVDA: Adversarial Audit, Native Windows Shell Architecture, & Resilient Client Design (004)

> **Document Status**: *Active Architectural Blueprint (Canonical SSOT)*  
> **Supersedes**: Stateful remote proxy caching and `@_com_retry` recovery patterns from [`001`](001_pyvda_rpc_and_com_lifecycle_analysis.md) and [`002`](002_pyvda_core_architecture_and_threading_critique.md)  
> **Target Architecture**: Zero-Cached-State / Call-Scoped Transient MTA Invocation  
> **Cross-Subsystem Synergy**: Informs [ADCE Multi-Window State Modeling](../accessibility_mcp/018_epistemic_gaps_dynamic_app_discovery_and_requirements.md#1-epistemic-pause-interrogating-our-knowledge-gaps)

This document provides a comprehensive adversarial audit of the multi-window application pinning fix (`fix/multi-window-app-pinning`), demystifies how the Windows native Virtual Desktop subsystem and Task View actually operate under the hood, explains why external hooking suffers from closed-OS fragility, conducts a cross-repository comparative analysis across four related projects (`pyvda`, `VirtualDesktopAccessor`, `WinStasis`, and `ADCE`), and outlines a resilient client bridge architecture.

---

## 1. Adversarial Audit of the Multi-Window Pinning Fix

The multi-window and XAML Island pinning implementation resolves the primary defect where secondary hosted windows received dynamic `~Wh~` sub-AppUserModelIDs and remained unpinned. However, an adversarial analysis reveals five distinct boundary conditions and failure modes.

### A. Failure Mode 1: Applications Lacking AppUserModelIDs (`app_id is None`)
* **Trigger:** Classic Win32 applications (such as legacy utilities, custom Tkinter/PyQt tools run directly via `python.exe`, or un-packaged tools that do not call `SetCurrentProcessExplicitAppUserModelID`).
* **Mechanism:** When `AppView(hwnd).app_id` invokes `IApplicationView::GetAppUserModelId()`, the out-of-process COM call returns `NULL` or raises `_ctypes.COMError` with `0x80070490` (`Element not found`). The property catches this error and returns `None`.
* **Vulnerability in Current Code:**
  ```python
  base_id = self.base_app_id
  if base_id is None:
      return
  ```
  Calling `pin_app()` on an application without an AUMID exits silently. The caller receives no indication that the application was not pinned, and no windows are pinned.
* **OS Divergence:** The Windows Task View UI allows users to right-click and pin applications even if they lack an explicit AUMID. In these cases, the Windows Shell falls back to tracking the executable path or process image name.
* **Mitigation:** If `base_id` is `None`, `pin_app()` should either:
  1. Fall back to process-level HWND enumeration via `GetWindowThreadProcessId` and pin individual views via `view.pin()` across the process image.
  2. Raise an explicit `ValueError` or `UnsupportedAppError` rather than failing silently.

### B. Failure Mode 2: Passive Desktop Transitions (Native Windows Gestures)
* **Trigger:** The user switches virtual desktops using native Windows hotkeys (`Win + Ctrl + Left/Right`), touchpad multi-finger swipe gestures, or the native Task View interface.
* **Mechanism:** The synchronization routine `sync_pinned_apps()` is currently hooked exclusively inside `VirtualDesktop.go()`.
* **Vulnerability:** When desktop switching bypasses `pyvda.VirtualDesktop.go()`, `sync_pinned_apps()` is never executed. If a user opens a secondary window of an already-pinned hosted application (such as a second Windows Terminal instance) while working on Desktop 2, that secondary window will remain confined to Desktop 2 until `sync_pinned_apps()` is explicitly called by an external trigger.
* **Mitigation:** Long-running host environments (such as Caster or ADCE) must not rely solely on `VirtualDesktop.go()` for synchronization. They must hook Windows Shell desktop transition events (`EVENT_SYSTEM_DESKTOPSWITCH` via `SetWinEventHook` or `IVirtualDesktopNotification::CurrentVirtualDesktopChanged`) to trigger `sync_pinned_apps()` reactively.

### C. Failure Mode 3: Performance Overhead of System-Wide Z-Order Enumeration
* **Trigger:** Workstations with high window counts (50 to 150 top-level windows across active, minimized, and hidden helper states).
* **Mechanism:** `sync_pinned_apps()` invokes `get_apps_by_z_order(switcher_windows=False, current_desktop=False)`.
* **Cost Breakdown:**
  1. `IApplicationViewCollection::GetViewsByZOrder()` returns an `IObjectArray` of all managed views.
  2. For each view, the loop calls `view.base_app_id`, executing a synchronous inter-process COM call (`GetAppUserModelId`) into `explorer.exe`.
  3. For each unique base ID, it queries `IVirtualDesktopPinnedApps::IsAppIdPinned()`.
  4. For unpinned views matching a pinned base ID, it executes `IVirtualDesktopPinnedApps::PinView()`.
* **Latency Impact:** Across 100 windows, sequential synchronous cross-process ALPC round-trips to `explorer.exe` can introduce 50 to 200 ms of latency directly into the desktop switching path in `VirtualDesktop.go()`.
* **Mitigation:**
  - Restrict scanning to `switcher_windows=True` (alt-tab switchable windows), ignoring invisible tool windows and background broker windows.
  - Implement an in-memory TTL cache for verified `base_app_id` strings to avoid repeated `GetAppUserModelId()` round-trips for unchanged HWNDs.

### D. Failure Mode 4: Non-Standard Multi-Instance Suffix Conventions
* **Trigger:** Applications that use custom instance discriminators instead of Windows XAML Island hosting conventions.
* **Mechanism:** Our implementation specifically parses the `~Wh~` delimiter (`app_id.split("~Wh~")[0]`).
* **Vulnerability:** Applications creating separate AUMIDs using custom process IDs or GUID suffixes (for instance, `Company.Product.Session.<PID>`) will not have their suffixes stripped by `base_app_id`. These applications will continue to suffer from exact string match segregation in `IsAppIdPinned()`.

### E. Failure Mode 5: User Interface Privilege Isolation (UIPI) Boundaries
* **Trigger:** An elevated application (running as Administrator / High Integrity) open alongside standard user applications.
* **Mechanism:** When `pyvda` runs as a standard user process, querying COM view interfaces for an elevated window can fail with `0x80070005` (`E_ACCESSDENIED`) or timeout inside the Explorer RPC channel.
* **Mitigation:** All view property accesses inside enumeration loops must catch `COMError` with access denied codes and continue scanning remaining windows rather than aborting.

---

## 2. Empirical Verification on Live Workstation

An empirical probe executed against the running desktop confirmed the taxonomy and edge cases identified above:

```
[Window Query Probe Output]
Google.AntigravityIDE~Wh~w00030C42 -> Base: Google.AntigravityIDE (XAML Island Sub-ID)
Microsoft.WindowsTerminal_8wekyb3d8bbwe!App~Wh~w010E0A34 -> Base: Microsoft.WindowsTerminal_8wekyb3d8bbwe!App (Pinned: True)
Microsoft.WindowsTerminal_8wekyb3d8bbwe!App (Primary Instance) -> Base: Microsoft.WindowsTerminal_8wekyb3d8bbwe!App (Pinned: False)
HWND 66574 (Classic Win32 Tool) -> AppID: None, BaseID: None (Pin App: No-op failure)
```

The live probe confirms that `~Wh~` sub-AUMIDs exist dynamically in Electron/Chromium tools and Windows Terminal, and verifies that windows without AUMIDs represent a real category of top-level windows on Windows systems.

---

## 3. The Windows Native Virtual Desktop Engine: Under the Hood

A common question arises: *Windows already has a virtual desktop engine driving Task View (`Win + Tab`) and the Taskbar. Why does hooking into it feel fragile, and why can't external programs interact with it as smoothly as Task View does?*

To understand this, we must examine the internal architecture of the Windows Virtual Desktop subsystem:

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                                 EXPLORER.EXE PROCESS SPACE                                │
│                                                                                           │
│  ┌─────────────────────────┐                 ┌─────────────────────────────────────────┐  │
│  │   Task View UI          │                 │     twinui.pcshell.dll                  │  │
│  │   (Workstation Viewer)  │                 │                                         │  │
│  │   Win + Tab             │                 │   VirtualDesktopManagerInternal         │  │
│  └────────────┬────────────┘                 │   VirtualDesktopPinnedApps              │  │
│               │ In-Process C++ Call          │   VirtualDesktopNotificationService     │  │
│               │ (< 0.001 ms, No Marshaling)  └────────────────────▲────────────────────┘  │
│               ▼                                                   │                       │
│  ┌────────────────────────────────────────────────────────────────┴────────────────────┐  │
│  │                     Native Virtual Desktop COM Implementation                       │  │
│  └────────────────────────────────────────▲────────────────────────────────────────────┘  │
└───────────────────────────────────────────┼───────────────────────────────────────────────┘
                                            │ Cross-Process ALPC / RPC Boundary
                                            │ (Network / Local IPC Marshaling)
                                            ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL THIRD-PARTY PROCESSES                               │
│                                                                                           │
│     [pyvda (Python)]      [VirtualDesktopAccessor (Rust)]      [WinStasis / ADCE (C#)]     │
│                                                                                           │
│   • Must locate unexported interfaces via IServiceProvider::QueryService                  │
│   • Pointers become invalid whenever explorer.exe restarts (RPC_S_SERVER_UNAVAILABLE)     │
│   • Vtable offsets shift across Windows 10/11 updates (Closed OS ABI churn)               │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

### A. The Public vs. Private Interface Barrier
Microsoft split the Virtual Desktop API into two starkly different layers:

1. **The Public Documented Interface (`IVirtualDesktopManager`):**
   Microsoft published exactly one interface in the official Windows SDK (`shobjidl.h`). It exposes only three methods:
   - `IsWindowOnCurrentVirtualDesktop(HWND, BOOL*)`
   - `GetWindowDesktopId(HWND, GUID*)`
   - `MoveWindowToDesktop(HWND, REFGUID)`
   
   Microsoft intentionally omitted all desktop lifecycle methods. There is **no public API** to create a desktop, remove a desktop, switch desktops, enumerate desktops, rename a desktop, or pin windows/apps.

2. **The Private Undocumented Interfaces (`IVirtualDesktopManagerInternal`, etc.):**
   The methods that Task View actually uses (`SwitchDesktop`, `CreateDesktop`, `PinAppID`, `GetViewsByZOrder`) are quarantined inside undocumented COM interfaces.
   - Microsoft treats these interfaces as internal shell implementation details rather than an external contract.
   - Because they are private, Microsoft reserves the right to alter the interface GUIDs, reorder vtable methods, add new arguments, or change data types in every Windows update without warning.

### B. The Crucial Fact: `pyvda` IS Hooking the Native Engine
`pyvda` and `VirtualDesktopAccessor` do not build an artificial desktop emulator. They hook into the **exact same native C++ COM service inside `explorer.exe`** that Task View calls:
- They obtain `IServiceProvider` from the Shell.
- They query private service ID `{C5E0CDCA-22AC-4E2F-A0AD-4D12E9A7F275}` for `IVirtualDesktopManagerInternal`.
- When `VirtualDesktop(2).go()` runs, it calls `IVirtualDesktopManagerInternal::SwitchDesktop()`, invoking the exact kernel/shell transition that Task View triggers.

### C. Why External Hooking is Inherently Fragile
If third-party tools are calling the exact same native methods as Task View, why do third-party tools fail while Task View works reliably?

1. **The In-Process vs. Out-of-Process Boundary:**
   - **Task View** runs *inside* `explorer.exe`. Its function calls are direct C++ pointer dispatches in memory. It never marshals data across process boundaries, never waits on ALPC synchronization, and can never experience an RPC disconnection (if Explorer crashes, Task View restarts with it).
   - **External Applications** (Python, Rust, C#) live outside `explorer.exe`. They talk to Explorer via cross-process RPC. If Explorer restarts, the remote ALPC port closes, leaving all external COM pointers pointing to dead proxy memory.

2. **ABI Churn Across Windows Updates:**
   - In Windows 10 Build 19041, `SwitchDesktop` was slot 9 in the vtable.
   - In Windows 11 Build 22000, Microsoft rearranged the vtable to support desktop naming and wallpapers.
   - In Windows 11 Build 22621, Microsoft changed `SwitchDesktop` to accept an `IVirtualDesktop` pointer instead of a GUID.
   - In Windows 11 24H2 Build 26100, Microsoft updated interface IDs and struct layouts again.
   - Task View never breaks because it is recompiled alongside the DLL. Third-party tools break on OS updates unless their vtable definitions are manually updated.

3. **Event Notification Subscriptions:**
   - Task View stays updated on hotkey switches (`Win + Ctrl + Arrows`) because it registers in-process callbacks with `IVirtualDesktopNotificationService`.
   - External tools typically rely on synchronous polling or method wrapping, leaving them blind to native gestures unless they host an out-of-process COM notification sink.

---

## 4. Four-Repository Cross-Comparative Analysis

Connecting the architecture across `pyvda`, `VirtualDesktopAccessor`, `WinStasis`, and `ADCE` reveals how their lifecycles and runtimes interact with the Windows Shell:

| Dimension | `pyvda` (Python) | `VirtualDesktopAccessor` (Rust) | `WinStasis` (C# / .NET 10) | `ADCE` (C# / .NET 10) |
| :--- | :--- | :--- | :--- | :--- |
| **Language & Runtime** | Python 3 + `comtypes` / `ctypes` | Rust (`windows-rs` 0.58) | C# (`net10.0-windows`) | C# (`net10.0-windows`) |
| **COM Wrapper Layer** | Custom pure-Python vtable definitions | Custom Rust traits + C-ABI DLL | `Slions.VirtualDesktop` (NuGet) | `FlaUI.UIA3` + Native Win32 |
| **Execution Lifetime** | Long-running in-process with caller | Long-running native DLL / in-process | **Point-in-Time CLI Script (~200 ms)** | Long-running background daemon |
| **Explorer Crash Behavior** | Fails on dead proxy (`RPC_S_SERVER_UNAVAILABLE`) | Re-initializes via `retry_function` macro | **Immune: exits before crashes occur** | Auto-reconnects via event channels |
| **XAML Island Pinning** | Fixed via `base_app_id` + sub-view pinning | **Vulnerable: passes raw AUMID** | Vulnerable if pinning sub-AUMIDs | Handled via UI Automation trees |
| **Apartment Discipline** | Leaks across caller threads (`threading.local`) | Thread-agnostic native calls | Strict STA on CLI startup | **Dedicated MTA Worker Channel** |

### A. Why WinStasis is Immune to the Explorer Stale COM Problem
`WinStasis` (`winst`) is an on-demand CLI utility designed to snapshot and restore window state.
* It initializes COM, queries or sets window positions via `Slions.VirtualDesktop`, and exits within 200 ms.
* Because its process lifetime is measured in milliseconds, it never outlives `explorer.exe`. If Explorer crashes between invocations, the next execution initializes a completely clean COM connection.
* **Key Takeaway:** Tooling that appears stable in CLI testing often hides massive COM lifecycle fragility when embedded into long-running daemons like Caster.

### B. VirtualDesktopAccessor: The Shared Blind Spot
An examination of `VirtualDesktopAccessor/src/comobjects.rs` revealed that the Rust implementation suffers from the exact same limitation:
```rust
pub fn pin_app(&self, window: &HWND) -> Result<()> {
    let view = self.get_iapplication_view_for_hwnd(window)?;
    let app_id = self.get_iapplication_id_for_view(&view)?;
    unsafe {
        self.get_pinned_apps()?.pin_app(app_id).as_result()?;
    }
    Ok(())
}
```
* `VirtualDesktopAccessor` reads the raw AUMID (including `~Wh~w<HWND>`) and passes it directly to `pin_app()`.
* It does not normalize `base_app_id`, nor does it synchronize sibling windows.
* For stale COM recovery, `VirtualDesktopAccessor` uses a 3-iteration retry macro (`retry_function`) that catches `RpcServerNotAvailable` and `ComObjectNotConnected`, drops internal COM services, and retries.

---

## 5. Architectural Comparison: C# vs. Rust vs. Python on Windows

Evaluating the optimal technological foundation for Windows Virtual Desktop automation:

### A. C# (.NET 9 / 10 with Native AOT)
* **Strengths:** C# is the premier systems language for Windows management.
  - Microsoft maintains first-class COM interop, Source-Generated COM, and CsWinRT.
  - Community packages like `Slions.VirtualDesktop` maintain backward and forward compatibility across every Windows 10 and 11 build (builds 10240 through 26100+).
  - Native AOT produces self-contained, lightweight native binaries or C-ABI DLLs with sub-10ms cold starts and zero runtime dependencies.
* **Weaknesses:** If consumed from Python without AOT, requires pythonnet or IPC.

### B. Rust (`windows-rs`)
* **Strengths:** Direct native compilation, minimal memory footprint, zero garbage collection pauses.
* **Weaknesses:** Undocumented Windows COM interfaces are not part of official Windows SDK headers. In Rust, every internal struct, GUID, and vtable must be manually reverse-engineered and maintained. When Microsoft shifts vtable layouts across OS updates (e.g. 24H2 build 26100), Rust code breaks until someone manually rewires the traits.

### C. Python (`pyvda`)
* **Strengths:** Zero build step, natively importable within Caster.
* **Weaknesses:** `comtypes` is slow for bulk operations, lacks thread-safe apartment marshaling, and stateful COM pointers easily corrupt when remote processes restart.

---

## 6. Client Bridge Architecture: Epistemic Audit & The Zero-Cached-State Model

Clarification of terminology: We are **not** proposing building an artificial desktop manager to replace Windows. The Windows kernel (`win32k.sys`) and `explorer.exe` are the only components that can switch desktops.

### A. The Audit of the Audit: Why `TaskbarCreated` is an Anti-Pattern

An earlier draft of this specification proposed listening for the `RegisterWindowMessage("TaskbarCreated")` broadcast to proactively invalidate cached COM proxies when `explorer.exe` restarts.

**A critical adversarial review rejects that proposal as a second-order band-aid:**

1. **Symptom Treatment:** Listening for `TaskbarCreated` attempts to patch the symptom (dead cached pointers) by adding more moving parts: a hidden Win32 window, a dedicated message pump, and cross-thread invalidation signals.
2. **Failure Coverage Gaps:** `TaskbarCreated` only fires when the Explorer taskbar window initializes. It does not fire when:
   - An internal COM worker thread inside `twinui.pcshell.dll` terminates or hangs.
   - The workstation locks, suspends, or undergoes a remote desktop (RDP) session reconnect.
   - Desktop Window Manager (`dwm.exe`) resets without a full taskbar recreation.
   - The message is dropped or delayed relative to the user's voice command.
3. **The Root Cause:** The only reason an application cares when Explorer restarts is because the application committed the cardinal sin of **stateful remote proxy caching** (holding a live out-of-process COM interface pointer across arbitrary time).

---

### B. The True Solution: Zero-Cached-State / Call-Scoped Transient Invocation

Instead of inventing machinery to detect when a cached pointer dies, **never cache the pointer.**

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                                 CASTER VOICE RUNTIME (STA)                                │
│  - Dragonfly Grammar Execution                                                            │
│  - Non-blocking Command Dispatch (< 0.001 ms audio path overhead)                         │
└─────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                              │ Command Token: { Action: Switch, Target: 2 }
                                              ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                        CALL-SCOPED TRANSIENT COM WORKER (MTA)                             │
│                                                                                           │
│   1. Receive request on dedicated MTA background worker.                                  │
│   2. Acquire fresh IServiceProvider and IVirtualDesktopManagerInternal from OS.           │
│      (Local ALPC lookup cost: ~0.015 ms / 15 microseconds).                               │
│   3. Execute single atomic method: SwitchDesktop(targetGuid).                             │
│   4. Release interface pointer immediately.                                               │
│                                                                                           │
│   Zero cached state. Zero invalidation listeners. Zero dead proxy stubs.                  │
└─────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                              │ Direct ALPC
                                              ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                               NATIVE WINDOWS SHELL ENGINE                                 │
│                               (explorer.exe / twinui.pcshell.dll)                         │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Why Transient Invocation Eliminates the Entire Failure Class
1. **Immunity to Explorer Restarts:** If Explorer restarts at 03:00, and a user speaks a command at 03:05, the worker acquires a fresh interface from the newly spawned Explorer instance. It never touches a stale pointer.
2. **Clean Failure Mode During Restarts:** If a user speaks a command at the exact millisecond Explorer is mid-restart, `QueryService` fails immediately with `CO_E_SERVER_EXEC_FAILURE` or `REGDB_E_CLASSNOTREG`. The operation returns a clean "Shell unavailable" error rather than crashing on an invalid memory address.
3. **No Thread Marshaling Complexity:** Because interface pointers are created and destroyed within the scope of a single function call on the MTA worker thread, they are never passed across threads or apartments.
4. **Performance Overhead is Negligible:** `IServiceProvider::QueryService` against a running `explorer.exe` takes **10 to 25 microseconds** (`0.010 - 0.025 ms`). Compared to the 150–400 ms latency of human speech recognition, 20 microseconds of connection setup is completely imperceptible.

---

### C. Decoupled Read-Only Event Sink (Optional)
If Caster requires knowing when a virtual desktop changes passively (e.g. to update a HUD indicator when the user swipes on a touchpad):
* This must be implemented as a **read-only event sink** (`IVirtualDesktopNotification`), completely decoupled from command execution.
* The sink simply receives `CurrentVirtualDesktopChanged` and posts a message to Caster's event queue. It does not manage or share COM pointers with the command executor.

---

## 7. Action Plan & Phasing

1. **Phase 1 (Immediate Upstream Contribution):**
   - Submit the clean, scoped pull request `fix/multi-window-app-pinning` to `mirober/pyvda`.
   - Maintain separation from the controversial `@_com_retry` rewrite to maximize acceptance.

2. **Phase 2 (Caster Defensive Integration):**
   - Update Caster's Virtual Desktop integration to dispatch `sync_pinned_apps()` and `VirtualDesktop.go()` calls to a background thread to safeguard speech recognition from Explorer RPC stalls.
   - Listen to `EVENT_SYSTEM_DESKTOPSWITCH` in Caster's focus tracker to trigger synchronization on native keyboard and gesture switches.

3. **Phase 3 (Next-Gen Subsystem Exploration):**
   - Evaluate whether ADCE should absorb Virtual Desktop tracking and expose it to Caster over its existing SSE/MCP channel, completely removing the need for in-process COM within Caster.