# Caster Workspace Rules

## Agent Constraints & Workflows

### Python Environment
- Always run Python commands in this workspace using the specific launcher command `py -3.10` instead of just `python`.
  - Example: `py -3.10 path/to/script.py`
  - Example: `py -3.10 -c "import dragonfly; print(dragonfly.__version__)"`

### File Paths & Documentation
- Always use relative paths for files and markdown links to prevent local system metadata leaks.
- If absolute paths are required in code, store them in the untracked `caster_user_content/environment_variables.py` and reference them using standard Python path utilities.

### Runtime Boundaries
- `caster_user_content/` is the active, loadable Caster rules package. Maintain its structure to ensure rules remain loadable.
- Private configurations, local machine state (`settings/`, `data/`, etc.), and environment variables must remain untracked to protect personal settings and keep the release artifacts clean.
- Experiments and non-production prototypes should be isolated from the production `rules/` directory.

### Validation
- Every behavior change to code or configuration must be followed by running the relevant validation command(s) to verify safety and correctness (e.g., custom validation scripts for absolute paths and duplicate phrases).

### Status Updates & README Preservation
- Whenever making changes to the master `README.md` at the repository root related to status updates or active engineering focus, any previous content being replaced or removed must be preserved and prepended to `status-update-history.md` exactly as it was, maintaining a continuous, accurate historical timeline.

