from dragonfly import Repeat, MappingRule, ShortIntegerRef, Choice, Pause

from castervoice.lib.actions import Key, Text

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R


class CustomGitHubDeskRule(MappingRule):
    pronunciation = "custom git hub desk"
    mapping = {
        "new repository": R(Key("c-n")),
        "add local repository": R(Key("c-o")),
        "clone repository": R(Key("cs-o")),
        "options | (show (settings | options))": R(Key("c-comma")),

        "changes": R(Key("c-1")),
        "history": R(Key("c-2")),
        "repos": R(Key("c-t")),
        "branches [list]": R(Key("c-b")),

        "zoom in [<n>]": R(Key("c-equals"))*Repeat(extra="n"),
        "zoom out [<n>]": R(Key("c-minus"))*Repeat(extra="n"),
        "reset zoom": R(Key("c-0")),

        "push [repository]": R(Key("c-p")),
        "pull [repository]": R(Key("cs-p")),
        "remove repository": R(Key("c-delete")),
        "view on github": R(Key("cs-g")),
        "(terminal | command prompt)": R(Key("c-backtick")),
        "explorer": R(Key("cs-f")),
        "edit": R(Key("cs-a")),

        "new branch": R(Key("cs-n")),
        "rename branch": R(Key("cs-r")),
        "delete branch": R(Key("cs-d")),

        "update from master": R(Key("cs-u")),
        "compare to branch": R(Key("cs-b")),
        "merge into current [branch]": R(Key("cs-m")),

        "compare on github": R(Key("cs-c")),
        "[create] pull request": R(Key("c-r")),

        # Composite commands
        # Switch to a specific repository
        "switch to <repository>":
            R(Key("escape/3, c-t") + Pause("30") + Text("%(repository)s") + Key("enter")),
        "fast update":
            R(Key("a-f/3, escape, tab:10") + Text("update") + Pause("30") + Key("tab:2/3, tab")),
    }
    extras = [
        ShortIntegerRef("n", 1, 10),
        Choice("repository", {
            "plans": "plans",
            "caster": "caster",
            "next": "next",
        }),
    ]
    defaults = {"n": 1}


def get_rule():
    return CustomGitHubDeskRule, RuleDetails(name="github desktop", executable="GitHubDesktop")
