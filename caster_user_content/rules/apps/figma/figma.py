from dragonfly import MappingRule, ShortIntegerRef, Mouse, Pause, Choice

from castervoice.lib.actions import Key, Text

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class FigmaRule(MappingRule):
    pronunciation = "figma"
    mapping = {
        "[show] keyboard shorts": R(Key("cs-?")),
        "(show | hide) ui": R(Key("c-\\")), # Shows/Hides all Figma UI elements
        "(show | hide) left": R(Key("cs-\\")), # Shows/Hides left panel
        
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
        "frame tool": R(Key("f")),
        "color picker": R(Key("i")),
        
        # View
        "show files": R(Key("a-1")),
        "show assets": R(Key("a-2/100, tab:3")), # focuses the assets after switching to the assets panel
        "show (libraries | library)": R(Key("a-3")),
        "show design": R(Key("a-8")),
        "show prototype": R(Key("a-9")),
        
        # Edit
        "duplicate": R(Key("c-d")),

        # Cursor
        "mode pan | mope": R(Key("space:down") + Mouse("left:down")),
        "mode not | maze": R(Key("space:up") + Mouse("left:up")),

        # Plugins
        "plug <plugin>": R(Key("c-p/30") + Text("%(plugin)s") + Pause("30") + Key("enter")),

        # Arrangement
        "layer under": R(Key("c-[")),
        "layer over": R(Key("c-]")),

    }
    extras = [
        ShortIntegerRef("n", 1, 41),
        Choice("plugin", {
            "colors": "coolors",
            "icons": "flaticon",
            "images": "unsplash",
        })
    ]
    defaults = {"n": 1}


def get_rule():
    return FigmaRule, RuleDetails(name="figma", executable="Figma")
