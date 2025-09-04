# TODO: replace ribbon navigation commands with windows 11 compatible macros
from dragonfly import Dictation, MappingRule, ShortIntegerRef, Choice, Pause, Repeat

from castervoice.lib.actions import Key

from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev

class FileExplorerRule(MappingRule):
    mapping = {
        "page new": R(Key("c-t")),
        "page over [<n>]": R(Key("c-tab:%(n)d")),
        "page under [<n>]": R(Key("cs-tab:%(n)d")),

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

        # Folder Navigation Shortcuts
        # Simply just doing a key press a-up/down/left/right no longer works reliably
        # in the new Windows 11 file explorer. By first holding down the alt key and then 
        # pressing the up/down/left/right keys, it works more reliably. A longer pause is
        # also necessary in order to wait for the GUI to refresh in between.
        "dirrup [<n>]":
            R(Key("alt:down, up, alt:up") + Pause("30")) * Repeat(extra='n'),
        "go back [<n>]":
            R(Key("alt:down, left, alt:up") + Pause("30")) * Repeat(extra='n'),
        "go forward [<n>]":
            R(Key("alt:down, right, alt:up") + Pause("30")) * Repeat(extra='n'),

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
        "expand folder": R(Key("cs-e")),
        "file preview": R(Key("a-p")),
        "folder preview": R(Key("as-p")),

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
        "new shortcut": R(Key("alt/20, enter/30, down, enter")),
        "create shortcut": # Create shortcut via context menu
            R(Key("s-f10/20, w/20, s:2, enter")),
        "new window": R(Key("c-n")),
        "select all": R(Key("a-h, s, a")),
        "show details": R(Key("alt/30, right:10, enter, tab:2")),
        "invert selection": R(Key("a-h, s, i")),
        "deselect": R(Key("a-h, s, n")),
        "edit file": R(Key("a-h, e")),
        "open with": R(Key("a-h, p, e")),

        # View
        "show files | hide left":
            R(Key("a-v, n, space")),
        "sort by recent": R(Key("a-v, o, down, enter")),
        "sort by size": R(Key("a-v, o, down:3, enter")),
        "view set extra large": R(Key("cs-1")),
        "view set large": R(Key("cs-2")),
        "view set medium": R(Key("cs-3")),
        "view set small": R(Key("cs-4")),
        "view set list": R(Key("cs-5")),
        "view set details": R(Key("cs-6")),
        "view set tiles": R(Key("cs-7")),
        "view set content": R(Key("cs-8")),

        # Share Ribbon
        "zippo": R(Key("s-f10/30, w/30, n, down, enter")), # Create a compressed (zipped) folder that contains the selected items
        
        # Manage - Shortcut Tools Ribbon
        "open location": R(Key("s-f10/30, i")),

        # Extract - Compressed Folder Tools Ribbon
        "extract all": R(Key("s-f10/30, t")),

        "open in wind": R(Key("s-f10/50, i")),

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
