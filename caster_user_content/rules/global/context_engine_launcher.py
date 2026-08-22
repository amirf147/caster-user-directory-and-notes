"""
Context Engine Launcher Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

import os
import subprocess
from dragonfly import MappingRule, Function
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib import printer


def launch_context_engine():
    """Launch the Python ADCE context monitor in an external, dedicated terminal window."""
    try:
        # Determine the relative path to scripts/context_poc.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate from caster_user_content/rules/global to repo root, then scripts/context_poc.py
        repo_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        script_path = os.path.join(repo_root, "scripts", "context_poc.py")

        if not os.path.exists(script_path):
            printer.out(f"Context Engine Error: Script not found at {script_path}")
            return

        printer.out("Context Engine: Spawning ADCE live monitor in separate console...")
        subprocess.Popen(
            ["py", "-3.10", script_path],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            cwd=repo_root,
        )
    except Exception as e:
        printer.out(f"Context Engine Launch Error: {e}")


class ContextEngineLauncherRule(MappingRule):
    pronunciation = "context engine launcher"
    mapping = {
        "launch context engine": Function(launch_context_engine),
    }


def get_rule():
    return ContextEngineLauncherRule, RuleDetails(name="context engine launcher", executable=None, title=None)
