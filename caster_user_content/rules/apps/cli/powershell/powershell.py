from dragonfly import Function, Repeat, Choice, Dictation, MappingRule, Pause, ShortIntegerRef, Mimic

from castervoice.lib.actions import Key, Mouse

from castervoice.lib import navigation
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev
from caster_user_content.rules.apps.cli.cli_support import OLLAMA_COMMANDS, DOCKER_COMMANDS

class PowershellRule(MappingRule):
    mapping = {
        "go <path>": R(Text("cd %(path)s") + Key("enter")),

        "dirrup": R(Text("cd ../") + Key("enter")),
        "list names": R(Text("Get-ChildItem -Name") + Key("enter")),
        "list folders": R(Text("Get-ChildItem -Directory -Name") + Key("enter")),
        "environment refresh": R(Text("$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine')") + Key("enter")),
        "get alias": R(Text("Get-Alias") + Key("space")),

        # "pi twelve": R(Text("$p312 ")),
        "pi quit": R(Text("quit()") + Key("enter")),
        "pi exit": R(Text("exit()") + Key("enter")),

        # sqlite
        "see exit": R(Text(".exit") + Key("enter")),

        "wiper": R(Text("clear") + Key("enter")),

        # Redmine
        "start redmine": R(Mimic("go redmine") + Pause("50") + Text("bundle exec rails server -e production") + Key("enter")),

        "start screen copy": R(Mimic("go screen copy") + Pause("50") + Text("./scrcpy") + Key("enter")),

        # netstat
        "port check": R(Text("netstat -ano | findstr :")),

        # CLI Tools with options
        "oh <ollama_command>": R(Text("%(ollama_command)s") + Key("enter")),
        "dock <docker_command>": R(Text("%(docker_command)s") + Key("enter")),

        # Variables
        "var <text>": R(Text("$%(text)s = \"\"") + Key("left")),
        "var string <text>": R(Text("$%(text)s = @\"") + Key("enter")),
        "end string": R(Text("\"@") + Key("enter")),
        "ref <text>": R(Text("$%(text)s")),

        # Create commit message generation prompt
        "generate commit prompt": R(Text("('I just made modifications within my caster user directory in caster an extension to the dragonfly speech recognition framework, can you generate me a commit message with the following requirements: it should only be focusing on what was added and what was removed in the diff, you do not need to reference the metadata of the diff, you do not need to talk about the coding syntax or conventions, do not need to mention the commit id, just mention briefly the commands that were added. Heres an example of a previous commit message: Add variable manipulation and commit prompt generation to PowerShell rule This commit introduces several new voice commands to the PowerShell rule in Caster: Removed dir home command. Added commands for variable manipulation: var : Creates a new variable with the given name. var string : Creates a multiline string variable. end string: Closes a multiline string variable. ref : References an existing variable. Added generate commit prompt command to copy a formatted git diff prompt to the clipboard, facilitating commit message generation. Added Dictation(text) to extras to support variable naming. These additions enhance the users ability to interact with PowerShell through voice commands, particularly for scripting and development tasks. given the following git diff.:`n' + (git diff)) | Set-Clipboard", pause=0.0)),
    }
    extras = [
        Choice("path", ev.PATHS),
        Choice("ollama_command", OLLAMA_COMMANDS),
        Choice("docker_command", DOCKER_COMMANDS),
        Dictation("text"),
    ]
    defaults = {
    }

def get_rule():
    return PowershellRule, RuleDetails(name="Powershell", executable="powershell")
