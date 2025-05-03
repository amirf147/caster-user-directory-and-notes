import pyautogui

def title(window_title):
    pyautogui.getWindowsWithTitle(window_title)[0].activate()


# Dictionary to store window PIDs for aliases
window_pids = {}

def set_alias(window_alias: str) -> None:
    """
    Set an alias for the currently focused window
    
    Args:
        window_alias (str): The alias name to assign to the window
    """
    active_window = pyautogui.getActiveWindow()
    if active_window:
        window_pids[window_alias] = active_window._hWnd  # Store the window handle
        print(f"Window alias '{window_alias}' set (ID: {active_window._hWnd})")

def alias(window_alias: str) -> None:
    """
    Switch to a window using its alias
    
    Args:
        window_alias (str): The alias name of the window to switch to
    """
    if window_alias not in window_pids:
        print(f"No window found with alias '{window_alias}'")
        return
    
    hwnd = window_pids[window_alias]
    try:
        # Get all windows
        windows = pyautogui.getAllWindows()
        # Find the window with matching handle
        for window in windows:
            if window._hWnd == hwnd:
                window.activate()
                return
        print(f"Window with ID {hwnd} not found")
    except Exception as e:
        print(f"Error switching to window: {e}")