from dragonfly import MappingRule, Function, List, ListRef
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R
from caster_user_content.util import window_switcher

# Create a Dragonfly List for aliases
window_aliases = List("window_alias")
window_aliases.set(["code", "power", "water"])

class WindowSwitchingRule(MappingRule):
    pronunciation = "window switching"
    
    mapping = {
        # Window level commands
        "set window <window_alias>": 
            R(Function(lambda window_alias: window_switcher.set_alias(window_alias, False))),
        "switch [to] window <window_alias>": 
            R(Function(lambda window_alias: window_switcher.alias(window_alias, False))),
        
        # Tab level commands
        "set page <window_alias>": 
            R(Function(lambda window_alias: window_switcher.set_alias(window_alias, True))),
        "switch [to] page <window_alias>": 
            R(Function(lambda window_alias: window_switcher.alias(window_alias, True))),
    }

    extras = [
        ListRef("window_alias", window_aliases),
    ]

def get_rule():
    details = RuleDetails(name="Window Switching")
    return WindowSwitchingRule, details