from dragonfly import Repeat, Dictation, MappingRule, ShortIntegerRef, Choice

from castervoice.lib.actions import Key

from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev

class FileExplorerRule(MappingRule):
    mapping = {
        "show properties": R(Key("a-enter")),
        "show settings": R(Key("a-v, y, o")),
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
            R(Key("a-d, tab:2")),
        "(center pane | (file | folder) (pane | list))":
            R(Key("a-d, tab:3")),
        "organize": R(Key("c-l, tab:2")),
        "sort [headings]": R(Key("c-l, tab:5")),
        "[file] name": R(Key("a-n")),
        "file type": R(Key("c-l, tab:7")),

        # Navigating via address bar
        "go <path>":
            R(Key("a-d/5") + Text("%(path)s", pause=0.0) + Key("enter")),
        "go clipboard":
            R(Key("a-d/5, c-v/3, enter")),
        
        "fit column":
            R(Key("a-v, s, f")),

        "copy file name": R(Key("f2/3, c-c/3, escape")),

        # Home Ribbon
        "copy path": R(Key("a-h, c, p")),
        "new shortcut": R(Key("a-h, w, s")),
        "new window": R(Key("c-n")),
        "select all": R(Key("a-h, s, a")),
        "details pane": R(Key("a-v, d")),
        "invert selection": R(Key("a-h, s, i")),
        "deselect": R(Key("a-h, s, n")),

        # View Ribbon
        "show files | hide left":
            R(Key("a-v, n, space")),
        "preview pane":         # I noticed that when the preview pane is open the
            R(Key("a-v/3, p")), # view ribbon interaction might require a pause after pressing a-v

        # Share Ribbon
        "zippo": R(Key("a-s, c")), # Create a compressed (zipped) folder that contains the selected items
        
        # Manage - Shortcut Tools Ribbon
        "open location": R(Key("a-j, t, o")),

        # Extract - Compressed Folder Tools Ribbon
        "extract all": R(Key("alt, j, z, a")),

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
    return FileExplorerRule, RuleDetails(name="File Explorer Rule",
                                         executable="explorer")
