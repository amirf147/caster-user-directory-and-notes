from dragonfly import Function, Repeat, Dictation, Choice, MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class GoogleMeetRule(MappingRule):

    pronunciation = "google meet"

    mapping = {
        "show chat": R(Key("ca-c")),
        "toggle mic": R(Key("c-d")),
    }
    extras = [
        ShortIntegerRef("n", 1, 100),
        Dictation("dictation"),
    ]
    defaults = {"n": 1}


def get_rule():
    return GoogleMeetRule, RuleDetails(name="google meet", executable="firefox", title="Meet")
