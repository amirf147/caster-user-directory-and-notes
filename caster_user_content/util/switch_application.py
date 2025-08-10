import pyautogui
import win32gui
import win32con
import time
import json
import os
from typing import Dict, NamedTuple
from castervoice.lib.actions import Key
from pathlib import Path
from caster_user_content import environment_variables as ev


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

def set_window(window_alias: str) -> None:
    """Set alias for current window"""
    window = pyautogui.getActiveWindow()
    if not window:
        print("No active window found")
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

def switch_to(window_alias: str) -> None:
    """Switch to window or tab based on stored alias type"""
    if window_alias not in aliases:
        print(f"No alias found for '{window_alias}'")
        return

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
        
    except Exception as e:
        print(f"Error switching: {e}")

def _get_taskbar_windows_in_order():
    """Get a list of window handles in taskbar order."""
    windows = []

    def enum_windows_proc(hwnd, lParam):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != "":
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            if not (style & win32con.WS_EX_TOOLWINDOW):
                windows.append(hwnd)
        return True

    win32gui.EnumWindows(enum_windows_proc, None)
    return windows

def switch_to_app_instance(window_alias: str, n: int = None) -> None:
    """Switch to a specific instance of an application by alias."""
    if n is None:
        n = 1  # Default to the first instance

    title_fragments = None
    for alias_entry in ev.WINDOW_ALIASES:
        if alias_entry[0] == window_alias:
            title_fragments = alias_entry[1]
            break
    if not title_fragments:
        print(f"No window titles defined for alias '{window_alias}'")
        return

    all_handles = _get_taskbar_windows_in_order()
    matching_handles = []
    for hwnd in all_handles:
        window_title = win32gui.GetWindowText(hwnd)
        if any(frag.lower() in window_title.lower() for frag in title_fragments):
            matching_handles.append(hwnd)

    if not matching_handles:
        print(f"No open windows found for alias '{window_alias}'")
        return

    if 1 <= n <= len(matching_handles):
        target_hwnd = matching_handles[n - 1]
        try:
            win32gui.SetForegroundWindow(target_hwnd)
            title = win32gui.GetWindowText(target_hwnd)
            print(f"Switched to instance {n} of '{window_alias}': {title}")
        except Exception as e:
            print(f"Failed to activate window: {e}")
    else:
        print(f"Instance {n} not found for '{window_alias}'. Found {len(matching_handles)} instances.")

# Load aliases when module is imported
load_aliases()