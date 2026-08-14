[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Tickets ](../../README.md#wayfinder-uia--threading-research) › **Ticket 013: Research UIAutomationClient Auxilia...**

---

# Ticket 013: Research UIAutomationClient Auxiliary DLL Architecture

**Type**: `wayfinder:research` (AFK)
**Status**: [CLOSED]
**Blocks**: Architecture Placement Decision

## Question
How does `UIAutomationClient` handle UIA threading, window focus, and COM lifecycle in Windows?

Specifically:
1. Does this library implement UIA COM interfaces directly?
2. What role does it play in high-performance UI automation?
3. How does it manage GDI+ and DPI awareness?

## Resolution
1. **No Direct UIA**: Despite its name, this repository is a C++ auxiliary DLL exposing GDI+ image processing (`GdiplusStartup`) and window screen captures via FFI, leaving UIA COM interop to Python.
2. **No COM Threading**: Does not invoke `CoInitializeEx`; delegates all COM lifecycle and apartment rules to the calling parent process.
3. **DPI Fallback**: Dynamically loads `Shcore.dll` at runtime via `LoadLibraryW` to set DPI awareness safely across legacy and modern OS versions.

**Full Educational Breakdown**: [013_uiautomationclient_uia_educational_breakdown.md](../research/013_uiautomationclient_uia_educational_breakdown.md)
