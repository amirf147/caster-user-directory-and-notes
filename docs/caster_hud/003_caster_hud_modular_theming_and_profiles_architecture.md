[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](005_caster_hud_requirements_and_specifications.md) › **003: Modular Theming & Profiles Architecture**

---

> [!NOTE]
> **Document Status**: *Earlier Theming & Profile Persistence Specification (Superseded)*.  
> This document details the initial modular theming transition. For active specifications, refer to **[005: Requirements, Feature Matrix & Technical Specifications](005_caster_hud_requirements_and_specifications.md)** and **[004: Next-Iteration Modular Architecture](004_caster_hud_nextgen_modular_architecture_and_context_integration.md)**.

# 003 — Caster Heads-Up Display: Modular Theming, Profiles, Drag Mode & Frameless Resizing

**Document ID**: `CASTER-DOC-HUD-003`  
**Status**: Historical Architectural Baseline (Superseded by 004/005)  
**Target Subsystem**: `castervoice/asynch/hud/theming/`  

---

## 1. Executive Summary

This document details the transition from a monolithic GUI into a modular theming subsystem featuring:
1. **QSS Theming Engine**: Preset themes (`classic`, `frosted-dark`, `minimal-transparent`, `high-contrast`).
2. **Interactive Profile Dialog (`ProfileDialog`)**: Hotkeys (`[Enter]`, `[L]`, `[Del]`, `[Esc]`).
3. **Dedicated Drag Mode**: Accidental-click protection with `'D'` hotkey and arrow-key nudging.
4. **Frameless Edge Resizability**: Win32 hardware border hit-testing and edge resize handles.
