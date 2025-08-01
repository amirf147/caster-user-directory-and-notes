from dragonfly import MappingRule, Pause, Function, Dictation, Mimic
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib import utilities, navigation
from castervoice.rules.core.navigation_rules import navigation_support

from caster_user_content.util import switch_application

class GlobalCopilotDesktopRule(MappingRule):
    pronunciation = "global copilot desktop"
    mapping = {
        # Copilot from Microsoft
        "(show | hide) q | cuse": R(Key("a-space")),
        "new q": R(Key("a-space/180")),
        "q max": R(Key("a-q")),
        "q <prompt>": R(Key("a-space/180") + Text("%(prompt)s")),
        "new q max": R(Key("a-space/180, s-tab:3, enter")),
        "q clipboard": R(Key("a-space/180") + Key("c-v")),
        "close q": R(
            Function(switch_application.title, window_title="Copilot") +
            Pause("30") + Key("a-f4")),

        "switch mode": R(Key("a-c")),
        "conversation mode": R(Key("a-t/80") + Mimic("caster sleep")),
        "vision mode": R(Key("a-s")),
    }
    extras = [
        Dictation("prompt")
    ]
    defaults = {}

def get_rule():
    details = RuleDetails(name="Global Copilot Desktop")
    return GlobalCopilotDesktopRule, details
    