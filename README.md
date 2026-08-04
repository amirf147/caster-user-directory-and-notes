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

## Dragonfly BPC Fork & UIA Investigation

Tracing and resolving the Kaldi engine race condition in the `dragonfly-bpc-oss` fork (v1.0.0rc2) to enable testing of the UIA accessibility features.

Detailed documentation from Antigravity agent sessions:
- [kaldi_crash_explanation.md](docs/kaldi_crash_explanation.md): Explains the `destroy()` use-after-free root cause and the queue-safety patch.
- [kaldi_race_condition_answers.md](docs/kaldi_race_condition_answers.md): Explains the rule key identity, synchronous C++ allocations, and git history behind the race condition.
- [dragonfly_rule_deepdive.md](docs/dragonfly_rule_deepdive.md): A step-by-step roadmap for print-tracing how Dragonfly rules enable and disable.