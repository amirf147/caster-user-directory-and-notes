from dragonfly import ShortIntegerRef, Text, Choice, Repeat

from castervoice.lib.actions import Key

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

class VimCCR(MergeRule):

    pronunciation = "vim c c r"
    mapping = {
    }
    extras = [
        ShortIntegerRef("n", 1, 11),
    ]
    defaults = {
        "n": 1,
    }

def get_rule():
    details = RuleDetails(executable="WindowsTerminal",
                          ccrtype=CCRType.APP)
    return VimCCR, details
