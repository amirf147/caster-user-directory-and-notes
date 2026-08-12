# LexiconCode Window Switching Functionality

This document provides a comprehensive breakdown of the window switching feature implemented by `LexiconCode`, detailing its architecture, mechanics, Kaldi engine compatibility, troubleshooting findings, and design critiques.

> [!NOTE]
> **TL;DR**: This feature lets you switch windows by saying words from their titles (e.g., `"window switch firefox"`). It works by polling all open windows every 2 seconds and injecting title words into the speech grammar. Focus switching itself works remarkably well—even across virtual desktops—but the background polling introduces significant Kaldi compatibility issues: lexicon pollution from junk tokens, FST compilation crashes from homophone collisions, and a fundamental inability for Kaldi to dynamically recompile its decoding graph at runtime (requiring a full Caster reboot for new windows to become recognizable). **The polling timer is currently disabled** pending a source-level token sanitization fix.

## Table of Contents

- [1. Introduction and Architecture](#1-introduction-and-architecture)
- [2. Core Mechanics](#2-core-mechanics)
- [3. Focus Stealing & Fallbacks](#3-focus-stealing--fallbacks)
- [4. Kaldi Engine Compatibility & Troubleshooting](#4-kaldi-engine-compatibility--troubleshooting)
- [5. Strengths, Weaknesses, and Critiques](#5-strengths-weaknesses-and-critiques)

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

1. **Window Scanning**: It calls `Window.get_all_windows()` to retrieve every window currently known to the OS.
2. **Filtering**: It explicitly ignores system background tasks, hidden windows, and specific utilities (like `C:\Windows` executables or the Dragonfly results box).
3. **Tokenization**: It splits the title of each valid window into individual words. A custom function (`lower_if_not_abbreviation`) attempts to preserve uppercase abbreviations (like "IDE") while lowercasing standard words.
4. **Grammar Injection**: These words are stored in a dictionary mapping the word to a list of matching window objects. This dictionary is then pushed into a Dragonfly `DictList` (`open_windows_dictlist`).

```python
window_options = {k: v for k, v in six.iteritems(window_options) if v is not None}
open_windows_dictlist.set(window_options)

```

Because the grammar uses a `DictListRef` pointing to this `DictList`, the Python-side data structure is updated in place. However, whether the speech engine can actually recognize these new words at runtime depends on the engine — Kaldi in particular fails to dynamically recompile its decoding graph, meaning newly added words are only recognizable after a full Caster reboot (see [Runtime Grammar Update Failures](#runtime-grammar-update-failures)).

### Window Switching Logic (`switch_window`)

When the user utters `"window switch <windows>"`:

1. The command passes the list of spoken keywords into `switch_window()`.
2. It performs an intersection. For example, if you say `"window switch chrome github"`, it finds windows that contain *both* "chrome" and "github" in their title.

```python
matched_window_handles = {w.handle: w for w in windows[0]}
for window_options in windows[1:]:
    matched_window_handles = {
        w.handle: w for w in window_options if w.handle in matched_window_handles}

```

3. **Exact Match**: If the intersection yields exactly *one* window, it calls `window.set_foreground()` to bring it to the front.
4. **Ambiguous Match**: If multiple windows match the spoken keywords, the script catches this ambiguity. It forcefully brings the *Caster Messaging Window* to the foreground and prints a list of the conflicting windows, prompting the user to provide a more specific keyword.
5. **No Match**: If no windows match, it retrieves the user's spoken words from Dragonfly's recognition history and prints an error message.

---

## 3. Focus Stealing & Fallbacks

There are two primary components to the window-switching execution: snapping focus to a target window, and handling ambiguous requests with a visual fallback.

1. **Target Window Focus**: When you speak a unique window command, it relies on Dragonfly's underlying `Window.set_foreground()` wrapper to bring the target window to the front. In practice, this works exceptionally well, flawlessly snapping focus to the target window even if it resides on a completely different virtual desktop.
> [!WARNING]
> **Sporadic Foreground Denial**: Windows can forcefully deny the focus switch (a known OS-level bug/limitation with `SetForegroundWindow`), causing the target application's taskbar icon to flash orange instead of coming to the front. This does happen sporadically, though the exact conditions that trigger it remain unclear.
> *(Note: Dragonfly's `set_foreground()` wrapper attempts to mitigate this by sending a dummy `Control` key press before calling the Win32 API to trick Windows into granting focus permission, but the denial can still occasionally occur.)*


> [!WARNING]
> **Cross-Workspace Pulling Quirk**: During testing, a strange quirk was observed when switching to an application on a different virtual desktop. On at least one occasion, instead of shifting the user's view to the target workspace, the script appeared to pull the target application over to the *current* workspace without focusing it, while simultaneously causing its taskbar icon to flash orange. Subsequently clicking the application's icon on the taskbar forcefully yanked the user back to the original workspace. This behavior requires further investigation.


> [!NOTE]
> **Error Reproduction (The "Control Key" Bypass)**: During testing, both of the errors described above (the flashing taskbar and the cross-workspace pulling quirk) were manually and consistently reproduced by **physically holding down the `Control` key** while issuing the voice command.
> Because Dragonfly explicitly checks if the `Control` key is held down—and skips its synthetic input hack if it is—Windows denies the focus request. While it is highly possible that previous natural occurrences of these bugs were caused by a key getting virtually stuck down during dictation (e.g., from an interrupted macro or aborted command), it's not 100% confirmed if this is the exclusive root cause. What *is* certain is that when no keys are held down, the switching functionality works exceptionally well.


> [!NOTE]
> **Error Occurrence (Post-Explorer.exe Restart Instability)**: During testing, an instance occurred where the Windows Explorer process (`explorer.exe`) crashed and automatically restarted itself. Immediately following this shell reset, issuing window switching voice commands resulted in target window failure, with taskbar icons repeatedly flashing orange upon each attempt. However, after several retries over a brief interval (a few seconds), window switching spontaneously recovered and resumed working smoothly without requiring a Caster or Dragonfly restart.
> **Probable Technical Mechanism (Best Estimate)**:
> * **Shell Message Queue Re-initialization**: When `explorer.exe` crashes and restarts, the Windows shell destroys and reconstructs taskbar handles, window z-order stacks, and shell hook listeners.
> * **Temporary Foreground Lock Enforcement**: During this re-initialization window, the OS strictly enforces foreground transfer rules (`LockSetForegroundWindow`). Dragonfly's synthetic `Control` key press hack—normally used to trick `SetForegroundWindow` into granting focus permission—may be ignored or rejected while the shell re-attaches thread input queues.
> * **Self-Healing Settlement**: Once Explorer finishes processing its initial message loop and re-syncs thread focus attachments, standard foreground permission rules are restored, allowing `set_foreground()` commands to work normally again.
> 
> 
> *(Note: While this mechanism aligns directly with known Win32 API foreground restrictions, confirming it as the exact 100% root cause would require low-level event tracing during the crash event.)*


2. **Legacy Messaging Window (Failed Disambiguation)**: If multiple windows match your spoken keyword (ambiguity), the script aborts the target window switch entirely. Instead, it explicitly seeks out the Caster Messaging window and forces *that* to the front to provide visual feedback.

```python
try:
    messaging_title = utilities.get_caster_messaging_window()
    messaging_window = find_window(lambda w: messaging_title in w.title, timeout_ms=100)
    if messaging_window.is_minimized:
        messaging_window.restore()
    else:
        messaging_window.set_foreground()
except AttributeError:
    pass

```

> [!WARNING]
> **Legacy API Deprecation Error**: The function `utilities.get_caster_messaging_window()` used in this fallback is **a legacy Caster 0.x API** (from ~5+ years ago, prior to the Caster 1.0 architecture overhaul in 2019). In early Caster versions, status messages were rendered in a dedicated WxPython GUI window titled `"Caster Messaging"`. When Caster migrated to `castervoice.lib.printer` and the Caster HUD, `utilities.get_caster_messaging_window()` was removed. Because the original LexiconCode pull request dates back to this era (~5 years ago), triggering an ambiguous command on modern Caster raises an `AttributeError`. Dragonfly gracefully catches this error in the terminal, but the ambiguity feedback fails to display. For a detailed breakdown of this API transition and historical commit dates, see [caster_printer_hud_timeline.md](../history/caster_printer_hud_timeline.md).

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

After installing `g2p-en`, you may encounter an error like this when the window switcher encounters alphanumerics (e.g., `2026` or a username string like `<username123>`):

```text
KeyError: ' '

```

* **Cause**: When `g2p-en` encounters numbers, it normalizes them to text (e.g., `2026` becomes `"twenty twenty-six"`). To denote word boundaries, it inserts space characters (`' '`) into the returned phoneme array. Kaldi's X-SAMPA converter expects only valid phoneme keys and throws a `KeyError` when it attempts to lookup `' '` in its mapping dictionary (`CMU_to_XSAMPA_dict`).
* **Fix**: Modify `kaldi_active_grammar/model.py` inside `generate_pronunciations_g2p_en` to filter out space elements and special formatting tags from `g2p-en`'s output:
```python
phones = [p for p in cls.g2p_en(word) if p != ' ' and not p.startswith('<')]

```


* **Alternative Solution (No Engine Changes)**: If you do not want to modify the third-party `kaldi-active-grammar` package, you can sanitize window titles inside Caster's `window_mgmt_rule_support.py` by removing all numbers and symbols before words are passed to the dictlist. However, this means you will not be able to switch windows using numeric keywords.

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
engine (ERROR): Grammar g8: failed to decode rule window management rule recognition ('window', 'switch', '<misrecognized>', '<fragments>', '<here>')

```

**Diagnosis:**

* **Virtual Environments are NOT the cause**: Running Caster from a Python virtual environment (e.g., `.venv_latest`) simply isolates package dependencies. It has absolutely zero impact on how timers or variables behave during runtime.
* **The True Cause**: The background polling timer *is* successfully updating the Python `DictList` in memory (verified via the `window switch show` diagnostic print). However, Kaldi (or Dragonfly's Kaldi integration) is failing to dynamically recompile the decoding graph during runtime. Because the new word is not in the compiled acoustic graph, Kaldi attempts to find the closest sounding path using only the words it *already* knows, resulting in a misrecognition string (the engine breaks the unknown word into the closest-sounding known tokens).
* **Why Rebooting Works**: Rebooting Caster forces the grammar to be completely rebuilt from scratch. Upon startup, the current window titles are passed into the `DictList`, and Kaldi compiles them successfully, allowing the command to be recognized perfectly without misrecognition. Resolving the runtime update issue will likely require an explicit grammar reload hook in the polling timer.

### Hex/Hash String Lexicon Pollution

Alphanumeric hashes (e.g., git commit SHAs or hex identifiers scraped from browser tab URLs) in active window titles are picked up by the polling timer and sent to Kaldi's compiler. Because these strings do not exist in the standard English lexicon, `g2p-en` attempts to generate automatic pronunciations for them, resulting in warnings like:
```text
kaldi.compiler (WARNING): KaldiCompiler(): Word not in lexicon (generated automatic pronunciation): '<sha-fragment>' [<phoneme chain>]
```
These automatically generated pronunciations are often complex phoneme combinations representing phonetic gibberish. Voice switching using these raw hex strings is consistently unsuccessful in practice, and they pollute the active vocabulary.

#### The Cumulative Growth Problem

A deeper issue is that pollution is **persistent and additive**. Kaldi writes all dynamically generated pronunciations to `kaldi_model/user_lexicon.txt`, and this file is **never automatically pruned**. Every unique token from every window title that has ever been open—across every session—accumulates in this file. Because `kaldi_model/` is excluded from version control (via `.gitignore`), this growth is invisible and easy to overlook.

In practice, after just a few sessions of typical use (multiple browser tabs, developer tools, GitHub PRs with hash-heavy URLs, media files with codec metadata in their names), the lexicon fills with entries like:

- **Git SHA fragments**: short hex strings scraped from GitHub tab titles or terminal windows — all generating nonsense phonemes
- **Raw digit strings and F-keys**: standalone numbers (`07`, `32`, `400`) and function key tokens (`f1` through `f12`) from tab titles or window names
- **Media codec metadata**: format strings found in video file titles (e.g., codec identifiers, resolution tags, encoder names)
- **URL-derived tokens**: service identifiers, numeric IDs, and path segments from browser tab titles
- **Username strings**: account names or handles appearing in window titles — g2p-en will attempt to phonetically spell these out character by character, producing extremely long phoneme chains

The practical consequences of an unchecked, growing lexicon:

1. **Slower FST recompilation on every poll cycle**: More lexicon entries means more FST states for Kaldi to process every 2 seconds. Recompile time grows with lexicon size.
2. **Increased acoustic confusion**: Each garbage entry is a noise path through the phoneme lattice. More junk paths mean more misrecognition risk for legitimate commands across the entire grammar.
3. **Homophone collision risk compounds over time**: The FATAL FST crash described above (`StringWeight::Plus` error) occurs when a newly polled token happens to share a pronunciation with an existing word. As the lexicon grows, the probability of a random new string colliding with an existing entry increases.

The cleanest mitigation is **source-level sanitization** in `refresh_open_windows_dictlist`: strip tokens matching hexadecimal patterns, pure digit strings, and very short tokens before they are ever injected into the `DictList`. A minimal regex filter such as `r'^[0-9a-f]{5,}$'` would catch most git SHAs and hex fragments.


### Inspecting the Lexicon

Kaldi writes all dynamically generated pronunciations to a user lexicon file. You can inspect this file to see how Kaldi has transcribed your active window titles:
👉 **`<caster_repo>/kaldi_model/user_lexicon.txt`** (usually located in your documents/repos directory under `Caster/kaldi_model/user_lexicon.txt`)

---

## 5. Strengths, Weaknesses, and Critiques

### Strengths

* **Automatic Window Discovery (Python-Side)**: The `DictList` combined with the timer means the Python grammar data structure is populated with new window titles automatically without requiring a manual "refresh" command. However, as noted below, while the *Python script* updates automatically, the **Kaldi engine** itself cannot dynamically rebuild its decoding graph to recognize these newly polled words at runtime. On Caster startup, all currently open windows are compiled into the vocabulary, making those initial windows perfectly available for voice switching—but any windows opened *after* startup require a full Caster reboot to be recognized.
* **Flexible Disambiguation**: By allowing multiple keywords (`<windows>` is a `Repetition` element), users can easily narrow down their target (e.g., `"window switch firefox"` vs `"window switch firefox youtube"`).
* **Seamless Multi-Workspace Navigation**: The script indexes all windows across all virtual desktops. When you utter a target window name, it perfectly shifts focus to the target window, automatically moving your view to the correct virtual desktop without any manual workspace swapping commands.

### Weaknesses

* **Kaldi Requires Full Reboot for New Windows**: Although the polling timer successfully updates the in-memory `DictList`, Kaldi fails to dynamically recompile its decoding graph at runtime. Windows opened after Caster starts are not recognizable until a full Caster reboot. This fundamentally undermines the value of continuous polling — the timer keeps running every 2 seconds, but the new words it discovers are unusable until a restart anyway.
* **Polling Overhead**: Running a loop that scans all OS windows and performs string parsing every 2 seconds introduces constant, unnecessary CPU overhead — made worse by the fact that the results are not usable by Kaldi without a reboot.
* **Title Volatility**: Modern web browsers change their window titles based on the active tab. If you are trying to target "Chrome" but the active tab is "Reddit - Google Chrome", the keywords shift dynamically, which can cause misrecognitions if the timer hasn't fired yet.
* **Hex/Hash Vocabulary Pollution**: Alphanumeric hashes (e.g., git SHAs, hex components of URLs) in window titles trigger automatic pronunciation generation. This produces gibberish phoneme patterns, increases acoustic model size, and fails to switch focus reliably by voice anyway.
* **Multi-Workspace Ambiguity**: Since the script blindly grabs all windows across all workspaces, uttering a common word might unintentionally yank you to an entirely different virtual desktop without warning. There is no concept of "workspace scope".
* **Possible Audio Buffer Overflow During Pronunciation Generation**: On at least one occasion, immediately following a new window title being encountered, Caster appeared to momentarily lock up or freeze. Checking the terminal output at the time revealed a warning resembling an audio buffer overflow (exact error string not captured). This may indicate that the work Kaldi performs to dynamically generate and compile new pronunciations is occasionally heavy enough to block or delay audio processing, causing the recognition engine to miss incoming speech frames. This has not been consistently reproduced and the root cause has not been confirmed—it could alternatively be an unrelated system resource spike—but it is worth noting as a potential instability vector.


### Architectural Opportunities

While the core focus-switching logic is highly effective, the architectural foundation relies on **polling**, which introduces unnecessary overhead.

1. **Event-Driven vs. Polling**: A more efficient implementation could discard the 2-second timer entirely and use **Win32 Event Hooks** (`SetWinEventHook` listening for `EVENT_OBJECT_CREATE`, `EVENT_OBJECT_DESTROY`, and `EVENT_OBJECT_NAMECHANGE`). This would make the system **event-driven**, updating the grammar *only* when a window actually changes state. This approach would result in zero idle CPU overhead and remove the latency introduced by polling delays.
2. **Global Scope vs Local Context**: While global multi-workspace navigation is a huge strength, grabbing every window across every workspace makes the vocabulary unnecessarily large and prone to ambiguous collisions if similar windows are open across different desktops. A more advanced approach would be to prioritize or scope the dictionary to the *current* workspace, falling back to global search only when requested.