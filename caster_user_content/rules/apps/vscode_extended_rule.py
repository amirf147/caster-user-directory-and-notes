from dragonfly import ShortIntegerRef

from castervoice.lib.actions import Key

from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.merge.state.short import R

class VSCodeExtendedCcrRule(MergeRule):
    pronunciation = "vscode extended"

    mapping = {
        "pane increase [<n>]":
            R(Key("cs-i:%(n)d")),
        "pane decrease [<n>]":
            R(Key("cs-o:%(n)d")),
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

        # Requires user-defined key bindings
        # Each mapping is preceded by the command name

        # Add selection to previous find match
        "curse previous [<n>]":
            R(Key("ca-d:%(n)d")),
        
        # Collapse folders in explorer
        "collapse folders":
            R(Key("c-k, cs-f")),
    }
    extras = [
        ShortIntegerRef("n", 1, 10),
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
