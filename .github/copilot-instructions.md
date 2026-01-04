## Quick orientation for AI code contributors

This file highlights the minimal, high-value knowledge an AI agent needs to be immediately productive in this repository.

### Big picture
- Purpose: a Python tool to analyze USB device activity (Registry + Event Logs), correlate events, run storage/folder/deleted-file analysis, score anomalies and export reports (CSV/JSON/XLSX/PDF).
- Two primary modes: GUI (Tkinter) and CLI. GUI is launched by `python main.py`; CLI via `python main.py --cli`.
- Platform: developed primarily for Windows (Registry + Event Log access). On non-Windows systems the code falls back to mock data in several modules.

### Major components (files to read first)
- `main.py` — application entry (splash → `gui_enhanced.USBForensicsApp`); catch ImportError for missing deps.
- `usb_device_manager.py` — device discovery & `USBDevice` dataclass (WMI on Windows, mock fallback). Good for device shape and classification helpers (`classify_device_type`, `extract_vid_pid`).
- `registry_parser.py` / `eventlog_parser.py` — collectors for Registry and Event Log. Look for `parse_registry()` and `parse_event_logs()` as entry points.
- `correlation.py` — correlates registry + event entries into unified device records (`correlate(...)`).
- `analysis.py` — enrichment and anomaly logic (`summarize`, `enrich_summary`, `compute_anomaly_score`, `detect_suspicious`). Key for business rules and scoring heuristics.
- `report_generator.py` — exporters for CSV/JSON/XLSX/PDF (23-column CSV). Use to see output schema.
- `extensions/` — modular extension system; `extensions/bridge.py` exposes `BaseToolExtensionInterface` used by the app.

### Project-specific conventions and patterns
- Graceful degradation: Windows-only features (pywin32, registry, event log) fall back to mock data — follow this pattern when adding features that may not be available on non-Windows hosts.
- Entry-point functions are stable and named; prefer using them rather than importing internal helpers. Examples: `parse_registry()`, `parse_event_logs()`, `correlate(...)`, `analyze.enrich_summary(...)`, `report_generator.write_csv(...)`.
- Data shapes: `USBDevice` dataclass in `usb_device_manager.py` is the canonical device shape. Many modules accept either dataclass instances or plain dicts — helpers like `analysis.summarize()` convert objects to dicts.
- Settings: `settings.py` reads/writes `settings.json`. Use `load_settings()` / `save_settings()` for configuration values (reports directory, splash screen toggle).

### How to run & developer workflows
- Install deps: `pip install -r requirements.txt` (optional: `openpyxl`, `reportlab`, `pywin32` for full features).
- GUI: `python main.py` (shows splash and launches `USBForensicsApp`).
- CLI: `python main.py --cli -f csv -o /path` (see README for examples including `--detailed`).
- Quick device scan (no GUI): run `python usb_device_manager.py` to see mock or WMI-based device listing.
- Run extension tests: `cd extensions && python test_extensions.py` (test suite exists in `extensions/test_extensions.py`).

### Integration points and external dependencies
- Windows Registry and Event Log: access requires admin privileges and `pywin32` on Windows. The code logs and uses mock data when access fails.
- Online lookups: `online_lookup.py` simulates vendor/product enrichment and is used by `analysis.py` to build reputation data.
- Extensions: drop new modules into `extensions/` and use `extensions.bridge.BaseToolExtensionInterface` to call them. Examples live in `extensions/README.md` and `extensions/test_extensions.py`.

### Examples for an AI agent to use directly
- Create a device summary and compute anomaly score:
```py
from analysis import summarize, compute_anomaly_score
summaries = summarize(devices)
for s in summaries:
    s['anomaly_score'] = compute_anomaly_score(s)
```
- Generate a CSV report from analysis results:
```py
from report_generator import write_csv
write_csv(path='reports/report.csv', devices=analysis_results)
```
- Query extensions bridge (recall / badusb):
```py
from extensions.bridge import BaseToolExtensionInterface
ext = BaseToolExtensionInterface()
recall = ext.query_recall(start_time, end_time, device_serial)
```

### Important gotchas & quick checks
- Admin-only features: tests and CI on non-Windows will see mock data. Don't change that behavior without updating callers.
- Report CSV schema: recently expanded to 23 columns — consult `report_generator.py` before renaming or reordering fields.
- Logging: app logs to `app.log`; debug by increasing logging level in `main.py` configuration.
- Settings persistence is best-effort — `save_settings()` intentionally ignores write errors to avoid crashing the app.

### What to update here
- If you add new long-running components, exporters, or change the CSV/JSON schema, update this file and add short examples showing new entry points and data shapes.

---

If any of these sections are unclear or you want more detail (call graphs, common test failures, or representative sample outputs), tell me which area to expand and I'll iterate. 
