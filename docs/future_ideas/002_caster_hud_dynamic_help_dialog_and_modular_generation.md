[ 🏠 Docs Home ](../README.md) › [ 💡 Future Ideas ](001_caster_help_rule_and_context_aware_assist_architecture.md) › **002: Dynamic Help Dialog Sizing & Modular HTML Generation**

---

# 002 — Dynamic Help Dialog Sizing & Modular HTML Generation

**Document ID**: `CASTER-DOC-FUT-002`  
**Status**: Future Architecture & Engineering Design Concept  
**Target Subsystem**: `castervoice/asynch/hud/ui/dialogs/help_dialog.py`  
**Authors**: Antigravity Principal Architecture Team (Pair Programming with Amir Farhadi)  

---

## 1. Concept Overview

Currently, `HelpDialog` renders static HTML tables formatted with voice command mappings and uses fixed initial dimensions (600x520).

In future iterations, we can evolve `HelpDialog` to be **dynamically sized** and **modularly generated**:
1. **Introspected Command Discovery**:
   - Rather than hardcoding HTML strings, `HelpDialog` dynamically introspects `CasterRule.mapping` and registered XML-RPC endpoints to generate the command reference table automatically.
2. **Context-Aware Dynamic Sizing**:
   - Automatically calculates ideal window geometry based on the user's current display DPI, font size, and table row count.
3. **Interactive Search & Filter**:
   - Includes a lightweight top filter bar to let users search through HUD commands and keybindings in real-time.

*Recorded in `docs/future_ideas/002_caster_hud_dynamic_help_dialog_and_modular_generation.md`.*
