# Architectural Analysis: Caster `NumberRef` Integration, Dragonfly `Number` AST & CCR Dynamics

This document provides a comprehensive analysis of the numeric dictation behaviors in **Caster** when using Dragonfly's `NumberRef`, explaining why specific number combinations work seamlessly while others encounter speech engine misrecognitions or greedy remainder matching.

---

## 1. Executive Summary & Empirical Findings

When Caster's `numeric.py` rule is updated to use `NumberRef("wnKK", zero=True)` without altering core Dragonfly:

| Spoken Sequence Type | Example | Behavior | Underlying Mechanism |
| :--- | :--- | :--- | :--- |
| **Digit / Small Series ($<100$)** | `numb 1 2 3 4 5 6 7` | **Highly Reliable** | Handled by Dragonfly `series` branch (`Integer(0, 100)`). Eliminates the old 4-digit limit. |
| **Single Large Number ($>100$)** | `numb 50,000` or `54,448` | **Highly Reliable** | Handled by Dragonfly `single` branch (`Integer(1, 1000000)`). |
| **Large Number followed by Small Series** | `numb 50,000 1 2 3 4 5` | **Intermittent** | Works only sometimes; prone to acoustic graph misrecognitions. |
| **Small Series followed by Large Numbers** | `numb 1 2 3 4 10,000 4,000` | **Unreliable / Fails** | Fails to cleanly separate `series` ($<100$) and CCR `single` ($>100$) transitions. |
| **Remainder Overlap (Large + `"1"`)** | `numb 10,000 1 2 3 4` | **Fails / Misrecognizes** | `single` sees `"ten thousand"` + `"one"` and greedily consumes `"one"` as an integer remainder ($10,001$), leaving `"2 3 4"` orphaned. |
| **Arbitrary Complex Mixed Combinations** | `numb 10,000 20,000 1 2 3` | **Unreliable** | Frequent acoustic mismatches / bleed into adjacent active CCR rules due to graph complexity. |

---

## 2. Deep Dive: Why Combining Large and Small Numbers Is Unreliable

### A. The Core Principle: Pure Patterns vs. Mixed Combinations
Empirical testing demonstrates that **neither mixed order (large $\to$ small or small $\to$ large) is reliable within a single continuous breath**. 

The only two 100% reliable dictation patterns are:
1. **Single Large Magnitude Numbers** (e.g. `numb 50,000` or `54,448`).
2. **Series of Small Numbers / Digits under 100** (e.g. `numb 1 2 3 4 5 6 7` up to 7–8 digits).

---

### B. Remainder Overlap / Orphaned Digits (`numb 10,000 1 2 3 4`) — **FAILURE**
Why does uttering a large number followed immediately by `"one"` in the same breath cause misrecognition (e.g. `10,001` + orphaned digits)?

```
Spoken Phrase:  "ten thousand"  +  "one"  +  "two three four"
                  |--------------------|     |--------------|
                   single matches 10,001     Orphaned words
                   (greedily steals "1")     trigger CCR error
```

1. In English grammar, `"ten thousand"` followed by `"one"` is a valid single integer: **$10,001$**.
2. The `single` branch (`Integer(1, 1000000)`) evaluates `"ten thousand one"`.
3. `single` greedily absorbs `"one"` as the remainder of `"ten thousand"`, producing **$10,001$**.
4. The remaining digits (`"two three four"`) are left without their leading `"one"`, causing the speech engine search graph to throw errors, drop digits, or misrecognize adjacent CCR words (e.g., `"sauce"`, `"ace"`).

---

### C. Arbitrary Complex Combinations & CCR Graph Bleed — **UNRELIABLE**
When attempting to mix multiple large numbers and small digit series in arbitrary orders during a single breath:
- The speech engine search graph evaluates dozens of overlapping paths across all active CCR rules.
- Because `single` and `series` have different boundary conditions, intermediate state transitions bleed into adjacent active CCR commands (e.g., matching phantom formatting/punctuation words like `"sauce"` or `"ace"`).

---

## 3. Dragonfly `Number` AST Structure & Magnitude Matching

The `Number` class in Dragonfly is structured as an `Alternative`:

```python
class Number(Alternative):
    def __init__(self, name=None, zero=False, default=None):
        ...
        single = Integer(None, int_min, self._int_max)
        item = Integer(None, 0, 100)
        series = Sequence([first, repetition])

        children = [single, series]
        Alternative.__init__(self, children, name=name, default=default)
```

### Magnitude Phrases vs. Spoken Chunk Chaining:
- **Spoken Magnitude Phrase (`"thirty thousand"`)**: Evaluates via `single` to $30,000$.
- **Dictating Separate Chunks (`"thirty"` + `"thousand"`)**: If spoken as distinct chunk elements (e.g. `numb 30 1000`), `series` concatenates the chunks into $31,000$.
- **`[single, series]` Order**: Preserves standard magnitude evaluation first, ensuring magnitude phrases like `"thirty thousand"` or `"fifty four thousand four hundred forty eight"` resolve correctly to $30,000$ and $54,448$.

---

## 4. Architectural Recommendation & Most Reliable Patterns

### Practical Reliability Summary

The most reliable and stable dictation patterns under the Caster-only fix (`NumberRef("wnKK", zero=True)` in `numeric.py`) are:

1. **Single Large Magnitude Numbers** (e.g., `numb 50,000` or `54,448` up to $1,000,000$).
2. **Series of Small Numbers / Digits** (e.g., `numb 1 2 3 4 5 6 7` up to 7-8 digits).

> [!NOTE]
> Combining large numbers and small digit series together in a single continuous breath is inherently unreliable due to CCR search graph ambiguity and potential misrecognitions with non-numeric CCR rules. Keep large numbers and small digit series as distinct dictation utterances for 100% reliability.
