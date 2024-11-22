from dragonfly import Repeat, Dictation, MappingRule, ShortIntegerRef, Choice

from castervoice.lib.actions import Key

from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from . import environment_variables as ev

class FileDialogRule(MappingRule):
    pronunciation = "custom file"
    mapping = {
        "address bar":
            R(Key("a-d")),
        "copy address":
            R(Key("a-d/5, c-c")),
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
            R(Key("a-d, tab:3")),
        "(center pane | (file | folder) (pane | list))":
            R(Key("a-d, tab:4")),
        "organize": R(Key("c-l, tab:2")),
        "sort [headings]": R(Key("c-l, tab:5")),
        "[file] name": R(Key("a-n")),
        "file type": R(Key("c-l, tab:7")),

        # Navigating via address bar
        "go <path>":
            R(Key("a-d/5") + Text("%(path)s") + Key("enter, tab:4")),
        "go clipboard":
            R(Key("a-d/5, c-v, enter")),

    }
    extras = [
        ShortIntegerRef("n", 1, 10),
        Dictation("text"),
        Choice("path", {
            "[my] documents" : "C:\\Users\\amirf\\Documents\\",
            "downloads" : "C:\\Users\\amirf\\Downloads\\",
            "home" : "C:\\Users\\amirf\\",
            "pictures": "C:\\Users\\amirf\\Pictures\\",
            "job search": ev.JOB_SEARCH
        }),
        ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return FileDialogRule, RuleDetails(name="custom file dialog", title=["open", "save", "select", "file upload", "Insert Picture"])
