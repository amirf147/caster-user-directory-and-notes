import pyautogui
import time
import json
import os
from typing import Dict, NamedTuple
from castervoice.lib.actions import Key
from pathlib import Path
import ctypes
from ctypes import wintypes


def title(window_title):
    pyautogui.getWindowsWithTitle(window_title)[0].activate()

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

# Default aliases map spoken alias -> identifying window title substring
DEFAULT_ALIASES: Dict[str, str] = {
    "colt": "Windsurf",
    "webs": "Waterfox",
    "docks": "LibreOffice Writer",
    "mails": "Outlook",
}

# Dictionary for aliases
aliases: Dict[str, WindowInfo] = {}

def load_aliases() -> None:
    """Load aliases from file"""
    global aliases
    try:
        if ALIASES_FILE.exists():
            with open(ALIASES_FILE, 'r') as f:
                data = json.load(f)
                # Convert stored dict back to WindowInfo objects
                aliases = {
                    k: WindowInfo(**v) for k, v in data.items()
                }
            print(f"Loaded {len(aliases)} aliases")
    except Exception as e:
        print(f"Error loading aliases: {e}")
        aliases = {}

def save_aliases() -> None:
    """Save aliases to file"""
    try:
        # Convert WindowInfo objects to dict for JSON storage
        data = {
            k: v._asdict() for k, v in aliases.items()
        }
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

def get_default_aliases() -> Dict[str, str]:
    """Expose defaults for grammar/rules to consume."""
    return DEFAULT_ALIASES

def set_window(window_alias: str) -> None:
    """Set alias for current window"""
    window = pyautogui.getActiveWindow()
    if not window:
        print("No active window found")
        return
    if window_alias in DEFAULT_ALIASES:
        print(f"'{window_alias}' is a reserved built-in alias and cannot be set/overwritten.")
        return

    aliases[window_alias] = WindowInfo(
        handle=window._hWnd,
        title=window.title,
        is_tab=False,
        window_type=get_window_type(window.title)
    )
    print(f"Set window alias '{window_alias}' for: {window.title}")
    save_aliases()

def set_page(window_alias: str) -> None:
    """Set alias for current tab"""
    window = pyautogui.getActiveWindow()
    if not window:
        print("No active window found")
        return
    if window_alias in DEFAULT_ALIASES:
        print(f"'{window_alias}' is a reserved built-in alias and cannot be set/overwritten.")
        return

    window_type = get_window_type(window.title)
    if not window_type:
        print(f"Warning: Setting tab alias for non-tabbed application: {window.title}")
        
    aliases[window_alias] = WindowInfo(
        handle=window._hWnd,
        title=window.title,
        is_tab=True,
        window_type=window_type
    )
    print(f"Set tab alias '{window_alias}' for: {window.title}")
    save_aliases()

def find_tab(target_title: str, window_type: str) -> bool:
    """Find specific tab using Caster Key actions"""
    initial_title = pyautogui.getActiveWindow().title
    tries = 0
    max_tries = 50

    while tries < max_tries:
        current_title = pyautogui.getActiveWindow().title
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

def _sorted_windows() -> list:
    """Return top-level windows filtered to visible ones with non-empty titles.

    Note: Order comes from pyautogui/pygetwindow enumeration and may not
    exactly match taskbar order, but is stable enough for instance indexing.
    """
    # Do not filter by visibility because minimized windows can be valid targets
    wins = [w for w in pyautogui.getAllWindows() if getattr(w, 'title', '')]
    return wins

def _windows_matching_title_substring(substr: str) -> list:
    """Find windows whose title contains the given substring (case-insensitive)."""
    # Prefer built-in lookup which typically honors substring matching
    try:
        wins = pyautogui.getWindowsWithTitle(substr)
        if wins:
            return wins
    except Exception:
        pass
    # Fallback manual filter
    s = substr.lower()
    return [w for w in _sorted_windows() if s in w.title.lower()]

# -------------------- Win32 backend --------------------

user32 = ctypes.windll.user32

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
SW_RESTORE = 9

EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

def _get_window_text(hwnd: int) -> str:
    length = user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        # Could be empty title; still return empty string
        buf = ctypes.create_unicode_buffer(1)
        user32.GetWindowTextW(hwnd, buf, 1)
        return buf.value
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value

def _is_alt_tab_window(hwnd: int) -> bool:
    # Filter out tool windows and child windows
    if user32.GetParent(hwnd):
        return False
    exstyle = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    if exstyle & WS_EX_TOOLWINDOW:
        return False
    # Accept windows even if minimized; require non-empty title
    title = _get_window_text(hwnd)
    return bool(title.strip())

def _enum_windows_win32() -> list:
    windows = []

    @EnumWindowsProc
    def callback(hwnd, lParam):
        try:
            if _is_alt_tab_window(hwnd):
                title = _get_window_text(hwnd)
                windows.append((hwnd, title))
        except Exception:
            pass
        return True

    user32.EnumWindows(callback, 0)
    return windows  # Z-order top to bottom

def _win32_list_by_title_substring(substr: str) -> list:
    s = substr.lower()
    return [(hwnd, title) for hwnd, title in _enum_windows_win32() if s in title.lower()]

def _activate_hwnd(hwnd: int) -> None:
    try:
        user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"Win32 activate error: {e}")

def switch_to(window_alias: str, n: int = 1) -> None:
    """Switch to window or tab based on stored alias type.

    If the alias is a reserved default alias, use Win32-based matching and the
    instance index n (1-based). Saved aliases ignore n and point to a specific
    window handle.
    """
    # If this is a default alias, ensure any stale saved alias doesn't shadow it
    if window_alias in DEFAULT_ALIASES and window_alias in aliases:
        # Remove conflicting saved alias to prioritize built-in behavior
        try:
            aliases.pop(window_alias)
            save_aliases()
            print(f"Removed stale saved alias for reserved '{window_alias}'.")
        except Exception:
            pass

    # 1) Exact saved alias -> restore specific window/tab
    if window_alias in aliases:
        info = aliases[window_alias]
        try:
            windows = pyautogui.getAllWindows()
            for window in windows:
                if window._hWnd == info.handle:
                    window.activate()
                    time.sleep(0.1)

                    if info.is_tab and info.window_type:
                        find_tab(info.title, info.window_type)
                    return
            print(f"Window for alias '{window_alias}' not found")
            aliases.pop(window_alias)
            save_aliases()  # Save after removing invalid alias
            return
        except Exception as e:
            print(f"Error switching: {e}")
            return

    # 2) Default alias -> activate nth matching instance (Win32-backed)
    if window_alias in DEFAULT_ALIASES:
        match_title = DEFAULT_ALIASES[window_alias]
        matches = _win32_list_by_title_substring(match_title)
        idx = max(0, (n or 1) - 1)
        if 0 <= idx < len(matches):
            hwnd, _ = matches[idx]
            _activate_hwnd(hwnd)
            return
        print(f"Instance {n} not found for alias '{window_alias}' (found {len(matches)}).")
        return

    print(f"No alias found for '{window_alias}'")

def switch_to_instance(window_alias: str, n: int = 1) -> None:
    """Switch using either saved alias or default alias with instance index (1-based).

    For default aliases, selects the nth matching window by enumeration order.
    """
    if n < 1:
        n = 1

    # If this is a default alias, ensure any stale saved alias doesn't shadow it
    if window_alias in DEFAULT_ALIASES and window_alias in aliases:
        try:
            aliases.pop(window_alias)
            save_aliases()
            print(f"Removed stale saved alias for reserved '{window_alias}'.")
        except Exception:
            pass

    # Saved alias ignores index (it points to a specific window)
    if window_alias in aliases:
        switch_to(window_alias)
        return

    if window_alias in DEFAULT_ALIASES:
        match_title = DEFAULT_ALIASES[window_alias]
        matches = _win32_list_by_title_substring(match_title)
        idx = n - 1
        if 0 <= idx < len(matches):
            hwnd, _ = matches[idx]
            _activate_hwnd(hwnd)
            return
        else:
            print(f"Instance {n} not found for alias '{window_alias}' (found {len(matches)}).")
            return

    print(f"No alias found for '{window_alias}'")

def list_instances(window_alias: str) -> None:
    """Print matching windows for a default alias, with indices."""
    # For reserved default aliases, ignore and clean any saved alias
    if window_alias in DEFAULT_ALIASES and window_alias in aliases:
        try:
            aliases.pop(window_alias)
            save_aliases()
            print(f"Removed stale saved alias for reserved '{window_alias}'.")
        except Exception:
            pass
    elif window_alias in aliases:
        info = aliases[window_alias]
        print(f"Saved alias '{window_alias}': {info.title}")
        return
    if window_alias in DEFAULT_ALIASES:
        match_title = DEFAULT_ALIASES[window_alias]
        matches = _win32_list_by_title_substring(match_title)
        if not matches:
            print(f"No windows found for '{window_alias}' -> '{match_title}'")
            return
        print(f"Instances for '{window_alias}' -> '{match_title}':")
        for i, (hwnd, title) in enumerate(matches, start=1):
            print(f"  {i}. {title}")
        return
    print(f"No alias found for '{window_alias}'")

# Load aliases when module is imported
load_aliases()