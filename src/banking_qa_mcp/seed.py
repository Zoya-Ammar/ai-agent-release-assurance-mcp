from __future__ import annotations

from banking_qa_mcp.database import connect, db_path

SCHEMA = """
DROP TABLE IF EXISTS test_results;
DROP TABLE IF EXISTS defects;
DROP TABLE IF EXISTS releases;

CREATE TABLE releases (
    release_id TEXT PRIMARY KEY,
    release_name TEXT NOT NULL,
    environment TEXT NOT NULL,
    planned_date TEXT NOT NULL,
    critical_flows_total INTEGER NOT NULL
);

CREATE TABLE test_results (
    test_result_id INTEGER PRIMARY KEY,
    release_id TEXT NOT NULL REFERENCES releases(release_id),
    test_name TEXT NOT NULL,
    suite TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PASSED', 'FAILED', 'BLOCKED')),
    criticality TEXT NOT NULL CHECK(criticality IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    duration_seconds INTEGER NOT NULL,
    failure_message TEXT
);

CREATE TABLE defects (
    defect_id TEXT PRIMARY KEY,
    release_id TEXT NOT NULL REFERENCES releases(release_id),
    title TEXT NOT NULL,
    component TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('SEV1', 'SEV2', 'SEV3', 'SEV4')),
    status TEXT NOT NULL CHECK(status IN ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'DEFERRED')),
    customer_impact TEXT NOT NULL
);
"""

RELEASES = [
    ("REL-2026.08.1", "Digital Account Opening 2026.08.1", "UAT", "2026-08-29", 6),
    ("REL-2026.08.2", "Mobile Banking 2026.08.2", "SIT", "2026-09-05", 5),
]

TEST_RESULTS = [
    (1, "REL-2026.08.1", "Open checking account", "E2E", "PASSED", "CRITICAL", 94, None),
    (
        2,
        "REL-2026.08.1",
        "Identity verification retry",
        "API",
        "FAILED",
        "CRITICAL",
        8,
        "Third retry returns HTTP 500",
    ),
    (3, "REL-2026.08.1", "Fund account with debit card", "E2E", "PASSED", "CRITICAL", 81, None),
    (
        4,
        "REL-2026.08.1",
        "Duplicate application idempotency",
        "API",
        "FAILED",
        "HIGH",
        4,
        "Duplicate application created",
    ),
    (
        5,
        "REL-2026.08.1",
        "Keyboard-only disclosure acceptance",
        "ACCESSIBILITY",
        "BLOCKED",
        "HIGH",
        20,
        "Focus trap in modal",
    ),
    (
        6,
        "REL-2026.08.1",
        "OFAC screening happy path",
        "INTEGRATION",
        "PASSED",
        "CRITICAL",
        31,
        None,
    ),
    (7, "REL-2026.08.1", "Application audit event", "DATABASE", "PASSED", "MEDIUM", 3, None),
    (8, "REL-2026.08.1", "Session timeout", "SECURITY", "PASSED", "HIGH", 65, None),
    (9, "REL-2026.08.2", "Biometric sign-in", "E2E", "PASSED", "CRITICAL", 48, None),
    (10, "REL-2026.08.2", "Remote deposit capture", "E2E", "PASSED", "CRITICAL", 73, None),
    (11, "REL-2026.08.2", "Transfer daily limit", "API", "PASSED", "HIGH", 5, None),
    (
        12,
        "REL-2026.08.2",
        "Push notification opt-out",
        "API",
        "FAILED",
        "MEDIUM",
        6,
        "Preference remains enabled",
    ),
    (
        13,
        "REL-2026.08.2",
        "Screen reader account balance",
        "ACCESSIBILITY",
        "PASSED",
        "HIGH",
        34,
        None,
    ),
]

DEFECTS = [
    (
        "BUG-1042",
        "REL-2026.08.1",
        "Identity retry causes server error",
        "Identity",
        "SEV1",
        "OPEN",
        "Applicants cannot complete verification after a recoverable mismatch.",
    ),
    (
        "BUG-1047",
        "REL-2026.08.1",
        "Duplicate application accepted",
        "Applications API",
        "SEV2",
        "IN_PROGRESS",
        "May create duplicate customer applications and manual review work.",
    ),
    (
        "BUG-1051",
        "REL-2026.08.1",
        "Disclosure modal traps keyboard focus",
        "Web Accessibility",
        "SEV2",
        "OPEN",
        "Keyboard-only customers cannot proceed.",
    ),
    (
        "BUG-1030",
        "REL-2026.08.1",
        "Audit timestamp timezone label",
        "Audit",
        "SEV4",
        "RESOLVED",
        "Internal audit display only; stored timestamp is correct.",
    ),
    (
        "BUG-1103",
        "REL-2026.08.2",
        "Opt-out preference not persisted",
        "Notifications",
        "SEV3",
        "OPEN",
        "Customers may continue receiving optional notifications.",
    ),
]


def seed() -> None:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect() as connection:
        connection.executescript(SCHEMA)
        connection.executemany("INSERT INTO releases VALUES (?, ?, ?, ?, ?)", RELEASES)
        connection.executemany(
            "INSERT INTO test_results VALUES (?, ?, ?, ?, ?, ?, ?, ?)", TEST_RESULTS
        )
        connection.executemany("INSERT INTO defects VALUES (?, ?, ?, ?, ?, ?, ?)", DEFECTS)
    print(f"Seeded synthetic QA data at {path}")


if __name__ == "__main__":
    seed()
