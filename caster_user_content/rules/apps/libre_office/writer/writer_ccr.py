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
        "linda <n_off_by_one>": # First moves text cursor to the top of the page 
                                # then moves it down by <n_off_by_one>
            R(Key("c-pgup, down:%(n_off_by_one)d")),
        "liner <n_off_by_one>": # First moves text cursor to the top of the page 
                                # then moves it down by <n_off_by_one>
                                # then moves the cursor to the end of the line
            R(Key("c-pgup, down:%(n_off_by_one)d, end")),
        "linda previous <n_off_by_one>": # navigating line numbers of the previous page
            R(Key("a-pgup, down:%(n_off_by_one)d")),
        "linda next <n_off_by_one>": # navigating line numbers of the next page
            R(Key("a-pgdown, down:%(n_off_by_one)d")),
        "liner previous <n_off_by_one>": # navigating line numbers of the previous page
            R(Key("a-pgup, down:%(n_off_by_one)d, end")),
        "liner next <n_off_by_one>": # navigating line numbers of the next page
            R(Key("a-pgdown, down:%(n_off_by_one)d, end")),
            
        # Editing
        "format bold | bowley": R(Key("c-b")),
        "format italic": R(Key("c-i")),
        "format underline": R(Key("c-u")),
        "format super": R(Key("cs-p")),
        "format sub": R(Key("cs-b")),
        "norse": R(Key("c-m")), # Removes all formatting

        # Styles
        "(apply heading | header) <n6>": R(Key("c-%(n6)d")),
        "apply normal": R(Key("c-0")),

        # "color reset":
        #     R(Key("a-h/3, f, c, a")),
        "ruge": # Changes the font color to red via the character dialog
            R(Key("a-o, h, enter, tab, home, down, tab, end, left, enter, tab, enter")),
        "color reset": # Requires user defined key binding: "Font Color" (second one)
            R(Key("cs-c, space, s-tab:2, space, tab, enter")),
        
        # # Find tab of Find and Replace dialog
        # "etsype": R(Key("c-h/5, s-tab, left")),

        "insert <text>": R(Text("%(text)s")),
    }
    extras = [
        IntegerRef("n6", 1, 7),
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
            "thirty": 29,
            "thirty one": 30,
            "thirty two": 31,
            "thirty three": 32,
            "thirty four": 33,
            "thirty five": 34,
            "thirty six": 35,
            "thirty seven": 36,
            "thirty eight": 37,
            "thirty nine": 38,
            "forty": 39,
            "forty one": 40,
            "forty two": 41,
            "forty three": 42,
            "forty four": 43,
            "forty five": 44,
            "forty six": 45,
            "forty seven": 46,
            "forty eight": 47,
            "forty nine": 48,
            "fifty": 49,
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
