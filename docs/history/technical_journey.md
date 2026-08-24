[ 🏠 Docs Home ](../README.md) › [ 📁 History ](../README.md#history) › **Technical Journey & Recent Focus**

---

# Technical Journey & Recent Focus

Our ongoing work focuses on real-time desktop context tracking, window switching, accessibility mechanics, and speech engine responsiveness. Below is a structured summary of our journey, ordered from active production focus back to foundational milestones:

### 1. Active Desktop Context Engine (ADCE) & Accessibility MCP (Phase 4 / Gate 4 Handover)
- **Active Handover Status**: Foundational accessibility and UIA research in Caster has concluded with the completion of Gate 3 empirical micro-spikes ([Doc 016](../accessibility_mcp/016_micro_spike_2_win32_shallow_python_telemetry.md)), the UI Automation Hierarchy Single Source of Truth ([Doc 017](../accessibility_mcp/017_ui_automation_tree_structures_and_target_zones_reference.md)), and Epistemic Gap Analysis & Requirements ([Doc 018](../accessibility_mcp/018_epistemic_gaps_dynamic_app_discovery_and_requirements.md)). Active engine implementation has officially transitioned to the standalone **[`amirf147/active-desktop-context-engine`](https://github.com/amirf147/active-desktop-context-engine)** repository.
- **Core Engineering Breakthroughs & Empirical Findings**:
  - **Empirical Falsification of DOM Crawling**: Proved that UIA3 is blazingly fast when scoped directly to named containers (`tabs-container`, `tabs normal`, `monaco-breadcrumbs`), extracting 30 tabs in **10.17 ms** and full focus envelopes in **0.66 ms** with zero recursive tree crawling.
  - **Single Source of Truth (SSOT)**: Codified exact UIA node hierarchies, class names, and target extraction recipes for Antigravity IDE, Waterfox, and Windows 11 File Explorer in [Doc 017](../accessibility_mcp/017_ui_automation_tree_structures_and_target_zones_reference.md).
  - **Dynamic App Discovery & Archetypes**: Formulated the 5 Universal Desktop Framework Archetypes and dynamic discovery pipeline in [Doc 018](../accessibility_mcp/018_epistemic_gaps_dynamic_app_discovery_and_requirements.md) to eliminate brittle hardcoded selectors.
  - **Unified Daemon Synthesis**: The C# .NET 10 ADCE service runs as an always-on background daemon at Windows boot (system tray), maintaining the live desktop graph, persisting historical context (SQLite/DuckDB), and streaming state over Model Context Protocol (MCP) to Caster and AI assistants.
- **Key Documentation**:
  * 🧠 **[ADCE Living Context Hub](../accessibility_mcp/CONTEXT.md)**
  * 📋 **[Epistemic Gaps, Dynamic Discovery & Engine PRS (018)](../accessibility_mcp/018_epistemic_gaps_dynamic_app_discovery_and_requirements.md)**
  * 📑 **[UI Automation SSOT & Target Zones Reference (017)](../accessibility_mcp/017_ui_automation_tree_structures_and_target_zones_reference.md)**
  * 📊 **[Micro-Spike 2 Telemetry & Comparative Analysis (016)](../accessibility_mcp/016_micro_spike_2_win32_shallow_python_telemetry.md)**
  * 🛡️ **[Epistemic Recalibration & Adversarial Review (015)](../accessibility_mcp/015_recalibration_and_adversarial_architecture_review.md)**
  * 🚀 **[Standalone ADCE Repository (GitHub)](https://github.com/amirf147/active-desktop-context-engine)**

---

### 2. Sub-Millisecond Native Win32 App Switcher Refactor (Active Production v3)
- **Active Production Status**: We have refactored and deployed the **v3 production architecture** for [`caster_user_content/util/app_switcher.py`](../../caster_user_content/util/app_switcher.py) (commit `8397b0c`).
- **Core Engineering Breakthroughs**:
  - **Native Win32 Hot Path**: Replaced slow pywinauto UI tree wrappers with direct, sub-millisecond native Win32 focus APIs (`SetForegroundWindow`, `BringWindowToTop`, `AllowSetForegroundWindow`), bringing focus transition times down to 0–10ms.
  - **Guarded Keystate Context Managers**: Eliminated sticky modifier keys and thread deadlocks using `_alt_key_bypass()` (with guaranteed nested `finally` release of `VK_NONE` 0xFF and `VK_MENU` 0x12) and `_attached_threads(target_hwnd)` for deterministic `AttachThreadInput` queue pairing and detachment.
  - **Encapsulated Persistence**: Refactored alias dictionary mutations and JSON serialization into a clean, thread-safe `AliasRegistry` class.
  - **Micro-Polling Verification**: Replaced coarse sleep intervals with non-blocking 10ms micro-polling loops in `verify_focus(target_hwnd)`.
  - **Macro Elimination**: Permanently removed brittle `Win+T` taskbar keyboard traversal macros.
- **Key Documentation**:
  - 🏗️ **[App Switcher Architectural Blueprint (v3)](../architecture/app_switcher_architectural_blueprint.md)**
  - 📜 **[App Switcher Evolution Timeline (2-Year Retrospective)](app_switcher_timeline.md)**
  - 📖 **[App Switcher Feature Guide](../features/app_switcher.md)**

---

### 3. LexiconCode Window Switching Rule Investigation
- **Scope & Context**: Evaluating and documenting the historical window management pull request developed by LexiconCode, which used dynamic grammar (`DictList`) background polling to continuously index open window titles for voice switching.
- **PR Reference**: **[Caster PR #881 (LexiconCode Window Switching)](https://github.com/dictation-toolbox/Caster/pull/881)**
- **Technical Feature Guide**: **[LexiconCode Window Switching Functionality](../features/lexicon_code_window_switching_functionality.md)**

---

### 4. Wayfinder Session: App Switching & UIA Threading Investigation
- **Condensed Summary**: Investigated perceived freezes in `app_switcher.py` and UIA/COM threading performance across speech stacks. Discovered through empirical telemetry (`ca5dc70`) that apparent hangs were caused by Windows PowerShell QuickEdit mode pausing standard output (`stdout`) during console logging.
- **Key Docs & Code**:
  - Feature Guide: **[App Switcher Documentation](../features/app_switcher.md)**
  - Session Index: **[Wayfinder UIA & Threading Directory](../wayfinder-uia-threading/map.md)**
  - Rule & Utility Code: **[window_switching.py](../../caster_user_content/rules/global/window_switching.py)** & **[app_switcher.py](../../caster_user_content/util/app_switcher.py)**

---

### 5. Historical Status & Archived Investigations
- Archive of past status updates with deep dives into the Dragonfly BPC Fork Kaldi race condition fixes and UIA threading synthesis:
  👉 **[Status Update History](../../status-update-history.md)**

---

### 6. Git Evolution & Subsystem Timelines
For complete historical retrospectives spanning our 27-month, 969-commit repository evolution:
- 📜 **[App Switcher Evolution Timeline](app_switcher_timeline.md)**: 2-year journey across 5 eras of window switching.
- 📜 **[Caster Printer & HUD Timeline](caster_printer_hud_timeline.md)**: Evolution of status messaging and async HUD overlays.
- 📜 **[Repository Master Timeline](repository_timeline.md)**: Comprehensive 4-era narrative covering 27 months of hands-free Voice OS engineering.
- 🌐 **[Interactive Timeline Visualizer](timeline.html)**: Interactive web timeline application.
