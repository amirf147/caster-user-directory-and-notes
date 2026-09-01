# Caster Documentation Hub

Welcome to the Caster documentation repository. This directory contains architectural blueprints, technical deep dives, troubleshooting diagnostics, framework breakdowns, and historical research for this Windows-only personal Caster/Dragonfly voice configuration.

---

## 🧭 Core Navigation & Entry Points

Start here to understand the core architecture, active features, and engineering history:

1. **[Repository Brain](context/repository-brain.md)** — **The Canonical Single Source of Truth (SSOT)**. Read this first for current facts, feature maps, confirmed architectural decisions, and known risks.
2. **[ADCE Context Hub](accessibility_mcp/CONTEXT.md)** — Living context hub and technical blueprint for the **Active Desktop Context Engine (ADCE)** and Accessibility MCP.
3. **[Technical Journey](history/technical_journey.md)** — Complete engineering log detailing active focus, milestones, and architectural pivots.
4. **[App Switcher Architectural Blueprint (v3)](architecture/app_switcher_architectural_blueprint.md)** — Authoritative production blueprint for our sub-millisecond native Win32 window switcher.
5. **[App Switcher Evolution Timeline](history/app_switcher_timeline.md)** — 2-year retrospective tracing window switching across 5 eras (Windhawk taskbar macros → Pywinauto → Native Win32 v3).
6. **[Speech Stack Thread Architecture](architecture/Speech_Stack_Thread_Architecture_and_Diagnostic_Report.md)** — Core breakdown of the Dragonfly/Caster threading model and STA/MTA constraints.
7. **[Wayfinder Master Map](wayfinder-uia-threading/map.md)** — Index of all 38+ research tickets and technical breakdowns on Windows UI Automation & threading.

---

## 📁 Categorized Directory Map

### 🌐 [Accessibility MCP & Active Context Engine](accessibility_mcp/)
Real-time OS semantic state tracking, deep tab discovery, and Model Context Protocol (MCP) server architecture.
* **[ADCE Living Context Hub](accessibility_mcp/CONTEXT.md)** *(Living Single Source of Truth)*
* [001: Exploration, Analysis & Planning](accessibility_mcp/001_exploration_analysis_planning.md)
* [002: Epistemology, Patterns & Observability](accessibility_mcp/002_epistemology_patterns_and_observability.md)
* [003: Cross-Platform Strategic Analysis](accessibility_mcp/003_strategic_analysis_cross_platform_and_context.md)
* [004: Deep Research Metaprompt](accessibility_mcp/004_deep_research_metaprompt.md)
* [005: Semantic Index & App SDK Analysis](accessibility_mcp/005_semantic_index_and_app_sdk.md)
* [006: PoC Architecture Specification](accessibility_mcp/006_poc_architecture.md)
* [007: Tab Extraction & Context Representation](accessibility_mcp/007_tab_extraction_and_context_representation.md)
* [008: Real-World Observations & Caching Architecture](accessibility_mcp/008_real_world_observations_and_caching_architecture.md)
* [009: Live Telemetry & Tab Diagnostics](accessibility_mcp/009_live_telemetry_and_tab_diagnostics.md)
* [010: Telemetry Benchmarks & Live Findings](accessibility_mcp/010_telemetry_benchmarks_and_live_findings.md)
* [011: Landscape Review, FlaUI & Dual-Plane Architecture](accessibility_mcp/011_flaui_evaluation_and_dual_plane_architecture.md)
* [012: Live Empirical Tab Extraction Report](accessibility_mcp/012_empirical_tab_extraction_report.md)
* [014: C# Context Daemon Handover & Skill Specification](accessibility_mcp/014_csharp_daemon_handover_and_skill_spec.md) *(Exploratory Blueprint - Paused)*
* [015: Epistemic Recalibration & Adversarial Architecture Review](accessibility_mcp/015_recalibration_and_adversarial_architecture_review.md)

### 🪟 [PyVDA Virtual Desktop Analysis](pyvda/)
Deep dive into Windows Virtual Desktop COM APIs, Explorer crash recovery, and threading.
* [001: RPC Server Unavailability & Stale Proxy Fix Analysis](pyvda/001_pyvda_rpc_and_com_lifecycle_analysis.md)
* [002: PyVDA Core Architecture & Threading Critique](pyvda/002_pyvda_core_architecture_and_threading_critique.md)

### 🖥️ [Caster HUD Architecture](caster_hud/)
Educational primers, specifications, and post-mortems for the Modular Caster HUD overlay.
* **[005: Master Requirements & Specifications (SSoT)](caster_hud/005_caster_hud_requirements_and_specifications.md)** *(Authoritative Single Source of Truth)*
* [001: Baseline Architecture, Threading & IPC Primer](caster_hud/001_caster_hud_architecture_and_threading_primer.md) *(Foundational Reference)*
* [002: System Tray Integration & Upstream Evolution Audit](caster_hud/002_caster_hud_system_tray_and_upstream_evolution_audit.md) *(Historical Context)*
* [003: Theming Presets & Layout Persistence Specification](caster_hud/003_caster_hud_modular_theming_and_profiles_architecture.md)
* [004: Next-Iteration Modular Architecture Blueprint](caster_hud/004_caster_hud_nextgen_modular_architecture_and_context_integration.md) *(Architectural Design)*
* [006: Thread Safety & Compatibility Post-Mortem](caster_hud/006_caster_hud_thread_safety_and_compatibility_postmortem.md) *(RCA & Deadlock Analysis)*
* [007: Continuous Lessons Learned Timeline](caster_hud/007_caster_hud_lessons_learned_timeline.md) *(Living Engineering Trail)*
* [008: Dragonfly & ADCE Active Rules Resolution Deep Dive](caster_hud/008_dragonfly_and_adce_active_rules_resolution_deep_dive.md)
* [009: Architectural Review & Clean Architecture Synthesis](caster_hud/009_caster_hud_architectural_review_and_clean_architecture_synthesis.md)
* [010: Fine-Grained Context: Native OS vs ADCE Explainer](caster_hud/010_fine_grained_context_recognition_native_vs_adce_explainer.md)
* [011: ADCE Realtime Stream & Native Focus Decoupling](caster_hud/011_adce_realtime_stream_and_native_focus_decoupling_deep_dive.md)

### 💡 [Future Ideas & Iterations](future_ideas/)
Conceptual designs and future capability blueprints for upcoming Caster iterations.
* [001: Caster Help Rule & Context-Aware Assistance Architecture](future_ideas/001_caster_help_rule_and_context_aware_assist_architecture.md)
* [003: Variable Changer Teardown & Reliable Editor Navigation Architecture](future_ideas/003_variable_changer_teardown_and_reliable_editor_navigation_architecture.md)

### 🏗️ [Architecture](architecture/)
High-level design documents, threading models, and Architecture Decision Records (ADRs).
* **[App Switcher Architectural Blueprint (v3)](architecture/app_switcher_architectural_blueprint.md)** *(Active Production Blueprint)*
* [Speech Stack Thread Architecture & Diagnostic Report](architecture/Speech_Stack_Thread_Architecture_and_Diagnostic_Report.md)
* [Dragonfly Foreground Focus Breakdown](architecture/dragonfly_foreground_focus_breakdown.md)
* [App Switcher Focus Analysis](architecture/app_switcher_focus_analysis.md)
* [App Switcher Code Review & Refactoring Guide](architecture/app_switcher_code_review.md)
* [ADR 001: Background Worker Pool](architecture/ADR_001_Background_Worker_Pool.md) *(Deprecated: See Wayfinder UIA Server)*
* **Archived Blueprints**:
  * [Blueprint v1 (Archived)](architecture/archive/app_switcher_architectural_blueprint_v1.md)
  * [Blueprint v2 (Archived)](architecture/archive/app_switcher_architectural_blueprint_v2.md)

### 🧠 [Context](context/)
Living repository memory and foundational state.
* [Repository Brain](context/repository-brain.md)

### 🚀 [Features](features/)
Feature specifications, implementation notes, and voice workflows.
* [App Switcher](features/app_switcher.md)
* [ADCE Dynamic IDE Terminal Context Guide](features/adce_dynamic_terminal_context_guide.md)
* [Foot Pedal Configuration](features/foot_pedal.md)
* [Top Voice Automations](features/top_voice_automations.md)
* [Antigravity Editor Insights](features/antigravity_editor_insights.md)
* [Lexicon Code Window Switching Functionality](features/lexicon_code_window_switching_functionality.md)
* [Lexicon PR 881 Feedback](features/lexicon_pr_881_feedback.md)
* [Number Series CCR Analysis](features/number-series-ccr-analysis.md)

### 🔬 [Framework Explainers](framework_explainers/)
Educational breakdowns of underlying voice engines and Dragonfly internals.
* [NodeRule and TreeRule Architecture (Stateful Command Trees)](framework_explainers/noderule_and_treerule_architecture.md)
* [Caster TreeRule Practical Candidates & Refactoring Guide](framework_explainers/caster_treerule_practical_candidates.md)
* [Dragonfly DictList Analysis](framework_explainers/dragonfly_dictlist_analysis.md)
* [Dragonfly Rule Deep Dive](framework_explainers/dragonfly_rule_deepdive.md)
* [Dragonfly Recognition Observers & Functional Contexts](framework_explainers/dragonfly_recognition_observers_and_functional_contexts.md)

### 📜 [History](history/)
Timelines and evolution of subsystems.
* [App Switcher Evolution Timeline](history/app_switcher_timeline.md) *(2-year window switching evolution)*
* [Repository Timeline (2024–2026)](history/repository_timeline.md) *(27-month, 969-commit repository narrative)*
* [Caster Printer HUD Timeline](history/caster_printer_hud_timeline.md) *(Status messaging & HUD evolution)*
* [Technical Journey](history/technical_journey.md) *(Current focus & milestones)*
* [Interactive Timeline Web App](history/timeline.html) *(Visual timeline application)*

### 🛠️ [Troubleshooting & Diagnostics](troubleshooting/)
Bug post-mortems, crash logs, and diagnostic runbooks.
* [UIA Diagnostic](troubleshooting/uia_diagnostic.md)
* [App Switcher Findings](troubleshooting/app_switcher_findings.md)
* [Virtual Desktop Switching Focus Bug](troubleshooting/virtual_desktop_switching_focus_bug.md)
* [Kaldi Crash Explanation](troubleshooting/kaldi_crash_explanation.md)
* [Kaldi Race Condition Answers](troubleshooting/kaldi_race_condition_answers.md)
* [2026-07-07 Kaldi Compiler Bug](troubleshooting/2026-07-07-kaldi-compiler-bug.md)
* [Fix Comparison](troubleshooting/Fix_Comparison.md)
* [AsynchronousAction Lifecycle Failure & Clipboard Polling Loop](troubleshooting/asynchronous_action_uncancellable_and_clipboard_loop.md)

### 🧭 [Wayfinder UIA & Threading Research](wayfinder-uia-threading/)
Consolidated research session archive from the Wayfinder investigation into Windows UI Automation, COM apartment threading models, and `app_switcher.py` hang mechanisms.
* [Wayfinder Map](wayfinder-uia-threading/map.md)
* [Claude Critique & Verified Takeaways](wayfinder-uia-threading/claude-critique-verified-takeaways.md)
* [Codex Context Extract](wayfinder-uia-threading/codex-context-extract.md)
* [Research Archive (38 tickets)](wayfinder-uia-threading/research/)

### ⚙️ [Kaldi Engine](kaldi_engine/)
Engine-specific static analysis and low-level anatomy.
* [Kaldi Engine Static Anatomy](kaldi_engine/kaldi_engine_static_anatomy.md)

### ⚖️ [Licensing & Attribution](licensing/licensing_and_attribution_guide.md)
Legal architecture, repository multi-licensing strategy, and comprehensive file attribution audit.
* **[Licensing & Attribution Guide](licensing/licensing_and_attribution_guide.md)** *(Authoritative licensing breakdown & compliance matrix)*

### 📝 [Prompts](prompts/) & 🗄️ [Legacy Notes](legacy_notes/)
* [Architecture Onboarding Prompt](prompts/Architecture-OnBoarding.md)
* [Git Journey Timeline Orchestration](prompts/git-journey-timeline-orchestration.md)
* [Legacy Notes Index](legacy_notes/) (`ideas.md`, `ace-space-transform.md`, `caster-study-notes.md`, `runcommand-system-settings.md`)

---

## 🤖 Agent Guardrails & Operating Standards

If you are an AI agent operating in this repository:
1. **Adhere to [AGENTS.md](../.agents/AGENTS.md)**: Follow all workspace rules (e.g., `py -3.10`, relative links, local state isolation).
2. **Context Window Discipline**: Use relative breadcrumbs at the top of documents and reference the [Repository Brain](context/repository-brain.md) rather than duplicating large file trees.
3. **Verify Links**: Maintain valid relative markdown links across all documentation.

