from dragonfly import MappingRule, ShortIntegerRef, Repeat
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

class ElementMatrixRule(MappingRule):

    mapping = {
        "show settings":
            R(Key("c-slash")),
        "show spaces":
            R(Key("cs-o")),
        "show menu":
            R(Key("c-`")),
        "go to home view":
            R(Key("ca-h")),
    }

def get_rule():
    return ElementMatrixRule, RuleDetails(name="element matrix", executable="Element")
