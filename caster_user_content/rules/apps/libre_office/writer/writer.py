from dragonfly import Repeat, Dictation, MappingRule, ShortIntegerRef, Choice, Repetition, Function, IntegerRef

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
        "apply title": R(Key("a-y, t")),
        "apply subtitle": R(Key("a-y, b")),

        # Format
        "insert bullet": # Requires user define key binding: "Bullets and Numbering"
            R(Key("s-f10")),
        "bullets": # unordered list via drop-down menu because unreliable via keyboard shortcut
            R(Key("a-o, t, left, t, u")),
        "cycle case": R(Key("s-f3")),
        "page style dialog": R(Key("as-p")),

        # Insert
        "show bookmarks": R(Key("a-i, k")),
        
        # View
        "web view": R(Key("a-v, w")),
        "normal view": R(Key("a-v, n")),
        "zoom entire page": R(Key("a-v, z, e")),
        "zoom seventy five": R(Key("a-v, z, 7")),
        "(show | hide) grid": R(Key("a-v, i:2, d")),

        # Edit
        # Requires user defined key binding: "Remove Hyperlink"
        "remove hyperlink": R(Key("cs-h")),

        # Tools
        "customize dialogue": R(Key("a-t, c:2, enter")),
        "show line numbers": R(Key("a-t, l, space, tab:5, 1, enter")),
        "remove line numbers": R(Key("a-t, l, space, enter")),
        "line numbers dialog": R(Key("a-t, l")),

        # Font
        # Requires user define key binding: "Font Color" (second one)
        "font color": R(Key("cs-c, space, tab:2")),
        "font black": R(Key("cs-c, space, left:120, enter, tab, enter")),
        "font red": R(Key("cs-c, space, tab:2, down:6, right:4, enter, tab, enter")),
        
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
