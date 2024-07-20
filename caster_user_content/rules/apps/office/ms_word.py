from dragonfly import Dictation, MappingRule, ShortIntegerRef, Pause
from castervoice.lib.actions import Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CustomMSWordRule(MappingRule):
    mapping = {
        "insert image": R(Key("alt, n, p")),
        "file open": R(Key("c-o")),
        "file retain": R(Key("c-s")),
        "file custom retain": 
            R(Key("a-f, a") +
              Pause("60") + Key("c")),
        "file new": R(Key("c-n")),
    }
    extras = [
        Dictation("dict"),
        ShortIntegerRef("n", 1, 100),
    ]
    defaults = {"n": 1, "dict": "nothing"}


def get_rule():
    details = RuleDetails(name="Custom Microsoft Word", executable="winword")
    return CustomMSWordRule, details
