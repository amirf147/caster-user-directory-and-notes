from dragonfly import MappingRule, Choice, ShortIntegerRef
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Mouse
from castervoice.lib.merge.state.short import R

class TaskbarRule(MappingRule):
    mapping = {
        # Switching applications via the taskbar
        "drip ten":
            R(Key("w-t/3, down:9, enter/30") + Mouse("(0.5, 0.5)")),
        "drip [<off1_1_20>]":
            R(Key("w-t/3, down:%(off1_1_20)s, enter/30") + Mouse("(0.5, 0.5)")),
        "drip [<off1_10_20>]":
            R(Key("w-t/3, down:%(off1_10_20)s, enter/30") + Mouse("(0.5, 0.5)")),
        "drip minus [<off1_1_20>]":
            R(Key("w-t/3, end, up:%(off1_1_20)s, enter/30") + Mouse("(0.5, 0.5)")),
        
        # Opening/focusing system tray icons
        "open system <off1_1_20>":
            R(Key("w-b/3, right:%(off1_1_20)s/3, enter")),
        "psy system <off1_1_20>":
            R(Key("w-b/3, right:%(off1_1_20)s/5, s-f10")),
        "close system <off1_1_20>":
            R(Key("w-b/3, right:%(off1_1_20)s/3, s-f10/3, up, enter"),
             rdescript="Taskbar: 'close system <off1_1_20>' - Closes a program via the system tray icon"),
    }
    extras = [
        Choice("off1_10_20", {
            "ten": "9", "eleven": "10", "twelve": "11",
            "thirteen": "12", "fourteen": "13", "fifteen": "14",
            "sixteen": "15", "seventeen": "16", "eighteen": "17",
            "nineteen": "18", "twenty": "19",
        }),
        ShortIntegerRef("n9", 1, 10),
        ShortIntegerRef("n20", 1, 21),
        Choice("off1_1_20", {
            "one": "0", "two": "1", "three": "2", "four": "3",
            "five": "4", "six": "5", "seven": "6", "eight": "7",
            "nine": "8", "eleven": "10", "twelve": "11",
            "thirteen": "12", "fourteen": "13", "fifteen": "14", "sixteen": "15",
            "seventeen": "16", "eighteen": "17", "nineteen": "18", "twenty": "19",
        }),
    ]
    defaults = {
        "n9": 1,
        "n20": 1,
        "off1_1_20": "0",
    }
def get_rule():
    details = RuleDetails(name="Taskbar")
    return TaskbarRule, details
