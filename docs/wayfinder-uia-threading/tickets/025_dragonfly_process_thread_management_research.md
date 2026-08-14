[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Tickets ](../../README.md#wayfinder-uia--threading-research) › **Ticket 025: Dragonfly Process and Thread Manage...**

---

# Ticket 025: Dragonfly Process and Thread Management Deep Dive

**Type**: `wayfinder:research` (Deep Dive / Definitive Analysis)
**Status**: Open / Unclaimed
**Blocks**: Final Architecture Proposal

## Question
How does Dragonfly actually manage threads and processes under the hood? We need a definitive, fresh, and unbiased analysis of its execution model without relying on our past assumptions. 

Specifically:
1. **The Execution Loop**: When you run Dragonfly and load rules, what is the exact lifecycle of the main thread? 
2. **Process Spawning**: When Dragonfly executes commands (like opening an application, `run_command`, or executing a macro), how are those processes spawned? Does it use `subprocess.Popen`? Do they run synchronously or asynchronously? 
3. **Thread Management**: When does Dragonfly spin off separate threads versus entirely separate processes? Are timers, accessibility hooks, and microphone listeners running on the same thread or different threads? 
4. **Underlying Conventions**: What is the core philosophy and convention Dragonfly uses for concurrency, and how does it handle IPC (Inter-Process Communication) if at all?

## Next Steps
- Perform a deep, layered code review of the `dictation-toolbox/dragonfly` repository, specifically targeting process execution (`dragonfly/actions`), engine loops (`dragonfly/engines`), and threading utilities.
- Do not rely on previous summaries—look directly at the raw code and standard libraries used.
- Produce a long, verbose, expertly crafted, and comprehensive markdown document with extensive code evidence (snippets and file paths) that definitively maps out Dragonfly's thread and process architecture.

## Research Breakdown
- [Dragonfly Process and Thread Management Deep Dive](../research/025_dragonfly_process_and_thread_management_deep_dive.md)
