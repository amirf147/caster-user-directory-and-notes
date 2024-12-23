from dragonfly import ShortIntegerRef, Text, Choice

from castervoice.lib.actions import Key

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

class CommandLineCCRRule(MergeRule):

    pronunciation = "command line c c r"

    mapping = {
        "axe": R(Key("a-backspace")),
        
        "dirrup":
            R(Text("cd ../ ; ls;") + Key("enter")),
        
        "go <path>": R(Text("cd %(path)s") + Key("enter")),

        "go": R(Key("c, d, space")),

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
        Choice("path", {
            "pi folder": "C:/Users/amirf/python",
            "documents": "C:/Users/amirf/Documents",
            "caster user": "C:/Users/amirf/AppData/Local/caster",
            "caster rules": "C:/Users/amirf/AppData/Local/caster/caster_user_content/rules",
            "caster apps": "C:/Users/amirf/AppData/Local/caster/caster_user_content/rules/apps",
        }),
        Choice("exe", {
            "pi twelve": "$p312", # Environment Variable
        }),
    ]

_executables = [
    "WindowsTerminal",
    "cmd",
]


def get_rule():
    details = RuleDetails(executable=_executables,
                          ccrtype=CCRType.APP)
    return CommandLineCCRRule, details
