from dragonfly import ShortIntegerRef, Text, Choice

from castervoice.lib.actions import Key

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

class WindowsTerminal(MergeRule):

    pronunciation = "windows terminal"
    mapping = {
        "menu": R(Key("a-space")),
        "dirrup":
            R(Text("cd ../ ; ls;") + Key("enter")),
        
        "go <path>": R(Text("cd %(path)s") + Key("enter")),

        # Executables
        "<exe>": R(Text("%(exe)s")),

        # Python exe
        "pi debug": R(Text("$p312 -m pdb ")),

    }
    extras = [
        Choice("path", {
            "pi folder": "C:/Users/amirf/python",
        }),
        Choice("exe", {
            "pi twelve": "$p312", # Environment Variable
        }),
    ]

def get_rule():
    details = RuleDetails(executable="WindowsTerminal",
                          ccrtype=CCRType.APP)
    return WindowsTerminal, details
