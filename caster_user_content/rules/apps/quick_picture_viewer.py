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
        "zoom size": R(Key("c-0")),

        "slideshow": R(Key("s-f5")),
        "checkerboard background": R(Key("c-b")),
        "picture in picture": R(Key("cs-p")),

        "show info": R(Key("c-i")),

        # Edit image
        "rotate right": R(Key("c-g")),
        "rotate left": R(Key("cs-g")),
        "rotate one eighty": R(Key("c-j")),
        "flip horizontal": R(Key("c-h")),
        "flip vertical": R(Key("cs-h")),
        "crop image": R(Key("cs-x")),

        # Open file with external app, the first two are not working
        # "open with default": R(Key("c-e")),
        # "open with paint": R(Key("cs-o")),
        "open with choose": R(Key("cs-e")),

        # Effects
        "effect blur": R(Key("cs-b")),
        "effect grayscale": R(Key("a-g")),
        "effect invert": R(Key("cs-i")),
        "effect rainbow": R(Key("a-r")),

        # More options
        "delete sure permanent": R(Key("s-delete")),
        "file print": R(Key("c-p")),
        "background color": R(Key("f3")),
        "remove background color": R(Key("s-f3")),
        "always on top": R(Key("c-t")),
        "flameless mode": R(Key("f10")),
        "new window": R(Key("c-n")),
        "show plugins": R(Key("f2")),
        "show settings": R(Key("c-comma")),
        "show app info": R(Key("f1")),
    }
    extras = [
        ShortIntegerRef("n2", 1, 10),
    ]
    defaults = {"n2": 1}


def get_rule():
    return QuickPictureViewerRule, RuleDetails(name="Quick Picture Viewer",
                                               executable="quick-picture-viewer")

