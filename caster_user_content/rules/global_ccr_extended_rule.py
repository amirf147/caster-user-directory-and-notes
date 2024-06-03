from dragonfly import MappingRule, ShortIntegerRef, Repeat

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.const import CCRType

class GlobalCCRExtendedRule(MergeRule):

    pronunciation = "global ccr extended"

    mapping = {
        "flash": R(Key("f2")),
        "go back [<n>]": R(Key("a-left:%(n)d"))
    }
    extras = [
        ShortIntegerRef("n", 1, 10),
    ]
    defaults = {
        "n": 1 
    }

def get_rule():
    details = RuleDetails(ccrtype=CCRType.GLOBAL)
    return GlobalCCRExtendedRule, details

