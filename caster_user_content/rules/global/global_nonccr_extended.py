from dragonfly import MappingRule, IntegerRef, Pause, Function, Choice, Mouse, Repeat, ShortIntegerRef, Mimic
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib import utilities, navigation
from castervoice.rules.core.navigation_rules import navigation_support

from caster_user_content import environment_variables as ev

class GlobalNonCCRExtendedRule(MappingRule):
    pronunciation = "global extended"
    mapping = {

        "show me calendar":
            R(Key("w-b, up/3, enter")),

        # Hunt and Peck activation
        "show hints":
            R(Key("a-semicolon")),

        "insert <text>": R(Text("%(text)s")),

        "open snipping tool":
            R(Key("ws-s")),
        "full screenshot":
            R(Key("ws-s") + Pause("160") + Key("tab/3, right:3, enter")),
        "window screenshot":
            R(Key("ws-s") + Pause("160") + Key("tab/3, right:2, enter")),

        # Window Manipulation
        "window move":
            R(Key("a-space/5, m")),

        "window middle":
            R(Key("a-space/5, m") +
             Mimic("squat") +
              Pause("30") +
               Mimic("curse", "left", "three seventy five") +
                Pause("50") +
                 Mimic("bench")),

        "window resize right":
            R(Key("a-space/5, s/3, right")),
        "window resize left":
            R(Key("a-space/5, s/3, left")),
        "window resize up":
            R(Key("a-space/5, s/3, up")),
        "window resize down":
            R(Key("a-space/5, s/3, down")),

        "volume output":
            R(Key("w-b/3, up:2, enter") +
              Pause("40") + Key("tab, enter") +
              Pause("40") + Key("tab")),
        "volume output earphones":
            R(Key("w-b/3, up:2, enter") +
              Pause("40") + Key("tab, enter") +
              Pause("40") + Key("tab/3, home") +
              Pause("40") + Key("down, enter") +
              Pause("40") + Key("a-tab")),
        "volume output TV":
            R(Key("w-b/3, up:2, enter") +
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

        # Placing mouse cursor in one of 4 quadrants on the screen
        "cork one":
            R(Mouse("[500, 262]")),
        "cork two":
            R(Mouse("[1500, 262]")),
        "cork three":
            R(Mouse("[500, 800]")),
        "cork four":
            R(Mouse("[1500, 800]")),
        "cork five":
            R(Mouse("[950, 500]")),
        "cork six":
            R(Mouse("[2351, 1525]")),

        # Moving mouse cursor and then scrolling in one utterance
        "cork one scree <direction> [<nnavi500>]":
            R(Mouse("[500, 262]") + Pause("30") + Function(navigation.wheel_scroll)),
        "cork two scree <direction> [<nnavi500>]":
            R(Mouse("[1500, 262]") + Pause("30") + Function(navigation.wheel_scroll)),
        "cork six scree <direction> [<nnavi500>]":
            R(Mouse("[2351, 1525]") + Pause("30") + Function(navigation.wheel_scroll)),

        # Mirroring a window to all workspaces for my secondary monitor
        "mirror space window":
            R(Key("tab/3")*Repeat(3) + Key("s-f10/4, down/2, down/2, down/2, enter")),
        
        # Combining the previous two words into one word
        "last join":
            R(Key("c-left, backspace, c-right")),

        # LLM Chatbot prompts
        "grammar check clipboard":
            R(Text("How is the grammar here: ") + Key("c-v")),
        "width adjust":
            R(Text("In a code pen, make this 40 characters wide: ") + Key("c-v")),
        
        "eco": R(Text(" = ")),
        "plooz": R(Text(" + ")),
    }

    extras = [
        IntegerRef("n", 1, 10),
        Choice("n_off_by_one", {
            "one": "0",
            "two": "1",
            "three": "2",
            "four": "3",
            "five": "4",
            "six": "5",
            "seven": "6",
            "eight": "7",
            "nine": "8",
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
        Choice("text", {
            "home address": ev.HOME_ADDRESS,
            "city state": ev.CITY_STATE,
            "zip code": ev.ZIP_CODE,
            "city": ev.CITY,
            "school": ev.SCHOOL,
            "phone": ev.PHONE,
            "employer": ev.EMPLOYER,
            "name": ev.NAME,
            "last name": ev.LAST_NAME,
            "email": ev.EMAIL,
            "line": "----------------------------------------",
        }),
        navigation_support.get_direction_choice("direction"),
        ShortIntegerRef("nnavi500", 1, 500),


    ]
    defaults = {
        "n": 1,
        "nnavi500": 1,
    }

def get_rule():
    details = RuleDetails(name="Global Non CCR Extended")
    return GlobalNonCCRExtendedRule, details
