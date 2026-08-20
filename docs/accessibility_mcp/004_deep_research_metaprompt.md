# Deep Research Meta-Prompt: Active Desktop Context Engines (ADCE) & Real-Time OS State Hubs

**Document ID:** `docs/accessibility_mcp/004_deep_research_metaprompt.md`  
**Status:** Laser-Focused Research Specification  
**Prior Documents:** [`001_exploration_analysis_planning.md`](./001_exploration_analysis_planning.md), [`002_epistemology_patterns_and_observability.md`](./002_epistemology_patterns_and_observability.md), [`003_strategic_analysis_cross_platform_and_context.md`](./003_strategic_analysis_cross_platform_and_context.md)  
**Objective:** A prompt designed for deep-web research engines to investigate existing implementations, architectures, and state-of-the-art patterns for **Active Desktop Context Engines** (centralized daemons that maintain live, in-memory OS context graphs for human voice and AI agents).

---

```markdown
# Comprehensive Deep-Dive Research Prompt: Active Desktop Context Engines (ADCE) & Real-Time OS State Hubs

## Research Role & Objective
You are a Principal Systems Architect and Operating Systems Researcher specializing in Windows Internals, UI Automation (UIA/WinEvent), Assistive Technology Daemons, and Real-Time Desktop Context Aggregation for AI Agents and Voice Systems.

Investigate the state of the art in **Active Desktop Context Engines (ADCE)**: background hubs/daemons that continuously maintain a live, in-memory semantic graph of the user's active desktop (e.g., active window, focused sub-pane/terminal, open tabs, active document state) without requiring expensive, on-demand full-tree UI traversals.

---

## Context & Scope Boundary
* **What is already solved / Out of Scope**: Basic Win32 window switching, foreground lock bypasses, and COM STA/MTA threading basics are already solved and tested. We do NOT need generic tutorials on `SetForegroundWindow` or basic window focus.
* **The Core Research Focus**: How to build or leverage a centralized **Desktop Context Hub** that decouples **Real-Time Context Observation** (listening to OS events, maintaining a hot in-memory state graph) from **Action Execution** (dispatching deterministic automation commands).

---

## Key Research Pillars & Questions

### 1. Existing Desktop Context Engines & Prior Art
* **Industry & Open-Source Implementations**: What existing frameworks, daemons, or open-source projects maintain a continuous, live representation of desktop context?
  * Investigate projects in screen-awareness and desktop perception (e.g., Screenpipe, Rewind.ai / Limitless, OS-Atlas, Windows Copilot Runtime / Semantic Context APIs, accessibility bridges, assistive screen-reader state trees).
  * How do modern tools track active sub-window contexts (e.g., detecting when keyboard focus moves into VS Code's embedded terminal vs. Monaco editor, or tracking the active tab title and URL in Chromium browsers)?
* **Architectural Separation (Context vs. Action)**:
  * Are there production systems that separate the **Context Engine** (event-driven, read-only $O(1)$ in-memory state cache) from the **Action Server** (command/tool execution pipeline)?
  * How do these two layers synchronize to avoid acting on stale context?

### 2. Event-Driven Windows OS Perception Mechanics
* **UIA & WinEvent Hook Architecture**:
  * What is the most performant, low-overhead mechanism on Windows to listen for global focus and structure changes?
    * `AutomationFocusChangedEventHandler` (UIA) vs. `SetWinEventHook` (`EVENT_OBJECT_FOCUS`, `EVENT_SYSTEM_FOREGROUND`) vs. DWM shell hooks.
  * How do high-performance assistive tools (e.g., NVDA's `_UIAHandler`, JAWS) debounce and filter thousands of rapid OS events to maintain a lightweight in-memory active-object graph without causing UI lag or memory leaks?
* **Sub-Application & Tab Extraction**:
  * How can a background daemon reliably track tab strips (Chrome/Edge/Firefox/VS Code) and sub-controls without recursively walking the entire element tree on every event?
  * What event types indicate tab creation, tab switching, or tab closure in modern browser accessibility trees?

### 3. In-Memory State Graph & Data Structures
* **The "Desktop State Mini-Database"**:
  * What data structures and graph models are best suited for representing the desktop hierarchy ($ \text{Desktop} \to \text{Window} \to \text{Active Sub-Pane/Document} \to \text{Focused Control} $)?
  * How should the context graph be modeled so that external consumers (like Caster speech grammars or MCP clients) can query `get_current_context` in $< 1\text{ms}$?
  * What is the optimal JSON/schema format for exposing hierarchical context to LLM agents and deterministic speech rule dispatchers?

### 4. Enterprise & OS Vendor Trajectory (Microsoft & Apple)
* **What Big Tech is Doing**:
  * How is Microsoft approaching real-time desktop context in Windows 11 Copilot Runtime and Windows Recall? (e.g., Screen OCR vs. UIA semantic event interception vs. Windows App SDK context APIs).
  * Are there emerging official Windows APIs (e.g., in Windows App SDK / WinRT) designed specifically to expose real-time application and window context to AI tools?

---

## Deliverable Format
Please provide:
1. **Prior Art & Project Audit**: Detailed breakdown of existing context-tracking engines, screenpipe-style daemons, and open-source tools with architectural critiques.
2. **Context Engine Architectural Blueprint**: Concrete design for an event-driven Windows context daemon (hook registration, event debouncing pipeline, in-memory graph cache, query interface).
3. **Context vs. Action Separation Model**: How the Context Daemon connects to and coordinates with an MCP Action Server.
4. **Performance & Pitfalls**: Specific Win32/UIA event traps (event flooding, disconnected COM proxies, memory leaks) and how production systems mitigate them.
```
