"""Parsing, linting and prompt rendering for idea files (stdlib only)."""
from __future__ import annotations

from dataclasses import dataclass, field

LIST_FIELDS = ("constraints", "acceptance", "tools", "non_goals")
KNOWN = ("goal",) + LIST_FIELDS


class ParseError(ValueError):
    pass


def _scalar(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse a minimal YAML subset: `key: value`, `key:` + `- item` lists, `key: []`."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ParseError("missing YAML frontmatter (file must start with '---')")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise ParseError("unterminated frontmatter (no closing '---')") from None
    data: dict = {}
    key = None
    for n, raw in enumerate(lines[1:end], start=2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        s = raw.strip()
        if s.startswith("- "):
            if key is None or not isinstance(data.get(key), list):
                raise ParseError(f"line {n}: list item without a list key")
            data[key].append(_scalar(s[2:]))
            continue
        if ":" not in s:
            raise ParseError(f"line {n}: expected 'key: value'")
        k, v = s.split(":", 1)
        key, v = k.strip(), v.strip()
        if v == "":
            data[key] = []
        elif v == "[]":
            data[key] = []
        elif v.startswith("[") and v.endswith("]"):
            data[key] = [_scalar(x) for x in v[1:-1].split(",") if x.strip()]
        else:
            data[key] = _scalar(v)
    body = "\n".join(lines[end + 1:]).strip()
    return data, body


@dataclass
class Idea:
    goal: str = ""
    constraints: list = field(default_factory=list)
    acceptance: list = field(default_factory=list)
    tools: list = field(default_factory=list)
    non_goals: list = field(default_factory=list)
    body: str = ""


@dataclass
class LintResult:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def load(text: str) -> tuple[Idea | None, LintResult]:
    res = LintResult()
    try:
        data, body = parse_frontmatter(text)
    except ParseError as e:
        res.errors.append(str(e))
        return None, res
    goal = data.get("goal", "")
    if isinstance(goal, list):
        goal = " ".join(goal)
    if not goal:
        res.errors.append("missing required field: goal")
    lists = {}
    for f in LIST_FIELDS:
        v = data.get(f, [])
        if isinstance(v, str):
            v = [v]
        lists[f] = [x for x in v if x]
    if not lists["acceptance"]:
        res.errors.append("missing required field: acceptance (need at least one checkable item)")
    if not lists["constraints"]:
        res.warnings.append("constraints is empty; agents will make their own trade-offs")
    for k in data:
        if k not in KNOWN:
            res.warnings.append(f"unknown field: {k}")
    return Idea(goal=goal, body=body, **lists), res


def to_prompt(idea: Idea) -> str:
    out = ["You are building software from an idea file. Build a custom implementation "
           "that satisfies the goal and every acceptance criterion.", "", "## Goal", idea.goal]
    def sec(title, items, checkbox=False):
        if items:
            out.extend(["", f"## {title}"])
            out.extend((f"- [ ] {i}" if checkbox else f"- {i}") for i in items)
    sec("Constraints", idea.constraints)
    sec("Non-goals", idea.non_goals)
    sec("Tools available", idea.tools)
    if idea.body:
        out.extend(["", "## Context", idea.body])
    sec("Acceptance criteria (verify each before finishing)", idea.acceptance, True)
    out.extend(["", "When done, report how each acceptance criterion was verified."])
    return "\n".join(out) + "\n"


TEMPLATE = """---
goal: Describe in one sentence what {name} should achieve
constraints:
  - Python 3.12+, standard library only
  - Runs offline
acceptance:
  - "`{name} --help` exits 0"
  - A test suite passes with `python -m unittest`
tools:
  - shell
non_goals:
  - A GUI
---

# {name}

Free-form context for the agent: background, inspiration, examples.
"""
