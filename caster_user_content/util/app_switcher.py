import win32gui
import win32con
import win32com.client
import time
import json
import os
from pathlib import Path
from typing import Dict, NamedTuple, List, Tuple, Any

from castervoice.lib.actions import Key
from pywinauto import Desktop
from pywinauto.findwindows import ElementNotFoundError

from caster_user_content.environment_variables import WINDOWS_APP_ALIASES, WINDOWS_APP_NAMES

# Try to import pyvda for Virtual Desktop tracking
try:
    from pyvda import AppView, VirtualDesktop
    PYVDA_AVAILABLE = True
except ImportError:
    PYVDA_AVAILABLE = False
    print("WARNING: pyvda not installed. Workspace awareness will be disabled. Run: pip install pyvda")

# Define application groups by their window title identifiers for tab switching
CTRL_TAB_APPS = ['Waterfox', 'Firefox', 'Windows Terminal']
CTRL_PGDN_APPS = ['Windsurf', 'Cursor', 'VSCodium', 'Visual Studio Code', 'Antigravity IDE']

_SEPARATORS = (" - ", " – ", " — ")

class WindowInfo(NamedTuple):
    handle: int
    title: str
    is_tab: bool = False
    window_type: str = None

# Get path to store aliases
CASTER_USER_DIR = Path(os.path.expanduser("~/AppData/Local/caster/caster_user_content/"))
ALIASES_FILE = CASTER_USER_DIR / "window_aliases.json"

# Dictionary for aliases
aliases: Dict[str, WindowInfo] = {}

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

load_aliases()

def extract_app_name(caption: str) -> str:
    if not caption:
        return "<blank>"

    caption = caption.strip()
    for name in sorted(WINDOWS_APP_NAMES, key=len, reverse=True):
        if name.lower() in caption.lower():
            return name

    if caption.lower().startswith(("windows powershell", "caster: status window")):
        return "Windows PowerShell"
    if caption.lower().startswith("copilot"):
        return "Copilot"

    for sep in _SEPARATORS:
        if sep in caption:
            parts = caption.split(sep)
            if len(parts) >= 2:
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

class TaskbarItem(NamedTuple):
    control: Any
    text: str
    app_name: str
    instance_index: int
    total_instances: int

def _get_taskbar_buttons():
    try:
        taskbar = Desktop(backend="uia").window(class_name="Shell_TrayWnd")
        if not taskbar.exists(): return []
        all_toolbars = taskbar.descendants(control_type="ToolBar")
        button_container = None
        for tb in all_toolbars:
            if tb.window_text() == "Running applications":
                button_container = tb
                break
        if not button_container: return []
        return button_container.children(control_type="Button") or []
    except Exception:
        return []

def extract_total_instances(caption: str) -> int:
    try:
        last_segment = caption.split(" - ")[-1]
        return int(last_segment.split()[0])
    except (IndexError, ValueError):
        return 1

def get_taskbar_items() -> List[TaskbarItem]:
    items = []
    instance_tracker = {}
    for btn in _get_taskbar_buttons():
        caption = btn.window_text()
        app = extract_app_name(caption)
        total = extract_total_instances(caption)
        count = instance_tracker.get(app, 0) + 1
        instance_tracker[app] = count
        items.append(TaskbarItem(control=btn, text=caption, app_name=app, instance_index=count, total_instances=total))
    return items

def _desktop(backend="uia"):
    return Desktop(backend=backend)

def _get_active_window_wrapper():
    try:
        w = _desktop("uia").get_active()
        if w is not None: return w, int(w.handle), w.window_text()
    except Exception: pass
    try:
        w = _desktop("win32").get_active()
        if w is not None: return w, int(w.handle), w.window_text()
    except Exception: pass
    if win32gui:
        h = win32gui.GetForegroundWindow()
        if h:
            try:
                w_uia = _desktop("uia").window(handle=h)
                return w_uia, int(h), w_uia.window_text()
            except Exception:
                title = win32gui.GetWindowText(h)
                return None, int(h), title or ""
    return None, None, ""

def get_window_type(title: str) -> str:
    if any(app in title for app in CTRL_TAB_APPS): return 'ctrl_tab'
    if any(app in title for app in CTRL_PGDN_APPS): return 'ctrl_pgdn'
    return None

def set_window(window_alias: str) -> None:
    w, handle, title_text = _get_active_window_wrapper()
    if not handle: return
    aliases[window_alias] = WindowInfo(handle=handle, title=title_text, is_tab=False, window_type=get_window_type(title_text))
    print(f"Set window alias '{window_alias}' for: {title_text}")
    save_aliases()

def set_page(window_alias: str) -> None:
    w, handle, title_text = _get_active_window_wrapper()
    if not handle: return
    window_type = get_window_type(title_text)
    aliases[window_alias] = WindowInfo(handle=handle, title=title_text, is_tab=True, window_type=window_type)
    print(f"Set tab alias '{window_alias}' for: {title_text}")
    save_aliases()

def find_tab(target_title: str, window_type: str) -> bool:
    _, __, initial_title = _get_active_window_wrapper()
    tries = 0
    while tries < 50:
        _, __, current_title = _get_active_window_wrapper()
        if target_title == current_title: return True
        if window_type == 'ctrl_tab': Key("c-tab").execute()
        elif window_type == 'ctrl_pgdn': Key("c-pgdown").execute()
        time.sleep(0.1)
        tries += 1
        if tries > 1 and current_title == initial_title: break
    return False

def show_window_info():
    print("\n--- Open Windows Info ---")
    windows = get_open_windows()
    for hwnd, title in windows:
        print(f"HWND: {hwnd:<8} | App: {extract_app_name(title):<20} | Title: {title}")

def switch_to_app(app_name, instance: int = 1) -> bool:
    """Switches to app using a 3-tier failsafe approach."""
    if isinstance(app_name, (list, tuple)):
        app_names_lc = [a.lower() for a in app_name]
        app_name_display = "/".join(app_name)
    else:
        app_names_lc = [app_name.lower()]
        app_name_display = app_name
        
    # Find matching window in workspace
    current_desktop_id = None
    if PYVDA_AVAILABLE:
        try: current_desktop_id = VirtualDesktop.current().id
        except Exception: pass

    windows = get_open_windows()
    matching_windows = []
    
    for hwnd, title in windows:
        if extract_app_name(title).lower() in app_names_lc:
            if PYVDA_AVAILABLE and current_desktop_id:
                try:
                    if AppView(hwnd=hwnd).desktop_id == current_desktop_id:
                        matching_windows.append((hwnd, title))
                except Exception:
                    matching_windows.append((hwnd, title))
            else:
                matching_windows.append((hwnd, title))
            
    if not matching_windows:
        print(f"No windows found for '{app_name_display}'.")
        return False
        
    if instance < 1 or instance > len(matching_windows):
        print(f"App '{app_name_display}' only has {len(matching_windows)} instances; requested #{instance}.")
        return False
        
    target_hwnd, target_title = matching_windows[instance - 1]
    
    # Tier 1: Pywinauto / Win32gui
    try:
        placement = win32gui.GetWindowPlacement(target_hwnd)
        if placement[1] == win32con.SW_SHOWMINIMIZED:
            win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)
            
        from pywinauto import Application
        app = Application().connect(handle=target_hwnd)
        app.window(handle=target_hwnd).set_focus()
        return True
    except Exception as e:
        print(f"Tier 1 Pywinauto focus failed: {e}")
        
    # Tier 2: Taskbar UIA Click
    try:
        t_items = get_taskbar_items()
        app_items = [it for it in t_items if it.app_name.lower() in app_names_lc]
        if app_items and len(app_items) >= instance:
            app_items.sort(key=lambda it: it.instance_index)
            target_item = app_items[instance - 1]
            target_item.control.click_input()
            return True
    except Exception as e:
        print(f"Tier 2 Taskbar UIA failed: {e}")
        
    # Tier 3: Keyboard Macro
    try:
        t_items = get_taskbar_items()
        target_idx = -1
        count = 0
        for i, item in enumerate(t_items):
            if item.app_name.lower() in app_names_lc:
                count += 1
                if count == instance:
                    target_idx = i
                    break
        if target_idx != -1:
            print(f"Tier 3 Keyboard Macro executing for taskbar index {target_idx}")
            Key(f"w-t/3, home, right:{target_idx}/3, enter").execute()
            return True
    except Exception as e:
        print(f"Tier 3 Keyboard Macro failed: {e}")
        
    return False

def title(window_title: str):
    """Activate a window whose title contains the given substring."""
    try:
        for backend in ("uia", "win32"):
            try:
                for w in _desktop(backend).windows():
                    try:
                        if window_title in w.window_text():
                            handle = int(w.handle)
                            placement = win32gui.GetWindowPlacement(handle)
                            if placement[1] == win32con.SW_SHOWMINIMIZED:
                                w.restore()
                            try: w.set_focus()
                            except Exception:
                                try: w.wrapper_object().set_focus()
                                except Exception: pass
                            return
                    except Exception: continue
            except Exception: continue
    except Exception as e:
        print(f"Error activating by title: {e}")

def switch_to_alias(window_alias: str) -> None:
    if window_alias not in aliases:
        print(f"No alias found for '{window_alias}'")
        return
        
    info = aliases[window_alias]
    try:
        try: w = _desktop("uia").window(handle=info.handle)
        except Exception: w = _desktop("win32").window(handle=info.handle)
        
        handle = int(info.handle)
        placement = win32gui.GetWindowPlacement(handle)
        if placement[1] == win32con.SW_SHOWMINIMIZED:
            w.restore()
            
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
                    
        # Failsafe for alias
        if not focused:
            app_name = extract_app_name(info.title)
            print(f"Falling back to switch_to_app for {app_name}")
            switch_to_app(app_name)
            
        time.sleep(0.1)
        if info.is_tab and info.window_type:
            find_tab(info.title, info.window_type)
            
    except ElementNotFoundError:
        print(f"Window for alias '{window_alias}' not found, dropping alias.")
        aliases.pop(window_alias, None)
        save_aliases()
    except Exception as e:
        print(f"Error switching: {e}")

if __name__ == "__main__":
    show_window_info()