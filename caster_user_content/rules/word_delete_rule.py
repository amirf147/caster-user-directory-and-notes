from dragonfly import MappingRule, IntegerRef, Repeat

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.const import CCRType

class WordDeleteRule(MergeRule):
    pronunciation = "word delete"
    mapping = {
        "scratch [<n>]": R(Key("c-backspace:%(n)d")),
        "dear [<n>]": R(Key("c-del:%(n)d")),
    }
    extras = [
        IntegerRef("n", 1, 99),
    ]
    defaults = {
        "n": 1
    }

def get_rule():
    details = RuleDetails(ccrtype=CCRType.GLOBAL)
    return WordDeleteRule, details

