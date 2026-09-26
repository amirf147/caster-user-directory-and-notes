[ 🏠 Docs Home ](../README.md) › [ 📁 PyVDA / WinVDA Subsystem ](README.md) › **008: VirtualDesktopAccessor COM Heap Hardening, RAII Wrapper Architecture, & Upstream PR #115**

---

# 008: VirtualDesktopAccessor COM Heap Hardening, RAII Wrapper Architecture, & Upstream PR #115

**From Unmanaged Task Memory Leaks to Idiomatic Rust RAII, Zero-Touch Calling Sites, and Cross-Ecosystem Reliability**

* **Status:** Complete & Upstream Review Active (PR #115)
* **Author:** Amir Farhadi
* **Date:** September 2026
* **Upstream PR:** [Ciantic/VirtualDesktopAccessor#115](https://github.com/Ciantic/VirtualDesktopAccessor/pull/115)
* **Target System:** Windows 10 and Windows 11 (Build 26100+)

---

## 1. Executive Summary & Review Context

During work on upstream pull request [VirtualDesktopAccessor PR #115](https://github.com/Ciantic/VirtualDesktopAccessor/pull/115), repository owner Jari Pennanen (`Ciantic`) reviewed our initial bugfix for an unmanaged COM memory leak and commented:

> "Hmm, I think we should not need to edit the calling site. We could wrap APPIDPWSTR to a struct that has Drop implementation calling the CoTaskMemFree..."

This document provides a technical breakdown of:
1. The exact anatomy and historical role of `APPIDPWSTR`.
2. The root cause of the memory leak in Windows COM.
3. The trade-offs between manual C-style deallocation and idiomatic Rust RAII wrappers.
4. How Rust's deterministic `Drop` trait mirrors and differs from Python memory management (`__del__` and `with` context managers).
5. The interface transition from raw `PCWSTR` to `APPIDPWSTR`, contrasting ABI register transparency with Rust move semantics.
6. Why this pattern preserves calling sites without modification while eliminating memory leaks across all control flow paths.
7. How this hardening aligns with Caster's production virtual desktop engine (`winvda`).

---

## 2. Anatomy and History of `APPIDPWSTR`

To understand Jari's comment, we must examine what `APPIDPWSTR` actually is and how it was originally defined in the codebase.

### Name Breakdown (Win32 Hungarian Notation)

In classic Windows Win32 API and C++ development, Microsoft uses Hungarian notation prefixes:

| Component | Meaning | Win32 / C Equivalent | Rust Equivalent |
| :--- | :--- | :--- | :--- |
| **APPID** | Application User Model ID (AUMID) | A unique string identifying an app | String data |
| **P** | Pointer | Raw memory address (`*`) | Raw pointer (`*mut` or `*const`) |
| **W** | Wide Character | UTF-16 wide char (`wchar_t`) | `u16` / `WCHAR` |
| **STR** | String | Null-terminated character array | `[u16]` ending in `0x0000` |

In Win32 SDK headers:
* `PWSTR` means **P**ointer to **W**ide **STR**ing (`wchar_t*` / `*mut u16`).
* `PCWSTR` means **P**ointer to **C**onstant **W**ide **STR**ing (`const wchar_t*` / `*const u16`).

Therefore, `APPIDPWSTR` translates directly to:
**"Pointer to a Wide String representing an Application ID."**

### How `APPIDPWSTR` Was Used Before PR #115

In upstream `VirtualDesktopAccessor/src/comobjects.rs`, Jari originally defined `APPIDPWSTR` at line 23 as a simple type alias:

```rust
type WCHAR = u16;
type APPIDPWSTR = *const WCHAR;
```

In Rust, `type Alias = Target;` does not create a new type. It is merely a synonym, identical to a Python type hint (`AppId = str`). Under the hood, `APPIDPWSTR` was just a raw pointer integer (`*const u16`).

Jari used this alias in the helper method `get_iapplication_id_for_view`:

```rust
fn get_iapplication_id_for_view(&self, view: &IApplicationView) -> Result<APPIDPWSTR> {
    let mut app_id: APPIDPWSTR = std::ptr::null_mut();
    unsafe {
        view.get_app_user_model_id(&mut app_id as *mut _ as *mut _)
            .as_result()?
    }
    Ok(app_id)
}
```

Notice that `get_iapplication_id_for_view` was already returning `APPIDPWSTR`. When Jari wrote his review comment, he was referring to his own existing type alias: instead of having `APPIDPWSTR` be a passive alias for a raw pointer, turn `APPIDPWSTR` into an active wrapper struct.

---

## 3. The Root Cause: COM Task Memory Allocation

```
+-----------------------------------------------------------------------------+
| Python Runtime (Managed Heap)                                               |
| - Garbage collector tracks references. Memory reclaims automatically.       |
+-----------------------------------------------------------------------------+
                                       |
                                       | FFI / C Bridge
                                       v
+-----------------------------------------------------------------------------+
| Windows COM / C ABI (Unmanaged Process Heap)                                |
| - The OS has no garbage collector.                                          |
| - Callee allocates memory on the process COM task heap (CoTaskMemAlloc).    |
| - Contract rule: The CALLER owns the buffer and MUST free it.               |
+-----------------------------------------------------------------------------+
```

### The Allocation Mechanism

When `IApplicationView::GetAppUserModelId` executes inside Windows Explorer:
1. Windows dynamically allocates an array of UTF-16 characters on the process COM task heap using `CoTaskMemAlloc`.
2. Windows copies the application identifier (such as `Google.AntigravityIDE` or `Microsoft.WindowsTerminal_8wekyb3d8bbwe!App`) into this buffer.
3. Windows assigns the buffer's memory address to our output pointer (`&mut app_id`).

### The COM Memory Ownership Contract

The Component Object Model defines strict rules for memory allocation across module boundaries:
* **`[in]` parameters**: The caller allocates the buffer; the callee reads it and must not free it.
* **`[out]` parameters**: The callee allocates the buffer using the COM task allocator; **the caller takes ownership and is required to release it using `CoTaskMemFree`**.

Because `VirtualDesktopAccessor` treated `APPIDPWSTR` as a raw pointer without ever calling `CoTaskMemFree`, every call to `is_pinned_app`, `pin_app`, or `unpin_app` orphaned the allocated buffer. In background accessibility systems like Caster that continuously inspect active windows, this resulted in chronic unmanaged heap leakage.

---

## 4. The Naive C-Style Fix (Commit `52b411f`)

In our initial commit (`52b411f`), we resolved the leak by adding explicit deallocation calls to every calling function:

```rust
#[apply(retry_function)]
pub fn is_pinned_app(&self, window: &HWND) -> Result<bool> {
    let view = self.get_iapplication_view_for_hwnd(window)?;
    let pinned_apps = self.get_pinned_apps()?;
    let app_id = self.get_iapplication_id_for_view(&view)?;
    let mut value = false;
    let res = unsafe { pinned_apps.is_app_pinned(app_id, &mut value).as_result() };
    unsafe { CoTaskMemFree(Some(app_id as *const _)) };
    res?;
    Ok(value)
}
```

### The Python Analogy: Manual Cleanup Anti-Pattern

In Python, this manual approach is equivalent to:

```python
f = open("data.txt")
try:
    content = f.read()
finally:
    f.close()
```

While functional, this approach has concrete disadvantages:
1. **Calling Site Noise**: Every high-level function that interacts with application IDs (`is_pinned_app`, `pin_app`, `unpin_app`) must repeat the exact same three-line deallocation ritual.
2. **Fragility on Early Exit**: Storing intermediate results (`let res = ...;`) before calling `CoTaskMemFree` creates an error-prone pattern. If an author writes an early return (`?`) before the deallocation call, the leak returns immediately.

---

## 5. Jari's Proposal: RAII and Deterministic Destruction

Jari suggested moving the deallocation responsibility into the type itself using **RAII** (Resource Acquisition Is Initialization).

### Python Comparison: `__del__` vs. `with` vs. Rust `Drop`

In Python, automatic resource cleanup takes two forms:

1. **`with` Context Managers (`__enter__` / `__exit__`)**:
   Guarantees cleanup upon leaving a block. However, it requires explicit syntax (`with get_app_id() as app_id:`) at every call site.
2. **Object Finalization (`__del__`)**:
   Runs when an object is reclaimed by the garbage collector. In Python, this is non-deterministic; you cannot control when the garbage collection sweep occurs.

In Rust, the `Drop` trait provides the benefits of both:
* **Automatic**: You do not need a special `with` block at the call site.
* **Deterministic**: Rust has no garbage collection pauses. When a variable goes out of scope (at the closing brace `}` of its enclosing block), its destructor runs at that exact microsecond.

### The Wrapper Definition

We replaced the raw pointer alias in `src/interfaces.rs` with a dedicated struct:

```rust
#[repr(transparent)]
#[derive(Debug, PartialEq, Eq)]
pub struct APPIDPWSTR(pub PWSTR);

impl Default for APPIDPWSTR {
    fn default() -> Self {
        Self(std::ptr::null_mut())
    }
}

impl APPIDPWSTR {
    pub fn is_null(&self) -> bool {
        self.0.is_null()
    }

    pub fn as_ptr(&self) -> *const WCHAR {
        self.0
    }
}

impl Drop for APPIDPWSTR {
    fn drop(&mut self) {
        if !self.0.is_null() {
            unsafe {
                CoTaskMemFree(Some(self.0 as *const _));
            }
        }
    }
}
```

### The Role of `#[repr(transparent)]`

Because `APPIDPWSTR` crosses the foreign C interface into Windows Explorer, its binary layout is critical:
* Standard Rust structs can include internal padding or compiler metadata.
* `#[repr(transparent)]` instructs the compiler that `APPIDPWSTR` must have the exact same size (8 bytes on x64), alignment, and register placement as the inner raw pointer (`PWSTR` / `*mut u16`).
* When passed into a COM function, it sits in register `RDX`, matching Windows Explorer's expected `LPCWSTR` parameter byte-for-byte.

---

## 6. The Interface Shift: `PCWSTR` to `APPIDPWSTR`

In `src/interfaces.rs`, the trait definition for `IVirtualDesktopPinnedApps` originally accepted raw `PCWSTR` pointers. In commit `18fe34d`, the parameter type was changed to the newtype wrapper `APPIDPWSTR`:

```diff
 #[windows_interface::interface("4CE81583-1E4C-4632-A621-07A53543148F")]
 pub unsafe trait IVirtualDesktopPinnedApps: IUnknown {
-    pub unsafe fn is_app_pinned(&self, app_id: PCWSTR, out_iss: *mut bool) -> HRESULT;
-    pub unsafe fn pin_app(&self, app_id: PCWSTR) -> HRESULT;
-    pub unsafe fn unpin_app(&self, app_id: PCWSTR) -> HRESULT;
+    pub unsafe fn is_app_pinned(&self, app_id: APPIDPWSTR, out_iss: *mut bool) -> HRESULT;
+    pub unsafe fn pin_app(&self, app_id: APPIDPWSTR) -> HRESULT;
+    pub unsafe fn unpin_app(&self, app_id: APPIDPWSTR) -> HRESULT;
```

### 6.1 Understanding `PCWSTR`

In the Windows SDK headers and `src/interfaces.rs` line 150:

```rust
type WCHAR = u16;
type PCWSTR = *const WCHAR;
```

`PCWSTR` designates a **P**ointer to a **C**onstant **W**ide **STR**ing (`const wchar_t*` in C/C++). In the COM Interface Definition Language (IDL) for `IVirtualDesktopPinnedApps`, Microsoft declares the methods with input string parameters:

```c
HRESULT IsAppPinned([in] LPCWSTR appId, [out] BOOL *isPinned);
HRESULT PinApp([in] LPCWSTR appId);
HRESULT UnpinApp([in] LPCWSTR appId);
```

The original author mapped `[in] LPCWSTR` directly to `PCWSTR`.

In Rust, raw pointers (`*const T`) have specific semantics:
1. **Implicit Copying**: Raw pointers implement the `Copy` trait. Passing a `PCWSTR` copies a 64-bit integer address without tracking resource ownership.
2. **Absence of Destructors**: Raw pointers do not implement `Drop`. When a raw pointer leaves scope, the memory address is discarded, but the buffer on the COM task heap remains allocated.
3. **No Lifetime or Ownership Enforcement**: The compiler cannot verify whether the caller or callee must release the underlying COM heap allocation.

### 6.2 Fundamental Shift vs. ABI Invariance

Evaluating whether this modification was fundamental depends on the layer of analysis:

#### Machine and FFI ABI Layer (Zero Difference)
At the binary level, the change is entirely invariant:
* `APPIDPWSTR` is declared as `#[repr(transparent)] pub struct APPIDPWSTR(pub PWSTR);`.
* On 64-bit Windows, both `PCWSTR` and `APPIDPWSTR` occupy 8 bytes with 8-byte alignment.
* Under the x64 Windows calling convention, the second parameter (`app_id`) is passed in CPU register `RDX`.
* Windows Explorer and the COM vtable receive the identical memory address in `RDX`. No data conversion or pointer indirection occurs.

#### Rust Type System and Lifetime Layer (Fundamental Transformation)
Within the Rust language, the change represents a fundamental architectural transition:
1. **Move Semantics Enforcement**: Because `APPIDPWSTR` implements `Drop`, Rust forbids implementing `Copy`. The type cannot be duplicated implicitly; it can only be moved.
2. **Interface as an Ownership Sink**: Declaring `app_id: APPIDPWSTR` by value requires the caller to transfer ownership of the allocation directly to the COM interface method.
3. **Automatic Lifecycle Termination**: Once `is_app_pinned` finishes executing, the parameter `app_id` reaches the end of its block. Rust automatically calls `Drop::drop(&mut app_id)`, which executes `CoTaskMemFree`.
4. **Preservation of Caller Cleanliness**: High-level callers in `src/comobjects.rs` are freed from performing manual cleanup, eliminating boilerplate while guaranteeing memory safety.

The operational differences between `PCWSTR` and `APPIDPWSTR` are summarized below:

| Feature | Raw Pointer (`PCWSTR`) | RAII Wrapper (`APPIDPWSTR`) |
| :--- | :--- | :--- |
| **Rust Type** | `*const u16` (type alias) | `#[repr(transparent)]` struct |
| **Semantics** | `Copy` (borrowed pointer) | Move-only (transfers ownership) |
| **Destructor (`Drop`)** | None | Runs `CoTaskMemFree` if non-null |
| **Deallocation Responsibility** | Explicit caller cleanup | Automated at method termination |
| **Binary Representation** | 8-byte address in `RDX` | 8-byte address in `RDX` |
| **Leak Risk on Early Return** | High (skipped manual call) | Zero (stack unwinding drops value) |

### 6.3 Restoration of High-Level Calling Sites

Because the trait methods consume `APPIDPWSTR` by value, calling sites in `src/comobjects.rs` return to their original concise structure without manual cleanup blocks:

```rust
#[apply(retry_function)]
pub fn is_pinned_app(&self, window: &HWND) -> Result<bool> {
    let view = self.get_iapplication_view_for_hwnd(window)?;
    let app_id = self.get_iapplication_id_for_view(&view)?;
    unsafe {
        let mut value = false;
        self.get_pinned_apps()?
            .is_app_pinned(app_id, &mut value)
            .as_result()?;
        Ok(value)
    }
}
```

### 6.4 Execution and Ownership Trace

The operational sequence proceeds as follows:

| Step | Operation | Memory and Ownership State |
| :--- | :--- | :--- |
| **1. Allocation** | `get_iapplication_id_for_view` calls `GetAppUserModelId`. | Windows allocates string via `CoTaskMemAlloc`. Address stored in `APPIDPWSTR`. |
| **2. Transfer** | `app_id` passed by value into `is_app_pinned(app_id, ...)`. | Ownership moves into `is_app_pinned`. Raw pointer placed in `RDX` for Explorer. |
| **3. COM Call** | Windows Explorer inspects string buffer. | Explorer reads the AUMID string. Buffer remains intact (`[in]` parameter). |
| **4. Destruction** | `is_app_pinned` returns. | Parameter `app_id` reaches end of scope. Rust runs `Drop::drop`, calling `CoTaskMemFree`. |
| **5. Return** | `is_pinned_app` returns `Ok(value)`. | Heap allocation is already released. Zero memory is leaked. |

### 6.5 Failure Paths and Unwinding Guarantees

If an error occurs before `is_app_pinned` takes ownership, resource cleanup remains guaranteed:
1. In `is_pinned_app`, `get_iapplication_id_for_view` successfully allocates `app_id`.
2. If `self.get_pinned_apps()?` subsequently fails (such as Explorer restarting and returning `RPC_S_SERVER_UNAVAILABLE`), the `?` operator initiates an early return.
3. Because `app_id` was not yet moved into `is_app_pinned`, it remains live in `is_pinned_app`'s local stack frame.
4. Rust's stack unwinder invokes `Drop::drop(&mut app_id)`, which executes `CoTaskMemFree`. Memory leaks are prevented across all execution paths.

---

## 7. Cross-Subsystem Alignment with WinVDA & Caster

In Caster's user repository (`%LOCALAPPDATA%\caster`), our virtual desktop architecture moved from `pyvda` to `winvda` (Document 006):
* `pyvda` cached COM pointers across threads, triggering unrecoverable crashes when Explorer restarted.
* `winvda` was implemented in Python using direct `ctypes` vtable dispatch with transient MTA contexts.

In Python `ctypes`, memory deallocation requires explicit Win32 calls:

```python
import ctypes
ole32 = ctypes.oledll.ole32

def free_com_string(ptr):
    if ptr:
        ole32.CoTaskMemFree(ptr)
```

`VirtualDesktopAccessor.dll` is compiled directly from this Rust codebase. Many tools in the Windows accessibility ecosystem (such as AutoHotkey scripts and custom Caster rules) load `VirtualDesktopAccessor.dll` directly into their process space. 

By eliminating heap leakage upstream:
1. Applications hosting `VirtualDesktopAccessor.dll` no longer experience memory growth during continuous window monitoring.
2. The codebase establishes clean encapsulation: low-level Win32 memory deallocation lives in `interfaces.rs`, while high-level desktop management in `comobjects.rs` remains readable.

---

## 8. Architectural Comparison Matrix

| Attribute | Upstream Original | Manual C-Style Fix (First PR) | RAII Wrapper (Final PR) | Python `winvda` (`ctypes`) |
| :--- | :--- | :--- | :--- | :--- |
| **Leak-Free on S_OK** | No (leaked every call) | Yes | Yes | Yes |
| **Leak-Free on Error (`?` / Exception)** | No | No (skipped manual free) | Yes (deterministic unwinding) | Yes (`try ... finally`) |
| **Call Site Cleanliness** | Clean (leaked) | Cluttered with manual frees | Clean (untouched) | Handled in helper layer |
| **ABI Compatibility** | Raw pointer | Raw pointer | Raw pointer (`#[repr(transparent)]`) | `c_void_p` / `c_wchar_p` |
| **Destruction Timing** | Never | Manual post-call | Immediate scope exit | Python GC or explicit free |
| **Copy / Clone Semantics** | `Copy` (raw pointer) | `Copy` (raw pointer) | Move-only (no `Clone`/`Copy`) | Python object reference |

---

## 9. Modern Multi-Window XAML Island Pinning & Verification Suite (`fix/xaml-island-multi-window-pinning`)

Following the resolution of the COM task memory leak in PR #115, active engineering in `VirtualDesktopAccessor` expanded to address the second major architectural limitation identified in [Document 004 Section B](004_adversarial_audit_and_hardened_com_architecture.md#b-virtualdesktopaccessor-the-shared-blind-spot) and [Document 005 Section 6](005_task_view_pinning_internals_and_shell_reverse_engineering.md#6-external-corroboration): **multi-window application pinning disparity in modern Windows Shell environments**.

### 9.1 The Problem: Synthetic Sub-AUMIDs & Sibling Window Isolation

In Windows 10 and 11, modern packaged applications and WinUI 3 / XAML Island architectures (such as Windows Terminal and tabbed Windows Notepad) do not share a single static AppUserModelID across all instances. Instead, the Windows Shell dynamically assigns synthetic sub-AUMIDs to individual windows:

```
Canonical Base Package:  Microsoft.WindowsTerminal_8wekyb3d8bbwe!App
Window 1 Shell AUMID:    Microsoft.WindowsTerminal_8wekyb3d8bbwe!App~Wh~w00420A10
Window 2 Shell AUMID:    Microsoft.WindowsTerminal_8wekyb3d8bbwe!App~Wh~w00680B44
```

Under the original upstream implementation of `pin_app(&HWND)`:
1. `get_iapplication_id_for_view` acquired the raw AUMID string (`...~Wh~w<HEX_HWND>`).
2. The raw string was passed directly to `IVirtualDesktopPinnedApps::PinAppID`.
3. Windows Explorer performed an exact string match (`wcscmp`) against its internal pinned application registry table.
4. **The Failure**: Only the specific window instance holding that transient sub-AUMID was pinned. Sibling windows belonging to the exact same application remained unpinned and were hidden when the user switched desktops. Furthermore, closing that window left an orphaned, invalid HWND key in `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VirtualDesktops\PinnedApps`.

### 9.2 FFI Interface Correction (`IApplicationViewCollection`)

To inspect and synchronize active application views, `VirtualDesktopAccessor` interacts with `IApplicationViewCollection`. During reverse engineering, a critical COM FFI signature bug was diagnosed in `src/interfaces.rs`:

```diff
 #[windows_interface::interface("1841c6d7-4f9d-42c0-af41-8747538f10e5")]
 pub unsafe trait IApplicationViewCollection: IUnknown {
-    pub unsafe fn get_views(&self, out_views: *mut IObjectArray) -> HRESULT;
-    pub unsafe fn get_views_by_zorder(&self, out_views: *mut IObjectArray) -> HRESULT;
-    pub unsafe fn get_views_by_app_user_model_id(&self, id: PCWSTR, out_views: *mut IObjectArray) -> HRESULT;
+    pub unsafe fn get_views(&self, out_views: *mut Option<IObjectArray>) -> HRESULT;
+    pub unsafe fn get_views_by_zorder(&self, out_views: *mut Option<IObjectArray>) -> HRESULT;
+    pub unsafe fn get_views_by_app_user_model_id(&self, id: PCWSTR, out_views: *mut Option<IObjectArray>) -> HRESULT;
```

In the Windows COM ABI, functions populating an out-pointer to an interface expect the caller to pass `*mut Option<T>` where the callee can return `None`/null if the collection is empty. Passing a non-optional struct resulted in invalid pointer initialization and potential access violations during shell enumeration.

### 9.3 Architectural Resolution: Base Normalization & Task View Parity

In branch `fix/xaml-island-multi-window-pinning` (commit `df8a72c`), `VirtualDesktopAccessor` was refactored to achieve complete parity with Windows Task View:

1. **Sub-AUMID Normalization**:
   Extracted canonical base package identities by stripping the `~Wh~` suffix via `raw.split_once("~Wh~")`:
   ```rust
   pub struct AppIdInfo {
       pub raw: String,
       pub base: String,
   }
   ```
2. **Persistent Canonical Registration**:
   `pin_app` registers the canonical base package identifier (`app_info.base`) in `IVirtualDesktopPinnedApps::PinAppID`, ensuring future application windows are recognized.
3. **Active Sibling View Synchronization**:
   Iterates active shell views using `self.for_each_view` and invokes `IVirtualDesktopPinnedApps::PinView` on every view matching `app_info.base`. This mirrors the native execution path of Task View (`DesktopTaskGroupsSwitchItemController::PinUnpinToAllDesktops`) without polluting the Windows registry with transient window handles.
4. **Dynamic Transition Reconciliation (`SyncPinnedApps`)**:
   Provides `sync_pinned_apps()` (exported via C-ABI and Rust wrapper `desktop::sync_pinned_apps`), which traverses open views and automatically pins any unpinned view whose parent package identity is already pinned:
   ```rust
   #[apply(retry_function)]
   pub fn sync_pinned_apps(&self) -> Result<u32> {
       let pinned_apps = self.get_pinned_apps()?;
       let mut count = 0;
       self.for_each_view(|sub_view| {
           // If view is not pinned, check if its base app package is pinned.
           // If pinned, call pin_view to reconcile.
           ...
       })?;
       Ok(count)
   }
   ```

### 9.4 Verification Suite (`tests/test_pinning_suite.py`)

To empirically validate both RAII memory safety and pinning behavior across complex applications, a comprehensive verification suite was built in `tests/test_pinning_suite.py`:

```
=======================================================
  VirtualDesktopAccessor - Pinning Verification Suite
=======================================================
  DLL: target/release/VirtualDesktopAccessor.dll
  Current Virtual Desktop: 0 (Total Desktops: 2)

  Discovered active managed applications:
    - Microsoft.WindowsTerminal_8wekyb3d8bbwe!App: 2 window(s)
    - Microsoft.WindowsNotepad_8wekyb3d8bbwe!App: 2 window(s)

  >>> PHASE 1: Testing PinWindow (Individual Window Isolation)
      Window 1: IsPinnedWindow=1, IsPinnedApp=0
      Window 2: IsPinnedWindow=0, IsPinnedApp=0
      Desktop 1: Window 1 VISIBLE, Window 2 HIDDEN
      [PASS] Single-window isolation verified on Target Desktop.

  >>> PHASE 2: Testing PinApp (Task View Parity - Entire Application)
      Window 1: IsPinnedWindow=1, IsPinnedApp=1
      Window 2: IsPinnedWindow=1, IsPinnedApp=1 (sibling auto-synchronized!)
      Desktop 1: BOTH Window 1 AND Window 2 VISIBLE
      [PASS] Multi-window presence verified on Target Desktop.

  >>> PHASE 3: Testing Desktop Switch Reconciliation (SyncPinnedApps)
      Simulating unpinned secondary window while app is pinned...
      Switching to Desktop 1 (switch_desktop triggers SyncPinnedApps)...
      Window 2 IsPinnedWindow after switch: 1
      [PASS] Dynamic desktop-switch reconciliation verified.
```

### 9.5 Synergy: Memory Safety Meets Rapid View Enumeration

The integration of PR #115 (`APPIDPWSTR` RAII wrapper) and the multi-window pinning engine creates critical architectural synergy:
* When `sync_pinned_apps` or `pin_app` iterates through every active window in `IApplicationViewCollection` (often 50+ windows on a busy desktop), it must query `view.get_app_user_model_id` for each view.
* Under the unhardened upstream implementation, a single run of `sync_pinned_apps` would leak dozens of UTF-16 heap allocations on the process COM task heap.
* With `APPIDPWSTR`'s deterministic `Drop` implementation invoking `CoTaskMemFree` upon scope termination, full-desktop view traversal executes with **zero memory leakage**, enabling continuous background reconciliation across hundreds of virtual desktop switches.

