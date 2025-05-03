from dragonfly import MappingRule, Pause, Function, Dictation, Mimic, Mouse, Repeat, IntegerRef, ShortIntegerRef, Choice, ListRef, List
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib import utilities, navigation
from castervoice.rules.core.navigation_rules import navigation_support
from datetime import datetime, timedelta

from caster_user_content import environment_variables as ev
from caster_user_content.util import switch_application

# Create a Dragonfly List
window_aliases = List("window_alias")
window_aliases.set(["code", "power", "water"])

class WindowSwitchingRule(MappingRule):
    pronunciation = "window switching"
    mapping = {
        # Custom Window Switching
        "set window <window_alias>": R(Function(switch_application.set_alias, window_alias="%(window_alias)s")),
        "switch [to] <window_alias>": R(Function(switch_application.alias, window_alias="%(window_alias)s")),
    }

    extras = [
        ListRef("window_alias", window_aliases),
    ]

def get_rule():
    details = RuleDetails(name="Window Switching")
    return WindowSwitchingRule, details