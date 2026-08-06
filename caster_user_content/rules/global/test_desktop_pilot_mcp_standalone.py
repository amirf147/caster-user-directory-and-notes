import subprocess
import json
import time
import re

try:
    from dragonfly import MappingRule, Function
    from castervoice.lib.ctrl.mgr.rule_details import RuleDetails

    HAS_DRAGONFLY = True
except ImportError:
    HAS_DRAGONFLY = False


def send_rpc_request(proc, req_id, method, params=None):
    payload = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        payload["params"] = params

    proc.stdin.write(json.dumps(payload) + "\n")
    proc.stdin.flush()

    line = proc.stdout.readline()
    if not line:
        return None
    return json.loads(line)


def parse_desktop_windows(output_text):
    pattern = re.compile(r'^\s*"(?P<title>.+?)"\s*\|\s*PID=(?P<pid>\d+)', re.MULTILINE)
    windows = []
    for match in pattern.finditer(output_text):
        windows.append({"title": match.group("title"), "pid": int(match.group("pid"))})
    return windows


def find_window_by_keyword(windows, keyword):
    for win in windows:
        if keyword.lower() in win["title"].lower():
            return win
    return None


def run_test():
    print("\n--- Testing Desktop Pilot MCP (winapp-mcp) Window & Tab Switching ---")
    print("Launching winapp-mcp via dotnet...")

    start_time = time.time()

    import os

    # 1. Spawn server process directly using compiled WinAppMCP.exe
    user_home = os.path.expanduser("~")
    exe_path = os.path.join(
        user_home,
        "Documents",
        "repos",
        "desktop-pilot-mcp",
        "src",
        "bin",
        "Debug",
        "net10.0-windows10.0.19041.0",
        "win-x64",
        "WinAppMCP.exe",
    )
    proc = subprocess.Popen(
        [exe_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8"
    )

    try:
        # 1. MCP initialize handshake
        _init_resp = send_rpc_request(
            proc,
            1,
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "caster-test-client", "version": "1.0.0"},
            },
        )
        init_done_time = time.time()
        print(f"Server Startup & Init Latency: {(init_done_time - start_time) * 1000:.2f}ms")

        # 2. Initialized notification
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()

        req_id = 2

        # 3. Query all visible desktop windows
        print("\nStep 1: Querying desktop windows via list_desktop_windows...")
        req_id += 1
        list_resp = send_rpc_request(proc, req_id, "tools/call", {"name": "list_desktop_windows", "arguments": {}})

        windows_text = ""
        if list_resp and "result" in list_resp and "content" in list_resp["result"]:
            for item in list_resp["result"]["content"]:
                if item.get("type") == "text":
                    windows_text += item.get("text", "")

        windows = parse_desktop_windows(windows_text)
        print(f"RAW WINDOWS TEXT:\n{windows_text[:500]}\n--- END RAW WINDOWS TEXT ---")
        print(f"Discovered {len(windows)} desktop windows:")
        for win in windows[:10]:  # Print first 10 for brevity
            print(f"  - [{win['pid']}] {win['title']}")

        # Targets to test
        targets = ["LibreOffice", "Waterfox"]

        for target_kw in targets:
            target_win = find_window_by_keyword(windows, target_kw)
            if not target_win:
                print(f"\n[SKIP] No window matching '{target_kw}' found.")
                continue

            print(f"\n--- Target Found: '{target_win['title']}' (PID: {target_win['pid']}) ---")

            # Step A: Attach to Process
            req_id += 1
            req_start = time.time()
            _attach_resp = send_rpc_request(
                proc, req_id, "tools/call", {"name": "attach_to_pid", "arguments": {"pid": target_win["pid"]}}
            )
            attach_latency = (time.time() - req_start) * 1000
            print(f"attach_to_pid latency: {attach_latency:.2f}ms")

            app_id = f"app_{target_win['pid']}"

            # Step B: Restore Window to Foreground
            req_id += 1
            req_start = time.time()
            restore_resp = send_rpc_request(
                proc, req_id, "tools/call", {"name": "restore_window", "arguments": {"appId": app_id}}
            )
            restore_latency = (time.time() - req_start) * 1000

            resp_text = ""
            if restore_resp and "result" in restore_resp and "content" in restore_resp["result"]:
                resp_text = restore_resp["result"]["content"][0].get("text", "")
            print(f"restore_window latency: {restore_latency:.2f}ms | Result: {resp_text.strip()}")

            time.sleep(2)  # Pause so user can see window come to front

            # Step C: If browser (Waterfox), test tab switching key combo
            if "waterfox" in target_kw.lower():
                print("Waterfox focused. Testing tab cycling via press_key_combo (Ctrl+Tab)...")
                for cycle in range(1, 4):
                    req_id += 1
                    req_start = time.time()
                    _combo_resp = send_rpc_request(
                        proc,
                        req_id,
                        "tools/call",
                        {"name": "press_key_combo", "arguments": {"keys": ["CONTROL", "TAB"]}},
                    )
                    combo_latency = (time.time() - req_start) * 1000
                    print(f"  Cycle {cycle}/3: Sent Ctrl+Tab | Latency: {combo_latency:.2f}ms")
                    time.sleep(1.5)  # Pause to observe tab switch visually

        print("\n--- Test Completed Successfully ---")

    except Exception as e:
        print(f"Error during execution: {e}")

    finally:
        print("Tearing down server process...")
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Teardown clean.")


if HAS_DRAGONFLY:

    class TestDesktopPilotMCPRule(MappingRule):
        pronunciation = "test desktop pilot"
        mapping = {
            "test desktop pilot": Function(run_test),
            "test pilot focus": Function(run_test),
        }

    def get_rule():
        return TestDesktopPilotMCPRule, RuleDetails(name="test desktop pilot rule", executable=None, title=None)


if __name__ == "__main__":
    run_test()
