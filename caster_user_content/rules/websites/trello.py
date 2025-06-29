from dragonfly import MappingRule, Choice
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

class TrelloRule(MappingRule):

    mapping = {
        "card new": R(Key("n")),
        "card archive": R(Key("c")),
        "label <color>": R(Key("l/30, %(color)s, tab, enter, escape")),
    }

    extras = [
        Choice("color", {
            "green": "1",
            "yellow": "2",
            "orange": "3",
            "red": "4",
            "purple": "5",
            "blue": "6",
        }),
    ]

    defaults = {
    }

def get_rule():
    return TrelloRule, RuleDetails(name="Trello", title="Trello")
