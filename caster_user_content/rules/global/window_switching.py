from dragonfly import MappingRule, Function, Choice, Dictation
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content.util import app_switcher
from caster_user_content.environment_variables import WINDOW_ALIASES


def list_aliases():
    """Print all current aliases"""
    print("\nCurrent Aliases:")
    for alias, info in app_switcher.aliases.items():
        alias_type = "Tab" if info.is_tab else "Window"
        print(f"{alias}: {alias_type} - {info.title}")


def _set_window(predefined_alias=None, dictated_alias=None):
    alias = predefined_alias or dictated_alias
    if alias:
        app_switcher.set_window(alias)


def _set_page(predefined_alias=None, dictated_alias=None):
    alias = predefined_alias or dictated_alias
    if alias:
        app_switcher.set_page(alias)


class WindowSwitchingRule(MappingRule):
    pronunciation = "window switching"

    mapping = {
        # Setting commands
        "set window <predefined_alias>": R(Function(_set_window)),
        "set window <dictated_alias>": R(Function(_set_window)),
        "set page <predefined_alias>": R(Function(_set_page)),
        "set page <dictated_alias>": R(Function(_set_page)),
        "clear alias": R(Function(app_switcher.clear_alias)),
        "alias reset": R(Function(app_switcher.clear_all_aliases)),
        # Utility command
        "list aliases": R(Function(list_aliases)),
        "show app info": R(Function(app_switcher.show_window_info)),
    }

    extras = [
        Choice("predefined_alias", {a: a for a in WINDOW_ALIASES}),
        Dictation("dictated_alias"),
    ]


def get_rule():
    details = RuleDetails(name="Window Switching")
    return WindowSwitchingRule, details
