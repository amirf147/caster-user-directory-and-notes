from dragonfly import MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class WindowsTerminalRule(MappingRule):
    mapping = {
        "show settings": R(Key("c-comma")),
        "show settings jason": R(Key("cs-comma")),
        "commander": R(Key("cs-p")),

        "zoom in [<n>]": R(Key("c-equal:%(n)d")),
        "zoom out [<n>]": R(Key("c-minus:%(n)d")),

        "close shell": R(Key("cs-w")),
        "reopen shell": R(Key("cs-t")),
        "pop out shell": R(Key("csa-t")), # Move pane into new window
        "shell under [<n>]": R(Key("control:down") + Key("tab:%(n)d, control:up")),
        "shell over [<n>]": R(Key("control:down, shift:down") + Key("tab:%(n)d, control:up, shift:up")),
        "new power | shell new": R(Key("cs-1")),
        "new (command | c m d | command prompt)": R(Key("cs-2")),
        "new git bash": R(Key("cs-6")),

        "mark mode": R(Key("cs-m")),
    }
    extras = [
        ShortIntegerRef("n", 1, 11),
    ]
    defaults = {
        "n": 1,
    }
def get_rule():
    return WindowsTerminalRule, RuleDetails(name="Windows Terminal", executable="WindowsTerminal")
