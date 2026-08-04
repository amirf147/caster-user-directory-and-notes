# UIA Fallback Strategies: NVDA and Terminator

Microsoft UI Automation (UIA) is powerful, but many applications (especially older Win32 apps, custom-rendered electron apps, or video games) do not properly expose their UI elements to the UIA tree. When UIA fails, screen readers and automation agents need fallbacks.

## 1. NVDA's Strategy: API Cascading
NVDA handles this by implementing a robust, hierarchical fallback system for accessibility APIs. 
When it focuses a window, it tries to find the best API representation dynamically (`findBestAPIClass`). If the highest-tier API is unavailable or broken, it cascades down:

1. **Microsoft UI Automation (UIA):** The modern standard.
2. **IAccessible2 (IA2):** A powerful open-source extension to MSAA, primarily used by Firefox, Chrome, and LibreOffice.
3. **Java Access Bridge (JAB):** Specifically for Java-based desktop applications.
4. **Microsoft Active Accessibility (MSAA / IAccessible):** The legacy fallback. Almost every Windows application supports basic MSAA.

*How Caster can use this:* For our `app_switcher`, if UIA cannot find the internal tabs of a specific application, we could theoretically fall back to querying MSAA. However, implementing IA2 or JAB from scratch in Caster is likely too complex for a v1 UIA Server.

## 2. Terminator's Strategy: Low-Level Win32 Hooks
Terminator focuses on automation rather than screen reading. For applications that don't support UIA well, Terminator relies heavily on raw Win32 APIs (`user32.dll` via `windows-rs`).
Instead of relying on UIA to focus a window (which can be flaky), Terminator directly invokes `SetForegroundWindow`, `BringWindowToTop`, and `AttachThreadInput`. 

*How Caster can use this:* We should design our UIA Server so that UIA is primarily used for **reading** the UI tree (finding the tabs), but the actual **focusing** of the window is done via robust Win32 API calls (`win32gui.SetForegroundWindow`). 

*(Research conducted under Wayfinder Ticket 003)*
