# 90-second demo script

## 0–15 seconds: the problem

“Release evidence is often split across test results and defects. I built an MCP server
that gives an AI assistant governed tools for analyzing that evidence. All data shown here
is synthetic.”

## 15–35 seconds: show the capabilities

Open the MCP Inspector and briefly show the four tools. Say:

“Rather than giving the model unrestricted database access, I exposed four narrow,
read-only actions: release readiness, failed tests, defect hotspots, and regression
prioritization.”

## 35–60 seconds: analyze the risky release

Call `assess_release_readiness` with `REL-2026.08.1`.

“This release returns NO-GO. The response includes a score of 100, a 62.5% test pass rate,
and explicit blockers: an open SEV1 plus failed critical and high-criticality tests. The
calculation is returned with the result, so it is inspectable rather than a black box.”

## 60–75 seconds: inspect evidence

Call `get_failed_tests` with criticality `CRITICAL`, then show `find_defect_hotspots`.

“The client can drill into the evidence instead of accepting the headline decision.”

## 75–90 seconds: compare and close

Call `assess_release_readiness` with `REL-2026.08.2`.

“A lower-risk release returns GO with a score of 7. My next step is a Snowflake adapter and
an evaluation suite for tool selection and grounding.”

