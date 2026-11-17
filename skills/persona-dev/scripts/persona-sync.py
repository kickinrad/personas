#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml"]
# ///
"""Report or apply a persona folder's generated files, or wrap the folder as an eval plugin.

The generated files are PERSONAS.md, copied from the shared rules, and the mcp_servers
tables of .codex/config.toml, projected from the mcpServers of the native agent file."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import tomllib
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

import yaml

SENSITIVE = re.compile(r"(?:api[_-]?key|token|secret|password|authorization|bearer|cookie)", re.I)
# Values under a credential-like key that cannot hold a secret: an env reference or a boolean flag.
NOT_SECRET = re.compile(r"\$\{[A-Za-z_][A-Za-z0-9_]*\}|true|false", re.I)
# Codex `-c mcp_servers.<name>.*` overrides need a server name that is a bare TOML key.
SERVER_NAME = re.compile(r"[A-Za-z0-9_-]+")
FRONTMATTER = re.compile(r"---[ \t]*\n(.*?)^---[ \t]*$", re.S | re.M)
SHARED = Path(__file__).resolve().parent.parent / "assets" / "PERSONAS.md"
# URL path segments must read as short lowercase words, so a token in the path is refused rather than guessed at.
# Each -/. part is letters (up to 24), digits (up to 12), or a short mix such as v2 or eu1.
PATH_PART = r"(?:[a-z]{1,24}|[0-9]{1,12}|[a-z0-9]{1,3})"
PATH_SEGMENT = re.compile(rf"{PATH_PART}(?:[-.]{PATH_PART})*")
URL = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^\s\"'<>]*")
# A credential-named flag with its value (--api-key=..., --token ...) or a header line (Authorization: ...).
FLAG = re.compile(r"--?([A-Za-z0-9_-]+)(?:=(.*))?", re.S)
HEADER = re.compile(r"\s*([A-Za-z0-9_-]+)\s*:\s+(.+)", re.S)
LITERAL = re.compile(r"(?:sk-[A-Za-z0-9_-]{12,}|eyJ[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_-]{12,})")


def fail(message: str) -> None:
    raise ValueError(message)


def strings(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def persona_slug(persona: Path) -> str:
    """The persona's name, also from a worktree of its folder at <persona>/.worktrees/<branch>."""
    name = persona.parent.parent.name if persona.parent.name == ".worktrees" else persona.name
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or fail("persona directory does not produce a slug")


def secret_flag(items: list[object]) -> bool:
    """Whether a credential-named flag carries a literal value: --api-key=value, or --token value."""
    secret = lambda name, given: SENSITIVE.search(name) and not NOT_SECRET.fullmatch(given.strip())
    for item, following in zip(items, [*items[1:], None]):
        flag = FLAG.fullmatch(item) if isinstance(item, str) else None
        if flag and flag.group(2) is not None and secret(flag.group(1), flag.group(2)): return True
        if flag and flag.group(2) is None and isinstance(following, str) and not following.startswith("-") and secret(flag.group(1), following): return True
    return False


def credential_free(value: object, key: str = "") -> None:
    if SENSITIVE.search(key) and not (isinstance(value, str) and NOT_SECRET.fullmatch(value)):
        fail(f"credential literal is unsupported: {key}")
    if isinstance(value, str) and LITERAL.search(value): fail("credential literal is unsupported")
    if isinstance(value, str):
        for text in URL.findall(value):
            url = urlsplit(text)
            if url.username is not None or url.password is not None: fail("url must not contain credentials")
            if any(SENSITIVE.search(key) for part in (url.query, url.fragment) for key, _ in parse_qsl(part, keep_blank_values=True)):
                fail("url must not contain credential parameters")
            if not all(PATH_SEGMENT.fullmatch(segment) for segment in url.path.split("/") if segment):
                fail("url must not contain a token-like path segment")
        header = HEADER.fullmatch(value)
        if secret_flag(value.split()) or header and SENSITIVE.search(header.group(1)) and not NOT_SECRET.fullmatch(header.group(2).strip()):
            fail("credential literal is unsupported in a flag or header")
    if isinstance(value, dict):
        for nested_key, nested in value.items(): credential_free(nested, str(nested_key))
    elif isinstance(value, list):
        for nested in value: credential_free(nested, key)
        if secret_flag(value): fail("credential literal is unsupported in a flag or header")


class UniqueKeyLoader(yaml.SafeLoader):
    """A safe YAML loader that refuses a mapping which sets the same key twice."""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict:
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            try: repeated = key in seen
            except TypeError: continue  # An unhashable key fails in the base constructor.
            if repeated: raise yaml.constructor.ConstructorError(None, None, f"duplicate key {key!r}", key_node.start_mark)
            seen.add(key)
        return super().construct_mapping(node, deep)

def agent_file(persona: Path) -> Path:
    return persona / ".claude" / "agents" / f"{persona_slug(persona)}.md"

def agent_servers(persona: Path) -> dict[str, object]:
    """The mcpServers of the persona's native agent file .claude/agents/<slug>.md, the one home of its MCP list.

    An agent file without an mcpServers key has no servers; a missing file or unreadable list is an error."""
    agent = agent_file(persona)
    try: text = agent.read_text(encoding="utf-8").removeprefix("\ufeff").replace("\r\n", "\n")
    except OSError as error: fail(f"cannot read the native agent {agent}: {error.strerror or error}")
    head = FRONTMATTER.match(text) or fail(f"{agent} needs frontmatter between --- lines")
    # The frontmatter starts on line 2 of the file, after the opening ---.
    at = lambda mark: f" at line {mark.line + 2}" if mark else ""
    loader = UniqueKeyLoader(head.group(1))
    try:
        node = loader.get_single_node()
        meta = loader.construct_document(node) if node else None
    except yaml.YAMLError as error:
        fail(f"{agent} frontmatter is not valid YAML{at(getattr(error, 'problem_mark', None))}: {getattr(error, 'problem', None) or error}")
    finally: loader.dispose()
    if meta is None: return {}
    if not isinstance(meta, dict): fail(f"{agent} frontmatter must be a mapping")
    if "mcpServers" not in meta: return {}
    value = next(value for key, value in node.value if key.value == "mcpServers")
    listed, shape = meta["mcpServers"], "- name: {server settings}"
    if not isinstance(listed, list): fail(f"{agent} mcpServers{at(value.start_mark)} must be a list of {shape}")
    servers: dict[str, object] = {}
    for item, item_node in zip(listed, value.value):
        if not (isinstance(item, dict) and len(item) == 1):
            fail(f"{agent} mcpServers{at(item_node.start_mark)} must list each server as {shape}, with its settings inline: {item!r}")
        ((name, server),) = item.items()
        if not isinstance(name, str) or not SERVER_NAME.fullmatch(name):
            fail(f"{agent} MCP server name{at(item_node.start_mark)} must use letters, digits, _ and -: {name!r}")
        if name in servers: fail(f"{agent} lists MCP server {name} twice{at(item_node.start_mark)}")
        servers[name] = server
    return servers

def agent_mcps(persona: Path) -> dict[str, dict[str, object]]:
    servers = agent_servers(persona)
    try: return checked_servers(servers)
    except ValueError as error: fail(f"{agent_file(persona)}: {error}")

def checked_servers(servers: dict[str, object]) -> dict[str, dict[str, object]]:
    """Servers whose settings pass the credential and transport gates, each with an explicit type."""
    selected = {}
    for name, raw in servers.items():
        if not isinstance(raw, dict): fail(f"MCP {name} must be an object")
        try: credential_free(raw)
        except ValueError as error: fail(f"MCP {name}: {error}")
        kind = raw.get("type", "stdio")
        if kind == "stdio":
            env = raw.get("env", {})
            if set(raw) - {"type", "command", "args", "env"} or not isinstance(raw.get("command"), str) or not strings(raw.get("args", [])) \
                    or not (isinstance(env, dict) and strings(list(env.values()))):
                fail(f"MCP {name} needs only a string command, string args, and string env")
        elif kind in ("http", "streamable-http", "sse"):
            if set(raw) - {"type", "url", "oauth", "headersHelper"} or not isinstance(raw.get("url"), str) or not raw["url"].startswith(("https://", "http://")):
                fail(f"MCP {name} needs only type, an HTTP url, and optional oauth or headersHelper")
            # A headers helper is a script that prints auth headers at connect time, so no secret lives here.
            helper = raw.get("headersHelper", "/")
            if not isinstance(helper, str) or not Path(helper).is_absolute() or any(c.isspace() for c in helper):
                fail(f"MCP {name} headersHelper must be an absolute path to a script, with no arguments")
            oauth = raw.get("oauth", {})
            if not isinstance(oauth, dict): fail(f"MCP {name} oauth must be an object")
            if extra := sorted(set(oauth) - {"clientId", "callbackPort"}):
                fail(f"MCP {name} oauth {', '.join(extra)} is unsupported; only clientId and callbackPort may be set, and credentials stay out of the agent file")
            if not isinstance(oauth.get("clientId", ""), str) or type(oauth.get("callbackPort", 0)) is not int:
                fail(f"MCP {name} oauth needs a string clientId and an integer callbackPort")
        else: fail(f"MCP {name} transport {kind!r} is unsupported")
        selected[name] = {"type": kind} | raw
    return selected


def toml_value(value: object) -> str:
    if isinstance(value, list): return "[" + ", ".join(map(toml_value, value)) + "]"
    if isinstance(value, dict): return "{" + ", ".join(f"{json.dumps(k, ensure_ascii=False)} = {toml_value(v)}" for k, v in value.items()) + "}"
    return json.dumps(value, ensure_ascii=False)


def codex_gap(server: dict[str, object]) -> str | None:
    """Name why Codex cannot run a server Claude can, or None when it can."""
    if server["type"] == "sse": return "sse transport is unsupported"
    if "oauth" in server: return "oauth config is Claude-only"
    if "headersHelper" in server: return "headersHelper is Claude-only"
    return None


def codex_tables(mcps: dict[str, dict[str, object]]) -> str:
    """Render the Codex [mcp_servers.*] tables for every server Codex can run."""
    text = ""
    for name, server in mcps.items():
        if codex_gap(server): continue
        fields = {key: value for key, value in server.items() if key != "type"}
        text += f"\n[mcp_servers.{json.dumps(name, ensure_ascii=False)}]\n" + "".join(f"{key} = {toml_value(value)}\n" for key, value in fields.items())
    return text


def codex_overrides(mcps: dict[str, dict[str, object]]) -> list[str]:
    """The agent's servers as Codex `-c mcp_servers.<name>.<field>=<TOML>` values, for a launch outside the folder."""
    return [f"mcp_servers.{name}.{key}={toml_value(value)}" for name, server in mcps.items() if not codex_gap(server)
            for key, value in server.items() if key != "type"]


def mcp_names(document: str) -> tuple[bool, set[str]]:
    """Whether a TOML fragment sets mcp_servers, and which servers it names."""
    servers = tomllib.loads(document).get("mcp_servers")
    return servers is not None, set(servers) if isinstance(servers, dict) else set()


def toml_units(text: str) -> list[tuple[str, str, bool, set[str]]]:
    """Split TOML into (kind, source, sets mcp_servers, server names) units whose sources join back to the text.

    A statement takes lines until it parses under its table header, so multi-line strings and arrays stay whole."""
    lines, units, header, index = text.splitlines(keepends=True), [], "", 0
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith("#"):
            units.append(("trivia", lines[index], False, set()))
            index += 1
            continue
        if stripped.startswith("["):
            header = lines[index]
            units.append(("header", header, *mcp_names(header)))
            index += 1
            continue
        end = index + 1
        while True:
            source = "".join(lines[index:end])
            try:
                units.append(("statement", source, *mcp_names(header.rstrip("\n") + "\n" + source)))
                break
            except tomllib.TOMLDecodeError:
                if end == len(lines): raise
                end += 1
        index = end
    return units


def folder_config(persona: Path, codex_home: Path, mcps: dict[str, dict[str, object]]) -> tuple[Path, str | None, str] | None:
    """Reconcile only the mcp_servers entries of the persona's tracked .codex/config.toml.

    Returns (path, existing text, desired text), or None when the persona has neither the file nor servers for it.
    Every byte outside the removed MCP entries is kept; regenerated tables are appended."""
    path, home = persona / ".codex" / "config.toml", codex_home / "config.toml"
    shared = tomllib.loads(home.read_text(encoding="utf-8")).get("mcp_servers", {}) if home.is_file() else {}
    wanted = {name: server for name, server in mcps.items() if name not in shared}
    if not path.is_file() and not codex_tables(wanted): return None
    for name in (name for name in mcps if name in shared): print(f"skipped {name} for {path}: defined in {home}")
    existing = path.read_text(encoding="utf-8") if path.is_file() else None
    parsed = tomllib.loads(existing or "")
    declared = json.loads((persona / ".mcp.json").read_text(encoding="utf-8")).get("mcpServers", {}) if (persona / ".mcp.json").is_file() else {}
    # Persona-owned entries: Codex variants of servers Codex cannot take as declared (in .mcp.json or the agent file,
    # which a worktree has without .mcp.json), and overrides of global servers.
    keep = set()
    for name, table in parsed.get("mcp_servers", {}).items():
        raw = mcps.get(name) or declared.get(name)
        variant = isinstance(raw, dict) and codex_gap({"type": raw.get("type", "stdio")} | raw)
        override = name in shared and isinstance(table, dict) and not {"command", "url"} & set(table)
        if not (variant or override): continue
        try:
            credential_free(table)
            keep.add(name)
        except ValueError as error: print(f"skipped {name} for {path}: {error}")
    units = toml_units(existing or "")
    kept = []
    for index, (kind, source, mcp, names) in enumerate(units):
        if names and names & keep and not names <= keep: fail(f"{path} sets kept and removed MCP servers in one entry; give each server its own table")
        if not mcp: kept.append(source)
        elif names: kept += [source] if names <= keep else []
        else:
            # A bare [mcp_servers] header stays while any entry under it is kept.
            following = next((i for i in range(index + 1, len(units)) if units[i][0] == "header"), len(units))
            kept += [source] if any(unit[3] and unit[3] <= keep for unit in units[index + 1:following]) else []
    content = "".join(kept)
    if tables := codex_tables(wanted):
        content = content + tables if content.endswith("\n") else (content + "\n" + tables if content else tables.lstrip("\n"))
    result = tomllib.loads(content)
    expected = {name: parsed["mcp_servers"][name] for name in keep}
    expected |= tomllib.loads(tables or "").get("mcp_servers", {})
    others = lambda config: {key: value for key, value in config.items() if key != "mcp_servers"}
    if others(result) != others(parsed) or result.get("mcp_servers", {}) != expected:
        fail(f"cannot edit the mcp_servers entries of {path} without changing other settings")
    # Formatting-only differences are current, so the file is not rewritten for them.
    return path, existing, existing if existing is not None and tomllib.loads(existing) == result else content


def eval_plugin(persona: Path, description: str, with_private: bool = False) -> Path:
    """Wrap the persona as a plugin whose main-thread agent it is, for `claude plugin eval`.

    The wrapper holds private user/ context, so it goes in a fresh owner-only temporary directory."""
    shared = persona / "PERSONAS.md"
    if not shared.is_file() or shared.read_text(encoding="utf-8") != SHARED.read_text(encoding="utf-8"):
        fail("PERSONAS.md is missing or drifted; run without --eval-plugin and --apply first")
    out, slug = Path(tempfile.mkdtemp(prefix=f"persona-eval-{persona_slug(persona)}-")), persona_slug(persona)
    # The sandbox cannot read the folder, so all private user/ context is inlined; evals therefore
    # cannot test whether the persona reads it only when relevant.
    sources = (shared, persona / "AGENTS.md", persona / "user/profile.md", *sorted((persona / "user/memory").glob("*.md")))
    body = "\n\n".join(path.read_text(encoding="utf-8") for path in sources if path.is_file())
    write(out / ".claude-plugin" / "plugin.json", json.dumps({"name": "persona"}) + "\n")
    write(out / "agents" / f"{slug}.md", f"---\nname: {json.dumps(slug)}\ndescription: {json.dumps(description)}\n---\n\n{body}")
    write(out / "settings.json", json.dumps({"agent": f"persona:{slug}"}) + "\n")
    # Evals answer these from evals/mocks/<server>/; real servers start only with --allow-real-servers.
    if mcps := agent_mcps(persona): write(out / ".mcp.json", json.dumps({"mcpServers": mcps}, indent=2) + "\n")
    # Private replays are long and costly, so they run only on request.
    pairs = (("skills", "skills"), ("evals", "evals")) + ((("user/evals", "evals/private"),) if with_private else ())
    for source, target in pairs:
        if (persona / source).is_dir(): shutil.copytree(persona / source, out / target, ignore=shutil.ignore_patterns("results"))
    return out


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as temporary:
        temporary_path = Path(temporary.name)
        try:
            temporary.write(content)
            temporary.close()
            temporary_path.replace(path)
        finally:
            temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--persona", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")))
    parser.add_argument("--eval-plugin", action="store_true", help="print a private temporary plugin that runs the persona as the main agent, for claude plugin eval")
    parser.add_argument("--with-private", action="store_true", help="with --eval-plugin, also include the private user/evals replays")
    parser.add_argument("--mcp-overrides", action="store_true", help="print the agent's MCP servers as Codex -c values, one per line, and change nothing")
    args = parser.parse_args()
    try:
        persona = args.persona.resolve()
        agents = persona / "AGENTS.md"
        lines = agents.read_text(encoding="utf-8").splitlines() if agents.is_file() else fail(f"missing {agents}")
        description = next((line[1:].strip() for line in lines if line.startswith(">")), None) or fail("AGENTS.md needs an opening blockquote")
        if args.eval_plugin:
            print(eval_plugin(persona, description, args.with_private))
            return 0
        mcps = agent_mcps(persona)
        for name, server in mcps.items():
            if reason := codex_gap(server): print(f"skipped {name} for codex: {reason}", file=sys.stderr if args.mcp_overrides else sys.stdout)
        if args.mcp_overrides:
            if overrides := codex_overrides(mcps): print(*overrides, sep="\n")
            return 0
        # PERSONAS.md is a generated copy in every persona, so it is always overwritten.
        shared = persona / "PERSONAS.md"
        targets = {"shared": shared}
        content = {"shared": SHARED.read_text(encoding="utf-8")}
        existing = {"shared": shared.read_text(encoding="utf-8") if shared.is_file() else None}
        if folder := folder_config(persona, args.codex_home, mcps):
            targets["folder"], existing["folder"], content["folder"] = folder
        drifted = False
        for target, path in targets.items():
            state = "current" if existing[target] == content[target] else "drift"
            drifted |= state == "drift"
            if args.apply and state == "drift":
                write(path, content[target])
                state = "updated"
            print(f"{state} {path}")
        return int(drifted and not args.apply)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
