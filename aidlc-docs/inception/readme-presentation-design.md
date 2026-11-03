# README presentation alignment: design

Separate documentation task, not a roadmap product task. Requested by the user; no product behavior changes.

- Goal: give resilint the same presentation family as the author's datagrant repository (banner, badges, reader journey) while keeping resilint's own purpose, limits and security guidance.
- Changes: new self-contained `docs/assets/banner.svg` (no scripts, remote fonts or external resources); README reordered to Demo, Features, Architecture, Quick start, CLI at a glance, Limits, Documentation, Contributing, How this project is built, License; detailed sections moved verbatim to `docs/reference.md` with compatibility anchors in the README; one internal link in `docs/ci.md` repointed.
- Release truth: v0.4.0 is the latest release; v1 is unreleased; no PyPI package exists. Features only on `main` are labeled development-only.
- Demo: existing text demo re-run against the v0.4.0 tag with its fictional register; output matched. GIF deferred to conserve effort.
- Out of scope: code, dependencies, workflows, settings, visibility, tags, releases.
