# Ticket 004: Research UFO UIA Architecture and Fallback Strategies

**Type**: `wayfinder:research` (AFK)
**Status**: [CLOSED]
**Blocks**: Architecture Decision (In-Process vs Out-of-Process)

## Question
How does the `ufo` repository (Microsoft's UI automation agent framework) handle UIA interactions and what fallback mechanisms does it use?

Specifically:
1. What libraries does it use for UIA?
2. Does it use dedicated threads?
3. What is its fallback strategy when UIA fails?

## Resolution
1. **Libraries:** UFO exclusively uses `pywinauto` (which wraps UIA) and `win32com.client` for direct Microsoft Office interaction.
2. **Threading:** UFO relies on `pywinauto`'s synchronous execution model, generally running on the main thread because it acts as a discrete AI agent rather than a continuously responsive daemon (like Caster or NVDA).
3. **Ultimate Fallback (Vision & AI):** When the UIA tree is broken, UFO captures screenshots (via `PrintWindow`) and passes them through an AI vision model (`OmniParser`) and OCR (`PaddleOCR`) to literally "look" at the screen and find bounding boxes. 

**Full Educational Breakdown**: [004_ufo_uia_architecture_educational_breakdown.md](../research/004_ufo_uia_architecture_educational_breakdown.md)
