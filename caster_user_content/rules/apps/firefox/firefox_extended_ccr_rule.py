"""
Firefox Extended CCR Rule

Derived from Caster browser CCR patterns (castervoice/rules/apps/browser/)
Copyright (c) 2015-2026 Caster Contributors

Continuous browser search and navigation commands:
Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: LGPL-3.0-or-later
"""

from castervoice.lib.actions import Key

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R


class FirefoxCcrRule(MergeRule):
    pronunciation = "custom fire fox c c r"

    mapping = {
        "switch focus": R(Key("f6/3")),
        "copy address": R(Key("c-l/5, c-c, escape, f6, tab/5, tab")),
        # CCR versions of a focusing address so you can continue to type characters without pausing
        # Web search
        "netspell": R(Key("c-l/5")),
        "netspell tab": R(Key("c-t/50")),
        # History search
        "hispell": R(Key("c-l/20, ^")),
        "hispell tab": R(Key("c-t/50, ^")),
        # "insert <text>": R(Text("%(text)s")), # Not working for some reason
        "juice": R(Key("c-f/20")),  # for spelling into find dialog
    }
    extras = [
        # Choice("text", ev.INSERTABLE_TEXT),
    ]
    defaults = {}


def get_rule():
    details = RuleDetails(executable=["firefox", "waterfox"], title=["Firefox", "Waterfox"], ccrtype=CCRType.APP)
    return FirefoxCcrRule, details
