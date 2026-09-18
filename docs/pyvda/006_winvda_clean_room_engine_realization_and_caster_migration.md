[ 🏠 Docs Home ](../README.md) › [ 📁 PyVDA / WinVDA Subsystem ](README.md) › **006: WinVDA Engine Realization, Clean-Room Release, & Caster Production Migration**

---

# 006: WinVDA Engine Realization, Clean-Room Release, & Caster Production Migration

**From Adversarial Audit to Standalone Clean-Room Engine, Apache-2.0 Release, and Production Caster Migration**

* **Status:** Complete & Active in Production
* **Author:** Amir Farhadi
* **Date:** September 2026
* **Public Repository:** [https://github.com/amirf147/winvda](https://github.com/amirf147/winvda)
* **License:** Apache License, Version 2.0
* **Target System:** Windows 10 (Build 19041+) and Windows 11 (Builds 22000, 22621, 22631, 26100+)

---

## 1. Executive Summary & Production Milestone

This document marks the successful culmination and realization of the architectural research conducted across Documents 001 through 005. 

Prior research exposed fundamental architectural vulnerabilities in the legacy `pyvda` library:
1. **Explorer Restart Crashes:** Holding long-lived, cached COM interface pointers in Python objects corrupted memory when `explorer.exe` terminated or restarted, leading to unrecoverable `RPC_S_SERVER_UNAVAILABLE` (`0x800706BA`) and dead ALPC stub exceptions.
2. **COM Apartment Collisions:** Forcing Single-Threaded Apartment (STA) modes collided with multi-threaded speech engine workers and async runtimes (`RPC_E_CHANGED_MODE`, `0x80010106`), while proxy wrappers leaked cross-thread boundaries (`RPC_E_WRONG_THREAD`, `0x8001010E`).
3. **Sub-AUMID Multi-Window Isolation:** Naively passing raw AppUserModelIDs to `IVirtualDesktopPinnedApps` failed on modern XAML Island and packaged applications (e.g. Windows Terminal), which append synthetic `~Wh~w<HEX_HWND>` tokens that fail Windows Shell exact string matching (`wcscmp`).

Rather than patching `pyvda` with compounding reactive retry decorators, we designed, implemented, validated, and published **`winvda`**—an independent, clean-room Python library built from first principles using direct `ctypes` direct vtable offset dispatch and a zero-cached-state execution model.

`winvda` is now published as an open-source library at **[`github.com/amirf147/winvda`](https://github.com/amirf147/winvda)** under the **Apache-2.0** license, and has replaced `pyvda` across all virtual desktop switching and window pinning workflows in the core Caster voice engine (`custom-setup` branch).

---

## 2. Core Architectural Pillars Realized in WinVDA

```
+-----------------------------------------------------------------------------+
|                          WinVDA High-Level Architecture                     |
+-----------------------------------------------------------------------------+
|  Public API: get_desktops, switch_desktop, pin_window, pin_app, sync_apps   |
+-----------------------------------------------------------------------------+
                                     |
               +---------------------+---------------------+
               |                                           |
               v                                           v
+-------------------------------+           +-------------------------------+
|    Engine Session Manager     |           |    Pinning Session Manager    |
|   (Transient MTA Context)     |           |    (Transient MTA Context)    |
+-------------------------------+           +-------------------------------+
               |                                           |
               v                                           v
+-------------------------------+           +-------------------------------+
|  Direct ctypes VTable Calls   |           |  Sub-AUMID Regex Normalizer   |
|   (IVirtualDesktopManager-    |           |   (Strips ~Wh~w<HEX_HWND>     |
|      Internal Slot Offsets)   |           |   for Canonical PinAppID)     |
+-------------------------------+           +-------------------------------+
               |                                           |
               +---------------------+---------------------+
                                     |
                                     v
+-----------------------------------------------------------------------------+
|                        Immutable Domain Models                              |
|         VirtualDesktop(number, id, name) | WindowView(hwnd, is_pinned)      |
|               (Zero cached COM pointers / thread-safe)                      |
+-----------------------------------------------------------------------------+
```

### 2.1 Zero-Cached-State Invocation
`winvda` never persists COM interface pointers in Python heap allocations across calls. Every API call executes within a call-scoped transient context manager:
* Fresh pointers (`IServiceProvider`, `IVirtualDesktopManagerInternal`, `IVirtualDesktopPinnedApps`, `IApplicationViewCollection`) are obtained directly from active `explorer.exe` ALPC endpoints.
* Vtable functions are called atomically via pointer arithmetic (`call_vtable`).
* All pointers are deterministically released inside `finally` blocks using `safe_release` (wrapping `IUnknown::Release`).
* **Explorer Resilience:** When `explorer.exe` crashes or restarts, no stale proxy stubs remain in memory. The subsequent command automatically binds to the newly spawned Explorer process without retry loops or restart-polling daemons.

### 2.2 Dual COM Apartment Resilience
Speech recognition engines (Caster with Kaldi/Dragonfly) and window switchers run on multi-threaded worker pools:
* `winvda` joins the Multi-Threaded Apartment (`COINIT_MULTITHREADED`) on entry.
* If the calling thread was previously initialized into an STA apartment (e.g., by GUI frameworks, Qt, or UI Automation), `CoInitializeEx` returns `RPC_E_CHANGED_MODE` (`0x80010106`). `winvda` detects this condition, safely executes within the caller's existing apartment without error, and preserves the caller's threading state upon exit.

### 2.3 Stateless Value Objects
Domain entities returned by `winvda` (`VirtualDesktop` and `WindowView`) are immutable frozen dataclasses containing purely primitive types (`uuid.UUID`, `int`, `str`, `bool`):
* They contain zero COM pointers or RPC proxies.
* They cross thread boundaries freely without triggering `RPC_E_WRONG_THREAD`.
* They serialize directly to dictionaries or JSON for consumption by external HUD overlays or IPC daemons.

### 2.4 Task View Parity Application Pinning
`winvda.pinning` mirrors the exact internal logic of Windows Task View (`VirtualPinnedAppsHandler` in `twinui.pcshell.dll`):
1. **Sub-AUMID Normalization:** Parses application identities through `normalize_base_app_id()`, stripping synthetic `~Wh~w<HEX_HWND>` tokens generated for detached tabs and XAML Islands.
2. **Canonical Registration:** Invokes `IVirtualDesktopPinnedApps::PinAppID` with the canonical base package identity.
3. **Active View Iteration:** Traverses active views via `IApplicationViewCollection::GetViewsByZOrder` and invokes `PinView` on all currently open sibling windows.
4. **Desktop Re-synchronization:** `sync_pinned_apps()` iterates open windows across desktop switches, dynamically binding newly created windows of pinned applications in `< 1 ms`.

### 2.5 Dual-Mode Diagnostic & Automation CLI
The CLI (`python -m winvda`) supports both interactive terminal usage and background automation:
* **Background Hotkeys & Voice Engines (Default):** Captures active foreground window handle via `user32.GetForegroundWindow()` without requiring arguments.
* **Tiling Window Managers & Scripts (`--hwnd`):** Accepts explicit window handles in hex (`0x1a2b3c`) or decimal.
* **Interactive Terminal Testing (`--delay`):** Countdown delay (e.g. `--delay 2`) allowing terminal users to focus target applications before capture.

---

## 3. Caster Integration & Upstream Deprecation

### 3.1 Caster Migration (`custom-setup` branch)
Caster's virtual desktop bridge (`castervoice/lib/windows_virtual_desktops.py`) has been fully migrated from `pyvda` to `winvda`:

```python
# Before (pyvda):
from pyvda import App, VirtualDesktop, get_virtual_desktops
desktops = get_virtual_desktops()
App(window.handle).pin()

# After (winvda):
import winvda
desktops = winvda.get_desktops()
winvda.pin_app(window.handle)
```

All window movement, desktop switching, and application pinning actions execute against `winvda`'s stateless API. Launcher scripts (`Run_Caster_Kaldi_Latest.bat`) configure `PYTHONPATH` to load `winvda` in development mode.

### 3.2 Deprecation & Retirement of PyVDA
With `winvda` verified in live voice computing production:
* `pyvda` is formally deprecated and retired from Caster's production runtime.
* The legacy `fix/rpc-server-unavailable` and `fix/multi-window-app-pinning` branches of `pyvda` are superseded by the clean-room `winvda` architecture.

---

## 4. Verification & Validation Metrics

| Metric | PyVDA (Legacy) | WinVDA (Production) | Result |
| :--- | :--- | :--- | :--- |
| **Explorer Crash Recovery** | Crash (`0x800706BA`) or 3-retry freeze | Transparent automatic re-bind | **Zero crash / zero freeze** |
| **COM Apartment Safety** | Crash on MTA worker threads (`0x80010106`) | Dynamic apartment detection & safe execution | **Thread-safe across STA/MTA** |
| **XAML Island Pinning** | Fails (pins single secondary window) | Native Task View parity (`~Wh~` stripped) | **100% multi-window coverage** |
| **Memory Footprint** | Stateful proxies held indefinitely | 0 leaked pointers (call-scoped release) | **Zero COM memory leaks** |
| **Automated Test Suite** | Broken on modern builds | 14/14 unit & live tests passing (0.11s) | **Fully tested CI suite** |

---

## 5. Related Documentation & Repositories

* 🌐 **Public WinVDA Repository:** [https://github.com/amirf147/winvda](https://github.com/amirf147/winvda)
* 📜 **WinVDA Technical Specification:** [`winvda/docs/SPECIFICATION.md`](https://github.com/amirf147/winvda/blob/master/docs/SPECIFICATION.md)
* 🪟 **Adversarial Audit & Hardened Architecture (004):** [`004_adversarial_audit_and_hardened_com_architecture.md`](004_adversarial_audit_and_hardened_com_architecture.md)
* 🪟 **Task View Pinning Internals (005):** [`005_task_view_pinning_internals_and_shell_reverse_engineering.md`](005_task_view_pinning_internals_and_shell_reverse_engineering.md)
* 🎙️ **Virtual Desktop Pinning & Grammar Ergonomics:** [`../features/virtual_desktop_pinning_and_grammar_ergonomics.md`](../features/virtual_desktop_pinning_and_grammar_ergonomics.md)
