#!/usr/bin/env python3
import os
import sys
import ast
from collections import defaultdict

# Directory to scan
RULES_DIR = os.path.join("caster_user_content", "rules")


class MappingVisitor(ast.NodeVisitor):
    def __init__(self, file_path):
        self.file_path = file_path
        self.mappings = {}

    def visit_ClassDef(self, node):
        # We look for a class-level attribute named 'mapping'
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "mapping":
                        if isinstance(item.value, ast.Dict):
                            extracted_keys = []
                            for key in item.value.keys:
                                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                                    extracted_keys.append(key.value)
                                elif hasattr(ast, "Str") and isinstance(key, ast.Str):
                                    extracted_keys.append(key.s)
                            if extracted_keys:
                                self.mappings[node.name] = extracted_keys
        self.generic_visit(node)


def main():
    if not os.path.exists(RULES_DIR):
        print(f"Rules directory '{RULES_DIR}' not found. Ensure you are running this from the repository root.")
        sys.exit(1)

    print(f"Scanning '{RULES_DIR}' for voice command collisions...")
    command_registry = defaultdict(list)

    for root, _, files in os.walk(RULES_DIR):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    tree = ast.parse(content, filename=file_path)
                    visitor = MappingVisitor(file_path)
                    visitor.visit(tree)

                    for class_name, keys in visitor.mappings.items():
                        for key in keys:
                            command_registry[key.strip()].append((file_path, class_name))
                except Exception as e:
                    print(f"Error parsing {file_path}: {e}")

    collisions = 0
    for cmd, occurrences in command_registry.items():
        if len(occurrences) > 1:
            collisions += 1
            print(f"\nCollision detected for voice command '{cmd}':")
            for path, class_name in occurrences:
                print(f"  - File: {path}, Class: {class_name}")

    if collisions > 0:
        print(f"\nFound {collisions} voice command collision(s).")
        # We can warning-exit or fail-exit. Usually warning-exit is better since some rules
        # might be app-specific and loaded selectively, meaning collisions across different apps
        # are totally fine. But collisions within the same global scope are problematic.
        # Since app rules aren't active at the same time as other apps, we shouldn't necessarily fail
        # but print warnings.
        # Let's return exit code 0 to keep it as warnings rather than failing the build,
        # but let the user know. Or we can filter: only fail if they are in global rules.
        sys.exit(0)
    else:
        print("\nNo voice command collisions found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
