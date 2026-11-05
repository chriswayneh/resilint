# DOC-FMT-02: DataGrant README format

## Scope and authority

The user requested DataGrant's format for the Resilint GitHub page before release, explicitly limiting the request to format. This resumes presentation work only; the paused release/security-remediation sequence stays paused. This is one documentation task outside the original 38 product tasks.

Base: `ed501a9ddc9f8e55f3a045ccad6a9aee733a1dd9`. Reference: [DataGrant README](https://github.com/chriswayneh/datagrant/blob/2ab4ee601a979d9f05f707848256d412c0fc717f/README.md) and its banner at that revision. Preserve the original checkout, prior DOC-FMT-01 draft, unfinished R-2 work and all existing artifacts. No additional ancestor or nested AGENTS.md was found; root instructions apply.

## Technical design

Keep the existing Resilint SVG banner: it already has DataGrant's centered navy/blue/teal presentation. Use the same Docs / Security / Roadmap / Releases navigation, followed by description, truthful release status, personal-repository note, Demo, Features, Architecture, Quick start, CLI at a glance, Limits, Documentation, Contributing, How this project is built, and License.

Format current feature statements as checklists while retaining released versus development-only availability. Put lengthy example data/captured output, business context, audience/evidence table and GRC discussion in accessible native GitHub details elements. Keep the existing wording, commands, historical-output date, draft/legal/export limits and old heading anchors. The concise demo command block stays visible. Repair the detached documentation table row by using grouped guide links in DataGrant's list format.

Move the existing future-PyPI install paragraph to Quick start, keeping its explicit post-publication condition. Do not create an animation, change the banner, invent demo output, copy DataGrant product claims or alter the roadmap presentation/counts.

Only README.md, its documentation-only Unreleased changelog entry, this task design/plan and append-only audit records are in scope. No runtime, tests, dependencies, workflow, version, settings, account, tag or release changes.

## Execution and acceptance

1. Record actual user request and Codex's scope/design decision before construction; do not attribute a design approval or independent review to the user or dot.
2. Apply a bounded Markdown reorganization with balanced details elements and unchanged demo data/output; preserve existing section anchors and links.
3. Verify required local gates (Ruff, mypy, full pytest, links and whitespace), complete exact-head diff privacy/security review, and desktop/narrow rendering. This task adds no implementation-mirroring tests.
4. Record measured outcomes and any limitations. Stage explicit task paths only and create a reviewable task commit/PR under existing authorization; no release activity. Hosted checks must pass on the exact published head before any merge.
5. Subsequent user direction asks to keep work going toward v1 tonight after the format fixes are in place. Complete this task and passing review/checks first; ordinary accepted merges use the existing v1 authorization. Tagging/publication belongs to the later release task and its gates.

The old paused release findings remain open and are not remediated or dismissed by this task. The user's subsequent instruction resumes that sequence only after this format task is in place. Rollback, if requested, is an ordinary scoped commit.
