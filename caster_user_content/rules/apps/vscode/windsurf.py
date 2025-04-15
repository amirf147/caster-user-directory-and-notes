from dragonfly import Function, Repeat, Choice, Dictation, MappingRule, Pause, ShortIntegerRef, Mimic

from castervoice.lib.actions import Key, Mouse

from castervoice.lib import navigation
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


from caster_user_content.util import switch_application

class WindsurfRule(MappingRule):
    mapping = {
        # Cascade Chat Initialization/Toggling
        "show chat": R(Key("c-l")),
        "hide right": R(Key("c-l:2")),
        "new chat": R(Key("cs-l")),
        "switch mode": R(Key("c-.")),

        # Cascade Chat Context
        "file <text>": R(Text("@file:%(text)s", pause=0.0)),
        "directory <text>": R(Text("@directory:%(text)s", pause=0.0)),

        "generate commit prompt": R(
                Function(switch_application.title, window_title="Windows PowerShell") +
                Pause("30") + Mimic("generate commit prompt") + Pause("200") +
                Key("a-tab") + Pause("100") + Key("cs-l/3, c-v/3, enter")),

        
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
