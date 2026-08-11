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

There are two primary components to the window-switching execution: snapping focus to a target window, and handling ambiguous requests with a visual fallback.

1.  **Target Window Focus**: When you speak a unique window command, it relies on Dragonfly's underlying `Window.set_foreground()` wrapper to bring the target window to the front. In practice, this works exceptionally well, flawlessly snapping focus to the target window even if it resides on a completely different virtual desktop.
    > [!WARNING]
    > **Sporadic Foreground Denial**: Windows can forcefully deny the focus switch (a known OS-level bug/limitation with `SetForegroundWindow`), causing the target application's taskbar icon to flash orange instead of coming to the front. This does happen sporadically, though the exact conditions that trigger it remain unclear.
    > 
    > *(Note: Dragonfly's `set_foreground()` wrapper attempts to mitigate this by sending a dummy `Control` key press before calling the Win32 API to trick Windows into granting focus permission, but the denial can still occasionally occur.)*

    > [!WARNING]
    > **Cross-Workspace Pulling Quirk**: During testing, a strange quirk was observed when switching to an application on a different virtual desktop. On at least one occasion, instead of shifting the user's view to the target workspace, the script appeared to pull the target application over to the *current* workspace without focusing it. Subsequently clicking the application's icon on the taskbar forcefully yanked the user back to the original workspace. This behavior requires further investigation.

    > [!TIP]
    > **Error Reproduction (The "Control Key" Bypass)**: During testing, both of the errors described above (the flashing taskbar and the cross-workspace pulling quirk) were manually and consistently reproduced by **physically holding down the `Control` key** while issuing the voice command.
    > Because Dragonfly explicitly checks if the `Control` key is held down—and skips its synthetic input hack if it is—Windows denies the focus request. While it is highly possible that previous natural occurrences of these bugs were caused by a key getting virtually stuck down during dictation (e.g., from an interrupted macro or aborted command), it's not 100% confirmed if this is the exclusive root cause. What *is* certain is that when no keys are held down, the switching functionality works exceptionally well.

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

### The FATAL FST Crash (Homophone Collision)
When rapidly switching browser tabs (e.g., navigating through sites with titles containing numbers like "07", "06"), the 2-second polling timer will scrape these new words and inject them into the grammar. Kaldi's `g2p-en` will then attempt to automatically generate pronunciations for them.

This can result in a hard C++ binary crash from Kaldi:
```text
kaldi.compiler (WARNING): KaldiCompiler(): Word not in lexicon: '07' [s 'E v V n]
kaldi.compiler (WARNING): KaldiCompiler(): Word not in lexicon: '06' [s 'I k s]
FATAL: StringWeight::Plus: Unequal arguments (non-functional FST?) w1 = 168878 w2 = 168735
```

**Cause:** 
This `StringWeight::Plus` error is an internal Finite State Transducer (FST) compilation failure. It occurs because `g2p-en` generates the exact same pronunciation for "07" as it does for the word "seven" (`[s 'E v V n]`). If the grammar already contains the word "seven" (or if multiple variations of the same pronunciation are dynamically added to the same rule with different text outputs), Kaldi's compiler creates a non-deterministic path with conflicting output tokens. During the graph determinization phase (`fstdeterminizestar`), it attempts to merge these identical pronunciation paths but encounters "Unequal arguments" (different text/semantic values) and immediately aborts the process to prevent corruption.

**Workaround:**
Because you cannot control what text is in a browser's window title, the most robust way to prevent this specific crash is to proactively sanitize the window titles inside `window_mgmt_rule_support.py`'s `refresh_open_windows_dictlist` function before they are ever sent to Kaldi. Stripping out digits, special characters, and obscure acronyms will stop `g2p-en` from generating overlapping homophone pronunciations.

### Runtime Grammar Update Failures
During testing with Kaldi, if you navigate to a new website (e.g., a tab named "tomatoes") and issue the command `"window switch tomatoes"`, the engine may completely misrecognize the command as a string of other seemingly random words already in the vocabulary:
```text
engine (ERROR): Grammar g8: failed to decode rule window management rule recognition ('window', 'switch', '2', 'amir', 'io', 's')
```

**Diagnosis:**
* **Virtual Environments are NOT the cause**: Running Caster from a Python virtual environment (e.g., `.venv_latest`) simply isolates package dependencies. It has absolutely zero impact on how timers or variables behave during runtime.
* **The True Cause**: The background polling timer *is* successfully updating the Python `DictList` in memory (verified via the `window switch show` diagnostic print). However, Kaldi (or Dragonfly's Kaldi integration) is failing to dynamically recompile the decoding graph during runtime. Because the new word is not in the compiled acoustic graph, Kaldi attempts to find the closest sounding path using only the words it *already* knows, resulting in a misrecognition string (e.g., matching "tomatoes" to "two amir io s").
* **Why Rebooting Works**: Rebooting Caster forces the grammar to be completely rebuilt from scratch. Upon startup, the current window titles are passed into the `DictList`, and Kaldi compiles them successfully, allowing the command to be recognized perfectly without misrecognition. Resolving the runtime update issue will likely require an explicit grammar reload hook in the polling timer.

### Inspecting the Lexicon
Kaldi writes all dynamically generated pronunciations to a user lexicon file. You can inspect this file to see how Kaldi has transcribed your active window titles:
👉 **`<caster_repo>/kaldi_model/user_lexicon.txt`** (usually located in your documents/repos directory under `Caster/kaldi_model/user_lexicon.txt`)

---

## 5. Strengths, Weaknesses, and Critiques

### Strengths
*   **Dynamic and Fluid Grammar**: The `DictList` combined with the timer means your grammar is always accurate. You don't have to say a "refresh" command when you open a new application.
*   **Flexible Disambiguation**: By allowing multiple keywords (`<windows>` is a `Repetition` element), users can easily narrow down their target (e.g., `"window switch firefox"` vs `"window switch firefox youtube"`).
*   **Excellent UX on Failure**: Bringing the messaging window to the front when a command is ambiguous is a highly practical way to keep the user informed.
*   **Seamless Multi-Workspace Navigation**: The script indexes all windows across all virtual desktops. When you utter a target window name, it perfectly shifts focus to the target window, automatically moving your view to the correct virtual desktop without any manual workspace swapping commands.

### Weaknesses
*   **Polling Overhead**: Running a loop that scans all OS windows and performs string parsing every 2 seconds introduces constant, unnecessary CPU overhead.
*   **Title Volatility**: Modern web browsers change their window titles based on the active tab. If you are trying to target "Chrome" but the active tab is "Reddit - Google Chrome", the keywords shift dynamically, which can cause misrecognitions if the timer hasn't fired yet.
*   **Brittle Heuristics**: The abbreviation logic (`len(s) <= 4 and s.upper() == s`) is overly simplistic and will fail on longer acronyms or mixed-case titles.

### Hard Critique
While this implementation is highly effective and practical for daily use, its architectural foundation relies on **polling**, which is an anti-pattern for OS-level window management. 

1. **Polling Inefficiency**: A state-of-the-art implementation would discard the 2-second timer entirely and use **Win32 Event Hooks** (`SetWinEventHook` listening for `EVENT_OBJECT_CREATE`, `EVENT_OBJECT_DESTROY`, and `EVENT_OBJECT_NAMECHANGE`). This would make the system **event-driven**, updating the grammar *only* when a window actually changes state. This results in zero idle CPU overhead and removes the latency introduced by polling delays.
2. **Global Scope vs Local Context**: While global multi-workspace navigation is a huge strength, grabbing every window across every workspace makes the vocabulary unnecessarily large and prone to ambiguous collisions if similar windows are open across different desktops. A more advanced approach would be to prioritize or scope the dictionary to the *current* workspace, falling back to global search only when requested.
