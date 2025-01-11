from dragonfly import Text, Choice

from castervoice.lib.actions import Key

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev

class PowershellCCRRule(MergeRule):

    pronunciation = "power shell c c r"

    mapping = {
        "to clipboard": R(Key("space, |, space, c, l, i, p")),

        # Executables/Commands
        "<exe>": R(Text("%(exe)s") + Key("space")),

        # SQL
        "ghost": R(Key("G, O, enter")),
    }
    extras = [
        Choice("exe", ev.EXECUTABLES),
    ]

def get_rule():
    details = RuleDetails(executable="powershell",
                          ccrtype=CCRType.APP)
    return PowershellCCRRule, details
