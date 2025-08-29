from dragonfly import MappingRule, Pause, Function, Dictation, Mimic, Mouse, Repeat, IntegerRef, ShortIntegerRef, Choice
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib import utilities, navigation
from castervoice.rules.core.navigation_rules import navigation_support
from datetime import datetime, timedelta

from caster_user_content import environment_variables as ev
from caster_user_content.util import switch_application

import os

class GlobalNonCCRExtendedRule(MappingRule):
    pronunciation = "global extended"
    mapping = {

        # Text insertion command - works in any text field
        "texter <text>": R(Text("%(text)s")),

        "show [me] calendar":
            R(Key("w-b, up/3, enter")),
        "show sounds": # Opens the Windows Sounds utility via run dialog
            R(Key("w-r/50") + Text("mmsys.cpl") + Key("enter")),
        "show mixer": # Opens the Windows Sound Mixer via run dialog
            R(Key("w-r/50") + Text("sndvol.exe") + Key("enter")),
        "show network connections": # Opens the Windows Network Connections utility via run dialog
            R(Key("w-r/50") + Text("ncpa.cpl") + Key("enter")),
        "show m s info": # Opens the Microsoft Information utility via run dialog
            R(Key("w-r/50") + Text("msinfo32.exe") + Key("enter")),
        "show device manager": # Opens the Device Manager utility via run dialog
            R(Key("w-r/50") + Text("devmgmt.msc") + Key("enter")),
        "show m s config": # Opens the Microsoft Configuration utility via run dialog
            R(Key("w-r/50") + Text("msconfig") + Key("enter")),
        "show display settings": # Opens the Display Settings utility via run dialog
            R(Key("w-r/50") + Text("ms-settings:display") + Key("enter")),

        "begin dictation": # Activate windows dictation mode and sleeps caster windows
            R(Key("w-h") + Mimic("caster sleep")),
        
        # Hunt and Peck activation
        "[show] hints":
            R(Key("a-semicolon")),

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

        "focus taskbar": R(Key("w-t")),

        # Placing mouse cursor in one of 4 quadrants on the screen
        "zone one":
            R(Mouse("[500, 262]")),
        "zone two":
            R(Mouse("[1500, 262]")),
        "zone three":
            R(Mouse("[500, 800]")),
        "zone four":
            R(Mouse("[1500, 800]")),
        "zone five":
            R(Mouse("[950, 500]")),
        "zone six":
            R(Mouse("[2351, 1525]")),
        "zone seven":
            R(Mouse("[2906, 1567]")),
 
        # TODO: Make this work
        # "pool": R(Function(navigation.wheel_scroll, direction="down", nnavi500=9)),
        # "cool": R(Function(navigation.wheel_scroll, direction="up", nnavi500=9)),

        # Moving mouse cursor and then scrolling in one utterance
        # "zone one scree <direction> [<nnavi500>]":
        #     R(Mouse("[500, 262]") + Pause("30") + Function(navigation.wheel_scroll)),
        # "zone two scree <direction> [<nnavi500>]":
        #     R(Mouse("[1500, 262]") + Pause("30") + Function(navigation.wheel_scroll)),
        # "zone six scree <direction> [<nnavi500>]":
        #     R(Mouse("[2351, 1525]") + Pause("30") + Function(navigation.wheel_scroll)),
        # "zone seven scree <direction> [<nnavi500>]":
        #     R(Mouse("[2906, 1567]") + Pause("30") + Function(navigation.wheel_scroll)),

        

        # Mirroring a window to all workspaces for my secondary monitor
        "mirror space window":
            R(Key("w-tab/150") + Key("tab/3")*Repeat(3) + Key("s-f10/40, down/40, down/2, down/2, enter, escape")),
        
        # Combining the previous two words into one word
        "last join":
            R(Key("c-left, backspace, c-right")),

        # LLM Chatbot prompts
        "grammar check clipboard":
            R(Text("How is the grammar here: ") + Key("c-v")),
        "width adjust":
            R(Text("I want to be able to copy and paste this into a cell in a \
spreadsheet. Can you make the following text 40 characters \
wide and put it into a code pen so it is easy for me to \
copy and paste it: ") + Key("c-v")),

        "fancy zones": R(Key("ws-`")),
        "fancy <n0>":
            R(Key("wca-%(n0)d")),

        # For Libre Office Writer because apparently this dialog is not recognized as being
        # in the same context as the Writer rule context
        "apply page margins":
            R(Text("0.35") + Key("tab") +
               Text("0.1") + Key("tab") +
               Text("0.1") + Key("tab") +
               Text("0.1") + Key("enter, left, enter")),

        # Triple click actions
        "bling [<nnavi500>]": # Copies the line under the mouse cursor
            R(Mouse("left") + Mouse("left") + Mouse("left") + Function(
                navigation.stoosh_keep_clipboard)),
        "cling": # Cuts the line under the mouse cursor
            R(Mouse("left")*Repeat(3) + Key("c-x")),

        # Double click actions
        "slacks [<n_off_by_one>]": # Cuts the word under the mouse cursor and n words after that
            R(Mouse("left")*Repeat(2) + Key("cs-right:%(n_off_by_one)d/30") + Key("c-x")),
        "slubs [<n_off_by_one>]": # Selects the word under the mouse cursor and n words after that
            R(Mouse("left")*Repeat(2) + Key("cs-right:%(n_off_by_one)d/30")),
        "garbs [<n_off_by_one>]": # Copies the word under the mouse cursor and n words after that
            R(Mouse("left:2") + Key("cs-right:%(n_off_by_one)d/30") + Key("c-c")),
        # Date Insertion
        "insert date":
            R(Text(datetime.now().strftime("%d-%m-%Y"))),
        "insert future date":
            R(Text((datetime.now() + timedelta(days=21)).strftime("%d-%m-%Y"))),

        "bring oh <program>": R(Key("win/30") + Text("%(program)s", pause=0.0) + Pause("30") + Key("enter")),
        "start screen copy": R(
            # After pressing alt-tab they pause needs to be separate otherwise it keeps the key combination pressed down
            Key("w-r/30") + Text(f"\"{ev.PATHS['screen copy']}/scrcpy\"", pause=0.0) +
            Key("enter/150, a-tab") + Pause("50") + Key("ws-right/50, w-right:3, a-tab")),
        
        "kil enable via cam": R(Key("w-r/30") + Text(f"{os.getenv('USERPROFILE')}\\Desktop\\kill cam.lnk", pause=0.0) + Key("enter")),

        "computer lock screen": # Locks the computer via the start menu power button
            R(Key("win/50, tab/30:3/30, right/30, enter/30, enter")),
    }

    extras = [
        Choice("text", ev.INSERTABLE_TEXT),
        Dictation("prompt"),
        IntegerRef("n", 1, 10),
        IntegerRef("n0", 0, 10),
        Choice("program", ev.PROGRAM_NAMES),
        Choice("n_off_by_one", {
            "one": 0,
            "two": 1,
            "three": 2,
            "four": 3,
            "five": 4,
            "six": 5,
            "seven": 6,
            "eight": 7,
            "nine": 8,
            "ten": 9,
            "eleven": 10,
            "twelve": 11,
            "thirteen": 12,
            "fourteen": 13,
            "fifteen": 14,
            "sixteen": 15,
            "seventeen": 16,
            "eighteen": 17,
            "nineteen": 18,
            "twenty": 19,
        }),
        navigation_support.get_direction_choice("direction"),
        ShortIntegerRef("nnavi500", 1, 500),


    ]
    defaults = {
        "n": 1,
        "n0": 0,
        "nnavi500": 1,
        "n_off_by_one": 0,
    }

def get_rule():
    details = RuleDetails(name="Global Non CCR Extended")
    return GlobalNonCCRExtendedRule, details
