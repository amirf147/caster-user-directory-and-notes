[ 🏠 Docs Home ](../../README.md) › [ 📁 Wayfinder Tickets ](../../README.md#wayfinder-uia--threading-research) › **Ticket 018: Research UIAutomation Microsoft Doc...**

---

# Ticket 018: Research UIAutomation Microsoft Documentation

**Type**: `wayfinder:research` (AFK)
**Status**: Open / Unclaimed
**Blocks**: Codebase evaluation of `uiautomation-mcp`

## Question
Before we can accurately evaluate the `uiautomation-mcp` server, we must fully understand the official Microsoft documentation and standards for UI Automation. What is the correct, Microsoft-recommended way to use UIA?

Specifically:
1. What are the core UIA patterns, element trees, and property fetching mechanics documented by Microsoft?
2. What does Microsoft say about COM threading requirements, event handling, and thread safety when utilizing `System.Windows.Automation`?
3. How are `CacheRequest` optimizations supposed to be implemented according to the official documentation?

## Next Steps
- Aggregate and summarize all relevant UI Automation Microsoft Learn documentation.
- Compile a comprehensive list of locations, rules, and best practices for UIA usage to serve as a grading rubric for evaluating existing codebases.
