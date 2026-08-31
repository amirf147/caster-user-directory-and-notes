"""
Antigravity IDE CCR Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

from dragonfly import Dictation
from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule


class AntigravityIDECCRRule(MergeRule):
    pronunciation = "antigravity i d e c c r"

    mapping = {}
    extras = [
        Dictation("text"),
    ]


def get_rule():
    details = RuleDetails(executable="Antigravity IDE", title="Antigravity IDE", ccrtype=CCRType.APP)
    return AntigravityIDECCRRule, details
