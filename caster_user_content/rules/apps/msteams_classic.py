from dragonfly import ShortIntegerRef 
from castervoice.lib.actions import Key, Text, Mouse
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R
from dragonfly import (AppContext, Choice, Dictation, Function, MappingRule,
                       Repeat)

class MSTeamsClassicRule(MappingRule):
    pronunciation = "teams classic"
    mapping = {
        # General
        "search":
            R(Key("c-e")),
        "keyboard shortcuts":
            R(Key("c-.")),
        "settings":
            R(Key("c-comma")),

        # Navigation
        "activity":
            R(Key("c-1")),
        "chat":
            R(Key("c-3")),
        "calendar":
            R(Key("c-4")),
        # "previous item [<nnavi10>]":
        #     R(Key("a-up"))*Repeat(extra="nnavi10"),
        # "next item [<nnavi10>]":
        #     R(Key("a-down"))*Repeat(extra="nnavi10"),
        "previous team":
            R(Key("cs-up")),
        "next team":
            R(Key("cs-down")),
        "previous section":
            R(Key("cs-f6")),
        "next section":  
            R(Key("c-f6")),

        # Messaging
        "focus compose":
            R(Key("as-c")),
        "expand compose":
            R(Key("cs-x")),
        "new-line":
            R(Key("s-enter")),
        "reply":
            R(Key("as-r")),

        # meetings calls and calendar
        "Accept [video] call":
            R(Key("cs-a")),
        "Accept [audio] call":
            R(Key("cs-s")),
        "decline [call]":
            R(Key("cs-d")),
        "start audio call":
            R(Key("cs-c")),
        "Start video call":
            R(Key("cs-u")),
        "toggle mute":
            R(Key("cs-m")),
        "screen share":
            R(Key("cs-e")),
        "toggle video":
            R(Key("cs-o")),
        "sharing toolbar":
            R(Key("cs-space")),
        "decline screen share":
            R(Key("cs-d")),
        "Accept screen share":
            R(Key("cs-a")),
        "Schedule meeting":
            R(Key("as-n")),
        "go to current time":
            R(Key("a-.")),
        "go to previous (day | week)":
            R(Key("ca-`left")),
        "go to next (day | week)":
            R(Key("ca-right")),
        "View day":
            R(Key("ca-1")),
        "View workweek":
            R(Key("ca-2")),
        "View week":
            R(Key("ca-3")),
   }
    exported = True
    extras = [
        ShortIntegerRef("nnavi10", 1, 11)
    ]
    defaults = {
        "nnavi10": 1
    }

def get_rule():
    return MSTeamsClassicRule, RuleDetails(name="Microsoft Teams Classic", executable="ms-teams")
