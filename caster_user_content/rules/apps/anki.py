from dragonfly import MappingRule

from castervoice.lib.actions import Key

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class AnkiRule(MappingRule):
    pronunciation = "anki"
    mapping = {
        "file import": R(Key("cs-i")),

    }
    extras = []
    defaults = {}

def get_rule():
    return AnkiRule, RuleDetails(name="anki", executable="anki")