## UIA Testing & Engine Troglyte Status Report

### 1. Established Facts

* **UIA Payload Verification:** The underlying text-manipulation features exposed by the `dragonfly-bpc-oss` fork are working. Direct buffer reading (`expanded_text`), text selection (`select_range`), and caret index tracking (via the discovered `.cursor` property) all interact correctly with active text fields when routed through the background thread.
* **The Crash Symptom:** The environment frequently encounters a fatal `KaldiError: Cannot use a KaldiRule after calling destroy()` crash, preceded by a `prepare_for_recognition ignored while in phrase` warning.
* **Isolating the Trigger:**
    * The crash is consistently reproducible when using **native voice commands** to alter the microphone state (e.g., saying *"caster sleep"* or *"caster on"*).
    * The crash **does not occur** when toggling the microphone sleep/wake state using the external foot pedal setup, which routes the command via an XML-RPC thread and an engine timer loop.
    * The error persists even when the custom diagnostic script is completely removed from the rules folder, indicating the instability exists natively within the development environment setup.
* **Root Cause Discovered (July 2026):**
    * When `Mimic("caster sleep")` or `"stop listening"` is called within a phrase, it triggers a grammar unload and load sequence before the phrase has completed (`self._in_phrase` is True).
    * The Kaldi backend engine queues `unload()` and `load()` operations in `_loadunload_queue` to execute at the end of the phrase.
    * Because the `Rule` objects persist across loads, `load_grammar()` immediately compiles the grammar and overwrites `self.kaldi_rule_by_rule_dict[rule]` to point to the **new** `KaldiRule` objects before the queued `unload()` has run.
    * When the phrase ends and the queue executes:
        1. The queued `unload()` runs and looks up the rule from `self.kaldi_rule_by_rule_dict[rule]`, which now incorrectly retrieves the **new** rule object (instead of the old one) and calls `destroy()` on it.
        2. The queued `load()` runs next and attempts to call `load()` on the new rule object, which crashes because it was just destroyed.
* **Resolution:** Patched the backend Kaldi engine (`engine.py` and `compiler.py`) to pass the specific rule dictionary during unload and only delete global mappings if they match the destroyed instance.

---

### 2. Working Hypotheses

* **Hypothesis A (Execution Timing Conflict - Verified/Resolved):** The timing conflict resulted from `load_grammar()` modifying the global rule dictionary mid-phrase, causing the deferred `unload()` to target the newly compiled rule instead of the old one.

---

### 3. Immediate Roadmap

* [x] **Step 1: Revert Temporary Timer Workaround**
Reverted the temporary timer wrapper in `mic_rules.py` after the root cause was resolved at the framework layer.
* [x] **Step 2: Verify Native Voice Transitions**
Verified the stability of the voice sleep/wake toggles directly with the engine-level patch active, confirming no warnings or crashes.
* [x] **Step 3: Document and Patch Core Fork Limits**
Identified and patched the load/unload compiler lifecycle bug in the Kaldi engine.

Pull Request: https://github.com/dictation-toolbox/dragonfly/pull/407
