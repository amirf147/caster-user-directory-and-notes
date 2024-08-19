from dragonfly import Function, Repeat, Dictation, Choice, MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CustomOutlookRule(MappingRule):

    pronunciation = "custom outlook"

    mapping = {
        "focus": R(Key("f6")),
        "locus": R(Key("s-f6")),
    }
    extras = [
        ShortIntegerRef("n", 1, 100),
    ]
    defaults = {"n": 1}


def get_rule():
    return CustomOutlookRule, RuleDetails(name="custom outlook", executable="olk")
