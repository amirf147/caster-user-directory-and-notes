#!/usr/bin/env python3
"""
Active Desktop Context Engine (ADCE) - Python Proof of Concept
Monitors Windows OS foreground and focus events in real-time, extracting
and formatting the active UI state into a live terminal tree.
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


def get_element_hierarchy(element, max_depth=4):
    """Walk up the parent chain to construct the hierarchy path."""
    hierarchy = []
    curr = element
    depth = 0
    while curr and depth < max_depth:
        name = curr.Name or ""
        c_type = curr.ControlTypeName or "Element"
        if len(name) > 30:
            name = name[:27] + "..."
        display_str = f"[{c_type}] {name}".strip()
        hierarchy.append(display_str)
        try:
            curr = curr.GetParentControl()
        except Exception:
            break
        depth += 1
    hierarchy.reverse()
    return hierarchy


def capture_and_display_context(event_type_name="FOCUS_CHANGE"):
    """Capture focused control context and print the updated live state tree."""
    try:
        focused = auto.GetFocusedControl()
        if not focused:
            focused = auto.GetForegroundControl()
        if not focused:
            return

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

        hierarchy = get_element_hierarchy(focused)

        # Clear and render the live view
        clear_terminal()
        print("=" * 70)
        print("  ACTIVE DESKTOP CONTEXT ENGINE (ADCE) - LIVE MONITOR")
        print("=" * 70)
        print(f" Timestamp    : {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" Event Trigger: {event_type_name}")
        print(f" Active App   : {app_name} (PID: {process_id})")
        print("-" * 70)
        print(" HIERARCHY TREE:")
        for idx, node in enumerate(hierarchy):
            indent = "  " * idx + ("└── " if idx > 0 else "┌── ")
            print(f"  {indent}{node}")

        print("-" * 70)
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
        print("=" * 70)
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
