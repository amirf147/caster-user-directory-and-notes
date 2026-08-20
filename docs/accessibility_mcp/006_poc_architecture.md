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

To keep this performant and adhere to the design patterns we discussed (Event-Driven rather than Polling), the PoC will consist of three main logical components running in a single Python script.

### Component A: The Event Hook (The Trigger)
We will not use a `while True` loop that checks the screen every second. Instead, we will use Python's `ctypes` library to register a `SetWinEventHook` with the Windows OS.
* **What it listens for:** `EVENT_SYSTEM_FOREGROUND` (Window switch) and `EVENT_OBJECT_FOCUS` (Clicking inside a window).
* **What it does:** When an event fires, it passes the window handle (`HWND`) to the Extractor.

### Component B: The UIA Extractor (The Brain)
When triggered by the Event Hook, this component uses the `uiautomation` Python library to interrogate the focused window.
* Instead of scraping the *entire* screen, it will use the focused element as the root and extract:
  1. The Application Name (e.g., "Google Chrome")
  2. The Window Title (e.g., "GitHub - User/Repo")
  3. The focused control type (e.g., "Edit", "Document", "Button")
  4. A localized tree of the immediate parents and children of the focused element.

### Component C: The Formatter (The Output)
This takes the raw UIAutomation objects and formats them into a clean, LLM-friendly JSON structure or a readable terminal tree, then prints it to standard output (your side terminal).

---

## 3. Workflow for the Proof of Concept

Here is how we will actually build and test this:

1. **Setup:** Create a standalone Python script (e.g., `context_poc.py`).
2. **Implementation:** We will write a lightweight script using the `uiautomation` library.
3. **Execution via Caster:** We will add a temporary rule in your Caster user directory to launch this script via a voice command.
4. **Testing:**
   * You say the command.
   * A terminal window pops up.
   * You click on a web browser. The terminal instantly prints the browser's tab name and focused text box.
   * You click back to VS Code. The terminal instantly prints the line of code your cursor is on.

## 4. Next Steps

If you approve of this architecture, our next step is to actually write the `context_poc.py` script. We can start with a very basic version that just prints the title of whatever window you click on, and then iteratively add the deeper UI tree extraction.
