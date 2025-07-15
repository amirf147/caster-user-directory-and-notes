from dragonfly import Dictation, MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CustomOutlookRule(MappingRule):

    pronunciation = "custom outlook"

    mapping = {

        # Go to
        "hide left": R(Key("a-f1")),
        "focus [<n>]": R(Key("f6:%(n)d")),
        "locus [<n>]": R(Key("s-f6:%(n)d")),
        "school inbox": R(Key("c-e/3, f6:2, home, left, down, \
                               left, down, right, down, enter")),
        "personal inbox": R(Key("c-e/3, f6:2, home, left, down, \
                                left, right, down, enter")),
        "mail list": R(Key("c-e/3, f6:3")),
        "synchronize": R(Key("f9")),
        "go to inbox": R(Key("c-1/3, cs-i")),
        "go inbox": R(Key("c-1")),

        # Calendar
        "go calendar": R(Key("c-2")),
        "event new": R(Key("c-2, c-n")),

        "show contacts": R(Key("c-3")),
        "hint insert": R(Key("alt/3, n")),
        "hint view": R(Key("alt/3, v")),
        "file attach": R(Key("alt/3, n, a, f")),
        "pop out email": R(Key("s-enter")),
        "etsy <dictation>": R(Key("c-e") + Text("%(dictation)s", pause=0.0)),

        # Writing email
        "mail new": # Opens mail composer in new window
            R(Key("c-n/50, s-tab:4, enter")),
        "insert simple ending": R(Text("Thanks,\nAmir Farhadi", pause=0.0)),

        # Text Formatting
        "insert bullet": R(Key("c-.")),
        "format bold": R(Key("c-b")),
        "format italic": R(Key("c-i")),
        "format underline": R(Key("c-u")),
    }
    extras = [
        ShortIntegerRef("n", 1, 100),
        Dictation("dictation"),
    ]
    defaults = {"n": 1,}


def get_rule():
    return CustomOutlookRule, RuleDetails(name="custom outlook", executable="olk")
