"""
Antigravity Standalone Desktop App Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

from dragonfly import MappingRule, ShortIntegerRef, Choice
from castervoice.lib.actions import Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev


class AntigravityAppRule(MappingRule):
    pronunciation = "antigravity"
    mapping = {
        "(show chats) | (hide left)": R(Key("c-b")),
        "hide right": R(Key("ca-b")),
        "zoom in [<n>]": R(Key("c-equal:%(n)d")),
        "zoom out [<n>]": R(Key("c-minus:%(n)d")),
        "keyboard shorts": R(Key("c-?")),
        "drips": R(Key("c-k, enter")),
        # Navigating to projects
        "go <project>": R(Key("cs-k/30") + Text("%(project)s") + Key("enter")),
    }
    extras = [
        ShortIntegerRef("n", 1, 11),
        Choice("project", ev.ANTIGRAVITY_PROJECTS),
    ]
    defaults = {
        "n": 1,
    }


def get_rule():
    return AntigravityAppRule, RuleDetails(
        name="Antigravity Standalone",
        executable=["antigravity", "antigravity.exe"],
    )
