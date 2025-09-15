from dragonfly import MappingRule, ShortIntegerRef, Mouse

from castervoice.lib.actions import Key

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class FigmaRule(MappingRule):
    pronunciation = "figma"
    mapping = {
        "zoom out [<n>]": R(Key("control:down") + Mouse("wheeldown:%(n)d") + Key("control:up")),
        "zoom in [<n>]": R(Key("control:down") + Mouse("wheelup:%(n)d") + Key("control:up")),
    }
    extras = [
        ShortIntegerRef("n", 1, 41),
    ]
    defaults = {"n": 1}


def get_rule():
    return FigmaRule, RuleDetails(name="figma", executable="Figma")
