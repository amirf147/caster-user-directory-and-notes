from dragonfly import MappingRule, IntegerRef, Choice, Dictation, Repeat
from castervoice.lib.actions import Key,Text
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

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


        "page <n>":
            R(Key("c-%(n)d")),
        "page [last | nine | minus | minus one]":
            R(Key("c-9")),
        "page minus <n_off_by_one>":
            R(Key("c-9, c-pgup:%(n_off_by_one)s")),
        "page <nn>":
            R(Key("c-8, c-pgdown:%(nn)s")),
        "show pages":
            R(Key("c-b/8, f1")), # workaround for when pressing just F1 doesn't work
        "hide left":
            R(Key("c-b:2")), # workaround for when pressing just F1 doesn't work

        "duplicate tab":
            R(Key("a-d/5, c-c, c-t, c-v/3, enter")),

        "[show] downloads":
            R(Key("c-j")),


        # Address bar querying with dictation
        "netzer <query>":
            R(Key("a-d/5") + Text("%(query)s") + Key("enter")),
        "hister <query>":
            R(Key("a-d/5") + Text("^%(query)s")),

        # Specific website navigation in new tab
        "go tab <website>":
            R(Key("c-t/5") + Text("%(website)s") + Key("enter")),

        # Specific website navigation via address bar
        "go <website>":
            R(Key("a-d/5") + Text("%(website)s") + Key("enter")),

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
        }),
        Choice("website", {
            "(github | git hub)": "https://github.com/",
            "(youtube | you tube)": "https://www.youtube.com/",
            "you tube lists": "https://www.youtube.com/feed/you",
            "gmail": "https://mail.google.com/mail/u/0/#inbox",
            "subscriptions": "https://www.youtube.com/feed/subscriptions",
            "school": "https://www.tuas.fi/en/",
            "pepe": "https://opiskelija.peppi.turkuamk.fi/",
            "library": "https://www.tuas.fi/en/about-us/library/tuas-library/",
            "gemini": "https://gemini.google.com/app",
            "chat gee pea tea": "https://chatgpt.com/",
            "copilot": "https://copilot.microsoft.com/",
            "ice hall": "https://www.turku.fi/en/culture-and-sports/sports/sports-facilities/ice-halls/varissuo-ice-hall"
        }),
        Dictation("query"),
    ]
    defaults = {"n": 1,}

def get_rule():
    return FirefoxExtendedRule, RuleDetails(name="fire fox extended", executable="firefox")
