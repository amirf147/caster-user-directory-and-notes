from castervoice.lib.actions import Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.const import CCRType

class EnableViaCamRule(MergeRule):
    mapping = {
        "pose":
            R(Key("f11")),
    }
    extras = [
    ]
    defaults = {}


def get_rule():
    details = RuleDetails(ccrtype=CCRType.GLOBAL)
    return EnableViaCamRule, details
