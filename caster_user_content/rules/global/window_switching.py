from dragonfly import MappingRule, Function, List, ListRef, Mouse, Dictation  # Added Dictation!
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content.util import switch_application
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

# -- NEW FUNCTION: For dynamic aliasing using dictation --
def set_window_dictation(dict_window_alias):
    """Helper for dynamic window alias assignment from dictation."""
    if not dict_window_alias:
        print("No alias provided")
        return
    # Convert Dragonfly Dictation to string and trim whitespace
    alias_str = str(dict_window_alias).strip()
    if not alias_str:
        print("Alias is empty after stripping whitespace")
        return
    switch_application.set_window(alias_str)

class WindowSwitchingRule(MappingRule):
    pronunciation = "window switching"

    mapping = {
        # Setting commands
        "set window <window_alias>": R(Function(switch_application.set_window)),
        # --- New dynamic command ---
        "custom window <dict_window_alias>": R(Function(set_window_dictation)),

        "set page <window_alias>": R(Function(switch_application.set_page)),

        # Utility command
        "list aliases": R(Function(list_aliases)),
    }

    extras = [
        ListRef("window_alias", window_aliases),
        Dictation("dict_window_alias"),  # Include Dictation!
    ]

def get_rule():
    details = RuleDetails(name="Window Switching")
    return WindowSwitchingRule, details