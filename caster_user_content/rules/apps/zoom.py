from dragonfly import MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class ZoomRule(MappingRule):

    mapping = {
        "show chat": R(Key("a-h")),
        "show mic": R(Key("a-a")),
        "show video": R(Key("a-v")),
        "(start | stop) sure recording": R(Key("a-r")),
        "(start | stop) sure sharing": R(Key("a-s")),
        "show reactions": R(Key("cs-y")),
        "show participants": R(Key("a-u")),
        "end sure meeting": R(Key("a-q")),
    }
    extras = [
        ShortIntegerRef("n", 1, 100),
    ]
    defaults = {"n": 1}


def get_rule():
    return ZoomRule, RuleDetails(name="Zoom", executable="zoom")
