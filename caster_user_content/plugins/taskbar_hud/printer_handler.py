# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Amir Farhadi

"""
Taskbar HUD Message Handler for Caster's printer pipeline.

Intercepts formatted command recognition from castervoice.lib.printer
and pushes recognition telemetry to TaskbarHudBridgeClient.
"""

import logging
from castervoice.lib import printer

_logger = logging.getLogger("caster.plugins.taskbar_hud.printer_handler")

_MIC_COMMAND_FILTER = {"caster sleep", "caster on", "caster off", "sleep", "wake up", "stop listening"}


class TaskbarHudPrintHandler(printer.BaseMessageHandler):
    """
    Message handler dispatching recognized commands to Taskbar HUD.
    """

    def __init__(self, bridge=None):
        super(TaskbarHudPrintHandler, self).__init__()
        self._bridge = bridge

    def set_bridge(self, bridge):
        self._bridge = bridge

    def handle_message(self, items):
        if not self._bridge:
            try:
                from .bridge import get_taskbar_hud_bridge
            except ImportError:
                from caster_user_content.plugins.taskbar_hud.bridge import get_taskbar_hud_bridge
            self._bridge = get_taskbar_hud_bridge()

        if not self._bridge:
            return

        for item in items:
            raw = str(item).strip()
            if not raw:
                continue

            # 1. Command recognition ($)
            if raw.startswith("$"):
                cmd = raw[1:].strip()
                cmd_low = cmd.lower()

                if cmd_low in _MIC_COMMAND_FILTER:
                    continue

                current_mic = "on"
                try:
                    from castervoice.lib import control

                    nexus = control.nexus()
                    if nexus and nexus.engine_modes_manager:
                        current_mic = nexus.engine_modes_manager.get_mic_mode() or "on"
                except Exception:
                    pass

                if current_mic in ("sleeping", "off"):
                    continue

                self._bridge.send_update(command=cmd, status="recognized")

            # 2. System / Status messages (@)
            elif raw.startswith("@"):
                sys_msg = raw[1:].strip()
                sys_low = sys_msg.lower()
                if "sleeping" in sys_low:
                    self._bridge.send_update(command="Sleeping", status="sleeping", mic_state="sleeping")
                elif "ready" in sys_low or "microphone is on" in sys_low:
                    self._bridge.send_update(command="Ready", status="idle", mic_state="on")
                else:
                    self._bridge.send_update(command=sys_msg, status="idle")

            # 3. Error / rejection messages (#)
            elif raw.startswith("#"):
                err_msg = raw[1:].strip()
                if "reject" in err_msg.lower() or "unrec" in err_msg.lower():
                    self._bridge.send_update(command="[?]", status="error")
