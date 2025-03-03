from dragonfly import Function, Repeat, Choice, Dictation, MappingRule, Pause, ShortIntegerRef

from castervoice.lib.actions import Key, Mouse

from castervoice.lib import navigation
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class WindsurfRule(MappingRule):
    mapping = {
        # Cascade Chat
        "show chat": R(Key("c-l")),
        "hide right": R(Key("c-l:2")),
        "new chat": R(Key("cs-l")),
    }
    extras = [
        ShortIntegerRef("n", 1, 101),
        Dictation("text"),
    ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return WindsurfRule, RuleDetails(name="Windsurf",
                                      executable="windsurf",
                                      title="Windsurf")
