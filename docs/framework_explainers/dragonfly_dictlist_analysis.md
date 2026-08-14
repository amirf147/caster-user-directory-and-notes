[ 🏠 Docs Home ](../README.md) › [ 📁 Framework Explainers ](../README.md#framework-explainers) › **Understanding Dragonfly Dynamic Data Types: Dic...**

---

# Understanding Dragonfly Dynamic Data Types: DictList, Choice, and List

In speech recognition grammar design using the Dragonfly framework, handling dynamic and static lists of words is a common requirement. When building a voice command like `"switch window to [name]"` or `"run application [app]"`, the grammar needs to know the possible options. 

Dragonfly provides several data types to handle these scenarios, primarily `Choice`, `List`, and `DictList`. This document breaks down how each works and when to use them.

## 1. The `Choice` Element

### What it is
A static, hardcoded dictionary mapping spoken forms to their corresponding programmatic values.

### How it is used
You pass a standard Python dictionary to the `Choice` element when defining a rule. The keys are the spoken words, and the values are what get passed to your action function.

**Code Example:**
```python
from dragonfly import Choice, MappingRule

class MyRule(MappingRule):
    mapping = {
        "open <app>": lambda app: print(f"Opening {app}") # `app` receives the mapped value
    }
    extras = [
        Choice("app", {
            "browser": "chrome.exe",
            "editor": "vscode.exe",
            "terminal": "powershell.exe"
        })
    ]
```

### Why use it?
`Choice` is ideal for options that **do not change at runtime**. If you know exactly what the options are when you write the code, `Choice` is the most performant and straightforward tool. It cannot be updated after the grammar is loaded without tearing down and reloading the entire rule.

## 2. The `List` Element

### What it is
A dynamic sequence of words. Unlike `Choice`, a `List` allows you to change its contents *at runtime* after the grammar has been loaded into the speech engine.

### How it is used
You create a `List` object, pass a `ListRef` to your rule's `extras`, and you can update the `List` whenever you want via its `.set()` method.

**Code Example:**
```python
from dragonfly import List, ListRef, MappingRule

# Initializing a List with default values
dynamic_names = List("names_list", ["alice", "bob", "charlie"])

class GreetRule(MappingRule):
    mapping = {
        "hello <name>": lambda name: print(f"Hello {name}")
    }
    extras = [
        ListRef("name", dynamic_names)
    ]

# Later in your code (e.g., triggered by an event or timer), update the list dynamically:
dynamic_names.set(["dave", "eve", "frank"])
```

### Why use it?
When you only need the *spoken form* of the word and the options change dynamically. A classic example is creating a voice command to select files in a changing directory, or referencing the names of people currently in a chat room.

## 3. The `DictList` Element

### What it is
A hybrid between `Choice` and `List`. It is a dynamic list that maps spoken forms (keys) to programmatic values, and its contents can be updated at runtime. 

### How it is used
You instantiate a `DictList`, pass a `DictListRef` into your rule, and update it via its `.set()` method by passing a dictionary.

**Code Example:**
```python
from dragonfly import DictList, DictListRef, MappingRule

# Initializing an empty DictList
open_windows = DictList("windows_dict")

class WindowRule(MappingRule):
    mapping = {
        "switch to <window>": lambda window: window.set_foreground()
    }
    extras = [
        DictListRef("window", open_windows)
    ]

# In a background thread or timer, update the options dynamically:
# The spoken word maps directly to complex objects
open_windows.set({
    "chrome": chrome_window_object,
    "slack": slack_window_object
})
```

### Why use it?
This is the most powerful tool for mapping dynamic spoken words to complex objects or values at runtime. 

In the window switching example from `Caster-LexiconCode`, the spoken words ("chrome", "slack") need to map to the actual Win32 window objects in memory so that `set_foreground()` can be called on them. Since open windows change constantly, a static `Choice` won't work, and a `List` wouldn't hold the window objects (only their names). `DictList` solves this perfectly by providing dynamic key-value mapping.

## 4. Summary of Use Cases

| Data Type | Mutability (Runtime Updates) | Data Structure | Best Used For |
| :--- | :--- | :--- | :--- |
| **`Choice`** | Static (No) | Dictionary (Key -> Value) | Hardcoded mappings (e.g., phonetic alphabet, static app list) |
| **`List`** | Dynamic (Yes) | Sequence (Array of strings) | Dynamically changing words where the word itself is the value (e.g., listing filenames) |
| **`DictList`**| Dynamic (Yes) | Dictionary (Key -> Value) | Dynamically changing mappings to objects (e.g., open window objects, changing IP addresses) |

## 5. Performance and Implementation Notes

*   **Grammar Compilation Overhead:** Every time `.set()` is called on a `List` or `DictList`, the underlying speech recognition engine (like Windows Speech Recognition or Kaldi) must recompile that specific part of the grammar on the fly. While this is significantly faster than reloading an entire rule, calling `.set()` too frequently (e.g., in a tight loop every 50ms) can cause performance hiccups, high CPU usage, or dropped utterances.
*   **Engine Support:** `DictList` and `List` support varied slightly in older versions of Dragonfly across different backend engines. However, in modern Dragonfly (supporting Kaldi, WSR, and Natlink), they are uniformly supported and handled safely by the engine wrappers.
