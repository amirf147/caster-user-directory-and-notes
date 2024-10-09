from dragonfly import Dictation, MappingRule, ShortIntegerRef, Pause, IntegerRef, Choice
from castervoice.lib.actions import Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class PowerPointRule(MappingRule):

    mapping = {

        "cycle case":
            R(Key("s-f3")),
        "hint <ribbon>":
           R(Key("a-%(ribbon)s")),

        # Slides
        "slide new":
           R(Key("a-h/3, z, s, i")),

        # Insert ribbon actions
        "insert text box":
            R(Key("a-n/3, x")),
        "insert image":
            R(Key("a-n/3, z, g/3, p, 1, d")),
            
        "show selection pane":
            R(Key("a-f10")),

        "show grid lines":
            R(Key("s-f9")),

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