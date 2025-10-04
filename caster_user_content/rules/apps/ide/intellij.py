from dragonfly import MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

class IntelliJRule(MappingRule):
    
    mapping = {

        "zoom in [<n>]": R(Key("as-=:%(n)d")),
        "zoom out [<n>]": R(Key("as-minus:%(n)d")),
        "zoom (reset | one hundred)": R(Key("as-0")),

        # Diagram related commands
        "show diagram": R(Key("cas-u")), # Requires Ultimate version
        "(find | show) usages": R(Key("a-f7")),

        "collapse methods": R(Key("cs-minus")),
        "expand methods": R(Key("cs-plus")),

    }
    extras = [
        ShortIntegerRef("n", 1, 21)
    ]
    defaults = {
        "n": 1
    }

def get_rule():
    return IntelliJRule, RuleDetails(name="intellij", executable="idea64")
