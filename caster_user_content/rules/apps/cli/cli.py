from dragonfly import Function, Repeat, Choice, Dictation, MappingRule, Pause, ShortIntegerRef

from castervoice.lib.actions import Key, Mouse

from castervoice.lib import navigation
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

class CommandLineRule(MappingRule):
    mapping = {
        "show settings": R(Key("c-comma")),
        "close tab": R(Key("cs-w")),

        "dirrup": R(Text("cd ../ ; ls;") + Key("enter")),
        "dir home": R(Text("cd; ls;") + Key("enter")),

        "pi twelve": R(Text("$p312 ")),
        "pi quit": R(Text("quit()") + Key("enter")),
        "pi exit": R(Text("exit()") + Key("enter")),
        "see exit": R(Text("EXIT") + Key("enter")),
        "wiper": R(Text("clear") + Key("enter")),
    }
    extras = [
    ]
    defaults = {
    }

_executables = [
    "WindowsTerminal",
    "cmd",
]
def get_rule():
    return CommandLineRule, RuleDetails(name="Command Line", executable=_executables)
