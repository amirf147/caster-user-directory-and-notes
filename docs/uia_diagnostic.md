## UIA Testing & Engine Troglyte Status Report

### 1. Established Facts

* **UIA Payload Verification:** The underlying text-manipulation features exposed by the `dragonfly-bpc-oss` fork are working. Direct buffer reading (`expanded_text`), text selection (`select_range`), and caret index tracking (via the discovered `.cursor` property) all interact correctly with active text fields when routed through the background thread.
* **The Crash Symptom:** The environment frequently encounters a fatal `KaldiError: Cannot use a KaldiRule after calling destroy()` crash, preceded by a `prepare_for_recognition ignored while in phrase` warning.
* **Isolating the Trigger:**
* The crash is consistently reproducible when using **native voice commands** to alter the microphone state (e.g., saying *"caster sleep"* or *"caster on"*).
* The crash **does not occur** when toggling the microphone sleep/wake state using the external foot pedal setup, which routes the command via an XML-RPC thread and an engine timer loop.
* The error persists even when the custom diagnostic script is completely removed from the rules folder, indicating the instability exists natively within the development environment setup.

---

### 2. Working Hypotheses

* **Hypothesis A (Execution Timing Conflict):** The native voice command path triggers a synchronous microphone/grammar mode change while Kaldi is still actively wrapping up the phrase processing window. This likely creates a timing clash with the fork’s background UIA thread loops during grammar reloads.
* **Hypothesis B (Thread Resource Contention):** The active COM event listeners handled by the branch's background controller thread might be locking shared thread resources, causing the engine to drop intermediate recognition lifecycles when handling high-priority grammar updates.

---

### 3. Immediate Roadmap

* [ ] **Step 1: Test Deferral on the Voice Path**
Modify the native Caster microphone rule file locally to wrap the microphone mode transitions inside a deferred engine timer (`engine.create_timer(..., 0.1)`), matching the execution structure of the stable foot pedal routine.
* [ ] **Step 2: Monitor State Transitions**
Run targeted stability passes using only the voice sleep toggle with the deferral patch active to observe if the timing warning clears.
* [ ] **Step 3: Document Core Fork Limits**
If the deferral patch fails, summarize the thread-boundary constraints affecting the Kaldi engine loop to submit alongside the functional UIA syntax confirmation on the GitHub Pull Request.

Pull Request: https://github.com/dictation-toolbox/dragonfly/pull/407
