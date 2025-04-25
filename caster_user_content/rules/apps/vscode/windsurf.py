from dragonfly import Function, Dictation, MappingRule, Pause, ShortIntegerRef

from castervoice.lib.actions import Key

from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


from caster_user_content.util import switch_application
from caster_user_content.util.text import text_to_clipboard
from caster_user_content import environment_variables as ev


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
            Pause("30") + Function(text_to_clipboard, text=ev.POWERSHELL_COMMIT_PROMPT_BUILDER) +
            Pause("20") + Key("c-c/2") + Text("cd " + ev.PATHS["caster user"]) + Key("enter") + Key("c-v/3,enter") + Pause("200") +
            Key("a-tab") + Pause("100") + Key("cs-l/150, c-v/3")),
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
