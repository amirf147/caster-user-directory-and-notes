from dragonfly import ShortIntegerRef, Pause, Dictation

from castervoice.lib.actions import Key, Text

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

class FirefoxCcrRule(MergeRule):
    pronunciation = "custom fire fox ccr"

    mapping = {
        "toggle focus":
            R(Key("f6/3")),
        "netzer <query>":
            R(Key("a-d/5") + Text("%(query)s") + Key("enter")),
        "hister <query>":
            R(Key("a-d/5") + Text("^%(query)s")),
    }

    extras = [
        Dictation("query"),
    ]

def get_rule():
    details = RuleDetails(executable="firefox",
                          title="Firefox",
                          ccrtype=CCRType.APP)
    return FirefoxCcrRule, details
