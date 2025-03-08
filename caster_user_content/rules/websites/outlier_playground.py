from dragonfly import MappingRule, ShortIntegerRef, Repeat, Choice
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

class OutlierPlaygroundRule(MappingRule):
    mapping = {
        "composer":
            R(Key("f1")),
        "show models": R(Key("f1/3, s-tab, space")),
        "switch to <model>": R(Key("f1/3, s-tab, space, home, down:%(model)s/100")),
    }

    extras = [
        Choice("model", {
            "four oh": "0",
            "four oh mini": "1",
            "oh one": "2",
            "oh three mini": "3",
            "claude sonnet": "4",
            "claude haiku": "5",
            "gemini pro": "6",
            "gemini flash": "7",
            "grok two": "8",
            "llama three three": "9",
        }),
    ]

def get_rule():
    return OutlierPlaygroundRule, RuleDetails(name="OutlierPlayground", title="Outlier Playground")