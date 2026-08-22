"""
Test Mcp Standalone Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

import subprocess
import json
import time


def run_test():
    print("\n--- Testing Persistent Windows-MCP ---")
    print("Launching windows-mcp via uvx...")

    start_time = time.time()

    proc = subprocess.Popen(
        ["uvx", "windows-mcp", "serve"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

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

    # Send initialize
    proc.stdin.write(json.dumps(init_payload) + "\n")
    proc.stdin.flush()

    _init_resp = proc.stdout.readline()
    init_done_time = time.time()
    startup_latency = (init_done_time - start_time) * 1000
    print(f"Server Startup & Init Latency (Cold): {startup_latency:.2f}ms")

    # 2. Initialized notification
    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    proc.stdin.flush()

    # 3. Persistent Tool Calls
    titles = ["", "", ""]

    call_id = 2
    for cycle in range(1, 4):
        print(f"\n--- Cycle {cycle}/3 ---")
        for title in titles:
            tool_payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "App", "arguments": {"mode": "switch", "name": title}},
                "id": call_id,
            }
            call_id += 1

            req_start = time.time()
            proc.stdin.write(json.dumps(tool_payload) + "\n")
            proc.stdin.flush()

            response = proc.stdout.readline()
            req_end = time.time()

            latency = (req_end - req_start) * 1000
            print(f"Switching to: '{title[:40]}...' | Latency: {latency:.2f}ms | Response: {response.strip()[:100]}")

            time.sleep(5)

    proc.terminate()
    print("\n---------------------------\n")


if __name__ == "__main__":
    run_test()
