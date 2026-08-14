[ 🏠 Docs Home ](../README.md) › [ 📁 Framework Explainers ](../README.md#framework-explainers) › **Dragonfly Rule Deepdive**

---

If looking at that technical deep-dive document feels like reading ancient hieroglyphics, **that is 100% normal.** Do not feel bad for a second. You just jumped straight from writing high-level Python voice commands into the absolute deepest, darkest, multi-threaded basement of an asynchronous speech recognition engine. It *should* feel like Greek.

To answer your question directly: **Do not touch `kaldi-active-grammar` yet. Start by tracing how simple Dragonfly rules enable and disable.**

Trying to study `kaldi-active-grammar` first is a trap. It is a highly specialized engine built around mathematical graphs and compiled C++ wrappers. Trying to learn that first is like trying to learn how a car works by reading organic chemistry papers on octane molecules. It is too abstract.

Instead, you should start with **Dragonfly rule enabling and disabling**. Dragonfly is the bridge. You already know what a Dragonfly `Rule` looks like because you write them. If you can trace exactly what happens when you tell a rule to wake up or go to sleep, everything else will suddenly start to make sense.

### The Best Way to Learn: "Print-Splatting"

Do not just read the code. Your brain will glaze over. The absolute best way to learn a new codebase is **print-tracing** (injecting raw `print()` statements into the library files on your computer, running the code, and watching your terminal spit out the execution timeline in real-time).

Here is a step-by-step roadmap to make this entire race condition concept visually jump off your screen:

1. **Create a Microscopic Test Grammar:** Step 1.
Create a file called `_trace_test.py` in your Caster directory. Keep it stupidly simple:

```python
from dragonfly import Grammar, MappingRule, Function


class TraceRule(MappingRule):
    mapping = {
        "trigger test": Function(lambda: print(">>> VOICE COMMAND FIRED <<<")),
    }


grammar = Grammar("trace_grammar")
grammar.add_rule(TraceRule())
grammar.load()
```


2. **Inject Print Markers into the Library:** Step 2.
Open your local developer clone of the Dragonfly engine code (`repos/dragonfly-bpc-oss/dragonfly/engines/backend_kaldi/engine.py`) and inject raw print statements inside the key lifecycle functions.

For example, find `_load_grammar` and `_unload_grammar` and add visual markers:

```python
def _load_grammar(self, grammar):
    print(f"\n[DRAGONFLY ENGINE] ---> Step 1: _load_grammar called for {grammar.name}")
    ...
```

And inside the deferred `load` helper function inside `_load_grammar`:

```python
def load():
    print(f"\n[DRAGONFLY ENGINE] ---> Step 2: Deferred load() helper executes now!")
    ...
```


3. **Run from the Console and Watch:** Step 3.
Boot up your environment using `run_caster_kaldi_uia.bat` from a standard command prompt or terminal window.

Say your command: *"trigger test"*.

Watch your terminal. You will physically see the exact order of operations scroll by. You will see when the engine detects you talking (`_in_phrase` becomes `True`), when your Python function runs, and when the engine decides the phrase is over.


4. **Spot the Race Condition:** Step 4.
Once you can see the normal flow, modify your custom `_trace_test.py` to trigger a grammar disable/enable command mid-phrase.

When you say it, watch the console. You will physically see **Step 1 (_load_grammar called)** fire instantly, but **Step 2 (Deferred load helper)** will get delayed and print out *after* your command output prints.


---

### Why this will make it click

The moment you see your own custom `print()` statements printing out in a specific order in your command prompt, the abstract concepts like "synchronous compilation" and "deferred queues" will instantly become concrete.

You won't be guessing what a "queue" is anymore. You will see that the code printed `[DRAGONFLY ENGINE] ---> Step 1`, then printed your voice command output, and *only then* printed `[DRAGONFLY ENGINE] ---> Step 2`.

That is how real systems engineers learn code bases. You make the system talk to you.

Would you like to start by locating those files in your local `dragonfly-bpc-oss` repository so we can inject our first couple of print statement markers together?