from dragonfly import Function, Repeat, Dictation, Choice, MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CustomOutlookRule(MappingRule):

    pronunciation = "custom outlook"

    mapping = {
        "focus [<n>]": R(Key("f6:%(n)d")),
        "locus [<n>]": R(Key("s-f6:%(n)d")),
        "synchronize": R(Key("f9")),
        "go to inbox": R(Key("c-1/3, cs-i")),
    }
    extras = [
        ShortIntegerRef("n", 1, 100),
    ]
    defaults = {"n": 1,}


def get_rule():
    return CustomOutlookRule, RuleDetails(name="custom outlook", executable="olk")
