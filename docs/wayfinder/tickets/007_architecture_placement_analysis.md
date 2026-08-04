# Ticket 007: Architecture Placement Analysis (Dragonfly vs Caster)

**Type**: `wayfinder:research` (AFK)
**Status**: Open / Unclaimed
**Blocks**: Architecture Decision (In-Process vs Out-of-Process), Implementation Plan

## Question
Based on the research from Tickets 005 (Dragonfly) and 006 (Caster), where is the most architecturally sound place to build the new UIA Server or MTA Thread?

Specifically:
1. Should this be built directly into Caster as a custom service/daemon?
2. Should it be built into the Dragonfly core engine so that all Dragonfly users benefit from safe, non-blocking UIA?
3. What are the trade-offs of each approach?
