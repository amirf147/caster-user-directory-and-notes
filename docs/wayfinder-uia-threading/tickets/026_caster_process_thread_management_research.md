# Ticket 026: Caster Process and Thread Management Deep Dive

**Type**: `wayfinder:research` (Deep Dive / Definitive Analysis)
**Status**: Open / Unclaimed
**Blocks**: Final Architecture Proposal

## Question
Building on Ticket 025, how does Caster specifically manage threads and processes? We need a definitive, fresh, and unbiased analysis of Caster's concurrency model without relying on our past assumptions.

Specifically:
1. **The Architecture of Multiprocessing**: We know certain subsystems (like the Sudoku grid, Homunculus, and mouse alternatives) launch as separate processes. How exactly are these managed? 
2. **Process vs Thread Conventions**: When Caster needs to run background tasks, does it prefer `multiprocessing`, `subprocess`, `threading`, or XML-RPC daemon threads? Is there a unified underlying convention being used, or is it fragmented across different features?
3. **Integration with Dragonfly**: How do Caster's thread and process conventions interact with Dragonfly's synchronous execution loop? Does Caster spawn its own threads that live alongside Dragonfly's loop?

## Next Steps
- Perform a deep, layered code review of the `caster` repository, specifically targeting UI overlays, background workers, node executables, and IPC mechanisms.
- Do not rely on previous summaries—look directly at the raw code to see the actual implementation patterns.
- Produce a long, verbose, expertly crafted, and comprehensive markdown document with extensive code evidence (snippets and file paths) that definitively maps out Caster's thread and process architecture.
- Identify the core conventions Caster uses so we can determine if our UIA server architecture should follow the same pattern or introduce a new one.
