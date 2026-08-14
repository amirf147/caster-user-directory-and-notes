[ 🏠 Docs Home ](../README.md) › [ 📁 Architecture ](../README.md#architecture) › **Architecture Decision Record: Background Worker...**

---

# Architecture Decision Record: Background Worker Pool for Speech Tasks

> [!WARNING]
> **DEPRECATED**: This ADR was produced during an initial grilling session and has been deprecated. Generic thread pools violate Microsoft UIA COM (STA/MTA) threading constraints and cause hangs/crashes. We have pivoted to the Wayfinder methodology to architect a dedicated UIA Server instead. See [Wayfinder Map](../wayfinder-uia-threading/map.md).

## Context
The Caster and Dragonfly speech recognition stack operates on a single-threaded, synchronous execution model. When user rules execute blocking operations—such as `time.sleep()` loops in `app_switcher.py` or synchronous Microsoft UI Automation (UIA) COM calls in `text_editing.py`—the main speech thread completely freezes. This causes microphone audio to build up in a background queue, resulting in a rapid-fire surge of delayed voice commands once the blocking call finishes (or is interrupted by `Ctrl+C`).

We needed a unified, safe way to handle these long-running tasks without blocking the main speech engine, while also keeping the user informed of the task's progress.

## Decision
1. **Unified Background Worker Pool:** We will introduce a centralized Background Worker Pool (using Python's `concurrent.futures.ThreadPoolExecutor`). Instead of spinning up custom daemon threads for every feature, all blocking tasks (UIA calls, window waiting) will be submitted as "jobs" to this single service. 
2. **Dual-Channel Communication Strategy:**
   - **Caster HUD (`printer.out`):** Will be used for simple, user-friendly notifications (e.g., "Color-coded notification: Task Started" or "Tab focused"). This keeps the user informed without cluttering their screen.
   - **Terminal Output (PowerShell):** Will be strictly reserved for developer-level diagnostic logging, stack traces, and deep error reports.

## Consequences
- **Positive:** The main speech engine will remain highly responsive. We eliminate the "freeze and surge" bug. We now have a standard convention for adding new, heavy features in the future.
- **Negative/Risk:** If a UIA text editing job hangs indefinitely in the background, we will need to ensure the worker thread eventually times out so the pool doesn't run out of available workers.
