from dragonfly import ShortIntegerRef, Text

from castervoice.lib.actions import Key

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

class CommandLineCCRRule(MergeRule):

    pronunciation = "command line c c r"

    mapping = {
        "axe": R(Key("a-backspace")),
    }

_executables = [
    "WindowsTerminal"
]


def get_rule():
    details = RuleDetails(executable=_executables,
                          ccrtype=CCRType.APP)
    return CommandLineCCRRule, details
