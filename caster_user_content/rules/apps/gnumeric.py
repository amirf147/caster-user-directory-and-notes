from dragonfly import Repeat, Dictation, MappingRule, ShortIntegerRef, Choice

from castervoice.lib.actions import Key

from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class GnumericRule(MappingRule):
    pronunciation = "numeric"
    mapping = {

        "fit width": R(Key("a-o, right, w")),
        "match above": R(Key("c-d")),

    }
    extras = [
        ShortIntegerRef("n", 1, 10),
        Dictation("text"),
        ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return GnumericRule, RuleDetails(name="Gnumeric Rule",
                                         executable="gnumeric")
