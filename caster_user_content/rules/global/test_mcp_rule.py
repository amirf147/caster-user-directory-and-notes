from dragonfly import MappingRule, Function
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
import subprocess
import json
import time


def test_mcp_focus():
    start_time = time.time()
    print("\n--- Testing Windows-MCP ---")
    print("Launching windows-mcp via uvx...")

    # 1. MCP initialize handshake
    init_payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "CasterClient", "version": "1.0.0"},
        },
        "id": 1,
    }

    # 2. Initialized notification
    initialized_notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}

    # 3. Tool call payload
    tool_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": "App", "arguments": {"mode": "switch", "name": "waterfox"}},
        "id": 2,
    }

    try:
        # Launch MCP server with 'serve' subcommand
        proc = subprocess.Popen(
            ["uvx", "windows-mcp", "serve"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        launch_time = time.time()
        print(f"Startup latency: {(launch_time - start_time) * 1000:.2f}ms")

        # Send initialize
        proc.stdin.write(json.dumps(init_payload) + "\n")
        proc.stdin.flush()

        # Read init response
        init_resp = proc.stdout.readline()
        print(f"Init Response: {init_resp.strip()}")

        # Send initialized notification
        proc.stdin.write(json.dumps(initialized_notification) + "\n")
        proc.stdin.flush()

        # Send tool call
        print("Sending JSON-RPC request to switch to Waterfox...")
        proc.stdin.write(json.dumps(tool_payload) + "\n")
        proc.stdin.flush()

        # Read tool response
        response = proc.stdout.readline()

        end_time = time.time()

        if response:
            print(f"Response received: {response.strip()}")
        else:
            print("Failed to receive a valid JSON-RPC response.")

        print(f"Execution latency: {(end_time - launch_time) * 1000:.2f}ms")
        print(f"Total time (Startup + Exec): {(end_time - start_time) * 1000:.2f}ms")
        print("---------------------------\n")

        # Cleanup
        proc.terminate()

    except Exception as e:
        print(f"Error during MCP test: {e}")


class TestMCPRule(MappingRule):
    pronunciation = "test m c p"
    mapping = {
        "test m c p focus": Function(test_mcp_focus),
    }


def get_rule():
    return TestMCPRule, RuleDetails(name="test mcp rule", executable=None, title=None)
