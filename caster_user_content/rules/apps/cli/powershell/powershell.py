from dragonfly import Function, Repeat, Choice, Dictation, MappingRule, Pause, ShortIntegerRef, Mimic

from castervoice.lib.actions import Key, Mouse

from castervoice.lib import navigation
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev

class PowershellRule(MappingRule):
    mapping = {
        "go <path>": R(Text("cd %(path)s") + Key("enter")),

        "dirrup": R(Text("cd ../ ; ls;") + Key("enter")),
        "dir home": R(Text("cd; ls;") + Key("enter")),

        # "pi twelve": R(Text("$p312 ")),
        "pi quit": R(Text("quit()") + Key("enter")),
        "pi exit": R(Text("exit()") + Key("enter")),

        # sqlite
        "see exit": R(Text(".exit") + Key("enter")),

        "wiper": R(Text("clear") + Key("enter")),

        # Redmine
        "start redmine": R(Mimic("go redmine") + Pause("50") + Text("bundle exec rails server -e production") + Key("enter")),

        "start screen copy": R(Mimic("go screen copy") + Pause("50") + Text("./scrcpy") + Key("enter")),

        "oh list": R(Text("ollama list") + Key("enter")),
        "oh serve": R(Text("ollama serve") + Key("enter")),
    }
    extras = [
        Choice("path", ev.PATHS),
    ]
    defaults = {
    }

def get_rule():
    return PowershellRule, RuleDetails(name="Powershell", executable="powershell")
