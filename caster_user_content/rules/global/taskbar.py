,from dragonfly import MappingRule, Choice, ShortIntegerRef
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R

class TaskbarRule(MappingRule):
    mapping = {
        # Switching applications via the taskbar
        "drip [<n9>]":
            R(Key("w-%(n9)d, enter")),
        "drip [<n_off_by_one_10_20>]":
            R(Key("w-t/3, down:%(n_off_by_one_10_20)s, enter")),
        "drip minus [<n20>]":
            R(Key("w-t/3, up:%(n20)d, enter")),
        
        # Opening/focusing system tray icons
        "open system <n_off_by_one_1_20>":
            R(Key("w-b/3, right:%(n_off_by_one_1_20)s, enter")),
        "go to system <n_off_by_one_1_20>":
            R(Key("w-b/3, right:%(n_off_by_one_1_20)s")),
    }
    extras = [
        Choice("n_off_by_one_10_20", {
            "ten": "9",
            "eleven": "10",
            "twelve": "11",
            "thirteen": "12",
            "fourteen": "13",
            "fifteen": "14",
            "sixteen": "15",
            "seventeen": "16",
            "eighteen": "17",
            "nineteen": "18",
            "twenty": "19",
        }),
        ShortIntegerRef("n9", 1, 10),
        ShortIntegerRef("n20", 1, 21),
        Choice("n_off_by_one_1_20", {
            "one": "0", "two": "1", "three": "2", "four": "3",
            "five": "4", "six": "5", "seven": "6", "eight": "7",
            "nine": "8", "ten": "9", "eleven": "10", "twelve": "11",
            "thirteen": "12", "fourteen": "13", "fifteen": "14", "sixteen": "15",
            "seventeen": "16", "eighteen": "17", "nineteen": "18", "twenty": "19",
        }),
    ]
    defaults = {
        "n9": 1,
        "n20": 1,
    }
def get_rule():
    details = RuleDetails(name="Taskbar")
    return TaskbarRule, details
