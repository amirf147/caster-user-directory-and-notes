"""
App Switcher: Sub-millisecond Native Win32 Window Manager & Focus Engine

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

import contextlib
import ctypes
import datetime
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

import win32api
import win32con
import win32gui
import win32process
from caster_user_content.environment_variables import WINDOWS_APP_NAMES
from castervoice.lib import printer
from castervoice.lib.actions import Key
from pywinauto import Desktop
from pywinauto.findwindows import ElementNotFoundError


def _log(level: str, msg: str):
    ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] [AppSwitcher:{level}] {msg}", flush=True)


# Try to import pyvda for Virtual Desktop tracking
try:
    from pyvda import AppView, VirtualDesktop

    PYVDA_AVAILABLE = True
except ImportError:
    PYVDA_AVAILABLE = False
    print("WARNING: pyvda not installed. Workspace awareness will be disabled. Run: pip install pyvda")

# Define application groups by their window title identifiers for tab switching
CTRL_TAB_APPS = ["Waterfox", "Firefox", "Windows Terminal"]
CTRL_PGDN_APPS = ["Windsurf", "Cursor", "VSCodium", "Visual Studio Code", "Antigravity IDE"]

_SEPARATORS = (" - ", " – ", " — ")

# Virtual Key constants for synthetic input
VK_MENU = 0x12  # Alt key
VK_NONE = 0xFF  # Unassigned dummy key to cancel menu focus activation


class WindowInfo(NamedTuple):
    handle: int
    title: str
    is_tab: bool = False
    window_type: Optional[str] = None


class TaskbarItem(NamedTuple):
    slot_index: int
    text: str
    app_name: str
    instance_index: int
    total_instances: int
    control: Any = None


# Get path to store aliases
CASTER_USER_DIR = Path(os.path.expanduser("~/AppData/Local/caster/caster_user_content/"))
ALIASES_FILE = CASTER_USER_DIR / "window_aliases.json"


class AliasRegistry:
    """Encapsulates persistent window and tab alias state."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self._aliases: Dict[str, WindowInfo] = {}
        self.load()

    @property
    def aliases(self) -> Dict[str, WindowInfo]:
        return self._aliases

    def load(self) -> None:
        """Load aliases from JSON file."""
        try:
            if self.filepath.exists():
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._aliases = {k: WindowInfo(**v) for k, v in data.items()}
                _log("DEBUG", f"Loaded {len(self._aliases)} aliases from {self.filepath}")
        except Exception as e:
            _log("ERROR", f"Error loading aliases: {e}")
            self._aliases = {}

    def save(self) -> None:
        """Persist aliases to JSON file."""
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            data = {k: v._asdict() for k, v in self._aliases.items()}
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            _log("ERROR", f"Error saving aliases: {e}")

    def get(self, key: str) -> Optional[WindowInfo]:
        return self._aliases.get(str(key))

    def set(self, key: str, info: WindowInfo) -> None:
        self._aliases[str(key)] = info
        self.save()

    def remove(self, key: str) -> bool:
        k = str(key)
        if k in self._aliases:
            del self._aliases[k]
            self.save()
            return True
        return False

    def remove_by_handle(self, handle: int) -> List[str]:
        keys_to_remove = [k for k, v in self._aliases.items() if v.handle == handle]
        for k in keys_to_remove:
            del self._aliases[k]
        if keys_to_remove:
            self.save()
        return keys_to_remove

    def clear(self) -> None:
        self._aliases.clear()
        self.save()


# Instantiate registry and expose backward-compatible module-level aliases
alias_registry = AliasRegistry(ALIASES_FILE)
aliases: Dict[str, WindowInfo] = alias_registry.aliases


def load_aliases() -> None:
    alias_registry.load()


def save_aliases() -> None:
    alias_registry.save()


@contextlib.contextmanager
def _alt_key_bypass():
    """
    Context manager that simulates an Alt key press to reset ForegroundLockTimeout.
    Guarantees that dummy cancel and Alt key-up events are ALWAYS sent, even on error.
    """
    user32 = ctypes.windll.user32
    user32.keybd_event(VK_MENU, 0, 0, 0)  # Alt down
    try:
        yield
    finally:
        try:
            user32.keybd_event(VK_NONE, 0, 0, 0)  # Dummy down (cancels menu bar focus)
            user32.keybd_event(VK_NONE, 0, 2, 0)  # Dummy up
        finally:
            user32.keybd_event(VK_MENU, 0, 2, 0)  # Alt up


@contextlib.contextmanager
def _attached_threads(target_hwnd: int):
    """
    Context manager that safely attaches the current thread to the foreground thread
    and target thread input queues, guaranteeing detachment in finally blocks.
    """
    current_thread = win32api.GetCurrentThreadId()
    fore_hwnd = win32gui.GetForegroundWindow()
    fore_thread = (
        win32process.GetWindowThreadProcessId(fore_hwnd)[0] if (fore_hwnd and win32gui.IsWindow(fore_hwnd)) else 0
    )
    target_thread = (
        win32process.GetWindowThreadProcessId(target_hwnd)[0] if (target_hwnd and win32gui.IsWindow(target_hwnd)) else 0
    )

    attached_fore = False
    attached_target = False

    try:
        if fore_thread and fore_thread != current_thread:
            try:
                win32process.AttachThreadInput(current_thread, fore_thread, True)
                attached_fore = True
            except Exception as e:
                _log("DEBUG", f"AttachThreadInput to fore_thread {fore_thread} failed: {e}")

        if target_thread and target_thread != current_thread and target_thread != fore_thread:
            try:
                win32process.AttachThreadInput(current_thread, target_thread, True)
                attached_target = True
            except Exception as e:
                _log("DEBUG", f"AttachThreadInput to target_thread {target_thread} failed: {e}")

        yield
    finally:
        if attached_fore:
            try:
                win32process.AttachThreadInput(current_thread, fore_thread, False)
            except Exception as e:
                _log("DEBUG", f"DetachThreadInput from fore_thread {fore_thread} failed: {e}")
        if attached_target:
            try:
                win32process.AttachThreadInput(current_thread, target_thread, False)
            except Exception as e:
                _log("DEBUG", f"DetachThreadInput from target_thread {target_thread} failed: {e}")


def _ensure_window_shown(handle: int) -> None:
    """Restores window if minimized, otherwise ensures it is visible."""
    try:
        if win32gui.IsIconic(handle):
            win32gui.ShowWindow(handle, win32con.SW_RESTORE)
        else:
            win32gui.ShowWindow(handle, win32con.SW_SHOW)
    except Exception as e:
        _log("DEBUG", f"ShowWindow failed for HWND {handle}: {e}")


def verify_focus(target_hwnd: int, timeout: float = 0.5) -> bool:
    """Helper to verify if the active window has successfully switched to the target handle."""
    if not target_hwnd or not win32gui.IsWindow(target_hwnd):
        return False
    if win32gui.GetForegroundWindow() == target_hwnd:
        return True
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(0.01)  # 10ms micro-polling
        if win32gui.GetForegroundWindow() == target_hwnd:
            return True
    return False


def extract_app_name(caption: str) -> str:
    if not caption:
        return "<blank>"

    # Strip taskbar suffix if present (e.g. " - 1 running window")
    cleaned = caption.strip()
    suffix_match = re.search(r"\s*-\s*\d+\s+running\s+window.*$", cleaned, flags=re.IGNORECASE)
    if suffix_match:
        cleaned = cleaned[: suffix_match.start()].strip()

    for name in sorted(WINDOWS_APP_NAMES, key=len, reverse=True):
        if name.lower() in cleaned.lower():
            return name

    if cleaned.lower().startswith(("windows powershell", "powershell", "caster: status window")):
        return "Windows PowerShell"
    if cleaned.lower().startswith("copilot"):
        return "Copilot"

    for sep in _SEPARATORS:
        if sep in cleaned:
            parts = cleaned.split(sep)
            if len(parts) >= 2:
                return parts[-1].strip()

    return cleaned


def extract_total_instances(caption: str) -> int:
    try:
        last_segment = caption.split(" - ")[-1]
        return int(last_segment.split()[0])
    except (IndexError, ValueError):
        return 1


class WindowsOSAdapter:
    """Deep interface adapter encapsulating raw OS calls to win32gui, pywinauto, and pyvda."""

    def __init__(self):
        self._desktop_uia = Desktop(backend="uia")
        self._desktop_win32 = Desktop(backend="win32")

    def get_open_windows(self) -> List[Tuple[int, str]]:
        windows = []

        def enum_cb(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and title not in ["Program Manager", "Windows Input Experience", "OmApSvcBroker"]:
                    windows.append((hwnd, title))

        win32gui.EnumWindows(enum_cb, None)
        return windows

    def get_active_window(self) -> Tuple[Any, int, str]:
        """Fast retrieval of the active foreground window handle and title."""
        try:
            h = win32gui.GetForegroundWindow()
            if h and win32gui.IsWindow(h):
                title_text = win32gui.GetWindowText(h)
                try:
                    w_uia = self._desktop_uia.window(handle=h)
                    return w_uia, int(h), title_text or ""
                except Exception:
                    return None, int(h), title_text or ""
        except Exception as e:
            _log("DEBUG", f"get_active_window fallback exception: {e}")
        return None, None, ""

    def get_taskbar_order(self) -> List[str]:
        """
        Retrieves the ordered list of application button captions on the Windows taskbar.
        Pure read-only discovery supporting both Windows 11 (XAML Island) and Windows 10 (ToolBar).
        No mouse simulation or UIA activation patterns are invoked.
        """
        captions = []
        try:
            hwnd_tb = win32gui.FindWindow("Shell_TrayWnd", None)
            if not hwnd_tb:
                return []
            taskbar = self._desktop_uia.window(handle=hwnd_tb)
            if not taskbar.exists():
                return []

            # 1. Windows 11 XAML Island Path
            for c in taskbar.children():
                if "InputSite" in c.element_info.class_name:
                    for child in c.children():
                        if "TaskbarFrame" in child.element_info.class_name:
                            for btn in child.children():
                                if "TaskListButton" in btn.element_info.class_name:
                                    captions.append(btn.window_text())
                            if captions:
                                return captions

            # 2. Windows 10 Fallback Path (Win32 ToolBar)
            for tb_bar in taskbar.descendants(control_type="ToolBar"):
                if tb_bar.window_text() == "Running applications":
                    for btn in tb_bar.children(control_type="Button"):
                        captions.append(btn.window_text())
                    break
        except Exception as e:
            _log("DEBUG", f"get_taskbar_order exception: {e}")
        return captions

    def get_taskbar_items(self) -> List[TaskbarItem]:
        """
        Builds an ordered list of TaskbarItem objects for taskbar navigation.
        Derived from pure read-only taskbar discovery.
        """
        items: List[TaskbarItem] = []
        captions = self.get_taskbar_order()
        instance_tracker: Dict[str, int] = {}

        for slot_idx, caption in enumerate(captions, start=1):
            app = extract_app_name(caption)
            total = extract_total_instances(caption)
            count = instance_tracker.get(app, 0) + 1
            instance_tracker[app] = count

            items.append(
                TaskbarItem(
                    slot_index=slot_idx,
                    text=caption,
                    app_name=app,
                    instance_index=count,
                    total_instances=total,
                )
            )
        return items

    def taskbar_keystroke_switch(self, target_hwnd: int, app_name: Optional[Any] = None, instance: int = 1) -> bool:
        """
        Tier 4 Fail-Safe: Activates target window via shell hotkeys (Win+T traversal / Win+<N>).
        Delegates foreground activation to explorer.exe, bypassing Windows UIPI restrictions.
        """
        items = self.get_taskbar_items()
        if not items:
            _log("DEBUG", "Tier 4: No taskbar items discovered.")
            return False

        target_item: Optional[TaskbarItem] = None

        if app_name:
            if isinstance(app_name, (list, tuple)):
                app_names_lc = [a.lower() for a in app_name]
            else:
                app_names_lc = [app_name.lower()]

            matching_items = [it for it in items if it.app_name.lower() in app_names_lc]
            if matching_items and len(matching_items) >= instance:
                matching_items.sort(key=lambda it: it.instance_index)
                target_item = matching_items[instance - 1]

        # If not matched by app name, attempt direct matching against target_hwnd title
        if not target_item and target_hwnd and win32gui.IsWindow(target_hwnd):
            hwnd_title = win32gui.GetWindowText(target_hwnd).strip().lower()
            hwnd_app = extract_app_name(hwnd_title).lower()
            for it in items:
                if hwnd_title and hwnd_title in it.text.lower():
                    target_item = it
                    break
                if hwnd_app and it.app_name.lower() == hwnd_app:
                    target_item = it
                    break

        if not target_item:
            _log("DEBUG", f"Tier 4: Could not resolve taskbar button slot for HWND {target_hwnd}.")
            return False

        slot = target_item.slot_index
        _log(
            "INFO",
            f"Tier 4: Selected taskbar slot {slot} for '{target_item.text}' (app: '{target_item.app_name}', instance #{target_item.instance_index})",
        )

        if 1 <= slot <= 10:
            key_num = slot % 10
            Key(f"w-{key_num}/50").execute()
        else:
            Key(f"w-t/25, home/10, right:{slot - 1}, enter/25").execute()

        return verify_focus(target_hwnd, timeout=0.5)

    def get_current_desktop_id(self):
        if PYVDA_AVAILABLE:
            try:
                return VirtualDesktop.current().id
            except Exception:
                pass
        return None

    def get_window_desktop_id(self, handle: int):
        if PYVDA_AVAILABLE:
            try:
                start_t = time.time()
                d_id = AppView(hwnd=handle).desktop_id
                elapsed = (time.time() - start_t) * 1000
                _log("DEBUG", f"AppView for HWND {handle} returned {d_id} in {elapsed:.2f}ms")
                return d_id
            except Exception as e:
                _log("DEBUG", f"AppView Exception for HWND {handle}: {e}")
        return None

    def restore_and_focus(self, handle: int, app_name: Optional[Any] = None, instance: int = 1) -> bool:
        """
        Attempt to restore and set focus to a specific window handle
        using progressive, non-blocking Win32 tiers.
        """
        if not handle or not win32gui.IsWindow(handle):
            _log("ERROR", f"HWND {handle} is no longer a valid window.")
            return False

        # Fast check if already active
        if win32gui.GetForegroundWindow() == handle:
            return True

        # 0. Allow SetForegroundWindow (best-effort)
        try:
            ctypes.windll.user32.AllowSetForegroundWindow(-1)
        except Exception:
            pass

        # Restore window if minimized
        _ensure_window_shown(handle)

        # ---------------------------------------------------------
        # TIER 1: Direct Win32 SetForegroundWindow (Fast Path: ~0-10ms)
        # ---------------------------------------------------------
        try:
            win32gui.BringWindowToTop(handle)
            win32gui.SetForegroundWindow(handle)
        except Exception as e:
            _log("DEBUG", f"Tier 1 SetForegroundWindow failed for HWND {handle}: {e}")

        if verify_focus(handle, timeout=0.08):
            return True

        # ---------------------------------------------------------
        # TIER 2: Alt-Key Bypass (Tricks OS ForegroundLockTimeout)
        # ---------------------------------------------------------
        _log("DEBUG", f"Tier 1 failed. Attempting Tier 2 (Alt-Key Bypass) for HWND {handle}...")
        try:
            with _alt_key_bypass():
                win32gui.BringWindowToTop(handle)
                win32gui.SetForegroundWindow(handle)
        except Exception as e:
            _log("DEBUG", f"Tier 2 Alt-Bypass failed for HWND {handle}: {e}")

        if verify_focus(handle, timeout=0.12):
            return True

        # ---------------------------------------------------------
        # TIER 3: Dual-Thread Input Attachment + SwitchToThisWindow
        # ---------------------------------------------------------
        _log("DEBUG", f"Tier 2 failed. Attempting Tier 3 (Thread Attachment) for HWND {handle}...")
        try:
            with _attached_threads(handle):
                with _alt_key_bypass():
                    win32gui.BringWindowToTop(handle)
                    win32gui.SetForegroundWindow(handle)
                try:
                    # SwitchToThisWindow is a legacy shell API that activates the window
                    ctypes.windll.user32.SwitchToThisWindow(handle, True)
                except Exception:
                    pass
        except Exception as e:
            _log("ERROR", f"Tier 3 Thread Attachment failed for HWND {handle}: {e}")

        if verify_focus(handle, timeout=0.2):
            return True

        # ---------------------------------------------------------
        # TIER 4: Taskbar Keystroke Navigation (Win+T Traversal Fail-Safe)
        # ---------------------------------------------------------
        _log("DEBUG", f"Tier 3 failed. Attempting Tier 4 (Taskbar Keystroke Navigation) for HWND {handle}...")
        try:
            if self.taskbar_keystroke_switch(handle, app_name=app_name, instance=instance):
                _log("INFO", f"Tier 4: Successfully focused HWND {handle} via taskbar keystroke navigation")
                return True
        except Exception as e:
            _log("ERROR", f"Tier 4 Taskbar Keystroke Navigation failed for HWND {handle}: {e}")

        return False

    def iter_windows(self):
        """Yields windows from both UIA and Win32 backends."""
        for backend in ("uia", "win32"):
            try:
                for w in (self._desktop_uia if backend == "uia" else self._desktop_win32).windows():
                    yield w
            except Exception:
                continue

    def get_window_by_handle(self, handle: int):
        try:
            return self._desktop_uia.window(handle=handle)
        except Exception:
            return self._desktop_win32.window(handle=handle)


os_env = WindowsOSAdapter()


def get_window_type(title: str) -> Optional[str]:
    if any(app in title for app in CTRL_TAB_APPS):
        return "ctrl_tab"
    if any(app in title for app in CTRL_PGDN_APPS):
        return "ctrl_pgdn"
    return None


def set_window(window_alias: Any) -> None:
    window_alias = str(window_alias)
    _, handle, title_text = os_env.get_active_window()
    if not handle:
        return
    info = WindowInfo(handle=handle, title=title_text, is_tab=False, window_type=get_window_type(title_text))
    alias_registry.set(window_alias, info)
    print(f"Set window alias '{window_alias}' for: {title_text}")


def set_page(window_alias: Any) -> None:
    window_alias = str(window_alias)
    _, handle, title_text = os_env.get_active_window()
    if not handle:
        return
    window_type = get_window_type(title_text)
    info = WindowInfo(handle=handle, title=title_text, is_tab=True, window_type=window_type)
    alias_registry.set(window_alias, info)
    print(f"Set tab alias '{window_alias}' for: {title_text}")


def clear_alias() -> None:
    _, handle, title_text = os_env.get_active_window()
    if not handle:
        return
    removed_keys = alias_registry.remove_by_handle(handle)
    if removed_keys:
        for k in removed_keys:
            print(f"Cleared alias '{k}' for window: {title_text}")
    else:
        print(f"No alias found for current window: {title_text}")


def clear_all_aliases() -> None:
    alias_registry.clear()
    print("Cleared all window aliases.")


def find_tab(target_title: str, window_type: str) -> bool:
    _, __, initial_title = os_env.get_active_window()
    tries = 0
    while tries < 50:
        _, __, current_title = os_env.get_active_window()
        if target_title == current_title:
            return True
        if window_type == "ctrl_tab":
            Key("c-tab").execute()
        elif window_type == "ctrl_pgdn":
            Key("c-pgdown").execute()
        time.sleep(0.1)
        tries += 1
        if tries > 1 and current_title == initial_title:
            break
    return False


def show_window_info():
    print("\n--- Open Windows Info ---")
    windows = os_env.get_open_windows()
    for hwnd, title_text in windows:
        print(f"HWND: {hwnd:<8} | App: {extract_app_name(title_text):<20} | Title: {title_text}")


def switch_to_app(app_name, instance: int = 1) -> bool:
    """Switches to app using a verified robust Win32 approach with fallback."""
    if isinstance(app_name, (list, tuple)):
        app_names_lc = [a.lower() for a in app_name]
        app_name_display = "/".join(app_name)
    else:
        app_names_lc = [app_name.lower()]
        app_name_display = app_name

    # Find matching window in workspace
    current_desktop_id = os_env.get_current_desktop_id()
    windows = os_env.get_open_windows()
    matching_windows = []

    for hwnd, title_text in windows:
        if extract_app_name(title_text).lower() in app_names_lc:
            _log("DEBUG", f"App matched for '{title_text}' (HWND {hwnd}). Checking desktop ID...")
            if current_desktop_id:
                win_desktop_id = os_env.get_window_desktop_id(hwnd)
                if win_desktop_id == current_desktop_id or win_desktop_id is None:
                    _log("DEBUG", f"Window HWND {hwnd} is on current desktop.")
                    matching_windows.append((hwnd, title_text))
            else:
                matching_windows.append((hwnd, title_text))

    if not matching_windows:
        print(f"No windows found for '{app_name_display}'.")
        printer.out("Failed to switch window")
        return False

    if instance < 1 or instance > len(matching_windows):
        print(f"App '{app_name_display}' only has {len(matching_windows)} instances; requested #{instance}.")
        printer.out("Failed to switch window")
        return False

    target_hwnd, target_title = matching_windows[instance - 1]

    _log("INFO", f"Request to switch_to_app: '{app_name_display}', instance #{instance} (HWND {target_hwnd})")
    if os_env.restore_and_focus(target_hwnd, app_name=app_name, instance=instance):
        _log("INFO", f"Successfully focused '{target_title}'")
        printer.out(f"Successfully switched to '{target_title}' using window focus APIs")
        return True

    _log("ERROR", f"Failed to focus '{app_name_display}' for HWND {target_hwnd}.")
    printer.out("Failed to switch window")
    return False


def title(window_title: str):
    """Activate a window whose title contains the given substring."""
    try:
        windows = os_env.get_open_windows()
        for handle, win_title in windows:
            if window_title.lower() in win_title.lower():
                if os_env.restore_and_focus(handle):
                    printer.out(f"Successfully switched to window matching '{window_title}' using window focus APIs")
                    return
        printer.out("Failed to switch window")
    except Exception as e:
        _log("ERROR", f"Error activating by title: {e}")
        printer.out("Failed to switch window")


def switch_to_alias(window_alias: Any) -> None:
    window_alias = str(window_alias)
    info = alias_registry.get(window_alias)
    if not info:
        printer.out(f"No alias found for '{window_alias}'")
        return

    try:
        _log("INFO", f"Request to switch_to_alias: '{window_alias}' (HWND {info.handle})")

        # Check if handle is still alive
        if not win32gui.IsWindow(info.handle):
            raise ElementNotFoundError

        # Failsafe for alias
        if os_env.restore_and_focus(info.handle):
            _log("INFO", f"switch_to_alias '{window_alias}' focus completed successfully.")
            printer.out(f"Successfully switched to alias '{window_alias}' ('{info.title}') using window focus APIs")
        else:
            app_name = extract_app_name(info.title)
            _log(
                "WARN",
                f"switch_to_alias '{window_alias}' direct focus failed. Falling back to switch_to_app for {app_name}",
            )
            if not switch_to_app(app_name):
                raise ElementNotFoundError

        time.sleep(0.05)
        if info.is_tab and info.window_type:
            find_tab(info.title, info.window_type)

    except ElementNotFoundError:
        printer.out(f"Window for alias '{window_alias}' not found, dropping alias.")
        alias_registry.remove(window_alias)
    except Exception as e:
        _log("ERROR", f"Error switching to alias '{window_alias}': {e}")
        printer.out("Failed to switch window")


if __name__ == "__main__":
    show_window_info()
