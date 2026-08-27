"""
Integrated IDE Terminal Rule

Activates shell and command-line navigation shortcuts dynamically when focus
is inside an integrated terminal (Antigravity IDE, VS Code, Cursor, Windsurf, VSCodium).

Gated via Active Desktop Context Engine (ADCE) FuncContext predicate.

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: LGPL-3.0-or-later
"""

from dragonfly import Dictation, Function, Key, MappingRule, Repeat, ShortIntegerRef, Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content.util.adce_bridge import is_ide_terminal_focused, print_adce_status


class IDETerminalRule(MappingRule):
    mapping = {
        # Shell Navigation & Flow Control
        "clear [terminal]": R(Key("c-l")),
        "kill terminal": R(Key("c-shift-w")),
        "scroll up [<n>]": R(Key("s-pageup") * Repeat(extra="n")),
        "scroll down [<n>]": R(Key("s-pagedown") * Repeat(extra="n")),
        "cancel command": R(Key("c-c")),
        "exit shell": R(Text("exit") + Key("enter")),
        "line up": R(Key("up")),
        "line down": R(Key("down")),
        # Git Workflow Commands
        "git status": R(Text("git status") + Key("enter")),
        "git diff": R(Text("git diff") + Key("enter")),
        "git diff cached": R(Text("git diff --cached") + Key("enter")),
        "git branch": R(Text("git branch -a") + Key("enter")),
        "git log": R(Text("git log -n 5 --oneline") + Key("enter")),
        "git pull": R(Text("git pull") + Key("enter")),
        "git push": R(Text("git push") + Key("enter")),
        "git fetch": R(Text("git fetch --all") + Key("enter")),
        "git stash": R(Text("git stash") + Key("enter")),
        "git stash pop": R(Text("git stash pop") + Key("enter")),
        "git add all": R(Text("git add -A") + Key("enter")),
        # Build, Test & Run Commands
        "run tests": R(Text("npm test") + Key("enter")),
        "run build": R(Text("npm run build") + Key("enter")),
        "run dev": R(Text("npm run dev") + Key("enter")),
        "cargo check": R(Text("cargo check") + Key("enter")),
        "cargo test": R(Text("cargo test") + Key("enter")),
        "cargo build": R(Text("cargo build") + Key("enter")),
        "python run": R(Text("py -3.10 ") + Key("tab")),
        # Terminal Split & Layout
        "split terminal": R(Key("c-shift-5")),
        "focus next terminal": R(Key("a-right")),
        "focus previous terminal": R(Key("a-left")),
        # Voice Ping & Diagnostic HUD Status
        "terminal voice ping": R(Text("echo '>>> ADCE TERMINAL CONTEXT VERIFIED <<<'") + Key("enter")),
        "(adce status | context status | show zone)": R(Function(print_adce_status)),
    }

    extras = [
        ShortIntegerRef("n", 1, 100),
        Dictation("text"),
    ]
    defaults = {
        "n": 1,
        "text": "",
    }


def get_rule():
    return IDETerminalRule, RuleDetails(
        name="IDETerminal",
        executable=["Code", "Antigravity", "Antigravity IDE", "cursor", "Windsurf", "VSCodium", "code - oss"],
        title=[
            "Visual Studio Code",
            "Antigravity",
            "Antigravity IDE",
            "Cursor",
            "Windsurf",
            "VSCodium",
        ],
        function_context=is_ide_terminal_focused,
    )
