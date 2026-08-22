"""
Window Switching Ccr Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

from dragonfly import Function, Mouse, ShortIntegerRef, Choice, Dictation

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.const import CCRType

from caster_user_content.util import app_switcher
from caster_user_content.environment_variables import WINDOWS_APP_ALIASES, WINDOW_ALIASES


def _switch_to_app(app_name, instance):
    app_switcher.switch_to_app(app_name, instance)


def _switch_to_alias(predefined_alias=None, dictated_alias=None):
    alias = predefined_alias or dictated_alias
    if alias:
        app_switcher.switch_to_alias(alias)


class WindowSwitchingCCRRule(MergeRule):
    pronunciation = "window switching c c r"

    mapping = {
        # Switching command
        "[switch [to]] <predefined_alias>": R(Function(_switch_to_alias) + Mouse("(0.5, 0.5)")),
        "switch [to] <dictated_alias>": R(Function(_switch_to_alias) + Mouse("(0.5, 0.5)")),
        "<app_name> [<instance>]": R(Function(_switch_to_app) + Mouse("(0.5, 0.5)")),
    }
    extras = [
        Choice("predefined_alias", {a: a for a in WINDOW_ALIASES}),
        Dictation("dictated_alias"),
        ShortIntegerRef("instance", 1, 10),
        Choice("app_name", WINDOWS_APP_ALIASES),
    ]
    defaults = {
        "instance": 1,
    }


def get_rule():
    details = RuleDetails(ccrtype=CCRType.GLOBAL)
    return WindowSwitchingCCRRule, details
