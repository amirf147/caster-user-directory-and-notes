from dragonfly import Repeat, Dictation, MappingRule, ShortIntegerRef, Choice, Repetition, Function, IntegerRef

from castervoice.lib.actions import Key
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

class WriterRule(MappingRule):
    mapping = {
        "file open": R(Key("c-o")),
        "file custom retain": R(Key("cs-s")),
        "open recent": R(Key("a-f, u")),
        
        "apply heading <n3>": R(Key("c-%(n3)d")),
        "apply normal": R(Key("c-0")),
        
        # View
        "web view": R(Key("a-v, w")),
        "normal view": R(Key("a-v, n")),
        
    }
    extras = [
        IntegerRef("n3", 1, 4),
        ShortIntegerRef("n", 1, 10),
        Dictation("text"),
        ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return WriterRule, RuleDetails(name="Writer Rule",
                                    executable="soffice",
                                    title="LibreOffice Writer")
