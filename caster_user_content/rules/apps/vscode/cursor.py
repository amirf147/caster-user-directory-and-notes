from dragonfly import Function, Repeat, Choice, Dictation, MappingRule, Pause, ShortIntegerRef

from castervoice.lib.actions import Key, Mouse

from castervoice.lib import navigation
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CursorRule(MappingRule):
    mapping = {
        "hide right": # Requires user defined key binding (View: Close AI Sidebar)
            R(Key("c-m, a-w")),
        "show chat": R(Key("cs-y")),
        
        "new chat": R(Key("c-l")),
        "chat new": R(Key("c-n")),  #"when": "focusedView == 'workbench.panel.aichat.view'"
        "composer": R(Key("cs-m, cs-k")), # Requires user defined key binding (View: Toggle Composer)

        # Source Control/Git
        "generate commit message": R(Key("c-k, cs-c")), # Requires user defined key binding (Generate Commit Message)
        "show changes": R(Key("c-g, c-o")), # Requires user defined key binding (Git: Open Changes)
        "stage changes": R(Key("c-g, c-s")), # Requires user defined key binding (Git: Stage Changes)
        "show stage": R(Key("c-g, cs-s")), # Requires user defined key binding (Git: View Staged Changes)
        "git sure commit": R(Key("c-g, c-c")), # Requires user defined key binding (Git: Commit)
        
        # Multiple Cursors
        "cursor above [<n>]": R(Key("ca-up:%(n)s")),
        "cursor below [<n>]": R(Key("ca-down:%(n)s")),
        "curse previous [<n>]": R(Key("ca-d:%(n)s")),
        "curse it [<n>]": R(Key("c-d:%(n)s")),

        "comment": R(Key("c-slash")),

        "suds <text>": R(Key("cs-f/3") + Text("%(text)s")),

    }
    extras = [
        ShortIntegerRef("n", 1, 101),
        Dictation("text"),
    ]
    defaults = {
        "n": 1,
    }

def get_rule():
    return CursorRule, RuleDetails(name="Cursor",
                                      executable="cursor",
                                      title="Cursor")
