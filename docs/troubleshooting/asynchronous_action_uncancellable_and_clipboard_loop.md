<!--
SPDX-License-Identifier: Apache-2.0
Copyright (c) 2024-2026 Amir Farhadi
-->

[ 🏠 Docs Home ](../README.md) › [ 📁 Troubleshooting ](../README.md#troubleshooting--diagnostics) › **AsynchronousAction Lifecycle Failure & Clipboard Polling Loop**

---

# AsynchronousAction Lifecycle Failure & Clipboard Polling Loop

## 1. Problem Statement

Spoken phrases such as *"file open"* can be phonetically misrecognized by speech engines (Dragon, WSR) as the Caster navigation command *"fill openers"*. When triggered, this command initiates an asynchronous loop designed to scan backwards across a line for delimiter characters (`(`, `[`, `{`). This scanning process executes repeated `Ctrl+Shift+Left` and `Ctrl+C` keystrokes via clipboard interrogation every 200 milliseconds.

When this occurs in non-target windows (such as terminals or command prompts), the burst of `Ctrl+C` inputs is interpreted as SIGINT interrupt signals, causing shell interruption. Furthermore, attempts to cancel the running loop by speaking cancellation words (*"cancel"*, *"escape"*) fail if the active action has been evicted from the internal Caster context history. This behavior directly reproduces upstream Caster [Issue #976](https://github.com/dictation-toolbox/Caster/issues/976).

---

## 2. Technical Anatomy of the Execution Sequence

The complete execution path involves three discrete phases across grammar matching, clipboard interrogation, and state stack management.

```
[ Speech Engine Recognition ]
             │
             ▼  Phonetic match: "file open" -> "fill openers"
[ nav.py: "fill <target>" ]
             │
             ▼  Instantiates AsynchronousAction(time_in_seconds=0.2, repetitions=50)
[ stack.py: ContextStack.add() ]
             │
             ├─► Appends StackItemAsynchronous to self.list
             │
             ▼  Timer triggers every 200 ms
[ context.py: fill_within_line() ]
             │
             ├─► Sends Key("cs-left")
             ├─► Calls read_selected_without_altering_clipboard() -> Key("c-c/20")
             │
             ▼  Delimiter not found
     [ Returns False ] ──► Continues loop (up to 50 iterations)
             │
             ▼  If 30 utterances occur, self.list.remove(self.list[0]) evicts action
[ ContextStack.get_incomplete_seekers() ]
             │
             ▼  Action no longer in self.list
  [ Voice "cancel" fails -> Timer orphaned in background ]
```

### Phase 1: Grammar Trigger and Target Resolution
In `castervoice/rules/core/navigation_rules/navigation_support.py`, target delimiters are registered within `TARGET_CHOICE`:

```python
TARGET_CHOICE = Choice(
    "target", {
        # ...
        "openers": "(~[~{",
        "closers": "}~]~)",
    })
```

In `castervoice/rules/core/navigation_rules/nav.py`, the `fill <target>` specification binds to an `AsynchronousAction`:

```python
"fill <target>":
    R(Key("escape, escape, end"), show=False) +
    AsynchronousAction([L(S(["cancel"], Function(context.fill_within_line)))],
                       time_in_seconds=0.2, repetitions=50),
```

### Phase 2: Clipboard Interrogation Loop
The callback `context.fill_within_line` invokes `navigate_to_character("left", "(~[~{", fill=True)` in `castervoice/lib/context.py`:

1. It sends `Key("cs-left")` to expand the text selection leftward.
2. It executes `read_selected_without_altering_clipboard()`, which saves the current system clipboard, issues a hardware `Key("c-c/20")` to copy the selected text, and then restores the previous clipboard buffer.
3. If none of the opener delimiters (`(`, `[`, `{`) are detected in the copied text, `navigate_to_character` resets the cursor with `Key("left")` and returns `False`.
4. Because `False` is returned, `control.nexus().state.terminate_asynchronous(success=True)` is not executed. The timer scheduled in Dragonfly continues firing every 0.2 seconds for up to 50 repetitions.
5. In an active terminal window, each `Ctrl+C` stroke cancels the current command prompt buffer or interrupts running child processes.

### Phase 3: ContextStack Eviction and Orphaned Timers
The cancellation failure reported in [Issue #976](https://github.com/dictation-toolbox/Caster/issues/976) originates in `castervoice/lib/merge/state/stack.py`:

```python
class ContextStack:
    def __init__(self, state):
        self.list = []
        self.max_list_size = 30
        self.state = state

    def add(self, stack_item):
        # ...
        self.list.append(stack_item)
        if len(self.list) > self.max_list_size:
            self.list.remove(self.list[0])

    def get_incomplete_seekers(self):
        incomplete = []
        for i in range(0, len(self.list)):
            if not self.list[i].complete:
                incomplete.append(self.list[i])
        return incomplete
```

Cancellation relies on `get_incomplete_seekers()` finding the active `StackItemAsynchronous` within `self.list`. Because `self.list` acts as a rolling history buffer capped at 30 items, any sequence of 30 speech events, mimics, or sub-actions pushes the running `StackItemAsynchronous` out of the list.

Once evicted from `self.list`:
1. `get_incomplete_seekers()` cannot locate the item.
2. Spoken cancellation commands (`"cancel"`, `"escape"`) fail to trigger `StackItemAsynchronous.execute(False)`.
3. The underlying timer registered in the speech engine runtime (`self.timer`) remains active and continues execution without a cancellation path, requiring a full engine restart.

---

## 3. Remediation Strategies

Two distinct approaches resolve this failure mode: an immediate configuration override and a comprehensive architectural refactoring.

### Strategy A: Immediate Local Remediation (User Configuration)

The immediate fix eliminates the phonetic trigger in the local user directory without requiring core engine modifications.

#### 1. Disable `fill <target>` in Custom Navigation Rules
Override the navigation mapping in user space (`caster_user_content/rules/`) by omitting `"fill <target>"` or remapping the trigger phrase to an explicit, non-colliding spec such as `"fill token <target>"`.

```python
# Remap to avoid collision with standard "file open" utterances
"fill delimiter <target>":
    R(Key("escape, escape, end"), show=False) +
    AsynchronousAction([L(S(["cancel"], Function(context.fill_within_line)))],
                       time_in_seconds=0.2, repetitions=15),
```

#### 2. Trade-offs
- **Pros:** Completely stops accidental phonetic triggers; reduces repetition cap from 50 to 15 if triggered manually.
- **Cons:** Does not fix the underlying upstream lifecycle bug in `ContextStack`.

---

### Strategy B: Full Architectural Refactoring (Core Engine & Lifecycle Management)

A robust software engineering solution addresses the architectural flaw: conflating a rolling undo/history buffer with active background task lifecycle tracking.

#### 1. Decouple Active Tasks from History Buffers
In `castervoice/lib/merge/state/stack.py`, active asynchronous tasks must be maintained in a dedicated collection (`active_asynchronous_tasks: dict[str, StackItemAsynchronous]`) rather than a bounded rolling list.

```python
class ContextStack:
    def __init__(self, state):
        self.history = []
        self.max_history_size = 30
        self.active_asynchronous_tasks = set()
        self.state = state

    def register_active_async(self, stack_item):
        self.active_asynchronous_tasks.add(stack_item)

    def unregister_active_async(self, stack_item):
        self.active_asynchronous_tasks.discard(stack_item)

    def get_incomplete_seekers(self):
        # Always includes active async tasks regardless of history depth
        seekers = [item for item in self.history if not item.complete]
        for task in self.active_asynchronous_tasks:
            if not task.complete and task not in seekers:
                seekers.append(task)
        return seekers
```

#### 2. Explicit Cancellation Tokens and Guaranteed Teardown
Modify `StackItemAsynchronous` in `castervoice/lib/merge/state/stackitems.py` to use explicit threading cancellation events and guaranteed unregistration upon completion or cancellation:

```python
class StackItemAsynchronous(StackItemSeeker):
    TYPE = "continuer"

    def execute(self, success):
        self.complete = True
        if self.timer is not None:
            self.timer.stop()
            self.timer = None
        self.nexus.state.stack.unregister_active_async(self)
        if self.base is not None:
            self.base.execute()
        self.clean()
        if success:
            self.nexus.state.run_waiting_commands()
        else:
            self.nexus.state.unblock()
```

#### 3. Bounded, Non-Intrusive Context Inspection
Hardware clipboard polling using `c-c/20` key synthesis should be replaced by deterministic UI Automation (UIA) TextPattern inspection or non-destructive accessibility queries. When clipboard interrogation is mandatory, the interrogation routine must:
1. Verify foreground window handle consistency before issuing keystrokes.
2. Terminate immediately if window focus changes.
3. Limit consecutive failures to a strict threshold (e.g., 5 attempts instead of 50).

---

## 4. Comparison of Approaches

| Evaluation Dimension | Strategy A: User Space Override | Strategy B: Core Architectural Refactor |
| :--- | :--- | :--- |
| **Scope of Changes** | Local grammar rule configuration | Core `ContextStack`, `StackItemAsynchronous`, and `context.py` |
| **Phonetic False Positive Elimination** | Resolved via command remapping | Addressed via safe inspection fallbacks |
| **Lifecycle Safety (Issue #976)** | Not addressed | Fully resolved via decoupled active task tracking |
| **Clipboard Keystroke Pollution** | Mitigated by reduced repetitions | Eliminated via focus checks and deterministic inspection |
| **Maintenance Burden** | Minimal local override | Requires upstream contribution and regression testing |

---

## 5. Related References

- [Upstream Issue #976: AsynchronousAction becomes uncancellable](https://github.com/dictation-toolbox/Caster/issues/976)
- [Caster Speech Stack Thread Architecture](../architecture/Speech_Stack_Thread_Architecture_and_Diagnostic_Report.md)
- [Dragonfly Recognition Observers & Functional Contexts](../framework_explainers/dragonfly_recognition_observers_and_functional_contexts.md)
