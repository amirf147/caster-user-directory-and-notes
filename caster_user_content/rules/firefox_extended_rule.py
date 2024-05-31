from dragonfly import Repeat, Pause, Function, Choice, MappingRule, IntegerRef

from castervoice.lib.actions import Key, Mouse, Text

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from castervoice.lib import github_automation
from castervoice.lib.temporary import Store, Retrieve

class FirefoxExtendedRule(MappingRule):
    pronunciation = "extended fire fox"
    mapping = {
        "page <n>":
            R(Key("c-%(n)d")),
    }
    extras = [
        IntegerRef("n", 1, 10),
    ]
    defaults = {
        "n": 1
    }

def get_rule():
    return FirefoxExtendedRule, RuleDetails(name="fire fox extended", executable="firefox")
