from dragonfly import MappingRule, IntegerRef, Choice
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

class FirefoxExtendedRule(MappingRule):
    pronunciation = "extended fire fox"
    mapping = {
        "page <n>":
            R(Key("c-%(n)d")),
        "page [last | nine | minus | minus one]":
            R(Key("c-9")),
        "page minus <n_off_by_one>":
            R(Key("c-9, c-pgup:%(n_off_by_one)s")),
        "show pages":
            R(Key("c-b/8, f1")), # workaround for when pressing just F1 doesn't work
        "hide left":
            R(Key("c-b:2")), # workaround for when pressing just F1 doesn't work
    }
    extras = [
        IntegerRef("n", 1, 9),
        Choice("n_off_by_one", {
            "two": "1",
            "three": "2",
            "four": "3",
            "five": "4",
            "six": "5",
            "seven": "6",
            "eight": "7",
            "nine": "8",
            "ten": "9",
        })
    ]

def get_rule():
    return FirefoxExtendedRule, RuleDetails(name="fire fox extended", executable="firefox")
