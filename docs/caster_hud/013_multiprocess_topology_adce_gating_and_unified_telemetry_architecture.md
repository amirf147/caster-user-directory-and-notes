[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](005_caster_hud_requirements_and_specifications.md) › **013: Multi-Process Topology, ADCE Gating, & Unified Telemetry Architecture**

---

> [!NOTE]
> **Document Status**: *Active Architecture Decision Record (ADR; Not Superseded)*.  
> Provides the empirical failure mode analysis, multi-process topology, and architectural decision to retire in-process window tracking in favor of out-of-process ADCE observation, realized in **[014: Out-of-Process Desktop Observation](014_out_of_process_desktop_observation_and_adce_hud_realization.md)**.

# 013: Multi-Process Topology, ADCE Gating, & Unified Telemetry Architecture

**Document ID**: `CASTER-DOC-HUD-013`  
**Status**: Active Architecture Decision Record (ADR; Not Superseded)  
**Target Subsystems**: `active-desktop-context-engine`, `castervoice/asynch/hud/`, `mods/caster-taskbar-hud.wh.cpp`, `caster_user_content/util/`  
**Authors**: Antigravity Principal Systems Architecture (Pair Programming with Amir Farhadi)  

---

## 1. Executive Summary & Problem Context

The integration of the Windows 11 Taskbar HUD (`caster-taskbar-hud.wh.cpp`), Caster voice engine (`_caster.py`), and the Active Desktop Context Engine (`ADCE.Daemon.exe`) reached an architectural impasse characterized by three symptoms:

1. **Scattered Responsibility & Inverted Coupling**: Core engine files (`engine_manager.py`, `hud_support.py`, `_caster.py`) contain direct, defensive imports pointing backwards into `caster_user_content`.
2. **Duplicate Desktop Observers**: Two independent systems run low-level Win32 `SetWinEventHook` listeners for `EVENT_SYSTEM_FOREGROUND`: the .NET 10 ADCE daemon and Caster's internal `window_tracker.py`.
3. **Split-Brain Telemetry & Concurrency Collisions**: Telemetry packets originate across three uncoordinated execution paths (Dragonfly voice recognition, OS window focus shifts, and ADCE semantic zone transitions). These paths feed two parallel, disconnected transport channels (a local TCP socket on port 13374 and a Windows Named Pipe on `\\.\pipe\CasterTaskbarHud`).

This document provides a systematic teardown of the running multi-process topology, evaluates whether window tracking belongs in Caster or ADCE, details why Dragonfly cannot drive the HUD proactively, and specifies the unified clean architecture.

---

## 2. Exhaustive Multi-Process & Threading Topology

The complete runtime spans three dedicated OS processes, eleven concurrent threads, and four distinct IPC channels:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        RUNTIME PROCESS & THREAD TOPOLOGY                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [ PROCESS 1: ADCE.Daemon.exe (.NET 10 Desktop Daemon) ]                               │
│  ├── Thread 1.1: STA Message Pump (SetWinEventHook: Foreground & Focus)                │
│  ├── Thread 1.2: Channel Debouncer & Extraction Pipeline (FlaUI.UIA3 Cache)            │
│  └── Thread 1.3+: Kestrel HTTP Server (SSE Stream on http://127.0.0.1:8424/sse)        │
│                                                                                        │
│                                           │ (HTTP SSE Stream / NDJSON)                 │
│                                           ▼                                            │
│  [ PROCESS 2: pythonw.exe (Caster & Dragonfly Engine) ]                                │
│  ├── Thread 2.1: Main Engine Thread (Dragonfly audio loop, actions, printer.out)       │
│  ├── Thread 2.2: Win32-Focus-Hook (SetWinEventHook in window_tracker.py) [REDUNDANT]   │
│  ├── Thread 2.3: ADCE-HUD-Tracker (SSE reader in hud/core/adce_tracker.py)             │
│  ├── Thread 2.4: ADCE-SSE-Client (Duplicate SSE reader in adce_bridge.py) [DUPLICATE] │
│  ├── Thread 2.5: ADCE-MCP-Poller (Polling thread in adce_bridge.py) [REDUNDANT]       │
│  ├── Thread 2.6: HUD-Telemetry-Worker (TCP socket client to Qt HUD)                    │
│  └── Thread 2.7: TaskbarHUD-NamedPipe-Worker (Named Pipe client to Taskbar HUD)        │
│                                                                                        │
│                                           │ (Named Pipe: \\.\pipe\CasterTaskbarHud)    │
│                                           ▼                                            │
│  [ PROCESS 3: explorer.exe (Windows Shell & Windhawk Mod) ]                            │
│  ├── Thread 3.1: PipeServerThreadProc (Overlapped ReadFile on Named Pipe)              │
│  └── Thread 3.2: Taskbar UI Thread (Shell_TrayWnd message pump & XAML island tree)     │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Thread Inventory & Data Flow Analysis

The operational parameters for all concurrent threads are summarized below:

| ID | Thread Name | Host Process | Purpose | Synchronization & Transport | Concurrency Vulnerability |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1.1** | `STA-WinEvent-Pump` | `ADCE.Daemon.exe` | Captures OS window foreground and focus events | Win32 message pump | None; native isolated STA apartment. |
| **1.2** | `Extraction-Worker` | `ADCE.Daemon.exe` | Evaluates UIA tree, resolves zones, sanitizes data | Bounded async channel (`System.Threading.Channels`) | Backpressure if UIA COM call exceeds 50 ms. |
| **1.3** | `Kestrel-SSE-Host` | `ADCE.Daemon.exe` | Streams context envelopes to subscribers on port 8424 | HTTP Server-Sent Events | Sockets drop if subscriber fails to read. |
| **2.1** | `Main Voice Engine` | `pythonw.exe` | Processes mic audio, matches grammars, runs macros | Natlink message pump; Python GIL | `TaskbarHudPrintHandler` runs synchronously here; lock delays stall recognition. |
| **2.2** | `Win32-Focus-Hook` | `pythonw.exe` | Runs WinEvent hook for foreground window detection | Win32 message pump thread; calls `hud_support.py` | Redundant with Thread 1.1; iterates grammars without holding grammar lock. |
| **2.3** | `ADCE-HUD-Tracker` | `pythonw.exe` | Reads port 8424 SSE for HUD zone transitions | HTTP stream loop; updates atomic dict | Duplicates work performed by Thread 2.4. |
| **2.4** | `ADCE-SSE-Client` | `pythonw.exe` | Reads port 8424 SSE for Dragonfly `FuncContext` | HTTP stream loop; updates local cache | Duplicates work performed by Thread 2.3. |
| **2.5** | `ADCE-MCP-Poller` | `pythonw.exe` | Periodic HTTP GET polling fallback on port 8424 | Sleep loop | Unnecessary CPU overhead when SSE is connected. |
| **2.6** | `HUD-Telemetry` | `pythonw.exe` | Drains queue to external PyQt HUD overlay | Local TCP socket (port 13374) | Drop-oldest queue policy protects memory. |
| **2.7** | `Taskbar-Pipe-Worker` | `pythonw.exe` | Drains queue to Windows Named Pipe | Win32 `WriteFile` with drop-oldest queue | Batches up to 16 packets into multi-line strings, triggering parsing failures. |
| **3.1** | `PipeServerThread` | `explorer.exe` | Ingests NDJSON frames from named pipe | Win32 overlapped I/O | WinRT `JsonObject::TryParse` fails on multi-line batches, silently dropping updates. |
| **3.2** | `Taskbar UI Thread` | `explorer.exe` | Modifies WinRT XAML controls in `SystemTrayFrameGrid` | `SetWindowsHookEx(WH_CALLWNDPROC)` marshaling | Deadlock if UI thread blocks waiting on a shared lock held by worker. |

---

## 3. The Core Architectural Question: Who Owns Window Tracking?

The system exhibits an architectural contradiction: ADCE was explicitly designed as an out-of-process accessibility daemon with native Win32 hooks, yet Caster runs its own in-process Win32 hook in `window_tracker.py`.

### Historical Upstream Context
Upstream Caster (`dictation-toolbox/Caster`) **possesses no window tracker**. Upstream Caster relies exclusively on:
1. Natlink and Dragonfly to evaluate context at the instant of speech.
2. A simple Tkinter GUI that updates only when Caster prints text through `printer.out()`.

The file `window_tracker.py` was introduced locally in commit `3c98fe488` to satisfy a specific requirement: the Caster HUD needed to update its top header immediately upon Alt-Tab, even if speech was not occurring.

### Capability Comparison: ADCE vs In-Process Caster Hook

The technical attributes of both approaches are contrasted below:

| Evaluation Dimension | Out-of-Process (`ADCE.Daemon.exe`) | In-Process (`window_tracker.py` in Caster) |
| :--- | :--- | :--- |
| **Execution Plane** | Native .NET 10 compilation; zero GIL overhead | CPython runtime; executes under Python GIL |
| **OS Integration** | Low-level Win32 `SetWinEventHook` + `FlaUI.UIA3` | Win32 `SetWinEventHook` via `ctypes` |
| **Granularity** | Sub-window controls, tabs, Monaco buffers, terminals | Top-level window handle (`HWND`) only |
| **Virtual Desktops** | Native COM interop extracting desktop GUID and index | None |
| **Privacy Redaction** | Strips passwords, secret files, query tokens | Raw window title exposure |
| **Standalone Operation** | Requires `ADCE.Daemon.exe` process to be running | Self-contained within `pythonw.exe` |
| **Grammar Awareness** | Zero; has no access to Dragonfly grammar objects | Direct access to Dragonfly grammar instances |

### Architectural Determination
The desktop window tracker **should not live in Caster core**. 
Maintaining low-level Win32 message pumps and window traversal logic inside Python introduces unnecessary GIL contention and maintenance overhead. ADCE already provides a hardened, debounced, out-of-process context engine.

However, ADCE cannot evaluate Caster grammar rules. ADCE understands the physical environment (`process="Antigravity.exe"`, `zone="terminal"`), but it has no knowledge of Python ASTs, Caster rules, or Dragonfly grammars.

Therefore, the system requires a clean separation between **Context Production** and **Grammar Evaluation**:
1. **ADCE produces the desktop context**: It tracks windows, processes, titles, and sub-window zones, emitting structured events over HTTP/SSE.
2. **Caster evaluates the grammar rules**: It ingests the context from ADCE and matches it against Dragonfly grammars.
3. **The HUD displays the state**: It renders the resolved context and active rule names in the taskbar or overlay.

---

## 4. Why Dragonfly Cannot Drive the HUD Proactively

Dragonfly is an acoustic engine integration layer designed to wrap SAPI, Natlink, and Kaldi. It is strictly reactive to speech.

```
[User Presses Alt+Tab] ──────────► OS Window Switches to "Antigravity.exe"
                                          │
                                          ├─► Dragonfly State: ASLEEP (No Audio)
                                          │   • rule.active remains True for ALL rules in RAM.
                                          │   • No context checking occurs.
                                          │
[User Speaks: "show chats"] ─────► Dragonfly Audio Threshold Exceeded
                                          │
                                          ▼
                                   Grammar.process_begin(executable, title, handle)
                                          │
                                          ├─► Queries Win32Window.get_foreground()
                                          ├─► Evaluates ctx.matches(full_path, title, hwnd)
                                          └─► Calls rule.activate() or rule.deactivate()
```

Because Dragonfly evaluates rules only when an utterance begins:
1. Querying `rule.active` while the user is silent returns `True` for every loaded grammar across the entire system.
2. The HUD cannot rely on Dragonfly's internal state to update visual indicators during silent desktop navigation.
3. The HUD must proactively pass the active window context into `grammar.context.matches()` to determine which rules are applicable before speech begins.

---

## 5. Teardown of the Current Fragile Architecture

The current implementation exhibits four critical architectural flaws:

### Flaw 1: Inverted Dependency Violation
In `engine_manager.py` (`castervoice/lib/ctrl/mgr/engine_manager.py`), core engine code imports directly from user space:
```python
from caster_user_content.util.taskbar_hud_bridge import get_taskbar_hud_bridge
```
Core framework classes must never depend on user directory content. If user files are altered, core engine methods fail or execute defensive fallback paths.

### Flaw 2: Redundant SSE Clients in the Same Python Process
Two independent modules create separate HTTP connections to `http://127.0.0.1:8424/sse`:
- `AdceTracker` in `castervoice/asynch/hud/core/adce_tracker.py`.
- `AdceBridgeClient` in `caster_user_content/plugins/adce/client.py` *(pending publication)* (originally in `caster_user_content/util/adce_bridge.py`).

This duplicates socket descriptors, background threads, and JSON decoding logic within the same Python process.

### Flaw 3: Suffix Truncation in Context Matching
In `window_tracker.py` (`castervoice/asynch/hud/core/window_tracker.py`), the process name is stripped of `.exe`:
```python
full_path = path_buf.value
process_name = full_path.rsplit("\\", 1)[-1]
if process_name.lower().endswith(".exe"):
    process_name = process_name[:-4]
```
When `target_process = "antigravity"` is tested against a rule declaring `executable="Antigravity.exe"`, Dragonfly executes:
```python
"antigravity".find("Antigravity.exe")  # Evaluates to -1 (False)
```
Any rule authored with `.exe` fails to match on the HUD, causing the display to report `Rules: Global`.

### Flaw 4: Multi-Line NDJSON Dropping in the Windhawk Mod
In `taskbar_hud_bridge.py` (`caster_user_content/util/taskbar_hud_bridge.py`), the sender batches queued updates:
```python
packets = [packet]
while not self._queue.empty() and len(packets) < 16:
    packets.append(self._queue.get_nowait())
json_lines = "".join(json.dumps(p) + "\n" for p in packets)
```
In `caster-taskbar-hud.wh.cpp` (`mods/caster-taskbar-hud.wh.cpp`), the mod attempts to parse the entire buffer as a single document:
```cpp
JsonObject jsonObject{nullptr};
if (JsonObject::TryParse(wideStr, jsonObject) && jsonObject) { ... }
```
WinRT's `JsonObject::TryParse` fails on multi-line text. When two or more updates are batched together, the entire buffer is dropped, causing command updates and sleep state changes to be lost.

---

## 6. Target Clean Architecture: The Unified 3-Tier Model

The target architecture resolves these issues by establishing a unidirectional data pipeline with strict boundary separation:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              TARGET CLEAN ARCHITECTURE                                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  [ TIER 1: CONTEXT PROVIDER (Out-of-Process Environment Daemon) ]                       │
│  • Component: ADCE.Daemon.exe (.NET 10)                                                │
│  • Responsibility: WinEvent hooks, UIA tree evaluation, zone classification            │
│  • Interface: HTTP Server-Sent Events (port 8424)                                      │
│  • Payload: { process_name, window_title, hwnd, semantic_zone, active_file }           │
│                                                                                        │
│                                           │ (Single Resilient SSE Stream)              │
│                                           ▼                                            │
│  [ TIER 2: CONTEXT EVALUATION & DISPATCH (Caster Core Voice Engine) ]                   │
│  • Component 2.1: Unified Context Ingestor (adce_tracker.py)                           │
│    - Maintains canonical in-memory state: CasterContextState                           │
│    - Lightweight Win32 fallback hook activates ONLY if ADCE daemon is offline          │
│                                                                                        │
│  • Component 2.2: Contextual Rule Evaluator (hud_support.py)                           │
│    - Maps CasterContextState into Dragonfly grammars using full-path matching          │
│    - Evaluates: ctx.matches(full_path, title, hwnd)                                    │
│                                                                                        │
│  • Component 2.3: Telemetry Publisher Bus (AsyncTelemetryPublisher)                   │
│    - Core Caster event bus: MicStateEvent, CommandEvent, ContextEvent                  │
│    - Decoupled fan-out via subscriber sinks                                            │
│                                                                                        │
│                     ┌─────────────────────┴─────────────────────┐                      │
│                     │ (Fan-out over memory queues)              │                      │
│                     ▼                                           ▼                      │
│       [ Sink 1: TaskbarPipeSink ]                 [ Sink 2: StandaloneTcpSink ]        │
│       • Formats NDJSON frames                     • Formats NDJSON frames              │
│       • Writes to \\.\pipe\CasterTaskbarHud       • Writes to 127.0.0.1:13374          │
│                                                                                        │
│                     │                                           │                      │
│                     ▼                                           ▼                      │
│  [ TIER 3: PRESENTATION LAYER (External UI Displays) ]                                 │
│  • Display A: Windows 11 Taskbar HUD (Windhawk mod in explorer.exe)                    │
│    - Line-by-line NDJSON parser with overlapped ReadFile                               │
│    - Direct XAML island injection in SystemTrayFrameGrid                               │
│                                                                                        │
│  • Display B: Floating Modular HUD Overlay (PyQt5 GUI process)                         │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Architectural Invariants

1. **Strict Upstream Invariance**: No core Caster module may import from `caster_user_content`. All user-specific integrations must attach as event subscribers or printer handlers.
2. **Single Ingestion Stream**: Exactly one thread in `pythonw.exe` connects to ADCE's SSE endpoint. It updates a thread-safe context object in memory. `FuncContext` functions and HUD rule evaluators read from this shared object.
3. **Full-Path Context Matching**: The context evaluator must pass the full executable path (`full_path`), the filename with extension (`app.exe`), and the bare name (`app`) to `ctx.matches()`. This guarantees compatibility regardless of how rules are authored.
4. **Line-Delimited Pipe Processing**: The Windhawk mod in `explorer.exe` must tokenize incoming named pipe data by newline before calling `JsonObject::TryParse`.

---

## 7. Implementation Roadmap & Migration Sequence

The migration proceeds in four sequential phases:

### Phase 1: Core Engine Decoupling
1. Revert backward imports in `engine_manager.py`, `hud_support.py`, and `_caster.py`.
2. Ensure `EngineModesManager` publishes `MicStateEvent` exclusively through Caster's existing `AsyncTelemetryPublisher`.

### Phase 2: Telemetry Fan-Out Sink Implementation
1. Create `TaskbarPipeSink` under `castervoice/asynch/hud/ipc/`.
2. Register the pipe sink as a subscriber on `AsyncTelemetryPublisher`.
3. Route recognized commands from `TaskbarHudPrintHandler` through the publisher rather than calling the pipe directly.

### Phase 3: Windhawk Mod Parser Hardening
1. Update `ProcessIncomingPayload` in `caster-taskbar-hud.wh.cpp` (`mods/caster-taskbar-hud.wh.cpp`) to iterate line-by-line using `std::wstringstream` and `std::getline`.
2. Ensure empty or malformed lines are skipped without aborting the batch.

### Phase 4: Full-Path Context Resolution
1. Update `get_active_contextual_rules()` in `hud_support.py` (`castervoice/asynch/hud_support.py`) to extract `window.executable` using Dragonfly's `Window.get_window(hwnd)`.
2. Remove hardcoded IDE alias tuples, allowing Dragonfly's native `AppContext` to handle matching naturally.
3. Update `caster_user_content/rules/apps/antigravity.py` to declare `executable=["antigravity", "antigravity.exe"]`.
