# -*- coding: utf-8 -*-
from dragonfly import Function, Mouse, List, ListRef, IntegerRef

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.const import CCRType

from caster_user_content import environment_variables as ev
from caster_user_content.util import switch_application


window_aliases = List("window_alias", ev.WINDOW_ALIASES)

# integer reference renamed to “instance” just for clarity
instance_ref = IntegerRef("instance", 1, 10)


class WindowSwitchingCCRRule(MergeRule):
    pronunciation = "window switching c c r"

    mapping = {
        # optional “switch/to”, required alias, optional instance number
        "[switch [to]] <window_alias> [<instance>]":
            # press Shift to break Windows’ foreground-lock, then call the
            # Python helper, finally click the middle of the screen so that the
            # newly-activated window receives focus.
            R(
                Key("shift")
                + Function(
                    # the helper to call
                    switch_application.switch_to_app_instance
                )
                + Mouse("(0.5, 0.5)")
            ),
    }

    extras = [
        ListRef("window_alias", window_aliases),
        instance_ref,
    ]

    # when the user omits the number, pass 1
    defaults = {
        "instance": 1,
    }


def get_rule():
    details = RuleDetails(ccrtype=CCRType.GLOBAL)
    return WindowSwitchingCCRRule, details