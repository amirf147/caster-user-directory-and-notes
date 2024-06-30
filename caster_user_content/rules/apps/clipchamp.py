from dragonfly import MappingRule, IntegerRef, Choice
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

class ClipchampRule(MappingRule):
    pronunciation = "clip champ"
    mapping = {
        "keyboard shortcuts":
            R(Key("c-slash")),
        "zoom in <n>":
            R(Key("c-equal:%(n)d")),
        "zoom out <n>":
            R(Key("c-minus:%(n)d")),
        "import media":
            R(Key("ca-i/3, enter")),
        "properties":
            R(Key("a-2:3, tab")),
    }
    extras = [
        IntegerRef("n", 1, 9),
    ]


def get_rule():
    return ClipchampRule, RuleDetails(name="clipchamp", executable="clipchamp")
