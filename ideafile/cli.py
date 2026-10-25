from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import TEMPLATE, load, to_prompt


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def cmd_lint(a) -> int:
    rc = 0
    for p in a.paths:
        _, res = load(_read(p))
        for w in res.warnings:
            print(f"{p}: warning: {w}", file=sys.stderr)
        for e in res.errors:
            print(f"{p}: error: {e}", file=sys.stderr)
        if res.ok:
            print(f"{p}: ok")
        else:
            rc = 1
    return rc


def cmd_to_prompt(a) -> int:
    idea, res = load(_read(a.path))
    if not res.ok:
        for e in res.errors:
            print(f"{a.path}: error: {e}", file=sys.stderr)
        return 1
    sys.stdout.write(to_prompt(idea))
    return 0


def cmd_init(a) -> int:
    path = Path(a.name if a.name.endswith(".md") else a.name + ".md")
    if path.exists() and not a.force:
        print(f"{path} exists (use --force)", file=sys.stderr)
        return 1
    path.write_text(TEMPLATE.format(name=path.stem), encoding="utf-8")
    print(f"created {path}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="ideafile", description="Lint and render idea files for coding agents.")
    ap.add_argument("--version", action="version", version=f"ideafile {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lint", help="validate idea file(s)")
    p.add_argument("paths", nargs="+")
    p.set_defaults(fn=cmd_lint)
    p = sub.add_parser("to-prompt", help="emit a single agent prompt")
    p.add_argument("path")
    p.set_defaults(fn=cmd_to_prompt)
    p = sub.add_parser("init", help="scaffold an example idea file")
    p.add_argument("name")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_init)
    a = ap.parse_args(argv)
    return a.fn(a)
