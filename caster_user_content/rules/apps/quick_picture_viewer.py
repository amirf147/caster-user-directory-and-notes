from dragonfly import MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class QuickPictureViewerRule(MappingRule):

    mapping = {
        "file open": R(Key("c-o")),
        "file retain": R(Key("c-s")),
        "file custom retain": R(Key("cs-s")),

        "zoom in [<n2>]": R(Key("c-equals:%(n2)d")),
        "zoom out [<n2>]": R(Key("c-minus:%(n2)d")),
        "zoom auto": R(Key("cs-a")),

        "slideshow": R(Key("s-f5")),

        "show info": R(Key("c-i")),
    }
    extras = [
        ShortIntegerRef("n2", 1, 10),
    ]
    defaults = {"n2": 1}


def get_rule():
    return QuickPictureViewerRule, RuleDetails(name="Quick Picture Viewer",
                                               executable="quick-picture-viewer")
