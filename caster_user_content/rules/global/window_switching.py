from dragonfly import MappingRule, Function, List, ListRef, Mouse
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content.util import switch_application
from caster_user_content import environment_variables as ev


# Create a Dragonfly List for aliases
window_aliases = List("window_alias")
# Merge aliases from environment, defaults, and saved runtime aliases
_merged_aliases = set(getattr(ev, "WINDOW_ALIASES", []))
_merged_aliases.update(switch_application.get_default_aliases().keys())
_merged_aliases.update(switch_application.aliases.keys())
window_aliases.set(list(_merged_aliases))

def refresh_aliases():
    """Rebuild the window_aliases Dragonfly list at runtime."""
    merged = set(getattr(ev, "WINDOW_ALIASES", []))
    merged.update(switch_application.get_default_aliases().keys())
    merged.update(switch_application.aliases.keys())
    window_aliases.set(list(merged))
    print(f"Refreshed alias list with {len(merged)} entries.")

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
        "list instances <window_alias>": R(Function(switch_application.list_instances)),
        "refresh aliases": R(Function(refresh_aliases)),
    }

    extras = [
        ListRef("window_alias", window_aliases),
    ]

def get_rule():
    details = RuleDetails(name="Window Switching")
    return WindowSwitchingRule, details