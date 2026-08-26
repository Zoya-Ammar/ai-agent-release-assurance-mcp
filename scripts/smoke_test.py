"""Dependency-free verification of the database and release-risk service."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from banking_qa_mcp.seed import seed
from banking_qa_mcp.service import failed_tests, regression_plan, release_readiness


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        os.environ["BANKING_QA_DB"] = str(Path(directory) / "smoke.db")
        seed()

        risky = release_readiness("REL-2026.08.1")
        assert risky["recommendation"] == "NO_GO"
        assert risky["risk_score"] == 100
        assert risky["test_pass_rate_percent"] == 62.5

        lower_risk = release_readiness("REL-2026.08.2")
        assert lower_risk["recommendation"] == "GO"
        assert lower_risk["risk_score"] == 7

        assert len(failed_tests("REL-2026.08.1", "critical")) == 1
        assert len(regression_plan("REL-2026.08.1", 2)["priority_tests"]) == 2

    print("Smoke test passed: database, scoring, filtering, and prioritization are valid.")


if __name__ == "__main__":
    main()
