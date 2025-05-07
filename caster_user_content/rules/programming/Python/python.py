from dragonfly import MappingRule, Function, Choice, IntegerRef

from castervoice.lib.actions import Text, Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

def _random_number_list(length, element_magnitude):
    import random
    length = int(length)
    element_magnitude = int(element_magnitude)
    print(length, element_magnitude)
    list = str([random.randint(0, element_magnitude) for _ in range(length)])
    list = "l = " + list
    Text(list).execute()


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

        "random list [<length>] [<element_magnitude>]":
            Function(_random_number_list),
        
        "a var": R(Text("a = ")),
        "b var": R(Text("b = ")),
        "c var": R(Text("c = ")),
    }
    extras = [
        IntegerRef("length", 1, 21),
        Choice("element_magnitude", {
            "ten": 10,
            "hundred": 100,
        }),
    ]
    defaults = {
        "length": 5,
        "element_magnitude": 10,
    }

def get_rule():
    return CustomPython, RuleDetails("Custom Python")
