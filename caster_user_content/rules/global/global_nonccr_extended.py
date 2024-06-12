from dragonfly import MappingRule, IntegerRef
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R

class GlobalNonCCRExtendedRule(MappingRule):
    pronunciation = "global extended"
    mapping = {
        "switch <n>":
            R(Key("w-%(n)d/3")),
        "switch minus [<n>]":
            R(Key("w-t/3, up:%(n)d, enter")),
        "volume output":
            R(Key("w-b/3, up:3, enter/9")),
    }
    extras = [
        IntegerRef("n", 1, 10),
    ]
    defaults = {
        "n": 1
    }

def get_rule():
    details = RuleDetails(name="Global Non CCR Extended")
    return GlobalNonCCRExtendedRule, details
