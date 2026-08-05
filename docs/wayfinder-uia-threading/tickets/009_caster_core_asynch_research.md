# Ticket 009: Research Caster Core Asynch Threading & UI Overlays

**Type**: `wayfinder:research` (AFK)
**Status**: [CLOSED]
**Blocks**: Core Engine Threading Understanding

## Question
How does the `Caster` core engine handle threading for its asynchronous UI overlays (Legion Grid, Mouse Grids, Homunculus) and why are they currently failing to work?

Specifically:
1. What exactly is "Homunculus" in the context of Caster?
2. How are these asynchronous features leveraging Python's `threading` library?
3. What are the architectural flaws in this implementation that could cause them to fail or become unresponsive in modern environments?

## Resolution
1. **Homunculus**: It is an asynchronous GUI overlay (built in PyQt/Tkinter) launched by Caster to display interactive prompts (like confirmations or macro recording forms) without blocking the voice engine.
2. **Threading Strategy**: Caster spawns a completely separate Python process via `subprocess.Popen("pythonw.exe")`. The new process runs its GUI event loop on the main thread and spins up a dedicated `threading.Thread` to run an XML-RPC server to receive commands from Caster.
3. **Flaws & Failures**: The grids are failing silently due to three primary flaws:
   - **Environment Mismatch**: By hardcoding execution to `pythonw.exe`, it bypasses the `py -3.10` launcher. This often launches a system Python devoid of required dependencies (`PyQt5`, `dragonfly2`), causing silent crashes.
   - **Port Zombie Locks**: The XML-RPC servers use hardcoded ports. If Caster crashes, the grid processes live for another 5 minutes. Restarting Caster and triggering a grid instantly causes a port conflict crash.
   - **Legion DLLs**: Legion's edge-detection relies on `tirg.dll` loaded via `ctypes`. This breaks easily if the environment architectural state is unexpected.

**Full Educational Breakdown**: [009_caster_core_asynch_threading_breakdown.md](../research/009_caster_core_asynch_threading_breakdown.md)
