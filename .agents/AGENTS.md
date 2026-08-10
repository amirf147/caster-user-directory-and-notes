# Caster Workspace Rules

## Python Environment
- Always run Python commands in this workspace using the specific launcher command `py -3.10` instead of just `python`.
  - Example: `py -3.10 path/to/script.py`
  - Example: `py -3.10 -c "import dragonfly; print(dragonfly.__version__)"`

## File Paths & Documentation Links
- Always use relative paths for files and markdown links to prevent local system metadata leaks.
- If absolute paths are required in code, store them in the untracked `caster_user_content/environment_variables.py` and reference them using standard Python path utilities.
