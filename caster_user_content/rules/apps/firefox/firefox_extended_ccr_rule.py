from dragonfly import ShortIntegerRef, Pause, Dictation, Choice

from castervoice.lib.actions import Key, Text

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev

class FirefoxCcrRule(MergeRule):
    pronunciation = "custom fire fox ccr"

    mapping = {
        "switch focus":
            R(Key("f6/3")),
        "copy address":
            R(Key("a-d/5, c-c, escape, f6, tab/5, tab")),
        "netspell":
            R(Key("a-d/5")),
        # "insert <text>": R(Text("%(text)s")), # Not working for some reason
    }
    extras = [
        # Choice("text", ev.INSERTABLE_TEXT),
    ]
    defaults = {
    }

def get_rule():
    details = RuleDetails(executable=["firefox", "waterfox"],
                          title=["Firefox", "Waterfox"],
                          ccrtype=CCRType.APP)
    return FirefoxCcrRule, details
