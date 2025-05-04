import pyautogui
import time
from castervoice.lib.actions import Key

def title(window_title):
    pyautogui.getWindowsWithTitle(window_title)[0].activate()


# Define application groups by their window title identifiers
CTRL_TAB_APPS = ['Waterfox', 'Firefox', 'Windows Terminal']
CTRL_PGDN_APPS = ['Windsurf', 'Cursor', 'VSCodium', 'Visual Studio Code']

window_info = {}

def set_alias(window_alias: str) -> None:
    """Set alias for current window, storing title for tabbed applications"""
    window = pyautogui.getActiveWindow()
    if window:
        is_tabbed_app = any(app in window.title for app in CTRL_TAB_APPS + CTRL_PGDN_APPS)
        info = {
            'handle': window._hWnd,
            'title': window.title if is_tabbed_app else None,
            'window_type': get_window_type(window.title)
        }
        window_info[window_alias] = info
        print(f"Set alias '{window_alias}' for: {window.title}")

def get_window_type(title):
    """Determine which type of tab switching to use"""
    if any(app in title for app in CTRL_TAB_APPS):
        return 'ctrl_tab'
    if any(app in title for app in CTRL_PGDN_APPS):
        return 'ctrl_pgdn'
    return None

def find_tab(target_title, window_type):
    """Cycle through tabs to find target using appropriate key combination"""
    initial_title = pyautogui.getActiveWindow().title
    tries = 0
    max_tries = 50  # Prevent infinite loop

    while tries < max_tries:
        current_title = pyautogui.getActiveWindow().title
        if target_title == current_title:
            return True
        
        # Use appropriate key combination based on application type
        if window_type == 'ctrl_tab':
            Key("c-tab").execute()
        elif window_type == 'ctrl_pgdn':
            Key("c-pgdown").execute()
            
        time.sleep(0.1)
        tries += 1

        # Stop if we've cycled back to start
        if tries > 1 and current_title == initial_title:
            break
    
    return False

def alias(window_alias: str) -> None:
    """Switch to window and find tab if applicable"""
    if window_alias not in window_info:
        print(f"No window found for alias '{window_alias}'")
        return

    info = window_info[window_alias]
    try:
        windows = pyautogui.getAllWindows()
        for window in windows:
            if window._hWnd == info['handle']:
                window.activate()
                time.sleep(0.1)
                # Only try to find specific tab if it's a tabbed application
                if info['title'] and info['window_type']:
                    find_tab(info['title'], info['window_type'])
                return
    except Exception as e:
        print(f"Error switching: {e}")