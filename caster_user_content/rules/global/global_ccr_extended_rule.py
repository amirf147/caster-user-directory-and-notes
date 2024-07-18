from dragonfly import ShortIntegerRef, Pause, Function, Dictation

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.const import CCRType
from castervoice.lib import utilities


class GlobalCCRExtendedRule(MergeRule):

    pronunciation = "global ccr extended"

    mapping = {
        "flash": R(Key("f2")),
        "go back [<n>]": R(Key("a-left:%(n)d")),
        "system tray": R(Key("w-b")),
        "scratch [<n101>]": R(Key("c-backspace:%(n101)d")),
        "dear [<n101>]": R(Key("c-del:%(n101)d")),
        "win key <query>": R(Key("win") + Pause("30") + Text("%(query)s")),
        
        # adding an empty line above or below the cursor
        "blank above [<n101>]": R(Key("home, enter, up:%(n101)d")),
        "blank below [<n101>]": R(Key("end, enter:%(n101)d")),

    }
    extras = [
        ShortIntegerRef("n", 1, 10),
        ShortIntegerRef("n101", 1, 101),
        Dictation("query"),
    ]
    defaults = {
        "n": 1,
        "n101": 1
    }

def get_rule():
    details = RuleDetails(ccrtype=CCRType.GLOBAL)
    return GlobalCCRExtendedRule, details
