"""
Copilot Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

from dragonfly import MappingRule
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails


class CopilotRule(MappingRule):
    mapping = {
        "focus compose [box]": R(Key("f1")),
    }


def get_rule():
    return CopilotRule, RuleDetails(name="copilot", title="copilot")
