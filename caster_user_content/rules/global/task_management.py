from dragonfly import MappingRule, Function, Clipboard, Key, Choice
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

# Attempt to import the helper that actually talks to the Trello REST API.
# Keep this import at module level so the rule fails early if the dependency
# is not available, rather than during recognition time.
try:
    import trello_tools  # expects a module with an `add_card` helper
except ImportError as err:
    # Swallow the import error so Caster can continue loading other rules.
    trello_tools = None
    _trello_tools_import_error = err  # noqa: E501
else:
    _trello_tools_import_error = None


def _safe_add_card(list_name):
    """Wrapper that reads the clipboard and delegates to ``trello_tools.add_card``.

    board_name and list_name are fixed for now. The clipboard text becomes the
    card name; description is left blank.
    """
    if trello_tools is None:
        # Surface the original failure to the user in a way that won't kill the
        # thread-pool but will still be visible in Caster's log window.
        raise RuntimeError(
            "The `trello_tools` module could not be imported: {}".format(_trello_tools_import_error)
        )

    card_name = Clipboard(from_system=True).get_system_text()
    if not card_name:
        raise ValueError("Clipboard is empty – nothing to add to the To-Do list.")

    trello_tools.add_card(
        board_name="Classes",
        list_name=list_name,
        card_name=card_name,
        card_desc="",  # description intentionally left blank for now
    )


class TaskManagementRule(MappingRule):
    mapping = {
        "add sure <list_name>": R(Key("c-c/30") + Function(_safe_add_card, list_name="%(list_name)s")),
    }
    extras = [
        Choice("list_name", {
            "to sort": "To Sort",
            "to do": "To Do",
            "caster": "Caster",
            "for later": "For Later",
            "projects | ideas": "Projects/Ideas",
            "statistics": "Statistical Data Analysis",
        }),
    ]


def get_rule():
    details = RuleDetails(name="Task Management")
    return TaskManagementRule, details
