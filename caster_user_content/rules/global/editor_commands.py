# This rule is for quickly opening files for editing, WIP

from dragonfly import MappingRule, Pause, Function, Dictation, Mimic, Mouse, Repeat, IntegerRef, ShortIntegerRef, Choice
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib import utilities, navigation
from castervoice.rules.core.navigation_rules import navigation_support
from datetime import datetime, timedelta

from caster_user_content import environment_variables as ev


class EditorCommandsRule(MappingRule):
    pronunciation = "editor commands"
    mapping = {
        "edit <file_path>": R(Key("w-r/50") + Text(f"windsurf %(file_path)s") + Pause("50") + Key("enter")),
    }
    extras = [
        Choice("file_path", ev.CASTER_FILE_PATHS),
    ]
    defaults = {}

def get_rule():
    details = RuleDetails(name="Editor Commands")
    return EditorCommandsRule, details
