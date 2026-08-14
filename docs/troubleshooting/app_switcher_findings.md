[ 🏠 Docs Home ](../README.md) › [ 📁 Troubleshooting ](../README.md#troubleshooting--diagnostics) › **App Switcher Findings**

---

# App Switcher Findings

## Issue: Windows PowerShell (Caster Status Window) Not Found
**Date**: 2026-08-10

### Overview
When attempting to switch to the "Windows PowerShell" application (which corresponds to the Caster Status Window), the `app_switcher` reported: `"No windows found for 'Windows Powershell'."`

This occurred despite the logger indicating that it had matched a window:
```
[AppSwitcher:DEBUG] App matched for 'Caster: Status Window (Dragonfly + Kaldi Latest)' (HWND 26546206). Checking desktop ID...
[AppSwitcher:DEBUG] get_window_desktop_id() calling AppView for HWND 26546206...
[AppSwitcher:DEBUG] AppView for HWND 26546206 returned {C2DDEA68-66F2-4CF9-8264-1BFD00FBBBAC} in 1.01ms
No windows found for 'Windows Powershell'.
```

### Potential Cause
The current implementation of `switch_to_app` only keeps a matched window if its `win_desktop_id` precisely matches the `current_desktop_id`. In this case, the PyVDA `AppView` returned a desktop ID that did not match the current virtual desktop.

**User Hypothesis**: 
It is highly likely that this behavior is related to the Caster Status Window being a **pinned item** (meaning it is set to appear on *all* virtual desktops). The PyVDA library might return a specific, non-matching GUID (or otherwise get confused) when queried for the desktop ID of a pinned window. We should not make any definitive assumptions on the diagnosis until further research is conducted into how PyVDA handles pinned items.

### Previous Attempted Fix (Reverted)
Before this hypothesis was noted, an attempted fix was made to the `app_switcher.py` code. The idea was to keep track of matched windows on the current desktop AND matched windows on other desktops, and then concatenate the two lists (prioritizing the current desktop). 

```python
    current_desktop_matches = []
    other_desktop_matches = []

    for hwnd, title_text in windows:
        if extract_app_name(title_text).lower() in app_names_lc:
            if current_desktop_id:
                win_desktop_id = os_env.get_window_desktop_id(hwnd)
                if win_desktop_id == current_desktop_id or win_desktop_id is None:
                    current_desktop_matches.append((hwnd, title_text))
                else:
                    other_desktop_matches.append((hwnd, title_text))
            else:
                current_desktop_matches.append((hwnd, title_text))
                
    matching_windows = current_desktop_matches + other_desktop_matches
```
This fix was **reverted** in order to keep the codebase clean while the behavior of pinned windows in PyVDA is properly researched.
