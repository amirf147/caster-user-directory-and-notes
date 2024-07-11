from dragonfly import Dictation, MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key, Text

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class ExplorerRule(MappingRule):
    """I just copied over the IERule because i feel like I'll change a lot of 
        the default phrases in the future.
    """
    pronunciation = "explore"
    mapping = {
        "address bar":
            R(Key("a-d")),
        "window new":
            R(Key("c-n")),
        "folder new":
            R(Key("cs-n")),
        "file new":
            R(Key("a-f, w, t")),
        "(show | file | folder) properties":
            R(Key("a-enter")),
        "dirrup [<n>]":
            R(Key("a-up:%(n)d")),
        "go back [<n>]":
            R(Key("a-left:%(n)d")),
        "go forward [<n>]":
            R(Key("a-right:%(n)d")),
        "search [<text>]":
            R(Key("a-d, tab:1") + Text("%(text)s")),
        "(navigation | nav | left) pane":
            R(Key("a-d, tab:2")),
        "(center pane | (file | folder) (pane | list))":
            R(Key("a-d, tab:3")),
            # for the sort command below,
            # once you've selected the relevant heading for sorting using the arrow keys, press enter
        "sort [headings]":
            R(Key("a-d, tab:4")),

    }
    extras = [
        Dictation("text"),
        ShortIntegerRef("n", 1, 1000),
    ]
    defaults = {"n": 1}


def get_rule():
    return ExplorerRule, RuleDetails(name="explore", executable="explorer")
