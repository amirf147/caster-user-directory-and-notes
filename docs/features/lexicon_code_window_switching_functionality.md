# LexiconCode Window Switching Functionality

This document provides a comprehensive breakdown of the window switching feature implemented by `LexiconCode`, detailing its architecture, mechanics, Kaldi engine compatibility, troubleshooting findings, and design critiques.

---

## 1. Introduction and Architecture

The window switching feature allows users to switch between open applications by speaking keywords found in the window titles. The implementation is split into two main files:

*   **`window_mgmt_rule.py`**: Defines the voice commands (e.g., `"window switch <windows>"`) and maps them to the backend logic.
*   **`window_mgmt_rule_support.py`**: Contains the core logic for tracking open windows, resolving spoken keywords to specific window handles, and executing the focus shift.

The architecture relies on a **background polling mechanism**. A timer runs every 2 seconds to scan the OS for all open windows, extracting words from their titles, and dynamically injecting them into the speech recognition grammar.

---

## 2. Core Mechanics

### Background Polling (`refresh_open_windows_dictlist`)
The mechanism relies on a Dragonfly timer to periodically fetch windows:

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

```python
window_options = {k: v for k, v in six.iteritems(window_options) if v is not None}
open_windows_dictlist.set(window_options)
```
Because the grammar uses a `DictListRef` pointing to this `DictList`, the speech engine instantly knows the names of all currently open windows without requiring a manual grammar reload.

### Window Switching Logic (`switch_window`)
When the user utters `"window switch <windows>"`:
1.  The command passes the list of spoken keywords into `switch_window()`.
2.  It performs an intersection. For example, if you say `"window switch chrome github"`, it finds windows that contain *both* "chrome" and "github" in their title.

```python
matched_window_handles = {w.handle: w for w in windows[0]}
for window_options in windows[1:]:
    matched_window_handles = {
        w.handle: w for w in window_options if w.handle in matched_window_handles}
```

3.  **Exact Match**: If the intersection yields exactly *one* window, it calls `window.set_foreground()` to bring it to the front.
4.  **Ambiguous Match**: If multiple windows match the spoken keywords, the script catches this ambiguity. It forcefully brings the *Caster Messaging Window* to the foreground and prints a list of the conflicting windows, prompting the user to provide a more specific keyword.
5.  **No Match**: If no windows match, it retrieves the user's spoken words from Dragonfly's recognition history and prints an error message.

---

## 3. Focus Stealing & Fallbacks

There are two distinct window-focus mechanisms at play in this implementation, and they fail in two completely different ways:

1.  **Target Window Focus (Successful Disambiguation)**: When you speak a unique window command, it relies on Dragonfly's underlying `Window.set_foreground()` wrapper to bring the target window to the front. Because this API is triggered directly by a voice command, Windows generally allows the focus change to occur seamlessly.
    > [!WARNING]
    > **Foreground Denial Bug**: While usually permissive, Windows can still forcefully deny the focus switch, causing the script to crash with `pywintypes.error: (0, 'SetForegroundWindow', 'No error message is available')`. When this happens, the target application does not come to the front; instead, its taskbar icon starts flashing orange. This is a known OS-level limitation with `SetForegroundWindow` and has **nothing to do with ambiguity**.
    > *Note on Custom Overlays:* If you are using custom UI overlays (like a Caster HUD pinned to a corner) or third-party taskbar modifiers (like Windhawk), they are **not** the root cause of this error—this is standard Windows behavior. However, if your HUD code has an aggressive "always on top" loop that repeatedly attempts to seize the foreground, it *can* exacerbate the issue by stealing the foreground lock right when Dragonfly attempts the switch.

2.  **Legacy Messaging Window (Failed Disambiguation)**: If multiple windows match your spoken keyword (ambiguity), the script aborts the target window switch entirely. Instead, it explicitly seeks out the Caster Messaging window and forces *that* to the front to provide visual feedback.

```python
try:
    messaging_title = utilities.get_caster_messaging_window()
    messaging_window = find_window(lambda w: messaging_title in w.title, timeout_ms=100)
    if messaging_window.is_minimized:
        messaging_window.restore()
    else:
        messaging_window.set_foreground()
```

> [!WARNING]
> **API Mismatch Error**: The function `utilities.get_caster_messaging_window()` used in this fallback is **not a standard Caster API** (it was likely custom to the original author's setup). If you trigger an ambiguous command, the action execution will fail with an `AttributeError`. Dragonfly gracefully catches this and prints the error to the terminal, so it does not crash Caster, but it prevents the ambiguity feedback from displaying. This missing API error is entirely unrelated to focus stealing.

**A Quick Fix for the Ambiguity Fallback:**
Since modern Caster uses the **Caster HUD** for feedback, one quick workaround is to patch the script to output the ambiguous options directly to the HUD or terminal, bypassing the missing messaging window logic entirely.

```python
# Quick Workaround: Replace the try/except block with HUD printing
from castervoice.lib.printer import printer

# Inside switch_window, when ambiguity is detected:
ambiguous_msg = f"Ambiguous window command. Matched windows:\n"
for w_options in windows:
    for w in w_options:
        ambiguous_msg += f"- {w.title}\n"

# Print directly to the Caster HUD (and terminal)
printer.out(ambiguous_msg)
```
This is a simple band-aid to resolve the missing API error and restore visual feedback when an ambiguous command is spoken.

---

## 4. Kaldi Engine Compatibility & Troubleshooting

If you use the Kaldi speech engine (`kaldi_active_grammar`), there are specific dependencies and potential issues to keep in mind.

### g2p-en Dependency Requirement
Because the window switcher dynamically updates the grammar with arbitrary text from active window titles (such as URL components, file names, or folder paths), Kaldi will frequently encounter **Out-Of-Vocabulary (OOV)** words. 

To handle these, you **must** have the `g2p-en` (Grapheme-to-Phoneme) package installed in your Python environment, **assuming your Kaldi model has `allow_online_pronunciations` enabled**:
```powershell
pip install g2p-en
```
*(Note: If `allow_online_pronunciations` is disabled in your setup, Kaldi will simply skip generating pronunciations for unknown words rather than crashing, so verify this configuration first.)*

Without `g2p-en` installed locally (and with online pronunciations allowed), Kaldi's dynamic updates will fail, throwing the following error every 2 seconds:
```text
kaldi_active_grammar.KaldiError: cannot generate word pronunciation: no generators available
```

### The Dictionary KeyError Bug
After installing `g2p-en`, you may encounter an error like this when the window switcher encounters alphanumerics (e.g., `2026` or `amirf147`):
```text
KeyError: ' '
```

*   **Cause**: When `g2p-en` encounters numbers, it normalizes them to text (e.g., `2026` becomes `"twenty twenty-six"`). To denote word boundaries, it inserts space characters (`' '`) into the returned phoneme array. Kaldi's X-SAMPA converter expects only valid phoneme keys and throws a `KeyError` when it attempts to lookup `' '` in its mapping dictionary (`CMU_to_XSAMPA_dict`).
*   **Fix**: Modify `kaldi_active_grammar/model.py` inside `generate_pronunciations_g2p_en` to filter out space elements and special formatting tags from `g2p-en`'s output:
    ```python
    phones = [p for p in cls.g2p_en(word) if p != ' ' and not p.startswith('<')]
    ```
*   **Alternative Solution (No Engine Changes)**: If you do not want to modify the third-party `kaldi-active-grammar` package, you can sanitize window titles inside Caster's `window_mgmt_rule_support.py` by removing all numbers and symbols before words are passed to the dictlist. However, this means you will not be able to switch windows using numeric keywords.

### Inspecting the Lexicon
Kaldi writes all dynamically generated pronunciations to a user lexicon file. You can inspect this file to see how Kaldi has transcribed your active window titles:
👉 **`<caster_repo>/kaldi_model/user_lexicon.txt`** (usually located in your documents/repos directory under `Caster/kaldi_model/user_lexicon.txt`)

---

## 5. Strengths, Weaknesses, and Critiques

### Strengths
*   **Dynamic and Fluid Grammar**: The `DictList` combined with the timer means your grammar is always accurate. You don't have to say a "refresh" command when you open a new application.
*   **Flexible Disambiguation**: By allowing multiple keywords (`<windows>` is a `Repetition` element), users can easily narrow down their target (e.g., `"window switch firefox"` vs `"window switch firefox youtube"`).
*   **Excellent UX on Failure**: Bringing the messaging window to the front when a command is ambiguous is a highly practical way to keep the user informed.

### Weaknesses
*   **Polling Overhead**: Running a loop that scans all OS windows and performs string parsing every 2 seconds introduces constant, unnecessary CPU overhead.
*   **Title Volatility**: Modern web browsers change their window titles based on the active tab. If you are trying to target "Chrome" but the active tab is "Reddit - Google Chrome", the keywords shift dynamically, which can cause misrecognitions if the timer hasn't fired yet.
*   **Brittle Heuristics**: The abbreviation logic (`len(s) <= 4 and s.upper() == s`) is overly simplistic and will fail on longer acronyms or mixed-case titles.
*   **Multi-Workspace Ambiguity**: Since the script blindly grabs all windows across all workspaces, uttering a common word might unintentionally yank you to an entirely different virtual desktop without warning. There is no concept of "workspace scope".

### Hard Critique
While this implementation is highly effective and practical for daily use, its architectural foundation relies on **polling**, which is an anti-pattern for OS-level window management. 

1. **Polling Inefficiency**: A state-of-the-art implementation would discard the 2-second timer entirely and use **Win32 Event Hooks** (`SetWinEventHook` listening for `EVENT_OBJECT_CREATE`, `EVENT_OBJECT_DESTROY`, and `EVENT_OBJECT_NAMECHANGE`). This would make the system **event-driven**, updating the grammar *only* when a window actually changes state. This results in zero idle CPU overhead and removes the latency introduced by polling delays.
2. **Global Scope vs Local Context**: Grabbing every window across every workspace makes the vocabulary unnecessarily large and prone to ambiguous collisions. A better approach would be to prioritize or scope the dictionary to the *current* workspace, falling back to global search only when requested.
