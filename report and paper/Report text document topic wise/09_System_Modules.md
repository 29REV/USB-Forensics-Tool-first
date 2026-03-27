# System Modules

## 9.1 Registry Parsing Module

This module reads USB-related registry paths and extracts persistent endpoint artifacts such as device identifiers, VID/PID values, serial candidates, and timestamps. It is designed to support graceful fallback when direct registry access is restricted.

## 9.2 Event Log Parsing Module

This module reads USB connection/disconnection style event entries from Windows logs and normalizes them into structured records with event ID, timestamp, and source/device context.

## 9.3 Data Correlation Module

This module merges registry and event records into unified per-device timelines. It uses serial and identifier heuristics, updates connection counters, and preserves unmatched event evidence as event-only records when necessary.

## 9.4 Analysis & Detection Module

This module performs analytical enrichment, including storage/folder/deleted-file summaries (where available), anomaly scoring, and suspicious-condition tagging. It converts raw correlations into investigator-actionable findings.

## 9.5 Report Generation Module

This module converts analyzed device summaries into final exports. It supports multiple output formats to serve different stakeholders: tabular review (CSV/XLSX), machine integration (JSON), and document-oriented sharing (PDF).

Inter-module behavior:
- Parsing modules produce source-specific records.
- Correlation produces unified records.
- Analysis enriches and scores records.
- Report module serializes final evidence outputs.
