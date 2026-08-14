[ 🏠 Docs Home ](../README.md) › [ 📁 Troubleshooting ](../README.md#troubleshooting--diagnostics) › **Kaldi Engine Crash: Root Cause and Resolution**

---

# Kaldi Engine Crash: Root Cause and Resolution

This document explains the technical root cause of the `KaldiError: Cannot use a KaldiRule after calling destroy()` crash, why it surfaced specifically upon migrating to the `dragonfly-bpc-oss` fork, and why the engine-level patch is structurally sound.

---

## 1. The Definitive Finding: Version Diff and the Observer Grammar

We compared the standard `dragonfly2` (version `0.35.0` installed in `site-packages`) used by `Run_Caster_Kaldi.bat` against the `dragonfly-bpc-oss` fork (version `1.0.0rc2`) loaded by `run_caster_kaldi_uia.bat` via `PYTHONPATH`. 

We discovered the exact architectural difference that kept this bug dormant in standard Dragonfly but made it a systemic failure in the fork:

### A. Standard Dragonfly (`dragonfly2` v0.35.0)
In standard Dragonfly, the Kaldi backend's Recognition Observer Manager (`KaldiRecObsManager`) is a stub. Its active hooks do **nothing**:
```python
# dragonfly/engines/backend_kaldi/recobs.py (v0.35.0)
class KaldiRecObsManager(RecObsManagerBase):
    def _activate(self):
        pass

    def _deactivate(self):
        pass
```
When `Mimic("caster sleep")` is executed, it calls:
1. `engine.disable_recognition_observers()`, which triggers `_deactivate()` (**no-op**).
2. `engine.enable_recognition_observers()`, which triggers `_activate()` (**no-op**).

Because no grammars are loaded or unloaded mid-phrase, the `_loadunload_queue` is never touched, and the engine remains perfectly stable.

### B. The `dragonfly-bpc-oss` Fork (v1.0.0rc2)
This fork implements actual recognition observer grammar tracking for Kaldi by introducing a dynamic observer grammar (`_recobs_grammar` containing an `Impossible()` rule):
```python
# dragonfly/engines/backend_kaldi/recobs.py (v1.0.0rc2)
class KaldiRecObsManager(RecObsManagerBase):
    def _activate(self):
        if not self._grammar:
            self._grammar = KaldiRecObsGrammar(self)
        self._grammar.load()  # Calls load_grammar() mid-phrase!

    def _deactivate(self):
        if self._grammar:
            self._grammar.unload()  # Calls unload_grammar() mid-phrase!
```
Every single time **any** `Mimic` command executes (including Caster's `"begin dictation"` macro), it toggles observers. In the fork, this immediately triggers:
1. An `unload()` of `_recobs_grammar`, which gets deferred to the `_loadunload_queue` because a phrase is active (`_in_phrase = True`).
2. A `load()` of `_recobs_grammar`, which compiles the new rules immediately, overwriting the global rules dictionary, and queues the rule activation.

---

## 2. The Core Compiler Logic Bug

The crash sequence is a pure Python logic error triggered by the deferred compilation queue:

1. **Overwritten References**: When the load operation executes, `compile_grammar` runs synchronously on the main thread and overwrites `self.kaldi_rule_by_rule_dict[rule]` with the new rule objects.
2. **Double Destroy / Use-After-Free**: When the phrase ends, `_loadunload_queue` is processed sequentially:
    * The queued `unload()` looks up the rules to destroy. Because the lookup dictionary was prematurely overwritten, it retrieves the **new** rule object and calls `destroy()` on it.
    * The queued `load()` runs next. It tries to register the **new** rule object, but the C++ wrapper throws:
      `KaldiError: Cannot use a KaldiRule after calling destroy()`

---

## 3. Structural Queue Safety: Back-to-Back Load/Unload Analysis

To ensure this fix handles back-to-back load/unload events safely, the engine-level patch completely decouples `unload()` from the live, mutating global dictionary by capturing a local snapshot:

1. **Local Snapshots**: When `_unload_grammar()` is queued, it captures a snapshot of the wrapper's specific `kaldi_rule_by_rule_dict` at that point in time:
   ```python
   def unload():
       self._compiler.unload_grammar(grammar, wrapper.kaldi_rule_by_rule_dict, self)
   ```
2. **Targeted Destruction**: When `unload_grammar()` executes, it iterates over this captured local snapshot. It destroys only the old rule objects that were instantiated during that specific wrapper's load cycle.
3. **Guarded Cleanup**: The compiler only deletes the reference from the global map if it has not been overwritten by a subsequent compilation:
   ```python
   if self.kaldi_rule_by_rule_dict.get(rule) is kaldi_rule:
       del self.kaldi_rule_by_rule_dict[rule]
   ```
   If a newer version of the rule has already been compiled (e.g., in a subsequent load), the global entry is preserved, and only the orphaned C++ handle of the old rule is released.

This guarantees that the deferral queue operates safely under arbitrary queue depth and timing fluctuations.

---

## 4. Verification

The fix has been applied directly to your local `dragonfly-bpc-oss` repository. You can verify the stability by:
1. Reverting the timer deferral in `mic_rules.py` (which has been completed).
2. Running `run_caster_kaldi_uia.bat` to load the development fork.
3. Issuing the `"begin dictation"` and `"stop listening"` commands.
4. Observing that the Kaldi engine no longer crashes, as the grammar lifecycle now safely respects mid-phrase rule compilation.
