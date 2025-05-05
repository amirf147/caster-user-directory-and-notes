import pyautogui
import time
from typing import Dict, NamedTuple
from castervoice.lib.actions import Key


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

# Single dictionary for all aliases
aliases: Dict[str, WindowInfo] = {}

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

def find_tab(target_title: str, window_type: str) -> bool:
    """Find specific tab using Caster Key actions"""
    initial_title = pyautogui.getActiveWindow().title
    tries = 0
    max_tries = 50

    while tries < max_tries:
        current_title = pyautogui.getActiveWindow().title
        if target_title == current_title:
            return True
        
        # Use Caster Key action for tab switching
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
        
    except Exception as e:
        print(f"Error switching: {e}")