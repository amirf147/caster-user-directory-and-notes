from dragonfly import MappingRule
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

class VsCodeExtendedRule(MappingRule):
    pronunciation = "code extended"
    mapping = {
        "pop out window": R(Key("c-k, o")),
        "open recent": R(Key("c-r")),

        # Requires user defined key binding
        # Command: Terminal: Move Terminal into New Window
        "pop out terminal": R(Key("c-k, a-t")),
    }

def get_rule():
    return VsCodeExtendedRule, RuleDetails(name="VSCodeExtended", executable="code")
