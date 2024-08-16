from dragonfly import Dictation, MappingRule, ShortIntegerRef, Pause, IntegerRef
from castervoice.lib.actions import Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CustomMSWordRule(MappingRule):
    mapping = {
        "insert image": R(Key("alt, n, p")),
        "file open": R(Key("c-o")),
        "file retain": R(Key("c-s")),
        "file new": R(Key("c-n")),

        # Initial attempt at getting to file save as
        "file custom retain": 
            R(Key("a-f, a") +
              Pause("60") + Key("c")),

        # text formatting
        "format bold":
            R(Key("c-b")),
        "italicize":
            R(Key("c-i")),
        "format underline":
            R(Key("c-u")),
        "text increase":
            R(Key("cs->")),
        "text decrease":
            R(Key("cs-<")),
        "insert bullet":
            R(Key("*, tab")),
        "insert number":
            R(Key("1, tab")),
        "super script":
            R(Key("c-plus")),
        "subscript":
            R(Key("c-equals")),

        # Applying styles
        "apply normal [style]":
            R(Key("cs-n")),
        "apply heading <n3>":
            R(Key("ac-%(n3)d")),
    }
    extras = [
        Dictation("dict"),
        ShortIntegerRef("n", 1, 100),
        IntegerRef("n3", 1, 4)
    ]
    defaults = {"n": 1, "dict": "nothing"}


def get_rule():
    details = RuleDetails(name="Custom Microsoft Word", executable="winword")
    return CustomMSWordRule, details