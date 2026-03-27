# Module Description

## 10.1 Registry Parsing Module

### 10.1.1 Functionality
Collects USB-related registry entries and transforms them into structured objects for correlation. It extracts critical identity fields (device_id, vid, pid, serial candidate) and preserves timestamp context.

### 10.1.2 Workflow
Open registry root -> enumerate USB subkeys -> parse VID/PID patterns -> extract instance-level values -> generate standardized registry entry list -> return data or fallback set.

### 10.1.3 Output
List of normalized registry entry objects with device identifiers, parsed vendor/product IDs, serial-related values, and time context for downstream timeline use.

## 10.2 Event Log Parsing Module

### 10.2.1 Functionality
Reads USB-related system events and converts them into normalized records suitable for correlation and chronology construction.

### 10.2.2 Event IDs Used
- 2003: USB connect (project logic)
- 2102: USB disconnect (project logic)

These IDs are used in project logic to identify key connection-state transitions.

### 10.2.3 Output
List of event objects containing event_id, ISO-formatted timestamp, and source/device naming context. The output is compact, chronology-ready, and correlation-safe.

## 10.3 Data Correlation Module

### 10.3.1 Correlation Logic
Performs heuristic matching across registry and event streams using serial presence, identifier overlap, and name hints. Updates connection counts and event lists for matched entities while preserving unmatched evidence.

### 10.3.2 Data Mapping
Maps raw source fields into a unified DeviceRecord-like schema:
- identity: device_id, name, vid, pid, serial
- chronology: first_seen, last_seen
- behavior: connection count, event sequence
- enrichment placeholders for later analysis

## 10.4 Analysis & Detection Module

### 10.4.1 Timeline Generation
Constructs per-device chronological summaries from event lists and artifact timestamps, helping analysts interpret activity windows and reuse behavior.

### 10.4.2 Suspicious Activity Detection
Applies explainable heuristic scoring (0-100) and condition checks, including missing serial patterns, unusually frequent interactions, and optional trace-based indicators. Produces machine-readable scores and analyst-readable reasons.

## 10.5 Report Generation Module

### 10.5.1 Report Format
Supports multi-format output:
- CSV for quick tabular forensic review
- JSON for integrations and scripted validation
- XLSX for spreadsheet-oriented analysis
- PDF for narrative and sharing workflows
- detailed JSON for enriched technical evidence

### 10.5.2 Output Files (CSV/PDF)
Produces timestamped output artifacts stored in report directories. CSV/PDF are human-facing investigation deliverables, while JSON/XLSX support cross-team analysis and archiving.
