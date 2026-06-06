# Caster custom rule hosting an XML-RPC server for external hotkey toggle
# This file is loaded by Caster from your user directory and binds to port 8341.

import sys
import threading
from xmlrpc.server import SimpleXMLRPCServer
from dragonfly import MappingRule, get_current_engine
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib import control
from castervoice.lib import printer

# Configuration
RPC_HOST = "127.0.0.1"
RPC_PORT = 8341

class XMLRPCServerThread(threading.Thread):
    def __init__(self, host, port, callback):
        super(XMLRPCServerThread, self).__init__()
        self.daemon = True
        self.host = host
        self.port = port
        self.callback = callback
        # logRequests=False keeps Caster console output clean from ping logs
        self.server = SimpleXMLRPCServer((self.host, self.port), logRequests=False, allow_none=True)
        self.server.register_function(self.callback, "toggle_mic_mode")

    def run(self):
        printer.out("Caster XML-RPC Server: Listening on http://{}:{}".format(self.host, self.port))
        try:
            self.server.serve_forever()
        except Exception as e:
            printer.out("Caster XML-RPC Server error: {}".format(e))

    def stop(self):
        printer.out("Caster XML-RPC Server: Shutting down...")
        self.server.shutdown()
        self.server.server_close()

def toggle_caster_mic():
    def callback():
        callback.timer.stop()
        nexus = control.nexus()
        if nexus is not None and nexus.engine_modes_manager is not None:
            manager = nexus.engine_modes_manager
            current_mode = manager.get_mic_mode()
            target_mode = "on" if current_mode == "sleeping" else "sleeping"
            printer.out("Caster Hotkey IPC: Toggling mic state to '{}'".format(target_mode))
            manager.set_mic_mode(target_mode)
        else:
            printer.out("Caster Hotkey IPC: Caster Nexus or engine modes manager is not initialized.")

    engine = get_current_engine()
    if engine is not None:
        callback.timer = engine.create_timer(callback, 0.05)
        return "Scheduled toggle"
    else:
        printer.out("Caster Hotkey IPC: Engine not ready")
        return "Engine not ready"

# Reload safety: cleanly shut down any existing server to release the port
if hasattr(sys, "_caster_hotkey_server"):
    try:
        printer.out("Caster Hotkey IPC: Stopping existing XML-RPC server...")
        sys._caster_hotkey_server.stop()
    except Exception as e:
        printer.out("Caster Hotkey IPC cleanup error: {}".format(e))
    finally:
        del sys._caster_hotkey_server

# Start the new XML-RPC server
try:
    server_thread = XMLRPCServerThread(RPC_HOST, RPC_PORT, toggle_caster_mic)
    server_thread.start()
    sys._caster_hotkey_server = server_thread
except Exception as e:
    printer.out("Caster Hotkey IPC: Failed to start XML-RPC server: {}".format(e))

# Dummy rule class to ensure Caster logs and loads this module
class CasterHotkeyToggleRule(MappingRule):
    mapping = {}
    extras = []
    defaults = {}

def get_rule():
    return CasterHotkeyToggleRule, RuleDetails(name="caster hotkey toggle ipc")
