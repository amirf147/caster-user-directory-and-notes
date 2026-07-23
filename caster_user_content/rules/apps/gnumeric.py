from dragonfly import Dictation, MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class GnumericRule(MappingRule):
    pronunciation = "numeric"
    mapping = {
        "file open": R(Key("c-o")),
        "fit width": R(Key("a-o, right, w")),
        "fit height": R(Key("a-o, right, h")),
        "match above": R(Key("c-d")),
        "cell insert": R(Key("cs-+")),
    }
    extras = [
        ShortIntegerRef("n", 1, 10),
        Dictation("text"),
    ]
    defaults = {
        "n": 1,
    }


def get_rule():
    return GnumericRule, RuleDetails(name="Gnumeric Rule", executable="gnumeric")
