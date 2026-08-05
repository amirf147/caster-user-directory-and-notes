# Ticket 016: Research dtactions UIA Architecture

**Type**: `wayfinder:research` (AFK)
**Status**: [CLOSED]
**Blocks**: Core Engine Threading Understanding / Non-blocking UIA

## Question
How does the `dtactions` library implement UI Automation (UIA) and COM threading? 
As per Issue #814, `dtactions` was designated to become the central repository for shared OS accessibility actions across the dictation-toolbox ecosystem (Dragonfly, Caster, Unimacro, Vocola). Does it fulfill this role, and if so, how does it handle STA/MTA threading for UIA?

## Resolution
1. **Zero UIA Presence**: Despite the roadmap laid out in Issue #814 (to move accessibility APIs into `dtactions`), `dtactions` currently contains absolutely **zero** UI Automation (UIA) code, `comtypes` references, or `pywinauto` dependencies. 
2. **Legacy Implementations**: The library strictly relies on legacy, synchronous methods for OS interaction. This includes `win32gui`/`win32con` for window handles, `SendInput` for simulated keystrokes (Vocola compatibility), clipboard manipulations, and `AutoHotkey` scripts.
3. **Threading Model**: Because there is no UIA or COM initialization (`CoInitializeEx`), there is no concept of an STA or MTA thread within `dtactions`. All functions are executed synchronously on the caller's thread (typically the main voice engine thread).
4. **Engine Hard-Lock (Dragon vs Kaldi)**: `dtactions` is tightly coupled to **Dragon NaturallySpeaking** via direct `import natlink` calls in core modules (`uniutils.py`). It does **not** work natively with Kaldi, Vosk, Whisper, or WSR backends. Dragonfly, by contrast, is engine-agnostic.

**Full Educational Breakdown**: [016_dtactions_uia_usage_educational_breakdown.md](../research/016_dtactions_uia_usage_educational_breakdown.md)
