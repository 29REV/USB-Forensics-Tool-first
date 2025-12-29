# Windows USB Forensics Tool

## Overview
A lightweight Python tool that analyzes USB activity on Windows systems by reading Registry and Event Logs, then generates human-readable reports.  
It’s designed for forensic investigators and cybersecurity students.

## Objectives
- Detect when and which USB devices were connected/disconnected.
- Extract Vendor ID, Product ID, Serial Number, and timestamps.
- Generate summarized reports (CSV/PDF).
- Provide a simple GUI interface for easy analysis.

## Modules
1. **Registry Parser**
   - Reads Windows Registry keys:
     - `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\USBSTOR`
     - `HKEY_LOCAL_MACHINE\SYSTEM\MountedDevices`
   - Extracts: Vendor ID, Product ID, Serial Number, LastWrite time, drive letter.

2. **Event Log Parser**
   - Analyzes Event Logs for:
     - Event ID 2003 → USB Connected  
     - Event ID 2102 → USB Disconnected  
   - Extracts timestamps and device names.

3. **Data Correlation**
   - Combines Registry + Event Log data to form a timeline.

4. **Analysis & Detection**
   - Lists all unique USB devices and how often they were used.
   - Flags unknown or suspicious patterns.

5. **Report Generator**
   - Creates CSV and PDF reports.
   - Fields: Device Name, VID, PID, Serial, First Seen, Last Seen, Total Connections.

6. **GUI**
   - Built with Tkinter.
   - Two buttons:
     - “Analyze PC” – scans registry & logs.
     - “Analyze USB” – scans specific USB details.
   - Shows table + Export buttons (CSV/PDF).

## Requirements
- Python 3.9+ (no venv)
- Windows 10 or 11
- Libraries:
  - winreg (built-in)
  - pywin32
  - python-evtx
  - csv (built-in)
  - reportlab
  - tkinter (built-in)

## Project Structure
usb_forensics_tool/
├── main.py
├── registry_parser.py
├── eventlog_parser.py
├── correlation.py
├── analysis.py
├── report_generator.py
├── gui.py
└── README.md

## How It Works
1. Registry & Event logs are parsed.
2. Data is combined and analyzed.
3. Report is generated.
4. User can interact through GUI.
