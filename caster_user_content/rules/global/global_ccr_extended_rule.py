from dragonfly import ShortIntegerRef, Pause, Dictation, Mouse, Choice

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.const import CCRType

from caster_user_content import environment_variables as ev

class GlobalCCRExtendedRule(MergeRule):
    pronunciation = "global ccr extended"

    mapping = {
        "name flash": R(Key("f2")),
        "go back [<n>]": R(Key("a-left:%(n)d")),
        "scratch [<n101>]": R(Key("c-backspace:%(n101)d")),
        "dear [<n101>]": R(Key("c-del:%(n101)d")),
        # "rash": R(Key("s-end")),
        # "lash": R(Key("s-home")),
        "win key <query>": R(Key("win") + Pause("30") + Text("%(query)s", pause=0.0)),
        
        # adding an empty line above or below the cursor
        "blank above [<n101>]": R(Key("home, enter, up:%(n101)d")),
        "blank below [<n101>]": R(Key("end, enter:%(n101)d")),

        "click": R(Mouse("[500, 262], left")),
        "clack": R(Mouse("[1500, 262], left")),
        
        "zick one": R(Mouse("[192, 199], left"), rdescript="Click sextant 1"),
        "zick two": R(Mouse("[923, 268], left"), rdescript="Click sextant 2"),
        "zick three": R(Mouse("[1540, 218], left"), rdescript="Click sextant 3"),
        "zick six": R(Mouse("[1542, 820], left"), rdescript="Click bottom right of screen"),
        "zick five": R(Mouse("[772, 756], left"), rdescript="Click sextant 5"),
        "alley": R(Key("c-a")),

        # "shtep <n>": R(Text("Step %(n)s: ")),
        # "ie": R(Text("i.e. ")),
        # "e g": R(Text("e.g., ", pause=0.0)),
        # "etc": R(Text(", etc. ", pause=0.0)),

        "eco": R(Text(" = ", pause=0.0)),
        "plooz": R(Text(" + ", pause=0.0)),
        "meece": R(Text(" - ", pause=0.0)),
        "dot t x t": R(Text(".txt", pause=0.0)),
        
        # Experimenting with continuing dictation and/or formatting text after custom word
        # "v s codium": R(Text(" VSCodium ", pause=0.0) + Function(textformat.master_format_text))
        "v s codium [<query>]": R(Text(" VSCodium %(query)s", pause=0.0)),

        # Finnish characters
        "a dots": R(Key("alt:down, numpad1, numpad3, numpad2, alt:up"), rdescript="Insert Finnish letter ä"),
        "o dots": R(Key("alt:down, numpad1, numpad4, numpad8, alt:up"), rdescript="Insert Finnish letter ö"),

        "insert <text>": R(Text("%(text)s")),
    }
    extras = [
        ShortIntegerRef("n", 1, 10),
        ShortIntegerRef("n101", 1, 101),
        Dictation("query"),
        Choice("text", ev.INSERTABLE_TEXT),
    ]
    defaults = {
        "n": 1,
        "n101": 1,
        "query": "",
    }

def get_rule():
    details = RuleDetails(ccrtype=CCRType.GLOBAL)
    return GlobalCCRExtendedRule, details
