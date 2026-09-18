[ 🏠 Docs Home ](../README.md) › **📁 PyVDA Virtual Desktop Subsystem**

---

# PyVDA Virtual Desktop Subsystem

This directory houses deep architectural analyses, COM lifecycle investigations, adversarial audits, and multi-window application pinning solutions for the Windows 10/11 Virtual Desktop manager and its Python bridge (`pyvda`).

> 🚀 **Production Engine Update (September 2026)**  
> `pyvda` has been formally superseded and retired in Caster production. Virtual desktop management is now powered by **[WinVDA](https://github.com/amirf147/winvda)**, an independent, zero-cached-state clean-room library implementing the transient MTA COM architecture specified in Document 004 and realized in [Document 006](006_winvda_clean_room_engine_realization_and_caster_migration.md).

---

## 📑 Document Index & Architectural Lineage

* **[001: RPC Server Unavailability & Stale Proxy Fix Analysis](001_pyvda_rpc_and_com_lifecycle_analysis.md)** — *Historical Analysis (Superseded)*  
  Technical analysis of `pyvda` branch `fix/rpc-server-unavailable` (commit `d2c6f2b`), examining `explorer.exe` restart failure modes, the `@_com_retry` decorator, and pointer re-hydration mechanics. Its reactive exception-handling approach is architecturally superseded by Document 004.

* **[002: PyVDA Core Architecture & Threading Critique](002_pyvda_core_architecture_and_threading_critique.md)** — *Architectural Critique (Formative Baseline)*  
  Deep architectural critique examining stateful remote proxy anti-patterns, COM apartment leaks across threads, and synchronous RPC blocking on the caller thread. Its recommended stateless principles are formalized in Document 004.

* **[003: Multi-Window & XAML Island Application Pinning Architecture](003_pyvda_multi_window_xaml_island_pinning_architecture.md)** — *Active Specification (Empirically Verified)*  
  Root cause analysis of Windows Terminal secondary window isolation, XAML Island `~Wh~w<HEX_HWND>` sub-AUMIDs, exact string matching in `IVirtualDesktopPinnedApps`, and the `base_app_id` + `sync_pinned_apps()` refactoring.

* **[004: Adversarial Audit, Native Windows Shell Architecture, & Resilient Client Design](004_adversarial_audit_and_hardened_com_architecture.md)** — *Active Architectural Blueprint (Canonical SSOT)*  
  Rigorous adversarial audit exposing 5 failure modes in `pyvda`, demystification of Windows's native `explorer.exe` / `twinui.pcshell.dll` engine, 4-repo cross-comparative analysis (`pyvda`, `VirtualDesktopAccessor`, `WinStasis`, `ADCE`), rejection of `TaskbarCreated` band-aids, and the zero-cached-state transient invocation blueprint.

* **[005: Task View Pinning Internals & Windows Shell Reverse Engineering](005_task_view_pinning_internals_and_shell_reverse_engineering.md)** — *Empirical Shell Audit (twinui.pcshell.dll)*  
  Binary disassembly and PDB symbol audit of VirtualPinnedAppsHandler, proving CompareStringOrdinal full-string mismatch on ~Wh~w<HWND> sub-AUMIDs, and verifying that Task View natively iterates window groups to call PinView individually.


* **[006: WinVDA Engine Realization, Clean-Room Release, & Caster Production Migration](006_winvda_clean_room_engine_realization_and_caster_migration.md)** — *Production Milestone (Published & Active)*  
  Realization of the hardened virtual desktop engine as a standalone, clean-room Python library ([`winvda`](https://github.com/amirf147/winvda), Apache-2.0). Documents the zero-cached-state direct ctypes vtable architecture, multi-apartment safety, Task View parity application pinning, and the production migration in Caster replacing `pyvda`.
---

## 🔄 Synergy with Active Desktop Context Engine (ADCE)

The empirical discovery of Windows Shell **Sub-AppUserModelIDs** in Document 003 directly informs ADCE window identification:

1. **Deterministic Sub-Window Identification:**
   Hosted applications (such as Windows Terminal and detached editor windows) append a synthetic identifier to their AUMID:
   ```
   <PackageFamilyName>!<ApplicationId>~Wh~w<HEX_HWND>
   ```
   The presence of `~Wh~` explicitly indicates a hosted secondary window, while the trailing hex string is the window handle (`HWND`).
2. **Zero-Crawl Context Classification:**
   Rather than performing recursive UI Automation tree queries to deduce whether a window is a terminal instance or child pane, ADCE can inspect the window's AUMID out-of-band via `IApplicationView::GetAppUserModelId()` or Win32 `SHGetPropertyStoreForWindow(PKEY_AppUserModel_ID)`.
3. **Multi-Profile Isolation:**
   Browsers such as Waterfox encode profile hashes into their AUMID (e.g. `6F940AC27A98DD61`), allowing ADCE to immediately disambiguate separate browser instances across desktop workspaces without DOM inspection.

---

## 🔗 Related Documentation
* [ADCE Living Context Hub](../accessibility_mcp/CONTEXT.md)
* [ADCE Dynamic App Discovery & Requirements (018)](../accessibility_mcp/018_epistemic_gaps_dynamic_app_discovery_and_requirements.md)
* [Virtual Desktop Pinning Architecture & Grammar Ergonomics](../features/virtual_desktop_pinning_and_grammar_ergonomics.md)
* [Repository Brain (Canonical SSOT)](../context/repository-brain.md)
* [Technical Journey & Recent Focus](../history/technical_journey.md)