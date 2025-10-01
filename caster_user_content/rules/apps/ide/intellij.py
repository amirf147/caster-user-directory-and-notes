from dragonfly import MappingRule

from castervoice.lib.actions import Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

class IntelliJRule(MappingRule):
    
    mapping = {
        # Diagram related commands
        "show diagram": R(Key("cas-u")),
        "find usages": R(Key("a-f7")),

        "collapse methods": R(Key("cs-minus")),
        "expand methods": R(Key("cs-plus")),

    }

def get_rule():
    return IntelliJRule, RuleDetails(name="intellij", executable="idea64")
