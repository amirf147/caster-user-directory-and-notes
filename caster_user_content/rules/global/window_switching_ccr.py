from dragonfly import Function, Mouse, ListRef, ShortIntegerRef, Choice

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.const import CCRType

from caster_user_content.util import switch_application, taskbar
from caster_user_content.environment_variables import WINDOWS_APP_ALIASES

# Import the shared window_aliases from the package
# from . import window_aliases

def _switch_to_app(app_name, instance):
    taskbar.activate_taskbar_instance(app_name, instance)

class WindowSwitchingCCRRule(MergeRule):
    pronunciation = "window switching c c r"

    mapping = {
        # Switching command
        # "[switch [to]] <window_alias>":
        #     R(Function(switch_application.switch_to) + Mouse("(0.5, 0.5)")),
        "<app_name> [<instance>]": R(Function(_switch_to_app) + Mouse("(0.5, 0.5)")),
    }
    extras = [
        # ListRef("window_alias", window_aliases),
        ShortIntegerRef("instance", 1, 10),
        Choice("app_name", WINDOWS_APP_ALIASES),
    ]
    defaults = {
        "instance": 1,
    }

def get_rule():
    details = RuleDetails(ccrtype=CCRType.GLOBAL)
    return WindowSwitchingCCRRule, details
