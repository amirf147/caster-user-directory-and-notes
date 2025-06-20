# This rule is for quickly opening files for editing, WIP

from dragonfly import MappingRule, Pause, Function, Dictation, Mimic, Mouse, Repeat, IntegerRef, ShortIntegerRef, Choice
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib import utilities, navigation
from castervoice.rules.core.navigation_rules import navigation_support
from datetime import datetime, timedelta

from caster_user_content import environment_variables as ev
from caster_user_content.util import variable_tracker


def go_to_variable(env_var): # Currently this is for just the environment variables file but maybe we can generalize it in the future
    """Jump to the line where a variable is defined"""
    env_var = env_var.upper()
    line_number = str(variable_tracker.var_tracker.get_line_number(env_var))
    if line_number:
        Key("w-r/50").execute()
        Text(f"windsurf {ev.ENVIRONMENT_FILE}").execute()
        Pause("30").execute()
        Key("enter").execute()
        Pause("150").execute()
        print(f"Jumping to line {line_number} for variable {env_var}")
        Key("cas-g/50").execute()
        Text(line_number).execute()
        Key("enter").execute()
    else:
        print(f"Variable {env_var} not found")

class EditorCommandsRule(MappingRule):
    pronunciation = "editor commands"
    mapping = {
        "edit <file_path>": R(Key("w-r/50") + Text(f"windsurf %(file_path)s") + Pause("50") + Key("enter")),
        "modify <env_var>": Function(go_to_variable), # Opens the environment variables file and jumps to the specified variable for faster editing
    }
    extras = [
        Choice("file_path", ev.CASTER_FILE_PATHS),
        Choice("env_var", ev.ENVIRONMENT_VARIABLES),
    ]
    defaults = {}

def get_rule():
    details = RuleDetails(name="Editor Commands")
    return EditorCommandsRule, details
