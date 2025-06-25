from dragonfly import MappingRule, IntegerRef, Repeat
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails


class EdgeRule(MappingRule):

    mapping = {
        # Window / tab management
        "(new window|win new)": R(Key("c-n")),
        "new tab [<n>]|tab new [<n>]": R(Key("c-t")) * Repeat(extra="n"),
        "reopen tab [<n>]|tab reopen [<n>]": R(Key("cs-t")) * Repeat(extra="n"),
        "close tab [<n>]|tab close [<n>]": R(Key("c-w")) * Repeat(extra="n"),

        # Navigation
        "go back [<n>]": R(Key("a-left")) * Repeat(extra="n"),
        "go forward [<n>]": R(Key("a-right")) * Repeat(extra="n"),
        "refresh|reload": R(Key("c-r")),

        # Address bar
        "address bar": R(Key("a-d")),
    }

    extras = [
        IntegerRef("n", 1, 9),
    ]

    defaults = {"n": 1}


def get_rule():
    """Return rule class and metadata for Caster dynamic loader."""
    return EdgeRule, RuleDetails(name="Edge", executable=["msedge", "msedge.exe", "Microsoft Edge"])
