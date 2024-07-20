from dragonfly import MappingRule, ShortIntegerRef, Repeat, Pause
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key

class YoutubeRule(MappingRule):
    pronunciation = "youtube rule"
    mapping = {
        # TODO: Not working, fix this when I have time
        "speed up [<n>]":
            R(Key("escape/8, escape") +
              Pause("100") + Key("i/3") +
              Key("colon:%(n)d")),
        "slow down [<n>]":
            R(Key("escape/8, escape") +
              Pause("100") + Key("i/3") +
              Key("semicolon:%(n)d")),
    }
    extras = [
        ShortIntegerRef("n", 1, 9),
    ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return YoutubeRule, RuleDetails(name="youtube rule", title="youtube")
