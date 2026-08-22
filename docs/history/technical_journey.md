[ 🏠 Docs Home ](../README.md) › [ 📁 History ](../README.md#history) › **Technical Journey & Recent Focus**

---

# Technical Journey & Recent Focus

Our ongoing work focuses on real-time desktop context tracking, window switching, accessibility mechanics, and speech engine responsiveness. Below is a structured summary of our journey, ordered from active production focus back to foundational milestones:

### 1. Current Focus: Active Desktop Context Engine (ADCE) & Accessibility MCP (Active / Prototype v2.1)
- **Active Prototype Status**: We have implemented and are actively validating the **Active Desktop Context Engine (ADCE)** live monitor (`scripts/context_poc.py`), launched via the voice rule `"launch context engine"` ([`context_engine_launcher.py`](../../caster_user_content/rules/global/context_engine_launcher.py)).
- **Core Engineering Breakthroughs**:
  - **Zero-Polling Win32 Event Hooks**: Implemented native Windows Event Hooks (`SetWinEventHook`) for `EVENT_SYSTEM_FOREGROUND` and `EVENT_OBJECT_FOCUS` running in a COM Multithreaded Apartment (MTA), achieving real-time state updates with 0% idle CPU usage.
  - **Deep Tab Discovery**: Added recursive UIA traversal down to depth 14 across Waterfox, Chrome, Firefox, and VS Code/Antigravity IDE, with multi-heuristic active tab detection (`SelectionItemPattern`, MSAA legacy bitmasks, and focus heuristics).
  - **PyVDA COM Resiliency**: Documented and verified `pyvda`'s `@_com_retry` decorator and GUID re-hydration (`_refresh()`) to make virtual desktop queries completely resilient against `explorer.exe` restarts.
  - **Caster HUD Threading Analysis**: Documented the Caster HUD's out-of-process Qt + XML-RPC + `postEvent` architecture as a proven pattern for zero-blocking GUI overlays.
  - **Two-Tier Caching Blueprint**: Formulated the v3 caching architecture (Macro Sync on window change, Micro Mutation on focus change) to prevent expensive tree traversals on micro-clicks.
- **Key Documentation**:
  - 🧠 **[ADCE Living Context Hub](../accessibility_mcp/CONTEXT.md)**
  - 🔬 **[Real-World Observations & Caching Architecture (008)](../accessibility_mcp/008_real_world_observations_and_caching_architecture.md)**
  - 🗂️ **[Tab Extraction & Context Representation (007)](../accessibility_mcp/007_tab_extraction_and_context_representation.md)**
  - ⚙️ **[PyVDA COM Lifecycle Analysis (001)](../pyvda/001_pyvda_rpc_and_com_lifecycle_analysis.md)**
  - 🖥️ **[Caster HUD Threading Primer (001)](../caster_hud/001_caster_hud_architecture_and_threading_primer.md)**

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
