from dragonfly import MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class VLCRule(MappingRule):
    pronunciation = "media player"
    mapping = {
        "speed up [<n>]": R(Key("rbracket:%(n)d")),
        "slow down [<n>]": R(Key("lbracket:%(n)d")),
        "file open" : R(Key("c-o")),
        "folder open" : R(Key("c-f")),

    }
    extras = [
        ShortIntegerRef("n", 1, 1001)
    ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return VLCRule, RuleDetails(name="media player", executable="vlc")