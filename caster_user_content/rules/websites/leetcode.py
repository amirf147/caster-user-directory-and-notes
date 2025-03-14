from dragonfly import MappingRule, ShortIntegerRef, Repeat, Pause
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

class LeetCodeRule(MappingRule):
    pronunciation = "leite code"
    mapping = {
        "leet run": R(Key("c-'")),
        "leet submit": R(Key("c-enter")),
        "expand panel": R(Key("c-]")),
        "next question": R(Key("a-right")),
        "previous question": R(Key("a-left")),
        "pane maximize": R(Key("a-equal")),
    }

def get_rule():
    return LeetCodeRule, RuleDetails(name="LeetCode Rule", title="LeetCode")
