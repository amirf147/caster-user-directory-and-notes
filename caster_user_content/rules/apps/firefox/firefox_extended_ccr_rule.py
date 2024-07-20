from dragonfly import ShortIntegerRef, Pause, Dictation

from castervoice.lib.actions import Key, Text

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

class FirefoxCcrRule(MergeRule):
    pronunciation = "custom fire fox ccr"

    mapping = {
        "focus":
            R(Key("f6/3")),
        "copy address":
            R(Key("a-d/5, c-c"))
    }
def get_rule():
    details = RuleDetails(executable="firefox",
                          title="Firefox",
                          ccrtype=CCRType.APP)
    return FirefoxCcrRule, details
