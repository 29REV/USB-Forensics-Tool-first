# USB Forensics Tool

A lightweight Python tool to analyze USB device activity on Windows systems by parsing the Windows Registry and Event Logs, correlating the data, analyzing for suspicious patterns, and generating forensic reports.

## Features

- **Registry Parsing**: Extracts USB device information from Windows Registry (HKLM\SYSTEM\CurrentControlSet\Enum\USBSTOR)
- **Event Log Analysis**: Reads Windows Event Log for USB connect/disconnect events (IDs: 2003, 2102)
- **Data Correlation**: Matches registry entries with event log records to build complete device timelines
- **Detailed Device Analysis** ⭐ NEW:
  - Storage capacity, usage, and fragmentation analysis
  - Folder structure analysis with hierarchical tracking
  - Deleted file detection with recovery probability
  - Online device reputation lookup (manufacturer, product, security, market status)
  - Comprehensive anomaly scoring
- **Anomaly Detection**: Identifies suspicious patterns:
  - Devices with missing serial numbers but multiple connections
  - Devices with unusually frequent connections (>10)
  - Numeric anomaly scoring (0-100 scale) with multi-factor analysis
- **Multiple Export Formats**: CSV (now with 23 columns), JSON, XLSX, PDF, Detailed JSON
- **GUI & CLI Modes**: User-friendly Tkinter GUI or command-line interface with enhanced reporting
- **Cross-Platform Support**: Gracefully falls back to mock data on non-Windows systems

## Requirements

### Minimum
- Python 3.9+
- tkinter (usually included with Python)

### Optional (for full functionality)
- Windows system (for real USB/Registry/Event Log data)
- pywin32 (for Event Log reading on Windows)
- openpyxl (for XLSX export)
- reportlab (for PDF export)

## Installation

1. **Clone or extract the project**
   ```bash
   cd USB-Forensics-Tool
   ```

2. **Install dependencies** (Windows with all features)
   ```bash
   pip install -r requirements.txt
   ```

   Or minimal installation (no PDF/XLSX):
   ```bash
   # No additional packages needed, uses Python stdlib
   ```

3. **Optional: Install specific formats**
   ```bash
   pip install openpyxl     # For XLSX support
   pip install reportlab    # For PDF support
   pip install pywin32      # For Windows Event Log (Windows only)
   ```

## Usage

### GUI Mode (Default)
```bash
python main.py
```

Features:
- Splash screen on startup
- Live device listing with search/filter
- Click device to view full details and event timeline
- Export individual device events as JSON
- Export full analysis in CSV, JSON, XLSX, or PDF format
- Settings dialog to configure display options

### CLI Mode
```bash
# Generate JSON report (default)
python main.py --cli

# Specify output format
python main.py --cli -f csv    # CSV format (23 columns with device details)
python main.py --cli -f json   # JSON format
python main.py --cli -f xlsx   # Excel format
python main.py --cli -f pdf    # PDF format

# Generate comprehensive device analysis report (NEW)
python main.py --cli --detailed                # Detailed analysis in JSON
python main.py --cli --format detailed         # Same as above
python main.py --cli -f csv --detailed         # CSV with enriched data

# Specify output directory
python main.py --cli -f csv -o /path/to/reports
```

### Help
```bash
python main.py --help
```

## What's New - Phase 5

### Comprehensive Device Analysis
The tool now collects extensive details about USB devices:

- **Storage Analysis**: Total capacity, used space, free space, usage percentage, fragmentation risk
- **Folder Structure**: Total folders, nesting depth, largest folders, folder changes
- **Deleted Files**: Detection, recovery probability, size estimation, confidence scores
- **Online Device Info**: Manufacturer lookup, product details, security vulnerabilities, market status, ratings
- **Enhanced Anomaly Scoring**: Multi-factor risk assessment (0-100)

### New Report Features
- **CSV Export**: Expanded from 9 to 23 columns
- **Detailed JSON Report**: Comprehensive analysis data
- **Enhanced Detection**: Includes storage, deleted files, and reputation factors

For detailed documentation, see [DEVICE_ANALYSIS.md](DEVICE_ANALYSIS.md)

## Project Structure

```
USB-Forensics-Tool/
├── main.py                 # Entry point (CLI & GUI launch)
├── gui.py                  # Tkinter GUI implementation
├── registry_parser.py      # Windows Registry parsing
├── eventlog_parser.py      # Windows Event Log parsing
├── correlation.py          # Data correlation logic
├── analysis.py             # Enhanced anomaly detection & analysis
├── report_generator.py     # Enhanced report export (CSV/JSON/XLSX/PDF/Detailed)
├── device_scanner.py       # Detailed device scanning (storage, folders, files)
├── online_lookup.py        # Online device information lookup
├── settings.py             # GUI settings management
├── requirements.txt        # Python dependencies
├── settings.json          # GUI configuration file
├── reports/               # Output directory for generated reports
├── pics/                  # Splash screen images
├── DEVICE_ANALYSIS.md     # Detailed device analysis documentation
├── CONFIGURATION.md       # Advanced configuration guide
├── QUICKSTART.md          # Quick start guide
├── PHASE_5_SUMMARY.md     # Phase 5 enhancement summary
└── README.md              # This file
```

## Module Documentation

### `registry_parser.py`
Reads Windows Registry for USB device information.
- **Entry Point**: `parse_registry() -> list[USBRegistryEntry]`
- Falls back to mock data on non-Windows systems or permission errors
- Extracts: Device ID, VID, PID, Serial Number, Last Write Time

### `eventlog_parser.py`
Reads Windows Event Log for USB events.
- **Entry Point**: `parse_event_logs() -> list[EventEntry]`
- Filters for USB connect (2003) and disconnect (2102) events
- Limited to last 50 events for performance
- Falls back to mock data if pywin32 is unavailable

### `correlation.py`
Correlates registry entries with event log records.
- **Entry Point**: `correlate(registry_entries, event_entries) -> list[DeviceRecord]`
- Matches by serial number, device ID, and name patterns
- Creates unified DeviceRecord with complete timeline

### `analysis.py`
Analyzes devices for suspicious patterns and provides detailed insights.
- `summarize(devices)`: Convert to report-friendly format
- `detect_suspicious(summaries)`: Flag suspicious devices with reasons
- `anomaly_score(summaries)`: Compute 0-100 anomaly scores
- `analyze_storage_patterns()`: Storage capacity and usage analysis
- `analyze_folder_structure()`: Folder hierarchy and size analysis
- `analyze_deleted_files()`: Deleted file detection and recovery
- `analyze_device_reputation()`: Online device information
- `enrich_summary()`: Comprehensive multi-factor analysis

### `report_generator.py`
Exports analysis results in multiple formats.
- `write_csv()`: Human-friendly CSV with 23 columns including device details
- `write_json()`: JSON export for programmatic use
- `write_xlsx()`: Excel spreadsheet with formatting
- `write_pdf()`: PDF document (basic)
- `write_device_details_report()`: Comprehensive JSON with all analysis fields

### `device_scanner.py` ⭐ NEW
Scans USB devices for detailed information.
- `scan_device(device_path)`: Main entry point
- Storage capacity and usage analysis
- Folder hierarchy scanning with depth tracking
- File system information detection
- Deleted file trace detection
- Cross-platform support (Windows/Unix)

### `online_lookup.py` ⭐ NEW
Looks up device information from online sources.
- `lookup_device_online(vid, pid)`: Main entry point
- Embedded USB vendor database (8 vendors)
- Embedded product database (6 products)
- Online query simulation for enrichment
- Security vulnerability checking
- Product alternatives and specifications
- Graceful fallback with mock data

### `gui.py`
Tkinter GUI implementation with device details.
- Multi-column device browser with filtering
- Device details pane with event timeline
- Export buttons for all formats
- Settings dialog for UI preferences
- Ready for tabbed interface enhancement

### `settings.py`
JSON-based configuration storage.
- `load_settings()`: Read app settings
- `save_settings()`: Persist user preferences

## Output Formats

### CSV
- Header metadata
- Friendly column names
- Suspicious flag for flagged devices
- Can be opened in Excel, Google Sheets, etc.

### JSON
- Structured data with full device records
- Event timeline included
- Machine-readable for automation

### XLSX (Excel)
- Formatted spreadsheet
- Multiple columns with proper widths
- Ideal for data analysis and presentations

### PDF
- Simple text-based report
- Suitable for distribution and archiving

## Anomaly Scoring

Devices are scored 0-100 based on:

| Factor | Points |
|--------|--------|
| Missing serial number | +25 |
| Each connection | +3 (max +40) |
| Unusual VID format | +10 |
| Short PID | +5 |

Higher scores indicate more suspicious behavior.

## Logging

- **GUI Mode**: Logs to `app.log` in the project directory
- **CLI Mode**: Logs to stdout and `app.log`
- **Log Level**: INFO by default (configurable)

## Error Handling

- Missing dependencies gracefully degrade (e.g., no PDF if reportlab not installed)
- Windows Registry/Event Log failures fall back to mock data
- All exceptions logged with full tracebacks
- User-friendly error messages in GUI

## Security Notes

- Requires local administrator privileges on Windows for registry/event log access
- Runs locally, no data sent to external services
- Reports are saved locally only
- Mock data used for testing on non-Windows systems

## Troubleshooting

**"Module not found" errors**
```bash
pip install -r requirements.txt
```

**"Permission denied" accessing registry**
- Run as Administrator on Windows
- Tool will use mock data as fallback

**PDF/XLSX export failing**
- Install missing package: `pip install reportlab openpyxl`

**Event Log showing no entries**
- Ensure running as Administrator
- Check Windows Event Viewer for System events

## Future Enhancements

- [ ] USB drive content scanning
- [ ] Timeline visualization
- [ ] Automated suspicious device alerting
- [ ] Machine learning-based anomaly detection
- [ ] Export to forensic report formats
- [ ] Batch processing of multiple devices
- [ ] Custom analysis rules engine

## Contributing

Contributions welcome! Please:
1. Test on both Windows and non-Windows systems
2. Add docstrings and type hints
3. Update logging in new functions
4. Maintain backwards compatibility

## License

Created by: srirevanth A, Deekshitha, Naghul Pranav C B

## Version

1.1.0 - Enhanced with comprehensive error handling, logging, and documentation

