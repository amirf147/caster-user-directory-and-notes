from dragonfly import MappingRule
from castervoice.lib.actions import Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class EnableViaCamRule(MappingRule):
    mapping = {
        "pointer":
            R(Key("f11")),
    }
    extras = [
    ]
    defaults = {}


def get_rule():
    details = RuleDetails(name="enable via cam rule")
    return EnableViaCamRule, details
