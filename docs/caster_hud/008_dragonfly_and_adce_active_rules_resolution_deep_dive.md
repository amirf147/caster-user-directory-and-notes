[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](005_caster_hud_requirements_and_specifications.md) › **008: Dragonfly & ADCE Active Rules Resolution Deep Dive**

---

# 008 — Caster Heads-Up Display: Dragonfly & ADCE Active Rules Resolution Deep Dive

**Document ID**: `CASTER-DOC-HUD-008`  
**Status**: Educational Explainer & Technical Deep Dive  
**Target Subsystem**: `castervoice/asynch/hud/`, `castervoice/lib/ctrl/mgr/rule_maker/`, `caster_user_content/util/adce_bridge.py`  
**Authors**: Antigravity Principal Architecture Team (Pair Programming with Amir Farhadi)  

---

## 1. Overview & Core Questions

This document provides a comprehensive, educational deep dive into how Caster, Dragonfly, and the Active Desktop Context Engine (ADCE) work together to resolve active voice rules, evaluate desktop context, and display real-time feedback in the Heads-Up Display (HUD).

Specifically, it answers:
1. **How does Caster know which rules are active?**
2. **How does `IDETerminal` know when focus is inside the VS Code / Antigravity integrated terminal?**
3. **When are rules evaluated by Dragonfly, and why did clicking without speaking not immediately update the HUD?**
4. **Why did `Repeater1` and `PreparedRule` appear in the Active Rules strip?**
5. **How can focus tracking be designed with a modular, cross-platform architecture rather than hardcoded Win32 coupling?**

---

## 2. The Anatomy of a Rule in Caster & Dragonfly

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             DRAGONFLY GRAMMAR                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Name: "IDETerminal_g4"                                                    │
│ • Context: AppContext(executable="code") & FuncContext(is_terminal_focused) │
│ • Rules: [ IDETerminalRule (MappingRule) ]                                  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Context.matches(window_info)
                                       ▼
                     ┌───────────────────────────────────┐
                     │ TRUE  ──► grammar.rules[0].active │
                     │ FALSE ──► rule is deactivated     │
                     └───────────────────────────────────┘
```

In Dragonfly, speech commands are organized into **Rules** (`MappingRule`, `CompoundRule`), which are hosted inside a **Grammar**.

Every Grammar possesses an optional `context` object:
* **Global Grammar (`context=None`)**: Always active across the entire operating system (e.g. `navigation`, `alphabet`, `numbers`, `caster_rule`).
* **Application-Scoped Grammar (`context=AppContext(...)`)**: Evaluates the foreground process executable (e.g. `code.exe`, `chrome.exe`) and window title.
* **Micro-Scoped Grammar (`context=AppContext(...) & FuncContext(...)`)**: Evaluates both the foreground window AND an arbitrary Python callable that returns `True` or `False`.

---

## 3. How `IDETerminal` Works (ADCE & Dragonfly Integration)

In `caster_user_content/rules/apps/vscode/ide_terminal.py`:

```python
def get_rule():
    return IDETerminalRule, RuleDetails(
        name="IDETerminal",
        executable=["Code", "Antigravity", "Antigravity IDE", "cursor", "Windsurf"],
        title=["Visual Studio Code", "Antigravity", "Antigravity IDE", "Cursor"],
        function_context=is_ide_terminal_focused,  # <--- ADCE Hook
    )
```

When Caster loads this rule during startup:
1. `MappingRuleMaker.create_non_ccr_grammar()` constructs a Dragonfly `Grammar`:
   $$\text{context} = \text{AppContext}(\text{executable}=\dots, \text{title}=\dots) \;\&\; \text{FuncContext}(\text{function}=\text{is\_ide\_terminal\_focused})$$
2. `is_ide_terminal_focused` points to `adce_bridge.py`:
   ```python
   def is_ide_terminal_focused(**kwargs):
       return adce.is_ide_terminal()
   ```
3. **The ADCE Pipeline**:
   - The standalone C# ADCE daemon (`ADCE.Daemon.exe`) runs on localhost port `8424`.
   - ADCE attaches native Windows UI Automation (UIA) event hooks (`EVENT_SYSTEM_FOREGROUND`, `EVENT_OBJECT_FOCUS`).
   - When the user focuses the terminal pane in VS Code or Antigravity IDE, ADCE extracts the control pattern and identifies `{SemanticZone: "IntegratedTerminal"}`.
   - ADCE streams this snapshot over Server-Sent Events (SSE) to `adce_bridge.py`.
   - `adce_bridge.py` updates its internal in-memory variable `self._current_zone = "IntegratedTerminal"` in RAM.
4. **Sub-Microsecond Context Evaluation**:
   - When Dragonfly tests `context.matches()`, `is_ide_terminal_focused()` simply checks the RAM variable (`_current_zone == "IntegratedTerminal"`).
   - This takes **$< 0.001\text{ ms}$** and requires zero IPC roundtrips on the speech thread.

---

## 4. Why Clicking Away Without Speaking Did Not Update the HUD

A key nuance in speech recognition architectures is the **context evaluation lifecycle**:

```
User Clicks Window / Terminal ──► OS changes focus
                                   │
                                   ├─► ADCE Daemon sees it (UIA event hook)
                                   │
                                   └─► Dragonfly IS IDLE (Waiting for microphone audio)
                                       └── Does NOT evaluate context until next speech event!
```

* **Speech Event Driven**: Dragonfly's engine loop evaluates `grammar.context.matches()` when an audio utterance is recognized.
* **Silent Window Switches**: When a user clicks with the mouse or presses Alt+Tab *without speaking*, Dragonfly's engine does not re-evaluate active grammars.
* Therefore, the HUD remained showing the previous rule state until speech occurred or an explicit toggle command was issued.

---

## 5. Why `Repeater1` and `PreparedRule` Appeared

When Caster merges Continuous Command Recognition (CCR) rules via `CCRMerger2`:
1. `CCRMerger2` combines multiple rules into sequence repetition structures (`RepeatRule` with auto-generated names: `Repeater1`, `Repeater2`, etc.).
2. Individual `MergeRule` instances wrap their dictionary mapping in an internal `PreparedRule` class.
3. `CCRMerger2` attaches a `negation_context` (a `FuncContext`) to the global CCR grammar so it only activates when no app-specific CCR rules match.
4. Our initial filter checked `if grammar.context is not None:`. Because the global CCR grammar had a `negation_context`, it was falsely identified as an application-specific rule, exposing the internal merger class names `Repeater1` and `PreparedRule`.

**The Permanent Solution**:
* Exclude internal merger artifacts matching `Repeater\d+`, `PreparedRule`, `RepeatRule`, `ccr`, and `_.*`.
* Inspect only genuine application-scoped grammars (`AppContext` or non-merger `FuncContext`).

---

## 6. Modular, Cross-Platform Architecture for Window Focus (Future-Proofing)

To avoid hardcoding Windows-specific Win32 APIs into core state and UI layers, we establish a **Pluggable Focus Provider Pattern**:

```
                        ┌───────────────────────────────┐
                        │      IFocusObserver (ABC)     │
                        ├───────────────────────────────┤
                        │ + start()                     │
                        │ + stop()                      │
                        │ + get_current_focus()         │
                        └───────────────┬───────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│ Win32HookFocusObserver  │ │  AdceStreamFocusObserver│ │   Darwin/LinuxObserver  │
├─────────────────────────┤ ├─────────────────────────┤ ├─────────────────────────┤
│ • SetWinEventHook       │ │ • Subscribes to SSE     │ │ • NSWorkspace (macOS)   │
│ • EVENT_SYSTEM_FG       │ │ • MCP JSON-RPC port 8424│ │ • xdotool / Wayland     │
│ • Zero polling          │ │ • Rich semantic zones   │ │ • Future cross-platform │
└─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘
```

### Key Architectural Benefits:
1. **Decoupled from OS**: The HUD and Caster core depend strictly on `IFocusObserver` events (`DesktopContextEvent`, `ActiveRulesEvent`).
2. **Pluggable Providers**:
   - **Win32 Hook Provider**: Native Windows zero-polling via `SetWinEventHook`.
   - **ADCE Streaming Provider**: Rich semantic micro-zones from ADCE daemon.
   - **macOS / Linux Providers**: Can be slotted in without touching the HUD Qt widget or state reducers.
3. **Graceful Fallbacks**: If no native hook is supported on a given environment, a `NullFocusObserver` or low-overhead timer safely takes over.

---

*Recorded in `docs/caster_hud/008_dragonfly_and_adce_active_rules_resolution_deep_dive.md`.*
