# This rule is for quickly opening files for editing, WIP

from dragonfly import MappingRule, Pause, Function, Dictation, Mimic, Mouse, Repeat, IntegerRef, ShortIntegerRef, Choice
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib import utilities, navigation
from castervoice.rules.core.navigation_rules import navigation_support
from datetime import datetime, timedelta

from caster_user_content import environment_variables as ev
from caster_user_content.util import switch_application

class EditorCommandsRule(MappingRule):
    pronunciation = "editor commands"
    mapping = {

        # TODO: Update the file path data structure to include the full path to the file
        "edit <file_name>": R(Key("w-r/50") + Text(f"windsurf {ev.CASTER_USER_DIRECTORY}\\caster_user_content\\%(file_name)s")),
    }
    extras = [
        Choice("file_name", ev.CASTER_FILE_NAMES),
    ]
    defaults = {}

def get_rule():
    details = RuleDetails(name="Editor Commands")
    return EditorCommandsRule, details
