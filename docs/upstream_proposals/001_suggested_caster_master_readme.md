[ 🏠 Docs Home ](../README.md) › **Suggested Upstream Caster README**

---

> [!NOTE]
> **Document Status**: *Draft Proposal for Upstream Master README*  
> This document stages a proposed root `README.md` for upstream Caster (`dictation-toolbox/Caster`) when the Foundational Plugin Architecture ([Doc 015](../caster_hud/015_foundational_plugin_system_and_hud_modularization.md)) is submitted as a feature branch or pull request. It is stored here in the user documentation repository to avoid introducing unmerged documentation changes directly into the Caster source repository while work remains in local testing.

# Proposed Upstream Caster README

# Caster

Caster is a voice programming and desktop automation platform built on top of the Dragonfly framework. It enables hands-free computer operation, code navigation, and system control across applications, programming languages, and operating system environments.

For complete user guides, command reference lists, and documentation index, see the [Documentation Hub](docs/README.md).

---

## Architecture Overview

Caster is organized into distinct execution layers to maintain clean boundaries between speech engine coordination, modular integrations, and user-defined grammars:

1. **Caster Core (`castervoice/lib/`)**:
   - Manages speech recognition engine connections (Kaldi, Dragon NaturallySpeaking, Windows Speech Recognition).
   - Coordinates rule merging, continuous command recognition (CCR), and grammar activation via `Nexus` and `GrammarManager`.
2. **Plugin Architecture (`castervoice/lib/plugin.py`, `castervoice/lib/ctrl/mgr/plugin_manager.py`)**:
   - Provides a standard lifecycle contract (`PluginBase`) with `initialize(nexus, config)`, `start()`, and `stop()` phases.
   - Isolates subsystem failures so that an error in an individual plugin does not crash Caster core or prevent speech engine startup.
   - Governs all visual interfaces, hardware bridges, and background services without hardcoding imports in `_caster.py` or disguising services as dummy voice rules.
3. **Official Plugins (`castervoice/plugins/`)**:
   - `themed_hud`: Advanced PyQt Heads-Up Display featuring 10+ QSS themes, independent background and text opacity controls, live status header, sub-window ADCE context strip, active rules tag bar, and frameless drag mode.
   - `standard_hud`: Lightweight monolithic Caster Heads-Up Display from upstream master, retained as a minimal resource option.
   - `taskbar_hud`: Windows 11 Taskbar Windhawk mod Named Pipe bridge (`\\.\pipe\CasterTaskbarHud`), projecting real-time speech telemetry directly into the Windows Shell adjacent to the system tray with zero desktop window footprint.
   - `adce`: Active Desktop Context Engine SSE client on port 8424, maintaining an atomic in-memory cache and exposing high-speed `FuncContext` predicates (`is_ide_terminal_focused`, `is_ide_editor_focused`).
   - `sikuli`: Out-of-process visual automation proxy for Sikulix integration.
4. **User Content Space (`caster_user_content/`)**:
   - Located in `%LOCALAPPDATA%\Caster\caster_user_content\` (or configured via environment variables).
   - Reserved strictly for personal voice grammars (`rules/`), custom macros, and private configurations (`settings/settings.toml`, `settings/rules.toml`).

---

## Configuration (`settings.toml`)

Plugins are enabled or disabled declaratively under the `[plugins]` table in `settings.toml`:

```toml
[plugins]
# Heads-Up Display Selection
themed_hud = true      # Advanced modular PyQt HUD with themes and opacity controls
standard_hud = false   # Upstream monolithic baseline HUD
taskbar_hud = true     # Windows 11 Taskbar Windhawk mod Named Pipe bridge

# Subsystem Integrations
adce = true            # Active Desktop Context Engine SSE client
sikuli = false         # Visual automation proxy
```

---

## Running Caster

Caster requires Python 3.10 (64-bit) on Windows:

```powershell
# Run via Python 3.10
py -3.10 _caster.py

# Alternatively, run via the batch launcher
.\Run_Caster_Kaldi_Latest.bat
```

---

## Running the Automated Test Suite

Run the verified test suite covering plugin management, HUD interfaces, telemetry pipelines, and engine modes from the repository root:

```powershell
$env:PYTHONPATH="$env:LOCALAPPDATA\caster;."
py -3.10 -m unittest `
    tests/lib/ctrl/mgr/test_plugin_manager.py `
    tests/test_antigravity_context_resolution.py `
    tests/test_focus_transition_sequence.py `
    tests/test_taskbar_hud_decoupled.py `
    tests/test_hud_core.py `
    tests/test_hud_ipc.py `
    tests/test_hud_theming.py `
    tests/test_hud_ui.py `
    tests/lib/test_printer.py `
    tests/lib/ctrl/test_EngineModesManager.py
```

---

## Documentation & References

- [Documentation Hub](docs/README.md): Master navigation, command references, and tutorials.
- [Plugin System & HUD Architecture Spec (Doc 015)](docs/caster_hud/015_foundational_plugin_system_and_hud_modularization.md): Architectural blueprint for `PluginBase`, `PluginManager`, and the HUD taxonomy.
- [Upstream Repository](https://github.com/dictation-toolbox/Caster): Upstream source repository and issue tracker.
