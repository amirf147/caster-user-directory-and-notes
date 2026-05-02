from dragonfly import Function, Dictation, MappingRule, Pause, ShortIntegerRef, Choice

from castervoice.lib.actions import Key

from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content.util.text import text_to_clipboard
from caster_user_content import environment_variables as ev


class AntigravityRule(MappingRule):
    mapping = {
        # Chat Panel Initialization/Toggling
        "show chat": R(Key("c-l")),
        "hide right": R(Key("c-l/50:2")),
        "new chat": R(Key("cs-l")),
        "switch mode": R(Key("c-.")),
        "chat here": 
            R(Key("cs-l/50") + Text("@file:") + Pause("50") + Key("enter")),
        
        # Voice recording (No default keybinding found in Antigravity, so placeholder for now)
        # "start voice": R(Key("...")),

        # Agent Hunk / Edits Navigation
        "change over": R(Key("a-k")),
        "change under": R(Key("a-j")),
        "accept change": R(Key("a-enter")),
        "reject change": R(Key("sa-backspace")),

        # Custom Commands
        "generate commit prompt": R(
            Key("cs-backtick") + # Create new terminal instance
            Pause("50") + Function(text_to_clipboard, text=ev.POWERSHELL_COMMIT_PROMPT_BUILDER) +
            Pause("100") + Key("s-insert/30, enter/30, c-k, c-f4/30") + Key("cs-l/180, c-v")),

        "go <file>":
            R(Key("c-k, cs-e/5") + Text("%(file)s") + Pause("40") + Key("enter")),
    }
    extras = [
        ShortIntegerRef("n", 1, 101),
        Dictation("text"),
        Choice("file", ev.CASTER_FILE_NAMES),
    ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return AntigravityRule, RuleDetails(name="Antigravity",
                                      executable="antigravity",
                                      title="Antigravity")
