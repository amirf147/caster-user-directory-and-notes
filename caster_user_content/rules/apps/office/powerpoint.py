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
        "new slide":
           R(Key("a-h/3, z, s, i")),
        "duplicate slide":
            R(Key("c-d")),

        # Home ribbon actions
        "show design pane":
            R(Key("a-h/3, d, 2")),

        "insert <insert_action>":
            R(Key("%(insert_action)s")),

        "show selection pane":
            R(Key("a-f10")),

        "show grid lines":
            R(Key("s-f9")),

        "queen <query>":
            R(Key("a-q/3") + Text("%(query)s")),

        }

    extras = [
        Dictation("query"),
        ShortIntegerRef("n", 1, 100),
        IntegerRef("n3", 1, 4),
        Choice("insert_action", {
            "text box": "a-n/3, x",
            "image": "a-n/3, z, g/3, p, 1, d",
            "smart art": "a-n/3, m",
        }),
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