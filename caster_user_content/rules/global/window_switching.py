from dragonfly import MappingRule, Function, List, ListRef, ShortIntegerRef, Choice, Pause, Mouse
from castervoice.lib.actions import Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content.util import app_switcher
from caster_user_content.environment_variables import WINDOW_ALIASES, WINDOWS_APP_ALIASES

def list_aliases():
    """Print all current aliases"""
    print("\nCurrent Aliases:")
    for alias, info in app_switcher.aliases.items():
        alias_type = "Tab" if info.is_tab else "Window"
        print(f"{alias}: {alias_type} - {info.title}")

class WindowSwitchingRule(MappingRule):
    pronunciation = "window switching"
    
    mapping = {
        # Setting commands
        "set window <window_alias>": R(Function(app_switcher.set_window)),
        "set page <window_alias>": R(Function(app_switcher.set_page)),
        
        # Utility command
        "list aliases": R(Function(list_aliases)),

        "show app info": R(Function(app_switcher.show_window_info)),
    }

    extras = [
        Choice("window_alias", {a: a for a in WINDOW_ALIASES}),
    ]

def get_rule():
    details = RuleDetails(name="Window Switching")
    return WindowSwitchingRule, details