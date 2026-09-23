[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](005_caster_hud_requirements_and_specifications.md) › **015: Foundational Plugin System & HUD Modularization**

---

> [!NOTE]
> **Document Status**: *Active Production Architecture & Canonical Reference (NOT SUPERSEDED)*.  
> Documents the Caster Plugin Architecture (`PluginBase`, `PluginManager`), the separation of the HUD taxonomy, and the boundary between Caster source and user content.

# 015: Caster Heads-Up Display: Foundational Plugin System & HUD Modularization

This document establishes the official architecture for Caster's **Plugin System**, formalizes the **HUD Taxonomy** across upstream and custom implementations, and defines the structural boundary between the Caster source repository and the user configuration directory.

---

## 1. Executive Summary & Root Cause Analysis

### The Evolutionary Problem
Prior to this architecture, Caster lacked a native plugin lifecycle. Caster's grammar loading subsystem (`ContentLoader`) recognized only three extension primitives:
1. `get_rule()`: Dragonfly voice grammars.
2. `get_transformer()`: Text formatting transformers.
3. `get_hook()`: Dragonfly CCR merger hooks.

Because Caster had no mechanism to manage non-grammar integrations, developers were forced into two architectural anti-patterns:
- **Hardcoding in Core Startup**: In `_caster.py`, conditional statements were hardcoded to launch external services (such as Sikuli and the PyQt HUD).
- **Disguising Services as Voice Rules**: Background bridges, Named Pipe clients, XML-RPC servers, and daemon launchers were implemented inside dummy `MappingRule` classes (such as `TaskbarHudRule`, `ContextEngineLauncherRule`, and `CasterHotkeyToggleRule`) simply so `ContentLoader` would import the file on startup.

### The Architectural Resolution
Caster Core now provides a first-class **Plugin Architecture** based on:
1. **`PluginBase`**: A standard lifecycle contract (`initialize`, `start`, `stop`, `get_rules`).
2. **`PluginManager`**: An orchestrator that discovers plugins across built-in and user directories, executes lifecycle phases, isolates failures, and registers companion voice grammars.
3. **`settings.toml [plugins]`**: A centralized configuration table governing all optional subsystems.
4. **Externalized Distribution Model**: Caster core remains minimal, retaining only baseline fallback plugins (`standard_hud` and `sikuli`). Advanced integrations (`themed_hud`, `taskbar_hud`, `adce`) reside in user space (`caster_user_content/plugins/`) or external repositories (`caster-plugins`), installable via `plugin_cli`.

---

## 2. HUD Taxonomy: Standard vs. Themed vs. Taskbar

Caster supports three distinct Heads-Up Display interfaces. Each is encapsulated as an independent plugin:

```
+-----------------------------------------------------------------------------------+
|                                  Caster Core                                      |
|                                                                                   |
|  - PluginManager: Discovers, instantiates, and manages plugin lifecycles          |
|  - settings.toml [plugins]: Governs active display subsystems                      |
+-----------------------------------------+-----------------------------------------+
                                          |
          +-------------------------------+-------------------------------+
          |                               |                               |
          v                               v                               v
+-----------------------+     +-----------------------+     +-----------------------+
|     standard_hud      |     |      themed_hud       |     |      taskbar_hud      |
| (Upstream Simple HUD) |     |  (Modular Custom HUD) |     |  (Windhawk Taskbar)   |
|                       |     |                       |     |                       |
| - Monolithic XML-RPC  |     | - QSS Theming (10+)   |     | - Named Pipe bridge   |
| - Basic history box   |     | - Opacity controls    |     | - Taskbar notification|
| - Rules tree view     |     | - Status header bar   |     | - Zero desktop window |
| - Minimal footprint   |     | - ADCE context strip  |     | - Fast visual feedback|
|                       |     | - Active rules pills  |     | - Windhawk mod driver |
|                       |     | - Frameless drag mode |     |                       |
+-----------------------+     +-----------------------+     +-----------------------+
```

### 1. Standard Upstream Caster HUD (`standard_hud`)
- **Origin**: Upstream Caster master (`dictation-toolbox/Caster`).
- **Characteristics**: Monolithic window, basic text area, minimal resource overhead.
- **Role**: Retained as an official baseline plugin for minimal or legacy environments.

### 2. Custom Modular/Themed HUD (`themed_hud`)
- **Origin**: Developed in branch `custom-setup`.
- **Characteristics**: Modular architecture communicating over a local IPC socket (`castervoice/asynch/hud/`). Supports 10+ accessible themes (Dark, Solarized, Nord, Monokai, High Contrast, Amber CRT), independent background and letter opacity sliders, live status header, sub-window ADCE context strip, active rules tag bar, and frameless drag mode.
- **Role**: The full-featured desktop heads-up display plugin.

### 3. Taskbar HUD (`taskbar_hud`)
- **Origin**: Windows 11 Taskbar Windhawk mod integration.
- **Characteristics**: Runs with zero desktop window footprint. Injects real-time speech telemetry directly into the Windows taskbar clock/notification area via Named Pipe (`\\.\pipe\CasterTaskbarHud`).
- **Role**: Low-profile, distraction-free voice display for users who do not want an on-screen desktop overlay.

---

## 3. Active Desktop Context Engine (ADCE) Plugin

The Active Desktop Context Engine is an out-of-process semantic focus provider (`http://127.0.0.1:8424/sse`).

In the externalized plugin system, it is encapsulated as `caster_user_content/plugins/adce/`:
- **Lifecycle**: Connects to the local ADCE daemon on port 8424 during `start()`; disconnects during `stop()`.
- **In-Memory Cache**: Maintains an atomic RAM cache updated via chunked SSE stream reading.
- **Dragonfly Integration**: Exports sub-microsecond (< 0.001 ms) `FuncContext` predicates:
  - `is_ide_terminal_focused()`: Gating for integrated terminals.
  - `is_ide_editor_focused()`: Gating for code editor buffers.
  - `is_ide_git_commit_focused()`: Gating for Git commit input boxes.
- **Pub-Sub Context Listeners**: Downstream plugins (such as `taskbar_hud` and `themed_hud`) register callbacks via `add_context_listener(callback)` to receive real-time updates without polling.

---

## 4. Configuration Schema (`settings.toml`)

All plugins are configured in `settings/settings.toml` under the `[plugins]` table:

```toml
[plugins]
# HUD Selection
themed_hud = true      # Enable the next-gen customizable modular HUD
standard_hud = false   # Disable the original legacy upstream HUD
taskbar_hud = true     # Enable the Windows 11 Taskbar Windhawk mod bridge

# Core Integrations
adce = true            # Enable Active Desktop Context Engine SSE bridge
sikuli = false         # Visual GUI automation server proxy
```

### Plugin-Specific Configuration Options
Plugins can read nested configuration parameters from `settings.toml`:
```toml
[plugins.taskbar_hud]
pipe_name = "CasterTaskbarHud"

[plugins.adce]
host = "127.0.0.1"
port = 8424
```

---

## 5. Plugin Lifecycle Contract (`PluginBase`)

All plugins implement `castervoice/lib/plugin.py`:

```python
class PluginBase(object):
    name = "base_plugin"
    version = "1.0.0"
    description = "Base Caster Plugin"

    def initialize(self, nexus, config):
        """Pre-speech engine phase: register print handlers, mic observers, and listeners."""
        pass

    def start(self):
        """Post-engine configuration phase: start worker threads, named pipes, or GUI loops."""
        pass

    def stop(self):
        """Shutdown phase: cleanly terminate workers and release system resources."""
        pass
```

### Execution Timeline During Caster Startup

1. **Nexus Initialization**: Caster Core creates the `Nexus`, `GrammarManager`, `EngineModesManager`, and `printer` delegator.
2. **Plugin Discovery**: `PluginManager` scans `castervoice/plugins/` and `caster_user_content/plugins/` for enabled plugins.
3. **Plugin Initialization**: `PluginManager` invokes `initialize(nexus, config)` on every active plugin.
   - `taskbar_hud` registers its print message handler with `printer.get_delegating_handler()`.
   - `taskbar_hud` registers a mic observer on `EngineModesManager.add_mic_listener()`.
   - `themed_hud` registers `HudPrintMessageHandler`.
4. **Engine Configuration**: Dragonfly engine is initialized.
5. **Plugin Startup**: `PluginManager` invokes `start()` on all active plugins.
   - `adce` connects to the SSE stream.
   - `taskbar_hud` opens the Named Pipe worker.
   - `themed_hud` starts the PyQt HUD process.
6. **Shutdown / Reload**: When Caster terminates, `PluginManager` invokes `stop()` in reverse order.

---

## 6. Boundary Between Caster Source and User Content

| Item | Location | Governing Mechanism |
|---|---|---|
| **Caster Core** | `castervoice/lib/` | Core Python classes (`PluginBase`, `PluginManager`) |
| **Core Baseline Plugins** | `castervoice/plugins/` | Minimal in-tree fallbacks (`standard_hud`, `sikuli`) |
| **Plugin CLI** | `castervoice/bin/plugin_cli.py` | Command-line plugin management (`list`, `install`, `remove`) |
| **User Plugins** | `caster_user_content/plugins/` | Externalized integrations (`themed_hud`, `taskbar_hud`, `adce`) |
| **User Voice Rules** | `caster_user_content/rules/` | `GrammarManager` & `settings/rules.toml` |
| **User Configuration** | `settings/` | `settings.toml`, `rules.toml` |

### Invariants & Rules
1. **Zero Core Inverted Dependencies**: Caster Core production files (`_caster.py`, `castervoice/lib/`, `castervoice/asynch/`) must never import from `caster_user_content`.
2. **Decoupled User Space Plugins**: Advanced drivers (Named Pipe clients, SSE decoders, and PyQt overlays) belong in `caster_user_content/plugins/` as modular packages, preserving core Caster minimalism.
3. **Zero Pseudo-Rules**: Never create a `MappingRule` whose sole purpose is launching background services. Use `PluginBase` instead.
4. **User Rule Consumption**: User voice rules (such as `IDETerminalRule`) query plugins directly via root bare imports (such as `from adce import is_ide_terminal_focused`) since `PluginManager` registers the user plugins path on `sys.path`.

---

## 7. Upstream Contribution Strategy

This architecture creates an isolated path for contributing improvements back to upstream Caster (`dictation-toolbox/Caster`):

1. **Step 1: Foundational Plugin PR**:
   - Submit `PluginBase` and `PluginManager` to upstream Caster.
   - Wraps the existing upstream HUD in `standard_hud` and Sikuli in `sikuli`.
   - Core behavior remains 100% backward compatible.
2. **Step 2: Modular Plugins**:
   - The `themed_hud`, `taskbar_hud`, and `adce` integrations are externalized into `caster_user_content/plugins/` or distributed via the dedicated `caster-plugins` repository without modifying upstream core code.
