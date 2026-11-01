#!/usr/bin/env python3
"""Render an OpenCode agent team into a project from templates + config.

Usage: render.py --config <agent-team.json> [--only <role>] [--scope agents,commands,docs|all]
                 [--force] [--check] [--out <project_root>]

Writes OpenCode V2 definitions:
  .opencode/agents/<role>.md      mode: subagent
  .opencode/commands/<name>.md
  .opencode/agent-memory/<role>/  (empty dirs)
  <docs_dir>/{PROJECT-CONTEXT.md,TEAM.md,LEARNINGS.md,product/BACKLOG.md}
"""
import argparse, json, os, re, sys, datetime, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent.parent
T = HERE / "templates"

AGENT_DIR = ".opencode/agents"
COMMAND_DIR = ".opencode/commands"
MEMORY_DIR = ".opencode/agent-memory"
CONFIG_PATH = ".opencode/agent-team.json"

HEAVY = {"architect", "security-engineer", "code-reviewer", "backend-dev", "e2e-tester"}
LIGHT = {"mobile-tester", "web-tester", "tech-writer"}

# Effort tier per profile. OpenCode expresses effort as a model variant (`#high`),
# so a tier only becomes a real variant when the config names one; otherwise the
# subagent inherits the session model and the tier is informational.
PROFILES = {
    "max":      {"heavy": "max",    "other": "xhigh",  "light": "xhigh"},
    "balanced": {"heavy": "high",   "other": "high",   "light": "high"},
    "economy":  {"heavy": "medium", "other": "medium", "light": "medium"},
}

# Roles that may edit repo code. Everything else is docs+memory only; the
# code-reviewer writes nothing at all.
CODE_WRITERS = {"product-manager", "architect", "backend-dev", "mobile-dev", "web-dev",
                "devops-engineer", "test-engineer", "tech-writer"}
NO_WRITE = {"code-reviewer"}
# Roles with no web tools in the original Claude Code definitions.
NO_WEB = {"api-tester", "e2e-tester", "mobile-tester", "web-tester", "code-reviewer"}

DEFAULT_SKILLS = {
    "architect": ["scrutinize"], "code-reviewer": ["scrutinize"],
    "backend-dev": ["debug-mantra"], "bug-triager": ["debug-mantra"],
    "mobile-dev": ["debug-mantra", "impeccable"], "web-dev": ["debug-mantra", "impeccable"],
    "ux-designer": ["artifact-design", "impeccable"], "ui-designer": ["artifact-design", "impeccable"],
    "tech-writer": ["post-mortem"],
}
CATEGORY = {
    "product-manager": "think", "architect": "think", "ux-designer": "think", "ui-designer": "think", "tech-writer": "think",
    "backend-dev": "build", "mobile-dev": "build", "web-dev": "build", "devops-engineer": "build", "test-engineer": "build",
    "api-tester": "adversarial", "e2e-tester": "adversarial", "mobile-tester": "adversarial", "web-tester": "adversarial",
    "code-reviewer": "adversarial", "bug-triager": "adversarial", "security-engineer": "adversarial",
}
CRITIC = {"build": "code reviewer and the QA team", "adversarial": "engineer who wrote the code", "think": "CTO who has to pay for it"}
VALID_MODES = {"primary", "subagent", "all"}
# Fields that belong to Claude Code or to V1 OpenCode. None of them are valid in a
# V2 agent file, and V2 silently ignores them — which is exactly how a ported team
# ends up running with the wrong model or full write access.
FORBIDDEN_AGENT_KEYS = {"name", "tools", "permission", "temperature", "top_p", "prompt",
                        "disable", "maxSteps", "effort", "memory", "skills", "argument-hint"}
FORBIDDEN_COMMAND_KEYS = {"argument-hint", "allowed-tools", "template"}
MODEL_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.:-]+(#[A-Za-z0-9_.-]+)?$")
SCOPES = ("agents", "commands", "docs")


def parse_scope(raw, only):
    """What to (re-)render. Default keeps the historical behaviour: a bare run writes
    everything (init), `--only <role>` writes just that role's agent.
    `docs` re-renders the four hand-filled doc templates back to empty TODO scaffolds,
    so upgrades must ask for `--scope agents,commands` rather than a bare `--force`."""
    if raw is None:
        return {"agents"} if only else set(SCOPES)
    out = set()
    for part in (p.strip() for p in raw.split(",")):
        if not part:
            continue
        if part == "all":
            out |= set(SCOPES)
        elif part in SCOPES:
            out.add(part)
        else:
            sys.exit(f"--scope: unknown value {part!r} (expected any of: {', '.join(SCOPES)}, all)")
    if not out:
        sys.exit(f"--scope: empty (expected any of: {', '.join(SCOPES)}, all)")
    return out


def skill_exists(name, root):
    """OpenCode discovers skills in these roots (global first, then project), plus the
    Claude Code / .agents compatibility roots it still reads."""
    candidates = [
        pathlib.Path.home() / ".config/opencode/skills",
        pathlib.Path(root) / ".opencode/skills",
        pathlib.Path.cwd() / ".opencode/skills",
        pathlib.Path.home() / ".claude/skills",
        pathlib.Path(root) / ".claude/skills",
        pathlib.Path.home() / ".agents/skills",
        pathlib.Path(root) / ".agents/skills",
    ]
    for base in candidates:
        if (base / name / "SKILL.md").exists() or (base / f"{name}.md").exists():
            return True
    return False


def yaml_quote(s):
    return '"' + s.replace('"', "'") + '"'


def tier_of(role):
    return "heavy" if role in HEAVY else ("light" if role in LIGHT else "other")


def model_for(role, cfg):
    """None means "omit the model field and inherit the session model".

    Precedence: per-role override > per-tier model > single top-level model > inherit.
    Model strings are OpenCode's `provider/model[#variant]`, so nothing here assumes
    an Anthropic model name.
    """
    ov = cfg.get("overrides", {}).get(role, {})
    if ov.get("model"):
        return ov["model"]
    models = cfg.get("models") or {}
    if models.get(tier_of(role)):
        return models[tier_of(role)]
    if cfg.get("model"):
        return cfg["model"]
    return None


def render_text(text, vars_):
    for k, v in vars_.items():
        text = text.replace("{{%s}}" % k, v)
    return text


def protocol(role, cfg, vars_):
    cat = CATEGORY[role]
    common = (T / "partials" / "expert-protocol.md").read_text(encoding="utf-8")
    extra = (T / "partials" / f"protocol-{cat}.md").read_text(encoding="utf-8")
    return render_text(common + "\n" + extra, {**vars_, "ROLE": role.replace("-", " "), "ROLE_SLUG": role, "CRITIC": CRITIC[cat]})


def permission_block(role, cfg, docs_resource, memory_resource):
    """Translate the role's original tool allowlist into OpenCode permission rules.

    OpenCode has no `tools:` frontmatter; it has ordered permission rules where the
    last match wins. `edit` covers write/patch, so a role that may only write reports
    gets `edit * deny` followed by an allow for the docs folder and its own memory.
    """
    rules = [("subagent", "*", "deny")]
    if role in NO_WRITE:
        rules.append(("edit", "*", "deny"))
    elif role not in CODE_WRITERS:
        rules += [("edit", "*", "deny"),
                  ("edit", f"{docs_resource}/**", "allow"),
                  ("edit", f"{memory_resource}/**", "allow")]
    if role in NO_WRITE:
        rules.append(("edit", f"{memory_resource}/**", "allow"))
    if role in NO_WEB:
        rules += [("webfetch", "*", "deny"), ("websearch", "*", "deny")]
    return "permissions:\n" + "".join(
        f'  - action: {a}\n    resource: "{r}"\n    effect: {e}\n' for a, r, e in rules)


def legacy_permission_block(role, cfg, docs_resource, memory_resource):
    """Opt-in V1 fallback (`compat_v1: true`).

    OpenCode V1 ignores the V2 `permissions` list and routes unknown fields into
    `options`, so a V1 install would let the code-reviewer edit files. V1 still
    enforces the older `permission:` map, including a per-pattern object for `edit`
    (last match wins), so the same guarantees can be expressed there. V2 ignores
    this block; it is only emitted when the config asks for it.
    """
    if not cfg.get("compat_v1"):
        return ""
    lines = ["permission:", "  task: deny"]
    if role not in CODE_WRITERS:
        lines += ["  edit:", '    "*": deny']
        if role not in NO_WRITE:
            lines.append(f'    "{docs_resource}/**": allow')
        lines.append(f'    "{memory_resource}/**": allow')
    if role in NO_WEB:
        lines += ["  webfetch: deny", "  websearch: deny"]
    return "\n".join(lines) + "\n"


def render_agent(role, cfg, vars_):
    src = T / "agents" / f"{role}.md"
    if not src.exists():
        sys.exit(f"unknown role: {role}")
    text = src.read_text(encoding="utf-8")
    model = model_for(role, cfg)
    model_line = f"model: {model}\n" if model else ""
    skills = cfg.get("skills", {}).get(role, DEFAULT_SKILLS.get(role, []))
    skills = [s for s in skills if skill_exists(s, vars_["_ROOT"])]
    skills_block = ""
    if skills:
        names = ", ".join(f"`{s}`" for s in skills)
        skills_block = (f"# Skills\nLoad {names} with the `skill` tool when the task matches it. "
                        f"If it is not in the advertised skill list, continue without it.\n\n")
    specifics = cfg.get("specifics", {}).get(role, "").strip()
    spec_block = f"# Project specifics (verified for {cfg['project']})\n\n{specifics}\n\n" if specifics else ""
    text = render_text(text, {
        **vars_, "MODEL_LINE": model_line, "SKILLS_BLOCK": skills_block,
        "PERMISSIONS_BLOCK": permission_block(role, cfg, vars_["_DOCS_RESOURCE"], vars_["_MEMORY_RESOURCE"]),
        "LEGACY_PERMISSION": legacy_permission_block(role, cfg, vars_["_DOCS_RESOURCE"], vars_["_MEMORY_RESOURCE"]),
        "SPECIFICS": spec_block, "PROTOCOL": protocol(role, cfg, vars_),
    })
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def check_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return f"{path.name}: no frontmatter"
    fm = m.group(1) + "\n"
    problems = []
    # A `permission:` map is the deliberate V1 fallback (compat_v1). V2 files must use
    # `permissions:`; a V1-style `tools:` list is a porting mistake either way.
    permission_map = re.search(r"^permission:\n((?:  [a-z_]+:(?: .*)?\n|    .*\n)+)", fm, re.M)
    if permission_map:
        fm = fm.replace(permission_map.group(0), "")
    kv = dict(re.findall(r"^([a-zA-Z_-]+):\s*(.*)$", fm, re.M))
    if path.parent.name == "agents":
        if not kv.get("description"):
            problems.append("missing description")
        d = kv.get("description", "")
        if not d.startswith('"') and (" #" in d or ": " in d):
            problems.append("description has YAML hazard (' #' or ': ') and is not quoted")
        if kv.get("mode") not in VALID_MODES:
            problems.append(f"mode={kv.get('mode')!r} (expected one of {sorted(VALID_MODES)})")
        if kv.get("model") and not MODEL_RE.match(kv["model"].strip('"')):
            problems.append(f"model={kv.get('model')!r} is not provider/model[#variant]")
        for key in sorted(FORBIDDEN_AGENT_KEYS & set(kv)):
            problems.append(f"deprecated/unsupported key: {key}")
        if "permissions:" in fm:
            body = fm.split("permissions:", 1)[1]
            if not re.search(r"^\s+- action:", body, re.M):
                problems.append("permissions must be a list of {action, resource, effect}")
    if path.parent.name == "commands":
        for key in sorted(FORBIDDEN_COMMAND_KEYS & set(kv)):
            problems.append(f"unsupported command key: {key}")
        body = text[m.end():].strip()
        if not body:
            problems.append("empty command body")
    if "{{" in text:
        problems.append("unrendered placeholder")
    return f"{path.name}: {', '.join(problems)}" if problems else None


def write(path, content, force, log):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        log.append(f"SKIP  {path} (exists; use --force)"); return
    if path.exists() and force:
        shutil.copy(path, str(path) + ".bak")
    path.write_text(content, encoding="utf-8")
    log.append(f"WROTE {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--only")
    ap.add_argument("--scope", help="comma-separated: agents, commands, docs, all. "
                                    "Default: everything, or agents only when --only is given.")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    cfg = json.loads(pathlib.Path(a.config).read_text(encoding="utf-8"))
    root = pathlib.Path(a.out or cfg["project_root"])
    docs = pathlib.Path(cfg.get("docs_dir") or root / "docs")
    lang = cfg.get("report_language", "English")
    ctx_name = cfg.get("context_file", "PROJECT-CONTEXT.md")
    # Paths written into agents are RELATIVE to project_root by default (portable across machines/users);
    # set "absolute_paths": true in the config to keep absolute paths.
    absolute = bool(cfg.get("absolute_paths"))

    def P(x):
        """Path as it will appear inside a rendered agent/doc — always forward slashes.

        These strings become markdown links and arguments the agent hands to its tools.
        os.path.relpath returns backslashes on Windows, so without the normalisation an
        agent rendered there gets `docs\\PROJECT-CONTEXT.md`, which is neither a working
        link nor a path the tools accept. Config-supplied paths (repos[].path) get the
        same treatment, because a config written on Windows is rendered elsewhere too.
        """
        s = str(x)
        if not absolute and os.path.isabs(s):
            s = os.path.relpath(s, str(root))
        return s.replace("\\", "/")

    def resource(x):
        """Permission resources must be either Location-relative or absolute.

        A docs folder outside project_root cannot be expressed as `../shared/docs` in a
        permission pattern, so it is rendered as an absolute path instead.
        """
        x = pathlib.Path(x).resolve()
        try:
            rel = x.relative_to(root.resolve())
        except ValueError:
            return str(x).replace("\\", "/")
        return str(rel).replace("\\", "/")

    memory_root = root / MEMORY_DIR
    vars_ = {
        "PROJECT": cfg["project"], "PROJECT_ROOT": P(root) if absolute else ".", "DOCS_DIR": P(docs),
        "CONTEXT_PATH": P(docs / ctx_name), "LEARNINGS_PATH": P(docs / "LEARNINGS.md"),
        "BACKLOG_PATH": P(docs / "product" / "BACKLOG.md"), "TEAM_PATH": P(docs / "TEAM.md"),
        "MEMORY_ROOT": P(memory_root) if absolute else MEMORY_DIR, "LANG": lang,
        "LANG_RULE": f"Reports and documents addressed to the owner are written in {lang}; code identifiers, paths, commands, and HTTP details stay in English.",
        "DATE": datetime.date.today().isoformat(),
        "_ROOT": str(root), "_DOCS_RESOURCE": resource(docs),
    }
    if a.check:
        probs = [p for p in (check_frontmatter(f) for f in sorted((root / AGENT_DIR).glob("*.md"))) if p]
        probs += [p for p in (check_frontmatter(f) for f in sorted((root / COMMAND_DIR).glob("*.md"))) if p]
        n_agents = len(list((root / AGENT_DIR).glob("*.md")))
        n_commands = len(list((root / COMMAND_DIR).glob("*.md")))
        print("\n".join(probs) if probs else
              f"OK: {n_agents} agents, {n_commands} commands, no frontmatter problems")
        sys.exit(1 if probs else 0)
    scope = parse_scope(a.scope, a.only)
    roles = ([a.only] if a.only else cfg["roles"]) if "agents" in scope else []
    log, written = [], []
    for role in roles:
        dest = root / AGENT_DIR / f"{role}.md"
        role_vars = {**vars_, "_MEMORY_RESOURCE": resource(memory_root / role)}
        write(dest, render_agent(role, cfg, role_vars), a.force, log)
        written.append(dest)
    if "agents" in scope:
        for role in cfg["roles"]:
            (memory_root / role).mkdir(parents=True, exist_ok=True)
    if "commands" in scope:
        for src in sorted((T / "commands").glob("*.md")):
            # skip pipelines whose roles are absent
            need = {"test-all": {"api-tester", "e2e-tester", "mobile-tester", "web-tester"}, "security-audit": {"security-engineer"},
                    "release": {"devops-engineer", "tech-writer"}, "prd": {"product-manager"}, "adr": {"architect"}, "review": {"code-reviewer"}}
            if src.stem in need and not (need[src.stem] & set(cfg["roles"])):
                log.append(f"SKIP  command {src.stem} (no matching roles)"); continue
            text = render_text(src.read_text(encoding="utf-8"), {**vars_, "ROLES": ", ".join(cfg["roles"]),
                                                  "TESTERS": ", ".join(r for r in cfg["roles"] if r.endswith("-tester"))})
            dest = root / COMMAND_DIR / src.name
            write(dest, text, a.force, log)
            written.append(dest)
    if "docs" in scope:
        # These four are hand-filled after init; re-rendering them resets them to TODO
        # scaffolds (a .bak is kept). Upgrades use --scope agents,commands to skip them.
        repo_rows = "\n".join(f"| {r['name']} | `{P(r['path'])}` | {r.get('stack','TODO')} | {' · '.join('`'+c+'`' for c in r.get('checks', [])) or 'TODO'} |" for r in cfg.get("repos", []))
        def model_cell(role):
            m = model_for(role, cfg)
            tier = tier_of(role)
            effort = PROFILES.get(cfg.get("profile", "balanced"), PROFILES["balanced"])[tier]
            return f"{m} ({tier} · {effort} effort)" if m else f"inherit ({tier} · {effort} effort)"
        role_rows = "\n".join(f"| `{r}` | {CATEGORY[r]} | {model_cell(r)} |" for r in cfg["roles"])
        dvars = {**vars_, "REPO_TABLE": repo_rows or "| TODO | | | |", "ROLE_TABLE": role_rows,
                 "PROFILE": cfg.get("profile", "balanced")}
        for src in sorted((T / "docs").rglob("*.md")):
            rel = src.relative_to(T / "docs")
            if rel.name == "PROJECT-CONTEXT.md": rel = rel.with_name(ctx_name)
            write(docs / rel, render_text(src.read_text(encoding="utf-8"), dvars), a.force, log)
    print("\n".join(log))
    probs = [p for p in (check_frontmatter(f) for f in written if f.exists()) if p]
    print("CHECK:", ("; ".join(probs) if probs else "frontmatter OK") if written else "nothing to check")


if __name__ == "__main__":
    main()
