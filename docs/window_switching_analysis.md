# Window Switching Implementation Breakdown

This document provides a full educational breakdown of the window switching feature implemented in the `Caster-LexiconCode` repository, an in-depth critique of its design, and instructions on how to integrate it into your custom Caster setup branch.

## 1. Introduction and Architecture

The window switching feature allows users to switch between open applications by speaking words found in the window titles. The implementation is cleanly separated into two main files:

*   [**`window_mgmt_rule.py`**](https://github.com/LexiconCode/Caster/blob/windows_switch_manager/castervoice/rules/core/navigation_rules/window_mgmt_rule.py): Defines the voice commands (e.g., `"window switch <windows>"`) and maps them to the backend logic.
*   [**`window_mgmt_rule_support.py`**](https://github.com/LexiconCode/Caster/blob/windows_switch_manager/castervoice/rules/core/navigation_rules/window_mgmt_rule_support.py): Contains the core logic for tracking open windows, resolving spoken keywords to specific window handles, and executing the focus shift.

The architecture relies on a **background polling mechanism**. A timer runs every 2 seconds to scan the OS for all open windows, extracting words from their titles, and dynamically injecting them into the speech recognition grammar.

## 2. Core Mechanics

### Background Polling (`refresh_open_windows_dictlist`)
The mechanism relies on a Dragonfly timer to periodically fetch windows.

**Citation (Timer Initialization):**
```python
def set(self):
    if self.timer is None:
        self.timer = get_engine().create_timer(refresh_open_windows_dictlist, 2)
        self.timer.start()
```

1.  **Window Scanning**: It calls `Window.get_all_windows()` to retrieve every window currently known to the OS.
2.  **Filtering**: It explicitly ignores system background tasks, hidden windows, and specific utilities (like `C:\Windows` executables or the Dragonfly results box).
3.  **Tokenization**: It splits the title of each valid window into individual words. A custom function (`lower_if_not_abbreviation`) attempts to preserve uppercase abbreviations (like "IDE") while lowercasing standard words.
4.  **Grammar Injection**: These words are stored in a dictionary mapping the word to a list of matching window objects. This dictionary is then pushed into a Dragonfly `DictList` (`open_windows_dictlist`).

**Citation (Updating DictList):**
```python
window_options = {k: v for k, v in six.iteritems(window_options) if v is not None}
open_windows_dictlist.set(window_options)
```
Because the grammar uses a `DictListRef` pointing to this `DictList`, the speech engine instantly knows the names of all currently open windows without requiring a manual grammar reload.

### Window Switching Logic (`switch_window`)
When the user utters `"window switch <windows>"`:
1.  The command passes the list of spoken keywords into `switch_window()`.
2.  It performs an intersection. For example, if you say "window switch chrome github", it finds windows that contain *both* "chrome" and "github" in their title.

**Citation (Window Intersection Logic):**
```python
matched_window_handles = {w.handle: w for w in windows[0]}
for window_options in windows[1:]:
    matched_window_handles = {
        w.handle: w for w in window_options if w.handle in matched_window_handles}
```

3.  **Exact Match**: If the intersection yields exactly *one* window, it calls `window.set_foreground()` to bring it to the front.
4.  **Ambiguous Match**: If multiple windows match the spoken keywords, the script catches this ambiguity. It forcefully brings the *Caster Messaging Window* to the foreground and prints a list of the conflicting windows, prompting the user to provide a more specific keyword.
5.  **No Match**: If no windows match, it retrieves the user's spoken words from Dragonfly's recognition history and prints an error message.

## 3. Focus Stealing

**How does it resolve "focus stealing"?**
Focus stealing typically refers to the OS preventing an application from forcefully bringing itself (or another app) to the foreground, which often results in the taskbar icon flashing orange instead.

In this implementation, the approach to focus stealing is twofold:
1.  **Direct API Call**: It relies on Dragonfly's underlying `Window.set_foreground()` wrapper. Because this API is triggered directly by a voice command—which Windows often interprets as legitimate user interaction (similar to a keyboard shortcut)—the OS is generally permissive and allows the focus change to occur seamlessly.
2.  **Graceful Fallback on Ambiguity**: When an ambiguous command is given, the script explicitly seeks out the Caster Messaging window and forces it to the front. By proactively taking control of the focus and shifting it to the feedback window, it prevents the user from being left in a state where a command failed but no visual feedback was provided (which would feel like a dropped command or a focus issue).

**Citation (Foregrounding Messaging Window):**
```python
try:
    messaging_title = utilities.get_caster_messaging_window()
    messaging_window = find_window(lambda w: messaging_title in w.title, timeout_ms=100)
    if messaging_window.is_minimized:
        messaging_window.restore()
    else:
        messaging_window.set_foreground()
```

## 4. Strengths and Weaknesses

### Strengths
*   **Dynamic and Fluid Grammar**: The `DictList` combined with the timer means your grammar is always accurate. You don't have to say a "refresh" command when you open a new application.
*   **Flexible Disambiguation**: By allowing multiple keywords (`<windows>` is a `Repetition` element), users can easily narrow down their target (e.g., "window switch firefox" vs "window switch firefox youtube").
*   **Excellent UX on Failure**: Bringing the messaging window to the front when a command is ambiguous is a highly practical way to keep the user informed.
*   **Asynchronous Tracking**: The heavy lifting of scanning windows happens in the background, keeping the main voice command processing loop fast.

### Weaknesses
*   **Polling Overhead**: Running a loop that scans all OS windows and performs string parsing every 2 seconds introduces constant, unnecessary CPU overhead.
*   **Title Volatility**: Modern web browsers change their window titles based on the active tab. If you are trying to target "Chrome" but the active tab is "Reddit - Google Chrome", the keywords shift dynamically, which can cause misrecognitions if the timer hasn't fired yet.
*   **Brittle Heuristics**: The abbreviation logic (`len(s) <= 4 and s.upper() == s`) is overly simplistic and will fail on longer acronyms or mixed-case titles.

## 5. Hard Critique

While this implementation is highly effective and practical for daily use, its architectural foundation relies on **polling**, which is an anti-pattern for OS-level window management. 

A state-of-the-art implementation would discard the 2-second timer entirely. Instead, it would use **Win32 Event Hooks** (specifically `SetWinEventHook` listening for `EVENT_OBJECT_CREATE`, `EVENT_OBJECT_DESTROY`, and `EVENT_OBJECT_NAMECHANGE`). This would make the system **event-driven**. The `DictList` would only update exactly when a window is opened, closed, or changes its title, resulting in zero idle CPU usage and immediate grammar accuracy without the 2-second delay.

Furthermore, forcibly pulling the Caster messaging window to the foreground on an ambiguous match disrupts the user's current context. A less intrusive design would utilize an on-screen display (OSD) overlay or auditory feedback to notify the user of the ambiguity without stealing their focus away from their current workspace.

## 6. How to Pull These Changes into Your Fork

To test this feature manually, you should pull these specific files into a new test branch in your local Caster repository.

Open your PowerShell terminal and run the following commands in your workspace root:

```powershell
# 1. Add the Lexicon repository as a remote (we'll call it 'lexicon')
git remote add lexicon ~\Documents\repos\Caster-LexiconCode

# 2. Fetch all branches and commits from the lexicon remote
git fetch lexicon

# 3. Create and checkout a new branch based on your current custom setup branch
git checkout -b test-window-switching

# 4. Extract only the specific window management files from the lexicon's windows_switch_manager branch
git checkout lexicon/windows_switch_manager -- castervoice/rules/core/navigation_rules/window_mgmt_rule.py
git checkout lexicon/windows_switch_manager -- castervoice/rules/core/navigation_rules/window_mgmt_rule_support.py

# 5. Commit the files to your test branch
git commit -m "Pull in window switching feature from Lexicon repo for testing"
```

After running these commands, start your Caster engine and test the `"window switch <keyword>"` command to evaluate its performance firsthand.
