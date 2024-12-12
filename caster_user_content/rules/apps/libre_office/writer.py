from dragonfly import Repeat, Dictation, MappingRule, ShortIntegerRef, Choice, Repetition, Function

from castervoice.lib.actions import Key
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

class WriterRule(MappingRule):
    mapping = {
        "file open": R(Key("c-o")),
        "open recent": R(Key("a-f, u")),
        
    }
    extras = [
        ShortIntegerRef("n", 1, 10),
        Dictation("text"),
        ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return WriterRule, RuleDetails(name="Writer Rule",
                                  title="LibreOffice Writer")
