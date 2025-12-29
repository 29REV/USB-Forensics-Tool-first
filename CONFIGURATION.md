"""Configuration Guide for USB Forensics Tool

This file documents how to configure various aspects of the tool.
"""

# =============================================================================
# 1. SETTINGS.JSON - GUI Configuration
# =============================================================================

"""
The settings.json file stores GUI preferences. Example:

{
  "show_splash": true,
  "reports_dir": "reports"
}

Configuration options:
  - show_splash (bool): Show splash screen on startup. Default: true
  - reports_dir (str): Default directory for saving reports. Default: "reports"

The GUI "Settings" button allows users to change these at runtime.
"""

# =============================================================================
# 2. ENVIRONMENT VARIABLES (Future Enhancement)
# =============================================================================

"""
The tool can be configured via environment variables:

  USB_FORENSICS_REPORTS_DIR    - Output directory for reports
  USB_FORENSICS_LOG_LEVEL      - Logging level (DEBUG, INFO, WARNING, ERROR)
  USB_FORENSICS_MOCK_DATA      - Force mock data instead of real sources
  
Example:
  set USB_FORENSICS_REPORTS_DIR=C:\Forensics\Reports
  python main.py --cli
"""

# =============================================================================
# 3. LOGGING CONFIGURATION
# =============================================================================

"""
Logging is configured in main.py using Python's logging module:

  - Format: %(asctime)s - %(name)s - %(levelname)s - %(message)s
  - File: app.log in the project directory
  - Level: INFO (shows important operations and errors)
  
To increase verbosity, modify main.py:
  logging.basicConfig(..., level=logging.DEBUG, ...)
"""

# =============================================================================
# 4. REGISTRY ANALYSIS CONFIGURATION
# =============================================================================

"""
Registry key analyzed (hardcoded in registry_parser.py):

  HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\USBSTOR

VID/PID Extraction patterns (in registry_parser.py):
  - VID_XXXX or Ven_XXXXX format detection
  - PID_XXXX or Prod_XXXXX format detection
  - Falls back to "UNKNOWN" if pattern not found

To analyze additional registry keys, modify parse_registry():
  1. Open registry_parser.py
  2. Change the 'path' variable to desired key
  3. Adjust the extraction logic as needed
"""

# =============================================================================
# 5. EVENT LOG ANALYSIS CONFIGURATION
# =============================================================================

"""
Event Log analyzed (hardcoded in eventlog_parser.py):

  Logtype: "System"
  Events: 2003 (USB Connect), 2102 (USB Disconnect)
  Max events read: 50 (for performance)
  
To modify:
  1. Open eventlog_parser.py
  2. Change logtype to desired log (e.g., "Application")
  3. Modify event IDs in the (2003, 2102) tuple
  4. Adjust max_events limit
"""

# =============================================================================
# 6. ANOMALY SCORING CONFIGURATION
# =============================================================================

"""
Scoring rules (in analysis.py):

  Missing serial:           +25 points
  Per connection:           +3 points (capped at +40)
  Unusual VID:              +10 points
  Short PID (<3 chars):     +5 points
  
Suspicious device rules (in analysis.py):

  Rule 1: No serial + >3 connections = "No serial number but multiple connections"
  Rule 2: >10 connections = "Unusually frequent connections (>10)"
  
To modify scoring, edit analysis.py:
  1. Change point values in anomaly_score()
  2. Modify rule logic in detect_suspicious()
"""

# =============================================================================
# 7. REPORT FORMAT CONFIGURATION
# =============================================================================

"""
Customize report columns (in report_generator.py):

CSV:
  - Edit fieldnames list in write_csv()
  - Reorder or remove columns as needed
  
JSON:
  - Inherits structure from summarize() in analysis.py
  - Includes full event history
  
XLSX:
  - Edit headers list in write_xlsx()
  - Adjust column widths with ws.column_dimensions
  
PDF:
  - Modify format string in write_pdf()
  - Change fonts with c.setFont()
"""

# =============================================================================
# 8. GUI CUSTOMIZATION
# =============================================================================

"""
Colors and styling (in gui.py, class App.__init__):

  primary = '#2E86AB'       # Blue accent color
  accent = '#F6A623'        # Orange secondary
  bg = '#F4F7FA'            # Light background
  
Font sizes (in gui.py):
  - Header: 14pt bold
  - Content: 11pt regular
  - Labels: 10pt regular
  
To customize:
  1. Open gui.py
  2. Change hex color codes
  3. Modify font size/family
  4. Update style.configure() calls
"""

# =============================================================================
# 9. DEPENDENCY CONFIGURATION
# =============================================================================

"""
Optional packages can be installed selectively:

Essential:
  - tkinter (included with Python)

Report formats:
  - openpyxl   for XLSX support
  - reportlab  for PDF support

Windows integration:
  - pywin32    for Event Log reading

Install all:
  pip install -r requirements.txt

Install specific:
  pip install openpyxl reportlab
"""

# =============================================================================
# 10. PERFORMANCE TUNING
# =============================================================================

"""
For large-scale analysis:

  1. Increase registry parsing timeout:
     - Modify loop limits in parse_registry()
  
  2. Adjust event log reading:
     - Change max_events in parse_event_logs()
     - Limit lookback period
  
  3. Optimize correlation:
     - Use faster string matching in correlate()
     - Implement caching for frequent lookups
  
  4. Reduce anomaly scoring overhead:
     - Skip anomaly_score() if not needed
"""

# =============================================================================
# 11. DEPLOYMENT CONFIGURATION
# =============================================================================

"""
For deployment as executable:

1. Install PyInstaller:
   pip install pyinstaller

2. Create bundle:
   pyinstaller --onefile --windowed main.py

3. Include resources:
   pyinstaller --onefile --windowed --add-data "pics:pics" main.py

4. Result: dist/main.exe (standalone Windows executable)
"""

# =============================================================================
# 12. TROUBLESHOOTING CONFIGURATION
# =============================================================================

"""
Enable debug logging:

1. In main.py, change:
   logging.basicConfig(..., level=logging.DEBUG, ...)

2. Check app.log for detailed diagnostics

3. For GUI debugging:
   python main.py  2>&1 | tee debug.log

4. For CLI debugging:
   python main.py --cli 2>&1 | tee debug.log
"""
