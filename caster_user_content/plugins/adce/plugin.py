# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Amir Farhadi

"""
Active Desktop Context Engine (ADCE) Plugin

Integrates out-of-process semantic focus context stream into Caster.
"""

import logging
from castervoice.lib.plugin import PluginBase
from .client import AdceBridgeClient

_logger = logging.getLogger("caster.plugins.adce")


class AdcePlugin(PluginBase):
    name = "adce"
    version = "1.0.0"
    description = "Active Desktop Context Engine (ADCE) SSE Bridge"

    def __init__(self):
        super(AdcePlugin, self).__init__()
        self._client = None

    def initialize(self, nexus, config):
        super(AdcePlugin, self).initialize(nexus, config)
        host = config.get("host", "127.0.0.1")
        port = int(config.get("port", 8424))
        self._client = AdceBridgeClient.get_instance(host=host, port=port)

    def start(self):
        super(AdcePlugin, self).start()
        if self._client:
            self._client.start()

    def stop(self):
        super(AdcePlugin, self).stop()
        if self._client:
            self._client.stop()


def get_plugin():
    return AdcePlugin()
