from dragonfly import Dictation, MappingRule, ShortIntegerRef, Pause, IntegerRef
from castervoice.lib.actions import Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CustomMSWordRule(MappingRule):
    mapping = {

       "hint <ribbon>":
           Key("a-%(ribbon)s"), 

    }
    extras = [
        Dictation("query"),
        ShortIntegerRef("n", 1, 100),
        IntegerRef("n3", 1, 4),
        Choice

    ]
    defaults = {"n": 1, "query": "",}


def get_rule():
    details = RuleDetails(name="Custom Microsoft Word", executable="winword")
    return CustomMSWordRule, details