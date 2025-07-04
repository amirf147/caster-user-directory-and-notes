# TODO: replace ribbon navigation commands with windows 11 compatible macros
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
            R(Key("a-d, tab:1")),
        "(center pane | (file | folder) (pane | list))":
            R(Key("a-d, tab:2")),
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
        "copy path": R(Key("cs-c")),
        "new shortcut": R(Key("a-h, w, s")),
        "new window": R(Key("c-n")),
        "select all": R(Key("a-h, s, a")),
        "details pane": R(Key("a-v, d")),
        "invert selection": R(Key("a-h, s, i")),
        "deselect": R(Key("a-h, s, n")),
        "edit file": R(Key("a-h, e")),
        "open with": R(Key("a-h, p, e")),

        # View Ribbon
        "show files | hide left":
            R(Key("a-v, n, space")),
        "preview pane":         # I noticed that when the preview pane is open the
            R(Key("a-v/3, p")), # view ribbon interaction might require a pause after pressing a-v
        "sort by recent": R(Key("a-v, o, down, enter")),
        "sort by size": R(Key("a-v, o, down:3, enter")),
        "view set extra large": R(Key("a-v, tab:6, enter, home, enter")),
        "view set large": R(Key("a-v, tab:6, enter, home, tab:1, enter")),
        "view set medium": R(Key("a-v, tab:6, enter, home, tab:2, enter")),
        "view set small": R(Key("a-v, tab:6, enter, home, tab:3, enter")),
        "view set list": R(Key("a-v, tab:6, enter, home, tab:4, enter")),
        "view set details": R(Key("a-v, tab:6, enter, home, tab:5, enter")),
        "view set tiles": R(Key("a-v, tab:6, enter, home, tab:6, enter")),
        "view set content": R(Key("a-v, tab:6, enter, home, tab:7, enter")),

        # Share Ribbon
        "zippo": R(Key("s-f10/30, w/30, n, down, enter")), # Create a compressed (zipped) folder that contains the selected items
        
        # Manage - Shortcut Tools Ribbon
        "open location": R(Key("a-j, t, o")),

        # Extract - Compressed Folder Tools Ribbon
        "extract all": R(Key("s-f10/30, t")),

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
