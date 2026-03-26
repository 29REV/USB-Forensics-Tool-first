# Appendix

## 20.1 Code Snippets

Representative pseudocode and module call flow are documented in:
- 11_Implementation_Details.md

Additional representative snippet (analysis pipeline):

```text
registry_entries = parse_registry()
event_entries = parse_event_logs()
device_records = correlate(registry_entries, event_entries)
summaries = summarize(device_records)
enriched = [enrich_summary(item) for item in summaries]
write_csv(enriched, output_csv)
```

Additional representative snippet (suspicious detection logic concept):

```text
if serial is missing and connections > threshold:
	raise_suspicion("No serial with multiple connections")
if anomaly_score > risk_threshold:
	raise_suspicion("High anomaly score")
```

## 20.2 Sample Logs

Sample runtime evidence files are available in:
- report and paper/runtime_evidence/20260326T093628Z/

Key files from this evidence set:
- runtime_summary.json
- forensics_report_20260326T093628Z.csv
- forensics_report_20260326T093628Z.json
- forensics_report_20260326T093628Z.xlsx
- forensics_report_20260326T093628Z.pdf
- forensics_detailed_20260326T093628Z.json

Sample interpreted log points:
- Device count observed: 10
- Suspicious count observed: 0
- Multi-format export set generated successfully

## 20.3 Additional Screenshots

Captured GUI screenshots are available in:
- report and paper/screenshots/01_devices_page.png
- report and paper/screenshots/02_analysis_page.png
- report and paper/screenshots/03_export_page.png

Screenshot notes:
- Devices page screenshot demonstrates enumeration and listing behavior.
- Analysis page screenshot demonstrates device selection for deeper review.
- Export page screenshot demonstrates report output options and execution UI.

## 20.4 Extended Sample Output Records

Sample enriched record fields used in generated outputs:
- name
- device_id
- vid
- pid
- serial
- first_seen
- last_seen
- total_connections
- anomaly_score
- communication_summary
- suspicious reason (if present)

Illustrative CSV row (format example):

```text
USB Input Device,USB\\VID_062A&PID_4101&MI_00\\...,062A,4101,,...,25.0,
```

Illustrative JSON fragment (format example):

```text
{
  "device_id": "USB\\VID_04F2&PID_B7BA\\0001",
  "vid": "04F2",
  "pid": "B7BA",
  "serial": "0001",
  "anomaly_score": 0.0
}
```

## 20.5 Additional Test Notes

Observed during runtime evidence generation:
- Warning messages related to COM object release were present.
- No blocking exceptions occurred in export pipeline.
- All expected output files were written successfully.

Recommended appendix practice for final submission:
- Include selected raw output excerpts with clear labels.
- Include one screenshot per major GUI page used in workflow.
- Include run timestamp and environment details for reproducibility.
- Preserve generated artifacts in a dated folder structure.
