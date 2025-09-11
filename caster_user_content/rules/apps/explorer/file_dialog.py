from dragonfly import Dictation, MappingRule, ShortIntegerRef, Choice

from castervoice.lib.actions import Key

from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev

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
            R(Key("a-d, tab:1") + Text("%(text)s", pause=0.0)),
        "(navigation | nav | left) pane":
            R(Key("a-d, tab:4")),
        "(center pane | (file | folder) (pane | list))":
            R(Key("a-d, tab:5")),
        "organize": R(Key("c-l, tab:2")),
        "sort [headings]": R(Key("c-l, tab:5")),
        "[file] name": R(Key("a-n")),
        "file type": R(Key("c-l, tab:7")),
        "show preview": R(Key("a-p")),

        # Navigating via address bar
        "(go | navigate) <path>":
            R(Key("a-d/5") + Text("%(path)s", pause=0.0) + Key("enter, tab:6")),
        "go clipboard":
            R(Key("a-d/5, c-v, enter")),

    }
    extras = [
        ShortIntegerRef("n", 1, 10),
        Dictation("text"),
        Choice("path", ev.FILE_EXPLORER_PATHS),
        ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return FileDialogRule, RuleDetails(
        name="custom file dialog",
        title=[
            "open", "save", "select", "file upload", 
            "Insert Picture", "Insert Image", "Export", 
            "Another Application", "Install from VSIX",
            "Save As"
        ]
    )
