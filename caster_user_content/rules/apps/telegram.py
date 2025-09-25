from dragonfly import MappingRule, ShortIntegerRef
from castervoice.lib.actions import Key
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

class TelegramRule(MappingRule):

    mapping = {
        "chat under [<n>]": R(Key("c-pgdown:%(n)d")),
        "chat over [<n>]": R(Key("c-pgup:%(n)d")),
    }
    extras = [
        ShortIntegerRef("n", 1, 11),
    ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return TelegramRule, RuleDetails(name="telegram", executable="Telegram")
