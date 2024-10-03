from dragonfly import Dictation, MappingRule
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

# Define a custom rule for Microsoft Word using the speech recognition framework.
class WordRule(MappingRule):
    # 'mapping' defines the spoken commands and the corresponding actions.
    mapping = {
        # The phrase "insert my address" will trigger the action that types
        # "5665 Hillcrest Avenue, Seattle, WA 98118" in the active text field.
        # The 'R' function not only performs the Text action but also sends terminal output,
        # logging the command that was executed for easier debugging or monitoring.
        "insert [(my | the)] address": R(Text("5665 Hillcrest Avenue, Seattle, WA 98118")),
    }

    # 'extras' can contain additional elements like Dictation for dynamic inputs.
    extras = []

    # 'defaults' defines default values for extras, but it remains empty here.
    defaults = {}

# The 'get_rule' function sets up rule details such as the rule's name and its target application.
def get_rule():
    # RuleDetails holds metadata about the rule, including the name "Word Rule" and that it
    # should only be active when Microsoft Word (executable "winword") is in use.
    details = RuleDetails(name="Word Rule", executable="winword")
    
    # The function returns the WordRule class and its associated details.
    return WordRule, details
