# Caster Documentation Hub

Welcome to the Caster documentation repository. This directory contains architectural blueprints, technical deep dives, troubleshooting diagnostics, framework breakdowns, and historical research for this Windows-only personal Caster/Dragonfly voice configuration.

---

## 🧭 Core Navigation & Entry Points

Start here to understand the core architecture, active features, and engineering history:

1. **[Repository Brain](context/repository-brain.md)** — **The Canonical Single Source of Truth (SSOT)**. Read this first for current facts, feature maps, confirmed architectural decisions, and known risks.
2. **[Technical Journey](history/technical_journey.md)** — Complete engineering log detailing active focus, milestones, and architectural pivots.
3. **[Speech Stack Thread Architecture](architecture/Speech_Stack_Thread_Architecture_and_Diagnostic_Report.md)** — Core breakdown of the Dragonfly/Caster threading model and STA/MTA constraints.
4. **[App Switcher Architecture](features/app_switcher.md)** — Dual-pipeline window management and switching design.
5. **[Wayfinder Master Map](wayfinder-uia-threading/map.md)** — Index of all 38+ research tickets and technical breakdowns on Windows UI Automation & threading.

---

## 📁 Categorized Directory Map

### 🏗️ [Architecture](architecture/)
High-level design documents, threading models, and Architecture Decision Records (ADRs).
* [ADR 001: Background Worker Pool](architecture/ADR_001_Background_Worker_Pool.md) *(Deprecated: See Wayfinder UIA Server)*
* [Dragonfly Foreground Focus Breakdown](architecture/dragonfly_foreground_focus_breakdown.md)
* [Speech Stack Thread Architecture & Diagnostic Report](architecture/Speech_Stack_Thread_Architecture_and_Diagnostic_Report.md)

### 🧠 [Context](context/)
Living repository memory and foundational state.
* [Repository Brain](context/repository-brain.md)

### 🚀 [Features](features/)
Feature specifications, implementation notes, and voice workflows.
* [App Switcher](features/app_switcher.md)
* [Foot Pedal Configuration](features/foot_pedal.md)
* [Top Voice Automations](features/top_voice_automations.md)
* [Antigravity Editor Insights](features/antigravity_editor_insights.md)
* [Lexicon Code Window Switching Functionality](features/lexicon_code_window_switching_functionality.md)
* [Lexicon PR 881 Feedback](features/lexicon_pr_881_feedback.md)

### 🔬 [Framework Explainers](framework_explainers/)
Educational breakdowns of underlying voice engines and Dragonfly internals.
* [Dragonfly DictList Analysis](framework_explainers/dragonfly_dictlist_analysis.md)
* [Dragonfly Rule Deep Dive](framework_explainers/dragonfly_rule_deepdive.md)

### 📜 [History](history/)
Timelines and evolution of subsystems.
* [Technical Journey](history/technical_journey.md)
* [Caster Printer HUD Timeline](history/caster_printer_hud_timeline.md)

### 🛠️ [Troubleshooting & Diagnostics](troubleshooting/)
Bug post-mortems, crash logs, and diagnostic runbooks.
* [UIA Diagnostic](troubleshooting/uia_diagnostic.md)
* [App Switcher Findings](troubleshooting/app_switcher_findings.md)
* [Virtual Desktop Switching Focus Bug](troubleshooting/virtual_desktop_switching_focus_bug.md)
* [Kaldi Crash Explanation](troubleshooting/kaldi_crash_explanation.md)
* [Kaldi Race Condition Answers](troubleshooting/kaldi_race_condition_answers.md)
* [2026-07-07 Kaldi Compiler Bug](troubleshooting/2026-07-07-kaldi-compiler-bug.md)
* [Fix Comparison](troubleshooting/Fix_Comparison.md)

### 🧭 [Wayfinder UIA & Threading Research](wayfinder-uia-threading/)
Consolidated research and ticket archive from the Wayfinder investigation into Windows UI Automation and thread models.
* [Wayfinder Map](wayfinder-uia-threading/map.md)
* [Claude Critique & Verified Takeaways](wayfinder-uia-threading/claude-critique-verified-takeaways.md)
* [Codex Context Extract](wayfinder-uia-threading/codex-context-extract.md)
* [Research Archive (38 tickets)](wayfinder-uia-threading/research/)

### ⚙️ [Kaldi Engine](kaldi_engine/)
Engine-specific static analysis and low-level anatomy.
* [Kaldi Engine Static Anatomy](kaldi_engine/kaldi_engine_static_anatomy.md)

### 📝 [Prompts](prompts/) & 🗄️ [Legacy Notes](legacy_notes/)
* [Architecture Onboarding Prompt](prompts/Architecture-OnBoarding.md)
* [Legacy Notes Index](legacy_notes/) (`ideas.md`, `ace-space-transform.md`, `caster-study-notes.md`, `runcommand-system-settings.md`)
* [Superseded Archive](archive/)

---

## 🤖 Agent Guardrails & Operating Standards

If you are an AI agent operating in this repository:
1. **Adhere to [AGENTS.md](../.agents/AGENTS.md)**: Follow all workspace rules (e.g., `py -3.10`, relative links, local state isolation).
2. **Context Window Discipline**: Use relative breadcrumbs at the top of documents and reference the [Repository Brain](context/repository-brain.md) rather than duplicating large file trees.
3. **Verify Links**: Maintain valid relative markdown links across all documentation.
