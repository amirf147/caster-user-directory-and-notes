from dragonfly import Dictation, MappingRule, ShortIntegerRef, IntegerRef
from castervoice.lib.actions import Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


REFERENCES_RIBBON = "a-s"

class CustomMSWordRule(MappingRule):
    mapping = {

        "go to page <n>":
            R(Key("f5/50") + Text("%(n)d") + Key("enter, escape")),
        
        "find and replace": R(Key("c-h")),
        "etsy <query>": R(Key("c-h/5, s-tab, left") +
                          Text("%(query)s") + Key("enter")),

        "update field": R(Key("f9")),
        "update table": R(Key("f9/50, down, enter")),

        # Read aloud
        "read aloud": R(Key("ca-space")),
        "(pause | resume | start | stop) reading": R(Key("c-space")),
        "next paragraph": R(Key("c-right")),
        "previous paragraph": R(Key("c-left")),

        "reading mode": R(Key("a-w/10, f")),

        "insert image": R(Key("alt, n, p")),
        "file open": R(Key("c-o/30, a-o/100, o")),
        "file retain": R(Key("c-s")),
        "file new": R(Key("c-n")),
        "file export": R(Key("a-f/100, e")),
        "file custom retain": R(Key("a-f, a/60") + Key("o")),

        "focus": R(Key("f6")),

        # Viewing Headings in Navigation Pane
        "navigate headings":
            R(Key("c-f/100, backspace, tab:2/3, left:2/3, tab:2")),

        # Pasting only text without formatting
        "paste text":
            R(Key("s-f10/3, t")),

        # Cycle through case formatting for highlighted text
        "cycle case":
            R(Key("s-f3")),


        # copy hyperlink via the context menu
        "copy hyperlink":
            R(Key("s-f10/3, down:5, enter")),

        # Zooming
        "zoom in [<n>]":
            R(Key("a-w/50, q/3, tab:2, up:%(n)d, enter")),
        "zoom out [<n>]":
            R(Key("a-w/50, q/3, tab:2, down:%(n)d, enter")),
        "zoom reset":
            R(Key("a-w/50, j")),
        "zoom dialogue":
            R(Key("a-w/50, q")),
        "zoom width": R(Key("a-w/50, i")),

        # Editing
        "remove formatting":
            R(Key("c-space")),
        "format underline":
            R(Key("c-u")),
        "format strike through":
            R(Key("a-h/3, 4")),
        "text increase":
            R(Key("cs->")),
        "text decrease":
            R(Key("cs-<")),
        "insert bullet":
            R(Key("cs-l")),
        "insert number":
            R(Key("ca-l")),
        "super script":
            R(Key("c-plus")),
        "subscript":
            R(Key("c-equals")),
        "create hyperlink":
            R(Key("c-k")),
        "highlight red": R(Key("a-h, i, down, enter")),
        "highlight yellow": R(Key("a-h, i, enter")),
        "remove highlight": R(Key("a-h, i, n")),
        "highlight dialogue": R(Key("a-h, i")),
        "color blue": R(Key("a-h/3, f, c, tab, right:7, enter")),

        # Beginning an italicized quote
        "format q":
            R(Key("c-space/2, \":2, left, c-i")),

        # Paragraph Formatting
        "page break":
            R(Key("c-enter")),
        "lay align":
            R(Key("c-l")),
        "center align":
            R(Key("c-e")),
        "ray align":
            R(Key("c-r")),
        "justify align":
            R(Key("c-j")),

        # Home Ribbon Actions
        "show paragraph":
            R(Key("a-h, z, p, 8")),
        "show styles":
            R(Key("a-h, l")),

        # References Ribbon Actions
        "insert caption":
            R(Key(f"{REFERENCES_RIBBON}, p")),

        # Opening Dialogs
        "font dialog":
            R(Key("c-d")),
        "paragraph dialog":
            R(Key("a-h/3, p, g")),
        "insert bookmark":
            R(Key("cs-f5")),
        "color dialog":
            R(Key("a-h/3, f, c")),
        "table dialog":
            R(Key("a-n/3, t, i")),

        # Applying styles
        "apply normal [style]":
            R(Key("cs-n")),

        # Page Layout
        # Add line numbers with option: "Restart Each Page"
        "page line numbers":
            R(Key("a-p/3, l, n, r")),
        "remove line numbers":
            R(Key("a-p/3, l, n, n")),

        # Expand/Collapse text under a heading
        "expand text":
            R(Key("as-+")),
        "collapse text":
            R(Key("as--")),

        # Ribbon
        "collapse ribbon":
            R(Key("c-f1")),
        "peak ribbon":
            R(Key("c-f1/150, c-f1")),
        "hint design":
            R(Key("a-g")),
        "hint references":
            R(Key("a-s")),
        "hint insert":
            R(Key("a-n")),
        "hint view":
            R(Key("a-w")),
        "hint home":
            R(Key("a-h")),
        "hint review":
            R(Key("a-r")),
        "hint layout":
            R(Key("a-p")),
        "hint mailings":
            R(Key("a-m")),
        "hint developer":
            R(Key("a-l")),

        # Ribbon: Table Design
        "hint table design":
            R(Key("alt/3, j, t")),
        "hint borders":
            R(Key("a-j, t/3, b")),
        "table shading":
            R(Key("alt/3, j, t/3, h")),
        "remove table shading":
            R(Key("alt/3, j, t/3, h, n")),

        # Ribbon: Table Layout
        "hint table lay out":
            R(Key("alt/3, j, l")),
        "table row above":
            R(Key("alt/3, j, l, a")),
        "table row below":
            R(Key("alt/3, j, l, b, e")),
        "table merge cells":
           R(Key("alt/3, j, l, m")),
        "table delete row":
            R(Key("alt/3, j, l, d, r")),
        "table auto fit":
            R(Key("alt/3, j, l, f, c")),

        # "Tell me" search box
        "queen [<query>]":
            R(Key("a-q/3") + Text("%(query)s")),

        # Panes
        "close pane":
            R(Key("c-space/3, up, enter")),
    }
    extras = [
        Dictation("query"),
        ShortIntegerRef("n", 1, 100),

    ]
    defaults = {"n": 1, "query": "",}


def get_rule():
    details = RuleDetails(name="Custom Microsoft Word", executable="winword")
    return CustomMSWordRule, details