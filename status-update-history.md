## Archived Status Update: Wayfinder Session & Dragonfly BPC Fork (August 2026)

### App Switching & UIA Threading Investigation (Wayfinder Session)

We recently investigated window switching and responsiveness in Caster (`app_switcher.py`). During this research, we explored COM threading mechanics (STA vs. MTA), UIA fallback mechanisms, and multi-process architectures across screen readers (NVDA), automation frameworks (Terminator, UFO), Dragonfly, and Caster core.

**Key Finding (App Switcher):** Our empirical testing of `app_switcher.py` revealed that perceived "hard freezes" during app switching were not caused by COM deadlocks or threading issues, but rather by Windows PowerShell **QuickEdit mode** pausing standard output (`stdout`) when Caster logged messages. 

*Note on Text Editing:* While `text_editing.py` and UIA-based text selection remain an interest for future exploration to build better grammars and extract value, our empirical investigation and findings so far pertain specifically to `app_switcher.py`.

We left open the possibility of building a custom out-of-process C# MCP server for experimental tool development and future AI agent compatibility. However, our next step was to conduct further empirical testing on `app_switcher.py` in-process to thoroughly double-check its real-world robustness and evaluate whether an out-of-process architecture is truly required.

#### Key Session Synthesis Documents
The research and analysis from this session have been synthesized into primary reference documents:
- **[Claude Critique: Verified Takeaways & Fact-Checked Corpus](docs/wayfinder-uia-threading/claude-critique-verified-takeaways.md)**: A fact-checked evaluation by Claude 3.5 Sonnet distilling load-bearing findings, verified Win32/UIA technical facts, and unconfirmed hypotheses across the 71-file Wayfinder corpus.
- **[Codex Context Extract: Operational Baseline](docs/wayfinder-uia-threading/codex-context-extract.md)**: A structured context synthesis by Codex mapping active constraints, core requirements, and benchmark data.
- **[Wayfinder UIA & Threading Session Directory](docs/wayfinder-uia-threading/map.md)**: Active decision tracking map, tickets, and deep-dive educational research breakdowns.
- **[ADR_001_Background_Worker_Pool.md](docs/architecture/ADR_001_Background_Worker_Pool.md)**: *(Deprecated)* Initial decision record for generic thread pool approach.
- **[Speech Stack Thread Architecture & Diagnostic Report](docs/architecture/Speech_Stack_Thread_Architecture_and_Diagnostic_Report.md)**: Initial thread architecture diagnostic report.

---

### Dragonfly BPC Fork & Kaldi Investigation

Tracing and resolving the Kaldi engine race condition in the `dragonfly-bpc-oss` fork (v1.0.0rc2) to enable testing of the UIA accessibility features.

Detailed documentation from Antigravity agent sessions:
- [kaldi_crash_explanation.md](docs/troubleshooting/kaldi_crash_explanation.md): Explains the `destroy()` use-after-free root cause and the queue-safety patch.
- [kaldi_race_condition_answers.md](docs/troubleshooting/kaldi_race_condition_answers.md): Explains the rule key identity, synchronous C++ allocations, and git history behind the race condition.
- [dragonfly_rule_deepdive.md](docs/framework_explainers/dragonfly_rule_deepdive.md): A step-by-step roadmap for print-tracing how Dragonfly rules enable and disable.

---

## Current Status (25 July 2024, see status-updates-history.md for previous status updates) 
Still using this full time, adding or modifying rules as needs arise. Switched to using the talon alphabet except a few letters, see words.txt in transformers directory. I've noticed that a lot of the transforms that I did in words.txt had to slowly be undone because they made sense in windows speech recognition because of poor recognition accuracy but as smy capabilities increased in using Caster and hs I've been increasing my command vocabulary, I've noticed that a lot of the specs are the words they are for good reason, for example because ofnot colliding with other specs or maybe just less voice straining. I'm thinking I might soon  
revert to the default spec, "bird", for jumping back one word (control + left arrow), as I have currently been using "blush" which was less misrecognized in windows speech recognition. I've noticed that it can take up to a week and sometimes longer to get used to a new spec that replaces one that you've been used to saying for a long time. It is however worth the struggle in the long run if it is an improvement in either reducing complexity or reducing voice strain. 

## Current Status (30 May 2024) 
I have added a significant portion of the core customizations that I require for enabling my full time usage of this accessibility tool. I am still switching between usage of kaldi-dragonfly-grammars, wsrmacros and this. I have noticed that there is a little noticeable latency increase when using caster as opposed to just using bare-bones dragonfly but I believe the benefits of using caster will ultimately outweigh this latency increase.

## 12 May 2024
I am still using and developing https://github.com/amirf147/kaldi-dragonfly-gammars for full handsfree computer control. I just created this repository to document/store my Caster user directory (https://caster.readthedocs.io/en/latest/readthedocs/User_Dir/Caster_User_Dir/) as I begin learning and using Caster. It may be that I eventually switch to just using Caster for my computer control needs.
