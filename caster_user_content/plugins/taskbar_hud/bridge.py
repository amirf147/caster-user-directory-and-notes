# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Amir Farhadi

"""
Caster Taskbar HUD Named Pipe Bridge Client

Provides low-latency telemetry transmission from Caster and ADCE
to the Windows 11 Taskbar HUD Windhawk mod via Named Pipes with NDJSON framing.
"""

import ctypes
from ctypes import wintypes
import json
import logging
import queue
import threading
import time
from typing import Optional, List, Union

_logger = logging.getLogger("caster.plugins.taskbar_hud.bridge")

GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x80
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

_kernel32 = ctypes.windll.kernel32


class TaskbarHudBridgeClient(object):
    """
    Singleton client maintaining an asynchronous queue and background worker
    for pushing NDJSON telemetry frames to \\.\\pipe\\CasterTaskbarHud.
    """

    _instance = None
    _lock = threading.RLock()

    def __init__(self, pipe_name: str = "CasterTaskbarHud"):
        self._pipe_path = "\\\\.\\pipe\\{}".format(pipe_name)
        self._queue = queue.Queue(maxsize=128)
        self._running = False
        self._worker_thread = None

        self._cached_zone = "--"
        self._cached_rules = "Global"
        self._cached_command = "Ready"
        self._cached_status = "idle"
        self._cached_mic_state = "on"

    @classmethod
    def get_instance(cls, pipe_name: str = "CasterTaskbarHud") -> "TaskbarHudBridgeClient":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = TaskbarHudBridgeClient(pipe_name=pipe_name)
        return cls._instance

    def start(self):
        """Starts background sender worker thread."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._worker_thread = threading.Thread(
                target=self._sender_loop, name="TaskbarHUD-NamedPipe-Worker", daemon=True
            )
            self._worker_thread.start()

    def stop(self):
        """Stops background sender thread."""
        self._running = False

    def send_update(
        self,
        command: Optional[str] = None,
        rules: Optional[Union[str, List[str]]] = None,
        adce_zone: Optional[str] = None,
        status: Optional[str] = None,
        mic_state: Optional[str] = None,
    ):
        """
        Non-blocking enqueue of state update.
        Preserves all state transitions without destructive overwriting.
        """
        packet = {}

        if mic_state is not None:
            self._cached_mic_state = mic_state
            packet["mic_state"] = mic_state

        current_mic = self._cached_mic_state

        if command is not None:
            cmd_norm = command.strip().lower()
            if cmd_norm in ("caster sleep", "sleep", "sleeping", "go to sleep"):
                command = "Sleeping"
                current_mic = "sleeping"
                self._cached_mic_state = "sleeping"
                packet["mic_state"] = "sleeping"
                status = "sleeping"
            elif cmd_norm in ("caster on", "ready", "wake up"):
                current_mic = "on"
                self._cached_mic_state = "on"
                packet["mic_state"] = "on"
                status = "idle"
                command = "Ready"

            if current_mic in ("sleeping", "off"):
                command = "Sleeping"
                status = "sleeping"

            self._cached_command = command
            packet["command"] = command

        if rules is not None:
            self._cached_rules = rules if isinstance(rules, str) else ", ".join(rules)
            packet["rules"] = self._cached_rules

        if adce_zone is not None:
            self._cached_zone = adce_zone
            packet["adce_zone"] = adce_zone

        if status is not None:
            if current_mic in ("sleeping", "off") and status != "sleeping":
                status = "sleeping"
            self._cached_status = status
            packet["status"] = status

        packet["timestamp_ms"] = int(time.time() * 1000)

        try:
            self._queue.put_nowait(packet)
        except queue.Full:
            try:
                _ = self._queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self._queue.put_nowait(packet)
            except queue.Full:
                pass

    def send_command(self, command: str, status: str = "recognized"):
        self.send_update(command=command, status=status)

    def send_zone(self, zone: str):
        self.send_update(adce_zone=zone)

    def set_zone(self, zone: str):
        self.send_update(adce_zone=zone)

    def send_rules(self, rules: Union[str, List[str]]):
        self.send_update(rules=rules)

    def _sender_loop(self):
        """Background worker consuming queue and writing to Named Pipe with NDJSON framing."""
        handle = INVALID_HANDLE_VALUE

        while self._running:
            try:
                packet = self._queue.get(timeout=0.25)
            except queue.Empty:
                continue

            packets = [packet]
            while not self._queue.empty() and len(packets) < 16:
                try:
                    packets.append(self._queue.get_nowait())
                except queue.Empty:
                    break

            json_lines = "".join(json.dumps(p) + "\n" for p in packets)
            payload_bytes = json_lines.encode("utf-8")

            if handle == INVALID_HANDLE_VALUE or handle == 0 or handle is None:
                handle = _kernel32.CreateFileW(
                    self._pipe_path,
                    GENERIC_WRITE,
                    0,
                    None,
                    OPEN_EXISTING,
                    0,
                    None,
                )
                if handle == INVALID_HANDLE_VALUE or handle == 0:
                    handle = INVALID_HANDLE_VALUE
                    time.sleep(0.05)
                    continue

            written = wintypes.DWORD(0)
            ok = _kernel32.WriteFile(
                handle,
                payload_bytes,
                len(payload_bytes),
                ctypes.byref(written),
                None,
            )

            if not ok or written.value != len(payload_bytes):
                _kernel32.CloseHandle(handle)
                handle = INVALID_HANDLE_VALUE
                time.sleep(0.05)
            else:
                _kernel32.FlushFileBuffers(handle)

        if handle != INVALID_HANDLE_VALUE and handle != 0 and handle is not None:
            _kernel32.CloseHandle(handle)


def get_taskbar_hud_bridge() -> TaskbarHudBridgeClient:
    return TaskbarHudBridgeClient.get_instance()
