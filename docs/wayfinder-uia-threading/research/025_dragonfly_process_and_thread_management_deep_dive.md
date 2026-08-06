# Ticket 025 Deep Dive: Dragonfly Process and Thread Management

This document provides a definitive, evidence-based analysis of how the `dictation-toolbox/dragonfly` repository handles threads, processes, and concurrency.

## 1. Process Spawning (External Applications)
When Dragonfly launches external applications (e.g., through voice commands that open programs or run batch scripts), it strictly utilizes the standard Python `subprocess.Popen` module. 

**Evidence:**
- In `dragonfly/actions/action_cmd.py` (Lines 240-243), commands are executed via:
  ```python
  self._proc = subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                stdin=subprocess.PIPE)
  ```
- In `dragonfly/actions/action_startapp.py` (Line 138), it similarly uses `Popen(self._args, cwd=self._cwd)`.

**Fact:** Dragonfly does not reinvent process spawning. It relies on non-blocking `subprocess.Popen` calls, allowing the target application to launch without locking the main voice recognition thread.

## 2. Multiprocessing
**Fact:** A repository-wide search (`grep`) for `import multiprocessing` yields **zero results**. 

Dragonfly does not spawn Python child processes to distribute workloads. Its entire execution model is confined to a single Python process (`python.exe` or `pythonw.exe`), inside which it relies on native OS threads.

## 3. Thread Management and The Main Loop
Dragonfly's architecture fundamentally orbits around a single **Main Thread** that runs a continuous polling loop, occasionally spinning off daemon `threading.Thread` instances for specific subsystems.

### The Synchronous Engine Loop
The core recognition loop runs on the main thread and is strictly synchronous. 

**Evidence:** 
In `dragonfly/engines/backend_sapi5/engine.py` (Lines 361-364), the recognition engine enters a blocking `while` loop:
```python
while self._recognizer is not None:
    pythoncom.PumpWaitingMessages()
    self.call_timer_callback()
    time.sleep(0.005)
```
- It pumps COM messages (`pythoncom.PumpWaitingMessages()`).
- It processes timers.
- It sleeps for 5 milliseconds (`0.005`) to prevent 100% CPU utilization.
- When an utterance is recognized, the COM event interrupts the pump and executes the grammar callbacks *synchronously* on this exact same thread.

### Accessibility Daemon Threads (UIA and IA2)
When dealing with Windows Accessibility APIs, Dragonfly spins up dedicated background threads (`threading.Thread`) to isolate the COM interop.

**Evidence (UIA):**
In `dragonfly/accessibility/uia.py`, a `Controller` class is defined. When `start()` is called (Lines 113-115):
```python
thread = threading.Thread(target=self._start_blocking)
thread.daemon = True
thread.start()
```
- It creates a daemon thread.
- The `_start_blocking` method loops infinitely, polling a thread-safe queue: `capture = self._closure_queue.get(timeout=0.01)`.

**Evidence (IAccessible2):**
In `dragonfly/accessibility/ia2.py` (Line 117), it does the exact same thing: `thread = threading.Thread(target=self._start_blocking)`. However, its internal loop (Line 83) is slightly different:
```python
while not self._shutdown_event.is_set():
    pyia2.Registry.iter_loop(0.01)
```

### IPC (Inter-Process Communication) and Synchronous Blocking
Dragonfly does not use complex IPC (like sockets or named pipes) because everything runs in the same process memory space. Threads communicate using `queue.Queue` and `threading.Event`.

**The "Run Sync" Convention:**
Even though accessibility tasks run on a background thread, the main voice thread *blocks itself* until the task is complete.

**Evidence:**
In both `uia.py` and `ia2.py` (Lines 124-130), the interface exposed to the voice commands is strictly synchronous:
```python
def run_sync(self, closure):
    capture = self.Capture(closure)
    self._closure_queue.put(capture)
    capture.done_event.wait()      # <--- MAIN THREAD FREEZES HERE
    if capture.exception:
        raise capture.exception
    return capture.return_value
```

## Summary of Facts
1. **Single Process**: Dragonfly is a monolithic, single-process application.
2. **Synchronous Core**: The main engine loop is synchronous. Voice commands freeze the engine until their python logic returns.
3. **Daemon Threads**: Background tasks (timers, accessibility polling) use `threading.Thread(daemon=True)`.
4. **Queue & Event Blocking**: The main thread communicates with daemon threads using `queue.Queue.put()` and immediately blocks itself using `threading.Event.wait()`.
5. **No Independent Windows Message Pump in UIA**: The UIA thread (`uia.py`) loops over `queue.get()` with a timeout but contains zero COM message pump logic, making it highly susceptible to cross-process COM deadlocks.
