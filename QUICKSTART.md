"""QUICK START GUIDE - USB Forensics Tool

Get up and running in 5 minutes!
"""

# ==============================================================================
# 1. INSTALLATION (2 minutes)
# ==============================================================================

# Step 1: Install Python 3.9+ if not already installed
# Download from: https://www.python.org/downloads/

# Step 2: Navigate to project directory
cd USB-Forensics-Tool

# Step 3: Install dependencies (optional, for full features)
pip install -r requirements.txt

# That's it! Tkinter is included with Python.


# ==============================================================================
# 2. RUN GUI MODE (1 minute)
# ==============================================================================

# Simply run:
python main.py

# You'll see:
# 1. Splash screen (can disable in Settings)
# 2. Main analysis window
# 3. Click "Analyze PC" to scan for USB devices
# 4. Select a device to see details and events
# 5. Export to CSV/JSON/XLSX/PDF using the buttons

# Keyboard shortcuts:
# - Search box: Type to filter devices
# - Double-click device: Show full details
# - Click columns: Can't sort yet (future feature)


# ==============================================================================
# 3. RUN CLI MODE (1 minute)
# ==============================================================================

# Generate JSON report (default):
python main.py --cli

# Output: reports/report_20251229T123456Z.json

# Generate CSV report:
python main.py --cli -f csv

# Output: reports/report_20251229T123456Z.csv

# Generate XLSX (Excel):
python main.py --cli -f xlsx

# Output: reports/report_20251229T123456Z.xlsx

# Generate PDF:
python main.py --cli -f pdf

# Output: reports/report_20251229T123456Z.pdf

# Custom output directory:
python main.py --cli -f csv -o C:\Forensics\Reports


# ==============================================================================
# 4. HELP & OPTIONS
# ==============================================================================

python main.py --help

# Shows all available options:
# --cli              Run in CLI mode (no GUI)
# --format -f        Output format (csv, json, xlsx, pdf)
# --output -o        Output directory for reports


# ==============================================================================
# 5. UNDERSTANDING OUTPUT
# ==============================================================================

# CSV Report:
# - Opens in Excel, Google Sheets, etc.
# - Contains: Device name, ID, VID, PID, Serial, First/Last seen, Connections
# - Suspicious flag marks devices detected as anomalous

# JSON Report:
# - Machine-readable format
# - Full event history included
# - Use for programmatic analysis

# XLSX Report:
# - Excel spreadsheet
# - Formatted columns
# - Easy to analyze and present

# PDF Report:
# - Text-based document
# - Good for printing and archiving
# - Summary format


# ==============================================================================
# 6. INTERPRETING RESULTS
# ==============================================================================

# Device ID: Unique identifier from Windows Registry
# VID: Vendor ID (manufacturer code)
# PID: Product ID (device type code)
# Serial: Device serial number (often missing)
# First Seen: When device first appeared in logs
# Last Seen: Most recent activity
# Connections: How many times connected/disconnected
# Suspicious: Flagged if matching anomaly rules


# ==============================================================================
# 7. WHAT'S SUSPICIOUS?
# ==============================================================================

# Device is marked suspicious if:
# 1. Has no serial number but multiple connections
# 2. Has more than 10 connections (unusually frequent)
# 3. Has unusual VID/PID values

# Higher numbers = more suspicious patterns


# ==============================================================================
# 8. TROUBLESHOOTING
# ==============================================================================

# "Permission denied" error?
# - Run as Administrator (right-click Command Prompt → Run as administrator)
# - Tool will use sample data if permission denied

# Missing XLSX/PDF export buttons?
# - Install: pip install openpyxl reportlab

# No devices found?
# - Tool works best with admin privileges
# - Sample data shown as fallback
# - Normal on non-Windows systems

# GUI not starting?
# - Check tkinter: python -c "import tkinter; print('OK')"
# - Ubuntu/Linux: sudo apt-get install python3-tk


# ==============================================================================
# 9. FILES CREATED
# ==============================================================================

# When you run the tool, it creates:

# app.log              - Application log file
# settings.json        - GUI preferences
# reports/             - Output directory
#   ├── report_*.csv   - CSV reports
#   ├── report_*.json  - JSON reports
#   ├── report_*.xlsx  - Excel reports
#   └── report_*.pdf   - PDF reports


# ==============================================================================
# 10. ADVANCED USAGE
# ==============================================================================

# Run with debug logging:
# python main.py 2>&1 | tee debug.log

# Run tests:
# python test_core.py

# Run with custom log level:
# Open main.py and change: level=logging.DEBUG
# Then: python main.py --cli


# ==============================================================================
# 11. CONFIGURATION
# ==============================================================================

# Edit settings.json:
# {
#   "show_splash": false,      # Disable splash screen
#   "reports_dir": "C:\\Reports"  # Custom report location
# }

# Or let GUI Settings dialog change them


# ==============================================================================
# 12. NEXT STEPS
# ==============================================================================

# Read README.md for comprehensive documentation
# Read CONFIGURATION.md for advanced setup
# Read IMPROVEMENTS.md for technical details
# Run test_core.py to verify installation
# Check app.log if issues occur


# ==============================================================================
# 13. SUPPORT
# ==============================================================================

# Common issues:
# 1. Registry permission denied → Run as Admin
# 2. No Event Log data → Check Windows Event Viewer
# 3. XLSX not exporting → pip install openpyxl
# 4. PDF not exporting → pip install reportlab

# Debug information:
# - app.log contains detailed logs
# - Error messages shown in GUI popups
# - CLI errors printed to console

# Happy forensics analyzing!
"""
