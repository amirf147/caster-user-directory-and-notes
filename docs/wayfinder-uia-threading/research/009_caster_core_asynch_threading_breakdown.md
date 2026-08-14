[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Research ](../../README.md#wayfinder-uia--threading-research) › **Caster Core Asynchronous Threading & Overlays (...**

---

# Caster Core Asynchronous Threading & Overlays (Educational Breakdown)

This document explores how the `Caster` core engine (`castervoice/asynch`) handles asynchronous UI overlays like Homunculus, Legion Grid, and Mouse Grids, and investigates the architectural flaws causing them to fail in modern Python 3.10 environments.

## 1. What is Homunculus (and Legion)?
**Homunculus** is an asynchronous graphical UI overlay (built in Qt/PyQt or Tkinter) used to display interactive prompts to the user—such as confirmation dialogs ("Are you sure?"), directory selection windows, or macro recording feedback—without blocking the main voice engine.

**Legion Grid** and **Mouse Grids** operate on the exact same architectural pattern: they are transparent full-screen overlay applications built in Tkinter that draw numbered boxes over UI elements so you can click them by voice.

## 2. The Asynchronous Architecture
Instead of running these UI loops inside the Caster voice engine (which would immediately freeze speech recognition), Caster isolates them using a clever but fragile pattern:
1. **Subprocess Invocation**: When you trigger a grid, Caster uses `subprocess.Popen` to launch a completely separate Python process (using `pythonw.exe`).
2. **The GUI Thread**: The new process immediately starts its native GUI event loop (e.g., Tkinter's `mainloop()` or Qt's `QApplication.exec_()`) on its main thread, which is required by Windows.
3. **The XML-RPC Daemon Thread**: To receive commands (like "click box 5"), the overlay spawns a dedicated background `threading.Thread` running an XML-RPC server (`SimpleXMLRPCServer`). 
4. **Timeouts**: Because these overlays are detached from Caster, they run an internal `threading.Timer(300, self.xmlrpc_kill)` to automatically kill themselves after 5 minutes to prevent zombie processes.

## 3. Why are they failing now?
If you are noticing that Legion or Homunculus are no longer appearing, there are three catastrophic flaws in this legacy architecture when running in modern setups (like Python 3.10 with virtual environments):

### Flaw A: The Launcher Path Mismatch (The `pythonw.exe` trap)
In `h_launch.py`, Caster tries to launch the overlay using `settings.SETTINGS["paths"]["PYTHONW"]`, which resolves to `sys.exec_prefix + "\pythonw.exe"`. 
However, as per your workspace rules, you must run Caster using the `py -3.10` launcher. When Caster manually calls `pythonw.exe`, it bypasses the launcher and often breaks out of the virtual environment, launching a system Python that lacks `PyQt5`, `PIL`, or `dragonfly2`. Because it is launched via `pythonw.exe` (no console), the `ImportError` happens silently in the background, and the grid simply never appears.

### Flaw B: XML-RPC Port Conflicts (Zombie Locks)
The overlays bind their XML-RPC servers to hardcoded ports (e.g., `comm.com_registry["grids"]`). If Caster crashes or is restarted during development, the detached `pythonw.exe` process stays alive for 5 minutes (due to the 300s timeout). When you try to launch a grid again, the new process tries to bind to the same hardcoded port, crashes instantly with an `OSError: [WinError 10048] Only one usage of each socket address is permitted`, and dies silently.

### Flaw C: 32-bit vs 64-bit DLLs (Legion specific)
Legion relies on a pre-compiled C++ library (`tirg-32.dll` or `tirg-64.dll`) to scan the screen for text edges. If the Python environment mismatch (Flaw A) results in loading a Python architecture that doesn't cleanly match the available DLLs, `ctypes.cdll.LoadLibrary` fails.

## Conclusion
The Caster core's approach to asynchronous UI is completely decoupled from COM or UIA threading. It relies entirely on multi-processing via `subprocess.Popen` and inter-process communication via `XML-RPC`. To fix these grids, the `PYTHONW` path logic must be rewritten to respect modern Python launcher (`py`) and virtual environment paradigms, and the XML-RPC servers must aggressively check for port locks.

*(Research conducted under Wayfinder Ticket 009)*
