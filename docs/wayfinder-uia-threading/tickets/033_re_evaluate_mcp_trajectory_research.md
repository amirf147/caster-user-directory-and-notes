# Ticket 033: Re-Evaluate UIA Architecture Trajectory (Voice vs. LLM)

**Type**: `wayfinder:research` (Retrospective & Alignment)
**Status**: [CLOSED]
**Blocks**: Ticket 034 (Implementation Path)

## Question
Are we going in the wrong direction by focusing on MCP (Model Context Protocol) servers designed for LLM agents? 

Specifically:
1. Is adopting an MCP server introducing unnecessary "LLM bloat" (screen scraping, OCR, 50+ tools) into what should be a deterministic, real-time voice engine?
2. Are MCP servers inherently meant for background tasks, or can they handle the instant latency required for voice command execution?
3. How do we reconcile the desire to be "LLM Ready" (allowing an AI to dynamically write Caster rules on the fly) with the need for Caster to execute those rules natively and instantly?

## Resolution
- We are **not** going in the wrong direction regarding the *technology* (C# + FlaUI) or the *protocol* (MCP over `stdio`). MCP overhead is essentially zero (~2ms).
- We **were** going in the wrong direction by trying to adopt bloated, AI-generated third-party servers (`Windows-MCP`, `desktop-pilot-mcp`). 
- **The Pivot**: We must build a bespoke "Micro MCP Server". It must strictly expose only the 3-5 macro-level tools Caster actually needs (Window Focus, Tab Listing, Element Clicking) using the official Anthropic MCP JSON schema. This makes it instantly responsive for Caster, while remaining perfectly "LLM-Ready" for future AI agents to connect to and explore.

**Full Educational Breakdown**: [033_re_evaluate_mcp_trajectory_deep_dive.md](../research/033_re_evaluate_mcp_trajectory_deep_dive.md)
