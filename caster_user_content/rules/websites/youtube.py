from dragonfly import MappingRule, ShortIntegerRef, Repeat
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

class YoutubeRule(MappingRule):
    pronunciation = "youtube rule"
    mapping = {
        "speed up [<n>]":
            R(Key("colon"))*Repeat(extra="n"),
        "slow down [<n>]":
            R(Key("semicolon"))*Repeat(extra="n"),
    }
    extras = [
        ShortIntegerRef("n", 1, 9),
    ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return YoutubeRule, RuleDetails(name="youtube rule", title="youtube")
