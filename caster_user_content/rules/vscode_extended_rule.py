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
            R(Key("cs-k:%(n)d"))
    }
    extras = [
        ShortIntegerRef("n", 1, 10),
        ShortIntegerRef("n03", 0, 3)
    ]
    defaults = {
        "n": 1,
    }

def get_rule():
    details = RuleDetails(executable="code",
                          title="Visual Studio Code",
                          ccrtype=CCRType.APP)
    return VSCodeExtendedCcrRule, details
