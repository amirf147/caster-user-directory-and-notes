[ 🏠 Docs Home ](../README.md) › **📁 PyVDA Virtual Desktop Subsystem**

---

# PyVDA Virtual Desktop Subsystem

This directory houses deep architectural analyses, COM lifecycle investigations, adversarial audits, and multi-window application pinning solutions for the Windows 10/11 Virtual Desktop manager and its Python bridge (`pyvda`).

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