from dragonfly import IntegerRef, Choice

from castervoice.lib.actions import Key, Text

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev

class WriterCCR(MergeRule):
    pronunciation = "writer c c r"
    mapping = {

        # Navigating to specific lines
        "liner <n_off_by_one>": R(Key("c-pgup, down:%(n_off_by_one)d")),

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
        Choice("n_off_by_one", {
            "one": 0,
            "two": 1,
            "three": 2,
            "four": 3,
            "five": 4,
            "six": 5,
            "seven": 6,
            "eight": 7,
            "nine": 8,
            "ten": 9,
            "eleven": 10,
            "twelve": 11,
            "thirteen": 12,
            "fourteen": 13,
            "fifteen": 14,
            "sixteen": 15,
            "seventeen": 16,
            "eighteen": 17,
            "nineteen": 18,
            "twenty": 19,
            "twenty one": 20,
            "twenty two": 21,
            "twenty three": 22,
            "twenty four": 23,
            "twenty five": 24,
            "twenty six": 25,
            "twenty seven": 26,
            "twenty eight": 27,
            "twenty nine": 28,
            "thirty": 30,
            "thirty one": 31,
            "thirty two": 32,
            "thirty three": 33,
            "thirty four": 34,
            "thirty five": 35,
            "thirty six": 36,
            "thirty seven": 37,
            "thirty eight": 38,
            "thirty nine": 39,
            "forty": 40,
            "forty one": 41,
            "forty two": 42,
            "forty three": 43,
            "forty four": 44,
            "forty five": 45,
            "forty six": 46,
            "forty seven": 47,
            "forty eight": 48,
            "forty nine": 49,
            "fifty": 50,
        }),
        Choice("text", ev.INSERTABLE_TEXT),
    ]
    defaults = {
    }

def get_rule():
    details = RuleDetails(executable="soffice",
                          title="LibreOffice Writer",
                          ccrtype=CCRType.APP)
    return WriterCCR, details
