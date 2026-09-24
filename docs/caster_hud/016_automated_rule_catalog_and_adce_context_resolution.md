[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](005_caster_hud_requirements_and_specifications.md) › **016: Automated Rule Catalog & ADCE Context Resolution**

---

> [!NOTE]
> **Document Status**: *Active Production Architecture & Canonical Reference (NOT SUPERSEDED)*.  
> Documents the automated AST-based rule catalog, dynamic context resolver, and the architectural separation between out-of-process OS context observation (ADCE) and in-process voice grammar resolution.

# 016: Automated Rule Catalog, AST Inspection, and Decoupled ADCE Context Resolution

This document specifies the architecture of the **Automated Rule Catalog** (`context_resolver.py`) within the `taskbar_hud` plugin. It details how Caster voice rules are indexed, filtered against active configuration, and matched to real-time Active Desktop Context Engine (ADCE) telemetry without hardcoded dictionaries or speech engine coupling.

---

## 1. Problem Statement & Root Cause Analysis

### Static Dictionary Fragility
In early iterations of the Taskbar HUD telemetry bridge, contextual rule resolution relied on a manually maintained dictionary (`PROCESS_RULES_MAP`) and hardcoded title patterns (`BROWSER_TITLE_RULES`):

```python
# Anti-pattern: Static, incomplete dictionary
PROCESS_RULES_MAP = {
    "winword": ["Word CCR"],
    "excel": ["Excel CCR"],
    "code": ["CustomVSCode", "CustomVSCode CCR"],
    "firefox": ["Firefox CCR", "Firefox Extended"],
}
```

This implementation exhibited four structural defects:
1. **Omission of Companion Rules:** `winword` was hardcoded solely to `Word CCR`, omitting standard non-CCR voice commands in `CustomMSWordRule`. Similarly, `excel` mapped only to `Excel CCR`, omitting `ExcelRule`.
2. **Duplicate Source of Truth (Split-Brain):** Every Caster rule declares its target executables and window titles inside its own `RuleDetails` configuration object. Maintaining a parallel dictionary in `context_resolver.py` created duplicate metadata that drifted out of sync whenever rules were added or updated.
3. **Configuration Ignorance:** The static map had no awareness of `rules.toml`. If a user disabled `Word CCR` or `CustomMSWordRule` in Caster's configuration, the HUD continued to display them as active when Word was focused. Conversely, newly enabled custom rules never appeared on the HUD unless manually added to the dictionary.
4. **Fragile Sub-Zone Coupling:** The resolver contained ad-hoc logic attempting to guess when to activate `IDETerminalRule` by checking whether IDE process names matched specific zone strings. Because semantic zone labeling across editors was still being standardized, this heuristic introduced unnecessary failures.

---

## 2. Separation of Concerns: ADCE vs. Context Resolver

A common architectural question is whether the Active Desktop Context Engine (ADCE) should resolve voice rules directly. The answer is negative due to boundary isolation.

### Functional Boundary
The responsibilities between the OS sensor and the voice grammar resolver are strictly separated:

| Attribute | Active Desktop Context Engine (ADCE) | Context Resolver (`taskbar_hud`) |
| :--- | :--- | :--- |
| **Execution Domain** | Out-of-process daemon (Port 8424) | In-process Caster plugin (`taskbar_hud`) |
| **System Scope** | Windows OS (Win32, UI Automation) | Caster runtime and user configuration |
| **Core Function** | Detects active process, window title, zone, and file | Resolves active Dragonfly voice rules |
| **Configuration Dependency** | Zero Caster dependencies | Reads Caster rule files and `rules.toml` |
| **Output Type** | Hardware and window telemetry | Human-readable voice rule tag strings |

ADCE is an OS-level focus sensor. It reports raw desktop facts:
```json
{
  "process_name": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
  "window_title": "Google Gemini - Mozilla Firefox",
  "semantic_zone": "content",
  "active_file": ""
}
```

ADCE has no knowledge of Python, Dragonfly grammars, CCR rule mergers, or user-specific speech toggles. Delegating rule resolution to ADCE would couple a language-agnostic desktop daemon to Caster internal grammar formats.

Instead, ADCE provides the sensory input, and `context_resolver.py` performs the Caster-specific domain interpretation.

---

## 3. Architecture: Automated Rule Cataloger via AST

The resolver replaces static dictionaries with an automated AST inspection engine.

```
┌─────────────────────────────────────────────────────────────┐
│                     Rule Discovery Phase                    │
│   Scans:                                                    │
│     - caster_user_content/rules/ (User Rules)               │
│     - castervoice/rules/         (Built-in Rules)           │
└──────────────────────────────┬──────────────────────────────┘
                               │ ast.parse() (Zero imports / no side effects)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    In-Memory RuleCatalog                    │
│   - _proc_map: { "winword": [RuleEntry, ...], ... }         │
│   - _title_rules: [ RuleEntry(titles=["gemini"]), ... ]     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │ Telemetry event arrives from ADCE
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Configuration Filter Gate                   │
│   Cross-references candidate rules against _enabled_ordered │
│   in settings/rules.toml (monitored via file mtime)         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Deduplicated Active Rule Tags                  │
│   Output: "Firefox CCR, Firefox Extended, Gemini"           │
│   Transmitted across Named Pipe to Taskbar HUD              │
└──────────────────────────────┴──────────────────────────────┘
```

### Static Analysis Without Runtime Execution
Importing all 160+ rule files at startup would trigger substantial side effects, initialize Dragonfly objects, and slow down startup. The `RuleCatalog` avoids module execution by inspecting the Abstract Syntax Tree directly:

```python
tree = ast.parse(file_path.read_text(encoding="utf-8", errors="ignore"))
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_rule":
        # Extract RuleDetails keywords: name, executable, title, ccrtype
        # Extract returned RuleClass symbol
```

This approach yields complete metadata for every rule:
- **Rule Class Name (RCN):** e.g., `CustomMSWordRule`, `MSWordCcrRule`, `GeminiRule`.
- **Target Executables:** Normalized lowercase executable stems (`winword`, `code`, `waterfox`).
- **Target Window Titles:** Lowercase title matching patterns (`gemini`, `youtube`).
- **CCR Indicator:** Extracted from `details.ccrtype` or class naming convention.

### Dynamic Configuration Synchronization
Rules displayed on the HUD must reflect actual configuration state. The `RuleCatalog` caches active rule identifiers from `rules.toml`:
1. It resolves `rules.toml` via `settings.SETTINGS["paths"]["RULES_CONFIG_PATH"]` or the relative user directory fallback `settings/rules.toml`.
2. It tracks the file modification timestamp (`st_mtime`).
3. When the configuration changes on disk, `refresh_enabled()` automatically reloads `_enabled_ordered` and updates the active set without requiring a Caster restart.

### Display Name Normalization
Rule display names are normalized deterministically:
- Generic suffixes (`Rule`, ` rule`) are stripped.
- Inconsistent vendor capitalization is corrected (e.g., `fire fox` to `Firefox`).
- Continuous Command Recognition (CCR) grammars are formatted with a trailing ` CCR` tag (e.g., `CustomVSCodeCcrRule` to `CustomVSCode CCR`).
- Title-only rules are converted to title case (e.g., `youtube rule` to `Youtube`).

### Terminal Zone Scope Reduction
As requested by engineering review, sub-zone heuristics for `IDETerminalRule` were removed from `context_resolver.py`. ADCE continues to report `semantic_zone` (`terminal`, `editor`, `sidebar`) directly to the Taskbar HUD for visual zone labeling. However, rule resolution remains strictly focused on deterministic process and title matching.

---

## 4. Telemetry Pipeline & Latency Profile

The context resolution pipeline executes across four sequential stages:

```
[ ADCE Daemon ] 
      │ (SSE HTTP Stream: process_name, window_title, semantic_zone)
      ▼
[ AdceBridgeClient ]
      │ (Dispatches to registered context listeners)
      ▼
[ TaskbarHudPlugin._on_adce_context_changed ]
      │ (Invokes resolve_active_rules)
      ▼
[ RuleCatalog.resolve ]
      ├── 1. Normalize process stem (Path(process).stem.lower())
      ├── 2. Retrieve process candidates from in-memory index
      ├── 3. Match window title against title-only rules
      ├── 4. Filter against cached _enabled_rcns from rules.toml
      └── 5. Deduplicate and format output string
      │
      ▼
[ TaskbarHudBridgeClient.send_update ]
      │ (Named Pipe: \\.\pipe\CasterTaskbarHud)
      ▼
[ Windows 11 Taskbar HUD Mod ]
```

### Performance Characteristics
Benchmarking on the reference workstation yielded the following metrics:
- **Catalog Construction:** 164 rule modules (79 user rules, 85 core rules) scanned, parsed via AST, and indexed in **98 milliseconds** during initial startup.
- **Per-Focus Resolution:** Process lookup, title matching, and set-intersection against enabled rules execute in **0.03 milliseconds** per window switch.
- **Memory Footprint:** The entire indexed catalog occupies less than **180 KB** of memory.

---

## 5. Empirical Verification & Test Matrix

The automated resolver was verified against target applications under active configuration:

| Active Window Focus | Process Name | Window Title | Resolved Active Rules | Verification Note |
| :--- | :--- | :--- | :--- | :--- |
| **Waterfox (Gemini)** | `waterfox.exe` | `Google Gemini - Waterfox` | `Firefox CCR, Firefox Extended, Gemini` | Matches process stem and website title rule. |
| **Waterfox (Standard)** | `waterfox.exe` | `Mozilla Firefox` | `Firefox CCR, Firefox Extended` | Standard browser rules active; site rule excluded. |
| **VS Code** | `code.exe` | `project.py - Visual Studio Code` | `CustomVSCode, CustomVSCode CCR` | Matches primary editor executable aliases. |
| **Antigravity IDE** | `antigravity ide.exe` | `agent.py - Antigravity IDE` | `Antigravity IDE, CustomVSCode, CustomVSCode CCR` | Accurately activates agent commands and editor CCR. |
| **Microsoft Word** | `WINWORD.EXE` | `Document1 - Word` | `Global` (when disabled) / `Custom Microsoft Word, MSWord CCR` (when enabled) | Correctly respects `rules.toml` disabled state. |
| **Windows Terminal** | `windowsterminal.exe` | `Windows PowerShell` | `PowerShell, PowerShell CCR` | Accurately maps terminal host shell alias via title. |
| **File Explorer** | `explorer.exe` | `Downloads` | `File Explorer, Explorer` | Matches native shell navigation rules. |

---

## 6. Summary of Architectural Guarantees

1. **Zero Core Modifications:** Operates completely within user space (`caster_user_content/plugins/taskbar_hud/context_resolver.py`). No changes were made to Caster core (`castervoice`).
2. **Zero In-Process Window Hooks:** Uses out-of-process ADCE telemetry exclusively.
3. **No Duplicate Configuration:** The rule source files themselves serve as the single source of truth for target executables and window titles.
4. **Configuration Fidelity:** Rules marked disabled in `rules.toml` are excluded from the HUD display tag strip.
