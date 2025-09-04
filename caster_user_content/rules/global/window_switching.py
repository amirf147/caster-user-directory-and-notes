from dragonfly import MappingRule, Function, List, ListRef, ShortIntegerRef, Choice
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content.util import switch_application, taskbar
from caster_user_content import environment_variables as ev


# Create a Dragonfly List for aliases
window_aliases = List("window_alias")
window_aliases.set(ev.WINDOW_ALIASES)

def list_aliases():
    """Print all current aliases"""
    print("\nCurrent Aliases:")
    for alias, info in switch_application.aliases.items():
        alias_type = "Tab" if info.is_tab else "Window"
        print(f"{alias}: {alias_type} - {info.title}")

def _switch_to_app(app_name, instance):
    taskbar.activate_taskbar_instance(app_name, instance)


class WindowSwitchingRule(MappingRule):
    pronunciation = "window switching"
    
    mapping = {
        # Setting commands
        "set window <window_alias>": R(Function(switch_application.set_window)),
        "set page <window_alias>": R(Function(switch_application.set_page)),
        
        # Utility command
        "list aliases": R(Function(list_aliases)),

        "show taskbar info": R(Function(lambda: taskbar.show_taskbar_info(taskbar.get_taskbar_items()))),
        "<app_name> [<instance>]": R(Function(_switch_to_app)),
    }

    extras = [
        ListRef("window_alias", window_aliases),
        ShortIntegerRef("instance", 1, 10),
        Choice("app_name", ev.WINDOWS_APP_ALIASES),
    ]
    defaults = {
        "instance": 1,
    }

def get_rule():
    details = RuleDetails(name="Window Switching")
    return WindowSwitchingRule, details