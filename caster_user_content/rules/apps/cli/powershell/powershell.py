from dragonfly import Function, Repeat, Choice, Dictation, MappingRule, Pause, ShortIntegerRef, Mimic

from castervoice.lib.actions import Key, Mouse

from castervoice.lib import navigation
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

from caster_user_content import environment_variables as ev
from caster_user_content.rules.apps.cli import cli_support
from caster_user_content.util.generate_rdescript import generate_rdescript
from caster_user_content.util.text import text_to_clipboard

PYTHON_12 = ev.EXECUTABLES["pi twelve"]
PYTHON_10 = ev.EXECUTABLES["pi ten"]
# PYTHON_8 = ev.EXECUTABLES["pi eight"]

class PowershellRule(MappingRule):
    mapping = {
        "show (settings | options)": R(Key("a-space, p")),
        "show font": R(Key("a-space, p/5, s-tab, right")),
        "show layout": R(Key("a-space, p/5, s-tab, right:2")),
        "show colors": R(Key("a-space, p/5, s-tab, right:3")),
        "show terminal": R(Key("a-space, p/5, s-tab, right:4")),
        
        # Editing Modes
        "scroll mode": R(Key("a-space, e, l")),

        "zoom in [<n>]": R(Key("a-space, p/5, s-tab, right, tab, down:%(n)d, enter")),
        "zoom out [<n>]": R(Key("a-space, p/5, s-tab, right, tab, up:%(n)d, enter")),

        "go <path>": R(Text("Push-Location \"%(path)s\"", pause=0.0) + Key("enter")),
        "go clipboard": R(Text("Push-Location \"\"", pause=0.0) + Key("left, c-v/3, enter")),
        "go back": R(Text("Pop-Location", pause=0.0) + Key("enter")),

        # Process
        "search process": R(Text("Get-Process | Where-Object { $_.Name -like \"\" } | Select-Object Name, Id, CPU, WorkingSet | Format-Table -AutoSize", pause=0.0) + Key("left:70")),

        # File/Folder Operations
        "tree": R(Text("tree", pause=0.0)),
        "tree eff": R(Text("tree /f", pause=0.0)),
        "tree eff to clipboard": R(Text("tree /f | Set-Clipboard", pause=0.0)),
        "copy address": # Copy current directory path to clipboard
            R(Text("'\"' + (Get-Location).Path + '\"' | Set-Clipboard", pause=0.0) + Key("enter")),
        "copy path":
            R(Text("Get-Item .\ | Select-Object -ExpandProperty FullName | Set-Clipboard", pause=0.0) + Key("left:57")),
        "search file are": R( # Search for a file in the current directory and all sub directories
            Text("Get-ChildItem -Recurse -Filter ", pause=0.0)),
        "search file here": R( # Search for a file in the current directory
            Text("Get-ChildItem -Filter ", pause=0.0)),
        "search word": R( # Search for a string in all files
            Text("Get-ChildItem -Recurse -File | Select-String -Pattern \"\" -SimpleMatch") + Key("left:14")),
        "search word python": R( # Search for a string in python files
            Text("Get-ChildItem -Recurse -File -Include \"*.py\" | Select-String -Pattern \"\" -SimpleMatch") + Key("left:14")),
        "copy recent name":
            R(Text("(Get-ChildItem -Path . -File -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 1).Name -replace '[\\r\\n]' | Set-Clipboard", pause=0.0) +
            Pause("20") + Key("enter"), 
            rdescript=generate_rdescript("copy recent name", "FILE/FOLDER OPERATIONS", "Get the most recently modified file in the current directory")),
        "copy recent contents":
            R(Text("Get-Content -Path ((Get-ChildItem -Path . -File -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName) -Raw | Set-Clipboard", pause=0.0)
            + Pause("20") + Key("enter"),
            rdescript=generate_rdescript("copy recent contents", "FILE/FOLDER OPERATIONS", "Get the contents of the most recently modified file in the current directory")),

        "dirrup": R(Text("Push-Location ../", pause=0.0) + Key("enter")),
        "dirrup two": R(Text("Push-Location ../../", pause=0.0) + Key("enter")),
        "dirrup three": R(Text("Push-Location ../../../", pause=0.0) + Key("enter")),

        # Environment Variables
        "environment refresh": R(Text("$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine')") + Key("enter")),
        "envo": R(Text("$env:", pause=0.0)),
        "show path": R(Text("$env:Path -split ';' | ForEach-Object { $i=0 } { \"[$i] $_\"; $i++ }", pause=0.0)),

        # Aliases
        "get alias": R(Text("Get-Alias", pause=0.0) + Key("space")),
        "show (aliases | alias)": R(Text("Get-Alias | Out-GridView", pause=0.0) + Key("enter")),

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

        "start screen copy": R(Text("./scrcpy", pause=0.0) + Key("enter")),

        # netstat
        "port check": R(Text("netstat -ano | findstr :", pause=0.0)),

        # CLI Tools with options
        "oh <ollama_command>": R(Text("%(ollama_command)s ", pause=0.0)),
        "dock <docker_command>": R(Text("%(docker_command)s ", pause=0.0)),
        "list [<list_command>]": R(Text("%(list_command)s", pause=0.0) + Key("enter")),

        # Ollama
        "oh create model": R(Text("ollama create --file .\\Modelfile") + Key("left:19, space:2, left")),
        "run model": R(Text(f"{PYTHON_12} .\\ollama_test.py")),

        # History
        "show history": R(Text("Invoke-History") + Key("enter")),
        "hister clip <n501>": R( # Places command (via id) from history to clipboard
            Text("(Get-History -Id %(n501)s).CommandLine | Set-Clipboard") + Key("enter")),
        "copy last command": R(Text("(Get-History -Count 1).CommandLine | Set-Clipboard", pause=0.0) + Key("enter")),
        
        # Python
        "pi twelve <python_command>": R(Text(PYTHON_12) + Key("space") + Text("%(python_command)s")),
        "pi ten <python_command>": R(Text(PYTHON_10) + Key("space") + Text("%(python_command)s")),
        "pip <pip_command>": R(Text("pip %(pip_command)s")),
        "pi repple": R(Text("python") + Key("enter")),
        "pi ten repple": R(Text(PYTHON_10) + Key("enter")),
        "pi twelve repple": R(Text(PYTHON_12) + Key("enter")),

        # Variables
        "var <text>": R(Text("$%(text)s = \"\"", pause=0.0) + Key("left")),
        "var string <text>": R(Text("$%(text)s = @\"", pause=0.0) + Key("enter")),
        "end string": R(Text("\"@", pause=0.0) + Key("enter")),
        "ref <text>": R(Text("$%(text)s", pause=0.0)),

        # Python Virtual 
        "virtual activate": R(Text(".\.venv\Scripts\Activate.ps1", pause=0.0) + Key("enter")),
        "[virtual] deactivate": R(Text("deactivate", pause=0.0) + Key("enter")),

        # Create commit message generation prompt
        "generate commit prompt": R(
            # Places the prompt builder text and commands into the clipboard for faster output
            # This is much faster than using Text("")
            Function(text_to_clipboard, text=ev.POWERSHELL_COMMIT_PROMPT_BUILDER) +
            Pause("20") + Key("c-v/3,enter")),

        # String Manipulation
        "to clipboard": R(Text(" | Set-Clipboard", pause=0.0)),
        "dot split": R(Text(".Split(\"\")", pause=0.0) + Key("left:2")),
        "split space": R(Text(".Split(\" \")", pause=0.0)),
    }
    extras = [
        Choice("path", ev.PATHS),
        Choice("ollama_command", cli_support.OLLAMA_COMMANDS),
        Choice("docker_command", cli_support.DOCKER_COMMANDS),
        Choice("list_command", cli_support.LIST_COMMANDS),
        Choice("python_command", cli_support.PYTHON_COMMANDS),
        Choice("pip_command", cli_support.PIP_COMMANDS),
        Dictation("text"),
        ShortIntegerRef("n", 1, 11),
        ShortIntegerRef("n501", 1, 501),
    ]
    defaults = {
        "list_command": cli_support.LIST_COMMANDS["names"],
        "n": 1,
    }

def get_rule():
    return PowershellRule, RuleDetails(name="Powershell", executable="powershell")
