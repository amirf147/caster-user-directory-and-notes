#!/usr/bin/env python3
"""
Check Absolute Paths Module

Validates Python rules/scripts and Markdown documentation across the repository
for hardcoded absolute paths, local system metadata leaks, and absolute file:/// links.

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

import ast
import os
import re
import sys

# Scanning roots
SCAN_DIRS = [
    ("caster_user_content", [".py"]),
    ("scripts", [".py"]),
    ("docs", [".md"]),
]

# Files explicitly exempt from absolute path scanning (untracked local environment definitions)
EXEMPT_FILES = {
    "environment_variables.py",
}

# Regex patterns for Python code string literals
WINDOWS_ABS_PATH_RE = re.compile(
    r"^[A-Za-z]:[\\/](Users|Documents|Program Files|AppData|Windows|Temp|python)[\\/]", re.IGNORECASE
)
UNIX_ABS_PATH_RE = re.compile(r"^/(Users|home|root|opt|var|etc|usr|bin)[/]", re.IGNORECASE)

# Regex pattern for Markdown link destinations e.g. [text](file:///...) or [text](C:/Users/...)
MD_LINK_ABS_RE = re.compile(
    r"\[([^\]]*)\]\((file:///[^\)]+|[A-Za-z]:[\\/][^\)]+|/(Users|home)/[^\)]+)\)", re.IGNORECASE
)


def check_python_file(file_path):
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
                if WINDOWS_ABS_PATH_RE.search(val) or UNIX_ABS_PATH_RE.search(val):
                    violations.append((node.lineno, f"Hardcoded absolute path: '{val}'"))

    except Exception as e:
        print(f"Error parsing Python file {file_path}: {e}")
    return violations


def check_markdown_file(file_path):
    violations = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line_no, line in enumerate(lines, start=1):
            # Allow educational discussion in specific insights document
            if "antigravity_editor_insights.md" in file_path and ("`file:///" in line or "system prompt" in line):
                continue

            matches = MD_LINK_ABS_RE.findall(line)
            for link_text, link_target in matches:
                violations.append((line_no, f"Absolute markdown link destination: '[{link_text}]({link_target})'"))

    except Exception as e:
        print(f"Error reading Markdown file {file_path}: {e}")
    return violations


def main():
    total_violations = 0
    print("Running repository-wide absolute path and link audit...")

    for dir_name, extensions in SCAN_DIRS:
        if not os.path.exists(dir_name):
            continue

        for root, _, files in os.walk(dir_name):
            for file in files:
                if file in EXEMPT_FILES:
                    continue

                file_ext = os.path.splitext(file)[1].lower()
                if file_ext not in extensions:
                    continue

                file_path = os.path.join(root, file)
                if file_ext == ".py":
                    violations = check_python_file(file_path)
                elif file_ext == ".md":
                    violations = check_markdown_file(file_path)
                else:
                    violations = []

                if violations:
                    total_violations += len(violations)
                    for line_no, msg in violations:
                        print(f"Violation in {file_path}:{line_no}: {msg}")

    if total_violations > 0:
        print(f"\nFound {total_violations} path/link violation(s).")
        sys.exit(1)
    else:
        print("\nNo hardcoded absolute paths or absolute markdown links found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
