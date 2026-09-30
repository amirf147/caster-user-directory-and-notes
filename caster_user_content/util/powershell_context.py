# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024-2026 Amir Farhadi

"""
Unified PowerShell Context Resolver for Caster & Dragonfly

Provides multi-environment context evaluation for PowerShell voice rules,
supporting:
1. Native Standalone Windows PowerShell (powershell.exe)
2. Native Standalone PowerShell 7 (pwsh.exe)
3. Windows Terminal (WindowsTerminal.exe / wt.exe) hosting a PowerShell tab
4. Integrated Terminal inside IDEs (Antigravity IDE, VS Code, Cursor, Windsurf)
   specifically verifying that the focused terminal is running PowerShell.
"""

import ctypes
from ctypes import wintypes
import time
from typing import Optional

POWERSHELL_HOST_EXECUTABLES = [
    "powershell",
    "pwsh",
    "windowsterminal",
    "wt",
    "code",
    "antigravity",
    "antigravity ide",
    "cursor",
    "windsurf",
    "vscodium",
]

IDE_PROCESS_NAMES = frozenset(
    [
        "code",
        "antigravity",
        "antigravity ide",
        "cursor",
        "windsurf",
        "vscodium",
        "code - oss",
    ]
)

TERMINAL_HOST_NAMES = frozenset(
    [
        "windowsterminal",
        "wt",
        "conhost",
    ]
)


# Toolhelp32 process snapshot structure for child process inspection
class _PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260),
    ]


_CHILD_CACHE = {}  # {root_pid: (has_ps_descendant: bool, timestamp: float)}
_CACHE_TTL = 0.5  # 500 ms TTL for near-zero latency repeated recognition queries


def _get_window_pid(handle: Optional[int]) -> Optional[int]:
    """Retrieves the process ID associated with a Win32 window handle."""
    if not handle:
        return None
    try:
        pid = wintypes.DWORD()
        res = ctypes.windll.user32.GetWindowThreadProcessId(handle, ctypes.byref(pid))
        return pid.value if (res and pid.value > 0) else None
    except Exception:
        return None


def _has_powershell_descendant_process(root_pid: int) -> bool:
    """Checks whether the given root PID has any active pwsh.exe or powershell.exe descendant processes."""
    now = time.time()
    if root_pid in _CHILD_CACHE:
        cached_result, ts = _CHILD_CACHE[root_pid]
        if now - ts < _CACHE_TTL:
            return cached_result

    found = False
    try:
        # TH32CS_SNAPPROCESS = 0x00000002
        h_snap = ctypes.windll.kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
        if h_snap != -1:
            pe = _PROCESSENTRY32()
            pe.dwSize = ctypes.sizeof(_PROCESSENTRY32)
            children_map = {}
            exe_map = {}
            if ctypes.windll.kernel32.Process32First(h_snap, ctypes.byref(pe)):
                while True:
                    pid = pe.th32ProcessID
                    ppid = pe.th32ParentProcessID
                    exe = pe.szExeFile.decode("utf-8", errors="ignore").lower()
                    children_map.setdefault(ppid, []).append(pid)
                    exe_map[pid] = exe
                    if not ctypes.windll.kernel32.Process32Next(h_snap, ctypes.byref(pe)):
                        break
            ctypes.windll.kernel32.CloseHandle(h_snap)

            # Traverse descendants from root_pid
            queue = [root_pid]
            visited = set()
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                for child_pid in children_map.get(current, []):
                    child_exe = exe_map.get(child_pid, "")
                    if "pwsh" in child_exe or "powershell" in child_exe:
                        found = True
                        break
                    queue.append(child_pid)
                if found:
                    break
    except Exception:
        found = False

    _CHILD_CACHE[root_pid] = (found, now)
    return found


def is_ide_powershell_active(handle: Optional[int] = None) -> bool:
    """
    Checks if keyboard focus is in an integrated terminal running PowerShell.

    Strictly gates on ADCE's real-time semantic focus:
    - If ADCE is not connected, or if focus is not in the integrated terminal,
      immediately returns False to guarantee no false activations in editor buffers.
    - If in the integrated terminal, verifies that the shell is PowerShell (not Bash/CMD/WSL)
      via ADCE element telemetry and verified descendant process checks.
    """
    try:
        try:
            from adce import adce, is_ide_terminal_focused
        except ImportError:
            from caster_user_content.plugins.adce import adce, is_ide_terminal_focused

        if not adce.is_connected() or not is_ide_terminal_focused():
            return False

        # Active terminal shell or focused element inspection via ADCE
        shell = (adce.get_current_terminal_shell() or "").lower()
        if not shell:
            shell = (adce.get_current_context().get("terminal_shell") or "").lower()

        if shell:
            # Explicitly reject foreign shells
            if any(other in shell for other in ("bash", "cmd.exe", "wsl", "zsh", "node.exe")):
                return False
            if "pwsh" in shell or "powershell" in shell:
                return True

        # If focused terminal element title is ambiguous (e.g. running a CLI tool like 'dotnet' or 'git'),
        # verify that the IDE window actually owns an active pwsh/powershell descendant process
        pid = _get_window_pid(handle)
        if pid and _has_powershell_descendant_process(pid):
            return True

        return True
    except Exception:
        return False


def is_powershell_active(executable=None, title=None, handle=None, **kwargs):
    """
    Universal predicate for Dragonfly FuncContext.
    Returns True if current input focus is within any PowerShell environment.
    """
    exe_low = (executable or "").lower()

    # 1. Native Standalone Windows PowerShell (5.1) or PowerShell 7 (pwsh)
    if "powershell" in exe_low or "pwsh" in exe_low:
        return True

    # 2. Windows Terminal host (strictly gated via ADCE telemetry)
    if any(host in exe_low for host in TERMINAL_HOST_NAMES):
        try:
            try:
                from adce import adce
            except ImportError:
                from caster_user_content.plugins.adce import adce

            if adce.is_connected() and adce.is_zone("terminal"):
                shell = (adce.get_current_terminal_shell() or "").lower()
                if not shell:
                    shell = (adce.get_current_context().get("terminal_shell") or "").lower()
                if shell:
                    if any(other in shell for other in ("bash", "cmd.exe", "wsl", "zsh")):
                        return False
                    if "pwsh" in shell or "powershell" in shell:
                        return True
                pid = _get_window_pid(handle)
                if pid and _has_powershell_descendant_process(pid):
                    return True
        except Exception:
            pass
        return False

    # 3. Integrated IDE Terminal (Antigravity IDE, VS Code, Cursor, Windsurf)
    if any(ide in exe_low or exe_low in ide for ide in IDE_PROCESS_NAMES):
        return is_ide_powershell_active(handle=handle)

    return False
