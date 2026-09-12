[ 🏠 Docs Home ](../README.md) › [ 📁 PyVDA ](001_pyvda_rpc_and_com_lifecycle_analysis.md) › **004: Adversarial Audit, Multi-Repo Cross-Analysis, & Hardened Architecture**

---

# PyVDA: Adversarial Audit, Multi-Repo Cross-Analysis, & Hardened Architecture (004)

This document provides a comprehensive adversarial audit of the multi-window application pinning fix (`fix/multi-window-app-pinning`), conducts a cross-repository comparative analysis across four related projects (`pyvda`, `VirtualDesktopAccessor`, `WinStasis`, and `ADCE`), diagnoses COM lifecycle and threading mismatches, and outlines an architectural roadmap for a resilient, next-generation Virtual Desktop subsystem.

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

## 3. Four-Repository Cross-Comparative Analysis

Connecting the architecture across `pyvda`, `VirtualDesktopAccessor`, `WinStasis`, and `ADCE` reveals why different tools experience or avoid COM issues:

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

## 4. Architectural Comparison: C# vs. Rust vs. Python on Windows

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

## 5. Blueprint: Decoupled MTA Engine Architecture for Caster

To achieve zero speech lag and complete resilience against Explorer crashes, Caster should transition from direct in-process COM manipulation to a decoupled architecture inspired by ADCE:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Caster Speech Loop (STA)                     │
│  - Speech Recognition Grammar (Dragonfly)                       │
│  - SetWinEventHook (Foreground & Desktop Switch Events)         │
│  - Non-blocking command dispatch (< 0.001 ms overhead)          │
└────────────────────────────────┬────────────────────────────────┘
                                 │ Dispatch Token / IPC
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│               Dedicated Virtual Desktop Engine                  │
│  - Executes on MTA Thread / Native AOT Daemon                   │
│  - Pure Value Objects: VirtualDesktop(guid), AppView(hwnd)     │
│  - TaskbarCreated Window Message Listener (Proactive Reconnect) │
│  - Bounded TTL Cache for base_app_id string lookups             │
│  - Debounced sync_pinned_apps() execution                       │
└─────────────────────────────────────────────────────────────────┘
```

### Core Design Rules
1. **Stateless Value Objects:** Never store raw COM interface pointers in long-lived Python or C# domain models. Store only stable OS identifiers (`HWND`, `Desktop GUID`).
2. **Proactive Invalidation via `TaskbarCreated`:** Register `RegisterWindowMessage("TaskbarCreated")`. When Explorer restarts, invalidate cached COM factories immediately rather than waiting for an RPC failure during user interaction.
3. **MTA Thread Isolation:** Run all Virtual Desktop COM RPC queries on an MTA worker thread, ensuring the STA speech loop never freezes.

---

## 6. Action Plan & Phasing

1. **Phase 1 (Immediate Upstream Contribution):**
   - Submit the clean, scoped pull request `fix/multi-window-app-pinning` to `mirober/pyvda`.
   - Maintain separation from the controversial `@_com_retry` rewrite to maximize acceptance.

2. **Phase 2 (Caster Defensive Integration):**
   - Update Caster's Virtual Desktop integration to dispatch `sync_pinned_apps()` and `VirtualDesktop.go()` calls to a background thread to safeguard speech recognition from Explorer RPC stalls.
   - Listen to `EVENT_SYSTEM_DESKTOPSWITCH` in Caster's focus tracker to trigger synchronization on native keyboard and gesture switches.

3. **Phase 3 (Next-Gen Subsystem Exploration):**
   - Evaluate whether ADCE should absorb Virtual Desktop tracking and expose it to Caster over its existing SSE/MCP channel, completely removing the need for in-process COM within Caster.