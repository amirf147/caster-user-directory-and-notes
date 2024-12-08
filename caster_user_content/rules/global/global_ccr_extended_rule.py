from dragonfly import ShortIntegerRef, Pause, Function, Dictation, Mouse

from castervoice.lib import textformat
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.const import CCRType
from castervoice.lib import utilities


class GlobalCCRExtendedRule(MergeRule):

    pronunciation = "global ccr extended"

    mapping = {
        "name flash": R(Key("f2")),
        "go back [<n>]": R(Key("a-left:%(n)d")),
        "scratch [<n101>]": R(Key("c-backspace:%(n101)d")),
        "dear [<n101>]": R(Key("c-del:%(n101)d")),
        "rash": R(Key("s-end")),
        "lash": R(Key("s-home")),
        "win key <query>": R(Key("win") + Pause("30") + Text("%(query)s")),
        
        # adding an empty line above or below the cursor
        "blank above [<n101>]": R(Key("home, enter, up:%(n101)d")),
        "blank below [<n101>]": R(Key("end, enter:%(n101)d")),

        "click":
            R(Mouse("[500, 262], left")),
        "clack":
            R(Mouse("[1500, 262], left")),
        "zick": R(Mouse("[500, 800], left")),

        "alley": R(Key("c-a")),

        # "shtep <n>": R(Text("Step %(n)s: ")),
        # "ie": R(Text("i.e. ")),
        "e g": R(Text("e.g., ")),
        "etc": R(Text(", etc. ")),

        "eco": R(Text(" = ")),
        "plooz": R(Text(" + ")),
        "meece": R(Text(" - ")),
        
        # Experimenting with continuing dictation and/or formatting text after custom word
        # "v s codium": R(Text(" VSCodium ") + Function(textformat.master_format_text))
        "v s codium [<query>]": R(Text(" VSCodium %(query)s")),
    }
    extras = [
        ShortIntegerRef("n", 1, 10),
        ShortIntegerRef("n101", 1, 101),
        Dictation("query"),
    ]
    defaults = {
        "n": 1,
        "n101": 1,
        "query": "",
    }

def get_rule():
    details = RuleDetails(ccrtype=CCRType.GLOBAL)
    return GlobalCCRExtendedRule, details
