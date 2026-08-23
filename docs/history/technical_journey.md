[ 🏠 Docs Home ](../README.md) › [ 📁 History ](../README.md#history) › **Technical Journey & Recent Focus**

---

# Technical Journey & Recent Focus

Our ongoing work focuses on real-time desktop context tracking, window switching, accessibility mechanics, and speech engine responsiveness. Below is a structured summary of our journey, ordered from active production focus back to foundational milestones:

### 1. Current Focus: Epistemic Recalibration & Adversarial Review (Phase 3 Gate 3 Micro-Spikes)
- **Active Status**: In accordance with **[015: Epistemic Recalibration](../accessibility_mcp/015_recalibration_and_adversarial_architecture_review.md)**, we have paused the premature compiled C# daemon handover (`014`) to eliminate solution bias. We have established a permanent **4-Gate Epistemic Gating Protocol** and are executing empirical micro-spikes to falsify core physical assumptions before committing to any architecture.
- **Core Engineering Breakthroughs & Findings**:
  - **The Jumping-the-Gun Post-Mortem**: Acknowledged teleological solution bias where multi-second browser DOM traversal latencies (6,800 nodes) triggered an immediate leap to a multi-runtime C# rewrite (`014`) without empirical proof that UIA 3 caching avoids underlying browser IPC stalls.
  - **Adversarial Critique & 3 Mutually Exclusive Options**: Evaluated three distinct architectural paths with fatal flaws and hidden operational assumptions: (A) Direct Browser Extension / Native Messaging, (B) Standalone C# .NET 10 FlaUI 5 Daemon, and (C) Pruned In-Process Python Win32/UIA.
  - **4-Gate Epistemic Protocol**: Codified workspace rules and an automated workflow (`.agents/workflows/adversarial-architecture-review.md`) enforcing: (1) Physical logs only → (2) Adversarial red-team → (3) <50-line micro-spike → (4) Architectural blueprint.
  - **Next Empirical Step (Gate 3 Micro-Spikes)**: Measuring raw latency across two minimal scripts: compiled C# FlaUI 5 `CacheRequest` (`spike_csharp_flaui_cache.cs`) vs shallow Win32 top-level caching in Python (`spike_win32_shallow_python.py`).
- **Key Documentation**:
  - 🧠 **[ADCE Living Context Hub](../accessibility_mcp/CONTEXT.md)**
  - 🛡️ **[Epistemic Recalibration & Adversarial Review (015)](../accessibility_mcp/015_recalibration_and_adversarial_architecture_review.md)**
  - 🚀 **[C# Context Daemon Handover Blueprint (014)](../accessibility_mcp/014_csharp_daemon_handover_and_skill_spec.md)** *(Exploratory Blueprint - Paused)*
  - 📑 **[Empirical Post-Mortem & WinEvent Diagnostics (013)](../accessibility_mcp/013_v23_empirical_postmortem_and_event_diagnostics.md)**
  - 📊 **[Live Empirical Tab Extraction Report (012)](../accessibility_mcp/012_empirical_tab_extraction_report.md)**
  - 🔬 **[Landscape Review, FlaUI & Dual-Plane Architecture (011)](../accessibility_mcp/011_flaui_evaluation_and_dual_plane_architecture.md)**
  - 📈 **[Live Telemetry Benchmarks & Multi-Container Diagnostics (010)](../accessibility_mcp/010_telemetry_benchmarks_and_live_findings.md)**
  - ⚙️ **[PyVDA COM Lifecycle Analysis (001)](../pyvda/001_pyvda_rpc_and_com_lifecycle_analysis.md)**

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
