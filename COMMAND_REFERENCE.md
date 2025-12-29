# Quick Command Reference - Phase 5 Features

## New CLI Commands

### Generate Comprehensive Device Analysis
```bash
python main.py --cli --detailed
```
**Output**: `device_details_20250101T000000Z.json`
**Contains**: All device analysis, storage, folders, deleted files, online info

### Generate CSV with Device Details
```bash
python main.py --cli -f csv
```
**Output**: `report_20250101T000000Z.csv`
**Columns**: 23 (includes storage, folder, deleted file, and online info)

### Generate Detailed JSON Report
```bash
python main.py --cli --format detailed
```
**Output**: `device_details_20250101T000000Z.json`
**Same as**: `--cli --detailed`

### Help with New Options
```bash
python main.py --help
```
**Shows**: All available options including `--detailed` and new format choices

---

## Python API Usage

### Import Analysis Functions
```python
from analysis import (
    analyze_storage_patterns,
    analyze_folder_structure,
    analyze_deleted_files,
    analyze_device_reputation,
    compute_anomaly_score,
    enrich_summary
)
```

### Analyze Individual Device
```python
from analysis import enrich_summary

device = {...}  # Device dictionary with data
enriched = enrich_summary(device)

# Access analysis results
storage = enriched['storage_analysis']
folders = enriched['folder_analysis']
deleted = enriched['deleted_files_analysis']
reputation = enriched['reputation_analysis']
score = enriched['anomaly_score']
```

### Custom Analysis
```python
from analysis import (
    analyze_storage_patterns,
    analyze_folder_structure,
    analyze_deleted_files,
    analyze_device_reputation,
    compute_anomaly_score
)

device = {...}

# Analyze specific aspects
storage_data = analyze_storage_patterns(device)
folder_data = analyze_folder_structure(device)
deleted_data = analyze_deleted_files(device)
reputation_data = analyze_device_reputation(device)
score = compute_anomaly_score(device)
```

---

## Report Generation

### Generate Detailed Device Report
```python
from report_generator import write_device_details_report

device_list = [...]
write_device_details_report(device_list, 'reports/detailed.json')
```

### Generate Standard Reports
```python
from report_generator import write_csv, write_json, write_xlsx

device_list = [...]

# CSV with extended columns
write_csv(device_list, 'reports/devices.csv')

# JSON format
write_json(device_list, 'reports/devices.json')

# Excel format
write_xlsx(device_list, 'reports/devices.xlsx')
```

---

## Data Structure Reference

### Storage Analysis Result
```python
{
    'total_capacity_gb': 15.95,
    'used_capacity_gb': 12.34,
    'free_capacity_gb': 3.61,
    'usage_percentage': 77.4,
    'is_full': False,
    'fragmentation_risk': 'Medium'
}
```

### Folder Analysis Result
```python
{
    'total_folders': 128,
    'max_depth': 7,
    'largest_folders': [
        ('Documents', 2456.78),
        ('Pictures', 1834.56)
    ],
    'previous_folder_count': 125,
    'folders_added': 3,
    'folders_deleted': 0
}
```

### Deleted Files Analysis Result
```python
{
    'deleted_count': 23,
    'total_deleted_size_mb': 1245.67,
    'recoverable_count': 18,
    'high_confidence_count': 15,
    'deletion_timeline': '~23 files detected'
}
```

### Device Reputation Result
```python
{
    'manufacturer': 'SanDisk',
    'product_name': 'Cruzer Blade',
    'product_category': 'USB Drive',
    'market_status': 'Active',
    'average_rating': 4.2,
    'known_vulnerabilities': 2,
    'has_alternatives': True
}
```

---

## Common Workflows

### 1. Complete Device Analysis Workflow
```bash
# Generate comprehensive report
python main.py --cli --detailed

# Output: device_details_20250101T000000Z.json
# Contains all analysis data in structured JSON format
```

### 2. Export to CSV for Excel
```bash
# Generate CSV with all device details
python main.py --cli -f csv

# Output: report_20250101T000000Z.csv
# 23 columns with storage, folder, and online info
```

### 3. GUI with Enriched Data
```bash
# Launch GUI with automatic enrichment
python main.py

# GUI displays all device information with analysis
```

### 4. Programmatic Analysis
```python
from correlation import correlate
from analysis import enrich_summary
from registry_parser import parse_registry
from eventlog_parser import parse_event_logs

# Get device records
regs = parse_registry()
evs = parse_event_logs()
devices = correlate(regs, evs)

# Enrich with analysis
enriched_devices = [enrich_summary(d) for d in devices]

# Access analysis
for device in enriched_devices:
    print(f"Device: {device['name']}")
    print(f"  Anomaly Score: {device['anomaly_score']}")
    print(f"  Storage: {device['storage_analysis']['usage_percentage']:.1f}%")
```

---

## Understanding Anomaly Scores

### Score Interpretation
- **0-30**: Normal device, low suspicion
- **30-60**: Moderate activity, monitor
- **60-85**: High anomaly, suspicious behavior
- **85-100**: Critical flags, investigate immediately

### Scoring Factors
- Missing serial number: +25 points
- High registry entries (>100): up to +25 points
- High event log entries (>50): up to +20 points
- Deleted files present: up to +20 points
- Storage >90% full: +15 points
- High connection frequency (>10): up to +15 points

---

## CSV Column Reference (23 columns)

1. Device Name
2. Device ID
3. Vendor ID (VID)
4. Product ID (PID)
5. Serial Number
6. Drive Letter
7. First Seen (UTC)
8. Last Seen (UTC)
9. Total Connections
10. **Storage Capacity (GB)**
11. **Storage Used (GB)**
12. **Storage Free (GB)**
13. **Storage Usage %**
14. **Total Folders**
15. **Max Folder Depth**
16. **Deleted Files Found**
17. **Deleted Files Recoverable**
18. **Manufacturer**
19. **Product (Online)**
20. **Market Status**
21. **Product Rating**
22. **Anomaly Score**
23. Suspicious (flag)

*Items in bold are new in Phase 5*

---

## Troubleshooting

### High Anomaly Score on Normal Device
Check contributing factors:
```bash
# Generate detailed report
python main.py --cli --detailed

# Look for:
# - missing_serial: True?
# - percentage_used > 90?
# - deleted_files count?
```

### Missing Storage Information
Device may not be mounted or permissions insufficient:
```bash
# Check if device is accessible
# Windows: Verify drive letter is visible
# Linux: Check mount points
```

### Unknown Manufacturer
VID/PID not in embedded database:
- Rare or new devices fall back to generic data
- See DEVICE_ANALYSIS.md for handling

---

## File Locations

### Generated Reports
```
reports/
├── report_20250101T000000Z.csv
├── report_20250101T000000Z.json
├── device_details_20250101T000000Z.json
└── report_20250101T000000Z.xlsx
```

### Documentation
```
├── README.md                 (Project overview)
├── DEVICE_ANALYSIS.md        (Feature guide)
├── PHASE_5_SUMMARY.md        (Implementation details)
├── IMPLEMENTATION_COMPLETE.md (Executive summary)
├── DELIVERY_SUMMARY.md       (Delivery details)
├── QUICKSTART.md             (5-minute guide)
└── CONFIGURATION.md          (Advanced setup)
```

---

## Performance Tips

1. **Fastest Analysis**: Use local analysis only
2. **Detailed Analysis**: Use `--detailed` flag
3. **Batch Processing**: Process multiple devices in sequence

---

## For More Information

- **Feature Documentation**: See [DEVICE_ANALYSIS.md](DEVICE_ANALYSIS.md)
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
- **Configuration**: See [CONFIGURATION.md](CONFIGURATION.md)
- **Project Overview**: See [README.md](README.md)

---

**Version**: Phase 5 Complete
**Last Updated**: January 2025
**Status**: Production Ready
