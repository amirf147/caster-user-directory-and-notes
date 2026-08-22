"""
Custom Git Bash CCR Rule

Base terminal executables and merge structure derived from Caster (castervoice/rules/apps/terminal/gitbash.py)
Copyright (c) 2015-2026 Caster Contributors

Personal customizations:
Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: LGPL-3.0-or-later
"""

from dragonfly import Text

from castervoice.lib.actions import Key

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R


class CustomGitbashRule(MergeRule):
    pronunciation = "custom gitbash"

    mapping = {
        "menu": R(Key("a-space")),
        "dirrup": R(Text("cd ../ ; ls;") + Key("enter")),
    }


_executables = [
    "\\sh.exe",
    "\\bash.exe",
    "\\cmd.exe",
    "\\mintty.exe",
    "\\powershell.exe",
    "idea",
    "idea64",
    "studio64",
    "pycharm",
]


def get_rule():
    details = RuleDetails(executable=_executables, ccrtype=CCRType.APP)
    return CustomGitbashRule, details
