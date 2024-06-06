from dragonfly import Repeat, Dictation, MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key

from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class OBSStudioRule(MappingRule):
    pronunciation = "studio"
    mapping = {
        "start recording": R(Key("c-r:%(n)d")),
        "stop recording": R(Key("cs-r:%(n)d")),
    }

def get_rule():
    return OBSStudioRule, RuleDetails(name="studio", executable="obs64")