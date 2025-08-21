# Written with GPT-5 (low reasoning) in windsurf ide

from typing import Dict, NamedTuple
import time
import json
import os
from pathlib import Path

from castervoice.lib.actions import Key
from pywinauto import Desktop
from pywinauto.findwindows import ElementNotFoundError

try:
    import win32gui  # type: ignore
except Exception:
    win32gui = None  # fallback handled at runtime


# Define application groups by their window title identifiers
CTRL_TAB_APPS = ['Waterfox', 'Firefox', 'Windows Terminal']
CTRL_PGDN_APPS = ['Windsurf', 'Cursor', 'VSCodium', 'Visual Studio Code']


class WindowInfo(NamedTuple):
    handle: int
    title: str
    is_tab: bool = False
    window_type: str = None


# Get path to store aliases
CASTER_USER_DIR = Path(os.path.expanduser("~/AppData/Local/caster/caster_user_content/"))
ALIASES_FILE = CASTER_USER_DIR / "window_aliases.json"

# Ensure directory exists
CASTER_USER_DIR.mkdir(exist_ok=True)

# Dictionary for aliases
aliases: Dict[str, WindowInfo] = {}


def _desktop(backend: str = "uia"):
    """Get a Desktop object for a specific backend (uia or win32)."""
    return Desktop(backend=backend)


def _get_active_window_wrapper():
    """Try to get the active window wrapper using UIA, Win32, then win32gui fallback.
    Returns (wrapper, handle, title) where wrapper can be None if only handle obtained.
    """
    # Try UIA
    try:
        w = _desktop("uia").get_active()
        if w is not None:
            return w, int(w.handle), w.window_text()
    except Exception:
        pass

    # Try Win32 backend
    try:
        w = _desktop("win32").get_active()
        if w is not None:
            return w, int(w.handle), w.window_text()
    except Exception:
        pass

    # Fallback via win32gui
    try:
        if win32gui is not None:
            h = win32gui.GetForegroundWindow()
            if h:
                # Try to wrap it with either backend to read title
                title = None
                try:
                    w_uia = _desktop("uia").window(handle=h)
                    title = w_uia.window_text()
                    return w_uia, int(h), title
                except Exception:
                    try:
                        w_w32 = _desktop("win32").window(handle=h)
                        title = w_w32.window_text()
                        return w_w32, int(h), title
                    except Exception:
                        # Final: get title via win32 api
                        try:
                            title = win32gui.GetWindowText(h)
                        except Exception:
                            title = ""
                        return None, int(h), title or ""
    except Exception:
        pass

    return None, None, ""


def _get_window_by_handle(handle: int):
    # Prefer UIA, but fall back to win32
    try:
        return _desktop("uia").window(handle=handle)
    except Exception:
        return _desktop("win32").window(handle=handle)


# --- Window state helpers (preserve maximized, only restore when minimized) ---
def _get_show_state(handle: int) -> int | None:
    """Return win32 SHOWCMD for the window if available.
    1=normal, 2=minimized, 3=maximized. None if unavailable.
    """
    if win32gui is None:
        return None
    try:
        placement = win32gui.GetWindowPlacement(handle)
        return placement[1]
    except Exception:
        return None


def _is_minimized(handle: int) -> bool | None:
    s = _get_show_state(handle)
    return (s == 2) if s is not None else None


def _is_maximized(handle: int) -> bool | None:
    s = _get_show_state(handle)
    return (s == 3) if s is not None else None


def title(window_title: str):
    """Activate a window whose title contains the given substring."""
    try:
        # Search across both backends for robustness
        for backend in ("uia", "win32"):
            try:
                for w in _desktop(backend).windows():
                    try:
                        if window_title in w.window_text():
                            handle = int(w.handle)
                            was_max = _is_maximized(handle)
                            is_min = _is_minimized(handle)
                            # Only restore if minimized
                            if is_min:
                                try:
                                    w.restore()
                                except Exception:
                                    pass
                            try:
                                w.set_focus()
                            except Exception:
                                try:
                                    w.wrapper_object().set_focus()
                                except Exception:
                                    pass
                            # Re-maximize if it was maximized
                            if was_max:
                                try:
                                    w.maximize()
                                except Exception:
                                    try:
                                        w.wrapper_object().maximize()
                                    except Exception:
                                        pass
                            return
                    except Exception:
                        continue
            except Exception:
                continue
        print(f"No window found with title containing: {window_title}")
    except Exception as e:
        print(f"Error activating by title: {e}")


def load_aliases() -> None:
    """Load aliases from file"""
    global aliases
    try:
        if ALIASES_FILE.exists():
            with open(ALIASES_FILE, 'r') as f:
                data = json.load(f)
                aliases = {k: WindowInfo(**v) for k, v in data.items()}
            print(f"Loaded {len(aliases)} aliases")
    except Exception as e:
        print(f"Error loading aliases: {e}")
        aliases = {}


def save_aliases() -> None:
    """Save aliases to file"""
    try:
        data = {k: v._asdict() for k, v in aliases.items()}
        with open(ALIASES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving aliases: {e}")


def get_window_type(title: str) -> str:
    """Determine which type of tab switching to use"""
    if any(app in title for app in CTRL_TAB_APPS):
        return 'ctrl_tab'
    if any(app in title for app in CTRL_PGDN_APPS):
        return 'ctrl_pgdn'
    return None


def set_window(window_alias: str) -> None:
    """Set alias for current window"""
    w, handle, title_text = _get_active_window_wrapper()
    if not handle:
        print("No active window found")
        return

    aliases[window_alias] = WindowInfo(
        handle=handle,
        title=title_text,
        is_tab=False,
        window_type=get_window_type(title_text),
    )
    print(f"Set window alias '{window_alias}' for: {title_text}")
    save_aliases()


def set_page(window_alias: str) -> None:
    """Set alias for current tab"""
    w, handle, title_text = _get_active_window_wrapper()
    if not handle:
        print("No active window found")
        return

    window_type = get_window_type(title_text)
    if not window_type:
        print(f"Warning: Setting tab alias for non-tabbed application: {title_text}")

    aliases[window_alias] = WindowInfo(
        handle=handle,
        title=title_text,
        is_tab=True,
        window_type=window_type,
    )
    print(f"Set tab alias '{window_alias}' for: {title_text}")
    save_aliases()


def find_tab(target_title: str, window_type: str) -> bool:
    """Find specific tab using Caster Key actions, reading active title via pywinauto."""
    _, __, initial_title = _get_active_window_wrapper()
    tries = 0
    max_tries = 50

    while tries < max_tries:
        _, __, current_title = _get_active_window_wrapper()
        if target_title == current_title:
            return True

        if window_type == 'ctrl_tab':
            Key("c-tab").execute()
        elif window_type == 'ctrl_pgdn':
            Key("c-pgdown").execute()

        time.sleep(0.1)
        tries += 1

        if tries > 1 and current_title == initial_title:
            break

    return False


def switch_to(window_alias: str) -> None:
    """Switch to window or tab based on stored alias type using pywinauto focus mechanics."""
    if window_alias not in aliases:
        print(f"No alias found for '{window_alias}'")
        return

    info = aliases[window_alias]
    try:
        try:
            w = _get_window_by_handle(info.handle)
        except ElementNotFoundError:
            print(f"Window for alias '{window_alias}' not found")
            aliases.pop(window_alias, None)
            save_aliases()
            return

        try:
            handle = int(info.handle)
            was_max = _is_maximized(handle)
            is_min = _is_minimized(handle)
            # Only restore if minimized
            if is_min:
                try:
                    w.restore()
                except Exception:
                    pass

            focused = False
            for attempt in range(3):
                try:
                    w.set_focus()
                    focused = True
                    break
                except Exception:
                    try:
                        w.wrapper_object().set_focus()
                        focused = True
                        break
                    except Exception:
                        time.sleep(0.05)

            if not focused:
                print("Warning: Could not set focus via pywinauto; window may still be backgrounded.")

            # Re-maximize if it was maximized
            if was_max:
                try:
                    w.maximize()
                except Exception:
                    try:
                        w.wrapper_object().maximize()
                    except Exception:
                        pass

            time.sleep(0.1)

            if info.is_tab and info.window_type:
                find_tab(info.title, info.window_type)
            return
        except Exception as e:
            print(f"Error focusing window: {e}")

    except Exception as e:
        print(f"Error switching: {e}")


# Load aliases when module is imported
load_aliases()