from dragonfly import MappingRule, Mimic

from castervoice.lib.actions import Key

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CopilotDesktopRule(MappingRule):
    pronunciation = "copilot desktop"
    mapping = {
        "q max": R(Key("a-q")),
        "close q": R(Key("a-f4")),
        
        "show chats | hide left": R(Key("a-1")),
        "show menu": R(Key("a-u")),
        "show settings": R(Key("a-u/50, enter")),
        
        # Chat modes
        "switch mode": R(Key("a-c")),
        "smart mode": R(Key("a-c/50, down:2, enter")),
        "thinking mode": R(Key("a-c/50, down, enter")),
        "research mode": R(Key("a-c/50, down:3, enter")),
        "vision mode": R(Key("a-s")),
        "conversation mode": R(Key("a-t/80") + Mimic("caster sleep")),
    }
    extras = []
    defaults = {}


def get_rule():
    return CopilotDesktopRule, RuleDetails(name="copilot desktop", executable="Copilot")
