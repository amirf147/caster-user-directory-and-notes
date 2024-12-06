from dragonfly import Repeat, Dictation, MappingRule, ShortIntegerRef, Choice

from castervoice.lib.actions import Key

from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class ExcelRule(MappingRule):
    mapping = {
        "file open": R(Key("c-o")),
        "hint home": R(Key("a-h")),
        
        # Zooming
        # "zoom in [<n>]":
        #     R(Key("a-w/50, q/3, tab:2, up:%(n)d, enter")),
        # "zoom out [<n>]":
        #     R(Key("a-w/50, q/3, tab:2, down:%(n)d, enter")),
        "zoom reset":
            R(Key("a-w/50, j")),
        "zoom dialogue":
            R(Key("a-w/50, q")),

    }
    extras = [
        ShortIntegerRef("n", 1, 10),
        Dictation("text"),
        ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return ExcelRule, RuleDetails(name="Excel Rule",
                                  executable="EXCEL")
