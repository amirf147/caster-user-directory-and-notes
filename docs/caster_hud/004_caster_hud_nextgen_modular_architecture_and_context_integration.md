[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](005_caster_hud_requirements_and_specifications.md) › **004: Next-Iteration Modular Architecture, Reactive State & Dynamic UX Indications**

---

> [!NOTE]
> **Document Status**: *Exploratory Architecture Blueprint (Superseded)*.  
> Formalized into the active runtime specification in **[005: Requirements, Feature Matrix & Technical Specifications](005_caster_hud_requirements_and_specifications.md)**, **[009: Clean Architecture Synthesis](009_caster_hud_architectural_review_and_clean_architecture_synthesis.md)**, and **[014: Out-of-Process Desktop Observation](014_out_of_process_desktop_observation_and_adce_hud_realization.md)**.

# 004: Caster Heads-Up Display: Next-Iteration Modular Architecture, Reactive State & Dynamic UX Indications

**Document ID**: `CASTER-DOC-HUD-004`  
**Status**: Exploratory Architecture Blueprint (Superseded by 005, 009, and 014)  
**Target Subsystem**: `castervoice/asynch/hud/` & `castervoice/lib/settings.py`  
**Authors**: Antigravity Principal Architecture Team (Pair Programming with Amir Farhadi)  

---

## 1. Executive Summary & Design Vision

The **Caster Heads-Up Display (HUD)** provides real-time visual feedback for hands-free computer control, speech recognition, and voice coding.

Key architectural pillars:
1. **Preserve Caster's Native Identity**: Dragonfly grammar engine integration and `settings.toml` configuration under `[hud]`.
2. **Zero-Overhead Dynamic UX Indications**:
   - 🟢 **Green Border**: Listening / Awake (`"caster on"`).
   - 🔴 **Red Border**: Sleeping (`"caster sleep"`).
   - **Safety State Priority**: $\text{Mic State (Red/Green)} \succ \text{Drag Mode (Amber)} \succ \text{Window Focus (Blue)}$.
3. **Ultra-Slim Container Hit-Testing (25px–30px Optimization)**:
   - Horizontal margins: 6px (`HTLEFT`, `HTRIGHT`).
   - Vertical margins: 3px (`HTTOP`, `HTBOTTOM`).
4. **Descender-Safe Single-Line Text Alignment**:
   - Zero-padding line-height clamping to prevent descender clipping (`g`, `y`, `p`, `q`).
5. **Robust Default Fallbacks**:
   - Deep dictionary fallback merger (`DEFAULT_HUD_CONFIG`).
6. **Resilient Non-Blocking Async IPC Pipeline**:
   - `AsyncTelemetryPublisher` with drop-oldest queue policy ($< 0.001\text{ ms}$ latency).
   - Strict `SignalBridge` isolation to main Qt GUI thread.
7. **Pluggable Context Adapters**:
   - Standalone autonomy with optional dynamic context integration (ADCE).
