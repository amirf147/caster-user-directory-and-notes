"""
Generate Rdescript Module

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""


def generate_rdescript(command_name, category, description):
    return f"""
-------- Executing:

            {category} - "{command_name}"

-------- Description:

            {description}
            """
