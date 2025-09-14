; I started trying to create this with GPT-5 thinking through several different iterations
; but then I created a summary prompt with GPT-5 and pasted that along with the not fully working
; code to Gemini 2.5 Pro and it gave me this after 2 prompts

#Requires AutoHotkey v2.0
#SingleInstance Force

; --- Config ---
F15_HoldDelay := 200     ; ms to treat F15 as hold (drag)
F13_HoldDelay := 500     ; ms long-press to reset

; Scrolling configuration
Scroll_HoldDelay := 250  ; ms to hold before continuous scrolling starts
Scroll_RepeatRate := 50  ; ms between each scroll tick (smaller is faster)

; --- State ---
global F15_FirstTapPending := true
global F15_HoldActive := false
global F15_HoldStart := 0

global F13_IsDown := false
global F13_HoldStart := 0
global F13_LongHoldActionFired := false

; State variables for scrolling
global F14_IsDown := false
global F14_HoldActionFired := false
global F14_HoldStart := 0 ; <-- FIX: Added variable to store start time
global F16_IsDown := false
global F16_HoldActionFired := false
global F16_HoldStart := 0 ; <-- FIX: Added variable to store start time

showCue(msg, dur:=800) {
    MouseGetPos &mx, &my
    ToolTip msg, mx+20, my+20
    SetTimer () => ToolTip(), -dur
}

; ---------------- F15 (Left Click / Drag) ----------------
*F15::
{
    global F15_HoldDelay, F15_HoldStart
    F15_HoldStart := A_TickCount
    SetTimer F15_HoldTimer, -F15_HoldDelay
}

*F15 up::
{
    global F15_FirstTapPending, F15_HoldActive
    SetTimer F15_DragStatus, 0
    ToolTip()
    SetTimer F15_HoldTimer, 0

    if F15_HoldActive {
        F15_HoldActive := false
        Send "{LButton up}"
        showCue("← Drag End")
        return
    }
    if F15_FirstTapPending {
        Send "{F11}"
        F15_FirstTapPending := false
        showCue("F11 (first tap)")
    } else {
        Send "{LButton}"
        showCue("Left Click")
    }
}

F15_HoldTimer() {
    global F15_HoldActive, F15_HoldStart
    if GetKeyState("F15","P") {
        F15_HoldActive := true
        Send "{LButton down}"
        showCue("← Drag Start")
        SetTimer F15_DragStatus, 50
    }
}

F15_DragStatus() {
    global F15_HoldStart
    elapsed := A_TickCount - F15_HoldStart
    MouseGetPos &mx, &my
    ToolTip "Dragging... " elapsed " ms", mx+20, my+20
}

; ---------------- F13 (Right Click / Reset) ----------------
*F13::
{
    global F13_IsDown, F13_HoldStart, F13_LongHoldActionFired
    if F13_IsDown
        return
    F13_IsDown := true
    F13_LongHoldActionFired := false
    F13_HoldStart := A_TickCount
    SetTimer F13_Monitor, 50
}

F13_Monitor() {
    global F13_IsDown, F13_HoldStart, F13_HoldDelay, F13_LongHoldActionFired, F15_FirstTapPending
    if GetKeyState("F13", "P") {
        elapsed := A_TickCount - F13_HoldStart
        if (!F13_LongHoldActionFired && elapsed >= F13_HoldDelay) {
            F13_LongHoldActionFired := true
            F15_FirstTapPending := true
            Send "{F11}"
            showCue("⟳ Reset + F11")
        }
    } else {
        SetTimer F13_Monitor, 0
        if !F13_LongHoldActionFired {
            Send "{RButton}"
            showCue("Right Click")
        }
        F13_IsDown := false
    }
}

; ---------------- F14 & F16 (Scrolling) ----------------

; --- F14 Scroll Down ---
*F14::
{
    global F14_IsDown, F14_HoldActionFired, F14_HoldStart
    if F14_IsDown
        return
    F14_IsDown := true
    F14_HoldActionFired := false
    F14_HoldStart := A_TickCount ; <-- FIX: Capture the start time here
    SetTimer F14_Monitor, 50
}

F14_Monitor()
{
    global F14_IsDown, F14_HoldActionFired, F14_HoldStart, Scroll_HoldDelay
    if GetKeyState("F14", "P") {
        ; Key is held down. Check if hold time has elapsed.
        elapsed := A_TickCount - F14_HoldStart ; <-- FIX: Calculate elapsed time correctly
        if !F14_HoldActionFired && elapsed >= Scroll_HoldDelay {
            F14_HoldActionFired := true
            F14_ContinuousScroll()
            SetTimer F14_ContinuousScroll, Scroll_RepeatRate
        }
    } else {
        ; Key has been released.
        SetTimer F14_Monitor, 0
        SetTimer F14_ContinuousScroll, 0
        if !F14_HoldActionFired {
            Send "{WheelDown}"
        }
        F14_IsDown := false
    }
}

F14_ContinuousScroll() {
    Send "{WheelDown}"
}

; --- F16 Scroll Up ---
*F16::
{
    global F16_IsDown, F16_HoldActionFired, F16_HoldStart
    if F16_IsDown
        return
    F16_IsDown := true
    F16_HoldActionFired := false
    F16_HoldStart := A_TickCount ; <-- FIX: Capture the start time here
    SetTimer F16_Monitor, 50
}

F16_Monitor()
{
    global F16_IsDown, F16_HoldActionFired, F16_HoldStart, Scroll_HoldDelay
    if GetKeyState("F16", "P") {
        ; Key is held down. Check if hold time has elapsed.
        elapsed := A_TickCount - F16_HoldStart ; <-- FIX: Calculate elapsed time correctly
        if !F16_HoldActionFired && elapsed >= Scroll_HoldDelay {
            F16_HoldActionFired := true
            F16_ContinuousScroll()
            SetTimer F16_ContinuousScroll, Scroll_RepeatRate
        }
    } else {
        ; Key has been released.
        SetTimer F16_Monitor, 0
        SetTimer F16_ContinuousScroll, 0
        if !F16_HoldActionFired {
            Send "{WheelUp}"
        }
        F16_IsDown := false
    }
}

F16_ContinuousScroll() {
    Send "{WheelUp}"
}