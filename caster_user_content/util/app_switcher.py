import win32gui
import win32con
import win32com.client
from caster_user_content.environment_variables import WINDOWS_APP_ALIASES, WINDOWS_APP_NAMES

_SEPARATORS = (" - ", " – ", " — ")

def extract_app_name(caption: str) -> str:
    if not caption:
        return "<blank>"

    caption = caption.strip()

    # First, check for known app names
    for name in WINDOWS_APP_NAMES:
        if name.lower() in caption.lower():
            return name

    # Special case: Windows PowerShell
    if caption.lower().startswith(("windows powershell", "caster: status window")):
        return "Windows PowerShell"

    # Special case: Copilot
    if caption.lower().startswith("copilot"):
        return "Copilot"

    # Fallback: use separator logic
    for sep in _SEPARATORS:
        if sep in caption:
            parts = caption.split(sep)
            if len(parts) >= 2:
                # App name is usually at the end, but let's just return the last part
                return parts[-1].strip()

    return caption

def get_open_windows():
    windows = []
    
    def enum_cb(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and title not in ["Program Manager", "Windows Input Experience", "OmApSvcBroker"]:
                windows.append((hwnd, title))
                
    win32gui.EnumWindows(enum_cb, None)
    return windows

def show_window_info():
    print("\n--- Open Windows Info ---")
    windows = get_open_windows()
    for hwnd, title in windows:
        app_name = extract_app_name(title)
        
        # Check if we have an alias for this app
        alias = "N/A"
        for key, val in WINDOWS_APP_ALIASES.items():
            if isinstance(val, (list, tuple)):
                if any(v.lower() == app_name.lower() for v in val):
                    alias = key
                    break
            else:
                if val.lower() == app_name.lower():
                    alias = key
                    break
                
        print(f"HWND: {hwnd:<8} | Alias: {alias:<10} | App: {app_name:<20} | Title: {title}")

def switch_to_app(app_name, instance: int = 1) -> bool:
    if isinstance(app_name, (list, tuple)):
        app_names_lc = [a.lower() for a in app_name]
        app_name_display = "/".join(app_name)
    else:
        app_names_lc = [app_name.lower()]
        app_name_display = app_name
        
    windows = get_open_windows()
    
    # Filter windows by app_name
    matching_windows = []
    for hwnd, title in windows:
        if extract_app_name(title).lower() in app_names_lc:
            matching_windows.append((hwnd, title))
            
    if not matching_windows:
        print(f"No windows found for application(s) '{app_name_display}'.")
        return False
        
    if instance < 1 or instance > len(matching_windows):
        print(f"Application '{app_name_display}' only has {len(matching_windows)} "
              f"instance(s); requested #{instance}.")
        return False
        
    # By default EnumWindows returns windows in Z-order (top to bottom).
    # Instance 1 is the most recently used matching window.
    target_hwnd, target_title = matching_windows[instance - 1]
    
    print(f"Switching to HWND: {target_hwnd} | Title: {target_title}")
    
    # Switch to the window
    try:
        # Hack to allow SetForegroundWindow to work reliably
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        
        # If minimized, restore it
        placement = win32gui.GetWindowPlacement(target_hwnd)
        if placement[1] == win32con.SW_SHOWMINIMIZED:
            win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)
            
        win32gui.SetForegroundWindow(target_hwnd)
        return True
    except Exception as e:
        print(f"Failed to switch to window: {e}")
        return False

if __name__ == "__main__":
    show_window_info()

