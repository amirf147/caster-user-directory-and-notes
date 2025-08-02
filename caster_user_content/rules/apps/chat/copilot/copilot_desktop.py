from dragonfly import MappingRule, Mimic

from castervoice.lib.actions import Key

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CopilotDesktopRule(MappingRule):
    pronunciation = "copilot desktop"
    mapping = {
        "q max | expo": R(Key("a-q")),
        "close q": R(Key("a-f4")),
        "switch mode": R(Key("a-c")),
        "conversation mode": R(Key("a-t/80") + Mimic("caster sleep")),
        "vision mode": R(Key("a-s")),
        "show chats | hide left": R(Key("a-1")),
        "show menu": R(Key("a-u")),
        "show settings": R(Key("a-u/50, enter")),
    }
    extras = []
    defaults = {}


def get_rule():
    return CopilotDesktopRule, RuleDetails(name="copilot desktop", executable="Copilot")
