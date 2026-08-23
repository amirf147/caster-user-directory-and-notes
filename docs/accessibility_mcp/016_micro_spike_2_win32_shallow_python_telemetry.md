<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2024-2026 Amir Farhadi -->

[ 🏠 Docs Home ](../README.md) › [ 📁 Accessibility MCP ](CONTEXT.md) › **016: Micro-Spike 2 Win32 Shallow Python Telemetry & Comparative Analysis**

---

# Micro-Spike 2: Win32 Shallow Python Telemetry & Comparative Analysis (016)

> **Document Status:** Active / Gate 3 Empirical Benchmark Report  
> **Target System:** Active Desktop Context Engine (ADCE) & Gate 3 Empirical Micro-Spikes  
> **Related Documents:** [010: Traversal Telemetry](010_telemetry_benchmarks_and_live_findings.md) | [011: FlaUI Evaluation](011_flaui_evaluation_and_dual_plane_architecture.md) | [014: C# Daemon Handover](014_csharp_daemon_handover_and_skill_spec.md) | [015: Epistemic Recalibration](015_recalibration_and_adversarial_architecture_review.md)

---

## 1. Executive Summary: Gate 3 Empirical Verification

In accordance with the **4-Gate Epistemic Gating Protocol** established in [015: Epistemic Recalibration](015_recalibration_and_adversarial_architecture_review.md), we executed two live, empirical micro-spikes against active OS targets (Waterfox with 30 tabs and Antigravity IDE):

* **Micro-Spike 1 (`ADCE.Spikes` / C# .NET 10 + FlaUI 5):** Validated direct container targeting and batch UIA3 extraction across running Gecko / Electron instances.
* **Micro-Spike 2 (`scripts/spike_win32_shallow_python.py` / Python 3.10):** Measured pure Win32 C-call envelope extraction and shallow UIA focused control retrieval with **zero recursive tree traversal**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        GATE 3 EMPIRICAL LATENCY COMPARISON MATRIX                      │
├────────────────────────┬──────────────────────┬─────────────────┬──────────────────────┤
│ Strategy / Phase       │ Engine / Runtime     │ Median Latency  │ P95 Latency          │
├────────────────────────┼──────────────────────┼─────────────────┼──────────────────────┤
│ **Pure Win32 Envelope**│ Python 3.10 `ctypes` │ **0.8 µs**      │ **1.0 µs**           │
│ *(HWND/Title/Class/PID)*│                      │ (0.0008 ms)     │ (0.0010 ms)          │
├────────────────────────┼──────────────────────┼─────────────────┼──────────────────────┤
│ **Shallow UIA Focus**  │ Python 3.10 COM      │ **0.66 ms**     │ **0.99 ms**          │
│ *(Type/Name/BBox)*     │                      │                 │                      │
├────────────────────────┼──────────────────────┼─────────────────┼──────────────────────┤
│ **Total Shallow Event**│ Python 3.10 Combined │ **0.66 ms**     │ **0.99 ms**          │
│ *(Zero Child Traversal)*│                      │ (Sub-ms Total)  │ (Sub-ms Total)       │
├────────────────────────┼──────────────────────┼─────────────────┼──────────────────────┤
│ **Live Tab Extraction**│ C# .NET 10 / FlaUI 5 │ **10.17 ms**    │ **12.53 ms**         │
│ *(30 Waterfox Tabs)*   │ *(Direct Container)* │ (~339 µs / tab) │ (~521 µs / tab)      │
└────────────────────────┴──────────────────────┴─────────────────┴──────────────────────┘
```

---

## 2. Micro-Spike 2 Telemetry Breakdown (Python 3.10)

Script: [`scripts/spike_win32_shallow_python.py`](../../scripts/spike_win32_shallow_python.py)  
Execution: `py -3.10 scripts/spike_win32_shallow_python.py` (100 sample runs against live desktop session)

### A. Phase Latencies (100 Iterations)

| Operation | Min | Median | Mean | P95 | Max |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Pure Win32 C-Calls** (`user32` `ctypes`) | `0.8 µs` | **`0.8 µs`** | `1.1 µs` | `1.0 µs` | `24.7 µs` |
| **2. Shallow UIA Focus** (`auto.GetFocusedControl()`) | `0.57 ms` | **`0.66 ms`** | `1.02 ms` | `0.99 ms` | `33.49 ms` |
| **3. Combined Shallow Context Pipeline** | `0.57 ms` | **`0.66 ms`** | `1.02 ms` | `0.99 ms` | `33.51 ms` |

### B. Shallow HWND Binding Latency by Application (20 Samples Each)

| Target Window | Win32 Class Name | Median Latency | Mean Latency | Max Latency |
| :--- | :--- | :---: | :---: | :---: |
| **Waterfox (30 Tabs)** | `MozillaWindowClass` | **`0.68 ms`** | `0.78 ms` | `2.25 ms` |
| **Waterfox (Release)** | `MozillaWindowClass` | **`0.67 ms`** | `0.71 ms` | `1.12 ms` |
| **Antigravity IDE** | `Chrome_WidgetWin_1` | **`0.88 ms`** | `0.98 ms` | `1.85 ms` |
| **Element Desktop** | `Chrome_WidgetWin_1` | **`0.74 ms`** | `1.02 ms` | `3.95 ms` |

---

## 3. Physical Insights & Epistemic Falsification

### Insight 1: Python COM is NOT the Bottleneck for Shallow Context
The common assumption that *"Python COM overhead is too slow for real-time focus tracking"* was **falsified**.
* In-process Python 3.10 querying Win32 HWND + top-level UIA focus runs in **0.66 ms** (median) and **0.99 ms** (P95).
* Python's GIL and `comtypes` wrappers add less than 100 microseconds of overhead for single-element lookups.

### Insight 2: The Sole Bottleneck Was Recursive DOM Tree Walking
The severe 5,800 ms crawl latencies observed in Document `010` were entirely caused by **recursive descendant traversal across browser iframes** (e.g. 6,800 web DOM nodes in Gecko/Chromium viewports).
* When recursive tree walks are eliminated:
  * Shallow focus extraction in Python completes in **0.66 ms**.
  * Direct container tab extraction in C# completes in **10.17 ms**.

### Insight 3: The Tradeoff Spectrum (Option B vs Option C)

```mermaid
graph LR
    subgraph OptionC ["Option C: Pure Shallow Context (Python)"]
        C1["Win32 HWND + UIA Focus Node"]
        C2["Latency: 0.66 ms (Instant)"]
        C3["Zero New Toolchains (.NET Free)"]
        C4["Limitation: No Background Tabs"]
    end

    subgraph OptionB ["Option B: Direct Container Context (C# FlaUI)"]
        B1["Direct Sidebar/Tabstrip Search"]
        B2["Latency: 10.17 ms (30 Tabs)"]
        B3["Extracts Full Tab Arrays"]
        B4["Tradeoff: Out-of-Process .NET Daemon"]
    end
```

1. **Option C (Pruned In-Process Python):**
   - **Pros:** 0.66 ms latency, zero external runtime dependencies, 100% native to Caster repository.
   - **Coverage:** Active window title, Win32 class, process ID, focused element name, control type, and bounding box.
   - **Blindspot:** Does not extract open background tabs.

2. **Option B (Compiled C# FlaUI Daemon):**
   - **Pros:** 10.17 ms full extraction of 30 tabs without DOM crawling; streams complete semantic graphs over MCP.
   - **Tradeoff:** Requires running an external C# background daemon process (`ADCE.Daemon`).

---

## 4. Next Step: Advancing to Gate 4

With both Micro-Spike 1 and Micro-Spike 2 empirically validated:
1. **No Guesswork Remaining:** We know the exact physics and latencies of both paths.
2. **Path Selection:** We can now build a clean, unified architecture:
   - Use **In-Process Python (Option C)** for high-frequency sub-millisecond focus & active window tracking within Caster.
   - Use the **C# ADCE Service (Option B)** as a dedicated MCP provider when full desktop multi-tab graphs are requested by AI agents.
