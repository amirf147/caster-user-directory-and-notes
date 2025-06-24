from dragonfly import MappingRule

from castervoice.lib.actions import Text
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails


class TightVNCRule(MappingRule):
    """Voice commands for TightVNC viewer."""

    pronunciation = "tight v n c"

    mapping = {
        # Toggle full-screen mode
        "full screen mode": R(Text("csa-f")),
    }

    extras = []
    defaults = {}


def get_rule():
    # TightVNC viewer executable is typically `tvnviewer.exe`
    return TightVNCRule, RuleDetails(name="tight v n c", executable="tvnviewer")
