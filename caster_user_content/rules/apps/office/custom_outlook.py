from dragonfly import Function, Repeat, Dictation, Choice, MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CustomOutlookRule(MappingRule):

    pronunciation = "custom outlook"

    mapping = {
        "new mail": R(Key("c-n")),

        "focus [<n>]": R(Key("f6:%(n)d")),
        "locus [<n>]": R(Key("s-f6:%(n)d")),
        "school inbox": R(Key("c-e/3, f6:2, home, left, down, \
                               left, down, right, down, enter")),
        "personal inbox": R(Key("c-e/3, f6:2, home, left, down, \
                                left, right, down, enter")),
        "synchronize": R(Key("f9")),
        "go to inbox": R(Key("c-1/3, cs-i")),
        "show calendar": R(Key("c-2")),
        "hint insert": R(Key("alt/3, n")),
        "file attach": R(Key("alt/3, n, a, f")),
        "pop out email": R(Key("s-enter")),
        "etsy <dictation>": R(Key("c-e") + Text("%(dictation)s")),
        "insert simple ending": R(Text("Thanks,\nAmir Farhadi")),
        

        # Text Formatting
        "insert bullet": R(Key("c-.")),
    }
    extras = [
        ShortIntegerRef("n", 1, 100),
        Dictation("dictation"),
    ]
    defaults = {"n": 1,}


def get_rule():
    return CustomOutlookRule, RuleDetails(name="custom outlook", executable="olk")
