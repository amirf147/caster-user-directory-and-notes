from dragonfly import MappingRule, ShortIntegerRef, Repeat, Pause, Mimic
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

class GeminiRule(MappingRule):
    pronunciation = "gemini rule"
    mapping = {
        # "focus compose [box]": # No longer is being recognized in Waterfox, instead it just toggles the side bar or something
        #     R(Key("f1")),
        
        # bring focus to the response area above the compose box so you can scroll the response
        # using keyboard keys
        # ever since an update to gemini, no longer able to "s-tab" out of the compose box
        # so using f6 and multiple presses of the tab key is used as a workaround
        # "response":
        #     R(Key("f6/3, f6") +
        #       Pause("40") + Key("tab") +
        #       Pause("40") + Key("tab:24") +
        #       Pause("60") + Key("end, up:10"))
        "pro mode": # Requires that you are in the message composer box, switches to pro mode from fast mode 
            R(Key("tab:3/50, space/50, tab, enter")),
        "fast mode": # Requires that you are in the message composer box, switches to fast mode from pro mode 
            R(Key("tab:3/50, space/50, enter")),
        "voice chat": # Requires that you are in the message composer box, starts the voice chat interface 
            R(Key("tab:4/50") + Mimic("caster sleep") + Pause("100") + Key("space")),      
    }

def get_rule():
    return GeminiRule, RuleDetails(name="gemini rule", title="gemini")
