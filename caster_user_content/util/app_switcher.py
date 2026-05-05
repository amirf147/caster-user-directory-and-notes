import win32gui
import win32con
import win32com.client
from caster_user_content.environment_variables import WINDOWS_APP_ALIASES, WINDOWS_APP_NAMES

# Try to import pyvda for Virtual Desktop tracking
try:
    from pyvda import AppView, VirtualDesktop
    PYVDA_AVAILABLE = True
except ImportError:
    PYVDA_AVAILABLE = False
    print("WARNING: pyvda not installed. Workspace awareness will be disabled. Run: pip install pyvda")

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
    
    current_desktop_id = None
    if PYVDA_AVAILABLE:
        try:
            current_desktop_id = VirtualDesktop.current().id
        except Exception:
            pass

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
        
        # Add workspace info to debug output
        workspace_status = ""
        if PYVDA_AVAILABLE and current_desktop_id:
            try:
                if AppView(hwnd=hwnd).desktop_id == current_desktop_id:
                    workspace_status = "[Current WS]"
                else:
                    workspace_status = "[Other WS]"
            except Exception:
                pass
                
        print(f"HWND: {hwnd:<8} {workspace_status:<12} | Alias: {alias:<10} | App: {app_name:<20} | Title: {title}")

def switch_to_app(app_name, instance: int = 1) -> bool:
    if isinstance(app_name, (list, tuple)):
        app_names_lc = [a.lower() for a in app_name]
        app_name_display = "/".join(app_name)
    else:
        app_names_lc = [app_name.lower()]
        app_name_display = app_name
        
    windows = get_open_windows()
    
    # 1. Identify current Virtual Desktop ID
    current_desktop_id = None
    if PYVDA_AVAILABLE:
        try:
            current_desktop_id = VirtualDesktop.current().id
        except Exception as e:
            print(f"Failed to get current Virtual Desktop ID: {e}")

    # 2. Filter windows by app_name AND restrict to current workspace
    matching_windows = []
    other_workspace_windows = 0

    for hwnd, title in windows:
        if extract_app_name(title).lower() in app_names_lc:
            if PYVDA_AVAILABLE and current_desktop_id:
                try:
                    app_view = AppView(hwnd=hwnd)
                    if app_view.desktop_id == current_desktop_id:
                        matching_windows.append((hwnd, title))
                    else:
                        other_workspace_windows += 1
                except Exception:
                    # Fallback if pyvda fails to read this specific handle
                    matching_windows.append((hwnd, title))
            else:
                matching_windows.append((hwnd, title))
            
    if not matching_windows:
        if other_workspace_windows > 0:
            print(f"Found {other_workspace_windows} instance(s) of '{app_name_display}' on OTHER workspaces. Ignoring to prevent snap-back.")
        else:
            print(f"No windows found for application(s) '{app_name_display}'.")
        return False
        
    if instance < 1 or instance > len(matching_windows):
        print(f"Application '{app_name_display}' only has {len(matching_windows)} "
              f"instance(s) on the CURRENT workspace; requested #{instance}.")
        return False
        
    # Target is strictly pulled from current workspace matches
    target_hwnd, target_title = matching_windows[instance - 1]
    
    print(f"Switching to HWND: {target_hwnd} | Title: {target_title}")
    
    # Switch to the window
    try:
        # If minimized, restore it first via win32gui
        placement = win32gui.GetWindowPlacement(target_hwnd)
        if placement[1] == win32con.SW_SHOWMINIMIZED:
            win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)
            
        # Use pywinauto to reliably set focus
        from pywinauto import Application
        app = Application().connect(handle=target_hwnd)
        app.window(handle=target_hwnd).set_focus()
        
        return True
    except Exception as e:
        print(f"Failed to switch to window using pywinauto: {e}")
        
        # Fallback to win32gui and WScript.Shell hack
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')
            win32gui.SetForegroundWindow(target_hwnd)
            return True
        except Exception as fallback_e:
            print(f"Fallback focus method also failed: {fallback_e}")
            return False

if __name__ == "__main__":
    show_window_info()