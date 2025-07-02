from dragonfly import MappingRule, Choice, IntegerRef, Repeat
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

class TrelloRule(MappingRule):

    mapping = {
        "sidebar": R(Key("[")),
        "board menu": R(Key("]")),
        "card new": R(Key("n")),
        "card archive": R(Key("c")),
        "due date": R(Key("d")),
        "checklist": R(Key("minus")),
        "card over [<n>]": R(Key("</20")) * Repeat(extra='n'),
        "card under [<n>]": R(Key(">/20")) * Repeat(extra='n'),
        "move over [<n>]": R(Key("comma/20")) * Repeat(extra='n'),
        "move under [<n>]": R(Key("./20")) * Repeat(extra='n'),
        "label <color>": R(Key("l/40, %(color)s, tab, enter, escape")),
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
        IntegerRef("n", 1, 10),
    ]

    defaults = {
        "n": 1,
    }

def get_rule():
    return TrelloRule, RuleDetails(name="Trello", title="Trello")
