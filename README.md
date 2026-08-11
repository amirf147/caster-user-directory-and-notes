# Caster User Directory

Welcome to my Caster user directory. Caster is an extension to the Dragonfly framework that allows you to control your computer with voice commands. Here I have all my custom commands and grammars for automating my workflows and speeding up voice computing.

## .agents Folder
This folder contains workflows and configuration files specifically for the **Antigravity** editor.

## Tools & Workflows

Here are the various tools and scripts configured in this environment:

- **[Top Desktop Voice Automations](docs/features/top_voice_automations.md)**: Curated showcase of top-tier desktop, web, and system voice automations for workflow demos and video showcases.
- **[Ideas Emerging From This Caster Journey](docs/legacy_notes/ideas.md)**: Ongoing brainstorming document for modular architectural components and accessibility primitives.
- **[Foot Pedal & XML-RPC IPC Bridge](docs/features/foot_pedal.md)**: Hardware debouncing, smart tap/drag/scroll control for the Olympus RS31H foot pedal, integrated with a local XML-RPC IPC bridge for thread-safe hands-free Caster microphone toggling.
- **[App & Window Switcher](docs/features/app_switcher.md)**: Failsafe and workspace-aware window management to switch apps and tabs by voice.
- **[LexiconCode Window Switching Functionality](docs/features/lexicon_code_window_switching_functionality.md)**: Dynamic grammar `DictList` polling architecture and troubleshooting analysis for window switching.

## In-Progress Documentation & Note-Taking

There is a loosely organized collection of notes and documentation that is still pending better consolidation and further improvement. You can find the index for this reference material here:
👉 **[Documentation Index](docs/README.md)**

## Technical Journey & Recent Focus

Our ongoing work focuses on window switching, accessibility mechanics, and speech engine responsiveness. Below is a summary of our recent journey, ordered from current focus back to initial foundations:

### 1. Current Focus: LexiconCode Window Switching Rule Investigation
- **Active Work**: We are evaluating and documenting the window management implementation originally developed by LexiconCode, which uses dynamic grammar (`DictList`) background polling to continuously index open window titles for voice switching.
- **PR Reference**: **[Caster PR #881 (LexiconCode Window Switching)](https://github.com/dictation-toolbox/Caster/pull/881)**
- **Technical Feature Guide**: **[LexiconCode Window Switching Functionality](docs/features/lexicon_code_window_switching_functionality.md)**

### 2. Wayfinder Session: App Switching & UIA Threading Investigation
- **Condensed Summary**: Investigated perceived freezes in `app_switcher.py` and UIA/COM threading performance across speech stacks. Discovered through empirical testing that apparent hangs were actually caused by Windows PowerShell QuickEdit mode pausing standard output (`stdout`) during logging.
- **Key Docs & Code**:
  - Feature Guide: **[App & Window Switcher Documentation](docs/features/app_switcher.md)**
  - Session Index: **[Wayfinder UIA & Threading Directory](docs/wayfinder-uia-threading/map.md)**
  - Rule & Utility Code: **[window_switching.py](caster_user_content/rules/global/window_switching.py)** & **[app_switcher.py](caster_user_content/util/app_switcher.py)**

### 3. Historical Status & Archived Investigations
Recently updated a long abondonded file containing past status updates with deep dives into the Dragonfly BPC Fork Kaldi race condition fixes, and UIA threading synthesis at:
👉 **[Status Update History](status-update-history.md)**