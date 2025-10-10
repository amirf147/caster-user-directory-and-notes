from dragonfly import IntegerRef

from castervoice.lib.actions import Key, Text

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

class MSWordCcrRule(MergeRule):
    pronunciation = "word c c r"

    mapping = {

        "(apply heading) | header <n3>": R(Key("ac-%(n3)d")),
        
        # Editing
        "format bold | bowley":
            R(Key("c-b")),
        "format italic":
            R(Key("c-i")),
        "color reset":
            R(Key("a-h/3, f, c, a")),
        "color red":
            R(Key("a-h/3, f, c, up:4, home, enter")),
        
        # Find tab of Find and Replace dialog
        "etsype": R(Key("c-h/5, s-tab, left")),
    }
    extras = [
        IntegerRef("n3", 1, 4),
    ]

def get_rule():
    details = RuleDetails(executable="winword",
                          title="Word",
                          ccrtype=CCRType.APP)
    return MSWordCcrRule, details
