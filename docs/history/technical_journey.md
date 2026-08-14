[ 🏠 Docs Home ](../README.md) › [ 📁 History ](../README.md#history) › **Technical Journey & Recent Focus**

---

# Technical Journey & Recent Focus

Our ongoing work focuses on window switching, accessibility mechanics, and speech engine responsiveness. Below is a summary of our recent journey, ordered from current focus back to initial foundations:

### 1. Current Focus: LexiconCode Window Switching Rule Investigation
- **Active Work**: We are evaluating and documenting the window management implementation originally developed by LexiconCode, which uses dynamic grammar (`DictList`) background polling to continuously index open window titles for voice switching.
- **PR Reference**: **[Caster PR #881 (LexiconCode Window Switching)](https://github.com/dictation-toolbox/Caster/pull/881)**
- **Technical Feature Guide**: **[LexiconCode Window Switching Functionality](../features/lexicon_code_window_switching_functionality.md)**

### 2. Wayfinder Session: App Switching & UIA Threading Investigation
- **Condensed Summary**: Investigated perceived freezes in `app_switcher.py` and UIA/COM threading performance across speech stacks. Discovered through empirical testing that apparent hangs were actually caused by Windows PowerShell QuickEdit mode pausing standard output (`stdout`) during logging.
- **Key Docs & Code**:
  - Feature Guide: **[App & Window Switcher Documentation](../features/app_switcher.md)**
  - Session Index: **[Wayfinder UIA & Threading Directory](../wayfinder-uia-threading/map.md)**
  - Rule & Utility Code: **[window_switching.py](../../caster_user_content/rules/global/window_switching.py)** & **[app_switcher.py](../../caster_user_content/util/app_switcher.py)**

### 3. Historical Status & Archived Investigations
Recently updated a long abondonded file containing past status updates with deep dives into the Dragonfly BPC Fork Kaldi race condition fixes, and UIA threading synthesis at:
👉 **[Status Update History](../../status-update-history.md)**

### 4. 2-Year Git Evolution & Timeline Narrative
For the complete 27-month, 969-commit retrospective covering all 4 development eras (foundations, modularization, grammar maturity, and modern UIA architecture):
- 📜 **[Repository Timeline Document](repository_timeline.md)**


