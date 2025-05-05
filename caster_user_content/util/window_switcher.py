import pyautogui
import time
from typing import Dict, NamedTuple

# Apps that support tabs and their tab-switching keys
TABBED_APPS = {
    'Waterfox': 'c-tab',
    'Firefox': 'c-tab',
    'Windows Terminal': 'c-tab',
    'WindSurf': 'c-pgdown',
    'Cursor': 'c-pgdown',
    'VSCodium': 'c-pgdown',
    'Visual Studio Code': 'c-pgdown'
}

class WindowInfo(NamedTuple):
    handle: int
    title: str
    is_tab: bool = False

# Separate storage for window and tab aliases
window_aliases: Dict[str, WindowInfo] = {}
tab_aliases: Dict[str, WindowInfo] = {}

def is_tabbed_app(window_title: str) -> bool:
    """Check if the window is a tabbed application"""
    return any(app in window_title for app in TABBED_APPS)

def get_tab_switch_key(window_title: str) -> str:
    """Get the appropriate tab switching key for the application"""
    for app, key in TABBED_APPS.items():
        if app in window_title:
            return key
    return 'c-tab'  # default

def set_alias(window_alias: str, is_tab: bool = False) -> None:
    """Set an alias for the current window or tab"""
    window = pyautogui.getActiveWindow()
    if not window:
        print("No active window found")
        return

    info = WindowInfo(
        handle=window._hWnd,
        title=window.title,
        is_tab=is_tab
    )

    if is_tab:
        if not is_tabbed_app(window.title):
            print(f"Warning: Setting tab alias for non-tabbed application: {window.title}")
        tab_aliases[window_alias] = info
        print(f"Set tab alias '{window_alias}' for: {window.title}")
    else:
        window_aliases[window_alias] = info
        print(f"Set window alias '{window_alias}' for: {window.title}")

def alias(window_alias: str, is_tab: bool = False) -> None:
    """Switch to a window or tab using its alias"""
    aliases = tab_aliases if is_tab else window_aliases
    
    if window_alias not in aliases:
        print(f"No {'tab' if is_tab else 'window'} found for alias '{window_alias}'")
        return

    info = aliases[window_alias]
    try:
        windows = pyautogui.getAllWindows()
        for window in windows:
            if window._hWnd == info.handle:
                window.activate()
                time.sleep(0.1)

                if is_tab and is_tabbed_app(window.title):
                    find_tab(window, info.title)
                return
        
        print(f"Window for alias '{window_alias}' not found")
        aliases.pop(window_alias)
        
    except Exception as e:
        print(f"Error switching: {e}")

def find_tab(window, target_title: str) -> bool:
    """Find specific tab in a window"""
    initial_title = window.title
    max_tries = 50
    
    tab_key = get_tab_switch_key(initial_title)
    
    for _ in range(max_tries):
        current_title = window.title
        
        if target_title == current_title:
            return True
            
        pyautogui.hotkey(*tab_key.split('-'))
        time.sleep(0.1)
        
        if _ > 0 and current_title == initial_title:
            break
    
    return False