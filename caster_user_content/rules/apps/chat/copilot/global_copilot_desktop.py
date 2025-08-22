from dragonfly import MappingRule, Pause, Function, Dictation, Mouse
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib import utilities
from caster_user_content.util import switch_application

class GlobalCopilotDesktopRule(MappingRule):
    pronunciation = "global copilot desktop"
    mapping = {
        # Copilot from Microsoft
        "(show | hide) q | cuse": R(Key("a-space") + Pause("50") + Mouse("(0.5, 0.5)")),
        "new q": R(Key("a-space/180")),
        "q <prompt>": R(Key("a-space/180") + Text("%(prompt)s")),
        "new q max": R(Key("a-space/180, a-q")),
        "q clipboard": R(Key("a-space/180") + Key("c-v")),
        "chats": # TODO: Investigate the apparent blocking by windows to switch to the application
                 # when it has been previously minimized from within the application. Perhaps start
                 # by investigating a different way to switch to the application.

                 # Update: The switch application has been modified to use pwinauto for more reliable
                 # window activation. The shift key is no longer necessary. Hopefully...
            R(Function(switch_application.title, window_title="Copilot") + Pause("50") + Mouse("(0.5, 0.5)")),
        "close q": R(
            Function(switch_application.title, window_title="Copilot") +
            Pause("30") + Key("a-f4")),
        "min q | minx": R(
            Function(switch_application.title, window_title="Copilot") + Pause("30") +
            Function(utilities.minimize_window)),

        # TODO: Figure out how to check the state of copilot to see if it is in the foreground,
        # expanded, etc. Consider using inspect.exe or uiautomation
        
    }
    extras = [
        Dictation("prompt")
    ]
    defaults = {}

def get_rule():
    details = RuleDetails(name="Global Copilot Desktop")
    return GlobalCopilotDesktopRule, details
    