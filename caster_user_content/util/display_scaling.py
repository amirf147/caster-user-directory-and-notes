import ctypes
from ctypes import wintypes
from typing import Optional, Dict, Any, List


class LUID(ctypes.Structure):
    _fields_ = [
        ("LowPart", wintypes.DWORD),
        ("HighPart", wintypes.LONG),
    ]


class DISPLAYCONFIG_PATH_SOURCE_INFO(ctypes.Structure):
    _fields_ = [
        ("adapterId", LUID),
        ("id", wintypes.UINT),
        ("modeInfoIdx", wintypes.UINT),
        ("statusFlags", wintypes.UINT),
    ]


class DISPLAYCONFIG_PATH_TARGET_INFO(ctypes.Structure):
    _fields_ = [
        ("adapterId", LUID),
        ("id", wintypes.UINT),
        ("modeInfoIdx", wintypes.UINT),
        ("outputTechnology", wintypes.UINT),
        ("rotation", wintypes.UINT),
        ("scaling", wintypes.UINT),
        ("refreshRate_Numerator", wintypes.UINT),
        ("refreshRate_Denominator", wintypes.UINT),
        ("scanLineOrdering", wintypes.UINT),
        ("targetAvailable", wintypes.BOOL),
        ("statusFlags", wintypes.UINT),
    ]


class DISPLAYCONFIG_PATH_INFO(ctypes.Structure):
    _fields_ = [
        ("sourceInfo", DISPLAYCONFIG_PATH_SOURCE_INFO),
        ("targetInfo", DISPLAYCONFIG_PATH_TARGET_INFO),
        ("flags", wintypes.UINT),
    ]


class DISPLAYCONFIG_MODE_INFO(ctypes.Structure):
    _fields_ = [
        ("infoType", wintypes.UINT),
        ("id", wintypes.UINT),
        ("adapterId", LUID),
        ("dummy", ctypes.c_byte * 64),
    ]


class DISPLAYCONFIG_DEVICE_INFO_HEADER(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int),
        ("size", wintypes.UINT),
        ("adapterId", LUID),
        ("id", wintypes.UINT),
    ]


class DISPLAYCONFIG_SOURCE_DPI_SCALE_GET(ctypes.Structure):
    _fields_ = [
        ("header", DISPLAYCONFIG_DEVICE_INFO_HEADER),
        ("minScaleRel", ctypes.c_int32),
        ("curScaleRel", ctypes.c_int32),
        ("maxScaleRel", ctypes.c_int32),
    ]


class DISPLAYCONFIG_SOURCE_DPI_SCALE_SET(ctypes.Structure):
    _fields_ = [
        ("header", DISPLAYCONFIG_DEVICE_INFO_HEADER),
        ("scaleRel", ctypes.c_int32),
    ]


user32 = ctypes.windll.user32

QDC_ONLY_ACTIVE_PATHS = 0x00000002
DISPLAYCONFIG_DEVICE_INFO_GET_DPI_SCALE = -3
DISPLAYCONFIG_DEVICE_INFO_SET_DPI_SCALE = -4

DPI_VALS: List[int] = [100, 125, 150, 175, 200, 225, 250, 300, 350, 400, 450, 500]


def _get_active_display_paths() -> List[DISPLAYCONFIG_PATH_INFO]:
    num_path = wintypes.UINT()
    num_mode = wintypes.UINT()
    res = user32.GetDisplayConfigBufferSizes(QDC_ONLY_ACTIVE_PATHS, ctypes.byref(num_path), ctypes.byref(num_mode))
    if res != 0:
        return []
    paths = (DISPLAYCONFIG_PATH_INFO * num_path.value)()
    modes = (DISPLAYCONFIG_MODE_INFO * num_mode.value)()
    res = user32.QueryDisplayConfig(
        QDC_ONLY_ACTIVE_PATHS, ctypes.byref(num_path), paths, ctypes.byref(num_mode), modes, None
    )
    if res != 0:
        return []
    return list(paths)


def get_display_scaling_info(display_index: int = 0) -> Optional[Dict[str, Any]]:
    """
    Returns display scaling information for the display at the given index.
    """
    paths = _get_active_display_paths()
    if not paths or display_index >= len(paths):
        return None

    path = paths[display_index]
    get_packet = DISPLAYCONFIG_SOURCE_DPI_SCALE_GET()
    get_packet.header.type = DISPLAYCONFIG_DEVICE_INFO_GET_DPI_SCALE
    get_packet.header.size = ctypes.sizeof(DISPLAYCONFIG_SOURCE_DPI_SCALE_GET)
    get_packet.header.adapterId = path.sourceInfo.adapterId
    get_packet.header.id = path.sourceInfo.id

    res = user32.DisplayConfigGetDeviceInfo(ctypes.byref(get_packet.header))
    if res != 0:
        return None

    rec_idx = abs(get_packet.minScaleRel)
    cur_idx = rec_idx + get_packet.curScaleRel
    cur_pct = DPI_VALS[cur_idx] if 0 <= cur_idx < len(DPI_VALS) else None
    rec_pct = DPI_VALS[rec_idx] if 0 <= rec_idx < len(DPI_VALS) else None
    max_idx = rec_idx + get_packet.maxScaleRel
    supported_pcts = DPI_VALS[0 : max_idx + 1]

    return {
        "adapterId": path.sourceInfo.adapterId,
        "sourceId": path.sourceInfo.id,
        "minScaleRel": get_packet.minScaleRel,
        "curScaleRel": get_packet.curScaleRel,
        "maxScaleRel": get_packet.maxScaleRel,
        "rec_idx": rec_idx,
        "cur_idx": cur_idx,
        "cur_pct": cur_pct,
        "rec_pct": rec_pct,
        "supported_pcts": supported_pcts,
    }


def set_display_scale(scale_percent: int = 100, display_index: int = 0) -> bool:
    """
    Sets the display scaling percentage (e.g. 100, 125, 150, 175, 200) for the display.
    """
    paths = _get_active_display_paths()
    if not paths or display_index >= len(paths):
        return False

    path = paths[display_index]
    info = get_display_scaling_info(display_index)
    if not info:
        return False

    scale_percent = int(scale_percent)
    rec_idx = info["rec_idx"]
    if scale_percent not in DPI_VALS:
        return False

    target_idx = DPI_VALS.index(scale_percent)
    target_rel = target_idx - rec_idx

    if target_rel < info["minScaleRel"] or target_rel > info["maxScaleRel"]:
        return False

    set_packet = DISPLAYCONFIG_SOURCE_DPI_SCALE_SET()
    set_packet.header.type = DISPLAYCONFIG_DEVICE_INFO_SET_DPI_SCALE
    set_packet.header.size = ctypes.sizeof(DISPLAYCONFIG_SOURCE_DPI_SCALE_SET)
    set_packet.header.adapterId = path.sourceInfo.adapterId
    set_packet.header.id = path.sourceInfo.id
    set_packet.scaleRel = target_rel

    res = user32.DisplayConfigSetDeviceInfo(ctypes.byref(set_packet.header))
    return res == 0


def step_display_scale(step: int = 1, display_index: int = 0) -> bool:
    """
    Steps the display scaling up (+1) or down (-1) by one index.
    """
    info = get_display_scaling_info(display_index)
    if not info or info["cur_idx"] is None:
        return False

    try:
        step_val = int(step)
    except (ValueError, TypeError):
        step_val = 1 if step in ("up", "larger") else -1

    new_idx = info["cur_idx"] + step_val
    if new_idx < 0 or new_idx >= len(DPI_VALS):
        return False

    target_pct = DPI_VALS[new_idx]
    return set_display_scale(scale_percent=target_pct, display_index=display_index)


def scale_up(display_index: int = 0) -> bool:
    """Steps display scaling up by one increment."""
    return step_display_scale(step=1, display_index=display_index)


def scale_down(display_index: int = 0) -> bool:
    """Steps display scaling down by one increment."""
    return step_display_scale(step=-1, display_index=display_index)


def scale_bed(display_index: int = 0) -> bool:
    """Sets display scaling to 175% (for viewing from bed)."""
    return set_display_scale(scale_percent=175, display_index=display_index)


def scale_default(display_index: int = 0) -> bool:
    """Sets display scaling to 100% (default day scale)."""
    return set_display_scale(scale_percent=100, display_index=display_index)
