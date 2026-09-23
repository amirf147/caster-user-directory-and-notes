# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Amir Farhadi

"""
Next-Gen Modular/Themed HUD Plugin

Wraps the advanced, customizable Caster Heads-Up Display featuring QSS themes,
status bar, active rules tag bar, ADCE sub-window strip, opacity controls,
frameless drag mode, and IPC telemetry.
"""

import logging
from dragonfly import get_current_engine
from castervoice.lib import printer
from castervoice.lib.plugin import PluginBase
from castervoice.asynch import hud_support

_logger = logging.getLogger("caster.plugins.themed_hud")


class ThemedHudPlugin(PluginBase):
    name = "themed_hud"
    version = "2.0.0"
    description = "Modular, Customizable PyQt Heads-Up Display with QSS Themes and ADCE Context Strip"

    def __init__(self):
        super(ThemedHudPlugin, self).__init__()
        self._print_handler = None

    def initialize(self, nexus, config):
        super(ThemedHudPlugin, self).initialize(nexus, config)
        # Register print message handler with printer delegator
        self._print_handler = hud_support.HudPrintMessageHandler()
        printer.get_delegating_handler().register_handler(self._print_handler)
        _logger.info("Themed HUD print message handler registered.")

    def start(self):
        super(ThemedHudPlugin, self).start()
        engine = get_current_engine()
        engine_name = engine.name if engine else "text"
        if engine_name != "text":
            try:
                hud_support.start_hud()
                _logger.info("Themed HUD process started successfully.")
            except Exception as ex:
                printer.out("Themed HUD: Failed to start HUD process: {}".format(ex))
                _logger.exception("Themed HUD startup error:")

    def stop(self):
        super(ThemedHudPlugin, self).stop()
        try:
            from castervoice.asynch.hud.ipc.client import get_telemetry_publisher

            pub = get_telemetry_publisher()
            if pub:
                pub.close()
        except Exception:
            pass


def get_plugin():
    return ThemedHudPlugin()
