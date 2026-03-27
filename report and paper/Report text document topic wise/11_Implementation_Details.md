# Implementation Details

## 11.1 System Design

The implementation follows a modular, layered architecture to improve maintainability and forensic reliability. Instead of building one monolithic script, each major responsibility is implemented as an independent module with explicit inputs and outputs.

Design principles applied:
- Separation of concerns: acquisition, correlation, analysis, and reporting are isolated.
- Graceful degradation: missing dependencies should reduce capability, not crash the system.
- Transparent scoring: suspicious detection logic remains explainable and auditable.
- Output consistency: exported schemas remain predictable across formats.

Internal design layers:
- Entry and orchestration layer: launches GUI, initializes settings, and controls execution paths.
- Source acquisition layer: reads USB devices, registry data, and event logs.
- Correlation layer: fuses heterogeneous records into device-level timelines.
- Analysis layer: computes anomaly score and suspicious indicators.
- Presentation/export layer: displays data in GUI and writes report artifacts.

This structure supports incremental updates. For example, improving event parsing logic does not require redesigning correlation or report generation.

## 11.2 Algorithm / Workflow

The end-to-end workflow is designed for evidence retention and analyst readability.

1. Enumerate USB devices.
   - Collect current endpoint USB/PnP inventory.
   - Parse identifiers such as VID, PID, and serial candidates.

2. Parse registry artifacts.
   - Access USB-relevant registry paths.
   - Build normalized registry-entry structures.

3. Parse USB-related event logs.
   - Read event channels and apply USB event filters.
   - Convert events to timestamped normalized objects.

4. Correlate all evidence into device records.
   - Match by serial, IDs, and name heuristics.
   - Preserve unmatched events as independent records.

5. Enrich records and compute anomaly scores.
   - Calculate timeline windows, counts, and risk indicators.
   - Apply suspicious-detection heuristics.

6. Export in selected formats.
   - Produce CSV/JSON/XLSX/PDF outputs.
   - Optionally generate detailed JSON for deeper audit trails.

## 11.3 Pseudocode

```text
devices = collect_usb_devices()
registry_entries = parse_registry()
event_entries = parse_event_logs()
records = correlate(registry_entries, event_entries)
summaries = summarize(records or devices)
enriched = [enrich_summary(s) for s in summaries]
findings = detect_suspicious(enriched)
export_reports(enriched, findings)
```

Extended pseudocode with fallback behavior:

```text
try:
	devices = collect_usb_devices_windows()
except:
	devices = collect_usb_devices_fallback()

try:
	registry_entries = parse_registry_windows()
except:
	registry_entries = parse_registry_mock()

try:
	event_entries = parse_event_logs_windows()
except:
	event_entries = parse_event_logs_mock()

records = correlate(registry_entries, event_entries)
if records is empty:
	records = build_records_from_devices(devices)

summaries = summarize(records)
enriched = []
for summary in summaries:
	enriched.append(enrich_summary(summary))

findings = detect_suspicious(enriched)
write_csv(enriched)
write_json(enriched)
write_xlsx(enriched)
write_pdf(enriched)
```

## 11.4 Execution Flow

Execution starts from the main entrypoint and follows one of two routes:
- GUI route for interactive analysis
- Scripted route for automated evidence/report generation

Detailed flow:
- Application startup initializes logging and settings.
- GUI initializes page modules and navigation components.
- Data collection actions trigger parsing modules.
- Correlation and analysis are invoked when summaries are requested.
- Export actions call report generation functions with validated data.

Runtime robustness considerations:
- Import errors are surfaced clearly with dependency guidance.
- Non-critical source failures trigger controlled fallback behavior.
- Logs capture errors and warnings for forensic reproducibility.

This execution model enables both demonstration and investigation modes with the same codebase.

## 11.5 Implementation Notes on Key Modules

USB device management implementation emphasizes identity extraction and classification. Device objects are normalized early so downstream modules receive predictable fields. Where serial extraction is ambiguous, the system preserves partial identity rather than forcing unsafe assumptions.

Registry parsing implementation uses key enumeration and pattern extraction to derive VID/PID and instance-level identifiers. Because registry formats vary, extraction helpers support tolerant parsing while keeping unknown values explicit.

Event parsing implementation targets USB-relevant events and converts timestamps into normalized formats. Event ingestion is intentionally bounded to keep performance practical in large logs.

Correlation implementation uses heuristic matching and incremental record updates. It handles matched and unmatched records to maximize evidence retention.

Analysis implementation performs enrichment and scoring using explicit rules. Scores are constrained to bounded ranges and intended as prioritization guidance.

Report generation implementation centralizes export logic to maintain schema consistency across formats.

## 11.6 Workflow Integrity and Traceability

Workflow integrity is supported through:
- Structured intermediate objects
- Repeatable pipeline sequencing
- Deterministic export generation for same input context

Traceability practices include:
- Logging key pipeline events
- Retaining generated artifacts with timestamps
- Preserving both summarized and detailed output formats

## 11.7 Practical Deployment Guidance

For practical use, recommended deployment flow is:
1. Set up Python virtual environment and dependencies.
2. Run initial GUI scan to validate source access.
3. Execute script-based evidence generation for reproducible outputs.
4. Review CSV/JSON outputs and inspect suspicious indicators.
5. Attach runtime screenshots and export artifacts in final report.

This deployment approach supports both demonstration and case documentation requirements.
