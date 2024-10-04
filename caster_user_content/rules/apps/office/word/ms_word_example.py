from dragonfly import MappingRule, Choice, IntegerRef
from castervoice.lib.actions import Text, Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

class WordRule(MappingRule):
    mapping = {

        # Example command 1:
        "insert [my | the] [<place>] address":
            R(
                Text("Address: %(place)s") +
                Key("c-left:8")
            ),

        # Example command 2:
        "empty above three":
            R(
                Key("home/5, enter:3")
            ),

        # Example command 2:
        "empty below <n>":
            R(
                Key("end/3, enter:%(n)d")
            )
    }

    extras = [
        Choice("place", {
            "home": "5665 Hillcrest Ave, Seattle, WA 98118",
            "work": "123 Main St, Seattle, WA 98118"
        }),
        IntegerRef("n", 1, 101),
    ]

    defaults = {
        "place": "5665 Hillcrest Ave, Seattle, WA 98118",
        }

def get_rule():
    details = RuleDetails(name="Word Rule", executable="winword")
    return WordRule, details
