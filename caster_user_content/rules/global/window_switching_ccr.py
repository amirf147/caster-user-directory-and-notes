from dragonfly import Function, Mouse, List, ListRef, ShortIntegerRef, Pause

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key, Text
from castervoice.lib.merge.state.short import R
from castervoice.lib.merge.mergerule import MergeRule
from castervoice.lib.const import CCRType

from caster_user_content import environment_variables as ev
from caster_user_content.util import switch_application


# Create a Dragonfly List for aliases
window_aliases = List("window_alias")
# Merge aliases from environment, defaults, and saved runtime aliases
_merged_aliases = set(getattr(ev, "WINDOW_ALIASES", []))
_merged_aliases.update(switch_application.get_default_aliases().keys())
_merged_aliases.update(switch_application.aliases.keys())
window_aliases.set(list(_merged_aliases))

def refresh_aliases():
    """Rebuild the window_aliases Dragonfly list at runtime."""
    merged = set(getattr(ev, "WINDOW_ALIASES", []))
    merged.update(switch_application.get_default_aliases().keys())
    merged.update(switch_application.aliases.keys())
    window_aliases.set(list(merged))
    print(f"Refreshed alias list with {len(merged)} entries.")

class WindowSwitchingCCRRule(MergeRule):
    pronunciation = "window switching c c r"

    mapping = {
        # Switching command (supports optional instance number)
        "[switch [to]] <window_alias> [<n>]":
            # The shift key is pressed as a workaround for overcoming windows foreground-lock.
            # Windows will only honour SetForegroundWindow API call from switch_application.switch_to
            # when it believes the request came from a process that most recently generated genuine user input.
            # By pressing the shift key we ensure that the caster process is the one that generated the most
            # genuine recent user input.
            R(Key("shift") + Function(switch_application.switch_to) + Pause("30") + Mouse("(0.5, 0.5)")),
    }
    extras = [
        ListRef("window_alias", window_aliases),
        ShortIntegerRef("n", 1, 50),
    ]
    defaults = {
        "n": 1,
    }

def get_rule():
    details = RuleDetails(ccrtype=CCRType.GLOBAL)
    return WindowSwitchingCCRRule, details
