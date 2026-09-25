[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](005_caster_hud_requirements_and_specifications.md) › **017: Native HUD Process Lifecycle & Plugin Decoupling**

---

> [!NOTE]
> **Document Status**: *Active Production Architecture & Canonical Reference (NOT SUPERSEDED)*.  
> Details the runtime architecture of the native Caster Heads-Up Display (HUD), comparing its legacy behavior with the current decoupled implementation using side-by-side code blocks, and specifying the cross-platform strategy pattern for Windows, Linux, and macOS.

# 017: Native HUD Process Lifecycle Management and Plugin Decoupling

This document specifies the architecture, runtime lifecycle, and inter-process communication (IPC) mechanics of Caster's traditional Heads-Up Display (`castervoice/asynch/hud.py`). It clarifies how the core HUD operates independently of the plugin system, contrasts its current capabilities with legacy upstream Caster through side-by-side code comparisons, details the cross-platform process lifecycle strategy, and outlines the exact file boundaries needed to extract these enhancements into a standalone upstream git branch.

---

## 1. Executive Summary and IPC Foundation

### IPC Mechanism: Was It Always XML-RPC?
The traditional Caster Heads-Up Display has always used XML-RPC over a local TCP loopback socket. 

Inside `castervoice/asynch/hud.py`, the standalone process initializes a standard Python `SimpleXMLRPCServer`:
```python
# Upstream baseline and current implementation in hud.py
server_address = (Communicator.LOCALHOST, Communicator().com_registry["hud"])  # 127.0.0.1:8338
server = SimpleXMLRPCServer(server_address, logRequests=False, allow_none=True)
server.register_function(self.xmlrpc_ping, "ping")
server.register_function(self.xmlrpc_send, "send")
server.register_function(self.xmlrpc_show_hud, "show_hud")
server.register_function(self.xmlrpc_hide_hud, "hide_hud")
server.register_function(self.xmlrpc_clear, "clear_hud")
server.register_function(self.xmlrpc_show_rules, "show_rules")
server.register_function(self.xmlrpc_hide_rules, "hide_rules")
server.register_function(self.xmlrpc_kill, "kill")
```

Within the main Caster process, client communication passes through `control.nexus().comm.get_com("hud")`, which wraps an `xmlrpc.client.ServerProxy("http://127.0.0.1:8338")`.

While the underlying XML-RPC wire protocol has remained identical, the **process management, connection resilience, threading model, and error handling** surrounding that XML-RPC connection in upstream Caster were fragile. The enhancements documented below resolve these operational bottlenecks without altering the base GUI window.

---

## 2. Granular Side-by-Side Code Comparison: Upstream vs. Current

The following sections provide code comparisons between the original upstream implementation (`castervoice/asynch/hud_support.py`, `castervoice/rules/core/utility_rules/caster_rule.py`) and the current resilient architecture.

### 2.1. Process Spawning and State Validation (`start_hud`)

In upstream Caster, `start_hud()` checked `ping()` and spawned a subprocess, but completely discarded the returned `subprocess.Popen` handle. It maintained no process state tracking and did not bind the child process to any operating system job object.

#### Upstream Implementation:
```python
# Upstream Caster: castervoice/asynch/hud_support.py
def start_hud():
    hud = control.nexus().comm.get_com("hud")
    try:
        hud.ping()
    except Exception:
        # Popen handle was discarded; no OS job binding
        subprocess.Popen([settings.SETTINGS["paths"]["PYTHONW"],
                          settings.SETTINGS["paths"]["HUD_PATH"]])
```

#### Current Resilient Implementation:
```python
# Current Caster: castervoice/asynch/hud_support.py
_HUD_PROCESS = None
_CURRENT_HUD_PATH = None
_IS_STARTING = False
_PROCESS_STRATEGY = get_process_strategy()

def start_hud(hud_path=None):
    global _HUD_PROCESS, _CURRENT_HUD_PATH, _IS_STARTING
    if hud_path is None:
        try:
            hud_path = settings.SETTINGS["paths"]["HUD_PATH"]
        except Exception:
            hud_path = "hud.py"
    _CURRENT_HUD_PATH = hud_path

    # Prevent concurrent re-entrant startup races
    if _IS_STARTING:
        return
    _IS_STARTING = True
    try:
        # Check active tracked process handle
        if _HUD_PROCESS is not None and _HUD_PROCESS.poll() is None:
            try:
                hud = control.nexus().comm.get_com("hud")
                hud.show_hud()
            except Exception:
                pass
            return

        # Check existing process via XML-RPC ping
        hud = control.nexus().comm.get_com("hud")
        try:
            hud.ping()
            hud.show_hud()
            return
        except Exception:
            pass

        try:
            pythonw = settings.SETTINGS["paths"]["PYTHONW"]
        except Exception:
            pythonw = sys.executable

        # Spawn via platform strategy kwargs and bind to OS lifecycle containment
        popen_kwargs = _PROCESS_STRATEGY.get_popen_kwargs()
        _HUD_PROCESS = subprocess.Popen([pythonw, hud_path], **popen_kwargs)
        _PROCESS_STRATEGY.bind_process(_HUD_PROCESS)
    finally:
        _IS_STARTING = False
```

### 2.2. Process Termination and Socket Sanitation (`stop_hud`)

In upstream Caster, there was no programmatic or voice-driven mechanism to stop the HUD process. Although `hud.py` implemented an `xmlrpc_kill` method (`QApplication.quit()`), upstream `hud_support.py` never exposed a `stop_hud()` function, and no voice commands existed to terminate the process.

#### Upstream Implementation:
```python
# Upstream Caster: castervoice/asynch/hud_support.py
# NON-EXISTENT. Upstream had no function to stop or kill the HUD process.
# Users had to right-click the taskbar icon or terminate pythonw.exe in Task Manager.
```

#### Current Resilient Implementation:
```python
# Current Caster: castervoice/asynch/hud_support.py
def _wait_for_port_release(port=8338, timeout=2.0):
    import socket
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                time.sleep(0.1)
        except (socket.error, ConnectionRefusedError, OSError):
            return True
    return False

def stop_hud():
    """Signals the external HUD process to gracefully shut down and ensures port release."""
    global _HUD_PROCESS
    hud = control.nexus().comm.get_com("hud")
    try:
        hud.kill()
    except Exception:
        pass
    if _HUD_PROCESS is not None:
        try:
            _HUD_PROCESS.wait(timeout=1.5)
        except Exception:
            _PROCESS_STRATEGY.terminate_process(_HUD_PROCESS)
        _HUD_PROCESS = None
    _wait_for_port_release(8338, timeout=1.0)
```

### 2.3. Window Display and Self-Healing Auto-Recovery (`show_hud`)

In upstream Caster, if the HUD window was closed or terminated, executing `show_hud()` caught the resulting socket error, printed an error message, and took no corrective action. The HUD remained inaccessible until the user restarted the entire speech recognition engine.

#### Upstream Implementation:
```python
# Upstream Caster: castervoice/asynch/hud_support.py
def show_hud():
    hud = control.nexus().comm.get_com("hud")
    try:
        hud.show_hud()
    except Exception as e:
        # Failure was fatal; printed error and aborted
        printer.out("Unable to show hud. Hud not available. \n{}".format(e))
```

#### Current Resilient Implementation:
```python
# Current Caster: castervoice/asynch/hud_support.py
def show_hud():
    hud = control.nexus().comm.get_com("hud")
    try:
        hud.show_hud()
    except Exception:
        # Self-healing: if the HUD is offline or unreachable, auto-spawn it
        try:
            start_hud()
        except Exception as e:
            printer.out("Unable to show hud. Hud not available. \n{}".format(e))
```

### 2.4. Clean Restart Coordination (`restart_hud`)

Upstream Caster had no restart capability. Re-initializing the HUD required restarting Dragon or Natlink.

#### Upstream Implementation:
```python
# Upstream Caster: castervoice/asynch/hud_support.py
# NON-EXISTENT in upstream Caster.
```

#### Current Resilient Implementation:
```python
# Current Caster: castervoice/asynch/hud_support.py
def restart_hud():
    """Gracefully terminates the HUD process and restarts it cleanly."""
    global _CURRENT_HUD_PATH
    path_to_restart = _CURRENT_HUD_PATH
    stop_hud()
    time.sleep(0.5)
    start_hud(path_to_restart)
```

### 2.5. Message Buffering and Thread Safety (`HudPrintMessageHandler`)

In upstream Caster, `HudPrintMessageHandler` dispatched messages synchronously on the active Dragonfly recognition thread. When socket latency or connection timeouts occurred, the speech recognition loop stuttered. Furthermore, once an unhandled exception occurred, `self.is_hud_active` was set to `False` and never recovered.

#### Upstream Implementation:
```python
# Upstream Caster: castervoice/asynch/hud_support.py
class HudPrintMessageHandler(printer.BaseMessageHandler):
    def __init__(self):
        super(HudPrintMessageHandler, self).__init__()
        self.hud = control.nexus().comm.get_com("hud")
        self.is_hud_active = False
        if get_current_engine().name != "text":
            # 10 blocking retries during startup
            for attempt in range(10):
                try:
                    self.hud.ping()
                    self.is_hud_active = True
                    break
                except Exception as e:
                    time.sleep(0.5)

    def handle_message(self, items):
        if self.is_hud_active is True:
            # Synchronous RPC on Dragonfly speech recognition thread
            # Caused noticeable speech recognition stutters on latency
            try:
                self.hud.send("\n".join([str(m) for m in items]))
            except Exception as e:
                self.is_hud_active = False
                printer.out("Hud not available. \n{}".format(e))
                raise("")
        else:
            raise("")
```

#### Current Resilient Implementation:
```python
# Current Caster: castervoice/asynch/hud_support.py
class HudPrintMessageHandler(printer.BaseMessageHandler):
    def __init__(self):
        super(HudPrintMessageHandler, self).__init__()
        try:
            self.hud = control.nexus().comm.get_com("hud")
        except Exception:
            self.hud = None
        # Thread-safe in-memory queue decouples speech recognition from networking
        self._queue = queue.Queue(maxsize=500)
        self._worker = threading.Thread(target=self._process_queue, name="HudPrintWorker")
        self._worker.daemon = True
        self._worker.start()

    def handle_message(self, items):
        text = "\n".join([str(m) for m in items])
        try:
            self._queue.put_nowait(text)
        except Exception:
            pass

    def _process_queue(self):
        while True:
            try:
                text = self._queue.get()
                try:
                    if self.hud is None:
                        self.hud = control.nexus().comm.get_com("hud")
                    if self.hud is not None:
                        self.hud.send(text)
                except Exception:
                    # Background retry sleep; never blocks Dragonfly recognition
                    time.sleep(1.0)
            except Exception:
                time.sleep(0.5)
```

---

## 3. Cross-Platform Process Strategy Pattern (`process_lifecycle.py`)

To eliminate operating-system-specific ctypes structs from `hud_support.py` and provide clean support for Windows, Linux, and macOS, process containment is abstracted through the **Strategy Pattern**:

```
                       +-----------------------------+
                       |     BaseProcessStrategy     |
                       |-----------------------------|
                       | + get_popen_kwargs()        |
                       | + bind_process(proc)        |
                       | + terminate_process(proc)   |
                       +-----------------------------+
                                      ^
                                      |
         +----------------------------+----------------------------+
         |                                                         |
+------------------------------+                         +----------------------------+
|    WindowsProcessStrategy    |                         |    LinuxProcessStrategy    |
|------------------------------|                         |----------------------------|
| Uses Win32 Job Object with   |                         | Uses PR_SET_PDEATHSIG      |
| KILL_ON_JOB_CLOSE via ctypes |                         | + setsid() process groups  |
+------------------------------+                         +----------------------------+
```

### Strategy Implementations by Operating System:
1. **Windows (`WindowsProcessStrategy`)**:
   - Creates an anonymous Win32 Job Object using `kernel32.CreateJobObjectW`.
   - Sets `LimitFlags = 0x2000` (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`).
   - Assigns the spawned process handle using `AssignProcessToJobObject`.
   - Result: If Caster exits normally or is terminated abruptly, the Windows kernel kills the HUD child process automatically.
2. **Linux (`LinuxProcessStrategy`)**:
   - Passes `preexec_fn` calling `libc.prctl(PR_SET_PDEATHSIG, signal.SIGTERM)` and `os.setsid()`.
   - Result: As soon as the parent Python process terminates, the Linux kernel automatically delivers `SIGTERM` to the child process.
   - For forced termination, it signals the entire process group via `os.killpg(os.getpgid(proc.pid), signal.SIGKILL)`.
3. **macOS (`DarwinProcessStrategy`)**:
   - Launches child processes with `start_new_session=True`.
   - Handles clean forced termination across process groups via `os.killpg()`.
4. **Generic Fallback (`BaseProcessStrategy`)**:
   - Employs standard `proc.kill()` for any unrecognized Unix variants.

---

## 4. Voice Command Surface (`caster_rule.py`)

Upstream Caster provided only five fixed commands. The user could not start, stop, or restart the HUD using voice. The current implementation adds full process controls with prefix and postfix flexibility:

| Voice Command Spec | Bound Function | Operational Behavior |
| :--- | :--- | :--- |
| `"(show caster hud \| caster show hud)"` | `show_hud` | Brings HUD window to foreground; auto-starts process if stopped. |
| `"(hide caster hud \| caster hide hud)"` | `hide_hud` | Minimizes HUD window to hidden state while keeping process alive. |
| `"(start caster hud \| launch caster hud \| caster (start \| launch) hud)"` | `start_hud` | Spawns HUD process if absent; unhides window if already running. |
| `"(stop caster hud \| kill caster hud \| close caster hud \| caster (stop \| kill \| close) hud)"` | `stop_hud` | Gracefully closes HUD process, releases socket, and kills on timeout. |
| `"(clear caster hud \| caster clear hud)"` | `clear_hud` | Clears all text entries from the HUD output log. |
| `"(caster (restart \| reset) hud \| caster hud (restart \| reset) \| (restart \| reset) caster hud)"` | `restart_hud` | Gracefully cycles HUD process teardown and respawn. |
| `"(show caster rules \| caster show rules)"` | `show_rules` | Serializes loaded Dragonfly grammars and displays rules tree window. |
| `"(hide caster rules \| caster hide rules)"` | `hide_rules` | Closes rules tree display frame. |

---

## 5. Architectural Decoupling from the Plugin System

The native HUD implementation has been decoupled from the generic plugin subsystem across three architectural boundaries:

1. **`PluginBase` Purity**:
   `castervoice/lib/plugin.py` defines only generic plugin lifecycle hooks (`initialize`, `start`, `stop`, `get_rules`) with default `version = "0.1.0"`. All references to `replaces_hud` have been removed from `PluginBase`.
2. **Dynamic Subclass Checking**:
   If an external plugin wishes to declare that it supersedes the standard HUD (such as `themed_hud`), the plugin author defines `replaces_hud = True` on their specific subclass. `PluginManager` checks this dynamically using `getattr(plugin, "replaces_hud", False)`. Standard plugins remain unaware of display subsystems.
3. **No Automatic Display Revival on Unload**:
   `PluginManager.unload_plugin(name)` terminates and pops the requested plugin without checking or altering HUD state. Disabling a custom HUD leaves the display closed. The standard HUD only starts if the user explicitly issues `start caster hud` or `show caster hud`.

---

## 6. Standalone Branch Preparation Manifest

To contribute these HUD process lifecycle enhancements back to upstream Caster in a clean, isolated git branch, only five files are modified. These changes have zero dependencies on the plugin architecture:

```
castervoice/
├── _caster.py                   # Clean atexit.register(hud_support.stop_hud)
├── asynch/
│   ├── hud.py                   # Upstream PyQt4/5 HUD window implementation (unmodified)
│   ├── hud_support.py           # Process start/stop/restart, recovery, and async queue
│   └── process_lifecycle.py     # Cross-platform strategy pattern (Win32, Linux, macOS)
└── rules/
    └── core/
        └── utility_rules/
            └── caster_rule.py   # HUD process control voice command specs
tests/
└── asynch/
    └── test_hud_lifecycle.py    # Unit tests for lifecycle, auto-recovery, and strategy selection
```

### Git Cherry-Pick and Isolation Instructions
When preparing the clean branch:
1. Branch directly from upstream `master`:
   ```pwsh
   git checkout master
   git checkout -b feature/native-hud-process-lifecycle
   ```
2. Apply changes only to `process_lifecycle.py`, `hud_support.py`, `caster_rule.py`, `_caster.py`, and `test_hud_lifecycle.py`.
3. Verify that no plugin imports (`plugin_manager`, `plugin_support`, `PluginBase`) exist in the staged diff:
   ```pwsh
   git diff master -- castervoice/asynch/hud_support.py castervoice/rules/core/utility_rules/caster_rule.py
   ```
4. Execute the test suite:
   ```pwsh
   py -3.10 -m pytest tests/asynch/test_hud_lifecycle.py
   ```
This produces an isolated pull request containing only process control, error recovery, and voice grammar enhancements for the core Caster display overlay.
