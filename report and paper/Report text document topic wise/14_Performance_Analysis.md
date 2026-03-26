# Performance Analysis

## 14.1 Accuracy

Accuracy is bounded by source artifact quality. Multi-source correlation improves confidence compared to single-source parsing, but final interpretation still requires analyst review.

Accuracy considerations in this project:
- Identity accuracy depends on quality of serial/device-id extraction.
- Timeline accuracy depends on event availability and timestamp normalization.
- Suspicious detection accuracy depends on heuristic threshold quality.

Accuracy strengths:
- Correlating registry and event sources reduces single-source blind spots.
- Preserving unmatched records avoids evidence loss.
- Structured outputs reduce interpretation ambiguity.

Accuracy caveat:
- The tool is an analysis assistant, not a legal proof engine; analyst validation is required.

## 14.2 Efficiency

The pipeline is efficient for endpoint-scale USB datasets. Limiting event-read windows and modular parsing keeps runtime practical for investigation workflows.

Efficiency design decisions:
- Bounded event reads reduce processing time for large logs.
- Modular parsers allow selective execution based on need.
- Lightweight in-memory structures support quick report generation.

Observed practical efficiency:
- Runtime evidence generation completed with multi-format output creation in a single pass.
- GUI route enables quick inspection before full export.

## 14.3 Comparison with Existing Tools

Compared to fragmented manual workflows, this tool improves speed and consistency by integrating collection, correlation, scoring, and reporting in one stack. Compared to large forensic suites, it is narrower in scope but easier to deploy and customize.

Comparative positioning:
- Versus manual scripts: better structure, stronger consistency, and easier reuse.
- Versus heavy enterprise suites: lighter setup and simpler customization, but narrower feature breadth.
- Versus single-purpose USB tools: stronger end-to-end integration with reporting and extension options.

Overall performance conclusion:
The project offers a balanced tradeoff between investigative depth and operational simplicity for focused USB forensic workflows.

Proposed metric framework for continued evaluation:

1. Data Completeness Ratio
	- Definition: mapped records / total collected records
	- Goal: maximize evidence retention while minimizing orphan records

2. Correlation Confidence Indicator
	- Definition: proportion of records matched by strong identifiers (serial/device_id)
	- Goal: reduce ambiguity in identity mapping

3. Export Reliability Rate
	- Definition: successful exports / attempted exports by format
	- Goal: ensure reporting pipeline stability

4. End-to-End Runtime
	- Definition: time from acquisition start to final artifact generation
	- Goal: maintain analyst-usable turnaround for endpoint-scale runs

5. False Escalation Tendency
	- Definition: percentage of flagged records later deemed benign after review
	- Goal: tune heuristic thresholds without suppressing real risk

Comparative dimensions with existing approaches:
- Speed of first actionable output
- Repeatability across different analysts
- Ease of integrating findings into formal reports
- Ability to preserve source context for each indicator
- Flexibility for extension and adaptation

Performance posture in current state:
- Strong in workflow integration and output consistency
- Moderate in advanced statistical detection depth
- Good for targeted endpoint investigations and academic demonstrations

Optimization directions:
- Cache-heavy artifact parsing for repeated runs on same endpoint
- Add confidence metadata per correlated field
- Introduce optional asynchronous export generation for large datasets
- Expand profiling hooks for module-level runtime diagnostics
