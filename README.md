# Caster User Directory

**Purpose and Scope:** A highly customized, Windows-only personal Caster and Dragonfly configuration for voice-driven computing and productivity. For upstream context on user directories in Caster, see the [Official Caster User Directory Documentation](https://caster.readthedocs.io/en/latest/readthedocs/User_Dir/Caster_User_Dir/).

---

### 🟢 Status Box
*   **Active Runtime**: Custom rules, robust global voice macros, and window management utilities via `caster_user_content/`.
*   **Active Utilities**: App Switcher (`caster_user_content/util/app_switcher.py`) providing fast, deterministic window focus and management.
*   **Research & Explorations**: Historical exploratory sessions and research spikes (e.g., UIA threading and window management investigations) are documented in `docs/wayfinder-uia-threading/` and `docs/archive/`.

---

## 🚀 Quick Start

1.  **Prerequisites**: Python 3.10 is strictly required. Ensure `py -3.10` works in your shell.
2.  **Location**: Clone this repository to your local AppData directory where Caster expects it (typically `%LOCALAPPDATA%\caster`).
3.  **Dependencies**: Install required packages via `py -3.10 -m pip install -r requirements.txt` (if applicable) or follow the standard Caster setup instructions.
4.  **Private Config Bootstrap**: Your local settings and data are not tracked by Git. Create them using the safe templates (e.g., `config/examples/`) and place them in the ignored `settings/` and `data/` directories.
5.  **Validation**: After any changes, run the validation checks (see "Development Checks" below).

---

## 🗺️ Runtime Map

The repository is structured to separate live runtime from experiments and local state:

*   `caster_user_content/rules/`: **Active Payload**. This is where live, loadable Caster grammars and macros live (`global/`, `apps/`, etc.).
*   `caster_user_content/util/`: Core utilities supporting active rules (e.g., window switching logic in `app_switcher.py`).
*   `settings/` & `data/`: **Ignored**. Your personal local machine state. Must remain untracked.
*   `integrations/`: Optional external integrations (e.g., Sikuli, foot pedals).

---

## 📋 Common Tasks

| Task | Action |
| :--- | :--- |
| **Add an app rule** | Create a new `.py` file in `caster_user_content/rules/apps/` |
| **Modify a global rule** | Edit existing files in `caster_user_content/rules/global/` |
| **Change window switching** | Review `caster_user_content/util/app_switcher.py` and refer to the feature docs |
| **Troubleshoot setup** | See the Operations Guide or verify your local `settings/` |

---

## 📚 Documentation Entry Points

New to this setup? Start here to understand the architecture and components:

1.  **[Documentation Hub](docs/README.md)**: Your front door for documentation navigation.
2.  **[Repository Brain](docs/context/repository-brain.md)**: The canonical project memory, facts, and architecture decisions.
3.  **Feature Map**: (Coming soon) Deep dive into core features.
4.  **Operations Guide**: (Coming soon) Setup and troubleshooting runbooks.
5.  **[Technical Journey](docs/history/technical_journey.md)**: The history of our investigations and why certain paths were chosen.
6.  **[Window Management & App Switching Notes](docs/context/repository-brain.md#4-current-facts--architecture-window-management--app-switching)**: Compact summary of window switching facts, empirical findings, and exploratory research spikes.

---

## 🧪 Development Checks & Guardrails

To prevent drift and metadata leakage, run these checks before committing:

1.  **Absolute Path Checker**: Validates that no absolute paths leaked into the `rules/` directory.
2.  **Duplicate Phrase Checker**: Verifies command uniqueness across grammars.
3.  **Ruff**: Standard Python linting and formatting.

**Local-State Policy**: 
Personal configurations, `settings/`, `data/`, environment variables, and API keys are strictly `.gitignore`d. This prevents accidentally publishing personal data. To recreate a local environment, copy the files from `config/examples/` (once created) to your root.

**Explicit Non-Goals & Experiment Boundary**:
Experiments and LLM exploratory tools (like broad "computer-use" servers) must not interfere with the deterministic Caster voice execution path. They are kept isolated from `caster_user_content/rules/`. 

> [!WARNING]
> **Archive Note**: If a document or folder is marked as "Archive" or "Legacy" (e.g., `attic/`, `old/`, `docs/legacy_notes/`), it contains superseded material. Please direct your attention to the **Repository Brain** for current facts.