# Research: WinStasis Architecture Review and Refactoring Strategy

**Ticket:** 035
**Author:** Wayfinder Agent
**Target:** `WinStasis`

## 1. Executive Summary

A comprehensive structural review of the WinStasis project has been conducted. WinStasis is a C# CLI tool that captures and restores the window layout state of an environment, including handling Windows Virtual Desktops. 

The review identifies several critical architectural flaws—predominantly related to tight coupling and leaky abstractions—but also highlights several high-value algorithms and "secrets" (such as hybrid matching and boundary clamping) that are highly valuable for extraction into future tools (e.g., Caster Desktop Pilot MCP).

---

## 2. The "Brutal" Truth: Architectural Flaws and Anti-Patterns

### 2.1 The `Program.cs` Monolith and Leaky Abstractions
The most significant architectural flaw in WinStasis is the severe violation of the Adapter Pattern and Single Responsibility Principle (SRP) within `Program.cs` (`WinStasis/Program.cs`).

- **Duplicate P/Invokes:** Despite having a dedicated `WindowsEnvironmentAdapter` (`WinStasis/Adapters/WindowsEnvironmentAdapter.cs`) to encapsulate Win32 API calls (`user32.dll`), `Program.cs` explicitly re-defines massive amounts of P/Invoke signatures (e.g., `EnumWindows`, `GetWindowText`, `GetWindowPlacement`) starting at line 18.
- **Adapter Bypass:** The `HandleSaveCommand` method (Line 116) completely bypasses the `IWindowingEnvironment` interface and manually executes Win32 callbacks (`CaptureWindowCallback`) to build the snapshot. This renders the adapter pattern useless for the save pipeline, tightly coupling the CLI parsing directly to the OS native layer.
- **Console Coupling:** Subsystems like `VirtualDesktopHelper` (`WinStasis/VirtualDesktopHelper.cs`) and `WindowRestorer` (`WinStasis/WindowRestorer.cs`) hardcode `Console.WriteLine` for telemetry and debugging, making them impossible to test or reuse in a non-CLI context (like an MCP server).

### 2.2 Flat Data Structures
The core domain model, `WindowRecord` (`WinStasis/Models/SessionProfile.cs`), is a completely flat DTO. It mixes volatile OS state (`Hwnd`), identity heuristics (`ProcessName`, `WindowTitle`), geometry (`X`, `Y`), and workspace context (`DesktopId`) into a single layer. It also exposes raw native constants (e.g., `ShowCmd`) instead of mapping them to a domain-safe Enum.

---

## 3. High-Value Extraction ("The Secrets")

Despite the structural flaws, WinStasis contains several exceptionally well-engineered, battle-tested algorithms that *must* be salvaged.

### 3.1 Hybrid Window Matching (ADR-0001)
The `FindWindow` logic in `WindowRestorer` (`WinStasis/WindowRestorer.cs#L107`) provides a highly resilient way to track windows across intra-session drift:
1. **Fast Path:** It checks if the saved `HWND` is still alive, visible, and strictly verifies the underlying process name hasn't changed (to prevent recycled HWND collisions).
2. **Fallback Path:** If the HWND is dead (app restarted), it falls back to a First-Come, First-Served fuzzy match on `WindowTitle` + `ProcessName`. 

### 3.2 Boundary Clamping (ADR-0003)
The `ClampToNearestMonitor` algorithm (`WinStasis/WindowRestorer.cs#L139`) is crucial for multi-monitor setups. If a monitor is unplugged between a "save" and a "restore," WinStasis actively recalculates the nearest visible working area using `MonitorFromRect` and shifts the window's `X`/`Y` coordinates inside the visible boundaries. This prevents windows from being restored off-screen.

### 3.3 Undocumented Virtual Desktop COM Wrapper
`VirtualDesktopHelper.cs` uses the `Slions.VirtualDesktop` library to bypass Microsoft's UIPI restrictions. The method `MoveWindowToDesktop` (`WinStasis/VirtualDesktopHelper.cs#L103`) successfully maps internal OS GUIDs to COM objects to move windows between virtual workspaces silently.

---

## 4. Constructive Architecture Redesign

To modularize this logic for future implementations (such as a C# MCP server), the data structures and containers must be fundamentally reorganized.

### 4.1 Segregated Data Containers
The flat `WindowRecord` should be broken down into nested, logical structs to separate identity from state:

```csharp
public class WindowSnapshot
{
    // Identity - Who the window is (Used for matching)
    public WindowIdentity Identity { get; set; } 
    
    // Geometry - Where the window is
    public WindowPlacement Placement { get; set; }
    
    // Workspace - Which desktop it belongs to
    public WorkspaceState Workspace { get; set; }
    
    // Volatile State - OS specific pointers (Ignored during long-term storage)
    [JsonIgnore]
    public VolatileContext Volatile { get; set; }
}

public class WindowIdentity
{
    public string ProcessName { get; set; }
    public string Title { get; set; }
}

public class WindowPlacement
{
    public int X { get; set; }
    public int Y { get; set; }
    public int Width { get; set; }
    public int Height { get; set; }
    public WindowState State { get; set; } // Enum (Normal, Minimized, Maximized) - NOT raw ShowCmd ints
}
```

### 4.2 Module Boundaries
The logic must be segmented into distinct service boundaries using Dependency Injection:

1. **`IWindowEnvironment` (Adapter):** Solely responsible for P/Invokes. *No P/Invokes should exist outside this layer.*
2. **`IWorkspaceManager` (Adapter):** Wraps the Virtual Desktop COM logic.
3. **`ISnapshotService` (Domain):** Orchestrates the `IWindowEnvironment` to build `WindowSnapshot` objects.
4. **`IRestoreService` (Domain):** Implements the Hybrid Matching and Boundary Clamping logic. 
5. **`ILogger` (Cross-Cutting):** Injected into all services to remove `Console.WriteLine` coupling.

## 5. Conclusion
WinStasis contains the exact Win32 algorithms needed to build a powerful window management MCP server. By extracting the Hybrid Matching and Boundary Clamping logic, and wrapping them in the proposed segregated data containers, we can build a highly modular, testable, and robust accessibility tool.
