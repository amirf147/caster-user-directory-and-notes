# Caster User Directory

Welcome to my Caster user directory, here I have all my custom commands and grammars for automating my workflows and speeding up voice computing.

## Tools & Workflows

Here are the various tools and scripts configured in this environment:

- **[Foot Pedal & XML-RPC IPC Bridge](docs/foot_pedal.md)**: Hardware debouncing, smart tap/drag/scroll control for the Olympus RS31H foot pedal, integrated with a local XML-RPC IPC bridge for thread-safe hands-free Caster microphone toggling.
- **[App & Window Switcher](docs/app_switcher.md)**: Failsafe and workspace-aware window management to switch apps and tabs by voice.

## Caster Extension

Caster is an extension to the Dragonfly framework that allows you to control your computer with voice commands.

### .agents Folder
This folder contains workflows and configuration files specifically for the **Antigravity** editor.

## App Switching & UIA Threading Investigation (Wayfinder Session)

We are currently undertaking a Wayfinder session to understand and rewrite our window switching code (`app_switcher.py` and `text_editing.py`). During this work, we have dug deep into COM threading mechanics (STA vs. MTA), UIA fallback mechanisms, and multi-process architecture across screen readers (NVDA), automation frameworks (Terminator, UFO), Dragonfly, and Caster core.

All decision tracking and research breakdowns for this investigation can be found in the Wayfinder directory:
- **[Wayfinder UIA & Threading Session Directory](docs/wayfinder-uia-threading/map.md)**: Active decision tracking map, tickets, and deep-dive educational research breakdowns.
- [ADR_001_Background_Worker_Pool.md](docs/ADR_001_Background_Worker_Pool.md): *(Deprecated)* Initial decision record for generic thread pool approach.
- [Speech Stack Thread Architecture & Diagnostic Report](docs/Speech_Stack_Thread_Architecture_and_Diagnostic_Report.md): Root cause analysis detailing why Caster freezes on synchronous `time.sleep()` loops and UIA COM calls.

## Dragonfly BPC Fork & Kaldi Investigation

Tracing and resolving the Kaldi engine race condition in the `dragonfly-bpc-oss` fork (v1.0.0rc2) to enable testing of the UIA accessibility features.

Detailed documentation from Antigravity agent sessions:
- [kaldi_crash_explanation.md](docs/kaldi_crash_explanation.md): Explains the `destroy()` use-after-free root cause and the queue-safety patch.
- [kaldi_race_condition_answers.md](docs/kaldi_race_condition_answers.md): Explains the rule key identity, synchronous C++ allocations, and git history behind the race condition.
- [dragonfly_rule_deepdive.md](docs/dragonfly_rule_deepdive.md): A step-by-step roadmap for print-tracing how Dragonfly rules enable and disable.