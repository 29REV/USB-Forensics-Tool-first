# Literature Survey

## 4.1 Existing Research Overview

Research in USB and endpoint forensics commonly focuses on host artifact extraction, timeline reconstruction, and cross-source validation. Established practices use registry artifacts, event records, and hardware identifiers to infer USB connection history and user/device interaction patterns. These approaches are valuable for incident response, policy auditing, and insider-threat investigation.

Academic and practical studies emphasize several principles:
- Evidence should be collected from more than one source to reduce false interpretation.
- Timestamp interpretation should preserve source context and confidence level.
- Investigator outputs should be structured and reproducible, not ad hoc.

Existing tooling ecosystems typically divide work across independent components: one utility for device listing, another for event parsing, and separate scripts for reporting. Advanced lines of work include communication-level indicators, such as repeated re-enumeration patterns, suspicious HID behavior, and vendor-specific transfer anomalies.

## 4.2 Comparative Analysis of Existing Works

Typical approaches in existing works include:
- Single-source analysis: registry-only or event-only approaches
- Command-line-only pipelines with limited analyst usability
- Basic output generation without enriched interpretation

Compared to these, this project contributes:
- Multi-source artifact correlation (registry + event + optional trace)
- GUI workflow for broader usability
- Built-in anomaly scoring and suspicious tagging
- Direct export to common investigation formats

Comparative observations:
- Registry-only tools provide persistence clues but weak temporal narrative.
- Event-only tools provide sequence clues but can miss persistent device identity context.
- Full-feature forensic suites are powerful but often heavyweight and less flexible for targeted USB workflows.
- Lightweight custom scripts are flexible but usually lack standard report structure and consistent scoring.

The current project positions itself between heavy suites and minimal scripts by combining modular depth with operational simplicity.

## 4.3 Research Gaps Identified

- Lack of integrated tooling that is both analyst-friendly and technically deep
- Limited adoption of fallback-safe behavior for constrained environments
- Insufficient coupling between artifact extraction and structured reporting
- Underuse of optional packet-level USB behavior analysis in desktop workflows

Additional practical gaps identified:
- Many implementations do not expose clear reasoning for risk scoring.
- Few tools provide both GUI and automation paths in the same codebase.
- Output schemas are often inconsistent across export formats.
- Extension-ready architecture is uncommon in small/medium USB forensic tools.

### Expanded Comparative Discussion

A review of commonly used USB analysis approaches shows recurring tradeoffs between depth and usability. Tools with deep parsing capabilities can be difficult for non-specialist analysts, while user-friendly tools often simplify outputs too aggressively. The literature and practical tool landscape suggest that balanced systems are still limited, especially in open, modifiable implementations.

Another recurring issue is reproducibility. In many workflows, analysts rely on manual extraction commands and ad hoc spreadsheets. Even when technically correct, this process creates documentation variance across investigators. This variance weakens comparability and makes long-term trend analysis difficult.

### Methodological Implications for This Project

The survey findings influenced this implementation in three direct ways:
- Multi-source evidence handling was prioritized over single-source depth.
- Export consistency was treated as a core requirement, not an afterthought.
- Explainable heuristic scoring was preferred over opaque classification.

These decisions align with forensic reporting needs where traceability and clarity are critical.

### Research Opportunity Areas

Future research opportunities derived from this survey include:
- Quantitative validation of heuristic thresholds across large endpoint corpora.
- Confidence-weighted correlation models for ambiguous identifiers.
- Hybrid symbolic + statistical scoring for suspicious behavior detection.
- Standardized interchange schema for USB forensic evidence across tools.

By identifying these gaps, the project positions itself both as a practical implementation and as a foundation for continued methodological research.
