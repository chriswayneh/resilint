"""Run the six required scanner controls, failing on skips or incomplete outcomes."""

import os
import sys
from collections import Counter
from pathlib import Path

TEST_FILE = "tests/test_security_ci.py"
EXPECTED = (
    f"{TEST_FILE}::test_real_gitleaks_history_redaction_and_ignore_resistance",
    f"{TEST_FILE}::test_real_audit_cli_with_mocked_advisories[clean-0]",
    f"{TEST_FILE}::test_real_audit_cli_with_mocked_advisories[vulnerable-1]",
    f"{TEST_FILE}::test_real_audit_cli_with_mocked_advisories[missing-1]",
    f"{TEST_FILE}::test_real_audit_cli_with_mocked_advisories[outage-1]",
    f"{TEST_FILE}::test_checksum_failure_prevents_acceptance",
)
TOOL_VARIABLES = (
    "RESILINT_TEST_GITLEAKS", "RESILINT_TEST_AUDIT_PYTHON", "RESILINT_TEST_BASH",
)


def validate_tools(environment):
    for name in TOOL_VARIABLES:
        value = environment.get(name, "")
        path = Path(value)
        if not value or not path.is_absolute() or not path.is_file() or not os.access(path, os.X_OK):
            raise ValueError(f"{name} must name an absolute executable file")


class ScannerControlGate:
    def __init__(self, expected=EXPECTED):
        self.expected = tuple(expected)
        self.collected = None
        self.reports = {}
        self.invalid = False

    def pytest_collection_finish(self, session):
        self.collected = [item.nodeid for item in session.items]

    def pytest_collectreport(self, report):
        if report.failed or report.skipped:
            self.invalid = True

    def pytest_runtest_logreport(self, report):
        key = (report.nodeid, report.when)
        if (report.nodeid not in self.expected or report.when not in ("setup", "call", "teardown")
                or key in self.reports or not report.passed or hasattr(report, "wasxfail")):
            self.invalid = True
        self.reports[key] = report.outcome

    def complete(self):
        expected_reports = {(node, phase) for node in self.expected
                            for phase in ("setup", "call", "teardown")}
        return (not self.invalid and self.collected is not None
                and len(set(self.expected)) == len(self.expected)
                and Counter(self.collected) == Counter(self.expected)
                and set(self.reports) == expected_reports
                and all(outcome == "passed" for outcome in self.reports.values()))

    def pytest_sessionfinish(self, session, exitstatus):
        if exitstatus != 0 or not self.complete():
            session.exitstatus = 1


def main():
    try:
        validate_tools(os.environ)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    import pytest

    gate = ScannerControlGate()
    result = pytest.main(["-q", "-p", "no:cacheprovider", *EXPECTED], plugins=[gate])
    if result != 0 or not gate.complete():
        print("Scanner controls require all six unique cases to pass every phase without skips.",
              file=sys.stderr)
        return 1
    print("Scanner controls: all six cases passed collection, setup, call and teardown.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
