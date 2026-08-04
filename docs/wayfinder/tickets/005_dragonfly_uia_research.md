# Ticket 005: Research Dragonfly UIA and Threading Architecture

**Type**: `wayfinder:research` (AFK)
**Status**: Open / Unclaimed
**Blocks**: Architecture Placement Decision

## Question
How does the `dragonfly` framework handle Microsoft UI Automation (UIA) and threading?

Specifically:
1. Does Dragonfly have an existing UIA implementation? If so, how does it initialize COM (STA vs MTA) and manage threads?
2. How does the core threading model of Dragonfly work (e.g., the engine loop)?
3. Can we leverage, extend, or fix Dragonfly's UIA implementation instead of building a completely new server in Caster?
