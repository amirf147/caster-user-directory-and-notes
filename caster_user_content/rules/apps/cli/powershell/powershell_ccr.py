from dragonfly import Text, Choice

from castervoice.lib.actions import Key

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

class PowershellCCRRule(MergeRule):

    pronunciation = "power shell c c r"

    mapping = {
        "dirrup":
            R(Text("cd ../ ; ls;") + Key("enter")),
        
        "go": R(Key("c, d, space")),
        "to clipboard": R(Key("space, |, space, c, l, i, p")),

        # Executables
        "<exe>": R(Text("%(exe)s")),

        # Python exe
        "pi debug": R(Text("$p312 -m pdb ")),

        # SQL
        "seekum": R(Text("sqlcmd") + Key("space")),
        "seekle": R(Text("sqlite3") + Key("space")),
        "ghost": R(Key("G, O, enter")),
    }
    extras = [
        Choice("exe", {
            "pi twelve": "$p312", # Environment Variable
            "print work": "pwd",
        }),

    ]



def get_rule():
    details = RuleDetails(executable="powershell",
                          ccrtype=CCRType.APP)
    return PowershellCCRRule, details
