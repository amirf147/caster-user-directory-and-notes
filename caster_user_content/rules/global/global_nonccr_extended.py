from dragonfly import MappingRule, IntegerRef
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R

class GlobalNonCCRExtendedRule(MappingRule):
    pronunciation = "global extended"
    mapping = {
        # Window Switching
        "switch <n>":
            R(Key("w-%(n)d/3")),
        "switch minus [<n>]":
            R(Key("w-t/3, up:%(n)d, enter")),
        
        # Window Manipulation
        "window move":
            R(Key("a-space/5, m")),
        "window resize right":
            R(Key("a-space/5, s/3, right")),
        "window resize left":
            R(Key("a-space/5, s/3, left")),
        "window resize up":
            R(Key("a-space/5, s/3, up")),
        "window resize down":
            R(Key("a-space/5, s/3, down")),

        "volume output":
            R(Key("w-b/3, up:3, enter/9")),

        "focus taskbar": R(Key("w-t")),

    }
    extras = [
        IntegerRef("n", 1, 10),
    ]
    defaults = {
        "n": 1
    }

def get_rule():
    details = RuleDetails(name="Global Non CCR Extended")
    return GlobalNonCCRExtendedRule, details
