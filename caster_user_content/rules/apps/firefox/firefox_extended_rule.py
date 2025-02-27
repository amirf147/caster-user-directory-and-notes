from dragonfly import MappingRule, IntegerRef, Choice, Dictation, Repeat, Function
from castervoice.lib.actions import Key,Text
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.temporary import Store, Retrieve

from caster_user_content import environment_variables as ev


from datetime import datetime
import os
import pyperclip
import sys
import subprocess


def _search_youtube(query):
    formatted_search = query.replace(" ", "+")
    formatted_url = f"https://www.youtube.com/results?search_query={formatted_search}"
    Key("a-d/5").execute() \
        + Text("%(formatted_url)s").execute({"formatted_url": formatted_url}) \
        + Key("enter").execute()

def _save_to_job_postings():
    try:
        # Check if directory exists
        if not os.path.exists(ev.PATHS["job postings"]):
            print(f"Error: Directory does not exist: {ev.PATHS['job postings']}")
            return

        content = pyperclip.paste()
        
        # Get the path to the save_to_text.py script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, "..", "..", "..", "util", "save_to_text.py")
        
        # Start the process detached from the parent
        if os.name == 'nt':  # Windows
            DETACHED_PROCESS = 0x00000008
            SW_SHOW = 5
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = SW_SHOW
            
            process = subprocess.Popen([
                sys.executable, 
                script_path, 
                ev.PATHS["job postings"],
                "--always-on-top"  # Add this flag to be handled in save_to_text.py
            ], stdin=subprocess.PIPE, 
               text=True,
               creationflags=DETACHED_PROCESS,
               startupinfo=startupinfo)
        
        # Send the content without waiting for completion
        process.stdin.write(content)
        process.stdin.close()
            
    except Exception as e:
        print(f"Error saving text: {str(e)}")


class FirefoxExtendedRule(MappingRule):
    pronunciation = "extended fire fox"
    mapping = {
        
        "(new window|win new)":
            R(Key("c-n")),
        "new tab [<n>]|tab new [<n>]":
            R(Key("c-t") * Repeat(extra="n")),
        "reopen tab [<n>]|tab reopen [<n>]":
            R(Key("cs-t")) * Repeat(extra="n"),
        "close tab [<n>]|tab close [<n>]":
            R(Key("c-w")) * Repeat(extra='n'),
        "win close|close all tabs":
            R(Key("cs-w")),

        "go back [<n>]":
            R(Key("a-left/20")) * Repeat(extra="n"),
        "go forward [<n>]":
            R(Key("a-right/20")) * Repeat(extra="n"),

        "zoom in [<n>]":
            R(Key("c-plus/20")) * Repeat(extra="n"),
        "zoom out [<n>]":
            R(Key("c-minus/20")) * Repeat(extra="n"),
        "zoom reset":
            R(Key("c-0")),
        "caret browsing":
            R(Key("f7")),

        "page <n>":
            R(Key("c-%(n)d")),
        "page (last | minus | minus one)":
            R(Key("c-9")),
        "page minus <n_off_by_one>":
            R(Key("c-9, c-pgup:%(n_off_by_one)s")),
        "page <nn>":
            R(Key("c-8/3, c-pgdown:%(nn)s")),
        "page over [<n>]":
            R(Key("c-pgup/3"))*Repeat(extra="n"),
        "page under [<n>]":
            R(Key("c-pgdown/3"))*Repeat(extra="n"),

        "show pages":
            R(Key("c-b/30, f1")), # workaround for when pressing just F1 doesn't work
        "hide left":
            R(Key("c-b:2")), # workaround for when pressing just F1 doesn't work

        "duplicate page":
            R(Key("a-d/5, a-enter")),
        "pop out page":
            R(Key("a-d/5, s-enter")),

        "[show] downloads":
            R(Key("c-j")),

        "address bar":
            R(Key("a-d")),

        # Address bar querying with dictation
        "netzer <query>": R(Key("a-d/5") + Text("%(query)s") + Key("enter")),
        "netzer tab <query>": R(Key("c-t/5") + Text("%(query)s") + Key("enter")),
        "netzer window <query>": R(Key("c-n/120") + Text("%(query)s") + Key("enter")),
        "reddit <query>": R(Key("a-d/5") + Text("%(query)s reddit") + Key("enter")),
        "reddit tab <query>": R(Key("c-t/5") + Text("%(query)s reddit") + Key("enter")),
        "reddit window <query>": R(Key("c-n/120") + Text("%(query)s reddit") + Key("enter")),
        "hister <query>": R(Key("a-d/5") + Text("^%(query)s")),
        "hister tab <query>": R(Key("c-t/5") + Text("^%(query)s")),
        "hister window <query>": R(Key("c-n/120") + Text("^%(query)s")),
        "bookzer <query>": R(Key("a-d/5") + Text("*%(query)s")),
        "bookzer tab <query>": R(Key("c-t/5") + Text("*%(query)s")),
        "bookzer window <query>": R(Key("c-n/120") + Text("*%(query)s")),

        # Specific website navigation in new tab
        "go tab <website>":
            R(Key("c-t/5") + Text("%(website)s") + Key("enter")),

        # Specific website navigation via address bar
        "go <website>":
            R(Key("a-d/5") + Text("%(website)s") + Key("enter")),
        "go window <website>":
            R(Key("c-n/120") + Text("%(website)s") + Key("enter")),

        # Link navigation
        "jink <query>":
            R(Key("c-f/5") + Text("%(query)s") + Key("enter/5, escape/3, enter")),
        "jinx <query>":
            R(Key("c-f/5") + Text("%(query)s") + Key("enter/5")),

        # Googling selected text
        "google that":
            R(Store(remove_cr=True) + Key("c-t/5") + Retrieve() + Key("enter")),
        "google that window":
            R(Store(remove_cr=True) + Key("c-n/120") + Retrieve() + Key("enter")),

        # Pasting clipboard content into address bar
        "go clipboard":
            R(Key("a-d/5") + Key("c-v") + Key("enter")),
        "go tab clipboard":
            R(Key("c-t/5") + Key("cs-v") + Key("enter")),
        "go window clipboard":
            R(Key("c-n/120") + Key("cs-v") + Key("enter")),

        # Searching YouTube
        "you search <query>":
            R(Function(_search_youtube)),
        "you search window <query>":
            R(Key("c-n/60") + Function(_search_youtube)),
        "you search tab <query>":
            R(Key("c-t") + Function(_search_youtube)),

        # Translations    
        "translate that": # Translates the selection via the context menu
            R(Key("s-f10/3, down:6, enter")),
        "translate page": # Presses the translate button in the address bar and enables page translation
            R(Key("a-d/5, tab, right:4, left:2, enter/50, tab:3, enter")),
        "remove translation":
            R(Key("a-d/5, tab, right:4, left:2, enter/50, tab:2, enter")),
        
        "text to job postings":
            R(Store() + Function(_save_to_job_postings)),

        # Developer Tools
        "show tools": R(Key("f12")),
        "show console": R(Key("cs-k")),
        "show debugger": R(Key("cs-z")), # Doesn't always work
        "show network": R(Key("cs-e")),
        "tool under": R(Key("c-]")),
        "tool over": R(Key("c-[")),
    }
    
    extras = [
        IntegerRef("n", 1, 9),
        Choice("n_off_by_one", {
            "two": "1",
            "three": "2",
            "four": "3",
            "five": "4",
            "six": "5",
            "seven": "6",
            "eight": "7",
            "nine": "8",
            "ten": "9",
        }),
        Choice("nn", {
            "nine": "1",
            "ten": "2",
            "eleven": "3",
            "twelve": "4",
            "thirteen": "5",
            "fourteen": "6",
            "fifteen": "7",
            "sixteen": "8",
            "seventeen": "9",
            "eighteen": "10",
            "nineteen": "11",
            "twenty": "12",
            "twenty one": "13",
            "twenty two": "14",
            "twenty three": "15",
            "twenty four": "16",
            "twenty five": "17",
            "twenty six": "18",
            "twenty seven": "19",
            "twenty eight": "20",
            "twenty nine": "21",
            "thirty": "22",
        }),
        Choice("website", ev.WEBSITES),
        Dictation("query"),
    ]
    defaults = {"n": 1,}

def get_rule():
    return FirefoxExtendedRule, RuleDetails(name="fire fox extended", executable="firefox")
