from dragonfly import MappingRule

from castervoice.lib.actions import Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class SumatraRule(MappingRule):
    pronunciation = "sumatra"
    mapping = {
        "zoom in": R(Key("equal")),
        "zoom out": R(Key("minus")),
        "bookmarks": R(Key("f12")),
        "file open": R(Key("c-o")),
    }

def get_rule():
    return SumatraRule, RuleDetails(name="sumatra", executable="SumatraPDF")
