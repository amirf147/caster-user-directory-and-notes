<!--
SPDX-License-Identifier: Apache-2.0
Copyright (c) 2024-2026 Amir Farhadi
-->

[ 🏠 Docs Home ](../README.md) › [ 📁 Framework Explainers ](../README.md#framework-explainers) › **NodeRule and TreeRule Architecture**

---

# NodeRule and TreeRule Architecture: Stateful Grammar Trees, Engine Perplexity, and Context Integration

**Document ID**: `CASTER-DOC-EXP-004`  
**Status**: Comprehensive Technical Explainer and Architectural Reference  
**Target Subsystems**: `castervoice/lib/merge/selfmod/tree_rule/`, `castervoice/lib/merge/ccrmerging2/hooks/`  
**Authors**: Antigravity Principal Architecture Team (Pair Programming with Amir Farhadi)  

---

## 1. Executive Summary

Voice command systems encounter a fundamental trade-off between grammar size and recognition accuracy. Exposing thousands of commands simultaneously in a flat continuous command recognition (CCR) grammar increases speech engine perplexity, elevates CPU load, and risks grammar compilation limits (such as the DNS `BadGrammar` error).

`NodeRule` (implemented in Caster as `TreeRule` and `TreeNode`) addresses this bottleneck by organizing command specifications into a hierarchical, state-dependent tree. Only nodes at the active path are registered with the engine at any given moment. Speaking a command executes its action, prunes irrelevant branches, and exposes only the child commands valid for the next step.

This document breaks down the internal mechanics of `TreeRule`, analyzes why it was historically underused, details how modern UI and AI workflows resolve its authoring bottlenecks, and provides a direct architectural comparison between temporal state trees (`NodeRule`) and spatial environment contexts (`ADCE` / `AppContext`).

---

## 2. Core Architectural Mechanics

### 2.1 The TreeNode Data Structure

A `TreeNode` represents a single decision point or terminal command inside the grammar tree. It encapsulates five parameters:

```python
TreeNode(spec, action, children=[], extras=[], defaults={})
```

- `spec` (str): The spoken phrase required to trigger this node.
- `action` (ActionBase): The Dragonfly action executed upon recognition (such as `Text`, `Key`, `Function`, or `NullAction`).
- `children` (list): A list of nested `TreeNode` objects accessible only after this node is spoken.
- `extras` (list): Dragonfly dynamic elements (such as `IntegerRef`, `Dictation`, or `Choice`) scoped to this specific node.
- `defaults` (dict): Default parameter values for the node extras.

```
                    ┌─────────────────────────┐
                    │    Root: "CSS" (Null)   │
                    └────────────┬────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       ┌───────────────────┐           ┌───────────────────┐
       │ "border" (Text)   │           │ "speech" (Null)   │
       └─────────┬─────────┘           └─────────┬─────────┘
                 │                               │
         ┌───────┴───────┐               ┌───────┴───────┐
         ▼               ▼               ▼               ▼
   ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
   │  "top"    │   │  "color"  │   │  "speak"  │   │  "voice"  │
   └─────┬─────┘   └───────────┘   └─────┬─────┘   └───────────┘
         │                               │
   ┌─────┴─────┐                   ┌─────┴─────┐
   ▼           ▼                   ▼           ▼
┌───────┐ ┌─────────┐           ┌───────┐ ┌─────────┐
│"width"│ │"radius" │           │"none" │ │"normal" │
└───────┘ └─────────┘           └───────┘ └─────────┘
```

### 2.2 TreeRule as a Self-Modifying Rule (`BaseSelfModifyingRule`)

`TreeRule` inherits from `BaseSelfModifyingRule`. In Caster, self-modifying rules dynamically mutate their internal mapping dictionary (`_smr_mapping`), extras list (`_smr_extras`), and defaults dictionary (`_smr_defaults`) at runtime.

When `_deserialize()` executes:

1. **Path Resolution**: The active path is retrieved from state (e.g., `["CSS", "border"]`).
2. **Node Traversal**: `TreeNode.get_nodes_along_path([self._root_node], active_path)` performs recursive lookups across child dictionaries, returning only the nodes speakable at the current depth.
3. **Action Interception**: For every active node, `TreeRule` wraps the user's action with a state transition callback:
   ```python
   action_and_node_change = action + Function(TreeRule._create_spec_fn(self._refresh, spec))
   self._smr_mapping[spec] = action_and_node_change
   ```
4. **Escape Injection**: A deterministic reset command (`cancel <tree_name>`) is automatically added to `_smr_mapping`.
5. **Grammar Reset**: `self.reset()` signals the CCR merger and Dragonfly engine to recompile and activate the updated grammar mapping.

### 2.3 The State Traversal and Auto-Reset Lifecycle

The state machine transitions through three distinct phases:

```
[ Root Inactive / Idle ]
         │
         ▼  (Speak Root Spec: e.g., "I say zero")
[ Depth 1 Active: Child Specs Speakable ]
         │
         ▼  (Speak Child Spec: e.g., "two A one")
[ Depth 2 Active: Sub-child Specs Speakable ]
         │
         ├──► [ Speak Leaf Node (0 Children) ] ───┐
         ├──► [ Speak "cancel <tree_name>" ] ─────┼──► [ Auto-Reset to Root ]
         └──► [ Unrelated Context Stack Action ] ─┘
```

1. **Descent**: When the user speaks a valid node spec, the wrapped callback invokes `_refresh(spec)`. The spoken spec is appended to `active_path`.
2. **Leaf Node Detection**: `_detect_leaf_node_reached()` inspects the resulting node. If `len(current_node.get_children()) == 0`, the tree detects that a terminal command completed and purges `active_path` completely (`del active_path[:]`).
3. **Cancellation and External Interruption**: Saying `cancel <tree_name>` forces `_refresh()` with no arguments, clearing the path. Executing an unrelated command outside the tree triggers a context reset in the CCR manager, returning the grammar to its root state.

---

## 3. Why NodeRule Was Historically Underused

Despite solving grammar complexity limits, `NodeRule` saw minimal adoption across upstream Caster and custom user configurations. The primary blockers were operational rather than algorithmic:

| Bottleneck | Technical Root Cause | Practical Consequence |
| :--- | :--- | :--- |
| **Cognitive Blindness** | No visual display of the active path or valid next commands. | Users had to memorize multi-tiered voice trees in their head. Forgetting a node name trapped the user mid-branch. |
| **Authoring Complexity** | Hand-writing nested `TreeNode` constructors in Python. | Writing a comprehensive domain tree (such as the 559-line `css.py`) required manual nesting of dozens of lists and objects. |
| **Modal Lock-in** | Strict sequential branching prevented fluid cross-grammar chaining. | In standard CCR, users chain multiple independent actions in one breath (`hug shock slap`). NodeRule required sequential step-by-step traversal. |
| **State Persistence Friction** | Early implementations serialized `active_path` into `settings.toml`. | Disk I/O overhead on state changes caused latency spikes and configuration corruption if paths broke. |

---

## 4. How AI and Modern UI Systems Transform NodeRule

The historical bottlenecks of `NodeRule` were caused by manual authoring and the lack of a real-time visual interface. Modern tooling eliminates both constraints.

### 4.1 Automated Tree Generation via AI

Instead of manually constructing nested Python dictionaries, LLMs can convert formal documentation, OpenAPI schemas, or CLI manuals into fully validated `TreeNode` hierarchies in seconds.

Target areas for automated tree synthesis include:

- **Complex CLI Builders**: Multi-stage command builders for `docker`, `kubectl`, `git`, and `aws-cli`.
- **Domain-Specific Languages**: CSS property trees, SQL clause builders, and regular expression generators.
- **Form Navigation and Dialogs**: Wizard-driven data entry with constrained choices at each field.

### 4.2 Real-Time Visual Feedback via Caster HUD (`NodeChangeEvent`)

`TreeRule` already contains an internal event hook for visual telemetry:

```python
if self._hooks_runner is not None:
    event = NodeChangeEvent(self._tree_name, active_path, [n.get_spec() for n in active_nodes])
    self._hooks_runner.execute(event)
```

When connected to the Caster HUD:

1. **Breadcrumb Display**: The HUD renders the active path in real time (e.g., `CSS › Border › Top`).
2. **Next-Command Palette**: The HUD lists all speakable child nodes for the current depth.
3. **Zero Memorization**: The user reads available options directly from the screen, eliminating cognitive blindness.

---

## 5. Architectural Comparison: Temporal Trees (`NodeRule`) vs Spatial Contexts (`ADCE` / `AppContext`)

A common point of confusion is how `NodeRule` compares to context engines like `ADCE` or Dragonfly's native `AppContext`. 

The fundamental distinction lies in **what drives the grammar activation**:

- **Spatial Context (`ADCE` / `AppContext`)**: Driven by the **external environment** (where the operating system focus and cursor reside).
- **Temporal State Tree (`NodeRule`)**: Driven by **utterance history** (the sequence of voice commands spoken over time).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 SPATIAL LAYER: ADCE / AppContext / FuncContext              │
│  • Input: Win32 Foreground HWND, Process Name, UIA Micro-Zone               │
│  • Scope: "Is the user currently inside VS Code Integrated Terminal?"      │
│  • Mutation Trigger: Hardware focus change, mouse click, Alt+Tab            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ (Activates Scoped Rule)
┌─────────────────────────────────────────────────────────────────────────────┐
│                 TEMPORAL LAYER: NodeRule / TreeRule State Machine           │
│  • Input: Prior spoken command specs (active_path)                          │
│  • Scope: "The user is at Step 2 of a 4-step Git Interactive Rebase"        │
│  • Mutation Trigger: Speech recognition callback (_refresh)                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Structural Comparison

| Dimension | Spatial Context (`ADCE` / `AppContext`) | Temporal State Tree (`NodeRule` / `TreeRule`) |
| :--- | :--- | :--- |
| **Primary Driver** | External OS and window accessibility state. | Internal conversational state and utterance sequence. |
| **Evaluation Timing** | Checked before an utterance is matched. | Checked after an utterance executes to rebuild the next grammar. |
| **Grammar Activation** | Enables or disables entire rules based on focus. | Rewrites active specs within a single rule dynamically. |
| **Context Scope** | Process, window title, UI Automation control type. | Branch path depth within a predefined command trie. |
| **Failure Mode** | Stale focus cache if poller lags behind OS. | User speaking an invalid spec while locked in a sub-branch. |
| **Ideal Use Case** | Scoping rules to VS Code, Browser, or Terminal. | Multi-step wizards, property builders, nested menus. |

### Hierarchical Fusion (The Combined Pattern)

The most effective design combines both systems in a two-tier hierarchy:

1. **Outer Guard (Spatial)**: Use `AppContext` or `ADCE` (`FuncContext`) to ensure the rule is only active when the target application is focused.
2. **Inner Workflow (Temporal)**: Inside that application, use a `TreeRule` to guide the user through a structured, multi-step operation.

---

## 6. Concrete Implementation Example: Git Interactive Rebase Tree

Below is a self-contained, working example of a `TreeRule` designed for multi-step Git interactive rebase workflows.

```python
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024-2026 Amir Farhadi

from castervoice.lib.actions import Text, Key
from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.selfmod.tree_rule.tree_node import TreeNode
from castervoice.lib.merge.selfmod.tree_rule.tree_rule import TreeRule
from castervoice.lib.merge.state.actions2 import NullAction

H = TreeNode


def get_git_rebase_tree():
    """
    Constructs a 3-tier stateful tree for Git rebase operations:
    1. Start: "git rebase"
    2. Branch selection: "onto main", "interactive head", "abort", "continue"
    3. Option selection: specific commit counts or sub-actions
    """
    commit_depths = [
        H("one", Text("1") + Key("enter")),
        H("two", Text("2") + Key("enter")),
        H("three", Text("3") + Key("enter")),
        H("five", Text("5") + Key("enter")),
        H("ten", Text("10") + Key("enter")),
    ]

    rebase_branches = [
        H("interactive head", Text("git rebase -i HEAD~"), commit_depths),
        H("onto main", Text("git rebase origin/main") + Key("enter")),
        H("onto master", Text("git rebase origin/master") + Key("enter")),
        H("continue", Text("git rebase --continue") + Key("enter")),
        H("abort", Text("git rebase --abort") + Key("enter")),
        H("skip", Text("git rebase --skip") + Key("enter")),
    ]

    return H("rebase", NullAction(), rebase_branches)


class GitRebaseTreeRule(TreeRule):
    pronunciation = "git rebase tree"

    def __init__(self):
        super(GitRebaseTreeRule, self).__init__("git rebase tree", get_git_rebase_tree())


def get_rule():
    return [GitRebaseTreeRule, RuleDetails(ccrtype=CCRType.SELFMOD)]
```

---

## 7. Strategic Impact on Voice Rule Design

When deciding whether to implement a new feature as standard CCR mapping rules, ADCE contexts, or a `TreeRule`, apply the following heuristics:

1. **Use Standard CCR Rules** when commands are independent, frequently combined, and do not rely on prior execution state (e.g., standard text editing, cursor navigation, general programming keywords).
2. **Use ADCE / AppContext** when commands must only exist inside specific applications, sub-panes, or document types (e.g., terminal-specific commands, browser-tab switching).
3. **Use TreeRule / NodeRule** when:
   - A command has a rigid sequential structure (Step 1 → Step 2 → Step 3).
   - The total spec list is massive (hundreds of CSS or API properties), and loading them all simultaneously degrades speech engine accuracy.
   - The user benefits from an interactive wizard where choices narrow at each stage.
   - The HUD can display the active choices, preventing cognitive load.

---

*Recorded in `docs/framework_explainers/noderule_and_treerule_architecture.md`.*
