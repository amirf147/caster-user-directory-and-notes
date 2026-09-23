[ 🏠 Docs Home ](../README.md) › [ 📁 Caster HUD ](005_caster_hud_requirements_and_specifications.md) › **003: Modular Theming & Profiles Architecture**

---

> [!NOTE]
> **Document Status**: *Initial Theming & Profile Specification (Superseded)*.  
> Formalized into the active runtime specification in **[005: Requirements, Feature Matrix & Technical Specifications](005_caster_hud_requirements_and_specifications.md)** and **[014: Out-of-Process Desktop Observation](014_out_of_process_desktop_observation_and_adce_hud_realization.md)**.

# 003: Caster Heads-Up Display: Modular Theming, Profiles, Drag Mode & Frameless Resizing

**Document ID**: `CASTER-DOC-HUD-003`  
**Status**: Initial Architecture (Superseded by 005 and 014)  
**Target Subsystem**: `castervoice/asynch/hud/theming/`  

---

## 1. Executive Summary

This document details the transition from a monolithic GUI into a modular theming subsystem featuring:
1. **QSS Theming Engine**: Preset themes (`classic`, `frosted-dark`, `minimal-transparent`, `high-contrast`).
2. **Interactive Profile Dialog (`ProfileDialog`)**: Hotkeys (`[Enter]`, `[L]`, `[Del]`, `[Esc]`).
3. **Dedicated Drag Mode**: Accidental-click protection with `'D'` hotkey and arrow-key nudging.
4. **Frameless Edge Resizability**: Win32 hardware border hit-testing and edge resize handles.
