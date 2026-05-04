from dragonfly import Function, Dictation, MappingRule, Pause, ShortIntegerRef, Choice, Mimic

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
        

        # Agent Hunk / Edits Navigation
        "change over": R(Key("a-k")),
        "change under": R(Key("a-j")),
        "accept change": R(Key("a-enter")),
        "reject change": R(Key("sa-backspace")),

        # Custom Commands
        # "generate commit prompt": R(
        #     Key("cs-backtick") + # Create new terminal instance
        #     Pause("50") + Function(text_to_clipboard, text=ev.POWERSHELL_COMMIT_PROMPT_BUILDER) +
        #     Pause("100") + Key("s-insert/30, enter/30, c-k, c-f4/30") + Key("cs-l/180, c-v")),
        # "generate commit prompt": R(
        #     Function(text_to_clipboard, text=ev.COMMIT_PROMPT_ANTIGRAVITY) + Key("cs-l/50, c-v")),

        # First stages changes and opens stage, then inputs /commit into agent chat window to get commit message.
        "generate commit message": R(Key("c-g, c-s/50, c-g, cs-s/50, cs-l/100") + Text("/commit") + Pause("100") + Key("enter/100:2")),

        "go <file>":
            R(Key("c-k, cs-e/5") + Text("%(file)s") + Pause("40") + Key("enter")),

        "voice chat": R(Key("c-l/50, tab:4/50") + Mimic("caster sleep") + Key("enter")),
        "new voice chat": R(Key("cs-l/50, tab:4/50") + Mimic("caster sleep") + Key("enter")),

        "agent manager": R(Key("c-e")),
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
