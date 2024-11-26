from dragonfly import Pause, Dictation, Choice

from castervoice.lib.actions import Text, Key
from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R


class GlobalProgramming(MergeRule):

    mapping = {

        "<formatted_operator>": R(Key("%(formatted_operator)s")),

    }
    extras = [
        Choice(
            "formatted_operator", {
                "eco": "space, equals, space",
                "meese": "space, minus, space",
                "plooz": "space, plus, space",
            }
        )]
    defaults = {}


def get_rule():
    return GlobalProgramming, RuleDetails(ccrtype=CCRType.GLOBAL)
