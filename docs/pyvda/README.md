[ 🏠 Docs Home ](../README.md) › **📁 PyVDA Virtual Desktop Subsystem**

---

# PyVDA Virtual Desktop Subsystem

This directory houses deep architectural analyses, COM lifecycle investigations, adversarial audits, and multi-window application pinning solutions for the Windows 10/11 Virtual Desktop manager and its Python bridge (`pyvda`).

---

## 📑 Document Index

* **[001: RPC Server Unavailability & Stale Proxy Fix Analysis](001_pyvda_rpc_and_com_lifecycle_analysis.md)**  
  Technical analysis of `pyvda` branch `fix/rpc-server-unavailable` (commit `d2c6f2b`), examining `explorer.exe` restart failure modes, the `@_com_retry` decorator, and pointer re-hydration mechanics.

* **[002: PyVDA Core Architecture & Threading Critique](002_pyvda_core_architecture_and_threading_critique.md)**  
  Deep architectural critique examining stateful remote proxy anti-patterns, COM apartment leaks across threads, and synchronous RPC blocking on the caller thread.

* **[003: Multi-Window & XAML Island Application Pinning Architecture](003_pyvda_multi_window_xaml_island_pinning_architecture.md)**  
  Root cause analysis of Windows Terminal secondary window isolation, XAML Island `~Wh~w<HEX_HWND>` sub-AUMIDs, exact string matching in `IVirtualDesktopPinnedApps`, and the `base_app_id` + `sync_pinned_apps()` refactoring.

* **[004: Adversarial Audit, Native Windows Shell Architecture, & Resilient Client Design](004_adversarial_audit_and_hardened_com_architecture.md)**  
  Rigorous adversarial audit exposing 5 failure modes in `pyvda`, demystification of Windows's native `explorer.exe` / `twinui.pcshell.dll` engine, 4-repo cross-comparative analysis (`pyvda`, `VirtualDesktopAccessor`, `WinStasis`, `ADCE`), rejection of `TaskbarCreated` band-aids, and the zero-cached-state transient invocation blueprint.

---

## 🔗 Related Documentation
* [Virtual Desktop Pinning Architecture & Grammar Ergonomics](../features/virtual_desktop_pinning_and_grammar_ergonomics.md)
* [Repository Brain (Canonical SSOT)](../context/repository-brain.md)
* [Technical Journey & Recent Focus](../history/technical_journey.md)