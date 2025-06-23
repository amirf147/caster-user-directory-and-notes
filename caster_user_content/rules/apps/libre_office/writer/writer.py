from dragonfly import Dictation, MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

class WriterRule(MappingRule):
    mapping = {
        "file new": R(Key("c-n")),
        "file open": R(Key("c-o")),
        "file custom retain": R(Key("cs-s")),
        "open recent": R(Key("a-f, u")),
        "file export pdf": R(Key("a-f, e, d")),
        
        # Styles
        "show styles": R(Key("a-y, y")),
        "apply title": R(Key("a-y, t")),
        "apply subtitle": R(Key("a-y, b")),

        # Format
        "insert bullet": # Requires user define key binding: "Bullets and Numbering"
            R(Key("s-f7")),
        "remove bullet": R(Key("s-f7, tab, s-r, enter")), # Requires user define key binding: "Bullets and Numbering"
        "bullets": # unordered list via drop-down menu because unreliable via keyboard shortcut
            R(Key("a-o, t, left, t, u")),
        "restart numbering": R(Key("a-o, t, left, t, r")),
        "cycle case": R(Key("s-f3")),
        "page style dialog": R(Key("as-p")),
        "lay align": R(Key("c-l")),
        "center align": R(Key("c-e")),
        "ray align": R(Key("c-r")),
        "justify align": R(Key("c-j")),

        # Insert
        "show bookmarks": R(Key("a-i, k")),
        
        # View
        "web view": R(Key("a-v, w")),
        "normal view": R(Key("a-v, n")),
        "zoom entire page": R(Key("a-v, z, e")),
        "zoom seventy five": R(Key("a-v, z, 7")),
        "zoom [page] width": R(Key("a-v, z, p")),
        "(show | hide) grid": R(Key("a-v, i:2, d")),
        "show paragraph": R(Key("c-f10")),

        # Edit
        "remove hyperlink": R(Key("cs-h")), # Requires user defined key binding: "Remove Hyperlink"
        "[insert] hyperlink": R(Key("c-k")),
        "paste special": R(Key("cs-v")),
        "unspark": R(Key("csa-v")),

        # Tools
        "hint tools": R(Key("a-t")),
        "keyboard shorts": R(Key("a-t, c:2, enter")),
        "key search": R(Key("a-t, c:2, enter, tab:6/50") + Text("%(text)s")),
        "show line numbers": R(Key("a-t, l, space, tab:5, 1, enter")),
        "remove line numbers": R(Key("a-t, l, space, enter")),
        "line numbers dialog": R(Key("a-t, l")),
        "show settings": R(Key("a-t, o")),

        # Table
        "insert table": R(Key("c-f12")),

        # Font
        # Requires user define key binding: "Font Color" (second one)
        "font color": R(Key("cs-c, space, tab:2")),
        "font black": R(Key("cs-c, space, left:120, enter, tab, enter")),
        "font red": R(Key("cs-c, space, tab:2, down:6, right:4, enter, tab, enter")),
        "font dialog": R(Key("a-o, h")),
        "text increase <n>": R(Key("a-o, h, tab:3, down:%(n)d, enter")), # Increases font size
        "text decrease <n>": R(Key("a-o, h, tab:3, up:%(n)d, enter")), # Decreases font size


        # File
        "template manager": R(Key("a-f, m:2")),
        
    }
    extras = [
        ShortIntegerRef("n", 1, 10),
        Dictation("text"),
        ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return WriterRule, RuleDetails(name="Writer Rule",
                                    executable="soffice",
                                    title="LibreOffice Writer")
