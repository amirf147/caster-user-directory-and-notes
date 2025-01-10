from dragonfly import Text, Choice

from castervoice.lib.actions import Key

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev


class CommandLineCCRRule(MergeRule):

    pronunciation = "command line c c r"

    mapping = {
        "axe": R(Key("a-backspace")),
        
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
        Choice("exe", ev.EXECUTABLES),
    ]

_executables = [
    "WindowsTerminal",
    "cmd",
]


def get_rule():
    details = RuleDetails(executable=_executables,
                          ccrtype=CCRType.APP)
    return CommandLineCCRRule, details
