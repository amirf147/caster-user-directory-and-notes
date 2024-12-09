from dragonfly import MappingRule

from castervoice.lib.actions import Text, Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CustomPython(MappingRule):
    mapping = {
        "with":
            R(Text("with ")),
        "open file":
            R(Text("open('filename','r') as f:")),
        "read lines":
            R(Text("content = f.readlines()")),
        "try catch":
            R(
                Text("try:") + Key("enter:2/10, backspace") + Text("except Exception:") +
                Key("enter")),
        # pdb
        "set trace": Text("pdb.set_trace()"),
        "break point": Text("breakpoint()"),

        # Test/dummy variables
        "example list": Text("l = [1, 2, 3, 4, 4, 5]"),

    }


def get_rule():
    return CustomPython, RuleDetails("Custom Python")
