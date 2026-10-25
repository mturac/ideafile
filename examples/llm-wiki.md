---
goal: A personal wiki that an LLM agent keeps up to date from my notes folder
constraints:
  - Plain markdown files on disk, no database
  - Works with any LLM CLI agent
  - Never deletes user-written notes
acceptance:
  - Running the update step creates or updates an index.md linking every note
  - Each generated page cites the source note paths it was built from
  - A dry-run flag prints planned changes without writing files
tools:
  - shell
  - filesystem
non_goals:
  - A web UI
---

# LLM wiki

Share this idea, not the code: your agent builds a version that fits your own folder layout.
