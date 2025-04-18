from dragonfly import MappingRule

from castervoice.lib.actions import Key

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CopilotDesktopRule(MappingRule):
    pronunciation = "copilot desktop"
    mapping = {
        "max q": R(Key("tab:4, enter/100, tab:4")),
        "previous chats": R(Key("tab:4, enter/100, tab:10")),
        "show settings": R(Key("s-tab:4, enter")),
        "close q": R(Key("a-f4/3, a-tab")),
    }
    extras = []
    defaults = {}


def get_rule():
    return CopilotDesktopRule, RuleDetails(name="copilot desktop", executable="Copilot")
