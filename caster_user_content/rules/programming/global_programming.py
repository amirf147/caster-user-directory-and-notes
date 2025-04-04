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
                "double eco": "space, equals, equals, space",
                "double meese": "minus:2, space",
                "double plooz": "plus:2, space",
                "pink": "space, plus, equals, space",
                "naughty": "space, !, equals, space",
                "pleak": "space, plus, equals, space",
                "arrow": "space, minus, >, space",
                "mink": "space, minus, equals, space",
                "grand": "space, >, space",
                "lands": "space, <, space",
                "greek": "space, >, =, space",
                "leak": "space, <, =, space",
                "coach": "end, comma",
                "cole": "end, colon, space",
            }
        )]
    defaults = {}


def get_rule():
    return GlobalProgramming, RuleDetails(ccrtype=CCRType.GLOBAL)
