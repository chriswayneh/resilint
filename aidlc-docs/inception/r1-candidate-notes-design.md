# R-1 follow-up: finalize rc1 release notes

Main `4ccd82ed1d4e0f97c4161ffcc9e23c2e5c8f1d8d` includes accepted presentation, private-output defaults and R-2's fictional-register validation. Before the first rc1 tag/publication, fold their three existing Unreleased bullets into the matching dated 1.0.0-rc1 sections and leave a fresh empty Unreleased heading. Preserve every historical bullet and all source/runtime/version/roadmap content.

This is one R-1 documentation follow-up under the user's actual continuing-v1 authority. It does not by itself create or publish a tag. No package version can be reused after publication; verify rc1 is still absent before later execution.

Record the actual design decision before editing, verify unchanged bullet multiset and metadata/tag helper, run required local and hosted gates, and review the complete exact diff. Commit/publish one small PR and merge only after all exact-head checks pass. Then independently verify merged-main CI, main full CodeQL, tag absence and current authority before a separately recorded candidate tag/publishing stage. Release artifacts must come from the trusted build-once pipeline with provenance/SBOM/checksum validation and normal protected environment gates.
