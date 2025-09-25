from dragonfly import Function, Dictation, MappingRule, Pause, ShortIntegerRef

from castervoice.lib.actions import Key

from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content.util.text import text_to_clipboard
from caster_user_content import environment_variables as ev


class WindsurfRule(MappingRule):
    mapping = {
        # Cascade Chat Initialization/Toggling
        "show chat": R(Key("c-l")),
        "hide right": R(Key("c-l/50:2")),
        "new chat": R(Key("cs-l")),
        "switch mode": R(Key("c-.")),
        "chat here": # Opens a new chat with the last focused file
            R(Key("cs-l/50") + Text("@file:") + Pause("50") + Key("enter")),
        "edit here": R(Key("ca-k")), # Windsurf (fast) edit
        "stop gen": R(Key("ca-c")),
        "change over": R(Key("a-k")),
        "change under": R(Key("a-j")),
        "accept change": R(Key("a-enter")),
        "reject change": R(Key("sa-backspace")),
        "reject that": R(Key("c-k, c-backspace")), # Rejecting Windsurf (fast) proposed changes
        "accept all": R(Key("c-enter")),

        # Cascade Chat Context
        "file <text>": R(Text("@file:%(text)s", pause=0.0)),
        "directory <text>": R(Text("@directory:%(text)s", pause=0.0)),

        "generate commit prompt": R(
            Key("cs-backtick") + # Create new terminal instance
            Pause("50") + Function(text_to_clipboard, text=ev.POWERSHELL_COMMIT_PROMPT_BUILDER) +
            Pause("100") + Key("s-insert/30, enter/30, c-k, c-f4/30") + Key("cs-l/180, c-v")),

        # I thought these were supposed to totally stop the autocomplete feature but they don't
        # In fact, they seemingly do nothing
        "snooze auto": R(Key("c-k, c-z")), # windsurf.snoozeAutocomplete
        "unsnooze auto": R(Key("c-k, cs-z")), # windsurf.cancelSnoozeAutocomplete
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
