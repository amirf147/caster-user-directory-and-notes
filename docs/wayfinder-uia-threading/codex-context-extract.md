# Wayfinder: Agent Context Extract

**Purpose:** a concise, evidence-aware project memory for agents working on the Wayfinder window-management/UIA work. It distils the 71 files in this directory (the map, 38 ticket trackers, and 32 research breakdowns) into durable context. Use it as a source for `context.md`; do not treat open-ticket questions or superseded hypotheses as decisions.

**Last distilled:** 2026-08-08  
**Canonical project map:** [map.md](map.md)

## Executive context

Wayfinder investigates dependable Windows window management, tab discovery, and element actions for Caster voice rules. The initial focus was perceived freezes in `caster_user_content/util/app_switcher.py` and whether UIA needed to move off the Dragonfly/Caster voice thread.

The current direction is an **experimental C#/.NET Micro MCP Server** using **FlaUI.UIA3**. It should expose a very small set of macro-level capabilities—window discovery/focus, tab discovery, and element action—to Caster via JSON-RPC/MCP. It is intentionally useful to future LLM clients, but the runtime voice path must be deterministic and use one pre-planned tool call, not LLM exploration.

This is an exploration and a potential architectural improvement, **not an emergency fix for a proven COM deadlock**. The only observed hard “freezes” have been traced to PowerShell QuickEdit pausing stdout while the app switcher tried to log. Keep this distinction explicit in all future work.

## Evidence rules and project truth

1. Prefer empirical findings and later decisions over older theory. In particular, the conclusions in Ticket 038 supersede earlier claims that Caster/Dragonfly had demonstrated UIA/COM deadlocks.
2. Brief synchronous blocking during a focus command is correct: later voice input must not be sent to a window whose focus transition is still in flight. The requirement is *bounded, observable, and recoverable* execution—not “make every operation asynchronous.”
3. UIA/COM can still be slow or fragile. Treat calls as timeout-prone and isolate them as a resilience measure, even though a real deadlock has not been reproduced here.
4. Ticket status is not a reliable statement of research completion. Several ticket files remain marked Open although their corresponding research document records findings. The map plus Tickets 033 and 038 are the best statement of current intent and facts.
5. Do not reintroduce the disproven causal chain “PowerShell/QuickEdit freeze = Python COM deadlock.” A blocked console stdout write can pause the Python code that prints; it does not show the Dragonfly speech engine is deadlocked.

## Current facts about the system

- Caster core has no built-in UIA service or COM apartment management. The user rules, notably the app switcher, own UIA/`pywinauto` usage and the more capable Win32 focus workarounds.
- Dragonfly/Caster command execution is predominantly synchronous. Caster’s existing overlays demonstrate process/IPC patterns, but are not a ready-made UIA service: they have environment, hard-coded-port, and lifecycle weaknesses.
- `win32gui.GetForegroundWindow()` is the preferred lightweight way to read the active HWND. Avoid UIA active-window traversal when only the HWND is needed.
- A measured 10.44-second switch delay occurred before target resolution, not during a successful focus attempt (which took about 201 ms). The leading suspected culprit is per-window virtual-desktop lookup through `pyvda`/`IVirtualDesktopManager`; instrument and bound that path instead of guessing.
- Browser tabs are not top-level windows. A design based only on `EnumWindows` and fuzzy title matching cannot locate a background tab reliably.
- UIA and Win32 enumeration require the active interactive desktop (`WinSta0\\Default`). A headless or non-interactive process can legitimately see zero desktop windows.

## Architecture decision record

### Decided direction

- Build a bespoke, narrow **C#/.NET Micro MCP Server** rather than adopt a generic “computer-use” server.
- Use **FlaUI.UIA3** for UIA access and keep the process in an MTA apartment (`[MTAThread]` at the entry point).
- Keep COM objects and UIA event handling inside the C# process. Do not send COM proxies or `AutomationElement` objects across threads or into Python; return serialized snapshots only.
- Use MCP/JSON-RPC as the boundary. Local `stdio` is the baseline transport, with negligible overhead for this use case. It avoids the fixed TCP-port conflicts of the existing XML-RPC style.
- Make the server stateless for the MVP. Aliases and rule-specific tab hotkey knowledge remain client-side.
- Keep the first release intentionally small. Generic screenshot/OCR/vision workflows, 50-tool LLM servers, and speculative “computer use” capability are out of scope for latency and reliability reasons.

### Still unresolved—do not silently decide

- Ticket 034 has not selected the final transport for potential simultaneous Caster and LLM clients (`stdio` versus named pipes/local HTTP), the C# MCP SDK versus a minimal protocol implementation, the exact tool schemas, or the Caster process-lifecycle owner.
- The final server name and whether it eventually grows from “UIA server” into a broader accessibility server are not settled. The broader need includes Win32 focus, and might later include other accessibility APIs.
- Virtual-desktop manipulation and taskbar-UIA fallback are deferred from the MVP. Do not add them merely because the legacy Python app switcher has them.

## Required implementation principles

### COM and UIA

- An STA client needs a message pump. The Micro Server instead uses MTA and should confine each COM object to the thread/apartment that created it.
- Keep a `UIA3Automation` instance alive for the server lifetime; dispose it predictably at shutdown.
- Discover top-level HWNDs cheaply with Win32 where possible, then bridge a selected HWND to UIA with `automation.FromHandle(hwnd)` only when UIA is needed.
- Constrain searches by scope and conditions. Unbounded descendant traversal and repeated `.Current` property reads create avoidable cross-process COM traffic.
- Use `CacheRequest` to request only necessary properties/patterns in one operation. For read-only discovery, use `AutomationElementMode.None` where compatible and read cached—not current—properties.
- For tab discovery, cache the narrow tab subtree/properties (name, automation ID, control type) rather than walking the full desktop. The reference implementation evaluated used a two-second descendant cache TTL; use caching deliberately and invalidate/expire it visibly.
- UIA action failure is expected, not exceptional. Catch the specific COM/UIA failure, return a structured result, and run the appropriate fallback rather than reporting success optimistically.

### Window identity and focus

- Validate `IsWindow(hwnd)` immediately before acting; HWNDs can become invalid or be recycled.
- Match conservatively: first validate a live HWND and its process identity; only then use title plus process matching if the original handle is dead. Never focus an arbitrary fuzzy match when multiple windows match—return the candidates and ask the client to refine.
- Filter ghost/background hosts (for example `ApplicationFrameHost` and `TextInputHost`) from discovery results.
- Use UIA primarily for semantic discovery and control actions; rely on native HWND/Win32 operations for reliable window foregrounding.
- Maintain a layered, verified focus path. The established practical path is restore/show the target, attempt normal foregrounding, then use `AttachThreadInput` with an injected Alt key when Windows blocks focus stealing. Command-line activation and taskbar macros are theoretical/later fallbacks, not MVP requirements.
- After every focus attempt, verify that the target became foreground within a finite timeout. Return a clear failure rather than spinning or sleeping indefinitely. Dragonfly’s historical `WaitWindow` tight loop is a pattern to avoid.
- Keep physical input as a last-resort UIA-control action fallback: `InvokePattern` -> focus plus Enter -> clickable point/bounding-rectangle click. It is not a substitute for explicit error reporting and has UIPI/session limits.

### Process, protocol, and logging

- The client owns child-process lifecycle and must always terminate/await the server in `try`/`finally`, including `KeyboardInterrupt`, to avoid orphan processes.
- Treat server stdout as protocol-only when using stdio JSON-RPC. Send diagnostics to stderr or a file. This also avoids the QuickEdit/logging trap and prevents corrupting JSON-RPC responses.
- Record timings for discovery, UIA traversal, desktop/virtual-desktop lookup, each focus tier, verification, and total command time. Measurements are required before attributing a slowdown to COM.
- Run and test in an interactive logged-in session. A background runner or service session is not a valid benchmark for desktop enumeration.

## MVP boundary and candidate tool contract

The exact schema is still a Ticket 034 decision. The following is the supported working contract, not a license to add more tools.

| Tool | Purpose | Essential behavior |
| --- | --- | --- |
| `ListWindows` | Discover candidate top-level windows, optionally filtered by process. | Return serialized `WindowContext` records; exclude ghost hosts; do not infer aliases or tabs. |
| `FocusWindow` | Focus one clearly identified window. | Accept process/title criteria (and eventually a handle); reject ambiguity; validate the live HWND; use verified Win32 focus fallbacks; return outcome/timing. |
| `GetTabs` | Read the tab controls for a selected browser/app window. | Use a constrained, cached UIA query; return stable IDs and names where exposed; do not invent app-specific hotkeys. |
| `ClickElement` | Invoke a specifically identified control. | Try semantic UIA action first, then bounded fallbacks; return whether the action was verified. |

Suggested returned window shape (field casing may be finalized later):

```json
{
  "processName": "Code",
  "windowTitle": "app_switcher.py - Caster - Visual Studio Code",
  "handle": "0x00123456",
  "isActive": true,
  "boundingRect": {"x": 0, "y": 0, "width": 1920, "height": 1080}
}
```

Every execution response should distinguish `success`, `not_found`, `ambiguous`, `invalid_handle`, `blocked`, `timeout`, and `unsupported` (or equivalent), include a human-readable diagnostic, and include timing. Do not encode failure as an exception with no usable result.

## Scope boundaries

**In scope:** deterministic voice-command window switching, tab discovery/selection support, focused element actions, Win32/UIA handoff, resilience, empirical diagnostics, and future MCP-compatible agent exploration.

**Out of scope for the MVP:** vision/OCR/screen parsing, a broad LLM computer-use framework, persistent aliases on the server, application-specific tab-hotkey policy, virtual-desktop control, taskbar UIA clicking, and an in-process Python `ThreadPoolExecutor` workaround.

## Useful prior-art conclusions

- **NVDA / Neru:** prove that dedicated MTA, thread-affine UIA execution and compact copied data are sound patterns.
- **Terminator / hunt-and-peck / legacy Caster:** confirm the value of direct Win32 focus control and `AttachThreadInput`; an STA design is only defensible with a real message pump.
- **Microsoft UIA guidance:** supports MTA for event handlers, narrow `TreeScope`/`TreeWalker` searches, `CacheRequest`, `AutomationElementMode.None` for read-only scans, `AutomationId` preference, and event registration before the action that triggers the event.
- **Python Windows-MCP:** reject as a foundation for app/tab switching. It enumerates only top-level windows, fuzzy-matches them, filters to the current virtual desktop, and its test teardown issue was client-side.
- **desktop-pilot-mcp:** confirms the benefits of C# + FlaUI UIA3, deep traversal, caching, and clean process teardown. Its generic, multi-call interface is not the desired voice-command API; mine its patterns, not its tool sprawl.
- **WinStasis:** retain the concepts of live-HWND-plus-process validation, process/title fallback matching, and multi-monitor boundary clamping. Do not copy its monolithic P/Invoke/CLI architecture.

## Benchmark and operational reference

These numbers are scenario-specific, not performance guarantees:

- A precompiled `WinAppMCP.exe` prototype measured roughly **232 ms** startup in one test (versus multi-second `dotnet run` startup).
- In that test, `list_desktop_windows` took **419.34 ms** and `get_focused_element` **7.76 ms** after startup. UI tree traversal can take 200–800 ms without careful caching.
- MCP serialization/pipe overhead was assessed as only a few milliseconds; UIA and OS behavior dominate end-to-end time.
- A current app-switcher focus sequence succeeded in about **201 ms**, while an earlier **10.44 s** total delay occurred before resolution. Instrument individual phases before optimizing.

## Agent checklist

Before changing Wayfinder-related code or documentation:

1. Read [map.md](map.md), [Ticket 033](tickets/033_re_evaluate_mcp_trajectory_research.md), and [Ticket 038 research](research/038_app_switcher_empirical_hang_investigation_research.md).
2. Preserve the distinction between confirmed observations, working hypotheses, and deferred design decisions.
3. Do not claim a COM deadlock without a reproducible trace that rules out stdout/QuickEdit and normal bounded COM delay.
4. Do not add an unbounded UIA traversal, busy wait, unsafely shared COM object, or stdout protocol logging.
5. Add or retain phase timing and structured errors. Test from an interactive desktop session.
6. Keep the server/client boundary narrow and the voice execution path atomic. If adding a tool requires multiple client-side discovery/action calls for an ordinary voice command, reconsider the tool design.
7. Update [map.md](map.md) and the relevant ticket/research record whenever a hypothesis becomes evidence or an MVP decision is finalized.

## Source coverage

This extract reviewed all material in this folder: the project map; ticket trackers `001`–`038`; and research documents `001`–`020`, `023`, `025`–`028`, `030`–`033`, and `035`–`038`. Comparative early research is retained above only where it informs a lasting pattern. Current project truth is governed by the later pivot and empirical records, especially [Ticket 033](tickets/033_re_evaluate_mcp_trajectory_research.md), [Ticket 034](tickets/034_determine_mcp_implementation_path_research.md), and [Ticket 038 research](research/038_app_switcher_empirical_hang_investigation_research.md).
