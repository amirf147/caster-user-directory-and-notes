; AutoHotkey v2 - Event-Driven Foot Pedal Script
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
global F15_ComboFired := false

global F13_IsDown := false
global F13_HoldStart := 0
global F13_LongHoldActionFired := false
global F13_ComboFired := false

; State variables for scrolling
global F14_IsDown := false
global F14_HoldActionFired := false
global F14_HoldStart := 0
global F16_IsDown := false
global F16_HoldActionFired := false
global F16_HoldStart := 0

; Persistent WinHTTP client instance for zero-allocation request dispatch
global g_WhrClient := ""

getWhrClient() {
    global g_WhrClient
    if (g_WhrClient == "") {
        try {
            g_WhrClient := ComObject("WinHttp.WinHttpRequest.5.1")
            g_WhrClient.SetTimeouts(200, 200, 200, 200)
        } catch {
            g_WhrClient := ""
        }
    }
    return g_WhrClient
}

showCue(msg, dur:=800) {
    MouseGetPos &mx, &my
    ToolTip msg, mx+20, my+20
    SetTimer () => ToolTip(), -dur
}

toggleCaster() {
    whr := getWhrClient()
    if (whr == "") {
        try {
            whr := ComObject("WinHttp.WinHttpRequest.5.1")
            whr.SetTimeouts(200, 200, 200, 200)
        } catch Error as err {
            showCue("❌ Caster Toggle Failed: " . err.Message, 1000)
            return
        }
    }

    try {
        whr.Open("POST", "http://127.0.0.1:8341/", false)
        whr.SetRequestHeader("Content-Type", "text/xml")
        xmlData := "<?xml version='1.0'?><methodCall><methodName>toggle_mic_mode</methodName><params></params></methodCall>"
        whr.Send(xmlData)
        showCue("🎤 Caster Mic Toggled")
    } catch Error as err {
        showCue("❌ Caster Toggle Failed: " . err.Message, 1000)
    }
}


; ---------------- F15 (Left Click / Drag / Right Click Chord) ----------------
*F15::
{
    global F15_HoldDelay, F15_HoldStart, F15_ComboFired, F13_IsDown, F13_ComboFired
    if F13_IsDown || GetKeyState("F13", "P") {
        F13_ComboFired := true
        F15_ComboFired := true
        Send "{RButton}"
        showCue("Right Click")
        return
    }
    F15_ComboFired := false
    F15_HoldStart := A_TickCount
    SetTimer F15_HoldTimer, -F15_HoldDelay
}

*F15 up::
{
    global F15_FirstTapPending, F15_HoldActive, F15_ComboFired
    SetTimer F15_DragStatus, 0
    ToolTip()
    SetTimer F15_HoldTimer, 0

    if F15_ComboFired {
        F15_ComboFired := false
        return
    }

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

; ---------------- F13 (Caster Toggle / Reset) - Event-Driven ----------------
*F13::
{
    global F13_IsDown, F13_HoldStart, F13_LongHoldActionFired, F13_ComboFired, F13_HoldDelay
    if F13_IsDown
        return
    F13_IsDown := true
    F13_LongHoldActionFired := false
    F13_ComboFired := false
    F13_HoldStart := A_TickCount
    SetTimer F13_LongHoldTimer, -F13_HoldDelay
}

*F13 up::
{
    global F13_IsDown, F13_LongHoldActionFired, F13_ComboFired
    SetTimer F13_LongHoldTimer, 0
    if !F13_IsDown
        return
    F13_IsDown := false

    if F13_ComboFired {
        F13_ComboFired := false
        return
    }

    if !F13_LongHoldActionFired {
        toggleCaster()
    }
}

F13_LongHoldTimer() {
    global F13_IsDown, F13_LongHoldActionFired, F13_ComboFired, F15_FirstTapPending
    if F13_IsDown && !F13_ComboFired {
        F13_LongHoldActionFired := true
        F15_FirstTapPending := true
        Send "{F11}"
        showCue("⟳ Reset + F11")
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
    F14_HoldStart := A_TickCount
    SetTimer F14_Monitor, 50
}

F14_Monitor()
{
    global F14_IsDown, F14_HoldActionFired, F14_HoldStart, Scroll_HoldDelay
    if GetKeyState("F14", "P") {
        elapsed := A_TickCount - F14_HoldStart
        if !F14_HoldActionFired && elapsed >= Scroll_HoldDelay {
            F14_HoldActionFired := true
            F14_ContinuousScroll()
            SetTimer F14_ContinuousScroll, Scroll_RepeatRate
        }
    } else {
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
    F16_HoldStart := A_TickCount
    SetTimer F16_Monitor, 50
}

F16_Monitor()
{
    global F16_IsDown, F16_HoldActionFired, F16_HoldStart, Scroll_HoldDelay
    if GetKeyState("F16", "P") {
        elapsed := A_TickCount - F16_HoldStart
        if !F16_HoldActionFired && elapsed >= Scroll_HoldDelay {
            F16_HoldActionFired := true
            F16_ContinuousScroll()
            SetTimer F16_ContinuousScroll, Scroll_RepeatRate
        }
    } else {
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
