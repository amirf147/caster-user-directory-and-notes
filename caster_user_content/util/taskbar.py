#!/usr/bin/env python
# taskbar.py
# Written with GPT-5/o3/Microsoft copilot (smart mode)

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
import time
from caster_user_content.environment_variables import WINDOWS_APP_NAMES
from pywinauto import Desktop
from pywinauto.controls.uia_controls import ButtonWrapper

# --------------------------------------------------------------------------
# Helper: simplified "application name" extractor
# --------------------------------------------------------------------------
_SEPARATORS = (" - ", " – ", " — ")  # ASCII dash, en-dash, em-dash


def extract_app_name(caption: str) -> str:
    if not caption:
        return "<blank>"

    caption = caption.strip()

    # First, check for known app names
    for name in WINDOWS_APP_NAMES:
        if name.lower() in caption.lower():
            return name

    # Special case: Windows PowerShell
    if caption.lower().startswith("windows powershell"):
        return "Windows PowerShell"

    # Special case: Copilot
    if caption.lower().startswith("copilot"):
        return "Copilot"

    # Fallback: use separator logic
    for sep in _SEPARATORS:
        if sep in caption:
            parts = caption.split(sep)
            if len(parts) >= 2:
                return parts[1].strip()

    return caption

def extract_total_instances(caption: str) -> int:
    try:
        last_segment = caption.split(" - ")[-1]
        return int(last_segment.split()[0])
    except (IndexError, ValueError):
        return 1

@dataclass
class TaskbarItem:
    control        : ButtonWrapper
    text           : str
    class_name     : str
    rectangle      : Tuple[int, int, int, int]
    is_enabled     : bool
    is_visible     : bool
    properties     : Dict[str, Any]

    app_name       : str = ""
    instance_index : int = 0
    total_instances: int = 1

    def invoke(self):
        try:
            self.control.invoke()
        except Exception as e:
            print(f"Invoke failed for {self.text!r}: {e}")

    def label(self) -> str:
        if self.total_instances > 1:
            return f"{self.app_name} {self.instance_index}/{self.total_instances}"
        return self.app_name

# --------------------------------------------------------------------------
# low-level discovery
# --------------------------------------------------------------------------
def _get_taskbar_buttons() -> List[ButtonWrapper]:
    return (Desktop(backend="uia")
            .window(class_name="Shell_TrayWnd")
            .children(control_type="ToolBar")[0]
            .children(control_type="Button"))

# --------------------------------------------------------------------------
# build TaskbarItem list with grouping info
# --------------------------------------------------------------------------
def get_taskbar_items() -> List[TaskbarItem]:
    items: List[TaskbarItem] = []
    instance_tracker: Dict[str, int] = {}

    for btn in _get_taskbar_buttons():
        caption = btn.window_text()
        app     = extract_app_name(caption)
        total   = extract_total_instances(caption)
        count   = instance_tracker.get(app, 0) + 1
        instance_tracker[app] = count

        items.append(TaskbarItem(
            control         = btn,
            text            = caption,
            class_name      = btn.class_name(),
            rectangle       = btn.rectangle(),
            is_enabled      = btn.is_enabled(),
            is_visible      = btn.is_visible(),
            properties      = btn.get_properties(),
            app_name        = app,
            instance_index  = count,
            total_instances = total
        ))

    return items

# --------------------------------------------------------------------------
# convenience functions
# --------------------------------------------------------------------------
def show_taskbar_info(items: List[TaskbarItem]):
    for i, it in enumerate(items, start=1):
        print(f"\n--- Button {i} ({it.label()}) ---")
        print("App name  :", it.app_name)
        print("Instance  :", f"{it.instance_index}/{it.total_instances}")
        print("Text      :", it.text)
        print("Class     :", it.class_name)
        print("Rectangle :", it.rectangle)
        print("Enabled   :", it.is_enabled)
        print("Visible   :", it.is_visible)
        print("Properties:")
        for k, v in it.properties.items():
            print(f"  {k}: {v}")

def cycle_taskbar_items(items: List[TaskbarItem], pause: float = 2.0):
    print("\nCycling through task-bar items:")
    for it in items:
        print(f"Activating {it.label()}  ({it.text or '[No title]'})")
        it.invoke()
        time.sleep(pause)

def activate_taskbar_instance(app_name: str, instance: int = 1) -> bool:
    app_name_lc = app_name.lower()
    items = [it for it in get_taskbar_items()
             if it.app_name.lower() == app_name_lc]

    if not items:
        print(f"No task-bar buttons found for application '{app_name}'.")
        return False

    if instance < 1 or instance > len(items):
        print(f"Application '{app_name}' only has {len(items)} "
              f"instance(s); requested #{instance}.")
        return False

    items.sort(key=lambda it: it.instance_index)
    target = items[instance - 1]
    print(f"Invoking {target.label()}  ({target.text or '[No title]'})")
    target.invoke()
    return True

# --------------------------------------------------------------------------
# demo / CLI
# --------------------------------------------------------------------------
if __name__ == "__main__":
    tbl_items = get_taskbar_items()
    if not tbl_items:
        print("No task-bar buttons found.")
    else:
        print(f"Found {len(tbl_items)} buttons across "
              f"{len(set(it.app_name for it in tbl_items))} applications.")
        show_taskbar_info(tbl_items)
        activate_taskbar_instance("Windsurf", instance=2)
    print("\nDone.")