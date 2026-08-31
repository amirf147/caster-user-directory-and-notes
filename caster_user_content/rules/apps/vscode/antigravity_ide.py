"""
Antigravity IDE Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

from dragonfly import Choice, Dictation, MappingRule, Mimic, Pause, ShortIntegerRef
from castervoice.lib.actions import Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev


class AntigravityIDERule(MappingRule):
    pronunciation = "antigravity i d e"
    mapping = {
        # Chat Panel Initialization/Toggling
        "show chat": R(Key("c-l")),
        "hide right": R(Key("c-l/50:2")),
        "new chat": R(Key("cs-l")),
        "switch mode": R(Key("c-.")),
        "chat here": R(Key("cs-l/50") + Text("@file:") + Pause("50") + Key("enter")),
        "voice chat": R(Key("c-l/50, tab:4/50") + Mimic("caster sleep") + Key("enter")),
        "new voice chat": R(Key("cs-l/50, tab:4/50") + Mimic("caster sleep") + Key("enter")),
        "voice chat here": R(Key("tab:4/50") + Mimic("caster sleep") + Key("enter")),
        "agent settings": R(Key("c-comma")),
        "agent manager": R(Key("c-e")),
        # Agent Hunk / Edits Navigation
        "change over": R(Key("a-k")),
        "change under": R(Key("a-j")),
        "accept change": R(Key("a-enter")),
        "reject change": R(Key("sa-backspace")),
        "debug console": R(Key("cs-y")),
        # Custom Commands
        # First stages changes and opens stage, then inputs /commit into agent chat window to get commit message.
        # new chat session
        "generate commit message": R(
            Key("c-g, c-s/50, c-g, cs-s/50, cs-l/100") + Text("/commit") + Pause("100") + Key("enter/100:2")
        ),
        # In open chat window
        "generate commit message here": R(
            Key("c-g, c-s/50, c-g, cs-s/50, c-l/100") + Text("/commit") + Pause("100") + Key("enter/100:2")
        ),
        "go <file>": R(Key("c-k, cs-e/5") + Text("%(file)s") + Pause("40") + Key("enter")),
        "open <text>": R(Key("c-p/5") + Text("%(text)s")),  # uses search files by name
        "hide panel": R(Key("c-j")),  # Hides bottom the panel
        "show problems": R(Key("cs-m")),  # Shows the problems panel
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
    return AntigravityIDERule, RuleDetails(
        name="Antigravity IDE",
        executable="Antigravity IDE",
        title="Antigravity IDE",
    )
