# Code Review: `app_switcher.py` — The Unforgiving Edition

> **Reviewer**: Angry Principal Engineer who has had enough
> **Subject**: [app_switcher.py](../caster_user_content/util/app_switcher.py) (520 lines)
> **Verdict**: This file works *despite* itself. It is a monument to "I'll refactor it later."

---

## 1. The God Module Problem

This is a **520-line single file** that is simultaneously:
- A Win32 API adapter
- A pywinauto wrapper
- A pyvda virtual desktop client
- A JSON persistence layer
- A window title parser
- A tab cycling engine
- A keyboard macro executor
- A taskbar UI automation scraper
- An alias CRUD manager
- A focus verification poller

That's **10 distinct responsibilities** in one file. This isn't a module, it's a *landfill*.

> [!CAUTION]
> **Single Responsibility Principle violation count: 10.** Every time someone needs to touch tab cycling logic, they have to scroll past `ctypes.windll.user32.keybd_event` incantations and JSON serialization code. Every. Single. Time.

---

## 2. Global Mutable State Everywhere

```python
# Line 55
aliases: Dict[str, WindowInfo] = {}

# Line 82
load_aliases()  # Side effect at import time

# Line 287
os_env = WindowsOSAdapter()  # Singleton at import time
```

Three pieces of **module-level mutable global state**, two of which execute side effects the moment anyone imports this file. Want to write a unit test? Too bad — importing the module immediately:

1. Instantiates two `pywinauto.Desktop` objects (which query the Windows UI tree)
2. Reads a JSON file from disk
3. Prints to stdout

You literally cannot `import app_switcher` in a test harness without a live Windows desktop session. This is the definition of **untestable code**.

> [!WARNING]
> **The `load_aliases()` call on line 82 is a landmine.** It sits between two function definitions with no visual separation, no comment saying "THIS RUNS AT IMPORT TIME." A new developer reading top-to-bottom will skim right past it and spend 45 minutes wondering why aliases are magically populated.

---

## 3. The `WindowsOSAdapter` Is Lying About What It Is

The class is called an "adapter" but it's actually a **God Object** hiding behind a fancy name. Let's count what it does:

| Method | Actual Responsibility |
|:-------|:---------------------|
| [get_open_windows()](../caster_user_content/util/app_switcher.py#L123-L133) | Win32 window enumeration |
| [get_active_window()](../caster_user_content/util/app_switcher.py#L135-L157) | Active window detection with 3-backend fallback |
| [get_taskbar_items()](../caster_user_content/util/app_switcher.py#L159-L186) | Taskbar UI automation scraping |
| [get_current_desktop_id()](../caster_user_content/util/app_switcher.py#L188-L194) | Virtual desktop tracking |
| [get_window_desktop_id()](../caster_user_content/util/app_switcher.py#L196-L202) | Virtual desktop tracking |
| [restore_and_focus()](../caster_user_content/util/app_switcher.py#L204-L269) | **65-line monster** doing Win32 focus, pywinauto focus, thread attachment, keyboard injection, AND focus verification |
| [iter_windows()](../caster_user_content/util/app_switcher.py#L271-L278) | Dual-backend window iteration |
| [get_window_by_handle()](../caster_user_content/util/app_switcher.py#L280-L284) | Handle-to-window lookup |

That's **window enumeration**, **taskbar scraping**, **virtual desktop management**, AND **a 65-line focus algorithm** all jammed into one class. The `restore_and_focus` method alone contains:

- `AllowSetForegroundWindow`
- `GetWindowPlacement` + `ShowWindow`
- `pywinauto.Application().connect().set_focus()` (with a **lazy import inside the method** on [line 229](../caster_user_content/util/app_switcher.py#L229))
- `AttachThreadInput` / `DetachThreadInput`
- 5 `keybd_event` calls
- `BringWindowToTop`
- `SetForegroundWindow`
- 2 calls to `verify_focus`

This method is doing more work than some entire Python packages. It should be its own class.

---

## 4. Exception Handling: The "Pray It Works" Pattern

```python
# Lines 207-210
try:
    ctypes.windll.user32.AllowSetForegroundWindow(-1)
except Exception as e:
    print(f"AllowSetForegroundWindow failed: {e}")
```

Catch `Exception`, print to stdout, and **keep going as if nothing happened**. This pattern repeats **15+ times** throughout the file. The philosophy is apparently: "If a critical OS call fails, just... shrug and try the next thing."

Some greatest hits:

- [Line 184](../caster_user_content/util/app_switcher.py#L184): `get_taskbar_items()` catches `Exception` and returns an empty list. Silently. No logging. The caller has no idea whether the taskbar doesn't exist or whether pywinauto crashed.

- [Line 67-69](../caster_user_content/util/app_switcher.py#L67-L69): `load_aliases()` catches `Exception` and resets to empty dict. If your JSON file is corrupted, you lose all aliases with a single `print` to stdout that nobody will ever see.

- [Lines 140-141](../caster_user_content/util/app_switcher.py#L140-L141): `get_active_window()` has **three** nested try-except blocks that all silently swallow exceptions, falling through to progressively worse backends.

> [!WARNING]
> **Not a single exception in this entire 520-line file is logged to a proper logger.** Everything goes to `print()`. In a speech recognition framework that runs in the background, `print()` output goes... where exactly? Into the void.

---

## 5. The `switch_to_app` Function: 88 Lines of Procedural Spaghetti

[switch_to_app](../caster_user_content/util/app_switcher.py#L376-L463) is an **88-line function** that:

1. Normalizes input (list vs string)
2. Queries open windows
3. Filters by virtual desktop
4. Validates instance count
5. Executes Tier 1 (restore_and_focus)
6. Executes Tier 2 (taskbar UIA click)
7. Executes Tier 3 (keyboard macro)
8. Handles failure reporting

This is a **Chain of Responsibility** pattern implemented as a giant `if-else` waterfall. Each "tier" is inlined directly, mixing orchestration logic with implementation details. You can't:

- Add a Tier 4 without modifying this function
- Reorder tiers without cutting and pasting 20-line blocks
- Test any individual tier in isolation
- Reuse a tier in a different context

The Tier 2 and Tier 3 blocks both independently call `os_env.get_taskbar_items()` — that's **two separate taskbar scrapes** in the same function call. Did nobody notice this?

---

## 6. Inconsistent Abstractions

The module can't decide what level of abstraction it wants to operate at:

- `switch_to_app()` is a high-level voice command handler that directly calls `win32gui` APIs
- `restore_and_focus()` is on `WindowsOSAdapter` but calls `verify_focus()` which is a **module-level function outside the class**
- `find_tab()` is a module-level function that calls both `os_env.get_active_window()` AND `Key().execute()` — mixing OS queries with keyboard injection
- `extract_app_name()` and `extract_total_instances()` are free-floating utility functions that `get_taskbar_items()` (inside the class) calls back out to

The dependency arrows go in circles. The class depends on functions outside it, and functions outside depend on the class. There's no clear layer boundary.

---

## 7. The `extract_app_name` Function: A Maintenance Nightmare

```python
def extract_app_name(caption: str) -> str:
    if not caption:
        return "<blank>"
    caption = caption.strip()
    for name in sorted(WINDOWS_APP_NAMES, key=len, reverse=True):
        if name.lower() in caption.lower():
            return name
    if caption.lower().startswith(("windows powershell", "caster: status window")):
        return "Windows PowerShell"
    if caption.lower().startswith("copilot"):
        return "Copilot"
    for sep in _SEPARATORS:
        if sep in caption:
            parts = caption.split(sep)
            if len(parts) >= 2:
                return parts[-1].strip()
    return caption
```

This function has **four completely different parsing strategies** stitched together with no explanation:

1. Brute-force substring match against a set imported from another file
2. Two hardcoded `startswith` checks that duplicate entries already in `WINDOWS_APP_NAMES`
3. A separator-based split strategy using three different dash characters
4. A "give up and return the whole thing" fallback

Why is `"Windows PowerShell"` in `WINDOWS_APP_NAMES` AND hardcoded on [line 94](../caster_user_content/util/app_switcher.py#L94)? Why does `"caster: status window"` map to `"Windows PowerShell"`? Is that a bug or a feature? Nobody knows, because there's no comment explaining the reasoning.

Also: `.lower()` is called on `caption` **five separate times** in this function. Store it once.

---

## 8. `find_tab`: The Busy-Wait Bomb

```python
def find_tab(target_title: str, window_type: str) -> bool:
    _, __, initial_title = os_env.get_active_window()
    tries = 0
    while tries < 50:
        _, __, current_title = os_env.get_active_window()
        ...
        time.sleep(0.1)
        tries += 1
```

This function will:
- Query the active window **up to 50 times**
- Send a keystroke each iteration
- Sleep 100ms between each
- Take up to **5 full seconds** if the tab isn't found

That's 5 seconds of **blocking the speech recognition thread**. During which the user cannot speak any other commands. And it uses `_` and `__` as throwaway variables — not `_` twice, but `_` and `__`, because apparently one underscore wasn't dismissive enough.

---

## 9. Naming Crimes

- `w` — used for window objects throughout. Is it a pywinauto wrapper? A handle? Who knows.
- `t_items` — what does the `t` stand for? Taskbar? Tab? Temporal? ([line 421](../caster_user_content/util/app_switcher.py#L421))
- `enum_cb` — callback for `EnumWindows`, fair enough, but `ctx` is never used and should be `_`
- `tb` — toolbar? tuberculosis? ([line 167](../caster_user_content/util/app_switcher.py#L167))
- `fore_hwnd`, `target_hwnd`, `active_hwnd` — three different variable names for "a window handle" with no consistent convention

---

## 10. The `title()` Function Name

```python
def title(window_title: str):
```

You named a function `title`. Just... `title`. In a module full of window titles. This shadows Python's built-in `str.title()` in readers' mental models and tells you absolutely nothing about what it does. It should be `switch_to_window_by_title` or `activate_window_by_title`.

---

## 11. Dual Output Channels

The module uses **two different output mechanisms** with no clear policy:

- `print()` — for debug/diagnostic messages ([23 occurrences](../caster_user_content/util/app_switcher.py))
- `printer.out()` — for user-facing Caster status messages

Some functions use both, some use only one, and the distinction is inconsistent. `switch_to_app` calls `printer.out("Failed to switch window")` in **three different places** with the exact same string. But each `print()` message is different. So the user sees the same failure message regardless of which tier failed, while the developer gets detailed tier-specific info — but only if they're watching stdout.

---

## 12. Magic Numbers and Strings

| Location | Magic Value | What It Means |
|:---------|:-----------|:-------------|
| [Line 129](../caster_user_content/util/app_switcher.py#L129) | `"Program Manager"`, `"Windows Input Experience"`, `"OmApSvcBroker"` | Hardcoded window title blacklist |
| [Line 168](../caster_user_content/util/app_switcher.py#L168) | `"Running applications"` | Windows 11 taskbar toolbar name |
| [Line 208](../caster_user_content/util/app_switcher.py#L208) | `-1` | `ASFW_ANY` constant |
| [Line 237](../caster_user_content/util/app_switcher.py#L237) | `0.3` | Standard focus verification timeout |
| [Line 257](../caster_user_content/util/app_switcher.py#L257) | `0x12` | `VK_MENU` (Alt key) |
| [Line 259](../caster_user_content/util/app_switcher.py#L259) | `0xFF` | `VK_NONE` (dummy key) |
| [Line 269](../caster_user_content/util/app_switcher.py#L269) | `0.5` | OS bypass verification timeout |
| [Line 354](../caster_user_content/util/app_switcher.py#L354) | `50` | Maximum tab cycle attempts |
| [Line 362](../caster_user_content/util/app_switcher.py#L362) | `0.1` | Tab cycle sleep interval |
| [Line 429](../caster_user_content/util/app_switcher.py#L429) | `1.0` | Tier 2 verification timeout |
| [Line 454](../caster_user_content/util/app_switcher.py#L454) | `1.5` | Tier 3 verification timeout |

Not a single named constant. Good luck figuring out why the Tier 1 timeout is `0.3`, Tier 2 is `1.0`, and Tier 3 is `1.5` without reading the surrounding context.

---

## Proposed Architecture: How This Should Be Built

### Design Patterns Needed

| Pattern | Where To Apply |
|:--------|:-------------- |
| **Strategy** | `extract_app_name` — each parsing approach becomes a strategy that can be ordered, added, or removed |
| **Chain of Responsibility** | The 3-tier focus system — each tier is a handler that either succeeds or passes to the next |
| **Repository** | Alias persistence — abstract the JSON file behind a clean interface |
| **Facade** | The public API — thin functions that delegate to composed internal services |
| **Observer/Logger** | Replace all `print()` with a proper logging abstraction |

### Proposed Module Decomposition

```
util/
├── app_switcher/
│   ├── __init__.py              # Public API facade (set_window, switch_to_app, etc.)
│   ├── models.py                # WindowInfo, TaskbarItem, FocusResult dataclasses
│   ├── constants.py             # All magic numbers, timeouts, VK codes, blacklists
│   ├── name_resolver.py         # extract_app_name with strategy chain
│   ├── alias_repository.py      # AliasRepository class (load/save/CRUD)
│   ├── os_adapter.py            # WindowsOSAdapter (enumeration + queries ONLY)
│   ├── focus/
│   │   ├── __init__.py
│   │   ├── chain.py             # FocusChain orchestrator
│   │   ├── pywinauto_focus.py   # Tier 1: Pywinauto + OS bypass handler
│   │   ├── taskbar_focus.py     # Tier 2: Taskbar UIA click handler
│   │   └── keyboard_focus.py    # Tier 3: Keyboard macro handler
│   └── tab_navigator.py         # find_tab with configurable key mappings
```

### What Each Module Does

#### `models.py` — Pure Data, No Logic
```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class FocusTier(Enum):
    PYWINAUTO = "pywinauto"
    TASKBAR_UIA = "taskbar_uia"
    KEYBOARD_MACRO = "keyboard_macro"

class TabNavigationKey(Enum):
    CTRL_TAB = "c-tab"
    CTRL_PGDN = "c-pgdown"

@dataclass(frozen=True)
class WindowTarget:
    handle: int
    title: str
    app_name: str
    desktop_id: Optional[str] = None

@dataclass(frozen=True)
class FocusResult:
    success: bool
    tier_used: Optional[FocusTier] = None
    error: Optional[str] = None

@dataclass
class AliasEntry:
    handle: int
    title: str
    is_tab: bool = False
    tab_key: Optional[TabNavigationKey] = None
```

#### `constants.py` — Every Magic Value Named
```python
# Win32 Virtual Key Codes
VK_MENU = 0x12          # Alt key
VK_NONE = 0xFF          # Dummy key (no-op)
ASFW_ANY = -1           # AllowSetForegroundWindow: any process
KEYEVENTF_KEYUP = 0x02

# Focus Verification Timeouts (seconds)
STANDARD_FOCUS_TIMEOUT = 0.3
OS_BYPASS_FOCUS_TIMEOUT = 0.5
TASKBAR_CLICK_TIMEOUT = 1.0
KEYBOARD_MACRO_TIMEOUT = 1.5

# Tab Navigation
MAX_TAB_CYCLE_ATTEMPTS = 50
TAB_CYCLE_DELAY = 0.1   # seconds

# Window Title Blacklist
IGNORED_WINDOW_TITLES = frozenset({
    "Program Manager",
    "Windows Input Experience",
    "OmApSvcBroker",
})

# Taskbar
TASKBAR_CLASS = "Shell_TrayWnd"
RUNNING_APPS_TOOLBAR = "Running applications"
```

#### `focus/chain.py` — Chain of Responsibility
```python
import logging
from typing import List, Protocol
from ..models import WindowTarget, FocusResult

log = logging.getLogger(__name__)

class FocusHandler(Protocol):
    """Each tier implements this interface."""
    @property
    def name(self) -> str: ...
    def attempt(self, target: WindowTarget) -> FocusResult: ...

class FocusChain:
    """Tries each handler in order until one succeeds."""
    def __init__(self, handlers: List[FocusHandler]):
        self._handlers = handlers

    def execute(self, target: WindowTarget) -> FocusResult:
        for handler in self._handlers:
            log.info("Attempting focus via %s for '%s'", handler.name, target.title)
            result = handler.attempt(target)
            if result.success:
                log.info("Focused via %s", handler.name)
                return result
            log.warning("%s failed: %s", handler.name, result.error)

        log.error("All %d focus handlers failed for '%s'",
                  len(self._handlers), target.title)
        return FocusResult(success=False, error="All tiers exhausted")
```

#### `alias_repository.py` — Clean Persistence
```python
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from .models import AliasEntry

log = logging.getLogger(__name__)

class AliasRepository:
    def __init__(self, filepath: Path):
        self._filepath = filepath
        self._aliases: Dict[str, AliasEntry] = {}

    def load(self) -> None:
        """Load from disk. Call explicitly, not at import time."""
        ...

    def save(self) -> None: ...
    def get(self, key: str) -> Optional[AliasEntry]: ...
    def put(self, key: str, entry: AliasEntry) -> None: ...
    def remove(self, key: str) -> bool: ...
    def remove_by_handle(self, handle: int) -> List[str]: ...
    def clear(self) -> None: ...
```

### Key Architectural Wins

1. **Testability**: Each tier handler can be tested independently with a mock `WindowTarget`. The `AliasRepository` can be tested with a temp file. The `FocusChain` can be tested with stub handlers.

2. **Extensibility**: Adding a Tier 4 means creating one new file implementing `FocusHandler` and adding it to the chain. Zero changes to existing code.

3. **Readability**: When someone opens `taskbar_focus.py`, they see *only* taskbar UIA logic. No JSON. No Alt key injection. No tab cycling.

4. **Debuggability**: `logging.getLogger(__name__)` gives you per-module log filtering. You can set `focus.pywinauto_focus` to DEBUG while keeping `alias_repository` at WARNING.

5. **No Import Side Effects**: Nothing runs until explicitly called. Tests can import anything safely.

---

## Summary Scorecard

| Dimension | Current Score | Notes |
|:----------|:-------------|:------|
| **Single Responsibility** | 2/10 | 10 responsibilities in 1 file |
| **Testability** | 1/10 | Import triggers OS calls; global mutable state |
| **Error Handling** | 2/10 | Bare `except Exception` + `print()` everywhere |
| **Naming** | 4/10 | `title()`, `w`, `tb`, `t_items` |
| **Magic Numbers** | 2/10 | 11+ unnamed constants |
| **Separation of Concerns** | 2/10 | Circular deps between class and free functions |
| **Extensibility** | 3/10 | Adding a tier requires modifying a 88-line function |
| **Logging** | 1/10 | `print()` to stdout in a background service |
| **Documentation** | 4/10 | Some docstrings, but no explanation of *why* |
| **Does It Work** | 8/10 | Yes, and that's the most frustrating part |

> **Final verdict**: This code was clearly written by someone who understands Win32 focus mechanics at a *deep* level — the Alt+VK_NONE bypass, the thread attachment dance, the 3-tier failsafe — that's genuinely clever systems engineering. But it's all entombed in a structure that makes it nearly impossible to maintain, test, extend, or onboard someone new into. The domain knowledge is excellent. The software engineering around it is undergraduate-level.
