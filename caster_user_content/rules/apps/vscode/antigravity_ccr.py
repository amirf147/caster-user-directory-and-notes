from dragonfly import Choice, Dictation

from castervoice.lib.actions import Key, Text
from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev

class AntigravityCCRRule(MergeRule):

    pronunciation = "antigravity c c r"

    mapping = {
    }
    extras = [
        Dictation("text"),
    ]

def get_rule():
    details = RuleDetails(executable="antigravity",
                          title="Antigravity",
                          ccrtype=CCRType.APP)
    return AntigravityCCRRule, details
