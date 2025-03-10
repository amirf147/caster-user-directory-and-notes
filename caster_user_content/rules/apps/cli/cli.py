from dragonfly import Function, Repeat, Choice, Dictation, MappingRule, Pause, ShortIntegerRef, Mimic

from castervoice.lib.actions import Key, Mouse

from castervoice.lib import navigation
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev
PYTHON_8 = ev.EXECUTABLES["pi eight"]
from caster_user_content.rules.apps.cli import cli_support

class CommandLineRule(MappingRule):
    mapping = {
        "go <path>": R(Text("cd %(path)s") + Key("enter")),

        "show settings": R(Key("c-comma")),
        "close tab": R(Key("cs-w")),

        "dirrup": R(Text("cd ../ ; ls;") + Key("enter")),
        "dir home": R(Text("cd; ls;") + Key("enter")),

        "pi twelve": R(Text("$p312 ")),
        "pi quit": R(Text("quit()") + Key("enter")),
        "pi exit": R(Text("exit()") + Key("enter")),

        # sqlite
        "see exit": R(Text(".exit") + Key("enter")),

        "wiper": R(Text("clear") + Key("enter")),

        # Redmine
        "start redmine": R(Mimic("go redmine") + Pause("50") + Text("bundle exec rails server -e production") + Key("enter")),

        "pi eight <python_command>": R(Text(PYTHON_8) + Text("%(python_command)s")), 
        
    }
    extras = [
        Choice("path", ev.PATHS),
        Choice("python_command", cli_support.PYTHON_COMMANDS),
    ]
    defaults = {
    }

_executables = [
    "WindowsTerminal",
    "cmd",
]
def get_rule():
    return CommandLineRule, RuleDetails(name="Command Line", executable=_executables)
