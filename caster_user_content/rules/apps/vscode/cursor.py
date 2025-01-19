from dragonfly import Function, Repeat, Choice, Dictation, MappingRule, Pause, ShortIntegerRef

from castervoice.lib.actions import Key, Mouse

from castervoice.lib import navigation
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CursorRule(MappingRule):
    mapping = {
        "hide right": # Requires user defined key binding (View: Close AI Sidebar)
            R(Key("c-m, a-w")),
    }
    extras = [
    ]
    defaults = {}

def get_rule():
    return CursorRule, RuleDetails(name="Cursor",
                                      executable="cursor",
                                      title="Cursor")
