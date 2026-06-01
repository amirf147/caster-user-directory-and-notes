# App & Window Switcher

The `app_switcher.py` script provides robust, multi-strategy window switching, focusing, and tab navigation via voice commands.

## Features

- **Multi-Tier Failsafe**:
  1. Primary focus via PyWinAuto and Win32 APIs.
  2. Fallback to UI Automation (UIA) clicks on the Taskbar.
  3. Fallback to keyboard macros (e.g., `Win + T`).
- **Tab Switching Support**: Allows grouping certain apps like web browsers and IDEs to smoothly transition between tabs (Ctrl+Tab, Ctrl+PgDn).
- **Virtual Desktop Awareness**: Seamlessly switches to windows across virtual desktops, provided `pyvda` is installed.
- **Window Aliasing**: Ability to define custom names for windows (`aliases`) allowing you to dynamically name tabs and windows for fast navigation later.

## Usage

This utility is used by voice commands directly to switch, find, and manage focus across your workspace effortlessly.
