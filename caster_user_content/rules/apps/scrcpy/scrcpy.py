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
        "hide (alerts | notifications)": R(Key("a-a" )),
        "show f p s": R(Key("a-i")),
    }
    extras = [
    ]
    defaults = {
    }

def get_rule():
    return ScreenCopyRule, RuleDetails(name="ScreenCopy",
                                      executable="scrcpy",
                                      title=ev.SCRCPY_TITLE)
