from dragonfly import Dictation, MappingRule, ShortIntegerRef, Pause, IntegerRef, Choice
from castervoice.lib.actions import Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class PowerPointRule(MappingRule):

    mapping = {
        "hint <ribbon>":
           Key("a-%(ribbon)s"),

        # Slides
        "slide new":
           Key("a-h/3, z, s, i"),
        }

    extras = [
        Dictation("query"),
        ShortIntegerRef("n", 1, 100),
        IntegerRef("n3", 1, 4),
        Choice("ribbon", {
            "file": "f",
            "home": "h",
            "insert": "n",
            "design": "g",
            "transitions": "k",
            "animations": "a",
            "slideshow": "s",
            "record": "c",
            "review": "r",
            "view": "w"
        }),
    ]
    defaults = {"n": 1, "query": "",}


def get_rule():
    details = RuleDetails(name="PowerPoint", executable="powerpnt")
    return PowerPointRule, details