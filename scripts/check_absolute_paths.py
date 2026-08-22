#!/usr/bin/env python3
"""
Check Absolute Paths Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

import os
import sys
import ast
import re

# Directory to scan
RULES_DIR = os.path.join("caster_user_content", "rules")

# Regex to detect absolute paths
# 1. Windows: e.g. C:\Users\... or C:/Users/...
WINDOWS_ABS_PATH_RE = re.compile(
    r"^[A-Za-z]:[\\/](Users|Documents|Program Files|AppData|Windows|Temp|python)[\\/]", re.IGNORECASE
)
# 2. Unix: e.g. /Users/... or /home/...
UNIX_ABS_PATH_RE = re.compile(r"^/(Users|home|root|opt|var|etc|usr|bin)[/]", re.IGNORECASE)


def check_file_for_abs_paths(file_path):
    violations = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=file_path)
        for node in ast.walk(tree):
            val = None
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
            elif hasattr(ast, "Str") and isinstance(node, ast.Str):
                val = node.s

            if val:
                # Check both regexes
                if WINDOWS_ABS_PATH_RE.search(val) or UNIX_ABS_PATH_RE.search(val):
                    violations.append((node.lineno, val))

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    return violations


def main():
    if not os.path.exists(RULES_DIR):
        print(f"Rules directory '{RULES_DIR}' not found. Ensure you are running this from the repository root.")
        sys.exit(1)

    total_violations = 0
    print(f"Scanning '{RULES_DIR}' for hardcoded absolute paths...")

    for root, _, files in os.walk(RULES_DIR):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                violations = check_file_for_abs_paths(file_path)
                if violations:
                    total_violations += len(violations)
                    for line_no, val in violations:
                        print(f"Violation in {file_path}:{line_no}: Hardcoded absolute path '{val}'")

    if total_violations > 0:
        print(f"\nFound {total_violations} hardcoded absolute path violations.")
        sys.exit(1)
    else:
        print("\nNo hardcoded absolute path violations found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
