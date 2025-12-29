# USB Forensics Tool - Professional Edition

## 🚀 Quick Start Guide

### What's New in Professional Edition?

**Before**: Only analyzed storage devices from registry
**Now**: Analyzes ALL USB devices in real-time like Wireshark!

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# If pywin32 installation fails, download from:
# https://github.com/mhammond/pywin32/releases
```

### Running the Professional GUI

```bash
python run_enhanced.py
```

Or:

```bash
python gui_enhanced.py
```

## 📊 Main Features

### 1. All USB Devices Tab

**What it shows:**
- **Storage**: USB drives, external HDDs, SD cards
- **Input**: Keyboards, mice, touchpads, game controllers
- **Network**: WiFi adapters, Ethernet adapters, Bluetooth
- **Hubs**: USB hubs and root hubs
- **Audio/Video**: Webcams, microphones, speakers
- **Printers**: USB printers
- **Serial**: COM port devices, Arduino, etc.
- **Unknown**: Any unclassified USB device

**How to use:**
1. Click "🔍 Scan All USB Devices"
2. Wait for scan to complete (2-5 seconds)
3. Browse devices in the tree (grouped by type)
4. Click any device to see full details

### 2. Device Information Panel

When you select a device, you see:

**Device Image:**
- Real photos when available
- Fallback icons for each device type
- USB, HDD, keyboard, mouse icons included

**Comprehensive Details:**
- Device name and description
- Manufacturer name and country
- VID (Vendor ID) and PID (Product ID)
- Serial number
- USB speed (2.0, 3.0, 3.1, 3.2)
- Connection status
- Hardware IDs
- Compatible IDs

**Web Information:**
- Manufacturer website
- Product specifications
- User reviews links
- Manuals and documentation
- Similar products

**Security Information:**
- Security rating (Good/Medium/Poor)
- Known vulnerabilities
- Recalls and warnings
- Safety recommendations
- BadUSB risk assessment

### 3. Storage Forensics Tab

**Original forensics features:**
- Registry artifact analysis
- Event log correlation
- Connection history
- First/last seen dates
- Drive letter assignments
- Volume serial numbers

**How to use:**
1. Switch to "Storage Forensics" tab
2. Click "Analyze Storage Devices"
3. View detailed forensics report
4. Export results

### 4. Timeline Analysis Tab

**Connection timeline:**
- When each device was first connected
- Last connection time
- Total number of connections
- Connection patterns
- Suspicious activity detection

## 🎯 Common Use Cases

### Security Audit

**"I want to check if unauthorized USB devices were used"**

1. Click "Scan All USB Devices"
2. Look for unfamiliar devices
3. Check security information
4. Review connection timeline
5. Export report for documentation

### Forensic Investigation

**"I need to investigate USB storage device usage"**

1. Go to "Storage Forensics" tab
2. Click "Analyze Storage Devices"
3. Review all devices that were EVER connected
4. Check first/last seen dates
5. Look for suspicious devices
6. Export detailed report

### Device Inventory

**"I want to document all USB devices"**

1. Click "Scan All USB Devices"
2. Review all current devices
3. Click "📊 Export CSV" for inventory
4. Or click "📄 Generate Report" for PDF

### Troubleshooting

**"My USB device isn't working"**

1. Scan all devices
2. Find your device in the list
3. Check "Status" column
4. If status is not "OK", device has issues
5. Check manufacturer website for drivers

## 🔍 Understanding the Information

### VID and PID

- **VID (Vendor ID)**: 4-digit code identifying manufacturer
  - Example: `0781` = SanDisk
  - Example: `046D` = Logitech
  
- **PID (Product ID)**: 4-digit code identifying specific product
  - Example: `5567` = SanDisk Cruzer Blade
  - Example: `C52B` = Logitech Unifying Receiver

### USB Speed

- **USB 1.0**: 1.5 Mbps (Low Speed)
- **USB 1.1**: 12 Mbps (Full Speed)
- **USB 2.0**: 480 Mbps (High Speed) - Most common
- **USB 3.0**: 5 Gbps (SuperSpeed) - Blue connectors
- **USB 3.1**: 10 Gbps (SuperSpeed+)
- **USB 3.2**: 20 Gbps
- **USB 4.0**: 40 Gbps

### Device Classes

- **Mass Storage**: USB drives, external disks
- **HID (Human Interface Device)**: Keyboards, mice
- **Wireless**: Bluetooth, WiFi
- **Video**: Webcams
- **Audio**: Speakers, microphones
- **Printer**: USB printers
- **Hub**: USB hubs

### Security Ratings

- **Good**: No known issues, reputable manufacturer
- **Medium**: Some concerns, older firmware
- **Poor**: Known vulnerabilities, recalls

## 📤 Exporting Data

### CSV Export

**Best for:** Excel analysis, data processing

Click "📊 Export CSV" and choose location.

**Contains:**
- Device type
- Name and description
- Manufacturer
- VID and PID
- Serial number
- Status and speed
- Device class

### PDF Report

**Best for:** Professional documentation, sharing

Click "📄 Generate Report"

**Contains:**
- Executive summary
- Device inventory
- Security assessment
- Timeline analysis
- Recommendations

### JSON Export

**Best for:** Integration with other tools

Available in Storage Forensics tab

**Contains:**
- Full device records
- Registry data
- Event log entries
- Metadata

## ⚙️ Advanced Features

### Filtering

Use the **Filter** dropdown to show only:
- Storage devices
- Input devices
- Network devices
- Or all devices

### Searching

Use the **Search** box to find:
- Device names
- Manufacturers
- VID/PID codes
- Serial numbers

### Auto-Refresh

Click "🔄 Refresh" to rescan devices (useful when plugging/unplugging)

## 🔧 Troubleshooting

### "WMI not available" Error

**Problem**: pywin32 not installed properly

**Solution**:
```bash
pip uninstall pywin32
pip install pywin32
python -c "import win32com.client; print('OK')"
```

### No Devices Found

**Problem**: Insufficient permissions

**Solution**: Run as Administrator
1. Right-click Command Prompt
2. Select "Run as administrator"
3. Navigate to tool directory
4. Run: `python run_enhanced.py`

### Images Not Displaying

**Problem**: Pillow not installed

**Solution**:
```bash
pip install Pillow
```

### Devices Show as "Unknown"

**Reason**: Device doesn't have standard USB IDs

**Normal for**: Custom hardware, Arduino, dev boards

## 📚 Comparison with Original Tool

| Feature | Original | Professional |
|---------|----------|--------------|
| Device Types | Storage only | ALL USB devices |
| Detection Method | Registry + logs | Real-time WMI |
| Device Images | Online only | Built-in icons |
| Information Depth | Basic | Comprehensive |
| Security Checks | None | Vulnerability DB |
| Interface | Single view | Multi-tab |
| Real-time | No | Yes |
| Web Lookup | Limited | Enhanced |

## 💡 Tips and Tricks

1. **Run as Administrator** for full device access
2. **Scan regularly** to catch new devices
3. **Export before/after** comparisons for audits
4. **Check timeline** for suspicious after-hours activity
5. **Review security info** for all new devices
6. **Use filters** when you have many devices
7. **Document VID/PID** for your organization's approved devices

## 🆘 Getting Help

1. Check this guide first
2. Review error messages
3. Check Windows Event Viewer
4. Verify pywin32 installation
5. Test with Administrator rights

## 🎓 Learning Resources

**USB Basics:**
- USB.org - Official USB specifications
- Linux USB database - Device ID lookup
- USB-IDs.org - Comprehensive ID database

**Windows Forensics:**
- Registry forensics guides
- Event log analysis tutorials
- WMI query documentation

**Security:**
- BadUSB research papers
- USB security best practices
- NIST USB security guidelines

## 🔐 Privacy & Security

This tool:
- ✅ Runs completely offline (except web lookups)
- ✅ No data sent to external servers
- ✅ All analysis is local
- ✅ No tracking or telemetry
- ✅ Open source and auditable

Web lookups only occur when you select a device and are optional.

## 📝 Changelog

**Professional Edition v2.0** (December 2025)
- ✨ All USB device detection (not just storage)
- ✨ Real-time WMI integration
- ✨ Built-in device icons
- ✨ Enhanced web lookup
- ✨ Security vulnerability checking
- ✨ Multi-tab professional interface
- ✨ Comprehensive device information
- ✨ Timeline analysis
- ✨ Export enhancements

**Original v1.0**
- ✓ Storage device forensics
- ✓ Registry parsing
- ✓ Event log analysis
- ✓ Basic GUI

---

**Ready to start?**

```bash
python run_enhanced.py
```

**Happy forensics! 🔍**
