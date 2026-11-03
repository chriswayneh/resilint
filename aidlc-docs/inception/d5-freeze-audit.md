# D-5 interface-freeze review

Scope: review and verify the existing D-5 draft prepared before workflow adoption. No retrospective design approval is claimed. Routine implementation-stage review is pending before merge.

The draft compares the v0.4.0 CLI with the proposed v1 surface, documents that no commands/flags/rule IDs are removed or deprecated, and adds smoke coverage for warning-free check, init, explain, export-roi and drill-record command paths. Python internals and experimental RoI mapping retain their documented exclusions. No runtime implementation, dependency, permission or output contract changes are proposed.

Execution: preserve the existing draft, integrate merged guidance without rewriting history, verify the interface comparison and five command paths, run required local/hosted gates, and present the exact head for routine review. Keep one D-5 PR; completion metadata takes effect only on authorized merge.

Acceptance: all 17 prior long flags and five report formats remain; all prior command paths and RL001–RL009 remain; additions are documented. No invented deprecation is introduced solely to exercise warnings. Future deprecations require positive warning/migration tests; current smoke tests require successful command completion and empty stderr.

Security: test-only writes use pytest temporary directories and fictional records. No network, real vendor data, PHI/PII, secrets, SQL, dependency or privilege changes. Preserve existing input/output guards and run the comprehensive regression suite. Review the complete diff before presentation, then retain exact-head review and passing hosted gates before any merge within the user's time-limited authorization.
