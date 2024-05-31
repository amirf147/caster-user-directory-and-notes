from dragonfly import MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

class FirefoxExtendedRule(MappingRule):
    pronunciation = "extended fire fox"
    mapping = {
        "page <n>":
            R(Key("c-%(n)d")),
    }
    extras = [
        ShortIntegerRef("n", 1, 10),
    ]
    defaults = {
        "n": 1
    }

def get_rule():
    return FirefoxExtendedRule, RuleDetails(name="fire fox extended", executable="firefox")
