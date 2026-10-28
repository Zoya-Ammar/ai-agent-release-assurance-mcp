import pytest
from banking_qa_mcp.grounding import (
    evaluate_grounding, evaluate_grounding_case, evaluate_grounding_suite, load_cases
)


def test_corpus_cases():
    assert len(load_cases()) == 6
    assert evaluate_grounding_case("AGENT-001")["verdict"] == "PASS"
    assert evaluate_grounding_case("AGENT-002")["claim_results"][0]["status"] == "NOT_VERIFIED"
    assert evaluate_grounding_case("AGENT-003")["claim_results"][0]["status"] == "MISSING_CITATION"
    assert evaluate_grounding_case("AGENT-004")["claim_results"][0]["status"] == "INVALID_CITATION"
    assert evaluate_grounding_case("AGENT-006")["verdict"] == "PASS"


def test_suite_totals():
    result = evaluate_grounding_suite()
    assert result["total_cases"] == 6
    assert result["passed"] == 2
    assert result["needs_review"] == 4


def test_no_cross_source_credit():
    case = {"case_id": "X", "sources": [
        {"id": "a", "text": "Cats are allowed"},
        {"id": "b", "text": "Dogs are allowed"}],
        "claims": [{"text": "Dogs are allowed", "citations": ["a"]}]}
    assert evaluate_grounding(case)["verdict"] == "REVIEW"


def test_invalid_input_and_unknown_case():
    with pytest.raises(ValueError, match="Unknown grounding"):
        evaluate_grounding_case("not-found")
    with pytest.raises(ValueError, match="claims"):
        evaluate_grounding({"case_id": "X", "sources": [], "claims": []})


def test_duplicate_ids_rejected(tmp_path):
    p = tmp_path / "cases.json"
    p.write_text('[{"case_id":"x","sources":[],"claims":[{"text":"hi","citations":[]}]},'
                 '{"case_id":"x","sources":[],"claims":[{"text":"hi","citations":[]}]}]')
    with pytest.raises(ValueError, match="unique"):
        load_cases(p)
