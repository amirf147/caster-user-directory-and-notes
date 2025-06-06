from dragonfly import Dictation, IntegerRef, Choice

from castervoice.lib.actions import Key, Text

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev

class WriterCCR(MergeRule):
    pronunciation = "writer c c r"
    mapping = {
        # Editing
        "format bold": R(Key("c-b")),
        "format italic": R(Key("c-i")),
        "format underline": R(Key("c-u")),
        "format super": R(Key("cs-p")),
        "format sub": R(Key("cs-b")),
        "norse": R(Key("c-m")), # Removes all formatting

        # Styles
        "apply heading <n3>": R(Key("c-%(n3)d")),
        "apply normal": R(Key("c-0")),

        # "color reset":
        #     R(Key("a-h/3, f, c, a")),
        "ruge": # Changes the font color to red via the character dialog
            R(Key("a-o, h, enter, tab, home, down, tab, end, left, enter, tab, enter")),
        
        # # Find tab of Find and Replace dialog
        # "etsype": R(Key("c-h/5, s-tab, left")),

        "insert <text>": R(Text("%(text)s")),
    }
    extras = [
        IntegerRef("n3", 1, 4),
        Choice("text", ev.INSERTABLE_TEXT),
    ]
    defaults = {
    }

def get_rule():
    details = RuleDetails(executable="soffice",
                          title="LibreOffice Writer",
                          ccrtype=CCRType.APP)
    return WriterCCR, details
