from dragonfly import Dictation

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule


class AntigravityCCRRule(MergeRule):

    pronunciation = "antigravity c c r"

    mapping = {
    }
    extras = [
        Dictation("text"),
    ]

def get_rule():
    details = RuleDetails(executable="Antigravity IDE",
                          title="Antigravity IDE",
                          ccrtype=CCRType.APP)
    return AntigravityCCRRule, details
