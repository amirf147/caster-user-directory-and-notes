from dragonfly import Function, Repeat, Choice, Dictation, MappingRule, Pause, ShortIntegerRef, Mimic

from castervoice.lib.actions import Key, Mouse

from castervoice.lib import navigation
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev
from caster_user_content.rules.apps.cli import cli_support

class WindowsTerminalRule(MappingRule):
    mapping = {
        "show settings": R(Key("c-comma")),
        "close shell": R(Key("cs-w")),
        "shell over [<n>]": R(Key("c-tab:%(n)d")),
        "shell under [<n>]": R(Key("cs-tab:%(n)d")),
        "new power": R(Key("cs-1")),
        "new (command | c m d | command prompt)": R(Key("cs-2")),
        "new git bash": R(Key("cs-6")),
        "commander": R(Key("cs-p")),
        "mark mode": R(Key("cs-m")),
    }
    extras = [
        ShortIntegerRef("n", 1, 11),
    ]
    defaults = {
        "n": 1,
    }
def get_rule():
    return WindowsTerminalRule, RuleDetails(name="Windows Terminal", executable="WindowsTerminal")
