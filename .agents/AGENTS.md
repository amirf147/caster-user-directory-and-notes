# Caster Workspace Rules

## Python Environment
- Always run Python commands in this workspace using the specific launcher command `py -3.10` instead of just `python`.
  - Example: `py -3.10 path/to/script.py`
  - Example: `py -3.10 -c "import dragonfly; print(dragonfly.__version__)"`

## Documentation & Markdown Links
- Always use relative file paths for links in markdown files and documentation (e.g., `../caster_user_content/util/app_switcher.py#L10` instead of absolute `file:///...` URLs).
  - This ensures file links render correctly on GitHub and across different local environments without breaking.

