from dragonfly import Dictation

from castervoice.lib.actions import Text
from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R


class WindsurfCCRRule(MergeRule):
    pronunciation = "windsurf c c r"

    mapping = {
        # Cascade Chat Context
        "site <text>": R(Text("@file:%(text)s", pause=0.0)),
        "lek": R(Text("@directory:%(text)s", pause=0.0)),
    }
    extras = [
        Dictation("text"),
    ]


def get_rule():
    details = RuleDetails(executable="Windsurf", ccrtype=CCRType.APP)
    return WindsurfCCRRule, details
