from dragonfly import Function, Mouse, ListRef, ShortIntegerRef, Choice

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.const import CCRType

from caster_user_content.util import app_switcher
from caster_user_content.environment_variables import WINDOW_ALIASES, WINDOWS_APP_ALIASES

def _switch_to_app(app_name, instance):
    app_switcher.switch_to_app(app_name, instance)

class WindowSwitchingCCRRule(MergeRule):
    pronunciation = "window switching c c r"

    mapping = {
        # Switching command
        "[switch [to]] <window_alias>":
            R(Function(app_switcher.switch_to_alias) + Mouse("(0.5, 0.5)")),
        "<app_name> [<instance>]": R(Function(_switch_to_app) + Mouse("(0.5, 0.5)")),
    }
    extras = [
        Choice("window_alias", {a: a for a in WINDOW_ALIASES}),
        ShortIntegerRef("instance", 1, 10),
        Choice("app_name", WINDOWS_APP_ALIASES),
    ]
    defaults = {
        "instance": 1,
    }

def get_rule():
    details = RuleDetails(ccrtype=CCRType.GLOBAL)
    return WindowSwitchingCCRRule, details
