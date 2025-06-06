from dragonfly import Repeat, Dictation, MappingRule, ShortIntegerRef, Choice, Repetition, Function, Pause, Mimic

from castervoice.lib.actions import Key
from castervoice.rules.core.alphabet_rules import alphabet_support
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

def _select_cell(column_1, row_1):
    column_1 = column_1[0]
    Key("c-g").execute()
    Text("%(column_1)s%(row_1)s").execute({"column_1": column_1, "row_1": row_1})
    Key("enter").execute()

class CalcRule(MappingRule):
    mapping = {
        "file open": R(Key("c-o")),
        "open recent": R(Key("a-f, u")),
        
        # Copied over and modified from builtin Excel rule
        # Credit: Alex Boche 2019
        "fly <column_1> <row_1>":
            R(Function(_select_cell)),
        "select <column_1> <row_1> through <column_2> <row_2>":
            R(Key("c-g") + Text("%(column_1)s%(row_1)s:%(column_2)s%(row_2)s") +
                Key("enter")),
                
        "match above": R(Key("c-d")),
        "match below": R(Key("cs-\"")),

        # Zooming
        # "zoom in [<n>]":
        #     R(Key("a-w/50, q/3, tab:2, up:%(n)d, enter")),
        # "zoom out [<n>]":
        #     R(Key("a-w/50, q/3, tab:2, down:%(n)d, enter")),
        "zoom reset":
            R(Key("a-w/50, j")),
        "zoom dialogue":
            R(Key("a-w/50, q")),

        "insert date": R(Key("cs-d")), # Custom key binding: Insert Current Date
        "continue date": R(Key("c-d, cs-d")),

        # View
        "freeze first row": R(Key("a-v, c, r")),
        "freeze first column": R(Key("a-v, c, f")),
        "unfreeze": R(Key("a-v, e")),

        # Tools
        "customize dialog": R(Key("a-t, c")),
        "macro editor": R(Key("a-t, m:2, e")),
        
        # Hyperlinking
        "hyperlink": R(Key("c-k")),
        "link to file": R(Key("c-k, s-tab, home, down:2, tab:2, space")),
        "link to job posting": # Selects the most recently created job posting text file
            R(Key("c-k, s-tab, home, down:2, tab:2, space")),
            # Pause("300") +
              # Mimic("go job postings") + Key("space")),
              # Key("tab/3, right/3, enter/3, home, space")),
        
        # Home Tab
        "fit width": R(Key("a-o, m, o, enter")),
        "fit height": R(Key("a-o, w, o, enter")),
        

    }
    extras = [
        ShortIntegerRef("row_1", 1, 100),
        ShortIntegerRef("row_2", 1, 100),
        ShortIntegerRef("n", 1, 10),
        Dictation("text"),
        Repetition(Choice("alphabet1", alphabet_support.caster_alphabet()), min=1, max=2, name="column_1"),
        Repetition(Choice("alphabet2", alphabet_support.caster_alphabet()), min=1, max=2, name="column_2"),
        ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return CalcRule, RuleDetails(name="Calc Rule",
                                  title="LibreOffice Calc")
