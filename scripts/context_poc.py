#!/usr/bin/env python3
"""
Active Desktop Context Engine (ADCE) - Python Proof of Concept (v2.1)
Monitors Windows OS foreground and focus events in real-time, extracting
window state, active/open tabs (VS Code, Waterfox, Firefox, Chrome, Edge),
and the focused UI element hierarchy.
"""

import sys
import os
import time
import ctypes
from ctypes import wintypes
import uiautomation as auto

# Win32 Constants
EVENT_SYSTEM_FOREGROUND = 0x0003
EVENT_OBJECT_FOCUS = 0x8005
WINEVENT_OUTOFCONTEXT = 0x0000
WINEVENT_SKIPOWNPROCESS = 0x0002

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32

WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.HWND,
    wintypes.LONG,
    wintypes.LONG,
    wintypes.DWORD,
    wintypes.DWORD,
)

# Debounce state
last_event_time = 0
DEBOUNCE_INTERVAL = 0.05  # 50ms debouncing window


def clear_terminal():
    """Clear terminal cleanly using ANSI escape codes."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def get_top_level_window(ctrl):
    """Walk up from any control to find the true top-level application window."""
    if not ctrl:
        return None
    try:
        root = auto.GetRootControl()
        curr = ctrl
        top = curr
        while curr:
            parent = curr.GetParentControl()
            if not parent or parent == root:
                top = curr
                break
            if curr.ControlType == auto.ControlType.WindowControl and (not parent or parent == root):
                top = curr
                break
            curr = parent
            top = curr
        return top
    except Exception:
        return ctrl


def get_element_hierarchy(element, max_depth=5):
    """Walk up the parent chain to construct the hierarchy path."""
    hierarchy = []
    curr = element
    depth = 0
    while curr and depth < max_depth:
        name = curr.Name or ""
        c_type = curr.ControlTypeName or "Element"
        if len(name) > 35:
            name = name[:32] + "..."
        display_str = f"[{c_type}] {name}".strip()
        hierarchy.append(display_str)
        try:
            curr = curr.GetParentControl()
        except Exception:
            break
        depth += 1
    hierarchy.reverse()
    return hierarchy


def extract_window_tabs(top_window, focused_element=None, max_depth=14):
    """
    Search the top-level application window for open tabs across VS Code,
    Waterfox, Firefox, Chrome, Edge, Windows Terminal, and Notepad.
    """
    tabs = []
    if not top_window:
        return tabs

    found_tab_items = []
    seen_names = set()

    try:
        # Traverse top window hierarchy up to max_depth
        for ctrl, depth in auto.WalkControl(top_window, includeTop=False, maxDepth=max_depth):
            try:
                ctype = ctrl.ControlTypeName or ""
                auto_id = ctrl.AutomationId or ""
                cname = (ctrl.Name or "").strip()

                # Fast check for TabItem controls or tab-like elements
                is_tab = False
                if ctrl.ControlType == auto.ControlType.TabItemControl or ctype in ("TabItemControl", "TabItem"):
                    is_tab = True
                elif "tab" in auto_id.lower() and ctype in ("ListItemControl", "ButtonControl", "CustomControl"):
                    is_tab = True
                elif "tab" in cname.lower() and ctype == "TabItemControl":
                    is_tab = True

                if is_tab:
                    is_selected = False

                    # Check SelectionItemPattern
                    try:
                        sel = ctrl.GetSelectionItemPattern()
                        if sel:
                            is_selected = bool(sel.IsSelected)
                    except Exception:
                        pass

                    # Check Legacy Accessible State (STATE_SYSTEM_SELECTED = 0x4)
                    if not is_selected:
                        try:
                            legacy = ctrl.GetLegacyIAccessiblePattern()
                            if legacy and (legacy.State & 0x00000004):
                                is_selected = True
                        except Exception:
                            pass

                    # Check HasKeyboardFocus
                    if not is_selected:
                        try:
                            if ctrl.HasKeyboardFocus:
                                is_selected = True
                        except Exception:
                            pass

                    display_name = cname if cname else "(Untitled Tab)"

                    # Clean up VS Code tab name suffixes (e.g. ", Editor Group 1" or uncommitted dot indicator)
                    if ", Editor Group" in display_name:
                        display_name = display_name.split(", Editor Group")[0].strip()
                    if display_name.startswith("● "):
                        display_name = display_name[2:].strip()

                    # Deduplicate adjacent duplicate accessibility nodes for same tab
                    key = (display_name, ctrl.BoundingRectangle.left if ctrl.BoundingRectangle else 0)
                    if key not in seen_names:
                        seen_names.add(key)
                        if len(display_name) > 55:
                            display_name = display_name[:52] + "..."
                        found_tab_items.append({"name": display_name, "selected": is_selected, "control": ctrl})

            except Exception:
                continue

    except Exception:
        pass

    # Fallback heuristic: If no tab was marked as selected by UIA patterns,
    # match against focused element or window title
    if found_tab_items and not any(t["selected"] for t in found_tab_items):
        matched = False
        if focused_element:
            f_name = (focused_element.Name or "").strip()
            for t in found_tab_items:
                if t["name"] and (t["name"] in f_name or f_name in t["name"]):
                    t["selected"] = True
                    matched = True
                    break
        if not matched and top_window:
            w_name = (top_window.Name or "").strip()
            for t in found_tab_items:
                if t["name"] and (t["name"] in w_name or w_name in t["name"]):
                    t["selected"] = True
                    matched = True
                    break
        if not matched:
            found_tab_items[0]["selected"] = True

    return found_tab_items


def capture_and_display_context(event_type_name="FOCUS_CHANGE"):
    """Capture focused control context, window tabs, and print the updated live state."""
    try:
        focused = auto.GetFocusedControl()
        if not focused:
            focused = auto.GetForegroundControl()
        if not focused:
            return

        # Resolve the true top-level application window
        top_window = get_top_level_window(focused)
        if not top_window:
            top_window = auto.GetForegroundControl()

        app_name = top_window.Name if top_window else "Unknown Window"
        process_id = top_window.ProcessId if top_window else 0

        # Extract focused element properties
        control_type = focused.ControlTypeName or "UnknownControl"
        element_name = focused.Name or "(No Name)"
        automation_id = focused.AutomationId or ""
        bounding_rect = focused.BoundingRectangle

        # Extract value / text snippet if available
        value_text = ""
        try:
            val_pattern = focused.GetValuePattern()
            if val_pattern:
                value_text = val_pattern.Value
        except Exception:
            pass

        if not value_text:
            try:
                txt_pattern = focused.GetTextPattern()
                if txt_pattern:
                    value_text = txt_pattern.DocumentRange.GetText(100)
            except Exception:
                pass

        # Extract tabs and control hierarchy
        tabs = extract_window_tabs(top_window, focused_element=focused)
        hierarchy = get_element_hierarchy(focused)

        # Clear and render the live view
        clear_terminal()
        print("=" * 76)
        print("  ACTIVE DESKTOP CONTEXT ENGINE (ADCE) - LIVE MONITOR (v2.1)")
        print("=" * 76)
        print(f" Timestamp    : {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" Event Trigger: {event_type_name}")
        print(f" Active App   : {app_name} (PID: {process_id})")
        print("-" * 76)

        # 1. TABS SECTION
        print(" WINDOW TABS:")
        if tabs:
            for idx, tab in enumerate(tabs, 1):
                if tab["selected"]:
                    status = "► [ACTIVE] "
                    tab_str = f"\033[1;32m{status}Tab {idx}: {tab['name']}\033[0m"
                else:
                    status = "  [      ] "
                    tab_str = f"{status}Tab {idx}: {tab['name']}"
                print(f"  {tab_str}")
        else:
            print("  (No tabs detected in current window)")

        print("-" * 76)

        # 2. HIERARCHY TREE SECTION
        print(" ACTIVE CONTROL HIERARCHY TREE:")
        for idx, node in enumerate(hierarchy):
            is_last = idx == len(hierarchy) - 1
            prefix = "  " * idx + ("└── " if idx > 0 else "┌── ")
            if is_last:
                print(f"  {prefix}\033[1;36m{node}  ◄ [FOCUSED NODE]\033[0m")
            else:
                print(f"  {prefix}{node}")

        print("-" * 76)

        # 3. FOCUSED DETAILS SECTION
        print(" FOCUSED ELEMENT DETAILS:")
        print(f"  • Control Type  : {control_type}")
        print(f"  • Element Name  : {element_name}")
        if automation_id:
            print(f"  • Automation ID : {automation_id}")
        if bounding_rect:
            print(
                f"  • Bounding Box  : (Left={bounding_rect.left}, Top={bounding_rect.top}, Width={bounding_rect.width()}, Height={bounding_rect.height()})"
            )
        if value_text:
            snippet = value_text.replace("\n", " ").strip()
            if len(snippet) > 80:
                snippet = snippet[:77] + "..."
            print(f'  • Value Snippet : "{snippet}"')
        print("=" * 76)
        print("\n [Listening for OS events... Press Ctrl+C in this terminal to exit]")
        sys.stdout.flush()

    except Exception:
        # Ignore transient COM disconnection errors during rapid UI transitions
        pass


def win_event_handler(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
    global last_event_time
    now = time.time()
    if now - last_event_time < DEBOUNCE_INTERVAL:
        return
    last_event_time = now

    event_name = "WINDOW_SWITCH" if event == EVENT_SYSTEM_FOREGROUND else "FOCUS_CHANGED"
    capture_and_display_context(event_name)


def main():
    # Set console title
    os.system("title ADCE Live Context Monitor")

    # Initialize COM in Multi-Threaded Apartment (MTA)
    ole32.CoInitializeEx(None, 0x0)  # COINIT_MULTITHREADED = 0x0

    print("Initializing Active Desktop Context Engine...")
    print("Registering Windows Event Hooks (EVENT_SYSTEM_FOREGROUND, EVENT_OBJECT_FOCUS)...")

    # Hook Window Switching & Focus Changes
    proc = WinEventProcType(win_event_handler)

    hook_foreground = user32.SetWinEventHook(
        EVENT_SYSTEM_FOREGROUND,
        EVENT_SYSTEM_FOREGROUND,
        0,
        proc,
        0,
        0,
        WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS,
    )

    hook_focus = user32.SetWinEventHook(
        EVENT_OBJECT_FOCUS,
        EVENT_OBJECT_FOCUS,
        0,
        proc,
        0,
        0,
        WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS,
    )

    if not hook_foreground or not hook_focus:
        print("Error: Failed to register WinEvent hooks.")
        sys.exit(1)

    # Initial capture on launch
    capture_and_display_context("INITIAL_CAPTURE")

    # Native Windows Message Pump to keep hooks alive without busy-spinning (0% CPU)
    msg = wintypes.MSG()
    try:
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    except KeyboardInterrupt:
        pass
    finally:
        user32.UnhookWinEvent(hook_foreground)
        user32.UnhookWinEvent(hook_focus)
        ole32.CoUninitialize()
        print("\nContext Engine shut down cleanly.")


if __name__ == "__main__":
    main()
