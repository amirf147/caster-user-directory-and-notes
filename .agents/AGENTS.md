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

### Licensing & File Headers
- Every newly created or modified source file must carry appropriate SPDX headers and copyright notices per [`docs/licensing/licensing_and_attribution_guide.md`](../docs/licensing/licensing_and_attribution_guide.md):
  - **Original Work & Utilities** (`scripts/`, `util/`, new rules): `SPDX-License-Identifier: Apache-2.0` with `Copyright (c) 2024-2026 Amir Farhadi`.
  - **Derivative Caster Rules** (modified upstream rules): `SPDX-License-Identifier: LGPL-3.0-or-later` preserving upstream author credits and modification notice.

### Epistemic Discipline & Architectural Gating
- Do not propose multi-file architectural rewrites or cross-runtime pivots based on theoretical advantages alone.
- Every major architectural recommendation must follow the 4-Gate Epistemic Gating Protocol via [`workflows/adversarial-architecture-review.md`](workflows/adversarial-architecture-review.md) (rationale codified in [`docs/accessibility_mcp/015_recalibration_and_adversarial_architecture_review.md`](../docs/accessibility_mcp/015_recalibration_and_adversarial_architecture_review.md)):
  1. **Gate 1: Physical Observation & Telemetry** (raw metrics only; architectural solutions strictly forbidden).
  2. **Gate 2: Adversarial Red-Team** (generate 3 mutually exclusive options; expose 3 fatal flaws & hidden assumptions; ban premature verdicts).
  3. **Gate 3: Empirical Micro-Spike** (minimal <50-line test script executed live against active OS targets to validate/falsify physical assumptions).
  4. **Gate 4: Architectural Blueprint & Spec** (formalize specs only after empirical micro-spikes prove viability).

