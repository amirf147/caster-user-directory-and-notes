from dragonfly import MappingRule, Function, Choice, ShortIntegerRef
from castervoice.lib.navigation import Grid
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CustomMouseAlternativesRule(MappingRule):
    mapping = {
        "legion [<monitor>] [<rough>]":
            R(Function(Grid.mouse_alternates, mode="legion")),
        # "rainbow [<monitor>]":
        #     R(Function(Grid.mouse_alternates, mode="rainbow")),
        # "douglas [<monitor>]":
        #     R(Function(Grid.mouse_alternates, mode="douglas")),
        "sudoku [<monitor>]":
            R(Function(Grid.mouse_alternates, mode="sudoku")),
    }
    extras = [
        ShortIntegerRef("monitor", 1, 10),
        Choice("rough", {
            "rough": True,
            "detailed": False
        })
    ]
    defaults = {"rough": True}


def get_rule():
    details = RuleDetails(name="custom mouse alternatives rule")
    return CustomMouseAlternativesRule, details
