# AI Agent Release Assurance MCP

> **Version 0.1:** Release-intelligence foundation using synthetic QA data.  
> AI-agent evaluation capabilities are planned for Version 0.2.

An explainable Model Context Protocol (MCP) server that helps AI clients analyze software test results and defects and produce evidence-based release-readiness recommendations.

All releases, tests, defects, and customer-impact scenarios in this repository are fictional. No employer, customer, production, personal, or regulated data is used.

## Why this project exists

Release decisions often require evidence distributed across test results, defect records, and team documentation.

This server gives an AI client a small, read-only interface for answering questions such as:

- Should a particular release ship?
- Which failed tests are potential release blockers?
- Where is unresolved defect risk concentrated?
- Which tests should be prioritized during targeted regression testing?

The AI does not invent the risk score. The server calculates it deterministically and returns the underlying evidence, weights, blockers, and recommended next actions for human review.

## Current capabilities

| Type | Name | Purpose |
|---|---|---|
| Tool | `assess_release_readiness` | Returns an explainable `GO`, `CONDITIONAL_GO`, or `NO_GO` recommendation |
| Tool | `get_failed_tests` | Retrieves failed and blocked tests with an optional criticality filter |
| Tool | `find_defect_hotspots` | Ranks components by severity-weighted unresolved defect risk |
| Tool | `recommend_regression_tests` | Creates a bounded, risk-based regression plan |
| Resource | `qa://releases` | Lists the synthetic releases available for analysis |
| Prompt | `release_go_no_go` | Guides an evidence-based release-readiness review |

## Architecture

```mermaid
flowchart TD
    A[AI host or MCP Inspector] -->|MCP request| B[Python MCP server]
    B --> C[QA service and risk rules]
    C --> D[(Synthetic SQLite data)]
    D --> C
    C -->|Structured evidence| B
    B -->|Tool result| A
    D -. optional migration .-> E[(Snowflake)]
```

SQLite keeps Version 0.1 reproducible and credential-free. The optional `snowflake/setup.sql` file demonstrates a possible Snowflake-native MCP path.

## Quick start

### Requirements

- Python 3.10 or newer
- [`uv`](https://docs.astral.sh/uv/)
- Node.js/npm for the visual MCP Inspector

### Install and run

```bash
git clone https://github.com/Zoya-Ammar/ai-agent-release-assurance-mcp.git
cd ai-agent-release-assurance-mcp
uv sync --extra dev
uv run python -m banking_qa_mcp.seed
uv run mcp dev src/banking_qa_mcp/server.py
```

The final command starts MCP Inspector.

Open **Tools**, select `assess_release_readiness`, and provide:

```json
{
  "release_id": "REL-2026.08.1"
}
```

Expected headline result:

```json
{
  "recommendation": "NO_GO",
  "risk_score": 100,
  "test_pass_rate_percent": 62.5,
  "blockers": [
    "Open SEV1 defect",
    "Failed or blocked critical test",
    "Failed or blocked high-criticality test"
  ]
}
```

For comparison, `REL-2026.08.2` returns `GO` with a risk score of `7`.

## Run the tests

Run the full automated test suite:

```bash
uv run pytest -q
```

Run the dependency-free core verification:

```bash
uv run python scripts/smoke_test.py
```

Version 0.1 includes tests for:

- High-risk and lower-risk release recommendations
- Test-result filtering
- Regression-plan limits and prioritization
- Invalid release identifiers

## Explainable risk scoring

The score is capped at `100`:

```text
25 × failed or blocked critical tests
12 × failed or blocked high-criticality tests
35 × open SEV1 defects
18 × open SEV2 defects
 7 × open SEV3 defects
 2 × open SEV4 defects
```

An open SEV1 defect, a failed or blocked critical test, or a failed or blocked high-criticality test is also reported as an explicit release blocker.

These weights are demonstration policy—not a universal financial-services or software-quality standard. In production, thresholds would require approval, version control, validation, and periodic review by the appropriate risk owners.

## Security considerations

Version 0.1 is deliberately read-only at the application layer. A production implementation should also include:

- Authentication and role-based authorization
- Least-privilege database and service roles
- Input and output validation
- Audit logs for tool calls and recommendations
- Rate limiting and observability
- Secrets management and encrypted transport
- Human approval for release decisions
- Prompt-injection testing for retrieved content

The optional Snowflake example includes a native SQL-execution tool for sandbox demonstration purposes. It should be restricted through a dedicated read-only role and narrowed further before any non-demo use.

## Version 0.2 roadmap

The next version will expand this release-intelligence foundation into an AI-agent assurance system.

Planned capabilities include:

- An original AI-agent evaluation corpus
- Grounding and citation validation
- Prompt-injection resistance testing
- Privacy and data-minimization checks
- Accessibility and negative-path scenarios
- Baseline-versus-candidate comparisons
- Regression detection between agent versions
- Playwright-based UI and accessibility execution
- Snowflake-backed evaluation evidence
- Human-reviewed AI-agent release recommendations

## Project status

This repository is an educational portfolio prototype. It is not a production banking system, compliance tool, or autonomous release authority.

## References

- [Official MCP Python SDK](https://py.sdk.modelcontextprotocol.io/)
- [Snowflake CREATE MCP SERVER documentation](https://docs.snowflake.com/en/sql-reference/sql/create-mcp-server)

## License

This project is available under the [MIT License](LICENSE).
