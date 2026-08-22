"""
Vim Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

from dragonfly import MappingRule

from castervoice.lib.actions import Key

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class VimRule(MappingRule):
    mapping = {
        "vim quit": R(Key("escape, colon, q, enter")),
        "vim retain": R(Key("escape, colon, w, enter")),
        "vim quit no save": R(Key("escape, colon, q, !, enter")),
    }
    extras = []
    defaults = {}


def get_rule():
    return VimRule, RuleDetails(name="Vim", executable="WindowsTerminal")
