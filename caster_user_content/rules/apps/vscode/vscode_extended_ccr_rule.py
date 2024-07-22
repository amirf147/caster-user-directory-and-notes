from dragonfly import ShortIntegerRef, Pause

from castervoice.lib.actions import Key, Text

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

class VSCodeExtendedCcrRule(MergeRule):
    pronunciation = "vscode ccr extended"

    mapping = {
        "pane <n03>":
            R(Key("c-%(n03)d")),
        "line del [<n>]":
            R(Key("cs-k:%(n)d")),
        "selina [<n101>]":
            R(Key("c-l:%(n101)d")),
        "hide left":
            R(Key("c-b")),
        "super find":
            R(Key("cs-f")),

        # Jumping to a line
        "zora <n>":
            R(Key("c-g") + Text("%(n)d") + Key("enter") + Pause("50")),

        # Python executable paths
        "python twelve":
            R(Text("C:\\Users\\amirf\\AppData\\Local\\Programs\\Python\\Python312\\python.exe")),
        "python ten":
            R(Text("C:\\Users\\amirf\\AppData\\Local\\Programs\\Python\\Python310\\python.exe")),

        # Requires user-defined key bindings
        # Command: Add selection to previous find match
        "curse previous [<n>]":
            R(Key("ca-d:%(n)d")),
        
    }
    extras = [
        ShortIntegerRef("n", 1, 1000),
        ShortIntegerRef("n101", 1, 101),
        ShortIntegerRef("n03", 0, 3)
    ]
    defaults = {
        "n": 1,
        "n101": 1
    }

def get_rule():
    details = RuleDetails(executable="code",
                          title="Visual Studio Code",
                          ccrtype=CCRType.APP)
    return VSCodeExtendedCcrRule, details
