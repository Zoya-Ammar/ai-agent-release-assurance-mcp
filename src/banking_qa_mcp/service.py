from __future__ import annotations

from typing import Any

from banking_qa_mcp.database import row, rows

WEIGHTS = {"SEV1": 35, "SEV2": 18, "SEV3": 7, "SEV4": 2}


def list_releases() -> list[dict[str, Any]]:
    return rows("SELECT * FROM releases ORDER BY planned_date")


def failed_tests(release_id: str, criticality: str | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT test_name, suite, status, criticality, failure_message
        FROM test_results
        WHERE release_id = ? AND status IN ('FAILED', 'BLOCKED')
    """
    parameters: tuple[Any, ...] = (release_id,)
    if criticality:
        query += " AND criticality = ?"
        parameters += (criticality.upper(),)
    query += " ORDER BY CASE criticality WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 ELSE 3 END"
    return rows(query, parameters)


def defect_hotspots(release_id: str) -> list[dict[str, Any]]:
    return rows(
        """
        SELECT component, COUNT(*) AS open_defects,
               SUM(CASE severity WHEN 'SEV1' THEN 35 WHEN 'SEV2' THEN 18
                   WHEN 'SEV3' THEN 7 ELSE 2 END) AS weighted_risk
        FROM defects
        WHERE release_id = ? AND status != 'RESOLVED'
        GROUP BY component
        ORDER BY weighted_risk DESC, component
        """,
        (release_id,),
    )


def release_readiness(release_id: str) -> dict[str, Any]:
    release = row("SELECT * FROM releases WHERE release_id = ?", (release_id,))
    if not release:
        raise ValueError(f"Unknown release_id: {release_id}")

    tests = rows(
        """
        SELECT status, criticality, COUNT(*) AS count
        FROM test_results WHERE release_id = ? GROUP BY status, criticality
        """,
        (release_id,),
    )
    defects = rows(
        """
        SELECT severity, COUNT(*) AS count
        FROM defects WHERE release_id = ? AND status != 'RESOLVED' GROUP BY severity
        """,
        (release_id,),
    )
    total = sum(item["count"] for item in tests)
    passed = sum(item["count"] for item in tests if item["status"] == "PASSED")
    failed_critical = sum(
        item["count"]
        for item in tests
        if item["status"] != "PASSED" and item["criticality"] == "CRITICAL"
    )
    failed_high = sum(
        item["count"]
        for item in tests
        if item["status"] != "PASSED" and item["criticality"] == "HIGH"
    )
    open_by_severity = {item["severity"]: item["count"] for item in defects}

    risk_score = min(
        100,
        failed_critical * 25
        + failed_high * 12
        + sum(WEIGHTS[severity] * count for severity, count in open_by_severity.items()),
    )
    blockers = []
    if open_by_severity.get("SEV1", 0):
        blockers.append("Open SEV1 defect")
    if failed_critical:
        blockers.append("Failed or blocked critical test")
    if failed_high:
        blockers.append("Failed or blocked high-criticality test")

    if blockers or risk_score >= 50:
        recommendation = "NO_GO"
    elif risk_score >= 20:
        recommendation = "CONDITIONAL_GO"
    else:
        recommendation = "GO"

    return {
        "release": release,
        "recommendation": recommendation,
        "risk_score": risk_score,
        "calculation": {
            "failed_critical_tests_x25": failed_critical,
            "failed_high_tests_x12": failed_high,
            "open_defects_by_severity": open_by_severity,
            "defect_weights": WEIGHTS,
        },
        "test_pass_rate_percent": round((passed / total * 100) if total else 0, 1),
        "blockers": blockers,
        "next_actions": [
            "Resolve and retest release blockers",
            "Run targeted regression for affected components",
            "Capture approval and residual risk in the release record",
        ]
        if recommendation != "GO"
        else ["Record release approval and monitor production signals"],
    }


def regression_plan(release_id: str, max_tests: int = 5) -> dict[str, Any]:
    hotspots = defect_hotspots(release_id)
    failures = failed_tests(release_id)
    tests = rows(
        """
        SELECT test_name, suite, criticality
        FROM test_results
        WHERE release_id = ?
        ORDER BY CASE status WHEN 'FAILED' THEN 1 WHEN 'BLOCKED' THEN 2 ELSE 3 END,
                 CASE criticality WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 ELSE 3 END
        LIMIT ?
        """,
        (release_id, max(1, min(max_tests, 20))),
    )
    return {
        "release_id": release_id,
        "priority_tests": tests,
        "failure_count": len(failures),
        "risk_hotspots": hotspots,
        "rationale": "Prioritizes current failures/blockers, then customer-critical flows.",
    }
