from dragonfly import MappingRule, ShortIntegerRef, Dictation
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

class VsCodeExtendedRule(MappingRule):
    pronunciation = "code extended"
    mapping = {
        "pop out window": R(Key("c-k, o")),
        "open recent": R(Key("c-r")),
        "pane increase [<n>]":
            R(Key("cs-i:%(n)d")),
        "pane decrease [<n>]":
            R(Key("cs-o:%(n)d")),
        "kill terminal":
            R(Key("ca-w")),
        "[show] completions": R(Key("c-space")),

        "quick open":
            R(Key("c-e")),

        # BUG: The text output results in missing letters
        # TODO: Switch to VScodium where this bug does not occur
        "open <text>":
            R(Key("c-e/5") + Text("%(text)s")),

        # Requires Extension: jumpy
        # Requires user defined key binding: "command": "extension.jumpy-exit"
        "hints":
            R(Key("s-enter")),

        # Requires user defined key binding
        # Command: Terminal: Move Terminal into New Window
        "pop out terminal": R(Key("c-k, a-t")),

        # Requires user defined key binding
        # Command: Python: Select Interpreter
        "[select [python]] interpreter": R(Key("c-k, a-p")),

        # Requires user defined key binding
        # Collapse folders in explorer
        "collapse folders":
            R(Key("c-k, cs-f")),

    }
    extras = [
        ShortIntegerRef("n", 1, 11),
        Dictation("text"),
    ]
    defaults = {"n": 1}

def get_rule():
    return VsCodeExtendedRule, RuleDetails(name="VSCodeExtended", executable="code")
