# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Amir Farhadi

"""
Taskbar HUD Plugin

Integrates Caster voice recognition and mic telemetry with the Windows 11
Taskbar HUD Windhawk mod via Named Pipe.
"""

import logging
from castervoice.lib import printer
from castervoice.lib.plugin import PluginBase
from .bridge import TaskbarHudBridgeClient
from .printer_handler import TaskbarHudPrintHandler

_logger = logging.getLogger("caster.plugins.taskbar_hud")


class TaskbarHudPlugin(PluginBase):
    name = "taskbar_hud"
    version = "1.0.0"
    description = "Windows 11 Taskbar HUD Windhawk Mod Bridge"

    def __init__(self):
        super(TaskbarHudPlugin, self).__init__()
        self._bridge = None
        self._print_handler = None

    def initialize(self, nexus, config):
        super(TaskbarHudPlugin, self).initialize(nexus, config)
        pipe_name = config.get("pipe_name", "CasterTaskbarHud")
        self._bridge = TaskbarHudBridgeClient.get_instance(pipe_name=pipe_name)

        # 1. Register delegating printer message handler
        self._print_handler = TaskbarHudPrintHandler(bridge=self._bridge)
        printer.get_delegating_handler().register_handler(self._print_handler)

        # 2. Register mic state observer on EngineModesManager
        if nexus and hasattr(nexus, "engine_modes_manager") and nexus.engine_modes_manager:
            nexus.engine_modes_manager.add_mic_listener(self._on_mic_mode_changed)

        # 3. Optionally attach to ADCE context listener if ADCE plugin is loaded
        try:
            from caster_user_content.plugins.adce import add_context_listener

            add_context_listener(self._on_adce_context_changed)
        except Exception:
            try:
                from castervoice.plugins.adce import add_context_listener

                add_context_listener(self._on_adce_context_changed)
            except Exception:
                pass

    def _on_mic_mode_changed(self, mode):
        """Dispatches mic state transitions to Taskbar HUD."""
        if not self._bridge:
            return
        status = "sleeping" if mode in ("sleeping", "off") else "idle"
        command = "Sleeping" if mode in ("sleeping", "off") else "Ready"
        self._bridge.send_update(
            mic_state=mode,
            status=status,
            command=command,
        )

    def _on_adce_context_changed(
        self, process_name="", window_title="", semantic_zone="", active_file="", is_connected=True
    ):
        """Forwards ADCE sub-window zone transitions to Taskbar HUD."""
        if not self._bridge:
            return
        zone = semantic_zone if (is_connected and semantic_zone) else "--"
        self._bridge.send_update(adce_zone=zone)

    def start(self):
        super(TaskbarHudPlugin, self).start()
        if self._bridge:
            self._bridge.start()

    def stop(self):
        super(TaskbarHudPlugin, self).stop()
        if self._bridge:
            self._bridge.stop()
        if self._nexus and hasattr(self._nexus, "engine_modes_manager") and self._nexus.engine_modes_manager:
            self._nexus.engine_modes_manager.remove_mic_listener(self._on_mic_mode_changed)


def get_plugin():
    return TaskbarHudPlugin()
