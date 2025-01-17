from dragonfly import Repeat, Dictation, Choice, ShortIntegerRef

from castervoice.lib.actions import Key, Text

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R


class CursorCcrRule(MergeRule):
    pronunciation = "cursor c c r"

    mapping = {
        "line del [<n>]": # Requires user-defined key binding (delete line)
            R(Key("c-k:2")*Repeat(extra='n')),
    }
    extras = [
        ShortIntegerRef("n", 1, 100),
    ]

    defaults = {"n": 1,}


def get_rule():
    details = RuleDetails(executable="cursor",
                          title="Cursor",
                          ccrtype=CCRType.APP)
    return CursorCcrRule, details
