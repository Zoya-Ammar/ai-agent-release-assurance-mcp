import pytest

from banking_qa_mcp.seed import seed
from banking_qa_mcp.service import failed_tests, regression_plan, release_readiness


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    monkeypatch.setenv("BANKING_QA_DB", str(tmp_path / "test.db"))
    seed()


def test_risky_release_is_no_go():
    result = release_readiness("REL-2026.08.1")
    assert result["recommendation"] == "NO_GO"
    assert result["risk_score"] == 100
    assert "Open SEV1 defect" in result["blockers"]
    assert result["test_pass_rate_percent"] == 62.5


def test_lower_risk_release_is_go():
    result = release_readiness("REL-2026.08.2")
    assert result["recommendation"] == "GO"
    assert result["risk_score"] == 7
    assert result["blockers"] == []


def test_failed_tests_can_be_filtered():
    results = failed_tests("REL-2026.08.1", "critical")
    assert len(results) == 1
    assert results[0]["test_name"] == "Identity verification retry"


def test_regression_plan_is_bounded():
    result = regression_plan("REL-2026.08.1", 2)
    assert len(result["priority_tests"]) == 2
    assert result["priority_tests"][0]["test_name"] == "Identity verification retry"


def test_unknown_release_is_rejected():
    with pytest.raises(ValueError, match="Unknown release_id"):
        release_readiness("missing")
