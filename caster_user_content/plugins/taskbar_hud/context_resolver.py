# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Amir Farhadi

"""
Decoupled ADCE Context Resolver for Taskbar HUD

Maps out-of-process Active Desktop Context Engine (ADCE) telemetry
(process name, window title, semantic zone) directly to active voice rules
without querying Caster's internal Dragonfly engine or speech loop.
"""

from pathlib import Path
from typing import List, Optional

# Process stem to active rules mapping
# Stems are normalized (lowercase, no '.exe')
PROCESS_RULES_MAP = {
    "waterfox": ["Firefox CCR", "Firefox Extended"],
    "firefox": ["Firefox CCR", "Firefox Extended"],
    "antigravity ide": ["Antigravity IDE", "CustomVSCode CCR"],
    "antigravity": ["Antigravity Standalone"],
    "code": ["CustomVSCode", "CustomVSCode CCR"],
    "cursor": ["CustomVSCode", "CustomVSCode CCR"],
    "windsurf": ["CustomVSCode", "CustomVSCode CCR"],
    "vscodium": ["CustomVSCode", "CustomVSCode CCR"],
    "explorer": ["Explorer"],
    "pwsh": ["PowerShell", "PowerShell CCR"],
    "powershell": ["PowerShell", "PowerShell CCR"],
    "windowsterminal": ["PowerShell", "PowerShell CCR"],
    "cmd": ["PowerShell", "PowerShell CCR"],
    "conhost": ["PowerShell", "PowerShell CCR"],
    "calc": ["Calc Rule"],
    "soffice": ["Writer CCR", "Writer Rule"],
    "excel": ["Excel CCR"],
    "winword": ["Word CCR"],
    "figma": ["Figma CCR"],
    "zoom": ["Zoom"],
    "telegram": ["Telegram"],
}

# Website-specific title triggers when a browser is active
BROWSER_TITLE_RULES = [
    ("youtube", "YouTube"),
    ("chatgpt", "ChatGPT"),
    ("gemini", "Gemini"),
    ("leetcode", "LeetCode"),
    ("trello", "Trello"),
    ("github", "GitHub"),
]

# Terminal zones that activate IDETerminalRule in developer editors
TERMINAL_ZONES = frozenset(
    [
        "terminal",
        "integratedterminal",
        "{terminal}",
        "[terminal]",
        "{integratedterminal}",
        "[integratedterminal]",
    ]
)


def normalize_process_name(raw_process: Optional[str]) -> str:
    """Normalizes process name or executable path to lowercase stem."""
    if not raw_process:
        return ""
    p = str(raw_process).strip().lower().replace("/", "\\")
    stem = Path(p).stem
    return stem


def normalize_zone(raw_zone: Optional[str]) -> str:
    """Normalizes semantic zone string."""
    if not raw_zone:
        return ""
    return str(raw_zone).strip().lower().replace(" ", "").replace("_", "")


def resolve_active_rules(
    process_name: Optional[str] = None,
    window_title: Optional[str] = None,
    semantic_zone: Optional[str] = None,
) -> List[str]:
    """
    Deterministically resolves active contextual voice rules from ADCE telemetry.
    Returns an empty list [] for generic, untracked, or desktop contexts.
    """
    proc = normalize_process_name(process_name)
    if not proc:
        return []

    rules: List[str] = []

    # 1. Base process matching
    base_rules = PROCESS_RULES_MAP.get(proc)
    if base_rules:
        rules.extend(base_rules)

    # 2. Browser website contextual rules
    if proc in ("waterfox", "firefox"):
        if window_title:
            title_low = window_title.lower()
            for trigger, rule_name in BROWSER_TITLE_RULES:
                if trigger in title_low and rule_name not in rules:
                    rules.append(rule_name)

    # 3. IDE Integrated Terminal sub-window zone rules
    if proc in ("antigravity ide", "code", "cursor", "windsurf", "vscodium"):
        z_norm = normalize_zone(semantic_zone)
        if any(tz in z_norm for tz in ("terminal", "integratedterminal")):
            if "IDETerminal" not in rules:
                rules.append("IDETerminal")

    return rules
