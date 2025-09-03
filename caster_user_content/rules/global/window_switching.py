from __future__ import annotations # for type hints of types that haven't been defined yet

from dragonfly import MappingRule, Function, List, ListRef, Mouse
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content.util import switch_application
from caster_user_content import environment_variables as ev


# Create a Dragonfly List for aliases
window_aliases = List("window_alias")
window_aliases.set(ev.WINDOW_ALIASES)

def _get_taskbar_info() -> list:
    from pywinauto import Desktop
    return [btn for i, btn in enumerate(Desktop(backend="uia").window(class_name="Shell_TrayWnd")\
        .children(control_type="ToolBar")[0].children(control_type="Button"))]

def _create_Taskbar() -> Taskbar: # TODO: implement this
    pass

def _show_taskbar_info():
    for i, btn in enumerate(_get_taskbar_info()):
        print(f"\n--- Button {i+1} ---")
        print("Text:", btn.window_text())
        print("Class:", btn.class_name())
        print("Rectangle:", btn.rectangle())
        print("Enabled:", btn.is_enabled())
        print("Visible:", btn.is_visible())
        print("Properties:")
        for k, v in btn.get_properties().items():
            print(f"  {k}: {v}")

def list_aliases():
    """Print all current aliases"""
    print("\nCurrent Aliases:")
    for alias, info in switch_application.aliases.items():
        alias_type = "Tab" if info.is_tab else "Window"
        print(f"{alias}: {alias_type} - {info.title}")

class WindowSwitchingRule(MappingRule):
    pronunciation = "window switching"
    
    mapping = {
        # Setting commands
        "set window <window_alias>": R(Function(switch_application.set_window)),
        "set page <window_alias>": R(Function(switch_application.set_page)),
        
        # Utility command
        "list aliases": R(Function(list_aliases)),

        "show taskbar info": R(Function(_show_taskbar_info)),
    }

    extras = [
        ListRef("window_alias", window_aliases),
    ]

def get_rule():
    details = RuleDetails(name="Window Switching")
    return WindowSwitchingRule, details