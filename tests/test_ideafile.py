import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from ideafile.cli import main
from ideafile.core import load, to_prompt

EX = Path(__file__).resolve().parent.parent / "examples"


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = main(list(args))
    return rc, out.getvalue(), err.getvalue()


class LintTests(unittest.TestCase):
    def test_valid_passes(self):
        rc, out, _ = run("lint", str(EX / "llm-wiki.md"))
        self.assertEqual(rc, 0)
        self.assertIn("ok", out)

    def test_invalid_fails(self):
        rc, _, err = run("lint", str(EX / "invalid-missing-acceptance.md"))
        self.assertEqual(rc, 1)
        self.assertIn("acceptance", err)
        self.assertIn("constraints is empty", err)

    def test_missing_goal(self):
        _, res = load("---\nacceptance:\n  - x\n---\n")
        self.assertIn("missing required field: goal", res.errors)

    def test_no_frontmatter(self):
        _, res = load("# just markdown\n")
        self.assertFalse(res.ok)


class PromptTests(unittest.TestCase):
    def test_contains_acceptance_lines(self):
        idea, res = load((EX / "llm-wiki.md").read_text())
        self.assertTrue(res.ok)
        p = to_prompt(idea)
        for a in idea.acceptance:
            self.assertIn(a, p)
        self.assertIn(idea.goal, p)
        self.assertIn("Never deletes user-written notes", p)

    def test_cli_to_prompt_fails_on_invalid(self):
        rc, _, _ = run("to-prompt", str(EX / "invalid-missing-acceptance.md"))
        self.assertEqual(rc, 1)


class InitTests(unittest.TestCase):
    def test_init_scaffold_lints(self):
        with tempfile.TemporaryDirectory() as d:
            cwd = os.getcwd()
            os.chdir(d)
            try:
                rc, _, _ = run("init", "demo")
                self.assertEqual(rc, 0)
                self.assertEqual(run("lint", "demo.md")[0], 0)
                self.assertEqual(run("init", "demo")[0], 1)
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
