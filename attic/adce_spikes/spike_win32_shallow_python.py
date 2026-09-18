#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024-2026 Amir Farhadi
"""
Micro-Spike 2: Pure Top-Level Win32 HWND + UIA Focus Shallow Extraction (Python 3.10)
Measures raw latency of shallow desktop context extraction with zero recursive DOM traversal.
Directly compares pure Win32, shallow UIA binding, and focused element extraction.
Part of Gate 3 (Empirical Micro-Spikes) in 015 Epistemic Gating Protocol.
"""

import ctypes
from ctypes import wintypes
import statistics
import sys
import time
import uiautomation as auto

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
ole32 = ctypes.windll.ole32

WINSTA_ALL_ACCESS = 0x37F
DESKTOP_ALL_ACCESS = 0x1FF
GA_ROOT = 2

EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


def attach_to_desktop():
    """Attach calling process/thread to interactive window station and desktop."""
    h_desktop = None
    try:
        h_winsta = user32.OpenWindowStationW("WinSta0", False, WINSTA_ALL_ACCESS)
        if h_winsta:
            user32.SetProcessWindowStation(h_winsta)
        h_desktop = user32.OpenDesktopW("Default", 0, False, DESKTOP_ALL_ACCESS)
        if h_desktop:
            user32.SetThreadDesktop(h_desktop)
    except Exception:
        pass
    return h_desktop


def enumerate_target_windows(h_desktop):
    """Discover active Waterfox, Antigravity IDE, Edge windows via EnumDesktopWindows."""
    targets = []

    def enum_cb(hwnd, lparam):
        buf_title = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buf_title, 512)
        title = buf_title.value

        buf_class = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buf_class, 256)
        class_name = buf_class.value

        if not title or title in ("Default IME", "MSCTFIME UI"):
            return True

        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        if class_name in ("MozillaWindowClass", "Chrome_WidgetWin_1"):
            targets.append(
                {
                    "hwnd": hwnd,
                    "hwnd_hex": f"0x{hwnd:08X}",
                    "pid": pid.value,
                    "class_name": class_name,
                    "title": title,
                }
            )
        return True

    cb = EnumWindowsProc(enum_cb)
    user32.EnumDesktopWindows(h_desktop or 0, cb, 0)
    return targets


def benchmark_pure_win32_envelope(iterations=100):
    """Benchmark pure Win32 C-API calls via ctypes."""
    times = []
    sample = None
    for _ in range(iterations):
        t0 = time.perf_counter_ns()
        hwnd = user32.GetForegroundWindow() or 0
        buf_title = ctypes.create_unicode_buffer(512)
        buf_class = ctypes.create_unicode_buffer(256)
        pid = wintypes.DWORD()
        rect = RECT()

        if hwnd:
            user32.GetWindowTextW(hwnd, buf_title, 512)
            user32.GetClassNameW(hwnd, buf_class, 256)
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            user32.GetWindowRect(hwnd, ctypes.byref(rect))

        t1 = time.perf_counter_ns()
        times.append((t1 - t0) / 1000.0)
        if not sample:
            sample = {
                "hwnd": f"0x{hwnd:08X}" if hwnd else "0x00000000",
                "pid": pid.value,
                "class_name": buf_class.value,
                "title": buf_title.value,
                "rect": (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top),
            }
    return sample, times


def benchmark_shallow_uia_binding(targets, iterations_per_target=20):
    """Benchmark binding AutomationElement from HWND in Python (zero traversal)."""
    results = []
    for t in targets:
        bind_times = []
        bound_ctrl = None
        for _ in range(iterations_per_target):
            t0 = time.perf_counter_ns()
            ctrl = auto.ControlFromHandle(t["hwnd"])
            _ = ctrl.Name if ctrl else ""
            t1 = time.perf_counter_ns()
            bind_times.append((t1 - t0) / 1000.0)
            if not bound_ctrl:
                bound_ctrl = ctrl

        results.append(
            {
                "target": t,
                "times_us": bind_times,
                "min_ms": min(bind_times) / 1000.0,
                "median_ms": statistics.median(bind_times) / 1000.0,
                "mean_ms": statistics.mean(bind_times) / 1000.0,
                "max_ms": max(bind_times) / 1000.0,
            }
        )
    return results


def benchmark_shallow_focus_element(iterations=100):
    """Benchmark UIA GetFocusedControl() property reading (zero traversal)."""
    times = []
    sample = None
    for _ in range(iterations):
        t0 = time.perf_counter_ns()
        focused = auto.GetFocusedControl()
        f_data = None
        if focused:
            try:
                c_type = focused.ControlTypeName or "UnknownControl"
                name = focused.Name or ""
                auto_id = focused.AutomationId or ""
                bbox = focused.BoundingRectangle
                b_tuple = (bbox.left, bbox.top, bbox.width(), bbox.height()) if bbox else None
                f_data = {
                    "control_type": c_type,
                    "name": name if len(name) <= 50 else name[:47] + "...",
                    "automation_id": auto_id,
                    "bounding_box": b_tuple,
                }
            except Exception:
                pass
        t1 = time.perf_counter_ns()
        times.append((t1 - t0) / 1000.0)
        if not sample:
            sample = f_data
    return sample, times


def compute_stats(arr_us):
    return {
        "min_us": min(arr_us),
        "median_us": statistics.median(arr_us),
        "mean_us": statistics.mean(arr_us),
        "p95_us": sorted(arr_us)[int(len(arr_us) * 0.95)],
        "max_us": max(arr_us),
        "min_ms": min(arr_us) / 1000.0,
        "median_ms": statistics.median(arr_us) / 1000.0,
        "mean_ms": statistics.mean(arr_us) / 1000.0,
        "p95_ms": sorted(arr_us)[int(len(arr_us) * 0.95)] / 1000.0,
        "max_ms": max(arr_us) / 1000.0,
    }


def main():
    print("=" * 82)
    print("  ADCE Micro-Spike 2: Pure Win32 vs Shallow UIA Focus Telemetry (Python 3.10)     ")
    print("==================================================================================")
    print(f" Python Runtime : {sys.version.split()[0]} (64-bit)")
    print(f" Timestamp      : {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print("-" * 82)

    ole32.CoInitializeEx(None, 0x0)
    h_desktop = attach_to_desktop()

    # 1. Benchmark Pure Win32 Envelope
    sample_w, times_w = benchmark_pure_win32_envelope(100)
    st_w = compute_stats(times_w)

    # 2. Benchmark Shallow UIA Focus
    sample_f, times_f = benchmark_shallow_focus_element(100)
    st_f = compute_stats(times_f)

    # 3. Benchmark Target Window Binding
    targets = enumerate_target_windows(h_desktop)
    print(f"[WIN32] Discovered {len(targets)} candidate application window(s).")
    bind_results = benchmark_shallow_uia_binding(targets, iterations_per_target=20)

    ole32.CoUninitialize()

    # Telemetry Output
    print("\n" + "=" * 82)
    print("  SECTION 1: PURE WIN32 & SHALLOW FOCUS LATENCY SUMMARY (100 SAMPLES)")
    print("=" * 82)
    print(f"{'Strategy / Operation':<36} | {'Min':>8} | {'Median':>8} | {'Mean':>8} | {'P95':>8} | {'Max':>8}")
    print("-" * 78)
    print(
        f"{'1. Pure Win32 C-Calls (HWND/Title/Rect)':<36} | {st_w['min_us']:>6.1f}µs | {st_w['median_us']:>6.1f}µs | {st_w['mean_us']:>6.1f}µs | {st_w['p95_us']:>6.1f}µs | {st_w['max_us']:>6.1f}µs"
    )
    print(
        f"{'2. Shallow UIA FocusedControl (COM)':<36} | {st_f['min_ms']:>6.2f}ms | {st_f['median_ms']:>6.2f}ms | {st_f['mean_ms']:>6.2f}ms | {st_f['p95_ms']:>6.2f}ms | {st_f['max_ms']:>6.2f}ms"
    )
    tot_min = st_w["min_ms"] + st_f["min_ms"]
    tot_med = st_w["median_ms"] + st_f["median_ms"]
    tot_mean = st_w["mean_ms"] + st_f["mean_ms"]
    tot_p95 = st_w["p95_ms"] + st_f["p95_ms"]
    tot_max = st_w["max_ms"] + st_f["max_ms"]
    print(
        f"{'3. Total Combined Shallow Pipeline':<36} | {tot_min:>6.2f}ms | {tot_med:>6.2f}ms | {tot_mean:>6.2f}ms | {tot_p95:>6.2f}ms | {tot_max:>6.2f}ms"
    )

    print("\n" + "=" * 82)
    print("  SECTION 2: SHALLOW HWND BINDING LATENCY BY APPLICATION (20 SAMPLES EACH)")
    print("=" * 82)
    print(f"{'Target Window':<42} | {'Class':<18} | {'Median':>8} | {'Mean':>8} | {'Max':>8}")
    print("-" * 82)
    for r in bind_results:
        t = r["target"]
        title_str = t["title"] if len(t["title"]) <= 40 else t["title"][:37] + "..."
        print(
            f"{title_str:<42} | {t['class_name']:<18} | {r['median_ms']:>6.2f}ms | {r['mean_ms']:>6.2f}ms | {r['max_ms']:>6.2f}ms"
        )
    print("=" * 82)


if __name__ == "__main__":
    main()
