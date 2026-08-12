# PR #881 (Window Switch Manager) - Testing Findings

*(Note: This document is a condensed summary of testing findings. For the full initial exploration and code review, see [lexicon_code_window_switching_functionality.md](./lexicon_code_window_switching_functionality.md)).*

The core focus-switching logic (using Dragonfly's `set_foreground()`) works well. However, testing the background polling mechanism with the **Kaldi** speech engine revealed a few critical blockers related to how Kaldi handles dynamic vocabularies.

### 1. Runtime Update Failures (Requires Reboot)
While the Python `DictList` updates successfully every 2 seconds in memory, Kaldi fails to dynamically recompile its decoding graph at runtime to include the new words. New window titles discovered by the polling timer are not actually recognizable by the engine until Caster is completely rebooted. This fundamentally limits the usefulness of continuous background polling.

### 2. Cumulative Lexicon Pollution
Because the script scrapes raw window titles, it indiscriminately picks up alphanumeric tokens (e.g., git commit SHAs, hex components of URLs, media codec strings, raw numbers). 
* Kaldi's `g2p-en` automatically generates phoneme pronunciations for these and writes them to `user_lexicon.txt` (a persistent disk file).
* Over time, this file bloats with hundreds of garbage entries, permanently slowing down FST recompilation and increasing acoustic confusion/misrecognition rates across the entire grammar.

### 3. FST Crashes / Homophone Collisions
As the lexicon becomes polluted with hex strings and numbers, the risk of `g2p-en` generating overlapping pronunciations (homophones) increases. If a newly scraped token happens to share a pronunciation with an existing word, Kaldi's FST compiler throws a `StringWeight::Plus` fatal error and crashes the engine.

### 4. Audio Buffer Instability
There is evidence that when a large influx of new window title tokens triggers a heavy batch of dynamic pronunciation generation and graph recompilation, it can briefly lock up the recognition thread, resulting in audio buffer overflow warnings and missed speech frames.

### 5. Focus Stealing & Fallbacks
The core focus-switching logic (using Dragonfly's `set_foreground()`) is generally very effective, snapping focus to target windows even across different virtual desktops. However, testing revealed several edge cases related to Windows foreground restrictions:

* **Sporadic Foreground Denial**: Windows can occasionally deny the focus switch request (a known OS-level limitation with `SetForegroundWindow`). This is not a regular occurrence, but when focus is denied, the behavior depends on the target window's location:
  * **Same Workspace**: The target application's taskbar icon simply flashes orange instead of the window coming to the front.
  * **Cross-Workspace Pulling**: If the target window resides on a different virtual desktop, the denied focus causes the application's visual presence to be pulled over to the current workspace, flashing orange on the taskbar. It remains temporarily pulled to the active workspace (persisting across workspace switches) until you click the taskbar item or focus the application, which then snaps you back to the original workspace where the window actually resides.
* **Error Reproduction (The "Control Key" Bypass)**: These foreground denial behaviors were consistently reproduced by holding down the `Control` key while issuing the voice command. Dragonfly's `set_foreground()` wrapper uses a dummy `Control` key press to bypass Win32 foreground locks, but it aborts this hack if it detects the key is already held down.
* **Post-Explorer.exe Restart Instability**: If the Windows Explorer process (`explorer.exe`) crashes and restarts, window switching temporarily fails (flashing taskbar icons). During shell re-initialization, the OS strictly enforces foreground transfer rules and rejects Dragonfly's focus requests. This issue self-heals after a few seconds once the shell settles.
* **Resolution via AppSwitcher (Thread Attachment Bypass)**: You have successfully resolved this focus denial issue in your custom AppSwitcher implementation. When a standard `SetForegroundWindow` call fails (causing the flashing orange behavior), the AppSwitcher detects the failure and falls back to a more robust Win32 bypass. It uses `AttachThreadInput` to temporarily link its input thread to the current foreground window's thread, tricking Windows into granting it foreground privileges. Combined with a synthetic `Alt` key press, this forces the target window to the front, completely bypassing the OS foreground lock that Dragonfly's simpler "Control key" hack fails to overcome. For a detailed technical breakdown of this mechanism, see the [AppSwitcher Focus Analysis](./app_switcher_focus_analysis.md).

### Architectural Recommendations (Proposed by Gemini LLMs)
To resolve the lexicon pollution, the Gemini LLMs recommend that tokens be heavily sanitized (stripping hex, numbers, and short acronyms) before they are passed to Kaldi. Furthermore, since Kaldi requires a reboot to recognize new words anyway, they suggest that an **event-driven** approach (using `SetWinEventHook` to update grammar only when windows are created/destroyed) would be more efficient than continuous polling, though the runtime update limitation would still need to be addressed at the engine level.
