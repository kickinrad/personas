#!/usr/bin/env python3
"""Check every persona folder under a root, and with --fix repair what can be repaired.

Every root gets the portable folder contract. A root with shared settings at
.claude/settings.json is an installed root and also gets the host checks: the
shared plugin baseline, MCP allows scoped to declared sources, no pinned model,
no override of a shared deny, Codex plugin overrides that match the Claude set,
a native agent file in each persona, and no project-scope plugin install that
shadows a user-scope one.
"""

from __future__ import annotations

import argparse
import copy
import difflib
import fnmatch
import importlib.util
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("persona_sync", SCRIPTS / "persona-sync.py")
assert _spec and _spec.loader
SYNC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SYNC)

PRIVATE_PATHS = ("user", ".claude/settings.local.json", ".codex/*.local.toml", ".mcp.json", ".env", ".env.*")
ALWAYS_LOADED_HEADINGS = re.compile(
    r"^#{1,6}\s+(?:tools?(?:\s+(?:inventory|available))?|procedures?|workflows?|rituals?|integrations?)\b",
    re.IGNORECASE | re.MULTILINE,
)
REQUIRED = ("AGENTS.md", "PERSONAS.md", ".claude/settings.json")
SHARED = SYNC.SHARED
TEMPLATE = SHARED.with_name("agents-template.md")
# Any of these in a persona or above it stops Claude Code from reading AGENTS.md.
CLAUDE_FILES = ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md")
ALIAS_NAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_-]*$")


# Portable folder contract ---------------------------------------------------


def tracked_files(repo: Path) -> set[Path]:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=repo, capture_output=True)
    if result.returncode == 0:
        return {repo / name for name in result.stdout.decode().split("\0") if name}
    return {path for path in repo.rglob("*") if path.is_file()}


def tracked_private_paths(repo: Path) -> list[str]:
    """Return tracked private paths, allowing user/ subpaths the persona re-includes after ignoring user/ by default."""
    result = subprocess.run(["git", "ls-files", "-z", "--", *PRIVATE_PATHS], cwd=repo, capture_output=True)
    if result.returncode:  # Not a Git checkout, such as a source export: everything present ships.
        return sorted({str(path.relative_to(repo)) for pattern in PRIVATE_PATHS for path in repo.glob(pattern)})
    names = [name for name in result.stdout.decode().split("\0") if name]
    user = [name for name in names if name.startswith("user/")]
    denies_user = subprocess.run(["git", "check-ignore", "-q", "--no-index", "user/.doctor-probe"], cwd=repo).returncode == 0
    if user and denies_user:
        ignored = subprocess.run(
            ["git", "check-ignore", "--no-index", "-z", "--stdin"], cwd=repo, input="\0".join(user).encode(), capture_output=True
        ).stdout.decode()
        user = [name for name in user if name in set(ignored.split("\0"))]
    private = [name for name in names if not name.startswith("user/")]
    private += ["/".join(name.split("/")[:2]) + ("/" if name.count("/") > 1 else "") for name in user]
    return sorted(set(private))


def persona_roots(root: Path) -> list[Path]:
    """Any folder holding a required file is a persona, so a missing one is reported, not skipped."""
    roots = [path for path in root.iterdir() if path.is_dir() and any((path / name).exists() for name in REQUIRED)]
    return sorted(roots, key=lambda path: path.name)


def words(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


def claude_settings(path: Path, repo: Path) -> bool:
    relative = path.relative_to(repo)
    return len(relative.parts) >= 2 and relative.parts[0] == ".claude" and path.name.startswith("settings") and path.suffix == ".json"


def verify_persona(repo: Path) -> list[str]:
    errors: list[str] = []
    name = repo.name
    tracked = tracked_files(repo)
    agents = repo / "AGENTS.md"

    for required in (repo / file for file in REQUIRED):
        if required not in tracked or not required.is_file():
            errors.append(f"{name}: required tracked file missing: {required.relative_to(repo)}")

    private = tracked_private_paths(repo)
    if private:
        errors.append(f"{name}: private local context is tracked: {', '.join(private)}")

    if agents.is_file():
        always_loaded = agents.read_text(encoding="utf-8")
        if words(agents) > 500:
            errors.append(f"{name}: AGENTS.md exceeds 500 words")
        if ALWAYS_LOADED_HEADINGS.search(always_loaded):
            errors.append(f"{name}: AGENTS.md contains an always-loaded tool/procedure heading")
        if len(re.findall(r"^\s*\d+[.)]\s+", always_loaded, re.MULTILINE)) >= 4:
            errors.append(f"{name}: AGENTS.md contains procedural bulk (four or more numbered steps)")
        craft = re.search(r"^## Craft\b(.*?)(?=^## |\Z)", always_loaded, re.MULTILINE | re.DOTALL)
        if not craft or not all(re.search(rf"\*\*{entry}:\*\*[^\n]*\w", craft.group(1)) for entry in ("Instruments", "Crew", "Proof")):
            errors.append(f"{name}: AGENTS.md needs a Craft section with Instruments, Crew, and Proof")
        flat = " ".join(always_loaded.split())
        if any(" ".join(slot.split()) in flat for slot in re.findall(r"\{[^{}]+\}", TEMPLATE.read_text(encoding="utf-8"))):
            errors.append(f"{name}: AGENTS.md still contains a template placeholder")
        if not re.search(r"@PERSONAS\.md\s*$", always_loaded, re.MULTILINE):
            errors.append(f"{name}: AGENTS.md must import the shared rules with a line ending in @PERSONAS.md")
    shared = repo / "PERSONAS.md"
    if shared.is_file() and shared.read_text(encoding="utf-8") != SHARED.read_text(encoding="utf-8"):
        errors.append(f"{name}: PERSONAS.md drifted from the plugin; run persona-sync.py --apply")

    errors += [f"{name}: delete {file}; it stops Claude Code from reading AGENTS.md" for file in CLAUDE_FILES if (repo / file).exists()]

    for skill in repo.glob("skills/**/SKILL.md"):
        if skill in tracked and words(skill) > 500:
            errors.append(f"{name}: {skill.relative_to(repo)} exceeds 500 words")

    for settings in (path for path in tracked if path.is_file() and claude_settings(path, repo)):
        try:
            json.loads(settings.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{name}: invalid JSON in {settings.relative_to(repo)}: {exc.msg}")
    if (repo / ".agent-mcp.json").exists():
        errors.append(f"{name}: delete .agent-mcp.json; the native agent file's mcpServers is the one MCP list")
    codex = repo / ".codex/config.toml"
    if codex.is_file():
        try:
            tomllib.loads(codex.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"{name}: invalid TOML in .codex/config.toml: {exc}")
    return errors


def verify(root: Path) -> list[str]:
    if not root.is_dir():
        return [f"persona root does not exist: {root}"]
    roots = persona_roots(root)
    if not roots:
        return [f"no persona folders under: {root}"]
    # Claude Code checks ancestors too. Above the root, .claude/CLAUDE.md is skipped because
    # the user-level ~/.claude/CLAUDE.md is exempt and looks the same.
    blocking = [root / file for file in CLAUDE_FILES]
    blocking += [directory / file for directory in root.parents for file in ("CLAUDE.md", "CLAUDE.local.md")]
    errors = [f"delete {path}; it stops Claude Code from reading AGENTS.md" for path in blocking if path.exists()]
    if (root / "AGENTS.md").exists():
        errors.append(f"remove {root / 'AGENTS.md'}; Claude Code would load it into every persona")
    return errors + [error for persona in roots for error in verify_persona(persona)]


# Host checks ----------------------------------------------------------------


def home() -> Path:
    return Path.home()


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", home() / ".codex"))


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def read_plugin_metadata(path: Path):
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise ValueError(f"plugin metadata is invalid: {path}: {error}") from error
    if not isinstance(data, dict):
        raise ValueError(f"plugin metadata is invalid: {path}: expected an object")
    return data


def plugin_source_servers(root: Path, source) -> list[str]:
    if isinstance(source, dict):
        return list(source)
    if isinstance(source, list):
        return [server for item in source for server in plugin_source_servers(root, item)]
    if isinstance(source, str):
        if source.endswith((".mcpb", ".dxt")):
            raise ValueError(f"plugin MCP bundle cannot be inspected: {source}")
        if not source.startswith("./"):
            raise ValueError(f"plugin metadata is invalid: MCP config path {source}")
        path = (root / source).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError(f"plugin metadata is invalid: MCP config path escapes plugin: {source}")
        data = read_plugin_metadata(path)
        if data is None:
            raise ValueError(f"plugin metadata is invalid: MCP config path missing: {source}")
        servers = data.get("mcpServers", data)
        if not isinstance(servers, dict):
            raise ValueError(f"plugin metadata is invalid: MCP config at {source}")
        return list(servers)
    raise ValueError("plugin metadata is invalid: MCP servers must be a path, map, or array")


def plugin_servers(plugin: str) -> list[str]:
    """MCP server names a plugin ships, from its installed copy."""
    registry = read_plugin_metadata(home() / ".claude/plugins/installed_plugins.json") or {}
    plugins = registry.get("plugins", {})
    if not isinstance(plugins, dict):
        raise ValueError("plugin metadata is invalid: installed plugin registry")
    installs = plugins.get(plugin)
    if installs is None:
        return []
    if (not isinstance(installs, list) or not installs or not isinstance(installs[0], dict)
            or not isinstance(installs[0].get("installPath"), str) or not installs[0]["installPath"]):
        raise ValueError(f"plugin metadata is invalid: install path for {plugin}")
    root = Path(installs[0]["installPath"])
    if not root.is_dir():
        raise ValueError(f"plugin metadata is invalid: installed directory for {plugin} is unavailable")
    servers = []
    default = read_plugin_metadata(root / ".mcp.json")
    if default is not None:
        servers += plugin_source_servers(root, default.get("mcpServers", default))
    manifest = read_plugin_metadata(root / ".claude-plugin/plugin.json") or {}
    if "mcpServers" in manifest:
        servers += plugin_source_servers(root, manifest["mcpServers"])
    return list(dict.fromkeys(servers))


def known_marketplaces() -> dict:
    return read_plugin_metadata(home() / ".claude/plugins/known_marketplaces.json") or {}


def local_markets() -> set[str]:
    """Marketplaces installed from a local directory: the ones whose plugins Codex loads from the same source."""
    return {name for name, entry in known_marketplaces().items()
            if isinstance(entry, dict) and (entry.get("source") or {}).get("source") == "directory"}


def local_plugin_identities(node) -> list[str]:
    """Claude plugin ids of every local-plugin dependency in a capabilities contract."""
    if isinstance(node, list):
        return [found for item in node for found in local_plugin_identities(item)]
    if not isinstance(node, dict):
        return []
    found = []
    if node.get("kind") == "local-plugin":
        identity = (node.get("runtimeImplementations") or {}).get("claude-code", {}).get("identity")
        if isinstance(identity, str) and identity:
            found.append(identity)
    return found + [f for value in node.values() for f in local_plugin_identities(value)]


def plugin_source(plugin: str) -> Path | None:
    """A plugin's source directory in its marketplace checkout, or None."""
    name, _, market = plugin.partition("@")
    location = (known_marketplaces().get(market) or {}).get("installLocation")
    if not isinstance(location, str) or not location:
        return None
    catalog = read_plugin_metadata(Path(location) / ".claude-plugin/marketplace.json") or {}
    for entry in catalog.get("plugins", []):
        source = entry.get("source") if isinstance(entry, dict) else None
        if isinstance(source, str) and entry.get("name") == name and source.startswith("./"):
            return Path(location) / source
    return None


def plugin_needs(plugin: str) -> list[str]:
    """Local plugins this plugin's source contract declares it depends on."""
    root = plugin_source(plugin)
    if root is None:
        return []
    contract = read_plugin_metadata(root / "interop/capabilities.json") or {}
    return list(dict.fromkeys(p for p in local_plugin_identities(contract) if p != plugin))


def canonical_mcp_name(name: str) -> str:
    """Claude Code replaces punctuation and spaces in MCP tool server names."""
    return re.sub(r"[^A-Za-z0-9_-]", "_", name)


def plugin_rule(plugin: str, server: str) -> str:
    return f"mcp__plugin_{canonical_mcp_name(plugin.split('@')[0])}_{canonical_mcp_name(server)}__*"


def shared_settings(persona: Path) -> dict:
    """The baseline every persona gets, merged into each persona session by the launcher."""
    return read_json(persona.parent / ".claude/settings.json")


def shared_plugins(persona: Path) -> dict:
    return shared_settings(persona).get("enabledPlugins", {})


def shared_denies(persona: Path) -> list[str]:
    return shared_settings(persona).get("permissions", {}).get("deny", [])


def explicit_mcp_servers(persona: Path) -> list[str]:
    path = persona / ".claude/mcp-allowlist.json"
    if not path.exists():
        return []
    try:
        names = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise ValueError(f"mcp-allowlist.json is invalid: {error}") from error
    if not isinstance(names, list) or any(not isinstance(name, str) or not name for name in names):
        raise ValueError("mcp-allowlist.json is invalid: expected a list of server names")
    return names


def plugin_rules(persona: Path, plugin: str) -> list[str]:
    """Allow rules for a plugin's MCP servers, skipping any the shared settings deny."""
    denied = shared_denies(persona)
    return [rule for rule in (plugin_rule(plugin, server) for server in plugin_servers(plugin)) if rule not in denied]


def mcp_policy(persona: Path, settings: dict) -> tuple[list[str], list[str]]:
    """Project servers to enable, and rules from declared persona sources."""
    project = list(read_json(persona / ".mcp.json").get("mcpServers", {}))
    explicit = explicit_mcp_servers(persona)
    rules = [f"mcp__{canonical_mcp_name(name)}__*" for name in project + explicit]
    for plugin, enabled in {**shared_plugins(persona), **settings.get("enabledPlugins", {})}.items():
        if enabled:
            rules += plugin_rules(persona, plugin)
    return project, list(dict.fromkeys(rules))


def mcp_widening(persona: Path, before: dict, after: dict) -> bool:
    old_allow = before.get("permissions", {}).get("allow", [])
    new_allow = after.get("permissions", {}).get("allow", [])
    old_enabled = before.get("enabledMcpjsonServers", [])
    new_enabled = after.get("enabledMcpjsonServers", [])
    added_rules = [rule for rule in new_allow if rule.startswith("mcp__") and rule not in old_allow]
    added_servers = [server for server in new_enabled if server not in old_enabled]
    old_plugins = before.get("enabledPlugins", {})
    activated = [rule for plugin, enabled in after.get("enabledPlugins", {}).items()
                 if enabled and not old_plugins.get(plugin) for rule in plugin_rules(persona, plugin)]
    if added_rules or added_servers or activated:
        old_mcp = [rule for rule in old_allow if rule.startswith("mcp__")]
        old_policy = {"enabledMcpjsonServers": old_enabled, "allow": old_mcp, "activatedPluginMcpServers": []}
        new_policy = {"enabledMcpjsonServers": new_enabled, "allow": old_mcp + added_rules,
                      "activatedPluginMcpServers": activated}
        diff = difflib.unified_diff(
            (json.dumps(old_policy, indent=2) + "\n").splitlines(keepends=True),
            (json.dumps(new_policy, indent=2) + "\n").splitlines(keepends=True),
            fromfile=f"{persona.name} MCP permissions", tofile=f"{persona.name} proposed MCP permissions",
        )
        print("".join(diff), end="")
    return bool(added_rules or added_servers or activated)


RULE = re.compile(r"^(\w+)\((.*)\)$")


def covered(rule: str, deny: str) -> bool:
    """Whether a rule targets something a deny already covers: the same rule, or a narrower one for the same tool."""
    ours, theirs = RULE.match(rule), RULE.match(deny)
    if ours and theirs:
        pattern = theirs.group(2)
        return ours.group(1) == theirs.group(1) and (fnmatch.fnmatchcase(ours.group(2), pattern)
                                                     or (pattern.endswith("/**") and ours.group(2) == pattern[:-3]))
    if theirs is None:
        return fnmatch.fnmatchcase(ours.group(1) if ours else rule, deny)
    return False


def under(path: str, denied: str) -> bool:
    path, denied = (os.path.expanduser(p).rstrip("/") for p in (path, denied))
    return path == denied or path.startswith(denied + "/")


def deny_overrides(persona: Path, settings: dict) -> list[str]:
    """Shared denies a persona tries to undo with its own allow, ask, or sandbox read rule."""
    shared = shared_settings(persona)
    denies = shared.get("permissions", {}).get("deny", [])
    deny_read = (shared.get("sandbox") or {}).get("filesystem", {}).get("denyRead", [])
    perms = settings.get("permissions", {})
    allow_read = (settings.get("sandbox") or {}).get("filesystem", {}).get("allowRead", [])
    found = [f"{kind} rule overrides a shared deny: {rule}" for kind in ("allow", "ask")
             for rule in perms.get(kind, []) if any(covered(rule, deny) for deny in denies)]
    return found + [f"sandbox allowRead overrides a shared denyRead: {path}" for path in allow_read
                    if any(under(path, denied) for denied in deny_read)]


def settings_gaps(persona: Path, settings: dict) -> list[str]:
    plugins = settings.get("enabledPlugins", {})
    shared = shared_plugins(persona)
    gaps = [] if shared else ["shared persona settings list no plugins"]
    gaps += [f"plugin duplicates shared settings: {p}" for p in plugins if p in shared and plugins[p] == shared[p]]
    if "model" in settings:
        gaps.append(f"pinned model: {settings['model']}")
    gaps += deny_overrides(persona, settings)
    active = {p for p, on in {**shared, **plugins}.items() if on}
    gaps += [f"plugin {p} needs {need}" for p in sorted(active) for need in plugin_needs(p) if need not in active]
    servers, rules = mcp_policy(persona, settings)
    enabled = settings.get("enabledMcpjsonServers", [])
    allowed = settings.get("permissions", {}).get("allow", [])
    gaps += [f"MCP server not enabled: {s}" for s in servers if s not in enabled]
    gaps += [f"MCP server not allowed: {r}" for r in rules if r not in allowed]
    return gaps


def fix_settings(persona: Path, settings: dict) -> None:
    settings.pop("model", None)
    plugins = settings.setdefault("enabledPlugins", {})
    shared = shared_plugins(persona)
    for plugin in [p for p in plugins if p in shared and plugins[p] == shared[p]]:
        plugins.pop(plugin)
    servers, rules = mcp_policy(persona, settings)
    enabled = settings.setdefault("enabledMcpjsonServers", [])
    enabled += [s for s in servers if s not in enabled]
    allowed = settings.setdefault("permissions", {}).setdefault("allow", [])
    allowed += [r for r in rules if r not in allowed]


def codex_plugins(text: str) -> dict:
    return {k: v.get("enabled", True) for k, v in tomllib.loads(text).get("plugins", {}).items()}


def codex_file(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def codex_overrides(persona: Path, settings: dict) -> dict:
    """Codex overrides that make the persona's local plugins match its Claude set: {plugin: enabled or None to drop}."""
    claude = {**shared_plugins(persona), **settings.get("enabledPlugins", {})}
    global_on = codex_plugins(codex_file(codex_home() / "config.toml"))
    local = codex_plugins(codex_file(persona / ".codex/config.toml"))
    markets = local_markets()
    changes = {}
    for plugin in sorted(set(global_on) | set(local)):
        if plugin.rsplit("@", 1)[-1] not in markets:
            continue
        want = bool(claude.get(plugin))
        if want != global_on.get(plugin, False):
            if local.get(plugin) != want:
                changes[plugin] = want
        elif plugin in local:
            changes[plugin] = None
    return changes


def fix_codex(persona: Path, changes: dict) -> None:
    path = persona / ".codex/config.toml"
    text = codex_file(path)
    for plugin, want in changes.items():
        block = re.compile(r'^\[plugins\."' + re.escape(plugin) + r'"\]\s*\nenabled\s*=\s*(true|false)\s*\n', re.M)
        text = block.sub("", text)
        if plugin in codex_plugins(text):
            raise ValueError(f"{path}: cannot rewrite the {plugin} table; edit it by hand")
        if want is not None:
            text = text.rstrip("\n") + f'\n[plugins."{plugin}"]\nenabled = {str(want).lower()}\n'
    tomllib.loads(text)
    path.parent.mkdir(exist_ok=True)
    path.write_text(text)


def agent_gaps(persona: Path) -> list[str]:
    """Each persona owns its native agent file; dotfiles links it for Claude and renders it for Codex."""
    slug = SYNC.persona_slug(persona)
    agent = persona / ".claude/agents" / f"{slug}.md"
    if agent not in tracked_files(persona) or not agent.is_file():
        return [f"missing tracked native agent: {agent}"]
    parts = agent.read_text(encoding="utf-8").split("---\n", 2)
    head = parts[1] if len(parts) == 3 and not parts[0] else ""
    name = re.search(r'^name: "?([^"\n]+)"?$', head, re.M)
    if not name or name.group(1) != slug or not re.search(r"^description: \S", head, re.M) or not parts[-1].strip():
        return [f"native agent needs frontmatter with name {slug} and a description, then a body: {agent}"]
    try:
        SYNC.agent_mcps(persona)
    except ValueError as error:
        return [f"native agent MCP servers are invalid: {error}"]
    return []


def host_gaps(persona: Path, fix: bool, allow_mcp_widening: bool) -> list[str]:
    gaps = [] if ALIAS_NAME.match(persona.name) else ["folder name cannot be a shell alias"]
    agent_problems = agent_gaps(persona)
    gaps += agent_problems

    mcp = persona / ".mcp.json"
    if mcp.is_file():
        try:
            folder = json.loads(mcp.read_text())
        except json.JSONDecodeError as error:
            folder = None
            gaps.append(f".mcp.json is invalid: {error}")
        if folder is not None and not (isinstance(folder, dict) and isinstance(folder.get("mcpServers", {}), dict)):
            gaps.append(".mcp.json must be an object whose mcpServers is an object")
        elif folder is not None:
            if {"agentMcpServers", "codexMcpServers"} & set(folder):
                gaps.append(".mcp.json holds a legacy agent MCP list; move it to the native agent file's mcpServers")
            # .mcp.json serves Claude sessions run in the folder; it must name the same servers as the one list.
            # An unreadable agent file is already reported by agent_gaps.
            if not agent_problems:
                listed, agent = set(folder.get("mcpServers", {})), set(SYNC.agent_servers(persona))
                if listed != agent:
                    gaps.append(f".mcp.json and the native agent file's mcpServers differ: only in .mcp.json {sorted(listed - agent)}, only in the agent file {sorted(agent - listed)}")

    path = persona / ".claude/settings.json"
    try:
        settings = json.loads(path.read_text()) if path.exists() else {}
    except json.JSONDecodeError:
        return gaps  # The folder contract already reports invalid JSON.
    try:
        explicit_mcp_servers(persona)
        found = settings_gaps(persona, settings)
        proposed = copy.deepcopy(settings)
        fix_settings(persona, proposed)
        added = mcp_widening(persona, settings, proposed)
        if fix and added and not allow_mcp_widening:
            return gaps + found + ["MCP allow widening requires --allow-mcp-widening"]
        if found and fix:
            if proposed != settings:
                temporary = path.with_suffix(".json.tmp")
                temporary.write_text(json.dumps(proposed, indent=2, ensure_ascii=False) + "\n")
                temporary.replace(path)
                print(f"{persona.name}: fixed {path}")
            found = settings_gaps(persona, proposed)
        current = proposed if fix else settings
        changes = codex_overrides(persona, current)
        if changes and fix:
            fix_codex(persona, changes)
            print(f"{persona.name}: fixed {persona / '.codex/config.toml'}")
            changes = codex_overrides(persona, current)
    except ValueError as error:
        return gaps + [str(error)]
    found += [f"Codex override for {p} is redundant" if want is None else f"Codex plugin {p} should be {'on' if want else 'off'}"
              for p, want in changes.items()]
    return gaps + found


def shadowing_installs(root: Path, fix: bool) -> list[str]:
    """Report, or with fix drop, project- or local-scope installs under the root that shadow a user-scope install."""
    path = home() / ".claude/plugins/installed_plugins.json"
    try:
        registry = read_plugin_metadata(path) or {}
    except ValueError as error:
        return [str(error)]
    plugins = registry.get("plugins", {})
    if not isinstance(plugins, dict):
        return [f"plugin metadata is invalid: {path}: plugins must be an object"]
    prefix = str(root.resolve()) + os.sep
    gaps = []
    for plugin, installs in plugins.items():
        if not isinstance(installs, list) or not any(i.get("scope") == "user" for i in installs):
            continue
        keep = [i for i in installs if not (i.get("scope") in ("project", "local")
                and (i.get("projectPath", "") + os.sep).startswith(prefix))]
        gaps += [f"{os.path.relpath(i.get('projectPath'), root)}: {i.get('scope')} install of {plugin} shadows the user install"
                 for i in installs if i not in keep]
        plugins[plugin] = keep
    if gaps and fix:
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(registry, indent=2) + "\n")
        temporary.replace(path)
        print(f"fixed {path}: dropped {len(gaps)} shadowing installs")
        return []
    return gaps


def doctor(root: Path, fix: bool = False, allow_mcp_widening: bool = False) -> list[str]:
    if not root.is_dir() or not persona_roots(root):
        return verify(root)
    problems = []
    if (root / ".claude/settings.json").is_file():
        for persona in persona_roots(root):
            problems += [f"{persona.name}: {gap}" for gap in host_gaps(persona, fix, allow_mcp_widening)]
        problems += shadowing_installs(root, fix)
    return verify(root) + problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", required=True, type=Path, help="directory containing persona folders")
    parser.add_argument("--fix", action="store_true", help="repair persona settings, Codex overrides, and shadowing installs")
    parser.add_argument("--allow-mcp-widening", action="store_true", help="with --fix, allow the displayed MCP permission additions")
    args = parser.parse_args()
    root = args.root.resolve()
    problems = doctor(root, args.fix, args.allow_mcp_widening)
    count = len(persona_roots(root)) if root.is_dir() else 0
    if problems:
        print(*(f"- {problem}" for problem in problems), sep="\n")
        print(f"Persona doctor: {count} personas, {len(problems)} problems")
        return 1
    print(f"Persona doctor: {count} personas clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
