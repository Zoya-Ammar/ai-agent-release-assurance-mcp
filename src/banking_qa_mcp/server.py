from __future__ import annotations

import json

from mcp.server import MCPServer

from banking_qa_mcp.service import (
    defect_hotspots,
    failed_tests,
    list_releases,
    regression_plan,
    release_readiness,
)

mcp = MCPServer("Banking QA Intelligence")


@mcp.tool()
def assess_release_readiness(release_id: str) -> dict:
    """Calculate an explainable GO, CONDITIONAL_GO, or NO_GO recommendation."""
    return release_readiness(release_id)


@mcp.tool()
def get_failed_tests(release_id: str, criticality: str | None = None) -> list[dict]:
    """Return failed and blocked tests, optionally filtered by criticality."""
    return failed_tests(release_id, criticality)


@mcp.tool()
def find_defect_hotspots(release_id: str) -> list[dict]:
    """Rank release components by the weighted risk of unresolved defects."""
    return defect_hotspots(release_id)


@mcp.tool()
def recommend_regression_tests(release_id: str, max_tests: int = 5) -> dict:
    """Build a risk-based regression plan grounded in test and defect evidence."""
    return regression_plan(release_id, max_tests)


@mcp.resource("qa://releases")
def releases_resource() -> str:
    """List the synthetic releases available for analysis."""
    return json.dumps(list_releases(), indent=2)


@mcp.prompt()
def release_go_no_go(release_id: str) -> str:
    """Guide an evidence-based release readiness review."""
    return (
        f"Assess release {release_id}. First call assess_release_readiness, then inspect "
        "failed tests and defect hotspots. State the recommendation, cite the returned "
        "evidence, identify customer impact, and list the three highest-priority actions. "
        "Do not invent facts that the tools did not return."
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
