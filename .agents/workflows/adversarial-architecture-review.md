---
description: Adversarial architectural review and 4-gate epistemic verification protocol to prevent premature convergence and solution bias.
---

# Adversarial Architecture Review & Epistemic Gating Protocol

Use this workflow whenever a significant architectural change, runtime pivot (e.g. Python to C#), or subsystem rewrite is proposed. Follow the 4 sequential gates strictly.

---

## Instructions

### 1. Gate 1: Physical Observation & Telemetry
- **Rule:** Architectural proposals and solutions are **STRICTLY FORBIDDEN** in this phase.
- **Collect Telemetry:** Gather and report raw empirical measurements from live OS benchmarks (e.g. `nodes_scanned`, `elapsed_ms`, error codes, WinEvent logs).
- **Physical Hypothesis:** Formulate a hypothesis grounded purely in OS, kernel, or COM mechanics (e.g. `UIAutomationCore.dll` message pump contention vs Python GIL).

### 2. Gate 2: Adversarial Red-Team (Ban the Verdict)
- **Role:** Adopt the mindset of a *Cynical Principal Systems Architect* attempting to kill the candidate proposal.
- **Generate 3 Mutually Exclusive Options:**
  - Formulate 3 distinct architectural paths (e.g., direct process extension, out-of-process daemon, pruned in-process observer).
- **Expose Fatal Flaws:** Identify at least 3 fatal flaws and hidden operational assumptions for **each** option:
  1. *OS boundary & physics fragility* (e.g., cross-process IPC stalls, asynchronous message pump deadlocks).
  2. *Developer & toolchain tax* (e.g., dual-runtime builds, SDK packaging friction).
  3. *Runtime IPC / lifecycle complexity* (e.g., pipe crashes, orphaned daemon processes).
- **No Early Verdict:** Do not declare a "winner" or approve an architecture based on theory alone.

### 3. Gate 3: Empirical Micro-Spike (Falsification First)
- **Design Minimal Spike:** Write a standalone test script under **50 lines** targeting the single most dangerous physical assumption (e.g. testing `CacheRequest` against a live 50-tab browser window).
- **Execute Live:** Run the micro-spike against active, real-world OS target windows.
- **Evaluate Data:**
  - If empirical measurements falsify the premise, **discard the proposal immediately** and return to Gate 2.
  - If empirical measurements validate the premise, proceed to Gate 4.

### 4. Gate 4: Architectural Blueprint & Formal Specification
- **Formalize Design:** Only after the Gate 3 micro-spike empirically proves viability and sub-millisecond latency, draft the formal architecture specification, sequence diagrams, and implementation plan.
- **Living Context Sync:** Update [`docs/accessibility_mcp/CONTEXT.md`](../../docs/accessibility_mcp/CONTEXT.md) and [`docs/context/repository-brain.md`](../../docs/context/repository-brain.md).

---

## Execution Checklist

- [ ] Has raw physical telemetry been gathered without solutionizing? (Gate 1)
- [ ] Were 3 mutually exclusive options evaluated with 3 fatal flaws each? (Gate 2)
- [ ] Was a <50-line micro-spike executed against active OS targets? (Gate 3)
- [ ] Did the micro-spike data confirm performance before drafting the formal spec? (Gate 4)
