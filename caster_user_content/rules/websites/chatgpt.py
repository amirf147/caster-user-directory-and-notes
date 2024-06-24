from dragonfly import MappingRule, ShortIntegerRef, Repeat
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

class ChatGPTRule(MappingRule):
    pronunciation = "chat jeepy tea rule"
    mapping = {
        "compose [box]":
            R(Key("f1")),
    }

def get_rule():
    return ChatGPTRule, RuleDetails(name="chatgpt rule", title="chatgpt")
