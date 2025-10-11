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
        "zoom out [<n40>]": R(Key("control:down") + Mouse("wheeldown:%(n40)d") + Key("control:up")),
        "zoom in [<n40>]": R(Key("control:down") + Mouse("wheelup:%(n40)d") + Key("control:up")),
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

        # Transform
        "rake [<n500>]": R(Key("c-right:%(n500)d")), # Expands the width of the selected element
        "lake [<n500>]": R(Key("c-left:%(n500)d")), # Contracts the width of the selected element
        "stretch [<n500>]": R(Key("c-down:%(n500)d")), # Expands the height of the selected element
        "squeeze [<n500>]": R(Key("c-up:%(n500)d")), # Contracts the height of the selected element

        # Cursor
        "mode pan | mope": R(Key("space:down") + Mouse("left:down")),
        "mode not | maze": R(Key("space:up") + Mouse("left:up")),

        # Plugins
        "plug <plugin>": R(Key("c-p/30") + Text("%(plugin)s") + Pause("30") + Key("enter")),

        # Arrangement
        "layer under": R(Key("c-[")),
        "layer over": R(Key("c-]")),

        # Component
        "create component": R(Key("ca-k")),

    }
    extras = [
        ShortIntegerRef("n40", 1, 41),
        ShortIntegerRef("n500", 1, 501),
        Choice("plugin", {
            "colors": "coolors",
            "icons": "flaticon",
            "images": "unsplash",
            "able": "able friction",
        })
    ]
    defaults = {"n40": 1, "n500": 1}


def get_rule():
    return FigmaRule, RuleDetails(name="figma", executable="Figma")
