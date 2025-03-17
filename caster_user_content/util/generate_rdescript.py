def generate_rdescript(command_name, category, description):
    return f"""
-------- Executing:

            {category} - "{command_name}"

-------- Description:

            {description}
            """
