from dragonfly import MappingRule, Function, List, ListRef, ShortIntegerRef, Choice, Pause, Mouse
from castervoice.lib.actions import Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content.util import switch_application, taskbar
from caster_user_content.environment_variables import WINDOW_ALIASES, WINDOWS_APP_ALIASES

# Import the shared window_aliases from the package
# from . import window_aliases

# def list_aliases():
#     """Print all current aliases"""
#     print("\nCurrent Aliases:")
#     for alias, info in switch_application.aliases.items():
#         alias_type = "Tab" if info.is_tab else "Window"
#         print(f"{alias}: {alias_type} - {info.title}")

class WindowSwitchingRule(MappingRule):
    pronunciation = "window switching"
    
    mapping = {
        # # Setting commands
        # "set window <window_alias>": R(Function(switch_application.set_window)),
        # "set page <window_alias>": R(Function(switch_application.set_page)),
        
        # # Utility command
        # "list aliases": R(Function(list_aliases)),

        "show taskbar info": R(Function(lambda: taskbar.show_taskbar_info(taskbar.get_taskbar_items()))),
    }

    extras = [
        # ListRef("window_alias", window_aliases),
    ]

def get_rule():
    details = RuleDetails(name="Window Switching")
    return WindowSwitchingRule, details