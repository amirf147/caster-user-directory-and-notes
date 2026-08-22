"""
Google Meet Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

from dragonfly import Dictation, MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class GoogleMeetRule(MappingRule):
    pronunciation = "google meet"

    mapping = {
        "show chat": R(Key("ca-c")),
        "toggle mic": R(Key("c-d")),
    }
    extras = [
        ShortIntegerRef("n", 1, 100),
        Dictation("dictation"),
    ]
    defaults = {"n": 1}


def get_rule():
    return GoogleMeetRule, RuleDetails(name="google meet", executable="firefox", title="Meet")
