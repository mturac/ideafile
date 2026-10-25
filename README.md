# ideafile

A spec format plus a linter and prompt renderer for "idea files": share the **idea** (goal, constraints, acceptance criteria) so a coding agent can build a version that fits you, instead of passing around one-size-fits-all code.

Inspired by Andrej Karpathy's idea-file gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

Python 3.12+, standard library only, no dependencies.

## Format

Markdown with YAML frontmatter:

```markdown
---
goal: A personal wiki that an LLM agent keeps up to date from my notes folder
constraints:
  - Plain markdown files on disk, no database
acceptance:
  - Running the update step creates or updates an index.md linking every note
tools:          # optional
  - shell
non_goals:      # optional
  - A web UI
---

Free-form context for the agent.
```

| field | required | type |
|---|---|---|
| `goal` | yes | string |
| `acceptance` | yes | list of checkable strings |
| `constraints` | recommended (warns if empty) | list |
| `tools` | no | list |
| `non_goals` | no | list |

The parser handles a small YAML subset: `key: value`, block lists (`- item`), and inline lists (`[a, b]`).

## Usage

```bash
pip install git+https://github.com/mturac/ideafile   # or: python -m ideafile ...
ideafile init my-idea              # scaffold my-idea.md
ideafile lint examples/*.md        # exit 1 if goal/acceptance missing
ideafile to-prompt examples/llm-wiki.md | your-agent
```

## Examples

- `examples/llm-wiki.md`: valid
- `examples/invalid-missing-acceptance.md`: fails lint on purpose

## Develop

```bash
python -m unittest discover -s tests -v
```

## License

MIT
