from dragonfly import Function, Repeat, Choice, Dictation, MappingRule, Pause, ShortIntegerRef, Mimic

from castervoice.lib.actions import Key, Mouse

from castervoice.lib import navigation
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev
from caster_user_content.rules.apps.cli import cli_support

PYTHON_12 = ev.EXECUTABLES["pi twelve"]
PYTHON_10 = ev.EXECUTABLES["pi ten"]
PYTHON_8 = ev.EXECUTABLES["pi eight"]

class PowershellRule(MappingRule):
    mapping = {
        "go <path>": R(Text("cd %(path)s", pause=0.0) + Key("enter")),

        # Copy current directory path to clipboard
        "copy address": R(Text("'\"' + (Get-Location).Path + '\"' | Set-Clipboard", pause=0.0) + Key("enter")),
        "copy file path": R(Text("Get-Item .\ | Select-Object -ExpandProperty FullName | Set-Clipboard") + Key("left:57")),

        "dirrup": R(Text("cd ../", pause=0.0) + Key("enter")),
        "dirrup two": R(Text("cd ../../", pause=0.0) + Key("enter")),        
        "environment refresh": R(Text("$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine')") + Key("enter")),
        "get alias": R(Text("Get-Alias", pause=0.0) + Key("space")),

        # "pi twelve": R(Text("$p312 ")),
        "pi quit": R(Text("quit()", pause=0.0) + Key("enter")),
        "pi exit": R(Text("exit()", pause=0.0) + Key("enter")),

        # sqlite
        "see exit": R(Text(".exit", pause=0.0) + Key("enter")),

        "wiper": R(Text("clear", pause=0.0) + Key("enter")),
        "remove recursive": R(Text("Remove-Item -Recurse -Force -Path", pause=0.0) + Key("space")),

        # Parrot.py
        "remove sure data": R(Text("Remove-Item -Recurse -Force -Path data\\recordings\\") + Key("tab:2")),
        "start parrot": R(Text("python settings.py") + Key("enter")),

        # Redmine
        "start redmine": R(Mimic("go redmine") + Pause("50") + Text("bundle exec rails server -e production", pause=0.0) + Key("enter")),

        "start screen copy": R(Mimic("go screen copy") + Pause("50") + Text("./scrcpy", pause=0.0) + Key("enter")),

        # netstat
        "port check": R(Text("netstat -ano | findstr :", pause=0.0)),

        # CLI Tools with options
        "oh <ollama_command>": R(Text("%(ollama_command)s", pause=0.0) + Key("enter")),
        "dock <docker_command>": R(Text("%(docker_command)s", pause=0.0) + Key("enter")),
        "list <list_command>": R(Text("%(list_command)s", pause=0.0) + Key("enter")),
        
        # Python
        "pi twelve <python_command>": R(Text(PYTHON_12) + Key("space") + Text("%(python_command)s")),
        "pi ten <python_command>": R(Text(PYTHON_10) + Key("space") + Text("%(python_command)s")),
        "pi eight <python_command>": R(Text(PYTHON_8) + Key("space") + Text("%(python_command)s")),
        "pip <pip_command>": R(Text("pip %(pip_command)s")),

        # Variables
        "var <text>": R(Text("$%(text)s = \"\"", pause=0.0) + Key("left")),
        "var string <text>": R(Text("$%(text)s = @\"", pause=0.0) + Key("enter")),
        "end string": R(Text("\"@", pause=0.0) + Key("enter")),
        "ref <text>": R(Text("$%(text)s", pause=0.0)),

        # Python Virtual 
        "virtual activate": R(Text(".\.venv\Scripts\Activate.ps1", pause=0.0) + Key("enter")),
        "[virtual] deactivate": R(Text("deactivate", pause=0.0) + Key("enter")),

        # Create commit message generation prompt
        "generate commit prompt": R(Text("('I just made modifications within my caster user directory in caster an extension to the dragonfly speech recognition framework, can you generate me a commit message with the following requirements: it should only be focusing on what was added and what was removed in the diff, you do not need to reference the metadata of the diff, you do not need to talk about the coding syntax or conventions, do not need to mention the commit id, just mention briefly the commands that were added. Heres an example of a previous commit message: Add variable manipulation and commit prompt generation to PowerShell rule This commit introduces several new voice commands to the PowerShell rule in Caster: Removed dir home command. Added commands for variable manipulation: var : Creates a new variable with the given name. var string : Creates a multiline string variable. end string: Closes a multiline string variable. ref : References an existing variable. Added generate commit prompt command to copy a formatted git diff prompt to the clipboard, facilitating commit message generation. Added Dictation(text) to extras to support variable naming. These additions enhance the users ability to interact with PowerShell through voice commands, particularly for scripting and development tasks. given the following git diff.:`n' + (git diff)) | Set-Clipboard", pause=0.0)),


    }
    extras = [
        Choice("path", ev.PATHS),
        Choice("ollama_command", cli_support.OLLAMA_COMMANDS),
        Choice("docker_command", cli_support.DOCKER_COMMANDS),
        Choice("list_command", cli_support.LIST_COMMANDS),
        Choice("python_command", cli_support.PYTHON_COMMANDS),
        Choice("pip_command", cli_support.PIP_COMMANDS),
        Dictation("text"),
    ]
    defaults = {
    }

def get_rule():
    return PowershellRule, RuleDetails(name="Powershell", executable="powershell")
