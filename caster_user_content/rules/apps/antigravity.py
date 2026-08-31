"""
Antigravity Standalone Desktop App Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

from dragonfly import MappingRule
from castervoice.lib.actions import Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class AntigravityAppRule(MappingRule):
    pronunciation = "antigravity"
    mapping = {
        "show chats": R(Key("c-b")),
        "hide right": R(Key("ca-b")),
    }


def get_rule():
    return AntigravityAppRule, RuleDetails(
        name="Antigravity Standalone",
        executable="Antigravity.exe",
    )
