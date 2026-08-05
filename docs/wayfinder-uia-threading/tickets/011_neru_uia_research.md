# Ticket 011: Research neru UIA Architecture

**Type**: `wayfinder:research` (AFK)
**Status**: [CLOSED]
**Blocks**: Architecture Placement Decision

## Question
How does `neru` handle UIA threading, window focus, and COM lifecycle in Windows?

Specifically:
1. How does it invoke UIA in Go without CGO overhead?
2. What COM apartment threading model (STA vs MTA) does it use?
3. How does it manage COM element memory and lifecycle to avoid leaks?

## Resolution
1. **Raw VTables**: Invokes COM interfaces directly via raw vtable slot indices using `syscall.SyscallN` to avoid CGO overhead.
2. **MTA Threading**: Explicitly initializes COM in MTA (`coinitMultithreaded = 0x0`) and locks goroutines to OS threads (`runtime.LockOSThread()`) to avoid STA message pump deadlocks.
3. **Shallow Offline Trees**: Instantly copies simple properties into Go structs and releases COM pointers immediately, ensuring no lingering COM memory leaks.

**Full Educational Breakdown**: [011_neru_uia_educational_breakdown.md](../research/011_neru_uia_educational_breakdown.md)
