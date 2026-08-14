# Example environment variables file.
# Copy this file to caster_user_content/environment_variables.py and populate it with your own paths.
# DO NOT commit your personalized version to version control.

ENVIRONMENT_FILE = "C:/path/to/caster_user_content/environment_variables.py"
ENVIRONMENT_VARIABLES = {
    "environment file": "ENVIRONMENT_FILE",
    "window aliases": "WINDOW_ALIASES",
    "caster file paths": "CASTER_FILE_PATHS",
    # Add other mappings here as needed
}

WINDOW_ALIASES = ["example1", "example2"]

# Personal info
FIRST_NAME = "Your First Name"
LAST_NAME = "Your Last Name"
EMAIL = "your.email@example.com"

# Paths
CASTER_USER_DIRECTORY = "C:\\path\\to\\caster"
RULES = "C:\\path\\to\\caster\\caster_user_content\\rules"

# File Paths (Example structure)
CASTER_FILE_PATHS = {
    "global": f"{RULES}\\global\\global_nonccr_extended.py",
}

CASTER_FILE_NAMES = {
    "global": "global_nonccr_extended.py",
}

WINDOWS_APP_ALIASES = {
    "code": ["Visual Studio Code", "Cursor"],
}

WINDOWS_APP_NAMES = {
    "Visual Studio Code",
    "Cursor",
}

PATHS = {
    "documents": "C:/Users/YourUser/Documents",
}

WEBSITES = {
    "github": "https://github.com/",
}

INSERTABLE_TEXT = {
    "first name": FIRST_NAME,
    "last name": LAST_NAME,
}

FILE_EXPLORER_PATHS = {
    "documents": "C:\\Users\\YourUser\\Documents\\",
}

EXECUTABLES = {
    "pi": "py",
}

RUN_COMMANDS = {
    "restart explorer": "bat file path here",
}
