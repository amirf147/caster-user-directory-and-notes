"""
Custom Windows Explorer CCR Rule

Derived from Caster IERule (castervoice/rules/apps/windows_os/explorer.py)
Copyright (c) 2015-2026 Caster Contributors

Personal customizations:
Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: LGPL-3.0-or-later
"""

from dragonfly import Dictation, ShortIntegerRef

from castervoice.lib.actions import Key, Text

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R
from castervoice.lib.const import CCRType
from castervoice.lib.merge.mergerule import MergeRule


class CustomIERule(MergeRule):
    pronunciation = "custom explorer rule"
    mapping = {
        "address bar": R(Key("a-d")),
        "new folder": R(Key("cs-n")),
        "new file": R(Key("a-f, w, t")),
        "(show | file | folder) properties": R(Key("a-enter")),
        "dirrup": R(Key("a-up")),
        "go back": R(Key("a-left")),
        "go forward": R(Key("a-right")),
        "search [<text>]": R(Key("a-d, tab:1") + Text("%(text)s")),
        "(navigation | nav | left) pane": R(Key("a-d, tab:2")),
        "(center pane | (file | folder) (pane | list))": R(Key("a-d, tab:3")),
        # for the sort command below,
        # once you've selected the relevant heading for sorting using the arrow keys, press enter
        "sort [headings]": R(Key("a-d, tab:4")),
    }
    extras = [
        Dictation("text"),
        ShortIntegerRef("n", 1, 1000),
    ]
    defaults = {"n": 1}


def get_rule():
    return CustomIERule, RuleDetails(executable="explorer", ccrtype=CCRType.APP)
