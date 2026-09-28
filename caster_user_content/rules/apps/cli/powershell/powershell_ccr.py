"""
Powershell Ccr Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

from dragonfly import Choice

from castervoice.lib.actions import Key, Text

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev
from caster_user_content.util.powershell_context import is_powershell_active


class PowershellCCRRule(MergeRule):
    pronunciation = "power shell c c r"

    mapping = {
        # Executables/Commands
        "<exe>": R(Text("%(exe)s") + Key("space")),
        "rename":  # Renaming a file or folder
        R(Text("Rename-Item -Path  -NewName") + Key("left:9")),
        # "mark mode": R(Key("a-space, e, k")),
        # SQL
        # "ghost": R(Key("G, O, enter")),
    }
    extras = [
        Choice("exe", ev.EXECUTABLES),
    ]


def get_rule():
    details = RuleDetails(
        name="PowerShell CCR",
        executable=[
            "powershell",
            "pwsh",
            "windowsterminal",
            "wt",
            "code",
            "antigravity",
            "antigravity ide",
            "cursor",
            "windsurf",
            "vscodium",
        ],
        function_context=is_powershell_active,
        ccrtype=CCRType.APP,
    )
    return PowershellCCRRule, details
