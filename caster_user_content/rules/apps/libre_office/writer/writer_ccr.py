from dragonfly import ShortIntegerRef, Pause, Dictation, IntegerRef

from castervoice.lib.actions import Key, Text

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

class WriterCCR(MergeRule):
    pronunciation = "writer c c r"
    mapping = {
        # Editing
        "format bold": R(Key("c-b")),
        "format italic": R(Key("c-i")),
        "format underline": R(Key("c-u")),

        # Styles
        "apply heading <n3>": R(Key("c-%(n3)d")),
        "apply normal": R(Key("c-0")),

        # "color reset":
        #     R(Key("a-h/3, f, c, a")),
        # "color red":
        #     R(Key("a-h/3, f, c, up:4, home, enter")),
        
        # # Find tab of Find and Replace dialog
        # "etsype": R(Key("c-h/5, s-tab, left")),
    }
    extras = [
        IntegerRef("n3", 1, 4),
    ]
def get_rule():
    details = RuleDetails(executable="soffice",
                          title="LibreOffice Writer",
                          ccrtype=CCRType.APP)
    return WriterCCR, details
