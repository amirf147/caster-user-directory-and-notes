from dragonfly import Dictation, MappingRule, ShortIntegerRef, Pause, IntegerRef
from castervoice.lib.actions import Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CustomMSWordRule(MappingRule):
    mapping = {
        "insert image": R(Key("alt, n, p")),
        "file open": R(Key("c-o")),
        "file retain": R(Key("c-s")),
        "file new": R(Key("c-n")),

        "focus": R(Key("f6")),

        # Initial attempt at getting to file save as
        "file custom retain": 
            R(Key("a-f, a") +
              Pause("60") + Key("c")),

        # Editing
        "format italic":
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
        "create hyperlink":
            R(Key("c-k")),

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

        # Opening Dialogs
        "font dialog":
            R(Key("c-d")),
        "paragraph dialog":
            R(Key("a-h/3, p, g")),
        "insert bookmark":
            R(Key("cs-f5")),

        # Applying styles
        "apply normal [style]":
            R(Key("cs-n")),
        "apply heading <n3>":
            R(Key("ac-%(n3)d")),

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
        "hint design":
            R(Key("a-g")),
        "hint references":
            R(Key("a-s")),
        "hint insert":
            R(Key("a-n")),
        "hint view":
            R(Key("a-w")),

        # Ribbon: Table Design
        "hint table":
            R(Key("a-j, t")),
        "hint borders":
        R(Key("a-j, t/3, b")),

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
        IntegerRef("n3", 1, 4),

    ]
    defaults = {"n": 1, "query": "",}


def get_rule():
    details = RuleDetails(name="Custom Microsoft Word", executable="winword")
    return CustomMSWordRule, details