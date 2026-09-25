[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](005_caster_hud_requirements_and_specifications.md) › **012: Taskbar HUD Windhawk Injection & Telemetry Explainer**

---

> [!NOTE]
> **Document Status**: *Active Production Specification (Taskbar HUD Subsystem; Published & Not Superseded)*.  
> Defines the Windhawk XAML injection, named pipe IPC, and single command strip architecture for the Windows 11 Taskbar HUD. The mod has been officially published in the `windhawk-mods` catalog (commit `b02f3654`) and is maintained in the standalone repository **[`amirf147/caster-taskbar-hud`](https://github.com/amirf147/caster-taskbar-hud)**.

# 012: Taskbar HUD Windhawk Mod Architecture, Telemetry Disconnects, & Unified Strip Pivot

**Document ID**: `CASTER-DOC-HUD-012`  
**Status**: Active Specification (Taskbar HUD Subsystem; Not Superseded)  
**Target Subsystems**: `mods/caster-taskbar-hud.wh.cpp`, `caster_user_content/util/taskbar_hud_bridge.py`, `caster_user_content/hooks/taskbar_hud_hook.py`, `castervoice/asynch/hud_support.py`  
**Authors**: Antigravity Principal Systems Architecture (Pair Programming with Amir Farhadi)  

---

## 1. Problem Statement & Operational Context

The Caster Taskbar HUD is a published native Windhawk modification (`caster-taskbar-hud.wh.cpp`) designed to inject real-time voice telemetry directly into the Windows 11 taskbar adjacent to the system tray. During live testing, two primary defects occurred:

1. **Static Telemetry Display**: The UI rendered only fallback values (`Z: --`, `Rules: Global`, `Ready`). Spoken commands produced no visual updates, enabling the Active Desktop Context Engine (ADCE) produced no zone updates, and active contextual rules remained static.
2. **Visual Overlap & Taskbar Encroachment**: The injected UI expanded horizontally into the running window buttons (`WorkerW` / `TaskListButtonPanel`), clipping the rightmost window title (`caster - File Exp...`).

This document details the internal mechanics of the Windhawk XAML injection, explains why the Python telemetry bridge remained disconnected from Caster's speech engine, and defines the architectural pivot to a single, compact command strip that taps into Caster's existing HUD output pipeline.

---

## 2. Windhawk Mod Architecture (`caster-taskbar-hud.wh.cpp`)

The Windhawk modification operates entirely in-process within `explorer.exe`. It consists of four distinct architectural components.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                             EXPLORER.EXE PROCESS                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [taskbar.dll Hook Engine]                                                   │
│    │ CTaskBand::GetTaskbarHost -> XamlRoot                                   │
│    ▼                                                                         │
│  [XAML Injection Target: SystemTrayFrameGrid]                                │
│    ├── Column 0: [ CasterTaskbarHudContainer (StackPanel) ]                  │
│    │     ├── [Z: --]         (adceBorder / adceText)                         │
│    │     ├── [Rules: Global] (rulesBorder / rulesText)                       │
│    │     └── [Ready]         (commandBorder / commandText)                   │
│    └── Column 1+: Native System Tray Icons, Chevron, Clock                   │
│                                                                              │
│  [Named Pipe Server Thread]                                                  │
│    └── Listens on \\.\pipe\CasterTaskbarHud                                  │
│          └── Ingests JSON -> Marshals to UI thread via SetWindowsHookEx      │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Symbol Hooking & XAML Root Acquisition
Windows 11 renders the taskbar using modern Windows UI XAML hosted via XAML Islands inside `Shell_TrayWnd`. The mod hooks five symbols in `taskbar.dll`:
* `CTaskBand::GetTaskbarHost`
* `CSecondaryTaskBand::GetTaskbarHost`
* `TaskbarHost::FrameHeight`
* `std::_Ref_count_base::_Decref`
* `TrayUI::StartTaskbar`

From `TaskbarHost`, the mod extracts the `IUnknown` pointer of the root `FrameworkElement` at runtime offset `TaskbarHost_FrameHeight` (`0x7F` range offset on x86-64). This yields the live `XamlRoot` for both primary and secondary taskbars.

### 2.2 Control Injection into `SystemTrayFrameGrid`
The mod searches the visual tree using `FindChildByName(root, L"SystemTrayFrameGrid")`. Once located:
1. It creates a horizontal `StackPanel` containing three bordered pill boxes (`adceBorder`, `rulesBorder`, `commandBorder`).
2. It inserts a new `ColumnDefinition` at index `0` of `SystemTrayFrameGrid`.
3. It shifts the column index of all existing tray children right by 1 (`Grid::SetColumn(child, col + 1)`).
4. It places `CasterTaskbarHudContainer` in column `0`.

### 2.3 IPC Server & Marshaling
The mod spawns a dedicated background thread running `PipeServerThreadProc`:
* It creates an inbound named pipe: `\\.\pipe\CasterTaskbarHud`.
* It handles client connections asynchronously via `FILE_FLAG_OVERLAPPED` and `ConnectNamedPipe`.
* Incoming byte buffers are parsed as UTF-8 JSON via `winrt::Windows::Data::Json::JsonObject`.
* Updates are marshaled to the taskbar UI thread using `WindhawkUtils::SetWindowSubclassFromAnyThread` and a thread-targeted message pump hook (`WH_CALLWNDPROC` via `RunFromWindowThread`).

---

## 3. Root-Cause Analysis: Why Telemetry Remained Static

The mod initialized correctly, yet no data flowed into the UI. The root causes exist across three distinct boundaries in Caster.

### 3.1 Defect A: `taskbar_hud_hook.py` Was Never Imported or Executed
In `caster_user_content/hooks/taskbar_hud_hook.py`, a `dragonfly.RecognitionObserver` was defined:

```python
class TaskbarHudRecognitionObserver(RecognitionObserver):
    def on_recognition(self, words=None, rule=None, **kwargs):
        bridge = get_taskbar_hud_bridge()
        bridge.send_update(command=" ".join(words), rules=rule.name)

_observer = TaskbarHudRecognitionObserver()
_observer.register()
```

This file resided in `caster_user_content/hooks/`. In Caster's architecture, hooks are loaded by `ContentLoader` and `ContentRequestGenerator`:
1. `ContentRequestGenerator._get_content_type()` scans every `.py` file for specific function signatures:
   - `def get_rule():` -> `ContentType.GET_RULE`
   - `def get_transformer():` -> `ContentType.GET_TRANSFORMER`
   - `def get_hook():` -> `ContentType.GET_HOOK`
2. `taskbar_hud_hook.py` contained no `def get_hook():` function.
3. Because the signature was absent, Caster skipped the file completely during startup.
4. The module was never imported, `_observer.register()` was never executed, and `TaskbarHudBridgeClient` was never instantiated.

### 3.2 Defect B: Caster Hooks Are CCR Lifecycle Hooks, Not Speech Observers
Even if `def get_hook():` were added to `taskbar_hud_hook.py`, Caster's hook infrastructure (`castervoice/lib/merge/ccrmerging2/hooks/`) is designed exclusively for CCR rule activation and deactivation events (`EventType.ACTIVATION`). It does not handle live audio decoding or word recognition streams. Placing a Dragonfly `RecognitionObserver` inside Caster's `hooks/` directory represented an architectural category error.

### 3.3 Defect C: ADCE Bridge Updates Were Never Forwarded to the Pipe
The user observed `Z: --` despite ADCE running. The telemetry path failed due to the following sequence:
1. The ADCE daemon ran on port `8424` and streamed SSE updates to `caster_user_content/util/adce_bridge.py`.
2. `AdceBridgeClient` updated its internal RAM fields (`self._current_zone = zone`).
3. `adce_bridge.py` had no reference to `taskbar_hud_bridge.py` and never forwarded zone updates to the named pipe.
4. `taskbar_hud_bridge.py` contained logic to query `adce.get_current_zone()`, but only within its own `send_update()` method.
5. Because `send_update()` was never triggered, no packet was ever transmitted over `\\.\pipe\CasterTaskbarHud`.

### 3.4 Summary Table: Intended vs Actual Data Path

| Subsystem | Intended Pipeline | Actual Execution State | Failure Mode |
| :--- | :--- | :--- | :--- |
| **Speech Commands** | Dragonfly recognition -> `taskbar_hud_hook` -> Named Pipe | `taskbar_hud_hook.py` never loaded by Caster | Unregistered observer; pipe received zero bytes |
| **ADCE Context** | Port 8424 SSE -> `adce_bridge` -> `taskbar_hud_bridge` | `adce_bridge` logged locally; no forwarding call | Disconnected publisher; `Z: --` fallback remained |
| **Active Rules** | Context evaluation -> `taskbar_hud_bridge` -> Named Pipe | Scoped grammar checks tied to uninvoked hook | Uncalled method; `Rules: Global` fallback remained |

---

## 4. Root-Cause Analysis: Taskbar Button Collision & Overlap

The screenshot demonstrated that `[Z: --]` collided with the running taskbar button for `caster - File Exp...`.

```
Taskbar Layout Collision:
┌────────────────────────────────────────────────────────┬──────────────────────────────────────────┐
│ TaskListButtonPanel (WorkerW)                          │ SystemTrayFrameGrid (Shell_TrayWnd)      │
├────────────────────────────────────────────────────────┼──────────────────────────────────────────┤
│ [Start] [Search] [Icon] [caster - File Exp... [Z: --]  │ [Rules: Global] [Ready] [^] [C] [Mic] Clock│
└───────────────────────────────────────────────▲────────┴──────────────────────────────────────────┘
                                                │
                        Overlap Region: 3 pill boxes (~260px)
                        expand SystemTrayFrameGrid into TaskList bounds
```

### 4.1 Width Starvation in Windows 11 Taskbar
The Windows 11 taskbar divides horizontal space between two primary XAML panels:
1. `TaskListButtonPanel`: The running application button strip on the left and center.
2. `SystemTrayFrameGrid`: The system status and notification icon strip on the right.

`SystemTrayFrameGrid` calculates its width based on its children. Injecting three separate pills (`adceBorder`, `rulesBorder`, `commandBorder`) introduced substantial horizontal overhead:
* `adceBorder`: 6px padding on each side, 1px border, font size 11 -> ~52px
* `rulesBorder`: 6px padding on each side, 1px border, font size 11 -> ~84px
* `commandBorder`: 8px padding on each side, semi-bold font size 11.5, max width 220px -> ~75px to 220px
* `StackPanel` margins and spacing: 4px spacing between items, 6px margins -> 14px
* **Total Width**: **225px to 370px**

### 4.2 Lack of TaskList Margin Recalculation
`TaskListButtonPanel` is not notified when third-party code injects additional columns into `SystemTrayFrameGrid`. When running windows occupy available space, the leftward growth of `SystemTrayFrameGrid` directly covers the right edge of `TaskListButtonPanel`. The multi-pill layout is too wide for stable co-existence with a populated taskbar.

---

## 5. Architectural Pivot: Unified Single Command Strip

As proposed during testing, the optimal design replaces three separate boxes with a single, compact command strip that mirrors Caster's existing HUD output.

### 5.1 Design Comparison

| Attribute | Multi-Pill Layout (Current) | Unified Command Strip (Proposed) |
| :--- | :--- | :--- |
| **Visual Footprint** | 3 separate bordered boxes (~260–370px) | Single bordered pill container (~140–180px) |
| **Taskbar Overlap** | High collision risk with open task buttons | Fits cleanly within standard system tray margins |
| **Content Strategy** | Fragmented across Zone, Rules, and Command | Dynamic single line: shows command with contextual prefix |
| **Idle State** | Displays `[Z: --] [Rules: Global] [Ready]` | Displays compact status: `[Ready]` or `[VS Code]` |
| **Recognition State** | Flashes command box while other boxes stay static | Displays full recognized utterance with glowing border |

### 5.2 Dynamic Text Formatting Examples
Instead of dedicating permanent screen space to static boxes, the single strip displays context-aware status strings:
* **Idle (Global)**: `Ready`
* **Idle (Focused Application)**: `Ready (VS Code)`
* **Idle with Active ADCE Zone**: `Terminal (VS Code)`
* **Active Speech Streaming**: `... listening`
* **Finalized Recognition**: `format selection`
* **Microphone Sleeping**: `Sleeping`

---

## 6. Integration Architecture: Tapping Caster's HUD Output Pipeline

Caster already contains a robust, centralized message dispatching architecture for displaying text on its Heads-Up Display. Rather than writing ad-hoc Dragonfly observers, the taskbar HUD should connect directly to Caster's established output path.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CASTER CORE ENGINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Recognized Speech / System Messages / Errors                                │
│    │                                                                        │
│    ▼                                                                        │
│  castervoice.lib.printer.out("$ format selection")                          │
│    │                                                                        │
│    ▼                                                                        │
│  DelegatingMessageHandler                                                   │
│    ├── Handler 1: ConsolePrinterHandler (PowerShell console)                │
│    ├── Handler 2: HudPrintMessageHandler (PyQt HUD window)                  │
│    └── Handler 3 [NEW]: TaskbarHudPrintHandler                              │
│          │                                                                  │
│          └── Non-blocking enqueue to TaskbarHudBridgeClient                 │
│                │                                                            │
│                ▼                                                            │
│              \\.\pipe\CasterTaskbarHud (Overlapped Named Pipe)              │
│                │                                                            │
│                ▼                                                            │
│              Windhawk Mod (SystemTrayFrameGrid XAML Island)                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.1 Intercepting `printer.out` via `DelegatingMessageHandler`
In `_caster.py`:
```python
dh = printer.get_delegating_handler()
dh.register_handler(hud_support.HudPrintMessageHandler())
```

All Caster commands and statuses are prefixed deterministically:
* `$` : Recognized voice commands and dictation (`$ format selection`)
* `@` : System and state notifications (`@ Caster v1.7.0 Ready`)
* `#` : Warnings and error diagnostics (`# Natlink engine reset`)

Registering a dedicated `TaskbarHudPrintHandler` with `dh` intercepts every recognized command without adding any Dragonfly `RecognitionObserver` overhead or threading risk.

### 6.2 Forwarding ADCE and Context Events
Caster's `hud_support.py` already manages background window focus hooks (`_on_window_focus_changed`) and ADCE stream transitions (`_on_adce_context_changed`). When focus or context changes, `hud_support` resolves active rules via `get_active_contextual_rules()`:

```python
def _on_adce_context_changed(process_name, window_title, semantic_zone, active_file, is_connected=True):
    # Existing HUD IPC dispatch
    ...
    # Forward to Taskbar HUD Named Pipe
    get_taskbar_hud_bridge().send_update(
        adce_zone=semantic_zone,
        rules=get_active_contextual_rules(process_name, window_title),
        status="idle"
    )
```

This ensures that clicking into the VS Code terminal pane updates both the floating Caster HUD and the taskbar strip simultaneously in `< 1 ms`.

---

## 7. Concrete Next Steps & Action Plan

The recommended implementation proceeds in two logical phases:

### Phase 1: Output Pipeline Wiring (Python Caster)
1. **Implement `TaskbarHudPrintHandler`**: Subclass `printer.BaseMessageHandler` to consume `$` command messages from `printer.out` and push them to `TaskbarHudBridgeClient`.
2. **Register in `_caster.py`**: Add `dh.register_handler(TaskbarHudPrintHandler())` during initialization alongside the standard HUD handler.
3. **Connect ADCE & Focus Callbacks**: Call `bridge.send_update()` directly from `hud_support._on_window_focus_changed` and `hud_support._on_adce_context_changed`.
4. **Deprecate `taskbar_hud_hook.py`**: Remove the uninvoked observer from `caster_user_content/hooks/` to eliminate dead code.

### Phase 2: Windhawk Mod Refactor (`caster-taskbar-hud.wh.cpp`)
1. **Consolidate to Single Command Strip**: Collapse `adceBorder`, `rulesBorder`, and `commandBorder` into a single `Border` containing one `TextBlock`.
2. **Set Restrained Dimensions**: Constrain the container's `MaxWidth` to 160–180px with `CharacterEllipsis` trimming to guarantee zero overlap with `TaskListButtonPanel`.
3. **Format Dynamic Telemetry**: Render combined context-aware strings (e.g. `Ready`, `Terminal | VS Code`, or `format selection`) with color-coded status backgrounds (amber for streaming, green for recognized, dim red for microphone sleeping).

---

## 8. UX Enhancements: Status Dot, Idle Carousel, and In-Situ Configuration

### 8.1 Circular Microphone Status Dot
A 7x7 DIP circular `Border` element (`CornerRadius="3.5"`) is injected directly into the command pill preceding the text. The fill color reflects both speech engine lifecycle and mic mode:
* **Emerald Green (`#10B981`)**: Microphone is active and listening (`mic_state="on"`, `status="idle"` or `"recognized"`).
* **Crimson Red (`#EF4444`)**: Microphone is sleeping (`mic_state="sleeping"`, `status="sleeping"`).
* **Amber (`#F59E0B`)**: Real-time partial speech hypothesis streaming (`status="streaming"`).
* **Coral Red (`#DC2626`)**: Speech recognition error or rejected grammar match (`status="error"`).

### 8.2 Idle Rotational Carousel (`rotate` Mode)
When speech recognition occurs, the HUD holds the recognized command for `commandClearTimeoutSec` (6 seconds). When the hold period expires, the HUD enters an idle rotational cycle ticking every `carouselIntervalSec` (4 seconds):
1. **State 0 (ADCE Semantic Zone)**: Formats the active sub-window context as `ADCE: {zone}` with a purple background tint (`Color{45, 168, 85, 247}`) and violet border (`Color{140, 192, 132, 252}`), directly replicating Caster HUD `adce_bar.py`. Renders `ADCE: [Offline]` if disconnected.
2. **State 1 (Active CCR Rules)**: Formats scoped grammar rules as `Rules: {names}` with a blue background tint (`Color{40, 59, 130, 246}`) and light blue border, replicating Caster HUD `active_rules_bar.py`. Renders `Rules: Global` in default contexts.
3. **State 2 (Last Spoken Command)**: Formats `Last: {phrase}` or `Caster Ready` with neutral dark glass styling.

Any new speech event immediately preempts the carousel and snaps back to active command display.

### 8.3 In-Situ Right-Click Context Menu
A XAML `RightTapped` handler on `CasterTaskbarHudContainer` opens a native Win32 popup menu (`TrackPopupMenuEx`) at cursor coordinates:
* **Mode Selection**: Switch between `Rotating Carousel`, `Unified Single Strip`, and `Side-by-Side (3 Pills)`.
* **Component Toggles**: Enable or disable `ADCE Zone`, `Active Rules`, or `Command Stream`.
* **Immediate Action**: `Cycle Next Item Now` steps to the next carousel component instantly.
* **Registry Persistence**: User selections are written to `HKCU\Software\Caster\TaskbarHud` and reloaded on mod initialization, persisting across Explorer restarts.
