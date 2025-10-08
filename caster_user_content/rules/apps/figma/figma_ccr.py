from castervoice.lib.actions import Key

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R


class FigmaCCR(MergeRule):
    pronunciation = "figma c c r"
    mapping = {

        "format bold | bowley": R(Key("c-b")),

    }
    extras = [
    ]
    defaults = {
    }

def get_rule():
    details = RuleDetails(executable="Figma",
                          title="Figma",
                          ccrtype=CCRType.APP)
    return FigmaCCR, details
