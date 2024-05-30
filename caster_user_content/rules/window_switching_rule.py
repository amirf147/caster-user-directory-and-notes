from dragonfly import MappingRule, IntegerRef

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R

class WindowSwitchingRule(MappingRule):
    mapping = {
        "switch <n>": R(Key("w-%(n)d/3")),
        "switch minus [<n>]": R(Key("w-t/3, up:%(n)d, enter")),
        "switchback": R(Key("a-tab")),
    }
    extras = [
        IntegerRef("n", 1, 9),
    ]
    defaults = {
        "n": 1
    }

def get_rule():
    details = RuleDetails(name="Window Switching Rule")
    return WindowSwitchingRule, details
