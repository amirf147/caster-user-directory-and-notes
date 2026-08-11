# App & Window Switcher

The [app_switcher.py](../caster_user_content/util/app_switcher.py) script provides robust, multi-strategy window switching, focusing, and tab navigation via voice commands.

## Features

- **Multi-Tier Failsafe**:
  1. Primary focus via Pywinauto and Win32 APIs with OS focus-steal bypass (`AttachThreadInput` + Alt key injection).
  2. Fallback to UI Automation (UIA) clicks on the Taskbar.
  3. Fallback to keyboard macros (e.g., `Win + T`).
- **Tab Switching Support**: Allows grouping certain apps like web browsers and IDEs to smoothly transition between tabs (`Ctrl+Tab`, `Ctrl+PgDn`).
- **Virtual Desktop Awareness**: Seamlessly switches to windows across virtual desktops, provided `pyvda` is installed.
- **Window Aliasing**: Ability to define custom names for windows (`aliases`) allowing you to dynamically name tabs and windows for fast navigation later.

## Usage

This utility is used by voice commands defined in [window_switching.py](../caster_user_content/rules/global/window_switching.py) and [window_switching_ccr.py](../caster_user_content/rules/global/window_switching_ccr.py) directly to switch, find, and manage focus across your workspace effortlessly.

---

## Architectural Blueprints & Code Review

For complete technical specifications, component relationships, state transitions, sequence diagrams, and refactoring guidelines, refer to the documentation suite:
- [Architectural Blueprint v1](app_switcher_architectural_blueprint.md): Initial deep architectural analysis of structural layers, state lifecycles, and sequence diagrams.
- [Architectural Blueprint v2](app_switcher_architectural_blueprint2.md): Refined architectural specification detailing exact layer boundaries, dual switching pipelines (`switch_to_app` vs `switch_to_alias`), and corrected OSAdapter method signatures.
- [Code Review & Refactoring Guide](app_switcher_code_review.md): Comprehensive critique analyzing architectural shortcomings, anti-patterns (God module, global mutable side effects, procedural waterfalls, magic constants), and proposing a clean modular redesign using Strategy, Chain of Responsibility, and Repository patterns.

> [!WARNING]
> **Architectural Status**: While [app_switcher.py](../caster_user_content/util/app_switcher.py) works reliably at runtime, its internal design suffers from high coupling, global mutable state, and violations of key software engineering principles (e.g. Single Responsibility Principle). Future refactoring work should follow the modular redesign proposed in the [Code Review](app_switcher_code_review.md).


### Architectural Overview & Layers

[app_switcher.py](../caster_user_content/util/app_switcher.py) is structured into five distinct components:

1. **Platform Abstraction Layer (`WindowsOSAdapter`)**:
   - Wraps raw Win32 APIs (`win32gui`, `win32process`, `win32api`, `ctypes`) for window enumeration, process ID resolution, and thread input attachment.
   - Maintains dual `pywinauto` Desktop backends (`_desktop_uia` and `_desktop_win32`) for flexible automation.
   - Integrates optional virtual desktop filtering via `pyvda` to restrict window matching to the active desktop.
   - Houses `restore_and_focus(handle)`, which features a 2-phase focus algorithm: standard focus attempt followed by an OS focus-steal bypass using thread attachment (`AttachThreadInput`) and synthetic Alt key injection (`keybd_event`).

2. **Data Contracts**:
   - `WindowInfo`: Immutable `NamedTuple` snapshot of a window's title, handle, executable path, tab flag, and tab navigation type.
   - `TaskbarItem`: Immutable `NamedTuple` snapshot of taskbar UI automation elements (title, rect, UIA element).

3. **Persistence Layer**:
   - Manages the `aliases` dictionary mapping user-defined names to `WindowInfo` objects.
   - Eagerly loads aliases from `window_aliases.json` at module import time (`load_aliases()`) and persists changes on alias mutation (`save_aliases()`).

4. **Public Command APIs**:
   - High-level entry points for voice rules: `switch_to_app()`, `switch_to_alias()`, `set_window()`, `set_page()`, `clear_alias()`, `clear_all_aliases()`, `title()`, and `show_window_info()`.

5. **Domain Logic & Tab Navigation**:
   - Helpers such as `extract_app_name()`, `get_window_type()`, `verify_focus()`, and `find_tab()`.
   - `find_tab()` cycles through tabs up to 50 times using application-specific keystrokes (`ctrl_tab` for browsers/terminals or `ctrl_pgdn` for IDEs like VS Code / Antigravity) until the foreground window title matches the target tab title.

### Dual Focus Pipelines

[app_switcher.py](../caster_user_content/util/app_switcher.py) executes two distinct focus pipelines depending on the target request:

- **`switch_to_alias(alias)` Pipeline**:
  1. Resolves alias to target `WindowInfo` in memory.
  2. Queries window handle and attempts fast direct restoration via `restore_and_focus(handle)`.
  3. If direct handle restoration fails (e.g., window closed), falls back to `switch_to_app()`.
  4. If `is_tab` is `True`, executes `find_tab()` to navigate to the exact tab title.
  5. If focus fails completely, prunes the stale alias from disk and memory.

- **`switch_to_app(app_name, instance)` Pipeline**:
  - Implements the 3-Tier Failsafe Focus Mechanism:
    - **Tier 1 (Direct Win32 / Pywinauto + OS Bypass)**: Searches open windows on active desktop, unminimizes, and invokes `restore_and_focus()`.
    - **Tier 2 (Taskbar UIA Click)**: Queries taskbar items in `Shell_TrayWnd` via pywinauto UIA backend and executes a physical UI click on the matching application button.
    - **Tier 3 (Taskbar Keyboard Macro)**: Focuses taskbar via `Win+T`, navigates horizontally using arrow keys, and presses `Enter`.

