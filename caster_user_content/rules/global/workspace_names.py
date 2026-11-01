"""
Workspace Names Navigation Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

from ctypes import windll
import re
import sys
import threading
from pathlib import Path

from dragonfly import DictList, DictListRef, Function, MappingRule, Window
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R
from castervoice.lib import printer

try:
    import winvda
except ImportError:
    winvda_repo = Path.home() / "Documents" / "repos" / "winvda"
    if winvda_repo.exists() and str(winvda_repo) not in sys.path:
        sys.path.insert(0, str(winvda_repo))
    import winvda

try:
    from caster_user_content.environment_variables import WORKSPACE_PRONUNCIATION_OVERRIDES
except ImportError:
    WORKSPACE_PRONUNCIATION_OVERRIDES = {}

ASFW_ANY = -1
DEFAULT_OVERRIDES = {
    "winvda": "win v d a",
}

workspace_dictlist = DictList("workspace_dictlist")


def _get_named_desktops_map():
    """Query winvda and construct a spoken-phrase-to-desktop-index mapping."""
    try:
        desktops = winvda.get_desktops()
    except Exception as e:
        printer.out(f"WorkspaceNames: Desktop enumeration failed: {e}")
        return {}

    mapping = {}
    overrides = dict(DEFAULT_OVERRIDES)
    if WORKSPACE_PRONUNCIATION_OVERRIDES:
        overrides.update(WORKSPACE_PRONUNCIATION_OVERRIDES)

    for d in desktops:
        raw_name = d.name.strip() if d.name else ""
        # Ignore unnamed or default Windows desktop names (e.g. "Desktop 1")
        if not raw_name or re.match(r"^desktop\s+\d+$", raw_name, re.IGNORECASE):
            continue

        spoken_forms = set()
        lower_name = raw_name.lower()

        # 1. Direct lowercased without punctuation
        cleaned = re.sub(r"[_\-]+", " ", lower_name)
        cleaned = re.sub(r"[^\w\s]", "", cleaned).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        if cleaned:
            spoken_forms.add(cleaned)

        # 2. PascalCase / camelCase splitting (e.g. "WinStasis" -> "win stasis")
        split_camel = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", raw_name).lower()
        split_camel = re.sub(r"[_\-]+", " ", split_camel)
        split_camel = re.sub(r"[^\w\s]", "", split_camel).strip()
        split_camel = re.sub(r"\s+", " ", split_camel)
        if split_camel:
            spoken_forms.add(split_camel)

        # 3. Custom pronunciation / acronym overrides
        for target_key, alias_val in overrides.items():
            if target_key.lower() in (lower_name, cleaned):
                alias_clean = re.sub(r"[_\-]+", " ", alias_val.lower())
                alias_clean = re.sub(r"[^\w\s]", "", alias_clean).strip()
                alias_clean = re.sub(r"\s+", " ", alias_clean)
                if alias_clean:
                    spoken_forms.add(alias_clean)

        for spoken in spoken_forms:
            mapping[spoken] = d.number

    return mapping


class WorkspaceSyncManager:
    """Manages periodic background and on-demand synchronization of named workspaces."""

    def __init__(self, dict_list, interval=5.0):
        self._dict_list = dict_list
        self._interval = interval
        self._stop_event = threading.Event()
        self._thread = None
        self._last_snapshot = None

    def sync(self, log=False):
        new_map = _get_named_desktops_map()
        if new_map != self._last_snapshot:
            self._dict_list.set(new_map)
            self._last_snapshot = new_map
            if log:
                printer.out(f"WorkspaceNames: Synced {len(new_map)} phrases: {list(new_map.keys())}")
        elif log:
            printer.out("WorkspaceNames: Already up to date.")

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="WorkspaceSyncDaemon",
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _run(self):
        while not self._stop_event.is_set():
            try:
                self.sync(log=False)
            except Exception:
                pass
            self._stop_event.wait(self._interval)


sync_manager = WorkspaceSyncManager(workspace_dictlist)
sync_manager.sync(log=False)
sync_manager.start()


def go_to_named_workspace(workspace):
    try:
        windll.user32.AllowSetForegroundWindow(ASFW_ANY)
        winvda.switch_desktop(workspace)
        printer.out(f"Switched to workspace #{workspace}")
    except Exception as e:
        printer.out(f"Failed to switch to workspace #{workspace}: {e}")


def send_to_named_workspace(workspace):
    try:
        window = Window.get_foreground()
        if window and window.handle:
            winvda.move_window_to_desktop(window.handle, workspace)
            printer.out(f"Moved current window to workspace #{workspace}")
    except Exception as e:
        printer.out(f"Failed to move window to workspace #{workspace}: {e}")


def move_to_named_workspace(workspace, follow=True):
    send_to_named_workspace(workspace)
    if follow:
        go_to_named_workspace(workspace)


def refresh_named_workspaces():
    sync_manager.sync(log=True)


def list_named_workspaces():
    try:
        desktops = winvda.get_desktops()
        printer.out("\nActive Virtual Desktops:")
        for d in desktops:
            printer.out(f"  #{d.number}: '{d.name}' (id={d.id})")
        printer.out(f"\nRecognized Spoken Workspace Phrases:\n  {list(workspace_dictlist.keys())}\n")
    except Exception as e:
        printer.out(f"Failed to list workspaces: {e}")


class WorkspaceNamesRule(MappingRule):
    pronunciation = "workspace names"

    mapping = {
        "go work [space] <workspace>": R(Function(go_to_named_workspace)),
        "send work [space] <workspace>": R(Function(send_to_named_workspace)),
        "move work [space] <workspace>": R(Function(move_to_named_workspace, follow=True)),
        "refresh work [spaces]": R(Function(refresh_named_workspaces)),
        "list work [spaces]": R(Function(list_named_workspaces)),
    }

    extras = [
        DictListRef("workspace", workspace_dictlist),
    ]


def get_rule():
    details = RuleDetails(name="Workspace Names")
    return WorkspaceNamesRule, details
