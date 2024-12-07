from dragonfly import Repeat, Dictation, MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key, Text, Mouse

from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CustomNPPRule(MappingRule):

    mapping = {
        
        # File Management
        "file open": R(Key("c-o")),
        "file new": R(Key("c-n")),
        "file custom retain": R(Key("ca-s")),

        # Line Operations
        "line del [<n>]": R(Key("c-l:%(n)d")),
        "move up [<n>]": R(Key("cs-up:%(n)d")),
        "move down [<n>]": R(Key("cs-down:%(n)d")),

        # Commenting
        "comment": R(Key("c-q")), # Toggle Comment

        "zoom in <n2>": R(Key("c-npadd:%(n2)d")),
        "zoom out <n2>": R(Key("c-npsub:%(n2)d")),

        "code run": R(Key("f5")),
        "pi run": R(Key("c-f6")),
        "exec": R(Key("f6")),
    }
    extras = [
        Dictation("text"),
        ShortIntegerRef("n", 1, 1000),
        ShortIntegerRef("n2", 1, 10),
    ]
    defaults = {"n": 1}


def get_rule():
    return CustomNPPRule, RuleDetails(name="Custom notepad plus plus", executable="notepad++")
