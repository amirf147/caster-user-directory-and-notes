from dragonfly import MappingRule, Choice, ShortIntegerRef
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R

# Define a custom rule for controlling the taskbar through speech commands.
class TaskbarRule(MappingRule):
    pronunciation = "task bar"  # This is the phrase the rule will listen for when the user
                                # wants to activate the rule.

    # Define the mapping of spoken phrases to actions.
    mapping = {

        # Window switching: Taskbar items up to 9th item
        "drip [<n9>]": # Listens for the word 'drip' followed by a number from 1 to 9.
            # This sends a key combination using the Windows key ('w') and the number key.
            # %(n9)d will be replaced by the number spoken.
            R(Key("w-%(n9)d, enter")),  # Presses Windows key + number, followed by Enter.

        # Window switching: Taskbar items from 10th up to 20th item.
        # Note: Windows taskbar items beyond the 9th are accessed differently.
        "drip [<n_off_by_one>]": # Listens for the word 'drip' followed by a number from 10 to 20.
            # This sequence simulates pressing the Windows key + 't' to open taskbar, then 
            # pressing the down key several times to navigate to the desired item.
            R(Key("w-t/3, down:%(n_off_by_one)s, enter")),  # 'down' key is pressed a number of times
                                                            # based on the number spoken.
        
        # Window switching: Taskbar items in reverse order.
        "drip minus [<n20>]": # Listens for the word 'drip minus' followed by a number from 1 to 20.
            # Similar to the previous mapping, but uses 'up' key instead of 'down' to move 
            # in reverse order through the taskbar items.
            R(Key("w-t/3, up:%(n20)d, enter")),  # Moves up by the number of taskbar items specified,
                                                 # followed by Enter to select the item.
    }

    # Define extra variables used in the mappings above.
    extras = [
        # A choice for interpreting spoken numbers between 10 and 20. 
        # These are mapped to 9 to 19 because of how taskbar items are accessed.
        Choice("n_off_by_one", {
            "ten": "9",
            "eleven": "10",
            "twelve": "11",
            "thirteen": "12",
            "fourteen": "13",
            "fifteen": "14",
            "sixteen": "15",
            "seventeen": "16",
            "eighteen": "17",
            "nineteen": "18",
            "twenty": "19",
        }),
        
        # ShortIntegerRef allows specifying a range of integers.
        # n9 is for numbers between 1 and 9.
        ShortIntegerRef("n9", 1, 10),

        # n20 is for numbers between 1 and 20.
        ShortIntegerRef("n20", 1, 21),
    ]

    # Default values for the variables in case none are provided.
    defaults = {
        "n9": 1,  # Default for n9 is 1, so 'drip' without a number uses the first taskbar item.
        "n20": 1,  # Default for n20 is 1, meaning 'drip minus' starts from the first item in reverse.
    }

# This function allows the rule to be registered and associated with the name 'Taskbar'.
def get_rule():
    details = RuleDetails(name="Taskbar")
    return TaskbarRule, details
