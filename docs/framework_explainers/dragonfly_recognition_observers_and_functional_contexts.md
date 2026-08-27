<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2024-2026 Amir Farhadi -->

[ 🏠 Docs Home ](../README.md) › [ 📁 Framework Explainers ](../README.md#framework-explainers) › **Dragonfly Recognition Observers & Functional Contexts**

---

# Dragonfly Recognition Observers, `FuncContext`, & Active Desktop Context Engine (ADCE)

> **Document Status:** Active Educational Primer & Architecture Reference  
> **Target Audience:** Caster & Dragonfly Rule Developers, Core Architecture Designers  
> **External Engine Reference:** [Active Desktop Context Engine (ADCE) GitHub Repository](https://github.com/amirf147/active-desktop-context-engine)  
> **Related Documents:** [Repository Brain](../context/repository-brain.md) | [017: UI Automation Tree Structures](../accessibility_mcp/017_ui_automation_tree_structures_and_target_zones_reference.md) | [Dragonfly Rule Deep Dive](dragonfly_rule_deepdive.md) | [Speech Stack Thread Architecture](../architecture/Speech_Stack_Thread_Architecture_and_Diagnostic_Report.md)

---

## 1. Executive Summary & The Problem Space

Traditional voice recognition frameworks (like early Dragonfly and basic Caster rules) rely on **Operating System (Win32) Window Metrics** to determine grammar activation:
1. `executable` (e.g., `code.exe`, `firefox.exe`, `cmd.exe`)
2. `title` (e.g., `● myfile.py - Visual Studio Code`)
3. `handle` (the Win32 top-level window `HWND`)

```
Traditional Window-Level Context:
┌────────────────────────────────────────────────────────┐
│ VS Code (HWND: 0x00DB083E, Executable: "Code.exe")     │
│ ┌─────────────────────────┬──────────────────────────┐ │
│ │ Monaco Editor           │ Integrated Terminal      │ │ ◄── Dragonfly treats
│ │ (Wants Python/IDE rules)│ (Wants Bash/CLI rules)   │ │     ALL of this as
│ └─────────────────────────┴──────────────────────────┘ │     a single monolithic
└────────────────────────────────────────────────────────┘     "Code.exe" window!
```

### The Modern "Single-Canvas" Challenge
Modern IDEs and Electron applications (VS Code, Cursor, Antigravity IDE, Windsurf) and tabbed web browsers run as single-window monolithic canvases. Within the **same window handle** and **same process name**, the user constantly jumps between fundamentally different interaction zones:
* **Monaco Code Editor Buffer:** Requires programming syntax commands, line manipulation, refactoring macros.
* **Integrated Terminal Pane:** Requires shell navigation, CLI commands (`git status`, `npm run dev`, `docker compose`), and terminal escape sequences.
* **Source Control Commit Box:** Requires conversational dictation and git commit commands.
* **File Explorer Tree:** Requires file tree navigation, folder creation, and renaming commands.

To make Dragonfly rules activate dynamically based on these micro-context changes, we combine three core architectural primitives:
1. **`FuncContext` (Functional Contexts):** Built-in Dragonfly predicate wrapper that turns rules on/off based on a Python callable.
2. **`RecognitionObserver`:** Global engine-level lifecycle event hooks that monitor speech events across the engine without being tied to a single rule.
3. **[Active Desktop Context Engine (ADCE)](https://github.com/amirf147/active-desktop-context-engine):** An asynchronous background daemon that extracts element-level semantic zones via Win32 hooks and UI Automation caching, streaming low-latency state directly to Python.

---

## 2. Deep Dive: Dragonfly Recognition Observers

### 2.1 What is a `RecognitionObserver`?
A `RecognitionObserver` is an engine-level listener that hooks directly into the speech engine's recognition pipeline. 

Unlike a `Grammar` or `Rule` (which only receives callbacks when its own speech pattern is successfully matched), a `RecognitionObserver` receives **every single engine lifecycle event across the entire system**, regardless of which grammar is active or whether recognition succeeded or failed.

```
Speech Engine Audio Stream
           │
           ▼
     [ Voice Activity Detected ] ──► on_begin()
           │
           ▼
    [ Acoustic & Grammar Decode ]
      /                       \
   [ Match ]               [ No Match ]
      │                         │
      ▼                         ▼
on_recognition(...)       on_failure(...)
      │                         │
      ▼                         ▼
[ Rule Processing ]             │
      │                         │
      ▼                         ▼
on_post_recognition(...)   on_end(...)
```

### 2.2 The Lifecycle Methods & Signature

```python
from dragonfly import RecognitionObserver

class CustomRecognitionObserver(RecognitionObserver):
    def on_begin(self):
        """Fired immediately when speech onset / voice activity is detected."""
        pass

    def on_recognition(self, words, rule, node, results):
        """
        Fired when speech decodes successfully to a grammar rule or dictation.
        CALLED BEFORE rule action execution (Rule.process_recognition).
        
        :param words: tuple of recognized words (e.g., ('git', 'status'))
        :param rule: recognized Rule object (or None)
        :param node: parse tree Node
        :param results: engine-specific recognition object
        """
        pass

    def on_post_recognition(self, words, rule, node, results):
        """
        Fired AFTER all rule actions (Rule.process_recognition) have completed.
        Ideal for post-command telemetry, state reset, or logging.
        """
        pass

    def on_failure(self, results):
        """Fired when speech fails to decode (noise, rejection, or out-of-grammar)."""
        pass

    def on_end(self, results):
        """
        Fired when speech processing terminates for any reason
        (always called after on_recognition or on_failure).
        """
        pass
```

### 2.3 Registration & Callback Helpers

You can register observers in two ways:

#### 1. Object-Oriented Subclassing:
```python
observer = CustomRecognitionObserver()
observer.register()   # Hooks into dragonfly.get_engine()
# observer.unregister() when done
```

#### 2. Functional Callbacks (`recobs_callbacks`):
```python
from dragonfly.grammar.recobs_callbacks import (
    register_beginning_callback,
    register_recognition_callback,
    register_post_recognition_callback,
    register_failure_callback,
    register_ending_callback
)

def my_begin():
    print("User started speaking...")

token = register_beginning_callback(my_begin)
```

### 2.4 The "Golden Rule" of Recognition Observers
> [!CAUTION]
> **Observers Run Synchronously on the Engine Audio Thread!**  
> `on_begin`, `on_recognition`, and `on_end` are executed directly on the engine's main processing loop. If you perform blocking I/O, sleep, network requests, or slow COM/UIA calls inside an observer method, **you freeze the speech recognition pipeline**, leading to audio buffer overflows, delayed command execution, and dropped words.

---

## 3. Deep Dive: Dragonfly Context Architecture & `FuncContext`

### 3.1 The Context Class Hierarchy
In Dragonfly, all contexts inherit from the abstract base class `Context` (`dragonfly/grammar/context.py`):

```
                       ┌───────────────┐
                       │    Context    │
                       └───────┬───────┘
                               │
       ┌───────────────────────┼────────────────────────┐
       ▼                       ▼                        ▼
┌───────────────┐      ┌───────────────┐       ┌─────────────────┐
│  AppContext   │      │  FuncContext  │       │  Logic Contexts │
│ (exe, title,  │      │  (Arbitrary   │       │ (&, |, ~)       │
│  hwnd check)  │      │   callable)   │       │ And, Or, Not    │
└───────────────┘      └───────────────┘       └─────────────────┘
```

Every context implements a single critical method:
```python
def matches(self, executable: str, title: str, handle: int) -> bool:
    """Returns True if the grammar should be active, False otherwise."""
```

### 3.2 Boolean Context Composition
Contexts can be combined using standard Python bitwise operators:
* **`&` (`LogicAndContext`):** Both contexts must match.
* **`|` (`LogicOrContext`):** Either context matches.
* **`~` (`LogicNotContext`):** Inverts the context match.

Example:
```python
# Active in VS Code, but ONLY when in the integrated terminal
terminal_context = AppContext(executable="code") & FuncContext(is_terminal_focused)

# Active everywhere EXCEPT full-screen games
not_game_context = ~AppContext(executable="game.exe")
```

### 3.3 How `FuncContext` Works Under the Hood
`FuncContext` takes a Python callable and evaluates it dynamically whenever Dragonfly checks if a grammar should be active:

```python
from dragonfly import FuncContext

def check_sub_zone(executable, title, handle):
    # Dragonfly inspects the function signature!
    # If parameters match 'executable', 'title', or 'handle', they are injected.
    return my_state_tracker.get_zone() == "terminal"

ctx = FuncContext(check_sub_zone)
```

**Key Mechanics:**
1. **Dynamic Keyword Injection:** Dragonfly uses `inspect.getargspec` (or `getfullargspec`) to inspect your function's parameters. If your function asks for `(executable, title, handle)`, Dragonfly passes them. If your function takes no arguments `lambda: ...`, Dragonfly filters them out.
2. **Exception Safety:** If your function raises an unhandled exception, `FuncContext` catches it, logs a traceback, and **defaults to `True`** (fail-open) to avoid permanently disabling the grammar.

---

## 4. The Context Evaluation Lifecycle & The Latency Dilemma

Understanding the exact millisecond timeline of context evaluation is critical for designing high-performance sub-window switching.

```
Time ──►
[ User speaks ] ──► Engine detects voice onset
                           │
                           ▼
             Engine calls process_begin() on each Grammar
                           │
                           ▼
          Grammar calls its Context.matches(exe, title, hwnd)
             ├── If True  ──► Grammar enters context (rules active)
             └── If False ──► Grammar exits context (rules deactivated)
                           │
                           ▼
         Engine compiles search graph / decodes acoustic frames
                           │
                           ▼
                     Utterance Decoded
```

### The Synchronous Evaluation Loop
When speech begins, the engine iterates over **all loaded grammars** (in Caster, often 30–60+ grammars) and calls `grammar.process_begin()`. Each grammar executes its `context.matches()`.

### The Latency Math & Fatal Flaw of Naive Deep Traversal:
* If you have **40 active grammars**...
* And 10 of them use `FuncContext`...
* And each `FuncContext` performs a synchronous Windows UI Automation (UIA) COM query taking **30 ms**...
* **Total delay before speech decoding even begins = 10 × 30 ms = 300 ms!**

The user experiences a noticeable lag between speaking and command execution, or the initial syllable of speech is clipped.

---

## 5. Bridging the Gap: Active Desktop Context Engine (ADCE) Architecture

To enable instant sub-window switching (e.g., detecting VS Code Terminal vs Monaco Editor in **< 0.05 ms**), we decouple state extraction from grammar evaluation using the [Active Desktop Context Engine (ADCE)](https://github.com/amirf147/active-desktop-context-engine).

### The High-Performance Dual-Plane Architecture

```
 ╔═══════════════════════════════════════════════════════════════════════════════╗
 ║                ADCE BACKGROUND DAEMON (.NET 10 / FlaUI.UIA3)                  ║
 ║  • Native SetWinEventHook (EVENT_SYSTEM_FOREGROUND, EVENT_OBJECT_FOCUS)        ║
 ║  • Scoped FlaUI CacheRequests (< 10 ms) on focused container                  ║
 ║  • Lock-Free In-Memory Atomic Snapshot Cache (InMemoryDesktopStateCache)      ║
 ╚═══════════════════════════════════════════════════════════════════════════════╝
                                       │
                    [ Focus shifts from Editor to Terminal ]
                                       │
                                       ▼ (Asynchronous SSE / Localhost Stream)
                  ADCE streams DesktopContextSnapshot to Python Client:
                       ADCE_STATE["zone"] = "IntegratedTerminal"
                                       │
 ══════════════════════════════════════╪═══════════════════════════════════════════
                                       │
 ╔═════════════════════════════════════╪═════════════════════════════════════════╗
 ║                     CASTER / DRAGONFLY SPEECH ENGINE THREAD                   ║
 ║                                     │                                         ║
 ║   [ User Speaks "git status" ]      ▼                                         ║
 ║   Grammar.process_begin() ──► FuncContext.matches()                           ║
 ║                                     │                                         ║
 ║                                     ▼ (O(1) Memory Lookup: < 0.0001 ms!)      ║
 ║                    return ADCE_STATE["zone"] == "IntegratedTerminal"          ║
 ║                                     │                                         ║
 ║                                     ▼                                         ║
 ║   Terminal Grammar: ACTIVE ──► Decodes & Executes "git status" Instantly!     ║
 ╚═══════════════════════════════════════════════════════════════════════════════╝
```

### 5.1 Analysis of the Asynchronous Race Condition
When using a background cache, there is a theoretical race condition: *What if the user speaks immediately after clicking, before the background worker finishes updating the cache?*

* **Human Neuromuscular Voice Reaction Time:** Human motor-to-vocal onset latency is **~250 ms to 450 ms** (the time it takes to click a mouse, cognitively process the focus change, and vocalize a syllable).
* **ADCE Background Latency:** ADCE resolves scoped FlaUI `CacheRequest` extractions in **5 ms to 15 ms**.
* **Result:** ADCE updates the RAM cache **200+ ms before the user can physically utter a sound**, rendering the race window practically non-existent during normal workflow.

---

## 6. ADCE Semantic Zone Mapping (VS Code & Beyond)

Inside ADCE's core models ([`ADCE.Core.Enums.DesktopSemanticZone`](https://github.com/amirf147/active-desktop-context-engine/blob/main/src/ADCE.Core/Enums/DesktopSemanticZone.cs)), desktop interaction zones are surfaced as typed primitives:

```csharp
public enum DesktopSemanticZone
{
    Unknown = 0,
    EditorCodeBuffer = 1,     // Monaco code buffer (native-edit-context)
    IntegratedTerminal = 2,   // VS Code terminal (xterm / terminal-wrapper)
    GitCommitBox = 3,         // Source Control commit message box
    SidebarExplorer = 4,      // File tree & Activity Bar
    AddressBar = 5,           // Browser URL bar
    DocumentContent = 6,      // Web page body
    ShellItemList = 7,        // File Explorer items
    TabBar = 8,               // Open tabs strip
    StatusBar = 9,            // Branch name, line/col
    CommandPalette = 10,      // Quick open (Ctrl+P)
    ChatAssistant = 11        // AI Copilot / Chat panel
}
```

Per our single source of truth in [017: UI Automation Tree Structures & Target Zones Reference](../accessibility_mcp/017_ui_automation_tree_structures_and_target_zones_reference.md), ADCE's `MonacoIdeExtractor` maps the Electron container hierarchy:

```
[D0] Window: (Class: 'Chrome_WidgetWin_1', Title: 'caster - Antigravity IDE')
 └── [D4] Document: AutoId='RootWebArea'
      ├── [D5] Group: Class='part sidebar'            ◄ (Sidebar / File Explorer)
      ├── [D5] Group: Class='part editor'             ◄ (Editor Area)
      │    ├── [D7] Tab: Class='tabs-container'       ◄ (Open Tabs Strip)
      │    └── [D9] Edit: Class='native-edit-context' ◄ (Active Code Buffer / Caret)
      ├── [D5] Group: Class='part panel'              ◄ (INTEGRATED TERMINAL / Panel)
      │    └── [D8] Pane: Class='xterm...' or terminal-instance
      └── [D8] Edit: Name='Message (Ctrl+Enter...'    ◄ (Git Commit Box)
```

---

## 7. Concrete Code Implementation Blueprint

### Step 1: Lightweight SSE Python Client for Caster

```python
# caster_user_content/util/adce_bridge.py
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024-2026 Amir Farhadi

import json
import threading
import urllib.request

class AdceClient:
    """Thread-safe SSE client bridging ADCE desktop snapshots into Caster."""
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.current_zone = "Unknown"
        self.current_app = ""
        self.active_file = ""
        self._running = True

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = AdceClient()
        return cls._instance

    def start_background_listener(self, url="http://127.0.0.1:5005/events"):
        def listen():
            while self._running:
                try:
                    with urllib.request.urlopen(url, timeout=60) as response:
                        for line in response:
                            decoded = line.decode('utf-8').strip()
                            if decoded.startswith("data:"):
                                snapshot = json.loads(decoded[5:])
                                focus = snapshot.get("Focus", {})
                                window = snapshot.get("Window", {})
                                ide = snapshot.get("IdeContext", {})

                                with self._lock:
                                    self.current_zone = focus.get("SemanticZone", "Unknown")
                                    self.current_app = window.get("ProcessName", "")
                                    self.active_file = ide.get("ActiveTab", {}).get("Title", "") if ide else ""
                except Exception:
                    pass  # Auto-reconnect on transient dropout

        t = threading.Thread(target=listen, daemon=True, name="ADCE-SSE-Bridge")
        t.start()

    def is_zone(self, app_name: str, zone_name: str) -> bool:
        """Sub-microsecond O(1) predicate evaluated by FuncContext."""
        with self._lock:
            if app_name and app_name.lower() not in self.current_app.lower():
                return False
            return self.current_zone == zone_name

# Global Singleton
adce = AdceClient.get_instance()
adce.start_background_listener()
```

### Step 2: Defining `FuncContext` Predicates in Caster

```python
# caster_user_content/util/sub_contexts.py
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024-2026 Amir Farhadi

from dragonfly import FuncContext
from caster_user_content.util.adce_bridge import adce

def is_vscode_terminal():
    return adce.is_zone("Code", "IntegratedTerminal")

def is_vscode_editor():
    return adce.is_zone("Code", "EditorCodeBuffer")

def is_vscode_git_commit():
    return adce.is_zone("Code", "GitCommitBox")

VSCodeTerminalContext = FuncContext(is_vscode_terminal)
VSCodeEditorContext = FuncContext(is_vscode_editor)
VSCodeGitCommitContext = FuncContext(is_vscode_git_commit)
```

### Step 3: Wiring into Caster Rules via `RuleDetails`

Caster's `RuleDetails` natively supports `function_context` and automatically combines it with `AppContext` using `&`:

```python
# caster_user_content/rules/apps/vscode/vscode_terminal.py
# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (c) 2024-2026 Amir Farhadi

from dragonfly import MappingRule, Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R
from caster_user_content.util.sub_contexts import is_vscode_terminal

class VSCodeTerminalRule(MappingRule):
    mapping = {
        "git status": R(Text("git status") + Key("enter")),
        "git branch": R(Text("git branch -a") + Key("enter")),
        "git pull": R(Text("git pull") + Key("enter")),
        "run tests": R(Text("npm test") + Key("enter")),
        "clear terminal": R(Key("c-l")),
        "kill terminal": R(Key("c-shift-w")),
    }

def get_rule():
    return VSCodeTerminalRule, RuleDetails(
        name="VSCodeTerminal",
        executable=["Code", "VSCodium", "cursor", "Windsurf", "Antigravity IDE"],
        title=["Visual Studio Code", "VSCodium", "Cursor", "Windsurf", "Antigravity IDE"],
        function_context=is_vscode_terminal,  # <--- Injected directly into Caster merger!
    )
```

### Step 4: Using `RecognitionObserver` for Observability & HUD Diagnostics

We attach a `RecognitionObserver` to log which sub-zone fired during speech and synchronize the active zone with the Caster HUD:

```python
# caster_user_content/hooks/context_telemetry_observer.py
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024-2026 Amir Farhadi

from dragonfly import RecognitionObserver
from caster_user_content.util.adce_bridge import adce

class ContextTelemetryObserver(RecognitionObserver):
    def on_begin(self):
        # Optional: Snapshot state at exact millisecond of voice onset (< 0.001 ms)
        pass

    def on_recognition(self, words, rule, node, results):
        rule_name = rule.name if rule else "Unknown"
        phrase = " ".join(words) if words else ""
        print(f"[RECOBS TELEMETRY] Fired '{phrase}' on Rule '{rule_name}' | Active Zone: {adce.current_zone}")

    def on_failure(self, results):
        print(f"[RECOBS TELEMETRY] Misrecognition in Zone: {adce.current_zone}")

# Automatically registers with the engine on startup
telemetry_observer = ContextTelemetryObserver()
telemetry_observer.register()
```

---

## 8. Summary Comparison Matrix

| Mechanism | Scope | Execution Timing | Performance Impact | Primary Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`AppContext`** | OS Window | Synchronous (`process_begin`) | Extremely Low (< 0.01 ms) | Top-level window gating (`executable`, `title`, `hwnd`). |
| **`FuncContext`** | Arbitrary Logic | Synchronous (`process_begin`) | **Depends on predicate!** (O(1) cache check = < 0.01 ms; COM/UIA = Fatal 50–300 ms). | Dynamic rule gating based on custom state. |
| **`RecognitionObserver`** | Global Engine | Synchronous (`on_begin`, `on_recognition`, `on_failure`, etc.) | Low (if non-blocking). Blocks engine if doing heavy I/O. | Global telemetry, HUD updates, state tracking, diagnostic logging. |
| **[ADCE](https://github.com/amirf147/active-desktop-context-engine)** | Sub-Window & UIA | **Asynchronous Background Thread** | Zero speech thread latency. Background CPU: < 1%. | Real-time tracking of active tabs, panes, terminal focus, and breadcrumbs. |

---

## 9. Next Steps & Upstream Collaboration Strategy

1. **Leverage `RuleDetails.function_context`:** Caster already supports `function_context` in `RuleDetails` for non-CCR rules and CCR merged grammars.
2. **Zero-Latency Invariant:** Never put direct UIA/COM calls in `FuncContext.matches()`. Always query the local atomic memory mirror populated by ADCE.
3. **Upstream Alignment with LexiconCode:** This decoupled architecture directly resolves upstream maintainer concerns regarding speech loop stalling and race condition risks.
