from dragonfly import Function, Repeat, Dictation, Choice, MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class ZoomRule(MappingRule):

    mapping = {
        "show chat": R(Key("a-h")),
    }
    extras = [
        ShortIntegerRef("n", 1, 100),
        Dictation("dictation"),
    ]
    defaults = {"n": 1}


def get_rule():
    return ZoomRule, RuleDetails(name="Zoom", executable="zoom")
