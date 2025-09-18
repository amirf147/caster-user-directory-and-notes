from dragonfly import MappingRule, ShortIntegerRef, Mouse

from castervoice.lib.actions import Key

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class FigmaRule(MappingRule):
    pronunciation = "figma"
    mapping = {
        "[show] keyboard shorts": R(Key("cs-?")),
        "show ui": R(Key("c-\\")),
        "commander": R(Key("c-k")),
        "reopen tab": R(Key("cs-t")),
        "zoom out [<n>]": R(Key("control:down") + Mouse("wheeldown:%(n)d") + Key("control:up")),
        "zoom in [<n>]": R(Key("control:down") + Mouse("wheelup:%(n)d") + Key("control:up")),
        "zoom fit": R(Key("s-1")),
        "zoom (select | selection)": R(Key("s-2")),
        "zoom one hundred": R(Key("c-0")),

        # Tools
        "move tool": R(Key("v")),
        "text tool": R(Key("t")),
        # "framer": R(Key("f")),
        # "color picker mode": R(Key("i")),
        
        # View
        "show layers": R(Key("a-1")),
        "show assets": R(Key("a-2")),
        "show (libraries | library)": R(Key("a-3")),

        # Edit
        "duplicate": R(Key("c-d")),

        # Cursor
        "mode pan | mope": R(Key("space:down")),
        "mode not | maze": R(Key("space:up, alt:up")),

    }
    extras = [
        ShortIntegerRef("n", 1, 41),
    ]
    defaults = {"n": 1}


def get_rule():
    return FigmaRule, RuleDetails(name="figma", executable="Figma")
