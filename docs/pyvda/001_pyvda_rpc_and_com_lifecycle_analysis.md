[ 🏠 Docs Home ](../README.md) › [ 📁 PyVDA ](001_pyvda_rpc_and_com_lifecycle_analysis.md) › **001: RPC Server Unavailability & Stale Proxy Fix Analysis**

---

# PyVDA: RPC Server Unavailability & Stale COM Proxy Fix Analysis (001)

This document provides a technical analysis of `pyvda`'s `fix/rpc-server-unavailable` branch (commit `d2c6f2b`), examining the specific failure mode where `explorer.exe` restarts cause stale COM proxies, evaluating the `@_com_retry` implementation, and reviewing the re-hydration mechanics.

---

## 1. Context & The Specific Failure Mode

`pyvda` provides Python bindings to undocumented Windows Virtual Desktop COM interfaces (`IVirtualDesktopManagerInternal`, `IApplicationViewCollection`, `IVirtualDesktopPinnedApps`) hosted out-of-process inside **`explorer.exe`**.

### The Failure Trigger:
When `explorer.exe` restarts (due to a crash, shell restart, or display change), the out-of-process COM server is destroyed and recreated. 

* **Before the Fix:** Any long-lived COM pointers held in Python memory (`self._view`, `self._virtual_desktop`, `managers.manager_internal`) immediately became **orphaned proxy stubs**.
* Any subsequent method invocation crashed with:
  - `RPC_S_SERVER_UNAVAILABLE` (`0x800706BA` / `-2147023174`)
  - `RPC_E_DISCONNECTED` (`0x80010108` / `-2147417848`)

---

## 2. Analysis of the Fix in Commit `d2c6f2b`

The solution implemented on `fix/rpc-server-unavailable` consists of three interconnected mechanisms:

```
                            ┌──────────────────────────────┐
                            │    @_com_retry Decorator     │
                            └──────────────┬───────────────┘
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                     ▼
           [Method Call Succeeded]                 [COMError: RPC Server Unavailable /
                                                             RPC Disconnected]
                                                              │
                                                              ▼
                                                   ┌─────────────────────────┐
                                                   │ 1. Sleep with backoff   │
                                                   │ 2. Re-init managers     │
                                                   │ 3. Call `_refresh()`    │
                                                   │ 4. Retry method (max 3) │
                                                   └─────────────────────────┘
```

### A. The `@_com_retry` Decorator
```python
def _com_retry(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        last_error = None
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except _ctypes.COMError as e:
                if e.args and e.args[0] in (
                    RPC_S_SERVER_UNAVAILABLE,
                    RPC_E_DISCONNECTED,
                    RPC_S_SERVER_UNAVAILABLE_U,
                    RPC_E_DISCONNECTED_U,
                ):
                    last_error = e
                    time.sleep(0.1 * (i + 1))
                    if args and hasattr(args[0], '_refresh') and not isinstance(args[0], type) and func.__name__ != '__init__':
                        args[0]._refresh()
                    else:
                        managers.__init__()
                    continue
                raise
        if last_error:
            raise last_error
    return wrapper
```

### B. Object Re-Hydration (`_refresh()`)
Instead of assuming a cached COM pointer is valid forever, `VirtualDesktop` and `AppView` cache their immutable identifiers:
* `VirtualDesktop` caches `self._id_cached = self._virtual_desktop.GetID()`
* `AppView` caches `self._hwnd_cached = self._view.GetThumbnailWindow()`

When an RPC failure occurs:
1. `managers.__init__()` reconnects to the newly launched `explorer.exe` instance via `CoCreateInstance(CLSID_ImmersiveShell, IServiceProvider)`.
2. `self._virtual_desktop = managers.manager_internal.FindDesktop(self._id_cached)` re-fetches a fresh, valid COM interface pointer matching that GUID.

### C. Thread-Local COM Initialization (`threading.local`)
`Managers` inherits from `threading.local`. When a new thread accesses `managers`, it automatically calls `CoInitializeEx()` on that thread.
* If COM was already initialized on that thread in a different mode (such as `COINIT_MULTITHREADED` / MTA), `CoInitializeEx` returns `0x80010106` (`RPC_E_CHANGED_MODE` / `-2147417850`).
* PyVDA catches this specific error gracefully without crashing.

---

## 3. Summary & Scope

This fix provides a pragmatic, backward-compatible patch that solves runtime crashes when `explorer.exe` restarts.

For a comprehensive critique of PyVDA's deeper threading architecture, apartment boundary management, and whether this fix is a symptom of a broader architectural pattern, see **[`002_pyvda_core_architecture_and_threading_critique.md`](002_pyvda_core_architecture_and_threading_critique.md)**.
