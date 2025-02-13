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
        "hide (alerts | notifications)": R(Key("a-a")),
        "show f p s": R(Key("a-i")),

        # "swipe": R(Mouse("(0.5, 0.5), left:down/100, (0.1, 0.5), left:up")),
        "swipe": R(Mouse("(0.9, 0.5), left:down") + Pause("20") + Mouse("<-300, 0>") + Pause("20") + Mouse("left:up")),
        "lipe": R(Mouse("(0.1, 0.5), left:down") + Pause("20") + Mouse("<300, 0>") + Pause("20") + Mouse("left:up")),

        # Swiping up
        # Added multiple steps of movement with pauses to slow down the swipe
        "swee": R(Mouse("(0.5, 0.9), left:down") + Pause("30") +
                  Mouse("<0, -100>") + Pause("5") +
                  Mouse("<0, -100>") + Pause("5") +
                  Mouse("<0, -100>") + Pause("5") +
                  Mouse("<0, -100>") + Pause("5") +
                  Mouse("<0, -100>") + Pause("5") +
                  Mouse("<0, -100>") + Pause("5") +
                  Mouse("<0, -100>") + Pause("5") +
                  Mouse("<0, -100>") + Pause("5") +
                  Pause("30") + Mouse("left:up")),
    }
    extras = [
    ]
    defaults = {
    }

def get_rule():
    return ScreenCopyRule, RuleDetails(name="ScreenCopy",
                                      executable="scrcpy",
                                      title=ev.SCRCPY_TITLE)
