from dragonfly import MappingRule
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

class VsCodeExtendedRule(MappingRule):
    pronunciation = "code extended"
    mapping = {
        "pop out window": R(Key("c-k, o")),
    }

def get_rule():
    return VsCodeExtendedRule, RuleDetails(name="VSCodeExtended", executable="code")
