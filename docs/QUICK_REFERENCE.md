# 🎯 QUICK REFERENCE CARD

## Launch Commands

```bash
# Easiest (Windows)
launch_professional.bat

# Python
python run_enhanced.py

# Direct
python gui_enhanced.py

# Original (still works)
python gui.py
python main.py
```

## Main Features

### Scan All Devices
```
Click: "🔍 Scan All USB Devices"
Wait: 2-5 seconds
Result: All USB devices listed by type
```

### View Device Details
```
1. Click device in tree
2. See image + full specs
3. Check security rating
4. Review web resources
```

### Storage Forensics
```
Tab: "Storage Forensics"
Click: "Analyze Storage Devices"
Result: Historical device analysis
```

### Export Data
```
CSV:  Click "📊 Export CSV"
PDF:  Click "📄 Generate Report"
JSON: Available in forensics tab
XLSX: Available in forensics tab
```

## Device Types Detected

| Icon | Type | Examples |
|------|------|----------|
| 💾 | Storage | USB drives, HDDs, SD cards |
| ⌨️ | Input | Keyboards, mice, touchpads |
| 🌐 | Network | WiFi, Ethernet, Bluetooth |
| 🔌 | Hub | USB hubs, root hubs |
| 🎥 | Audio/Video | Webcams, mics, speakers |
| 🖨️ | Printer | USB printers |
| 📡 | Serial | COM ports, Arduino |
| ❓ | Unknown | Unclassified devices |

## Information Available

### Basic
- Device name
- Manufacturer
- VID (Vendor ID)
- PID (Product ID)
- Serial number

### Hardware
- USB speed (1.0 - 4.0)
- Device class
- Hardware IDs
- Compatible IDs
- Driver version

### Connection
- Current status
- First seen
- Last seen
- Connection count
- Location

### Security
- Security rating
- Known vulnerabilities
- Recalls
- Recommendations
- Risk assessment

### Web Data
- Product page
- Specifications
- Manuals
- Reviews
- Similar products

## Filtering & Search

### Filter Dropdown
```
All      → All devices
Storage  → USB drives only
Input    → Keyboards/mice only
Network  → Network adapters only
Hub      → USB hubs only
Unknown  → Unidentified devices
```

### Search Box
```
Type: Device name, manufacturer, VID/PID
Updates: Real-time as you type
Clears: Backspace
```

## Keyboard Shortcuts

```
Ctrl+R   Refresh device list
Ctrl+E   Export CSV
Ctrl+F   Focus search box
F5       Refresh
Esc      Clear selection
```

## Status Indicators

```
✅ OK       Device working properly
⚠️ Warning  Device has issues
❌ Error    Device not functioning
🔒 Secure   Good security rating
⚠️ Medium   Some security concerns
🔴 Risk     Known vulnerabilities
```

## Export Formats

### CSV (Excel)
```
Use for: Inventory, analysis in Excel
Contains: Basic device info
Size: Small (KB)
```

### PDF (Report)
```
Use for: Professional documentation
Contains: Full report with images
Size: Medium (MB)
```

### JSON (Data)
```
Use for: Integration, APIs
Contains: Complete data structure
Size: Medium (KB-MB)
```

### XLSX (Spreadsheet)
```
Use for: Formatted Excel workbooks
Contains: Multiple sheets
Size: Medium (KB)
```

## Troubleshooting Quick Fixes

### No Devices Found
```bash
# Solution 1: Run as Admin
Right-click → Run as Administrator

# Solution 2: Check WMI
python -c "import win32com.client"

# Solution 3: Restart WMI
net stop winmgmt
net start winmgmt
```

### Images Not Showing
```bash
# Install Pillow
pip install Pillow

# Verify
python -c "import PIL; print('OK')"
```

### Slow Performance
```bash
# Close other apps
# Disable web lookups
# Use filter to reduce device count
# Run in non-admin mode
```

### Import Errors
```bash
# Reinstall dependencies
pip uninstall -y pywin32 Pillow
pip install -r requirements.txt

# Verify
python -c "import win32com.client; import PIL; print('All OK')"
```

## Security Ratings Explained

### ✅ Good
```
- No known vulnerabilities
- Reputable manufacturer
- Regular firmware updates
- No recalls or warnings
```

### ⚠️ Medium
```
- Some older vulnerabilities (patched)
- Less known manufacturer
- Infrequent updates
- Minor concerns
```

### 🔴 Poor
```
- Known active vulnerabilities
- Security recalls issued
- No firmware updates
- High risk assessment
```

## USB Speed Reference

```
USB 1.0   →  1.5 Mbps  (Low Speed)
USB 1.1   →  12 Mbps   (Full Speed)
USB 2.0   →  480 Mbps  (High Speed) ← Most common
USB 3.0   →  5 Gbps    (SuperSpeed)  ← Blue port
USB 3.1   →  10 Gbps   (SuperSpeed+)
USB 3.2   →  20 Gbps
USB 4.0   →  40 Gbps
```

## VID/PID Quick Reference

### Common Vendors
```
0781 → SanDisk
0951 → Kingston
046D → Logitech
045E → Microsoft
8087 → Intel
04E8 → Samsung
05AC → Apple
413C → Dell
```

### Device Classes
```
Mass Storage  → USB drives, HDDs
HID          → Keyboards, mice
Wireless     → Bluetooth, WiFi
Video        → Webcams
Audio        → Mics, speakers
Printer      → USB printers
Hub          → USB hubs
```

## CLI Mode (Original)

```bash
# Basic analysis
python main.py

# Detailed output
python main.py --detailed

# Specific format
python main.py --format json
python main.py --format csv
python main.py --format pdf

# Help
python main.py --help
```

## File Locations

```
Logs:           app.log
Reports:        reports/
Settings:       settings.json
Icons:          device_icons.py (embedded)
Documentation:  *.md files
```

## Key Files

```
gui_enhanced.py           → Professional GUI
usb_device_manager.py     → Device detection
device_icons.py           → Built-in icons
enhanced_online_lookup.py → Web lookup
launch_professional.bat   → Easy launcher
```

## Getting Help

```
1. Check PROFESSIONAL_EDITION_GUIDE.md
2. Check README_PROFESSIONAL.md
3. Check ENHANCEMENT_SUMMARY.md
4. Check error in app.log
5. Verify dependencies
6. Test with admin rights
```

## Quick Tips

### Tip 1: Regular Scans
```
Scan daily to catch new devices
```

### Tip 2: Export Before/After
```
Export before making changes
Compare after changes
Track differences
```

### Tip 3: Admin Mode
```
Run as Administrator for full access
User mode for quick checks
```

### Tip 4: Filter First
```
Use filters to narrow results
Faster for specific device types
```

### Tip 5: Check Timeline
```
Review connection patterns
Spot suspicious after-hours activity
```

### Tip 6: Security Ratings
```
Always check security info
Update firmware regularly
Remove high-risk devices
```

## Advanced Features

### Timeline Analysis
```
Tab: "Timeline Analysis"
Shows: Connection history
Useful for: Forensics, audits
```

### Device Tree
```
Hierarchical view
Group by type
Expandable categories
```

### Real-time Detection
```
Scan on demand
No periodic scanning
Low resource usage
```

### Multi-format Export
```
Single click exports
Multiple formats available
Choose based on use case
```

## System Requirements

```
OS:      Windows 7/8/10/11
Python:  3.7 or higher
RAM:     2 GB minimum
Disk:    100 MB for tool
Admin:   Recommended (not required)
```

## Performance Tips

```
✓ Close unused applications
✓ Use filters for large device counts
✓ Disable web lookups if slow
✓ Export during off-peak hours
✓ Clear old reports periodically
```

## Best Practices

```
1. Run as Administrator
2. Scan regularly
3. Check security ratings
4. Export for documentation
5. Review timeline periodically
6. Update tool dependencies
7. Keep device database current
```

---

## 🎯 Most Common Workflows

### Security Audit
```
1. Scan All Devices
2. Check for unknown devices
3. Review security ratings
4. Export CSV
5. Document findings
```

### Forensic Investigation
```
1. Go to Storage Forensics tab
2. Click Analyze
3. Review timeline
4. Check suspicious devices
5. Export full report
```

### Device Troubleshooting
```
1. Scan All Devices
2. Find problematic device
3. Check status
4. View manufacturer info
5. Download drivers
```

### IT Inventory
```
1. Scan All Devices
2. Export CSV
3. Import to Excel
4. Track over time
5. Compare changes
```

---

**Keep this card handy for quick reference! 📋**

*USB Forensics Tool - Professional Edition*
