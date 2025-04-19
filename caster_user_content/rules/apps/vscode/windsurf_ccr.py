from dragonfly import Choice, Dictation

from castervoice.lib.actions import Key, Text
from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev

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
    details = RuleDetails(executable="Windsurf",
                          ccrtype=CCRType.APP)
    return WindsurfCCRRule, details
