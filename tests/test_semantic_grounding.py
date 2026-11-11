
from banking_qa_mcp.grounding import evaluate_grounding


def test_paraphrased_claim_needs_semantic_review():
    case = {
        "case_id": "SEMANTIC-001",
        "sources": [
            {
                "id": "DOC-001",
                "text": "The customer successfully authenticated."
            }
        ],
        "claims": [
            {
                "text": "The customer logged in successfully.",
                "citations": ["DOC-001"]
            }
        ]
    }

    result = evaluate_grounding(case)

    assert result["claim_results"][0]["status"] == "NOT_VERIFIED"
