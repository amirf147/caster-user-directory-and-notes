"""
Text Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

import pyperclip


def text_to_clipboard(text):
    pyperclip.copy(text)
