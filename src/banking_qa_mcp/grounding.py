"""Deterministic, conservative grounding checks for synthetic AI-agent responses.

This is an exact-claim evidence matcher, not a semantic entailment model.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

CORPUS = Path(__file__).resolve().parents[2] / "data" / "agent_evaluations.json"
_TOKEN = re.compile(r"[a-z0-9]+")
_CITATION = re.compile(r"\[([A-Za-z0-9_-]+)\]")


def _normalize(value: str) -> str:
    return " ".join(_TOKEN.findall(value.lower()))


def _validate_case(case: dict) -> None:
    if not isinstance(case, dict):
        raise ValueError("case must be an object")
    if not isinstance(case.get("case_id"), str) or not case["case_id"].strip():
        raise ValueError("case_id must be a non-empty string")
    if not isinstance(case.get("claims"), list) or not case["claims"]:
        raise ValueError("claims must be a non-empty list")
    if not isinstance(case.get("sources"), list):
        raise ValueError("sources must be a list")
    ids = set()
    for source in case["sources"]:
        if not isinstance(source, dict) or not isinstance(source.get("id"), str) or not isinstance(source.get("text"), str):
            raise ValueError("each source needs string id and text")
        if not source["id"] or source["id"] in ids:
            raise ValueError("source ids must be unique and non-empty")
        ids.add(source["id"])
    for claim in case["claims"]:
        if not isinstance(claim, dict) or not isinstance(claim.get("text"), str) or not claim["text"].strip():
            raise ValueError("each claim needs non-empty text")
        if not isinstance(claim.get("citations"), list) or any(not isinstance(c, str) for c in claim["citations"]):
            raise ValueError("each claim needs a list of citation ids")


def evaluate_grounding(case: dict) -> dict:
    """Evaluate explicit atomic claims against cited source text.

    A claim passes only when its normalized full text is a contiguous substring
    of at least one cited source. This intentionally produces false negatives for
    paraphrases and does not prove factual truth or semantic entailment.
    """
    _validate_case(case)
    sources = {s["id"]: s["text"] for s in case["sources"]}
    results = []
    for index, claim in enumerate(case["claims"], 1):
        cited = list(dict.fromkeys(claim["citations"]))
        unknown = [c for c in cited if c not in sources]
        valid = [c for c in cited if c in sources]
        normalized = _normalize(claim["text"])
        supporting = [c for c in valid if normalized and normalized in _normalize(sources[c])]
        if unknown:
            status = "INVALID_CITATION"
        elif not cited:
            status = "MISSING_CITATION"
        elif supporting:
            status = "SUPPORTED_EXACT"
        else:
            status = "NOT_VERIFIED"
        results.append({"claim_number": index, "claim": claim["text"], "status": status,
                        "citations": cited, "supporting_sources": supporting,
                        "unknown_citations": unknown})
    counts = {status: sum(r["status"] == status for r in results) for status in
              ("SUPPORTED_EXACT", "NOT_VERIFIED", "MISSING_CITATION", "INVALID_CITATION")}
    total = len(results)
    return {"case_id": case["case_id"], "verdict": "PASS" if counts["SUPPORTED_EXACT"] == total else "REVIEW",
            "total_claims": total, "supported_claims": counts["SUPPORTED_EXACT"],
            "exact_support_rate_percent": round(100 * counts["SUPPORTED_EXACT"] / total, 1),
            "counts": counts, "claim_results": results,
            "method": "normalized contiguous-text matching against explicitly cited sources",
            "limitations": "Not semantic entailment or factual verification; paraphrases may be flagged and copied falsehoods may pass."}


def load_cases(path: str | Path | None = None) -> list[dict]:
    filepath = Path(path) if path is not None else CORPUS
    data = json.loads(filepath.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("evaluation corpus must be a list")
    for case in data:
        _validate_case(case)
    ids = [c["case_id"] for c in data]
    if len(ids) != len(set(ids)):
        raise ValueError("case_id values must be unique")
    return data


def list_grounding_cases() -> list[dict]:
    return [{"case_id": c["case_id"], "scenario": c.get("scenario", "")} for c in load_cases()]


def evaluate_grounding_case(case_id: str) -> dict:
    for case in load_cases():
        if case["case_id"] == case_id:
            return evaluate_grounding(case)
    raise ValueError(f"Unknown grounding case_id: {case_id}")


def evaluate_grounding_suite() -> dict:
    results = [evaluate_grounding(c) for c in load_cases()]
    return {"total_cases": len(results), "passed": sum(r["verdict"] == "PASS" for r in results),
            "needs_review": sum(r["verdict"] == "REVIEW" for r in results), "results": results}
