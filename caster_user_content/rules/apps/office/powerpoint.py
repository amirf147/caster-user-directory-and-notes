from dragonfly import Dictation, MappingRule, ShortIntegerRef, IntegerRef, Choice, Function
from castervoice.lib.actions import Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

def _change_slide(n0_50):
    n0_50 -= 1
    Key("escape, home/5, pgdown:%(n0_50)d").execute({"n0_50": n0_50})

class PowerPointRule(MappingRule):

    mapping = {

        "switch focus [<n>]":
            R(Key("f6:%(n)d")),
        "shin focus [<n>]":
            R(Key("s-f6:%(n)d")),

        "zoom in [<n>]":
            R(Key("a-w/3, q/3, tab, up:%(n)d, enter")),
        "zoom out [<n>]":
            R(Key("a-w/3, q/3, tab, down:%(n)d, enter")),

        "file custom retain":
            R(Key("a-f/3, a")),

        "cycle case":
            R(Key("s-f3")),
        "hint <ribbon>":
           R(Key("a-%(ribbon)s")),

        # Text
        "center align":
            R(Key("c-e")),
        "lay align":
            R(Key("c-l")),
        "indent":
            R(Key("as-right")),
        "unindent":
            R(Key("as-left")),
        
        # Font
        "font color":
            R(Key("a-h, f, c")),
        "font size":
            R(Key("a-h, f, s")),
        "text increase [<n10>]":
            R(Key("cs->:%(n10)d")),
        "text decrease [<n10>]":
            R(Key("cs-<:%(n10)d")),
        "format underline":
            R(Key("c-u")),
        "format bold":
            R(Key("c-b")),


        # Table
        "merge cells":
            R(Key("a-j, l, m")),

        # Slides
        "slide <n0_50>":
            R(Function(_change_slide)),
        "new slide":
           R(Key("a-h/3, z, s, i")),
        "duplicate slide":
            R(Key("c-d")),
        "slide layout":
            R(Key("a-h, l")),

        # Animations
        "add animation":
            R(Key("a-a/3, a, a")),
        "(annie | animation) start":
            R(Key("a-a/3, t")),

        "<pane> pane":
            R(Key("%(pane)s")),

        "insert <insert_action>":
            R(Key("%(insert_action)s")),

        "show grid lines":
            R(Key("s-f9")),

        "queen <query>":
            R(Key("a-q/3") + Text("%(query)s")),

        }

    extras = [
        ShortIntegerRef("n0_50", 0, 51),
        Dictation("query"),
        ShortIntegerRef("n", 1, 100),
        IntegerRef("n3", 1, 4),
        IntegerRef("n10", 1, 11),
        Choice("insert_action", {
            "text box": "a-n/3, x",
            "image": "a-n/3, z, g/3, p, 1, d",
            "smart art": "a-n/3, m",
            "shape": "a-n, s, h",
        }),
        Choice("pane", {
            "selection": "a-f10",
            "design": "a-h/3, d, 2",
            "animation": "a-a/3, c",
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
            "view": "w",
            "table layout": "j, l",
        }),
    ]
    defaults = {"n": 1, "n10": 1, "query": "",}


def get_rule():
    details = RuleDetails(name="PowerPoint", executable="powerpnt")
    return PowerPointRule, details
