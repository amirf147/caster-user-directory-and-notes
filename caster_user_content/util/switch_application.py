import pyautogui
import time
from castervoice.lib.actions import Key

def title(window_title):
    pyautogui.getWindowsWithTitle(window_title)[0].activate()


class WindowInfo:
    def __init__(self, hwnd, tab_title=None):
        self.hwnd = hwnd
        self.tab_title = tab_title

window_info = {}

def get_browser_tab_title():
    """Get the current browser tab title"""
    active_window = pyautogui.getActiveWindow()
    if active_window:
        return active_window.title
    return None

def set_alias(window_alias: str) -> None:
    """
    Set an alias for the currently focused window and tab
    
    Args:
        window_alias (str): The alias name to assign to the window
    """
    active_window = pyautogui.getActiveWindow()
    if active_window:
        tab_title = get_browser_tab_title()
        window_info[window_alias] = WindowInfo(active_window._hWnd, tab_title)
        print(f"Window alias '{window_alias}' set (ID: {active_window._hWnd}, Tab: {tab_title})")

def find_and_activate_tab(window, target_tab_title):
    """Find and activate the specific tab"""
    if not target_tab_title:
        return

    # Store the initial tab title
    initial_tab = get_browser_tab_title()
    
    # Try to find the tab by cycling through tabs
    max_tries = 50  # Prevent infinite loop
    tries = 0
    
    while tries < max_tries:
        current_tab = get_browser_tab_title()
        
        if current_tab and target_tab_title in current_tab:
            return True  # Found the tab
            
        # Press Ctrl+Tab to move to next tab
        Key("c-tab").execute()
        time.sleep(0.1)  # Small delay to let the tab switch
        tries += 1
        
        # If we've cycled back to the initial tab, stop searching
        if tries > 1 and current_tab == initial_tab:
            break
    
    return False

def alias(window_alias: str) -> None:
    """
    Switch to a window using its alias and restore the specific tab
    
    Args:
        window_alias (str): The alias name of the window to switch to
    """
    if window_alias not in window_info:
        print(f"No window found with alias '{window_alias}'")
        return
    
    info = window_info[window_alias]
    try:
        # Get all windows
        windows = pyautogui.getAllWindows()
        # Find the window with matching handle
        for window in windows:
            if window._hWnd == info.hwnd:
                window.activate()
                time.sleep(0.2)  # Wait for window to activate
                
                # If we stored a tab title, try to find and activate it
                if info.tab_title:
                    if not find_and_activate_tab(window, info.tab_title):
                        print(f"Could not find tab: {info.tab_title}")
                return
        print(f"Window with ID {info.hwnd} not found")
    except Exception as e:
        print(f"Error switching to window: {e}")