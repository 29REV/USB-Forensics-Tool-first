# Results and Output

## 12.1 Sample Registry Output

Registry extraction provides identifiers such as:
- Device ID
- VID and PID
- Serial candidate
- Last write/observation timestamp

Representative registry-style output fields used in this project include:
- device_id: USB\\VID_xxxx&PID_xxxx\\instance
- vid: parsed vendor ID
- pid: parsed product ID
- serial: serial or instance-derived candidate
- last_write: timestamp used for timeline context

Registry results are particularly useful for identifying persistent historical device traces even when the device is no longer connected.

## 12.2 Sample Event Log Output

Event log output includes USB connect/disconnect records with event IDs and timestamps for timeline alignment.

Typical event record structure:
- event_id: numeric event code
- timestamp: normalized ISO time
- device_name/source: source hint used in mapping

Observed use in pipeline:
- Connect/disconnect-style events increase chronological confidence.
- Event counts support behavior pattern analysis.
- Timestamp ordering supports first_seen/last_seen refinement.

## 12.3 Correlated Data Output

Correlated records combine evidence into per-device structures with event arrays and computed first/last seen values.

Correlation output fields generally include:
- device identity block: device_id, name, vid, pid, serial
- timeline block: first_seen, last_seen
- behavior block: total connections and event list
- analysis block: anomaly score and suspicious rationale

The correlation stage is where independent artifacts become analyst-ready entities.

## 12.4 Timeline Visualization

Timeline data is represented in the GUI timeline/analysis pages and can be exported for report documentation.

Timeline interpretation benefits:
- Establishes event sequence for narrative writing
- Highlights repeated connection cycles
- Supports incident window narrowing
- Improves explainability of suspicious scores

In practice, investigators can cross-reference timeline views with exported CSV/JSON rows for defensible reporting.

## 12.5 Screenshots

Captured runtime screenshots are available at:
- report and paper/screenshots/01_devices_page.png
- report and paper/screenshots/02_analysis_page.png
- report and paper/screenshots/03_export_page.png

Recent runtime evidence snapshot:
- Device count: 10
- Suspicious devices: 0
- Report artifacts: CSV, JSON, XLSX, PDF, detailed JSON

Generated runtime evidence directory:
- report and paper/runtime_evidence/20260326T093628Z/

Artifacts generated in this run:
- forensics_report_20260326T093628Z.csv
- forensics_report_20260326T093628Z.json
- forensics_report_20260326T093628Z.xlsx
- forensics_report_20260326T093628Z.pdf
- forensics_detailed_20260326T093628Z.json

Result interpretation summary:
- The platform executed end-to-end collection, analysis, and export without blocking failures.
- GUI evidence confirms functional page rendering across key workflows.
- Output set demonstrates both human-readable and machine-readable report readiness.

Detailed sample structured output (illustrative format):

```text
{
	"name": "Realtek Bluetooth Adapter",
	"device_id": "USB\\VID_0BDA&PID_4853\\00E04C000001",
	"vid": "0BDA",
	"pid": "4853",
	"serial": "00E04C000001",
	"first_seen": "2026-03-26T09:36:28Z",
	"last_seen": "2026-03-26T09:36:28Z",
	"total_connections": 1,
	"anomaly_score": 0.0,
	"suspicious": ""
}
```

Illustrative event-style output record:

```text
event_id: 2003
timestamp: 2026-03-26T09:30:14Z
device_name: SanDisk Ultra USB Device
message: Device connection event captured
```

Correlation interpretation notes:
- When serial numbers are present, mapping confidence increases.
- When serial values are missing, device_id/name heuristics become primary.
- Event-only records are preserved to avoid losing temporal evidence.

Anomaly score interpretation guidance:
- 0-20: low forensic concern in current context
- 21-50: moderate concern requiring contextual analyst review
- 51-100: higher concern, prioritize manual validation and corroboration

In the current run, several records received moderate baseline score due to missing serial context, while no high-risk suspicious flags were triggered by rule thresholds.

Export usability observations:
- CSV is best for quick analyst filtering and manual review.
- JSON is best for scripted post-processing.
- XLSX is useful for management/operations handoff.
- PDF is useful for static sharing and archival snapshots.

Overall output quality assessment:
The report set is complete, readable, and structurally consistent across formats. This consistency is important when multiple stakeholders (analysts, supervisors, auditors) consume the same findings through different mediums.
