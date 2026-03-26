# Limitations

## 16.1 Current Constraints

- Full capabilities are Windows-centric.
- Some deep features depend on optional packages and admin rights.
- Trace-based analysis depends on capture availability.

Additional current constraints:
- Artifact richness varies by endpoint configuration and policy.
- Some fields depend on device driver metadata quality.
- Deep ETW/URB workflows may require specialized setup and privileges.

## 16.2 System Limitations

- Heuristic scoring is not a legal conclusion by itself.
- Online/enrichment data can be incomplete depending on runtime context.
- Endpoint-only perspective may miss network-side corroboration.

System-level limitations to consider in report interpretation:
- Correlation logic is heuristic and may produce conservative or ambiguous mappings in edge cases.
- Event logs can be truncated or unavailable, limiting timeline completeness.
- Export reports summarize evidence and should be accompanied by raw artifacts for high-stakes legal use.
- The tool currently prioritizes breadth of practical workflow over deep filesystem carving.

Operational impact of these limitations:
- Investigators may need secondary tools for deep validation in complex cases.
- Report conclusions should include confidence qualifiers when source coverage is partial.
- Absence of strong identifiers can increase analyst interpretation effort.

Mitigation strategies currently possible:
- Use multi-source corroboration instead of single artifact dependency.
- Preserve raw exports alongside interpreted summaries.
- Document assumptions explicitly in final case reports.
- Trigger deeper trace analysis when heuristic output suggests elevated risk.

Recommended caution statement for formal reports:
The tool provides structured investigative intelligence and timeline support; however, findings should be validated with complementary forensic methods before legal or disciplinary decisions are finalized.
