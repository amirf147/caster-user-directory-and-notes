[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Research ](../../README.md#wayfinder-uia--threading-research) › **UFO UIA Architecture and Fallback Strategies**

---

# UFO UIA Architecture and Fallback Strategies

This document provides a deep dive into how Microsoft's `ufo` repository (a UI automation agent framework) handles UI Automation (UIA) and fallback strategies.

## 1. Libraries and Threading
UFO is written in Python and primarily drives Windows applications using the **`pywinauto`** library. `pywinauto` itself is a wrapper around `uiautomation` and `win32` APIs.
* **Threading:** Unlike NVDA or Terminator, UFO does not appear to manage low-level COM apartments (MTA/STA) explicitly via `sys.coinit_flags` or dedicated C++ threads. It relies on `pywinauto`'s default execution model, which is typically synchronous on the calling thread. For an AI agent taking discrete actions, blocking for a few milliseconds is acceptable, unlike a screen reader (NVDA) or voice engine (Caster) that must remain responsive continuously.
* **Office Fallback:** For Microsoft Office applications, UFO bypasses UIA entirely and uses `win32com.client.Dispatch` (raw COM interop) to manipulate documents directly.

## 2. UFO's Ultimate Fallback: Vision and AI (OmniParser)
What makes UFO unique is its strategy when the UIA accessibility tree is broken, empty, or unreadable (common in web apps, games, or legacy apps).

When UIA fails, UFO falls back to **Visual Grounding** using an AI model called `OmniParser` combined with OCR (`PaddleOCR`).
1. It takes a screenshot of the window (using `pywinauto` or falling back to `PrintWindow`).
2. It sends the image to `OmniParser`.
3. The AI "looks" at the screenshot, runs OCR to find text, and detects buttons/icons visually.
4. It returns absolute bounding boxes (`x0, y0, x1, y1`) for the interactive elements.
5. UFO then uses standard mouse coordinate clicks to interact with the elements.

## Conclusion for Caster
* **Tier 1 (UIA):** Our primary approach for `app_switcher.py` should be UIA (implemented safely on an Out-of-Process Server or MTA thread).
* **Tier 2 (Fallback):** If UIA fails to find tabs, falling back to Vision/OCR (like UFO) is likely too slow for a real-time voice command. Instead, Caster should fall back to its historical method: **Hotkey Injection** (`Ctrl+Tab` cycling) combined with Win32 `SetForegroundWindow` (like Terminator).

*(Research conducted under Wayfinder Ticket 004)*
