<!--
SPDX-License-Identifier: Apache-2.0
Copyright (c) 2024-2026 Amir Farhadi
-->

[ 🏠 Docs Home ](../README.md) › [ 📁 Framework Explainers ](../README.md#framework-explainers) › **Caster TreeRule Practical Candidates & Refactoring Guide**

---

# Caster TreeRule Practical Candidates, Refactoring Guide, and Workspace Implementations

**Document ID**: `CASTER-DOC-EXP-005`  
**Status**: Practical Engineering Reference and Rule Refactoring Catalog  
**Target Subsystems**: `caster_user_content/rules/apps/cli/`, `caster_user_content/rules/global/`, `castervoice/lib/merge/selfmod/tree_rule/`  
**Authors**: Antigravity Principal Architecture Team (Pair Programming with Amir Farhadi)  

---

## 1. Executive Summary

While the foundational explainer [`noderule_and_treerule_architecture.md`](noderule_and_treerule_architecture.md) covers the theoretical mechanics of stateful grammar trees, this document provides concrete, production-ready refactoring implementations tailored to active voice rules in this workspace.

Flat mapping rules (`MappingRule` and `MergeRule`) with extensive choices (`Choice`) or large spec counts increase speech recognition perplexity and force users to speak long composite phrases in a single breath (e.g., `"dock run nathan"` or `"dock compose up"`). Refactoring these into `TreeRule` hierarchies narrows the active command space to 3 to 6 specs per step, reducing engine load and enabling structured visual navigation in the Caster HUD.

---

## 2. Refactoring Candidate Evaluation Matrix

The following table reviews the primary rule files in `caster_user_content/rules/` to identify where `TreeRule` delivers tangible benefits versus where flat rules should remain.

| Rule File | Current Mechanism | Candidate Fit | Technical Rationale |
| :--- | :--- | :--- | :--- |
| [`apps/cli/cli_support.py`](../../caster_user_content/rules/apps/cli/cli_support.py) | Flat `Choice` dictionaries (`DOCKER_COMMANDS`, `OLLAMA_COMMANDS`). | **High** | High command density (20+ commands per tool) with clear object-verb hierarchies (`container`, `image`, `compose`, `volume`). |
| [`global/global_nonccr_extended.py`](../../caster_user_content/rules/global/global_nonccr_extended.py) | Flat `MappingRule` with 50+ mixed OS/utility commands. | **Medium** | Display scaling, brightness tiers, and administrative tools naturally group into a `system` command tree. |
| [`global/markdown.py`](../../caster_user_content/rules/global/markdown.py) | Dynamic lambda functions for table rows and breaks. | **Medium** | Multi-stage document generation (table columns → headers → rows) benefits from sequential step transitions. |
| [`apps/vscode/ide_terminal.py`](../../caster_user_content/rules/apps/vscode/ide_terminal.py) | `MappingRule` gated by ADCE `is_ide_terminal_focused`. | **Low to Medium** | Quick terminal actions (`clear`, `kill terminal`, `cargo check`) require instant single-breath execution; Git subcommands can use a tree. |
| [`global/window_switching.py`](../../caster_user_content/rules/global/window_switching.py) | Win32 programmatic focus hooks and taskbar index mapping. | **Zero (Anti-pattern)** | Window switching must execute with sub-millisecond single-utterance latency; modal trees add unacceptable navigation friction. |

---

## 3. Production Candidate 1: Docker CLI TreeRule

### Current Baseline Problem
In [`apps/cli/powershell/powershell.py`](../../caster_user_content/rules/apps/cli/powershell/powershell.py), Docker commands are exposed via `"dock <docker_command>"` with a flat dictionary of 24 items in `cli_support.py`. The engine must constantly evaluate all 24 potential endings simultaneously.

### TreeRule Implementation

```python
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024-2026 Amir Farhadi

from castervoice.lib.actions import Key, Text
from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.selfmod.tree_rule.tree_node import TreeNode
from castervoice.lib.merge.selfmod.tree_rule.tree_rule import TreeRule
from castervoice.lib.merge.state.actions2 import NullAction

H = TreeNode


def get_docker_tree():
    """
    Constructs a 3-tier hierarchical tree for Docker CLI workflows:
    Tier 1: "dock" (Root entry)
    Tier 2: "container", "image", "compose", "volume", "system"
    Tier 3: Specific operations and subcommands
    """
    # Container operations
    container_nodes = [
        H("list", Text("docker ps") + Key("enter")),
        H("list all", Text("docker ps -a") + Key("enter")),
        H("stop", Text("docker stop ")),
        H("start", Text("docker start ")),
        H("restart", Text("docker restart ")),
        H("remove", Text("docker rm ")),
        H("logs", Text("docker logs -f ")),
        H("inspect", Text("docker inspect ")),
        H("stats", Text("docker stats") + Key("enter")),
        H(
            "run nathan",
            Text(
                "docker run -it --rm --name n8n -p 5678:5678 -p 11434:11434 "
                "-v n8n_data:/home/node/.n8n -e N8N_RUNNERS_ENABLED=true "
                "-e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true docker.n8n.io/n8nio/n8n"
            )
            + Key("enter"),
        ),
    ]

    # Image operations
    image_nodes = [
        H("list", Text("docker images") + Key("enter")),
        H("pull", Text("docker pull ")),
        H("build", Text("docker build -t .") + Key("left:2")),
        H("remove", Text("docker rmi ")),
        H("prune", Text("docker image prune -a") + Key("enter")),
    ]

    # Compose operations
    compose_nodes = [
        H("up", Text("docker-compose up -d") + Key("enter")),
        H("down", Text("docker-compose down") + Key("enter")),
        H("logs", Text("docker-compose logs -f") + Key("enter")),
        H("status", Text("docker-compose ps") + Key("enter")),
        H("restart", Text("docker-compose restart") + Key("enter")),
    ]

    # Volume & System operations
    volume_nodes = [
        H("list", Text("docker volume ls") + Key("enter")),
        H("prune", Text("docker volume prune") + Key("enter")),
        H("inspect", Text("docker volume inspect ")),
    ]

    system_nodes = [
        H("prune", Text("docker system prune -a --volumes") + Key("enter")),
        H("disk usage", Text("docker system df") + Key("enter")),
        H("info", Text("docker info") + Key("enter")),
    ]

    categories = [
        H("container", NullAction(), container_nodes),
        H("image", NullAction(), image_nodes),
        H("compose", NullAction(), compose_nodes),
        H("volume", NullAction(), volume_nodes),
        H("system", NullAction(), system_nodes),
        # Immediate top-level shortcuts under "dock"
        H("status", Text("docker ps") + Key("enter")),
        H("prune", Text("docker system prune") + Key("enter")),
    ]

    return H("dock", NullAction(), categories)


class DockerTreeRule(TreeRule):
    pronunciation = "docker tree rule"

    def __init__(self):
        super(DockerTreeRule, self).__init__("docker tree", get_docker_tree())


def get_rule():
    return [DockerTreeRule, RuleDetails(ccrtype=CCRType.SELFMOD)]
```

---

## 4. Production Candidate 2: Ollama Local Model TreeRule

### Current Baseline Problem
In [`apps/cli/cli_support.py`](../../caster_user_content/rules/apps/cli/cli_support.py), `OLLAMA_COMMANDS` includes 15 separate commands (`"oh run deep"`, `"oh show deep"`, `"oh help create"`, `"oh create model"`).

### TreeRule Implementation

```python
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024-2026 Amir Farhadi

from castervoice.lib.actions import Key, Text
from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.selfmod.tree_rule.tree_node import TreeNode
from castervoice.lib.merge.selfmod.tree_rule.tree_rule import TreeRule
from castervoice.lib.merge.state.actions2 import NullAction

H = TreeNode


def get_ollama_tree():
    """
    Hierarchical tree for Ollama LLM management:
    Tier 1: "llama" (Root entry)
    Tier 2: "run", "model", "service", "help"
    Tier 3: Target models or management actions
    """
    model_targets = [
        H("deep seek", Text("deepseek-r1:1.5b") + Key("enter")),
        H("llama", Text("llama3.2:3b") + Key("enter")),
        H("mistral", Text("mistral:7b") + Key("enter")),
        H("qwen", Text("qwen2.5-coder:7b") + Key("enter")),
    ]

    service_nodes = [
        H("serve", Text("ollama serve") + Key("enter")),
        H("status", Text("ollama ps") + Key("enter")),
        H("stop", Text("ollama stop ")),
        H("list", Text("ollama list") + Key("enter")),
    ]

    model_management = [
        H("list", Text("ollama list") + Key("enter")),
        H("pull", Text("ollama pull ")),
        H("remove", Text("ollama rm ")),
        H("show", Text("ollama show "), model_targets),
        H("create custom", Text("ollama create --file .\\Modelfile") + Key("left:19, space:2, left")),
    ]

    help_nodes = [
        H("list", Text("ollama help list") + Key("enter")),
        H("show", Text("ollama help show") + Key("enter")),
        H("create", Text("ollama help create") + Key("enter")),
        H("general", Text("ollama --help") + Key("enter")),
    ]

    categories = [
        H("run", Text("ollama run "), model_targets),
        H("service", NullAction(), service_nodes),
        H("model", NullAction(), model_management),
        H("help", NullAction(), help_nodes),
        H("list", Text("ollama list") + Key("enter")),
    ]

    return H("llama", NullAction(), categories)


class OllamaTreeRule(TreeRule):
    pronunciation = "ollama tree rule"

    def __init__(self):
        super(OllamaTreeRule, self).__init__("ollama tree", get_ollama_tree())


def get_rule():
    return [OllamaTreeRule, RuleDetails(ccrtype=CCRType.SELFMOD)]
```

---

## 5. Production Candidate 3: Windows Display & System Control TreeRule

### Current Baseline Problem
In [`global/global_nonccr_extended.py`](../../caster_user_content/rules/global/global_nonccr_extended.py), display controls, brightness adjustments, and administrative utilities occupy flat root-level phrases.

### TreeRule Implementation

```python
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024-2026 Amir Farhadi

from dragonfly import Function, Key, Mimic, Pause, RunCommand, Text
from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.selfmod.tree_rule.tree_node import TreeNode
from castervoice.lib.merge.selfmod.tree_rule.tree_rule import TreeRule
from castervoice.lib.merge.state.actions2 import NullAction

from caster_user_content.util.display_scaling import (
    scale_bed,
    scale_default,
    scale_down,
    scale_up,
)

H = TreeNode


def get_system_tree():
    """
    Hierarchical tree for Windows system controls:
    Tier 1: "system" (Root entry)
    Tier 2: "display", "brightness", "admin", "window"
    Tier 3: Specific parameters and control actions
    """
    brightness_nodes = [
        H("zero", Key("w-a/100, tab/20:4, home, escape")),
        H("twenty five", Key("w-a/100, tab/20:4, home, right:25, escape")),
        H("fifty", Key("w-a/100, tab/20:4, home, right:50, escape")),
        H("max", Key("w-a/100, tab/20:4, end, escape")),
        H("dialog", Key("w-a/100, tab/20:4")),
    ]

    display_nodes = [
        H("night mode", Key("w-a/100, down/30:2, enter/30, escape")),
        H("scale up", Function(scale_up)),
        H("scale down", Function(scale_down)),
        H("scale bed", Function(scale_bed)),
        H("scale default", Function(scale_default)),
        H("mode bed", Mimic("toggle night") + Pause("100") + Mimic("brightness zero")),
        H("mode day", Mimic("toggle night") + Pause("100") + Mimic("brightness one hundred")),
    ]

    admin_nodes = [
        H("device manager", Key("w-r/50") + Text("devmgmt.msc") + Key("enter")),
        H("network", Key("w-r/50") + Text("ncpa.cpl") + Key("enter")),
        H("sounds", RunCommand("rundll32.exe shell32.dll,Control_RunDLL mmsys.cpl")),
        H("system info", Key("w-r/50") + Text("msinfo32.exe") + Key("enter")),
        H("calendar", Key("w-b, up:2, enter")),
    ]

    categories = [
        H("brightness", NullAction(), brightness_nodes),
        H("display", NullAction(), display_nodes),
        H("admin", NullAction(), admin_nodes),
    ]

    return H("system", NullAction(), categories)


class SystemTreeRule(TreeRule):
    pronunciation = "system tree rule"

    def __init__(self):
        super(SystemTreeRule, self).__init__("system tree", get_system_tree())


def get_rule():
    return [SystemTreeRule, RuleDetails(ccrtype=CCRType.SELFMOD)]
```

---

## 6. Registration and Configuration Checklist

To activate any `TreeRule` in Caster:

1. **Create the Rule File**: Place the Python rule file in `caster_user_content/rules/` (or a subdirectory such as `apps/cli/`).
2. **Configure State Persistence Path**: Add the path key to `settings.toml` under the `[Tree_Node_Path]` section.
   ```toml
   [Tree_Node_Path]
   SM_DOCKER_TREE_TREE_PATH = "C:/Users/Amir/AppData/Local/caster/data/sm_docker_tree_tree_node.toml"
   SM_OLLAMA_TREE_TREE_PATH = "C:/Users/Amir/AppData/Local/caster/data/sm_ollama_tree_tree_node.toml"
   SM_SYSTEM_TREE_TREE_PATH = "C:/Users/Amir/AppData/Local/caster/data/sm_system_tree_tree_node.toml"
   ```
3. **Merger Specification**: Ensure `get_rule()` returns `RuleDetails(ccrtype=CCRType.SELFMOD)`.
4. **Voice Activation**: Say `Enable <Pronunciation>` (e.g., `"Enable Docker Tree Rule"`).
5. **Escape Command**: Say `cancel <tree_name>` (e.g., `"cancel docker tree"`) at any time to immediately reset to the root node.

---

*Recorded in `docs/framework_explainers/caster_treerule_practical_candidates.md`.*
