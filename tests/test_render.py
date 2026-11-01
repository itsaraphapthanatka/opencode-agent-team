r"""Regression tests for scripts/render.py (OpenCode port).

The renderer used to emit Claude Code files (`.claude/agents`, `tools:`, `effort:`,
`name:`) and two encoding/path bugs made it unusable on a Thai-locale Windows
machine. Both were invisible on a UTF-8 machine:

1. **Default encoding.** Every read/write used the locale encoding. With
   `locale.getpreferredencoding(False) == "cp874"` the very first template read raised
   `UnicodeDecodeError: 'charmap' codec can't decode byte 0x81`.
2. **Backslash paths.** `os.path.relpath` returns `docs\PROJECT-CONTEXT.md` on Windows,
   which is neither a working markdown link nor a path a tool accepts.

The encoding test uses `-X warn_default_encoding -W error::EncodingWarning`, which turns
any encoding-less `open()`/`read_text()`/`write_text()` into a hard error on every OS.

Run: python -m unittest discover -s tests
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
RENDER = REPO / "scripts" / "render.py"
ROLES = ["architect", "backend-dev", "code-reviewer", "api-tester", "tech-writer"]


class _Rendered(unittest.TestCase):
    """Render a throwaway project once per test class."""

    extra_args: tuple[str, ...] = ()
    config_extra: dict = {}
    roles: list[str] = ROLES
    setup_project = None
    docs_outside = False

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = pathlib.Path(tempfile.mkdtemp(prefix="agent-team-test-")).resolve()
        cls.addClassCleanup(shutil.rmtree, cls.tmp, ignore_errors=True)
        cls.project = cls.tmp / "proj"
        cls.docs = (cls.tmp / "shared" / "docs") if cls.docs_outside else (cls.project / "docs")
        cls.docs.mkdir(parents=True)
        if cls.setup_project:
            cls.setup_project(cls.project)
        cfg = {
            "project": "demo",
            "project_root": str(cls.project),
            "docs_dir": str(cls.docs),
            "profile": "balanced",
            "roles": cls.roles,
            "repos": [{"name": "app", "path": str(cls.project), "stack": "python"}],
            **cls.config_extra,
        }
        cls.config = cls.tmp / "agent-team.json"
        cls.config.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
        # An empty HOME keeps the machine's globally installed skills out of the render,
        # so the tests assert the renderer's logic rather than this laptop's setup.
        cls.home = cls.tmp / "home"
        cls.home.mkdir()
        cls.result = cls._render(*cls.extra_args)

    @classmethod
    def _render(cls, *extra: str) -> subprocess.CompletedProcess:
        env = {**os.environ, "HOME": str(cls.home), "USERPROFILE": str(cls.home),
               "XDG_CONFIG_HOME": str(cls.home / ".config")}
        return subprocess.run(
            [sys.executable, "-X", "warn_default_encoding",
             "-W", "error::EncodingWarning",
             str(RENDER), "--config", str(cls.config), *extra],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)

    @property
    def agents(self) -> list[pathlib.Path]:
        return sorted((self.project / ".opencode" / "agents").glob("*.md"))

    @property
    def commands(self) -> list[pathlib.Path]:
        return sorted((self.project / ".opencode" / "commands").glob("*.md"))

    def agent(self, role: str) -> str:
        return (self.project / ".opencode" / "agents" / f"{role}.md").read_text(encoding="utf-8")


class TestItRunsWithoutRelyingOnTheLocaleEncoding(_Rendered):

    def test_it_exits_zero(self):
        self.assertEqual(self.result.returncode, 0,
                         f"stdout:\n{self.result.stdout}\nstderr:\n{self.result.stderr}")

    def test_no_read_or_write_used_the_default_encoding(self):
        self.assertNotIn("EncodingWarning", self.result.stderr)

    def test_it_wrote_one_agent_per_role_in_the_opencode_layout(self):
        self.assertEqual([p.stem for p in self.agents], sorted(ROLES))
        self.assertFalse((self.project / ".claude").exists(),
                         "the OpenCode port must not write a .claude directory")

    def test_every_file_it_wrote_is_valid_utf8(self):
        for path in self.agents + self.commands:
            with self.subTest(path=path.name):
                path.read_bytes().decode("utf-8")   # raises if it is not

    def test_the_non_ascii_text_in_the_templates_survived(self):
        source = (REPO / "templates" / "agents" / "architect.md").read_text(encoding="utf-8")
        marks = {c for c in source if ord(c) > 127}
        self.assertTrue(marks, "template has no non-ASCII left to check")
        self.assertTrue(marks & set(self.agent("architect")),
                        "none of the template's non-ASCII characters reached the output")


class TestOpenCodeFrontmatter(_Rendered):

    def test_every_agent_is_a_subagent(self):
        for path in self.agents:
            with self.subTest(path=path.name):
                self.assertIn("mode: subagent\n", path.read_text(encoding="utf-8"))

    def test_no_claude_code_keys_survive(self):
        for path in self.agents:
            text = path.read_text(encoding="utf-8")
            head = text.split("---\n", 2)[1]
            for key in ("name:", "tools:", "effort:", "memory:", "skills:"):
                with self.subTest(path=path.name, key=key):
                    self.assertNotIn(f"\n{key}", "\n" + head)

    def test_no_v1_permission_map_by_default(self):
        for path in self.agents:
            with self.subTest(path=path.name):
                self.assertNotIn("\npermission:\n", path.read_text(encoding="utf-8"))

    def test_descriptions_are_quoted(self):
        for path in self.agents:
            with self.subTest(path=path.name):
                line = next(l for l in path.read_text(encoding="utf-8").splitlines()
                            if l.startswith("description:"))
                self.assertTrue(line.split(":", 1)[1].strip().startswith('"'), line)

    def test_commands_have_no_argument_hint(self):
        for path in self.commands:
            with self.subTest(path=path.name):
                self.assertNotIn("argument-hint", path.read_text(encoding="utf-8"))

    def test_commands_talk_to_the_opencode_tools(self):
        for path in self.commands:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotIn("Agent tool", text)
                self.assertNotIn("AskUserQuestion", text)
                self.assertNotIn("general-purpose", text)
                self.assertNotIn(".claude", text)

    def test_rendered_files_have_no_claude_or_v1_leftovers(self):
        for path in self.agents + self.commands + list((self.project / "docs").rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotIn(".claude", text)
                self.assertNotIn("CLAUDE_PROJECT_DIR", text)
                self.assertNotIn("{{", text)


class TestPermissions(_Rendered):

    def test_a_code_writer_may_edit_repo_files(self):
        self.assertNotIn("action: edit", self.agent("architect"))

    def test_a_docs_only_role_can_write_docs_and_memory_but_not_code(self):
        text = self.agent("api-tester")
        self.assertIn('action: edit\n    resource: "*"\n    effect: deny', text)
        self.assertIn('resource: "docs/**"\n    effect: allow', text)
        self.assertIn('resource: ".opencode/agent-memory/api-tester/**"\n    effect: allow', text)

    def test_the_code_reviewer_writes_nothing(self):
        text = self.agent("code-reviewer")
        self.assertIn('action: edit\n    resource: "*"\n    effect: deny', text)
        self.assertNotIn('resource: "docs/**"', text)
        self.assertIn('resource: ".opencode/agent-memory/code-reviewer/**"\n    effect: allow', text)

    def test_a_role_without_web_tools_gets_web_denied(self):
        self.assertIn("action: webfetch", self.agent("api-tester"))
        self.assertIn("action: websearch", self.agent("api-tester"))
        self.assertNotIn("action: webfetch", self.agent("architect"))

    def test_every_subagent_denies_nesting(self):
        for path in self.agents:
            with self.subTest(path=path.name):
                self.assertIn('action: subagent\n    resource: "*"\n    effect: deny',
                              path.read_text(encoding="utf-8"))


class TestModels(_Rendered):

    def test_no_model_by_default_so_the_session_model_is_inherited(self):
        for path in self.agents:
            with self.subTest(path=path.name):
                self.assertNotIn("\nmodel:", "\n" + path.read_text(encoding="utf-8"))

    def test_the_team_doc_says_inherit(self):
        text = (self.project / "docs" / "TEAM.md").read_text(encoding="utf-8")
        self.assertIn("inherit (heavy", text)
        self.assertIn("inherit (light", text)


class TestModelTiers(_Rendered):
    config_extra = {"models": {"heavy": "anthropic/claude-opus-4-5#high",
                               "other": "anthropic/claude-sonnet-4-5#high",
                               "light": "anthropic/claude-haiku-4-5#high"}}

    def test_heavy_roles_get_the_heavy_model(self):
        self.assertIn("model: anthropic/claude-opus-4-5#high", self.agent("architect"))

    def test_other_roles_get_the_other_model(self):
        # api-tester is not heavy and not light
        self.assertIn("model: anthropic/claude-sonnet-4-5#high", self.agent("api-tester"))

    def test_light_roles_get_the_light_model(self):
        self.assertIn("model: anthropic/claude-haiku-4-5#high", self.agent("tech-writer"))


class TestModelOverride(_Rendered):
    config_extra = {"models": {"heavy": "anthropic/claude-opus-4-5#high"},
                    "overrides": {"code-reviewer": {"model": "openai/gpt-5.1#max"}}}

    def test_the_override_wins_over_the_tier(self):
        self.assertIn("model: openai/gpt-5.1#max", self.agent("code-reviewer"))

    def test_other_roles_keep_their_tier(self):
        self.assertIn("model: anthropic/claude-opus-4-5#high", self.agent("architect"))


class TestSkillDiscovery(_Rendered):

    @staticmethod
    def setup_project(project: pathlib.Path) -> None:
        (project / ".opencode" / "skills" / "scrutinize").mkdir(parents=True)
        (project / ".opencode" / "skills" / "scrutinize" / "SKILL.md").write_text(
            "---\nname: scrutinize\ndescription: test\n---\n", encoding="utf-8")

    def test_an_installed_skill_is_referenced_with_the_skill_tool(self):
        self.assertIn("`scrutinize`", self.agent("architect"))
        self.assertIn("`skill` tool", self.agent("architect"))

    def test_a_missing_skill_is_not_mentioned(self):
        self.assertNotIn("debug-mantra", self.agent("backend-dev"))


class TestPathsAreForwardSlashOnly(_Rendered):

    def test_no_rendered_file_contains_a_backslash_path(self):
        for path in self.agents + self.commands + list((self.project / "docs").rglob("*.md")):
            with self.subTest(path=path.name):
                self.assertNotIn("\\", path.read_text(encoding="utf-8"),
                                 "backslash in a rendered file — links and tool arguments break on it")

    def test_the_context_path_is_written_with_slashes(self):
        self.assertIn("docs/PROJECT-CONTEXT.md", self.agent("architect"))


class TestAbsolutePathsModeIsNormalisedToo(_Rendered):
    config_extra = {"absolute_paths": True}

    def test_it_exits_zero(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)

    def test_absolute_paths_also_come_out_with_slashes(self):
        text = self.agent("architect")
        self.assertNotIn("\\", text)
        self.assertIn(str(self.project).replace("\\", "/"), text)

    def test_permissions_stay_location_relative(self):
        # OpenCode matches `edit` on a Location-relative path for internal files; only
        # paths outside the project are canonical absolute.
        self.assertIn('resource: "docs/**"', self.agent("api-tester"))


class TestV1Compat(_Rendered):
    """`compat_v1` is for installs that still run the V1 runner, which ignores V2
    `permissions`. The legacy `permission:` map is what V1 enforces."""

    config_extra = {"compat_v1": True}

    def test_the_code_reviewer_cannot_write(self):
        text = self.agent("code-reviewer")
        self.assertIn('  edit:\n    "*": deny', text)
        self.assertIn('    ".opencode/agent-memory/code-reviewer/**": allow', text)
        self.assertIn("  task: deny", text)

    def test_a_web_less_role_has_web_tools_disabled(self):
        text = self.agent("api-tester")
        self.assertIn("  webfetch: deny", text)
        self.assertIn("  websearch: deny", text)
        self.assertIn('    "docs/**": allow', text)

    def test_a_code_writer_keeps_edit(self):
        text = self.agent("architect")
        self.assertNotIn("  edit:", text)
        self.assertIn("  task: deny", text)

    def test_check_accepts_the_legacy_permission_map(self):
        out = self._render("--check")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)


class TestDocsOutsideTheProject(_Rendered):
    docs_outside = True

    def test_an_external_docs_folder_uses_an_absolute_permission_path(self):
        # A permission pattern cannot express `..`, so external docs must be absolute.
        external = str(self.docs).replace("\\", "/")
        self.assertIn(f'resource: "{external}/**"', self.agent("api-tester"))


class TestCheckMode(_Rendered):

    def test_check_passes_on_what_it_just_rendered(self):
        out = self._render("--check")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertNotIn("EncodingWarning", out.stderr)

    def test_check_catches_a_claude_code_key(self):
        target = self.project / ".opencode" / "agents" / "architect.md"
        target.write_text(target.read_text(encoding="utf-8").replace(
            "mode: subagent", "mode: subagent\ntools: Read, Bash"), encoding="utf-8")
        self.addCleanup(target.write_text,
                        target.read_text(encoding="utf-8").replace("\ntools: Read, Bash", ""),
                        encoding="utf-8")
        out = self._render("--check")
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("deprecated/unsupported key: tools", out.stdout)

    def test_check_catches_an_argument_hint(self):
        target = self.project / ".opencode" / "commands" / "review.md"
        original = target.read_text(encoding="utf-8")
        self.addCleanup(target.write_text, original, encoding="utf-8")
        target.write_text(original.replace("---\n", "---\nargument-hint: x\n", 1), encoding="utf-8")
        out = self._render("--check")
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("unsupported command key: argument-hint", out.stdout)


class TestCommandsMatchTheRoles(_Rendered):
    roles = ["architect", "backend-dev"]

    def test_pipelines_without_their_roles_are_skipped(self):
        names = {p.stem for p in self.commands}
        self.assertIn("adr", names)
        self.assertNotIn("security-audit", names)
        self.assertNotIn("test-all", names)


class TestUpgradeKeepsBackups(_Rendered):

    def test_a_second_run_without_force_overwrites_nothing(self):
        before = self.agent("architect")
        out = self._render()
        self.assertEqual(self.agent("architect"), before)
        self.assertIn("SKIP", out.stdout)

    def test_force_writes_a_backup(self):
        target = self.project / ".opencode" / "agents" / "architect.md"
        out = self._render("--force", "--scope", "agents", "--only", "architect")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertTrue(pathlib.Path(str(target) + ".bak").exists())


class TestMemoryDirectories(_Rendered):

    def test_every_role_gets_a_memory_directory(self):
        for role in ROLES:
            with self.subTest(role=role):
                self.assertTrue((self.project / ".opencode" / "agent-memory" / role).is_dir())


class TestTheSkillItself(unittest.TestCase):
    """The entry point is an OpenCode skill: no Claude Code argument handling."""

    def setUp(self):
        self.text = (REPO / "SKILL.md").read_text(encoding="utf-8")

    def test_it_has_the_opencode_frontmatter(self):
        self.assertTrue(self.text.startswith("---\n"))
        head = self.text.split("---\n", 2)[1]
        self.assertIn("name: agent-team", head)
        self.assertIn("description:", head)

    def test_it_does_not_use_claude_code_argument_syntax(self):
        self.assertNotIn("argument-hint", self.text)
        self.assertNotIn("$ARGUMENTS", self.text)
        self.assertNotIn("CLAUDE_", self.text)

    def test_the_optional_command_wrapper_is_opencode_shaped(self):
        text = (REPO / "extras" / "commands" / "agent-team.md").read_text(encoding="utf-8")
        self.assertNotIn("argument-hint", text)
        self.assertIn("$ARGUMENTS", text)
        self.assertIn("`skill` tool", text)


class TestTemplatesArePorted(unittest.TestCase):

    def test_no_claude_code_isms_survive_in_the_templates(self):
        bad = (".claude/", "AskUserQuestion", "general-purpose", "Agent tool",
               "argument-hint", "CLAUDE_")
        for path in sorted((REPO / "templates").rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            for needle in bad:
                with self.subTest(path=path.name, needle=needle):
                    self.assertNotIn(needle, text)


if __name__ == "__main__":
    unittest.main()
