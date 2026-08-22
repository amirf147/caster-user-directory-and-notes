[ 🏠 Docs Home ](../README.md) › [ 📁 Accessibility MCP ](CONTEXT.md) › **006: PoC Architecture**

---

# Proof of Concept: Python Desktop Context Engine

## 1. Critique and Evaluation of Your Proposal

Your intuition for how to approach this Proof of Concept (PoC) is spot on. Here is a critique and validation of your key thoughts:

### Is Python the right choice for this?
**Yes, absolutely.** While a production-grade, enterprise context engine (like the one discussed in previous documents) might eventually need to be written in Rust or C++ to squeeze out every microsecond of performance and handle COM memory perfectly, Python is the ultimate language for a PoC. 
Libraries like `uiautomation` (a wrapper around Microsoft's UIAutomation COM API) or `pywinauto` make it incredibly easy to hook into Windows events and walk accessibility trees without writing hundreds of lines of C++ boilerplate. It will allow us to validate the *logic* quickly.

### Do we need a hyper-performant Vector Database right now?
**No, definitely not.** Introducing a vector database (like ChromaDB or FAISS) at this stage is massive architectural overkill and will just slow down development. 
For the PoC, your idea is exactly right: we just want to output a live **JSON object** or print a visual **tree representation** directly to a terminal. The goal right now is simply to prove: *"Can we reliably detect when the user switches apps, and can we instantly grab the text/structure of that app?"* Once we have clean JSON, feeding it to an LLM or a Vector DB is the easy part.

### Caster Integration
Triggering this from Caster is a great workflow test. We can create a simple voice command (e.g., "Start Context Engine") that spawns this Python script as a background subprocess. You can keep a side terminal open to watch it print the UI tree in real-time as you click around your browser or VS Code.

---

## 2. Proposed Architecture for the PoC

```
[Windows OS Events (SetWinEventHook)]
       │
       ▼
[Event Listener (Python ctypes / pywin32)]
       │  (EVENT_SYSTEM_FOREGROUND, EVENT_OBJECT_FOCUS)
       ▼
[Active Element Inspector (uiautomation)]
       │  - Extract Window Title & Process Name
       │  - Extract Focused Element (Type, Name, BoundingBox)
       │  - Walk Up Tree (Ancestry Hierarchy)
       │  - (Optional) Walk Down Tree (Extract Immediate Text Children)
       ▼
[Structured Context Graph (Python Dict / JSON)]
       │
       ▼
[Terminal Visualizer (Rich or simple ANSI prints)]
```

---

## 3. Step-by-Step Implementation Blueprint

### Step 1: Install Dependencies
We will need `uiautomation` and `pywin32`.
```bash
py -3.10 -m pip install uiautomation pywin32
```

### Step 2: Build the Event Hook Engine (`scripts/context_poc.py`)
We will write a standalone script that:
1. Registers a Win32 event hook for `EVENT_SYSTEM_FOREGROUND` (when the active window changes) and `EVENT_OBJECT_FOCUS` (when the user clicks a button, focuses a text box, switches tabs, etc.).
2. Uses `uiautomation` to inspect the focused UI element and its parent hierarchy.
3. Formats the output into a clean, colored terminal view.

### Step 3: Integrate with Caster (`caster_user_content/rules/global/context_engine_launcher.py`)
We will create a Caster rule with a voice command:
* `"launch context engine"` $\rightarrow$ Spawns `scripts/context_poc.py` in a new terminal window using `subprocess.Popen(["py", "-3.10", "scripts/context_poc.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)`.
