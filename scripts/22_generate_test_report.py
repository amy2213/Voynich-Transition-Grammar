#!/usr/bin/env python3
"""Run both supported test entry points and write a machine-readable report."""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
JUNIT = RESULTS / "test_report.junit.xml"
REPORT = RESULTS / "test_report.json"
TEST_FILE = ROOT / "tests" / "test_canonical_values.py"


def run(command):
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.returncode, result.stdout


def main():
    RESULTS.mkdir(exist_ok=True)
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-ra",
        str(TEST_FILE),
        f"--junitxml={JUNIT}",
    ]
    pytest_rc, pytest_output = run(pytest_cmd)
    suite = ElementTree.parse(JUNIT).getroot().find("testsuite")
    pytest_counts = {
        key: int(suite.attrib.get(key, 0))
        for key in ("tests", "failures", "errors", "skipped")
    }
    pytest_counts["passed"] = (
        pytest_counts["tests"]
        - pytest_counts["failures"]
        - pytest_counts["errors"]
        - pytest_counts["skipped"]
    )
    warning_match = re.search(r"(\d+) warnings?", pytest_output)
    pytest_counts["warnings"] = int(warning_match.group(1)) if warning_match else 0

    direct_cmd = [sys.executable, str(TEST_FILE)]
    direct_rc, direct_output = run(direct_cmd)
    ran = re.search(r"Ran (\d+) tests?", direct_output)
    direct_tests = int(ran.group(1)) if ran else None

    report = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "pytest": {
            "command": "python -m pytest -ra tests/test_canonical_values.py "
                       "--junitxml=results/test_report.junit.xml",
            "exit_code": pytest_rc,
            **pytest_counts,
        },
        "direct_python": {
            "command": "python tests/test_canonical_values.py",
            "exit_code": direct_rc,
            "tests": direct_tests,
            "passed": direct_tests if direct_rc == 0 else None,
        },
        "complete": pytest_rc == 0 and direct_rc == 0
                    and direct_tests == pytest_counts["tests"],
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(pytest_output, end="")
    print(direct_output, end="")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0 if report["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
