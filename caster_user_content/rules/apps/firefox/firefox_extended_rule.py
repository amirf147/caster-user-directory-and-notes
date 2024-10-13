from dragonfly import MappingRule, IntegerRef, Choice, Dictation, Repeat
from castervoice.lib.actions import Key,Text
from castervoice.lib.merge.state.short import R
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.temporary import Store, Retrieve


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
            R(Key("c-b/8, f1")), # workaround for when pressing just F1 doesn't work
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
        "netzer <query>":
            R(Key("a-d/5") + Text("%(query)s") + Key("enter")),
        "netzer tab <query>":
            R(Key("c-t/5") + Text("%(query)s") + Key("enter")),
        "hister <query>":
            R(Key("a-d/5") + Text("^%(query)s")),
        "hister tab <query>":
            R(Key("c-t/5") + Text("^%(query)s")),

        # Specific website navigation in new tab
        "go tab <website>":
            R(Key("c-t/5") + Text("%(website)s") + Key("enter")),

        # Specific website navigation via address bar
        "go <website>":
            R(Key("a-d/5") + Text("%(website)s") + Key("enter")),

        # Link navigation
        "jink <query>":
            R(Key("c-f/5") + Text("%(query)s") + Key("enter/5, escape/3, enter")),
        "jinx <query>":
            R(Key("c-f/5") + Text("%(query)s") + Key("enter/5")),

        "google that":
            R(Store(remove_cr=True) + Key("c-t/5") + Retrieve() + Key("enter")),

        "go clipboard":
            R(Key("a-d/5") + Key("c-v") + Key("enter")),

        "go tab clipboard":
            R(Key("c-t/5") + Key("cs-v") + Key("enter")),

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
        Choice("website", {
            "(github | git hub)": "https://github.com/",
            "(youtube | you tube)": "https://www.youtube.com/",
            "you tube lists": "https://www.youtube.com/feed/you",
            "youtube history": "https://www.youtube.com/feed/history",
            "gmail": "https://mail.google.com/mail/u/0/#inbox",
            "subscriptions": "https://www.youtube.com/feed/subscriptions",
            "school": "https://www.tuas.fi/en/",
            "pepe": "https://opiskelija.peppi.turkuamk.fi/",
            "it's learning": "https://turkuamk.itslearning.com/",
            "library": "https://www.tuas.fi/en/about-us/library/tuas-library/",
            "theseus": "https://www.theseus.fi/",
            "gemini": "https://gemini.google.com/app",
            "chat gee pea tea": "https://chatgpt.com/",
            "copilot": "https://copilot.microsoft.com/",
            "ice hall": "https://www.turku.fi/en/culture-and-sports/sports/sports-facilities/ice-halls/varissuo-ice-hall",
            "read it": "https://reddit.com/",
        }),
        Dictation("query"),
    ]
    defaults = {"n": 1,}

def get_rule():
    return FirefoxExtendedRule, RuleDetails(name="fire fox extended", executable="firefox")
