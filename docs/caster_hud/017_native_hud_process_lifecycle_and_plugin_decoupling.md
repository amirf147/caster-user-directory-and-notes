[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](005_caster_hud_requirements_and_specifications.md) › **017: Native HUD Process Lifecycle & Plugin Decoupling**

---

> [!NOTE]
> **Document Status**: *Active Production Architecture & Canonical Reference (NOT SUPERSEDED)*.  
> Details the runtime architecture of the native Caster Heads-Up Display (HUD), comparing its legacy behavior with the current decoupled implementation using side-by-side code blocks, and specifying the boundaries required for a clean upstream branch.

# 017: Native HUD Process Lifecycle Management and Plugin Decoupling

This document specifies the architecture, runtime lifecycle, and inter-process communication (IPC) mechanics of Caster's traditional Heads-Up Display (`castervoice/asynch/hud.py`). It clarifies how the core HUD operates independently of the plugin system, contrasts its current capabilities with legacy upstream Caster through side-by-side code comparisons, and outlines the exact file boundaries needed to extract these enhancements into a standalone git branch.

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

        # Spawn and retain process handle; bind to Windows Job Object
        _HUD_PROCESS = subprocess.Popen([pythonw, hud_path])
        _bind_process_to_job(_HUD_PROCESS)
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
            try:
                _HUD_PROCESS.kill()
            except Exception:
                pass
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

### 2.6. Kernel Process Containment (Windows Job Object)

In upstream Caster, the HUD ran as an unconstrained child process. If the parent Python process exited abnormally or was terminated via task management, the HUD window frequently stayed open as an orphaned process holding port 8338.

#### Upstream Implementation:
```python
# Upstream Caster: castervoice/asynch/hud_support.py
# NO OS Job Object binding existed. Process cleanup relied on cooperative shutdown.
```

#### Current Resilient Implementation:
```python
# Current Caster: castervoice/asynch/hud_support.py
def _get_or_create_hud_job():
    global _HUD_JOB_OBJECT
    if sys.platform != "win32":
        return None
    if _HUD_JOB_OBJECT is not None:
        return _HUD_JOB_OBJECT
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        job = kernel32.CreateJobObjectW(None, None)
        # Configure JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE (0x2000)
        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = 0x2000
        kernel32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info))
        _HUD_JOB_OBJECT = job
        return _HUD_JOB_OBJECT
    except Exception:
        return None

def _bind_process_to_job(proc):
    if sys.platform != "win32" or proc is None:
        return
    try:
        job = _get_or_create_hud_job()
        if job and hasattr(proc, "_handle") and proc._handle:
            import ctypes
            ctypes.windll.kernel32.AssignProcessToJobObject(job, int(proc._handle))
    except Exception:
        pass
```

### 2.7. Voice Command Surface (`caster_rule.py`)

Upstream Caster provided only five fixed commands. The user could not start, stop, or restart the HUD using voice.

#### Upstream Implementation:
```python
# Upstream Caster: castervoice/rules/core/utility_rules/caster_rule.py
class CasterRule(MappingRule):
    mapping = {
        "reboot caster":
            R(Function(utilities.reboot)),
        "update dragonfly":
            R(_DependencyUpdate([_PIP, "install", "--upgrade", "dragonfly2"])),
        "enable (c c r|ccr)":
            R(Function(lambda: control.nexus().set_ccr_active(True))),
        "disable (c c r|ccr)":
            R(Function(lambda: control.nexus().set_ccr_active(False))),

        # Upstream had only these 5 commands; no start/stop/restart
        "show caster hud":
            R(Function(show_hud), rdescript="Show the HUD window"),
        "hide caster hud":
            R(Function(hide_hud), rdescript="Hide the HUD window"),
        "show caster rules":
            R(Function(show_rules), rdescript="Open HUD frame with the list of active rules"),
        "hide caster rules":
            R(Function(hide_rules), rdescript="Hide the list of active rules"),
        "clear caster hud":
            R(Function(clear_hud), rdescript="Clear output the HUD window"),
    }
```

#### Current Resilient Implementation:
```python
# Current Caster: castervoice/rules/core/utility_rules/caster_rule.py
class CasterRule(MappingRule):
    mapping = {
        "reboot caster":
            R(Function(utilities.reboot)),
        "update dragonfly":
            R(_DependencyUpdate([_PIP, "install", "--upgrade", "dragonfly2"])),
        "enable (c c r|ccr)":
            R(Function(lambda: control.nexus().set_ccr_active(True))),
        "disable (c c r|ccr)":
            R(Function(lambda: control.nexus().set_ccr_active(False))),

        # Full process lifecycle support with bidirectional grammar syntax
        "(show caster hud | caster show hud)":
            R(Function(show_hud), rdescript="Show the HUD window"),
        "(hide caster hud | caster hide hud)":
            R(Function(hide_hud), rdescript="Hide the HUD window"),
        "(start caster hud | launch caster hud | caster (start | launch) hud)":
            R(Function(start_hud), rdescript="Start the HUD process"),
        "(stop caster hud | kill caster hud | close caster hud | caster (stop | kill | close) hud)":
            R(Function(stop_hud), rdescript="Stop and close the HUD process"),
        "(clear caster hud | caster clear hud)":
            R(Function(clear_hud), rdescript="Clear output the HUD window"),
        "(caster (restart | reset) hud | caster hud (restart | reset) | (restart | reset) caster hud)":
            R(Function(restart_hud), rdescript="Restart the HUD process cleanly"),
        "(show caster rules | caster show rules)":
            R(Function(show_rules), rdescript="Open HUD frame with the list of active rules"),
        "(hide caster rules | caster hide rules)":
            R(Function(hide_rules), rdescript="Hide the list of active rules"),
    }
```

---

## 3. High-Level Architecture Comparison Matrix

| Architectural Feature | Upstream Legacy Baseline | Current Resilient Implementation |
| :--- | :--- | :--- |
| **Communication Protocol** | XML-RPC (`127.0.0.1:8338`). | XML-RPC (`127.0.0.1:8338`). |
| **Subprocess Handle Tracking** | Discarded on spawn (`_HUD_PROCESS = None`). | Retained in module-level `_HUD_PROCESS`. |
| **Windows Job Object Binding** | None; risk of orphaned background processes. | Configured with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`. |
| **Failure Recovery on Show** | Fatal exception; printed error and aborted. | Self-healing; automatically calls `start_hud()`. |
| **Process Termination API** | None; manual window close only. | `stop_hud()` with XML-RPC signal and SIGKILL fallback. |
| **Process Restart API** | None; required restarting speech engine. | `restart_hud()` with port release verification. |
| **Logging Dispatch Queue** | Synchronous RPC; blocked Dragonfly recognition loop. | Asynchronous `queue.Queue` with background daemon worker. |
| **Voice Commands Available** | 5 commands (show, hide, clear, show/hide rules). | 8 command families (adds start, stop, kill, restart). |
| **Plugin Subsystem Coupling** | N/A (no plugin architecture existed). | Completely decoupled; zero HUD attributes in `PluginBase`. |

---

## 4. Architectural Decoupling from the Plugin System

The native HUD implementation has been decoupled from the generic plugin subsystem across three architectural boundaries:

1. **`PluginBase` Purity**:
   `castervoice/lib/plugin.py` defines only generic plugin lifecycle hooks:
   ```python
   class PluginBase(object):
       name = "base_plugin"
       version = "0.1.0"
       description = "Base Caster Plugin"

       def initialize(self, nexus, config): ...
       def start(self): ...
       def stop(self): ...
       def get_rules(self): ...
   ```
   All references to `replaces_hud` have been removed from `PluginBase`.
2. **Dynamic Subclass Checking**:
   If an external plugin wishes to declare that it supersedes the standard HUD (such as `themed_hud`), the plugin author defines `replaces_hud = True` on their specific subclass. `PluginManager` checks this dynamically using `getattr(plugin, "replaces_hud", False)`. Standard plugins remain unaware of display subsystems.
3. **No Automatic Display Revival on Unload**:
   `PluginManager.unload_plugin(name)` terminates and pops the requested plugin without checking or altering HUD state. Disabling a custom HUD leaves the display closed. The standard HUD only starts if the user explicitly issues `start caster hud` or `show caster hud`.

---

## 5. Standalone Branch Preparation Manifest

To contribute these HUD process lifecycle enhancements back to upstream Caster in a clean, isolated git branch, only four files are modified. These changes have zero dependencies on the plugin architecture:

```
castervoice/
├── asynch/
│   ├── hud.py                   # Upstream PyQt4/5 HUD window implementation
│   └── hud_support.py           # Process start/stop/restart, recovery, and job binding
└── rules/
    └── core/
        └── utility_rules/
            └── caster_rule.py   # HUD process control voice command specs
tests/
└── asynch/
    └── test_hud_lifecycle.py    # Unit tests for start, stop, kill, and auto-recovery
```

### Git Cherry-Pick and Isolation Instructions
When preparing the clean branch:
1. Branch directly from upstream `master`:
   ```pwsh
   git checkout master
   git checkout -b feature/native-hud-process-lifecycle
   ```
2. Apply changes only to `hud_support.py`, `caster_rule.py`, and `test_hud_lifecycle.py`.
3. Verify that no plugin imports (`plugin_manager`, `plugin_support`, `PluginBase`) exist in the staged diff:
   ```pwsh
   git diff master -- castervoice/asynch/hud_support.py castervoice/rules/core/utility_rules/caster_rule.py
   ```
4. Execute the test suite:
   ```pwsh
   py -3.10 -m pytest tests/asynch/test_hud_lifecycle.py
   ```
This produces an isolated pull request containing only process control, error recovery, and voice grammar enhancements for the core Caster display overlay.
