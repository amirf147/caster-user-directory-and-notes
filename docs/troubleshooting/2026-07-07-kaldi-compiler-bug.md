[ 🏠 Docs Home ](../README.md) › [ 📁 Troubleshooting ](../README.md#troubleshooting--diagnostics) › **Learning Diary: July 7, 2026**

---

# Learning Diary: July 7, 2026
## Subject: Kaldi Engine Compiler Concurrency & UIA Integration

---

## 1. Summary of What We Learned (The Knowns)

* **The Engine Crash Root Cause**: 
  We identified a deterministic logic bug in the Kaldi engine's grammar compilation queue. When a grammar is unloaded and loaded mid-phrase (`self._in_phrase` is True), the engine defers the operations but immediately recompiles rules and overwrites the shared `self.kaldi_rule_by_rule_dict`. When the deferred queue executes at the end of the phrase, `unload()` destroys the *newly compiled* rule object, causing `load()` to crash with a `KaldiError`.
  
* **Why it Dormantly Slept in Standard Dragonfly**:
  In standard `dragonfly2` (v0.35.0), the Kaldi Recognition Observer Manager (`KaldiRecObsManager`) is a no-op stub. It does not load or unload any observer grammar. In the `dragonfly-bpc-oss` fork (v1.0.0rc2), it actively loads and unloads a custom `_recobs_grammar` to track phrase status. Because `Mimic()` toggles observers mid-phrase, it continuously invoked the compiler loading cycle and triggered the crash.
  
* **The Frame-Level Patch**:
  We patched the Dragonfly compiler (`compiler.py` and `engine.py`) to pass a local snapshot of the rule dictionary to `unload_grammar()` and only delete keys if they match the active rule. This makes the compilation queue structurally safe against back-to-back compiler changes.
  
* **Reversion of Workarounds**:
  The temporary timer workaround in `mic_rules.py` was successfully reverted. The engine-level patch handles voice-triggered microphone state switches natively and reliably.

---

## 2. What is Still Outstanding (The Unknowns)

* **`kaldi-active-grammar` version differences**: 
  Our current Python environment is running version `3.1.0`. Version `3.2.0` has been released. It is currently unknown if `3.2.0` modifies the `destroy()` validation checks or introduces memory cleanup enhancements that alter this behavior.
  
* **Upstream Dragonfly Codebase Status**:
  It is unknown whether the latest master branch of the official `dictation-toolbox/dragonfly` repository has already fixed this lifecycle queue bug, or if they still have this latent bug. 

---

## 3. Recommended Roadmap (First Things First)

1. **Upstream Investigation**: Check the latest code on the official Dragonfly repository to see if the compiler queue bug remains unaddressed on the master branch.
2. **Upstream Contribution**: If the bug is still present upstream, prepare our clean local patch to submit as a Pull Request to `dictation-toolbox/dragonfly`.
3. **Upgrade Validation**: Upgrade to `kaldi-active-grammar` v3.2.0 and run local stability tests to ensure compatibility with our compiler patch.
