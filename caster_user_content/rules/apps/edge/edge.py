from dragonfly import MappingRule, IntegerRef, Repeat, Choice, Dictation, Function, Pause
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.temporary import Store, Retrieve
from castervoice.lib import utilities
from caster_user_content import environment_variables as ev


class EdgeRule(MappingRule):

    mapping = {
        # Window / tab management
        "(new window|win new)": R(Key("c-n")),
        "new tab [<n>]|tab new [<n>]": R(Key("c-t")) * Repeat(extra="n"),
        "reopen tab [<n>]|tab reopen [<n>]": R(Key("cs-t")) * Repeat(extra="n"),
        "close tab [<n>]|tab close [<n>]": R(Key("c-w")) * Repeat(extra="n"),
        "win close|close all tabs": R(Key("cs-w")),

        # Navigation
        "go back [<n>]": R(Key("a-left/20")) * Repeat(extra="n"),
        "go forward [<n>]": R(Key("a-right/20")) * Repeat(extra="n"),
        "refresh|reload": R(Key("c-r")),

        # Zoom
        "zoom in [<n>]": R(Key("c-plus/20")) * Repeat(extra="n"),
        "zoom out [<n>]": R(Key("c-minus/20")) * Repeat(extra="n"),
        "zoom reset": R(Key("c-0")),

        # Address bar
        "address bar": R(Key("a-d")),
        "extensions bar": R(Key("a-d/5, tab:2, right:2")),
        "show menu": R(Key("a-d/5, tab:2, right:7, enter")),

        # Address bar querying with dictation
        "netzer <query>": R(Key("a-d/5") + Text("%(query)s", pause=0.0) + Key("enter")),
        "netzer tab <query>": R(Key("c-t/5") + Text("%(query)s", pause=0.0) + Key("enter")),
        "netzer window <query>": R(Key("c-n/120") + Text("%(query)s", pause=0.0) + Key("enter")),
        "netzer sprite <query>": R(
            Function(utilities.maximize_window) + Pause("50") +
            Key("w-right/50, c-n/100, wca-0/30, w-right:2/50") + Text("%(query)s", pause=0.0) + Key("enter")),

        "reddit <query>": R(Key("a-d/5") + Text("%(query)s reddit", pause=0.0) + Key("enter")),
        "reddit tab <query>": R(Key("c-t/5") + Text("%(query)s reddit", pause=0.0) + Key("enter")),
        "reddit window <query>": R(Key("c-n/120") + Text("%(query)s reddit", pause=0.0) + Key("enter")),
        "reddit sprite <query>": R(
            Function(utilities.maximize_window) + Key("w-right/50, c-n/100, wca-0/30, w-right:2/50") +
            Text("%(query)s reddit", pause=0.0) + Key("enter")),

        "hister <query>": R(Key("a-d/5") + Text("^%(query)s", pause=0.0)),
        "hister tab <query>": R(Key("c-t/5") + Text("^%(query)s", pause=0.0)),
        "hister window <query>": R(Key("c-n/120") + Text("^%(query)s", pause=0.0)),

        "bookzer <query>": R(Key("a-d/5") + Text("*%(query)s", pause=0.0)),
        "bookzer tab <query>": R(Key("c-t/5") + Text("*%(query)s", pause=0.0)),
        "bookzer window <query>": R(Key("c-n/120") + Text("*%(query)s", pause=0.0)),

        # Specific website navigation
        "go <website>": R(Key("a-d/5") + Text("%(website)s", pause=0.0) + Key("enter")),
        "go tab <website>": R(Key("c-t/5") + Text("%(website)s", pause=0.0) + Key("enter")),
        "go window <website>": R(Key("c-n/120") + Text("%(website)s", pause=0.0) + Key("enter")),
        "go sprite <website>": R(
            Function(utilities.maximize_window) + Key("w-right/50, c-n/100, wca-0/30, w-right:2/50") +
            Text("%(website)s", pause=0.0) + Key("enter")),

        # Pasting clipboard content into address bar
        "go clipboard": R(Key("a-d/5") + Key("c-v") + Key("enter")),
        "go tab clipboard": R(Key("c-t/5") + Key("c-v") + Key("enter")),
        "go window clipboard": R(Key("c-n/120") + Key("c-v") + Key("enter")),
        "go sprite clipboard": R(
            Function(utilities.maximize_window) + Key("w-right/50, c-n/100, wca-0/30, w-right:2/50, c-v, enter")),

        # Link navigation
        "jink <query>": R(Key("c-f/5") + Text("%(query)s", pause=0.0) + Key("enter/5, escape/3, enter")),
        "jinx <query>": R(Key("c-f/5") + Text("%(query)s", pause=0.0) + Key("enter/5")),

        # Googling selected text
        "google that": R(Store(remove_cr=True) + Key("c-t/5") + Retrieve() + Key("enter")),
        "google that window": R(Store(remove_cr=True) + Key("c-n/120") + Retrieve() + Key("enter")),
    }

    extras = [
        IntegerRef("n", 1, 9),
        Choice("website", ev.WEBSITES),
        Dictation("query"),
    ]

    defaults = {
        "n": 1,
        "query": "",
    }


def get_rule():
    """Return rule class and metadata for Caster dynamic loader."""
    return EdgeRule, RuleDetails(name="Edge", executable=["msedge", "msedge.exe", "Microsoft Edge"])
