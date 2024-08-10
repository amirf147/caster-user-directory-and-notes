from dragonfly import MappingRule, IntegerRef, Pause, Function
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib import utilities

class GlobalNonCCRExtendedRule(MappingRule):
    pronunciation = "global extended"
    mapping = {
        # Window Switching
        "drip <n>":
            R(Key("w-%(n)d/3")),
        "drip minus [<n>]":
            R(Key("w-t/3, up:%(n)d, enter")),

        # hunt-and-peck activation
        "show hints":
            R(Key("a-semicolon")),

        "open snipping tool":
            R(Key("ws-s")),

        # Window Manipulation
        "window move":
            R(Key("a-space/5, m")),
        "window resize right":
            R(Key("a-space/5, s/3, right")),
        "window resize left":
            R(Key("a-space/5, s/3, left")),
        "window resize up":
            R(Key("a-space/5, s/3, up")),
        "window resize down":
            R(Key("a-space/5, s/3, down")),

        "volume output":
            R(Key("w-b/3, up:3, enter") +
              Pause("40") + Key("tab, enter") +
              Pause("40") + Key("tab")),
        "volume output earphones":
            R(Key("w-b/3, up:3, enter") +
              Pause("40") + Key("tab, enter") +
              Pause("40") + Key("tab/3, home") +
              Pause("40") + Key("down, enter") +
              Pause("40") + Key("a-tab")),
        "volume output TV":
            R(Key("w-b/3, up:3, enter") +
              Pause("40") + Key("tab, enter") +
              Pause("40") + Key("tab/3, end") +
              Pause("40") + Key("a-tab")),

        "focus taskbar": R(Key("w-t")),

        # window snapping into 1 of 4 quadrants
        "snap window one":
            R(Function(utilities.maximize_window) +
            Pause("80") + Key("w-left") +
            Pause("40") + Key("w-left") +
            Pause("40") + Key("escape") +
            Pause("80") + Key("w-up")),
        "snap window two":
            R(Function(utilities.maximize_window) +
            Pause("80") + Key("w-right") +
            Pause("40") + Key("w-right") +
            Pause("40") + Key("escape") +
            Pause("80") + Key("w-up")),
        "snap window three":
            R(Key("w-up") +
            Pause("80") + Key("w-left") +
            Pause("40") + Key("w-left") +
            Pause("40") + Key("escape") +
            Pause("80") + Key("w-down")),
        "snap window four":
            R(Key("w-up") +
            Pause("80") + Key("w-right") +
            Pause("40") + Key("w-right") +
            Pause("40") + Key("escape") +
            Pause("80") + Key("w-down")),

        # Putting computer to sleep via start menu
        "computer go to sleep":
            R(Key("win") +
            Pause("80") + Key("tab") + Pause("30") + Key("down") +
            Pause("30") + Key("down:2") + Pause("30") + Key("down") +
            Pause("30") + Key("down:2") + Pause("30") + Key("down") +
            Pause("30") + Key("enter") + Pause("30") + Key("enter")),

    }
    extras = [
        IntegerRef("n", 1, 10),
    ]
    defaults = {
        "n": 1
    }

def get_rule():
    details = RuleDetails(name="Global Non CCR Extended")
    return GlobalNonCCRExtendedRule, details
