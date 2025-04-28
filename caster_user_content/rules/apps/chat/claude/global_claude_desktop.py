from dragonfly import MappingRule, Pause, Function, Dictation
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib import utilities, navigation
from castervoice.rules.core.navigation_rules import navigation_support

from caster_user_content.util import switch_application

class GlobalClaudeDesktopRule(MappingRule):
    pronunciation = "claude global"
    mapping = {
        # Copilot from Microsoft
        "(show | hide) q": R(Key("ca-space")),
        # "new q": R(Key("a-space/180")),
        "q <prompt>": R(Key("ca-space/80") + Text("%(prompt)s")),
        # "new q max": R(Key("a-space/180, s-tab:3, enter")),
        # "q clipboard": R(Key("a-space/180") + Key("c-v")),
    #     "close q": R(
    #         Function(switch_application.title, window_title="Copilot") +
    #         Pause("30") + Key("a-f4")),
    }
    extras = [
        Dictation("prompt")
    ]
    defaults = {}

def get_rule():
    details = RuleDetails(name="Global Claude Desktop")
    return GlobalClaudeDesktopRule, details
    