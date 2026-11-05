"""
Text Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

import pyperclip
from dragonfly import Clipboard
from castervoice.lib.actions import Text


def text_to_clipboard(text):
    pyperclip.copy(text)


def type_clipboard(pause=0.0, max_chars=10000):
    text = Clipboard.get_system_text()
    if not text:
        return
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if len(normalized) > max_chars:
        print(f"[Caster] Warning: Clipboard text exceeds {max_chars} characters; truncating.")
        normalized = normalized[:max_chars]
    Text(normalized, static=True, pause=pause).execute()
