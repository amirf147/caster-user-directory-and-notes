# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Amir Farhadi

"""
Automated Rule Catalog and Dynamic Context Resolver for Taskbar HUD

Dynamically catalogs application and contextual voice rules across user
and built-in rule directories via AST inspection, mapping target executables
and window titles directly to active rules synchronized with Caster's
rules.toml configuration.
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set

_logger = logging.getLogger("caster.plugins.taskbar_hud.context_resolver")


def normalize_process_name(raw_process: Optional[str]) -> str:
    """Normalizes process name or executable path to lowercase stem."""
    if not raw_process:
        return ""
    p = str(raw_process).strip().lower().replace("/", "\\")
    return Path(p).stem


def format_display_name(raw_name: Optional[str], class_name: str, is_ccr: bool = False) -> str:
    """Formats a clean, human-readable display title for a rule."""
    name = str(raw_name).strip() if raw_name else class_name

    # Normalize common naming inconsistencies
    name = name.replace("fire fox", "firefox").replace("Fire Fox", "Firefox")

    # Strip generic suffixes
    for suffix in (" Rule", " rule", "Rule"):
        if name.endswith(suffix):
            name = name[: -len(suffix)].strip()

    # Determine if CCR
    ccr = is_ccr or any(class_name.endswith(x) for x in ("CCR", "CcrRule", "CCRRule", "Ccr"))
    for suffix in (" CCR", " Ccr", "CCR", "Ccr"):
        if name.endswith(suffix):
            name = name[: -len(suffix)].strip()
            ccr = True
            break

    if ccr:
        name = f"{name} CCR"

    if name.islower():
        name = name.title()

    return name


class RuleEntry:
    __slots__ = ("rule_class", "display_name", "executables", "titles")

    def __init__(self, rule_class: str, display_name: str, executables: List[str], titles: List[str]):
        self.rule_class = rule_class
        self.display_name = display_name
        self.executables = executables
        self.titles = titles

    def __repr__(self) -> str:
        return f"<RuleEntry {self.rule_class} ({self.display_name})>"


class RuleCatalog:
    """
    Automated in-memory catalog of all discovered voice rules.
    Indexes target executables and window titles directly from rule source files,
    cross-referenced with enabled rules in rules.toml.
    """

    def __init__(self):
        self._proc_map: Dict[str, List[RuleEntry]] = {}
        self._title_rules: List[RuleEntry] = []
        self._enabled_rcns: Set[str] = set()
        self._rules_config_path: Optional[Path] = self._resolve_rules_config_path()
        self._last_config_mtime: float = 0.0
        self._catalog_built: bool = False
        self.refresh_catalog()

    def _resolve_rules_config_path(self) -> Optional[Path]:
        try:
            from castervoice.lib import settings

            if getattr(settings, "SETTINGS", None) and "paths" in settings.SETTINGS:
                cfg_path = settings.SETTINGS["paths"].get("RULES_CONFIG_PATH")
                if cfg_path and Path(cfg_path).exists():
                    return Path(cfg_path)
        except Exception:
            pass

        # Relative path fallback: <user_dir>/settings/rules.toml
        user_settings = Path(__file__).resolve().parents[3] / "settings" / "rules.toml"
        if user_settings.exists():
            return user_settings
        return None

    def refresh_enabled(self):
        """Reloads enabled rule class names from rules.toml if modified."""
        if not self._rules_config_path or not self._rules_config_path.exists():
            return
        try:
            mtime = self._rules_config_path.stat().st_mtime
            if mtime != self._last_config_mtime:
                self._last_config_mtime = mtime
                from castervoice.lib import utilities

                data = utilities.load_toml_file(str(self._rules_config_path))
                if isinstance(data, dict):
                    enabled_list = data.get("_enabled_ordered", [])
                    self._enabled_rcns = set(str(x) for x in enabled_list)
        except Exception as ex:
            _logger.debug("Failed to read rules.toml for enabled state: %s", ex)

    def refresh_catalog(self):
        """Scans user and core rule directories and rebuilds the lookup indexes."""
        self._proc_map.clear()
        self._title_rules.clear()

        user_rules_dir = Path(__file__).resolve().parents[2] / "rules"
        scan_dirs = [user_rules_dir]

        try:
            import castervoice

            core_rules_dir = Path(castervoice.__file__).parent / "rules"
            if core_rules_dir.exists():
                scan_dirs.append(core_rules_dir)
        except Exception:
            pass

        for d in scan_dirs:
            if not d.exists():
                continue
            for p in d.rglob("*.py"):
                if p.name.startswith("_"):
                    continue
                self._parse_rule_file(p)

        self._catalog_built = True
        self.refresh_enabled()

    def _parse_rule_file(self, file_path: Path):
        """Inspects a rule module AST for get_rule() and RuleDetails metadata."""
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            return

        rule_class = None
        details = {}
        has_get_rule = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "get_rule":
                has_get_rule = True
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Call):
                        func_name = getattr(sub.func, "id", getattr(sub.func, "attr", ""))
                        if func_name == "RuleDetails":
                            for kw in sub.keywords:
                                try:
                                    details[kw.arg] = ast.literal_eval(kw.value)
                                except Exception:
                                    pass
                    if isinstance(sub, ast.Return):
                        if isinstance(sub.value, ast.Tuple) and len(sub.value.elts) >= 1:
                            elt0 = sub.value.elts[0]
                            rule_class = getattr(elt0, "id", getattr(elt0, "attr", None))

        if has_get_rule and rule_class:
            raw_name = details.get("name")
            is_ccr = bool(details.get("ccrtype"))
            display = format_display_name(raw_name, rule_class, is_ccr=is_ccr)

            execs = details.get("executable")
            if isinstance(execs, str):
                execs = [execs]
            elif not isinstance(execs, list):
                execs = []
            exec_stems = [Path(str(e)).stem.lower() for e in execs if e]

            titles = details.get("title")
            if isinstance(titles, str):
                titles = [titles]
            elif not isinstance(titles, list):
                titles = []
            clean_titles = [str(t).lower() for t in titles if t]

            entry = RuleEntry(
                rule_class=rule_class,
                display_name=display,
                executables=exec_stems,
                titles=clean_titles,
            )

            if exec_stems:
                for stem in exec_stems:
                    self._proc_map.setdefault(stem, []).append(entry)
            if clean_titles and not exec_stems:
                self._title_rules.append(entry)

    def resolve(
        self,
        process_name: Optional[str] = None,
        window_title: Optional[str] = None,
        semantic_zone: Optional[str] = None,
    ) -> List[str]:
        """Resolves active contextual rules matching process and title."""
        if not self._catalog_built:
            self.refresh_catalog()
        else:
            self.refresh_enabled()

        proc = normalize_process_name(process_name)
        if not proc:
            return []

        candidates: List[RuleEntry] = []

        # 1. Base executable stem lookup
        if proc in self._proc_map:
            candidates.extend(self._proc_map[proc])

        # 2. Terminal shell aliases in terminal host windows
        if proc in ("windowsterminal", "conhost", "cmd", "wt"):
            t_low = (window_title or "").lower()
            if "powershell" in t_low or "pwsh" in t_low:
                candidates.extend(self._proc_map.get("powershell", []))
                candidates.extend(self._proc_map.get("pwsh", []))

        # 3. Title-based website rules (in browsers or any window with matched title)
        if window_title:
            t_low = window_title.lower()
            for r in self._title_rules:
                if any(t in t_low for t in r.titles):
                    candidates.append(r)

        # 4. Filter by enabled rules in rules.toml if available
        active_names: List[str] = []
        seen: Set[str] = set()
        for r in candidates:
            if self._enabled_rcns and r.rule_class not in self._enabled_rcns:
                continue
            name = r.display_name
            if name and name not in seen:
                seen.add(name)
                active_names.append(name)

        return active_names


_GLOBAL_CATALOG: Optional[RuleCatalog] = None


def get_catalog() -> RuleCatalog:
    global _GLOBAL_CATALOG
    if _GLOBAL_CATALOG is None:
        _GLOBAL_CATALOG = RuleCatalog()
    return _GLOBAL_CATALOG


def resolve_active_rules(
    process_name: Optional[str] = None,
    window_title: Optional[str] = None,
    semantic_zone: Optional[str] = None,
) -> List[str]:
    """
    Deterministically resolves active contextual voice rules from process and title telemetry.
    Returns an empty list [] for generic, untracked, or desktop contexts.
    """
    return get_catalog().resolve(
        process_name=process_name,
        window_title=window_title,
        semantic_zone=semantic_zone,
    )
