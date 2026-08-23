#!/usr/bin/env python3
"""
Active Desktop Context Engine (ADCE) - Python Proof of Concept (v2.3)
Monitors Windows OS foreground and focus events in real-time, extracting
window state, active/open tabs (VS Code, Antigravity, Waterfox, Firefox, Chrome, Edge, Explorer),
focused UI element hierarchy, and high-fidelity microsecond execution telemetry.

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

import sys
import os
import time
import json
import ctypes
from ctypes import wintypes
import uiautomation as auto

# Win32 Constants
EVENT_SYSTEM_FOREGROUND = 0x0003
EVENT_OBJECT_FOCUS = 0x8005
WINEVENT_OUTOFCONTEXT = 0x0000
WINEVENT_SKIPOWNPROCESS = 0x0002
GA_ROOT = 2
STD_INPUT_HANDLE = -10
ENABLE_QUICK_EDIT_MODE = 0x0040
ENABLE_EXTENDED_FLAGS = 0x0080

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32
kernel32 = ctypes.windll.kernel32

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

# Log file configuration
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
LOG_FILE = os.path.join(LOG_DIR, "adce_telemetry.jsonl")


def disable_quick_edit_mode():
    """Disable Windows Console QuickEdit mode to prevent click-to-pause terminal freezes."""
    try:
        h_stdin = kernel32.GetStdHandle(STD_INPUT_HANDLE)
        if h_stdin and h_stdin != -1:
            mode = wintypes.DWORD()
            if kernel32.GetConsoleMode(h_stdin, ctypes.byref(mode)):
                new_mode = (mode.value & ~ENABLE_QUICK_EDIT_MODE) | ENABLE_EXTENDED_FLAGS
                kernel32.SetConsoleMode(h_stdin, new_mode)
                return True
    except Exception:
        pass
    return False


def get_hwnd_class_name(hwnd):
    """Retrieve the Win32 window class name for a given HWND."""
    if not hwnd:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buf, 256)
        return buf.value
    except Exception:
        return ""


def clear_terminal():
    """Clear terminal cleanly using ANSI escape codes."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def get_top_level_window_info(ctrl):
    """
    Resolve the true top-level application window HWND, class name, and UIA control.
    Anchors to Win32 GA_ROOT or GetForegroundWindow to prevent container scope bleed.
    """
    hwnd = 0
    top_ctrl = None
    class_name = ""

    # Attempt 1: From control's NativeWindowHandle
    if ctrl:
        try:
            native_hwnd = ctrl.NativeWindowHandle
            if native_hwnd:
                root_hwnd = user32.GetAncestor(native_hwnd, GA_ROOT)
                hwnd = root_hwnd if root_hwnd else native_hwnd
        except Exception:
            pass

    # Attempt 2: Fallback to active foreground window
    if not hwnd:
        try:
            fg_hwnd = user32.GetForegroundWindow()
            if fg_hwnd:
                root_hwnd = user32.GetAncestor(fg_hwnd, GA_ROOT)
                hwnd = root_hwnd if root_hwnd else fg_hwnd
        except Exception:
            pass

    if hwnd:
        class_name = get_hwnd_class_name(hwnd)
        try:
            top_ctrl = auto.ControlFromHandle(hwnd)
        except Exception:
            pass

    # Fallback to climbing UIA parent tree if Handle binding failed
    if not top_ctrl and ctrl:
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
            top_ctrl = top
            if not hwnd and top_ctrl:
                hwnd = top_ctrl.NativeWindowHandle
                class_name = get_hwnd_class_name(hwnd)
        except Exception:
            top_ctrl = ctrl

    return top_ctrl, hwnd, class_name


def get_element_hierarchy(element, max_depth=5):
    """Walk up the parent chain from the focused element to construct the hierarchy path."""
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


def walk_control_pruned(
    control,
    include_top=False,
    max_depth=14,
    prune_control_types=(auto.ControlType.DocumentControl,),
):
    """
    Depth-first UI tree traversal with subtree pruning capability.
    Skips descending into expensive subtrees (e.g. DocumentControl in browsers)
    while continuing traversal of sibling chrome, toolbars, and tabstrips.
    """
    if include_top:
        yield control, 0
    if max_depth <= 0:
        return
    depth = 0
    child = control.GetFirstChildControl()
    control_list = [child]
    while depth >= 0:
        last_control = control_list[-1]
        if last_control:
            yield last_control, depth + 1
            child = last_control.GetNextSiblingControl()
            control_list[depth] = child

            should_prune = False
            if prune_control_types:
                try:
                    if last_control.ControlType in prune_control_types:
                        should_prune = True
                except Exception:
                    pass

            if not should_prune and depth + 1 < max_depth:
                child = last_control.GetFirstChildControl()
                if child:
                    depth += 1
                    control_list.append(child)
        else:
            del control_list[depth]
            depth -= 1


def extract_electron_tabs_bottom_up(focused_element, max_ancestor_depth=8):
    """
    Bottom-up tab discovery for Electron / VS Code / Antigravity IDE.
    Climbs upward from the active editor/control to locate the editor group container,
    then inspects the title/tabstrip header container directly.
    """
    found_tabs = []
    if not focused_element:
        return found_tabs

    curr = focused_element
    ancestor_count = 0
    seen_names = set()

    while curr and ancestor_count < max_ancestor_depth:
        try:
            parent = curr.GetParentControl()
            if not parent:
                break

            # Check siblings of ancestors for tab containers
            # In Monaco/VS Code, the tab bar is a sibling of the editor body within the editor group
            for sibling in parent.GetChildren():
                auto_id = (sibling.AutomationId or "").lower()

                if (
                    "tab" in auto_id
                    or "title" in auto_id
                    or "tabs-container" in auto_id
                    or "tabs" in auto_id
                    or "editor-group-header" in auto_id
                ):
                    for item in sibling.GetChildren():
                        iname = (item.Name or "").strip()
                        ictype = item.ControlTypeName or ""
                        iauto = (item.AutomationId or "").lower()

                        if iname and (
                            ictype in ("TabItemControl", "ListItemControl", "CustomControl", "ButtonControl")
                            or "tab" in iauto
                        ):
                            is_selected = False
                            try:
                                sel = item.GetSelectionItemPattern()
                                if sel and sel.IsSelected:
                                    is_selected = True
                            except Exception:
                                pass
                            if not is_selected:
                                try:
                                    legacy = item.GetLegacyIAccessiblePattern()
                                    if legacy and (legacy.State & 0x00000004):
                                        is_selected = True
                                except Exception:
                                    pass

                            display_name = iname
                            if ", Editor Group" in display_name:
                                display_name = display_name.split(", Editor Group")[0].strip()
                            if display_name.startswith("● "):
                                display_name = display_name[2:].strip()

                            if display_name not in seen_names:
                                seen_names.add(display_name)
                                found_tabs.append({"name": display_name, "selected": is_selected, "control": item})

            if found_tabs:
                break

            curr = parent
            ancestor_count += 1
        except Exception:
            break

    return found_tabs


def extract_window_tabs(top_window, focused_element=None, max_depth=14, hwnd_class=""):
    """
    Search the application window for open tabs across VS Code, Antigravity,
    Waterfox, Firefox, Chrome, Edge, Windows Terminal, and File Explorer.
    Collects traversal statistics (nodes scanned, max depth reached).
    Utilizes subtree pruning (skipping DocumentControl bodies in browsers)
    and bottom-up sibling lookup in Electron/Monaco editors.
    """
    tabs = []
    traversal_stats = {
        "nodes_scanned": 0,
        "max_depth_reached": 0,
        "tab_containers_found": 0,
    }
    if not top_window:
        return tabs, traversal_stats

    found_tab_items = []
    seen_names = set()
    is_explorer = hwnd_class in ("CabinetWClass", "ExplorerBrowserControl")
    is_electron = "Chrome_WidgetWin" in hwnd_class

    # Subtree pruning: In browsers, prune DocumentControl to avoid crawling thousands of web DOM nodes
    prune_types = (auto.ControlType.DocumentControl,) if ("Mozilla" in hwnd_class or is_electron) else ()

    try:
        for ctrl, depth in walk_control_pruned(
            top_window, include_top=False, max_depth=max_depth, prune_control_types=prune_types
        ):
            traversal_stats["nodes_scanned"] += 1
            if depth > traversal_stats["max_depth_reached"]:
                traversal_stats["max_depth_reached"] = depth

            try:
                ctype = ctrl.ControlTypeName or ""
                auto_id = ctrl.AutomationId or ""
                cname = (ctrl.Name or "").strip()

                is_tab = False

                # 1. Native TabItem Controls
                if ctrl.ControlType == auto.ControlType.TabItemControl or ctype in ("TabItemControl", "TabItem"):
                    is_tab = True
                # 2. Electron / VS Code / Antigravity editor tab containers
                elif (
                    is_electron
                    and ("editor" in auto_id.lower() or "tab" in auto_id.lower())
                    and ctype in ("TabItemControl", "ListItemControl", "CustomControl", "ButtonControl")
                ):
                    is_tab = True
                # 3. Generic tab-like controls (excluding File Explorer navigation shortcuts)
                elif (
                    not is_explorer
                    and "tab" in auto_id.lower()
                    and ctype in ("ListItemControl", "ButtonControl", "CustomControl")
                ):
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

                    # Clean up VS Code tab name suffixes and indicators
                    if ", Editor Group" in display_name:
                        display_name = display_name.split(", Editor Group")[0].strip()
                    if display_name.startswith("● "):
                        display_name = display_name[2:].strip()

                    # Deduplicate adjacent duplicate accessibility nodes
                    rect_left = ctrl.BoundingRectangle.left if ctrl.BoundingRectangle else 0
                    key = (display_name, rect_left)
                    if key not in seen_names:
                        seen_names.add(key)
                        if len(display_name) > 55:
                            display_name = display_name[:52] + "..."
                        found_tab_items.append({"name": display_name, "selected": is_selected, "control": ctrl})

            except Exception:
                continue

    except Exception:
        pass

    # Fast-path / Fallback for Electron / Monaco: If top-down walk missed tabs, use bottom-up search
    if is_electron and not found_tab_items and focused_element:
        bottom_up_tabs = extract_electron_tabs_bottom_up(focused_element)
        if bottom_up_tabs:
            found_tab_items.extend(bottom_up_tabs)

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

    return found_tab_items, traversal_stats


def log_telemetry_event(event_data):
    """Append structured JSONL record to data log file."""
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_data, ensure_ascii=False) + "\n")
    except Exception:
        pass


def capture_and_display_context(event_type_name="FOCUS_CHANGE"):
    """Capture focused context, compute timing breakdown, and render live telemetry view."""
    t_start = time.perf_counter()

    try:
        focused = auto.GetFocusedControl()
        if not focused:
            focused = auto.GetForegroundControl()
        if not focused:
            return

        # 1. Resolve Top-Level Application Window & HWND
        top_window, hwnd, hwnd_class = get_top_level_window_info(focused)
        t_hwnd = time.perf_counter()
        hwnd_ms = (t_hwnd - t_start) * 1000

        app_name = top_window.Name if top_window else "Unknown Window"
        process_id = top_window.ProcessId if top_window else 0
        hwnd_hex = f"0x{hwnd:08X}" if hwnd else "0x00000000"

        # 2. Extract Focused Element Properties
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

        # 3. Extract Tabs with Traversal Diagnostics
        tabs, traversal_stats = extract_window_tabs(
            top_window, focused_element=focused, max_depth=14, hwnd_class=hwnd_class
        )
        t_tabs = time.perf_counter()
        tab_discovery_ms = (t_tabs - t_hwnd) * 1000

        # 4. Extract Control Hierarchy
        hierarchy = get_element_hierarchy(focused)
        t_hierarchy = time.perf_counter()
        hierarchy_ms = (t_hierarchy - t_tabs) * 1000

        # 5. Render Live ANSI Monitor
        clear_terminal()
        total_pipeline_ms = (time.perf_counter() - t_start) * 1000

        print("=" * 78)
        print("  ACTIVE DESKTOP CONTEXT ENGINE (ADCE) - LIVE MONITOR (v2.3)")
        print("=" * 78)
        print(f" Timestamp     : {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" Event Trigger : {event_type_name}")
        print(f" Active App    : {app_name} (PID: {process_id})")
        print(f" HWND / Class  : {hwnd_hex} | Class: {hwnd_class or '(Unknown)'}")
        print(
            f" Latency       : Total: \033[1;33m{total_pipeline_ms:.1f}ms\033[0m "
            f"(HWND: {hwnd_ms:.1f}ms | Tabs: {tab_discovery_ms:.1f}ms | Tree: {hierarchy_ms:.1f}ms)"
        )
        print(
            f" Traversal     : Scanned: \033[1;36m{traversal_stats['nodes_scanned']}\033[0m nodes | "
            f"Max Depth: {traversal_stats['max_depth_reached']} | "
            f"Tabs Found: {len(tabs)}"
        )
        print("-" * 78)

        # A. TABS SECTION (With Bounded Pagination)
        print(" WINDOW TABS:")
        if tabs:
            max_display = 12
            for idx, tab in enumerate(tabs[:max_display], 1):
                if tab["selected"]:
                    status = "► [ACTIVE] "
                    tab_str = f"\033[1;32m{status}Tab {idx}: {tab['name']}\033[0m"
                else:
                    status = "  [      ] "
                    tab_str = f"{status}Tab {idx}: {tab['name']}"
                print(f"  {tab_str}")

            if len(tabs) > max_display:
                remaining = len(tabs) - max_display
                print(f"  \033[90m... (+{remaining} more tabs open)\033[0m")
        else:
            print("  (No tabs detected in current window)")

        print("-" * 78)

        # B. HIERARCHY TREE SECTION
        print(" ACTIVE CONTROL HIERARCHY TREE:")
        for idx, node in enumerate(hierarchy):
            is_last = idx == len(hierarchy) - 1
            prefix = "  " * idx + ("└── " if idx > 0 else "┌── ")
            if is_last:
                print(f"  {prefix}\033[1;36m{node}  ◄ [FOCUSED NODE]\033[0m")
            else:
                print(f"  {prefix}{node}")

        print("-" * 78)

        # C. FOCUSED DETAILS SECTION
        print(" FOCUSED ELEMENT DETAILS:")
        print(f"  • Control Type  : {control_type}")
        print(f"  • Element Name  : {element_name}")
        if automation_id:
            print(f"  • Automation ID : {automation_id}")
        if bounding_rect:
            print(
                f"  • Bounding Box  : (Left={bounding_rect.left}, Top={bounding_rect.top}, "
                f"Width={bounding_rect.width()}, Height={bounding_rect.height()})"
            )
        if value_text:
            snippet = value_text.replace("\n", " ").strip()
            if len(snippet) > 80:
                snippet = snippet[:77] + "..."
            print(f'  • Value Snippet : "{snippet}"')
        print("=" * 78)
        print("\n [Listening for OS events... QuickEdit disabled. Press Ctrl+C in terminal to exit]")
        sys.stdout.flush()

        # 6. Structured JSONL Log Output
        selected_tabs = [t["name"] for t in tabs if t.get("selected")]
        active_tab_str = selected_tabs[0] if selected_tabs else ""
        telemetry_record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "event_trigger": event_type_name,
            "active_app": app_name,
            "pid": process_id,
            "hwnd": hwnd_hex,
            "hwnd_class": hwnd_class,
            "latency_ms": {
                "hwnd_resolution": round(hwnd_ms, 2),
                "tab_discovery": round(tab_discovery_ms, 2),
                "hierarchy_walk": round(hierarchy_ms, 2),
                "total_pipeline": round(total_pipeline_ms, 2),
            },
            "traversal_stats": {
                "nodes_scanned": traversal_stats["nodes_scanned"],
                "max_depth_reached": traversal_stats["max_depth_reached"],
                "tabs_found": len(tabs),
            },
            "active_tab": active_tab_str,
            "focused_element": {
                "control_type": control_type,
                "name": element_name,
                "automation_id": automation_id,
            },
        }
        log_telemetry_event(telemetry_record)

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

    # Disable Windows Console QuickEdit mode
    quick_edit_disabled = disable_quick_edit_mode()

    # Initialize COM in Multi-Threaded Apartment (MTA)
    ole32.CoInitializeEx(None, 0x0)  # COINIT_MULTITHREADED = 0x0

    print("Initializing Active Desktop Context Engine (v2.2)...")
    if quick_edit_disabled:
        print(" [OK] Console QuickEdit mode disabled (click-to-pause protection active).")
    print(" [OK] Registering WinEvent Hooks (EVENT_SYSTEM_FOREGROUND, EVENT_OBJECT_FOCUS)...")
    print(f" [OK] Structured telemetry logging to: {LOG_FILE}")

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
