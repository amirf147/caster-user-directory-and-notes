from dragonfly import ShortIntegerRef, Pause, Dictation

from castervoice.lib.actions import Key, Text

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

class MSWordCcrRule(MergeRule):
    pronunciation = "word c c r"

    mapping = {

        # Editing
        "format bold":
            R(Key("c-b")),
            
    }
def get_rule():
    details = RuleDetails(executable="winword",
                          title="Word",
                          ccrtype=CCRType.APP)
    return MSWordCcrRule, details
