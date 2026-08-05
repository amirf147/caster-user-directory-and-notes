# Ticket 015: Research Integration with OS Accessibility APIs (Issue #814)

**Type**: `wayfinder:research` (AFK)
**Status**: [CLOSED]
**Blocks**: Core Engine Threading Understanding / Non-blocking UIA

## Question
What are the requirements and historical context of Caster's plan to integrate with OS Accessibility APIs as outlined in Issue #814? 

Specifically:
1. What was the core problem that Issue #814 aimed to solve?
2. Which OS accessibility APIs and inspection tools were evaluated?
3. How did they plan to integrate this with Dragonfly's existing accessibility APIs?

## Resolution
1. **Core Problem**: Re-implementing Dragon's Select-and-Say capability and text navigation using an API, Engine, and OS-agnostic approach that is "as fast as possible". 
2. **APIs and Tools**: 
   - **Windows**: MSAA and UI Automation. Tools: Accessibility Insights for Windows (noted as best in class), aViewer, au3spy, Inspect, spy++, winspy.
   - **Linux**: AT-SPI, IA2.
   - **Mac**: Accessibility API.
3. **Integration Plan**: The goal was to build this support into `dtactions` (to support common OS actions across dictation-toolbox projects), while experimenting with integrating APIs like `pywinauto`, `Python-UIAutomation`, `WinAppDriver`, and `robotframework` directly into Dragonfly's Accessibility API design.

**Full Educational Breakdown**: [015_os_accessibility_apis_issue_814_educational_breakdown.md](../research/015_os_accessibility_apis_issue_814_educational_breakdown.md)
