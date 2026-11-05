# M0-1 follow-up: serialize drill-log target inspection

Evidence: PR #53 final-head CI run 41959175566, Windows/Python 3.10 job 127021167368, failed the existing six-writer test. One writer returned exit 2 with an Access is denied diagnostic for the drill log rather than lock contention. No data-loss success was observed; the original test correctly rejected that outcome.

The writer currently calls check_target on the log before acquiring its sidecar lock. Windows target inspection can briefly hold file handles while a cooperating writer replaces the log. Put all log-target validation and log access inside the writer critical section. Continue validating the sidecar target before opening it; validate the log immediately after lock acquisition and again before replacement. Preserve output-root, input-identity and symlink guards, the bounded contention timeout, atomic replacement and release in finally. Invalid log requests may leave the same persistent sidecar used for ordinary failed record attempts; they must not modify the source or target.

Add a deterministic regression that requires every log target check to occur while the sidecar lock is held. Keep the existing real concurrent-writer assertion unchanged. Run the relevant guard/error tests and repeated real Windows concurrency checks, then all required local/hosted gates, complete exact-head security review and one M0-1 follow-up PR. Do not accept arbitrary exit-2 errors, skip the failure, change a platform gate or retry CI to hide the issue.

No dependency, network, permission, settings or publication change. Preserve private failure logs locally and record only sanitized failure evidence publicly. Roll back only through ordinary commits; no cleanup or history rewriting.
