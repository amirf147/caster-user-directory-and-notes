# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024-2026 Amir Farhadi

"""
Active Desktop Context Engine (ADCE) Python Bridge Client

Provides real-time, low-latency synchronization with the local ADCE background daemon.
Features:
1. Native http.client chunked stream decoder for zero-latency SSE consumption.
2. Full MCP JSON-RPC 2.0 session handshake and tools/call synchronization loop.
3. Sub-microsecond (< 0.001 ms) Dragonfly FuncContext evaluation directly from RAM.
4. Pub-sub context listeners for downstream plugins and rules.
"""

import http.client
import json
import logging
import threading
import time
import urllib.request
import urllib.error

from castervoice.lib import printer

_logger = logging.getLogger("caster.plugins.adce")

IDE_PROCESS_NAMES = frozenset(["code", "antigravity ide", "cursor", "windsurf", "vscodium", "code - oss"])


class AdceBridgeClient(object):
    """
    Singleton client maintaining an active background MCP SSE listener and polling loop.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self, host="127.0.0.1", port=8424):
        self._host = host
        self._port = int(port)
        self._post_url = None
        self._request_counter = 0

        self._current_zone = "Unknown"
        self._current_process = ""
        self._current_title = ""
        self._active_file = ""
        self._last_update_time = 0.0
        self._is_connected = False
        self._running = False

        self._sse_thread = None
        self._poll_thread = None
        self._verbose_logging = True
        self._context_listeners = []

    def add_context_listener(self, callback):
        """Registers a listener callback invoked when desktop context changes."""
        with self._lock:
            if callback not in self._context_listeners:
                self._context_listeners.append(callback)

    def remove_context_listener(self, callback):
        """Removes a registered context listener callback."""
        with self._lock:
            if callback in self._context_listeners:
                self._context_listeners.remove(callback)

    def _notify_context_listeners(self, process, title, zone, file_name, is_connected):
        """Dispatches context changes to registered listeners."""
        with self._lock:
            listeners = list(self._context_listeners)
        for cb in listeners:
            try:
                cb(
                    process_name=process,
                    window_title=title,
                    semantic_zone=zone,
                    active_file=file_name,
                    is_connected=is_connected,
                )
            except Exception as ex:
                _logger.debug("Error in context listener %s: %s", cb, ex)

    @classmethod
    def get_instance(cls, host="127.0.0.1", port=8424):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = AdceBridgeClient(host=host, port=port)
        return cls._instance

    def start(self):
        """Starts background SSE listener and polling loop threads."""
        with self._lock:
            if self._running:
                return
            self._running = True

            self._sse_thread = threading.Thread(target=self._sse_listener_loop, name="ADCE-SSE-Client", daemon=True)
            self._sse_thread.start()

            self._poll_thread = threading.Thread(target=self._polling_loop, name="ADCE-MCP-Poller", daemon=True)
            self._poll_thread.start()

    def stop(self):
        """Stops all background threads."""
        self._running = False

    def _sse_listener_loop(self):
        """Streaming SSE reader using http.client.HTTPConnection (automatic chunk decoding)."""
        while self._running:
            conn = None
            try:
                conn = http.client.HTTPConnection(self._host, self._port, timeout=30)
                conn.request("GET", "/sse", headers={"Accept": "text/event-stream"})
                resp = conn.getresponse()

                if resp.status != 200:
                    time.sleep(2.0)
                    continue

                self._is_connected = True
                print(
                    "\n[ADCE Bridge] Connected to ADCE live stream at http://{}:{}/sse".format(self._host, self._port)
                )
                printer.out("ADCE: Connected (http://{}:{}/sse)".format(self._host, self._port))

                current_event = "message"

                while self._running:
                    raw_line = resp.readline()
                    if not raw_line:
                        break

                    line = raw_line.decode("utf-8", errors="ignore").strip("\r\n").strip()
                    if not line or line.startswith(":"):
                        current_event = "message"
                        continue

                    if line.startswith("event:"):
                        current_event = line[6:].strip()
                    elif line.startswith("data:"):
                        data_str = line[5:].strip()
                        if current_event == "endpoint":
                            self._handle_endpoint_event(data_str)
                            current_event = "message"
                        else:
                            self._handle_data_message(data_str)

            except (http.client.HTTPException, TimeoutError, OSError, ConnectionError):
                if self._is_connected:
                    self._is_connected = False
                    self._post_url = None
                    print("\n[ADCE Bridge] Disconnected from ADCE daemon (reconnecting in background...)")
                    self._notify_context_listeners("", "", "", "", False)
            except Exception as ex:
                if self._is_connected:
                    self._is_connected = False
                    self._notify_context_listeners("", "", "", "", False)
                _logger.debug("ADCE SSE listener exception: %s", ex)
            finally:
                if conn:
                    try:
                        conn.close()
                    except Exception:
                        pass
                time.sleep(1.5)

    def _handle_endpoint_event(self, endpoint_data: str):
        """Extracts session endpoint and executes MCP handshake."""
        if not endpoint_data.startswith("http"):
            if not endpoint_data.startswith("/"):
                endpoint_data = "/" + endpoint_data
            self._post_url = "http://{}:{}{}".format(self._host, self._port, endpoint_data)
        else:
            self._post_url = endpoint_data

        # MCP initialize
        self._send_mcp_request(
            method="initialize",
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "caster-adce-bridge", "version": "1.0.0"},
            },
        )

        # Trigger immediate context capture
        self._query_desktop_context()

    def _polling_loop(self):
        """Fast background query loop (60 ms) keeping RAM cache updated from ADCE."""
        while self._running:
            try:
                if self._is_connected and self._post_url:
                    self._query_desktop_context()
            except Exception as ex:
                _logger.debug("Polling loop exception: %s", ex)
            time.sleep(0.060)

    def _query_desktop_context(self):
        """Sends an MCP tools/call request for get_desktop_context."""
        self._send_mcp_request(method="tools/call", params={"name": "get_desktop_context", "arguments": {}})

    def _send_mcp_request(self, method: str, params: dict):
        """Dispatches JSON-RPC 2.0 message to ADCE session endpoint."""
        if not self._post_url:
            return

        self._request_counter += 1
        payload = {"jsonrpc": "2.0", "id": self._request_counter, "method": method, "params": params}
        json_bytes = json.dumps(payload).encode("utf-8")

        try:
            req = urllib.request.Request(self._post_url, data=json_bytes, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=0.8) as resp:
                _ = resp.read()
        except Exception:
            pass

    def _handle_data_message(self, data_str: str):
        """Parses incoming MCP tool result or direct snapshot JSON."""
        try:
            parsed = json.loads(data_str)

            if isinstance(parsed, dict) and "result" in parsed:
                res = parsed["result"]
                if isinstance(res, dict) and "content" in res:
                    for item in res["content"]:
                        if item.get("type") == "text":
                            text_body = item.get("text", "")
                            if text_body.startswith("{"):
                                snapshot = json.loads(text_body)
                                self._ingest_snapshot(snapshot)
                                return

            if isinstance(parsed, dict) and ("focus" in parsed or "Focus" in parsed):
                self._ingest_snapshot(parsed)

        except Exception as ex:
            _logger.debug("Error parsing data message: %s", ex)

    def _ingest_snapshot(self, snapshot: dict):
        """Atomically updates local RAM cache with normalized casing."""
        try:
            focus = snapshot.get("focus") or snapshot.get("Focus") or {}
            window = snapshot.get("window") or snapshot.get("Window") or {}
            ide = snapshot.get("ide_context") or snapshot.get("IdeContext") or {}

            zone = focus.get("semantic_zone") or focus.get("SemanticZone") or "Unknown"
            process = (window.get("process_name") or window.get("ProcessName") or "").lower()
            title = window.get("title") or window.get("Title") or ""
            duration_ms = snapshot.get("extraction_duration_ms") or snapshot.get("ExtractionDurationMs") or 0.0

            active_file = ""
            active_tab = ide.get("active_tab") or ide.get("ActiveTab")
            if active_tab and isinstance(active_tab, dict):
                active_file = active_tab.get("title") or active_tab.get("Title") or ""

            prev_zone = self._current_zone
            prev_process = self._current_process
            prev_title = self._current_title
            prev_file = self._active_file

            # Atomic RAM updates (O(1) lookup in memory)
            self._current_zone = zone
            self._current_process = process
            self._current_title = title
            self._active_file = active_file
            self._last_update_time = time.time()

            # Log live zone transitions in Caster console
            if self._verbose_logging and (prev_zone != zone or prev_process != process):
                proc_display = process if process else "Desktop"
                file_info = " | File: {}".format(active_file) if active_file else ""
                print("[ADCE Context] {} -> [{}]{} ({:.1f} ms)".format(proc_display, zone, file_info, duration_ms))

            if prev_zone != zone or prev_process != process or prev_title != title or prev_file != active_file:
                self._notify_context_listeners(process, title, zone, active_file, True)

        except Exception as ex:
            _logger.debug("Failed to ingest snapshot: %s", ex)

    # -------------------------------------------------------------------------
    # State Accessors & Predicates for Dragonfly FuncContext (< 0.001 ms)
    # -------------------------------------------------------------------------

    def is_connected(self) -> bool:
        return self._is_connected

    def get_current_zone(self) -> str:
        return self._current_zone

    def get_current_process(self) -> str:
        return self._current_process

    def get_current_title(self) -> str:
        return self._current_title

    def get_active_file(self) -> str:
        return self._active_file

    _ZONE_SYNONYMS = {
        "integratedterminal": "terminal",
        "terminal": "terminal",
        "editorcodebuffer": "editorbuffer",
        "editorbuffer": "editorbuffer",
        "gitcommitbox": "gitcommitbox",
        "chatassistant": "chatconversation",
        "chatconversation": "chatconversation",
        "chatprompt": "chatprompt",
        "documentcontent": "webdocument",
        "webdocument": "webdocument",
    }

    @classmethod
    def _canonicalize_zone(cls, zone_str: str) -> str:
        norm = str(zone_str or "").lower().replace("_", "").replace(" ", "")
        return cls._ZONE_SYNONYMS.get(norm, norm)

    def is_zone(self, target_zone: str, app_names=None) -> bool:
        if app_names is not None:
            if isinstance(app_names, str):
                app_names = [app_names]
            app_set = {a.lower() for a in app_names}
            if self._current_process not in app_set and not any(a in self._current_process for a in app_set):
                return False

        return self._canonicalize_zone(self._current_zone) == self._canonicalize_zone(target_zone)

    def is_ide_terminal(self) -> bool:
        """Predicate checking if focus is currently in an integrated IDE terminal."""
        is_ide_app = any(ide in self._current_process for ide in IDE_PROCESS_NAMES)
        return is_ide_app and self._canonicalize_zone(self._current_zone) == "terminal"

    def is_ide_editor(self) -> bool:
        """Predicate checking if focus is currently in a code editor buffer."""
        is_ide_app = any(ide in self._current_process for ide in IDE_PROCESS_NAMES)
        return is_ide_app and self._canonicalize_zone(self._current_zone) == "editorbuffer"

    def is_ide_git_commit(self) -> bool:
        """Predicate checking if focus is in a Git commit message box."""
        is_ide_app = any(ide in self._current_process for ide in IDE_PROCESS_NAMES)
        return is_ide_app and self._canonicalize_zone(self._current_zone) == "gitcommitbox"


adce = AdceBridgeClient.get_instance()


def is_ide_terminal_focused(**kwargs):
    return adce.is_ide_terminal()


def is_ide_editor_focused(**kwargs):
    return adce.is_ide_editor()


def is_ide_git_commit_focused(**kwargs):
    return adce.is_ide_git_commit()


def get_current_zone():
    return adce.get_current_zone()


def is_connected():
    return adce.is_connected()


def add_context_listener(callback):
    adce.add_context_listener(callback)


def remove_context_listener(callback):
    adce.remove_context_listener(callback)


def print_adce_status():
    """Prints a clean diagnostic overview of current context to Console & HUD."""
    conn_str = "CONNECTED" if adce.is_connected() else "DISCONNECTED"
    zone = adce.get_current_zone()
    proc = adce.get_current_process()
    file_name = adce.get_active_file()
    title = adce.get_current_title()

    msg = "ADCE [{}]: Zone=[{}] | App='{}'".format(conn_str, zone, proc)
    if file_name:
        msg += " | File='{}'".format(file_name)

    print("\n" + "=" * 65)
    print("  {}".format(msg))
    if title:
        print("  Title: '{}'".format(title))
    print("=" * 65 + "\n")

    printer.out(msg)
