from dragonfly import Function, Repeat, Choice, Dictation, MappingRule, Pause, ShortIntegerRef

from castervoice.lib.actions import Key, Mouse

from castervoice.lib import navigation
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev


class ScreenCopyRule(MappingRule):
    mapping = {
        "go home": R(Key("a-h")),
        "go back": R(Key("a-b")),
        "show menu": R(Key("a-m")),
        "switcher": R(Key("a-s")),
        "hit power": R(Key("a-p")),
        "phone screen off": R(Key("a-o")),
        "phone screen on": R(Key("as-o")),
        "show (alerts | notifications)": R(Key("a-n")),
        "show quick settings": R(Key("alt:down, n/20, n, alt:up")),
        "hide (alerts | notifications)": R(Key("a-a")),
        "show f p s": R(Key("a-i")),

        # Swiping actions
        "swipe": # Right to left
            R(Mouse("(0.8, 0.5)/20, left:down/20, <-300, 0>/20, left:up")),
        "lipe": # Left to right
            R(Mouse("(0.1, 0.5)/20, left:down/20, <300, 0>/20, left:up")),
        "swee": # Bottom to top
            R(Mouse("(0.5, 0.85)/20, left:down/20, <0, -800>/20, left:up")),
        "swoo": # Top to bottom
            R(Mouse("(0.5, 0.2)/20, left:down/20, <0, 800>/20, left:up")),
    }
    extras = [
    ]
    defaults = {
    }

def get_rule():
    return ScreenCopyRule, RuleDetails(name="ScreenCopy",
                                      executable="scrcpy",
                                      title=ev.SCRCPY_TITLE)
