import pyautogui

def title(window_title):
    pyautogui.getWindowsWithTitle(window_title)[0].activate()