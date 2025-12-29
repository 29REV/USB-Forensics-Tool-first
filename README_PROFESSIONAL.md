# 🔍 USB Forensics Tool - Professional Edition

## **Wireshark-Level Analysis for USB Devices**

A comprehensive USB device forensics and analysis tool that brings Wireshark's level of detail to USB device inspection. Analyze ALL USB devices (not just storage) with real-time detection, security assessment, and forensic timeline analysis.

---

## 🌟 What Makes This Professional?

### **Before (Basic Version)**
- ❌ Storage devices only
- ❌ Historical data only (registry/logs)
- ❌ Limited information
- ❌ Basic text output

### **Now (Professional Edition)**
- ✅ **ALL USB devices** (keyboard, mouse, network, storage, etc.)
- ✅ **Real-time detection** via WMI
- ✅ **Comprehensive information** (specs, security, history)
- ✅ **Professional GUI** with images and rich details
- ✅ **Security analysis** (vulnerabilities, threats)
- ✅ **Timeline forensics** (connection patterns)
- ✅ **Web-enhanced** (manufacturer data, specs, manuals)

---

## 🚀 Quick Start

### **Easy Launch** (Windows)

```batch
launch_professional.bat
```

This will:
1. Check Python installation
2. Install missing dependencies
3. Launch the professional GUI

### **Manual Launch**

```bash
# Install dependencies
pip install -r requirements.txt

# Run professional GUI
python run_enhanced.py
```

### **First-Time Setup**

```bash
# For full functionality, you need:
pip install pywin32 Pillow

# Verify installation
python -c "import win32com.client; import PIL; print('All OK!')"
```

---

## 📊 Main Features

### 1. **All USB Device Detection**

Detects and analyzes:
- 💾 **Storage**: USB drives, external HDDs, SD cards
- ⌨️ **Input**: Keyboards, mice, touchpads, game controllers
- 🌐 **Network**: WiFi adapters, Ethernet, Bluetooth
- 🔌 **Hubs**: USB hubs and root hubs
- 🎥 **Audio/Video**: Webcams, microphones, speakers
- 🖨️ **Printers**: USB printers
- 📡 **Serial**: COM ports, Arduino, dev boards
- ❓ **Unknown**: Any USB device Windows can see

### 2. **Comprehensive Device Information**

For each device:
- **Identity**: Name, manufacturer, description
- **Hardware IDs**: VID, PID, serial number
- **Specifications**: USB speed, device class, capabilities
- **Connection**: Status, location, power consumption
- **History**: First seen, last seen, connection count
- **Security**: Vulnerability assessment, risk rating
- **Web Data**: Product page, manuals, reviews

### 3. **Device Images & Icons**

- 📸 Online device photos (when available)
- 🎨 Built-in fallback icons for all device types
- 🖼️ Professional visual identification

### 4. **Security Analysis**

- ⚠️ Known vulnerability detection
- 🛡️ Security rating (Good/Medium/Poor)
- 📋 Recall and warning checks
- 💉 BadUSB risk assessment
- ✅ Safety recommendations

### 5. **Forensic Timeline**

- 📅 Connection history
- ⏰ First/last seen timestamps
- 📈 Connection frequency patterns
- 🔍 Suspicious activity detection
- 📊 Usage statistics

### 6. **Storage Forensics** (Original Features)

- 📂 Registry artifact analysis
- 📝 Event log correlation
- 💿 Volume serial tracking
- 🗂️ Folder structure analysis
- 🗑️ Deleted file detection
- 💾 Storage capacity tracking

---

## 💻 User Interface

### **Multi-Tab Professional Interface**

#### Tab 1: **All USB Devices**
- Tree view grouped by device type
- Real-time device list
- Click any device for details
- Filter and search capabilities

#### Tab 2: **Storage Forensics**
- Historical storage device analysis
- Registry and event log parsing
- Forensic timeline reconstruction
- Suspicious device detection

#### Tab 3: **Timeline Analysis**
- Chronological connection history
- Pattern detection
- Anomaly highlighting
- Visual timeline

### **Device Details Panel**

Shows:
- Device photo/icon
- Complete specifications
- Manufacturer information
- Security assessment
- Web resources
- Technical details

---

## 📤 Export & Reporting

### **Available Formats**

- **CSV**: Device inventory for Excel
- **PDF**: Professional reports
- **JSON**: Machine-readable data
- **XLSX**: Spreadsheet with formatting

### **Export Options**

```
📊 Export CSV     → Quick device list
📄 Generate Report → Full professional report
💾 Export JSON    → API/integration format
📑 Export XLSX    → Excel workbook
```

---

## 🔧 Technical Details

### **Architecture**

```
┌─────────────────────────────────────┐
│      Professional GUI (Tkinter)    │
├─────────────────────────────────────┤
│  ┌──────────┐  ┌─────────────────┐ │
│  │ WMI      │  │ Registry/Logs   │ │
│  │ Real-time│  │ Forensics       │ │
│  └──────────┘  └─────────────────┘ │
├─────────────────────────────────────┤
│  ┌──────────┐  ┌─────────────────┐ │
│  │ Device   │  │ Web Lookup      │ │
│  │ Icons    │  │ & Security      │ │
│  └──────────┘  └─────────────────┘ │
├─────────────────────────────────────┤
│      Analysis & Correlation         │
└─────────────────────────────────────┘
```

### **Key Modules**

1. **usb_device_manager.py**: WMI-based device enumeration
2. **device_icons.py**: Embedded device type icons
3. **enhanced_online_lookup.py**: Web scraping & API queries
4. **gui_enhanced.py**: Professional multi-tab interface
5. **registry_parser.py**: Windows registry forensics
6. **eventlog_parser.py**: Event log analysis
7. **correlation.py**: Device record correlation
8. **analysis.py**: Anomaly detection & scoring

### **Dependencies**

```python
pywin32>=300      # WMI access (Windows only)
Pillow>=10.0.0    # Image display
openpyxl>=3.0.0   # Excel export
reportlab>=3.6.0  # PDF generation
```

---

## 🎯 Use Cases

### **Security Audits**

*"Check if unauthorized USB devices were used"*

1. Scan all current devices
2. Review device security ratings
3. Check for unknown/suspicious devices
4. Export audit report
5. Review timeline for after-hours activity

### **Forensic Investigations**

*"Investigate USB storage usage"*

1. Go to Storage Forensics tab
2. Analyze historical connections
3. Review first/last seen dates
4. Check deleted file artifacts
5. Generate forensic report

### **IT Asset Management**

*"Document all USB peripherals"*

1. Scan all devices
2. Export comprehensive CSV
3. Track device inventory
4. Monitor for changes

### **Troubleshooting**

*"USB device not working"*

1. Scan devices
2. Locate problematic device
3. Check status and driver info
4. View manufacturer website
5. Download correct drivers

### **Compliance**

*"Ensure only approved devices are used"*

1. Export device list
2. Compare against approved list
3. Flag unauthorized devices
4. Generate compliance report

---

## 📖 Documentation

- **[Professional Edition Guide](PROFESSIONAL_EDITION_GUIDE.md)** - Complete user guide
- **[Quick Start](QUICKSTART.md)** - Get started in 5 minutes
- **[Configuration](CONFIGURATION.md)** - Settings and options
- **[Device Analysis](DEVICE_ANALYSIS.md)** - Analysis features
- **[Command Reference](COMMAND_REFERENCE.md)** - CLI commands

---

## 🔐 Security & Privacy

### **Data Protection**

- ✅ All analysis runs locally
- ✅ No data sent to external servers
- ✅ Web lookups are optional
- ✅ No telemetry or tracking
- ✅ Open source and auditable

### **Required Permissions**

- **User Mode**: Basic device listing
- **Admin Mode**: Full WMI access, comprehensive data

---

## 🆚 Comparison

| Feature | Basic Tool | Professional |
|---------|-----------|-------------|
| **Device Types** | Storage only | All USB devices |
| **Detection** | Registry | Real-time WMI |
| **Information** | Basic | Comprehensive |
| **Security** | None | Vulnerability DB |
| **Images** | Online only | Built-in icons |
| **Interface** | Single view | Multi-tab |
| **Timeline** | Limited | Full forensics |
| **Web Lookup** | Basic | Enhanced |
| **Export** | CSV, PDF | CSV, PDF, JSON, XLSX |

---

## 🐛 Troubleshooting

### **"WMI not available"**

**Solution**: Install pywin32
```bash
pip install pywin32
```

### **"No devices found"**

**Solution**: Run as Administrator
```bash
# Right-click Command Prompt → Run as Administrator
python run_enhanced.py
```

### **"Images not displaying"**

**Solution**: Install Pillow
```bash
pip install Pillow
```

### **Slow Performance**

**Solution**: 
- Close other applications
- Run in User mode (not Admin) for faster scans
- Disable web lookups in settings

---

## 🎓 Learning Resources

### **USB Fundamentals**
- USB.org - Official specifications
- USB-IDs.org - Device ID database
- Linux USB documentation

### **Windows Forensics**
- Registry forensics guides
- Event log analysis
- WMI query reference

### **Security**
- BadUSB research
- USB security standards
- NIST guidelines

---

## 📝 Version History

### **Professional Edition v2.0** (December 2025)
- ✨ All USB device detection
- ✨ Real-time WMI integration
- ✨ Built-in device icons
- ✨ Enhanced web lookup
- ✨ Security vulnerability database
- ✨ Professional multi-tab GUI
- ✨ Timeline analysis
- ✨ Comprehensive device information

### **Original v1.0**
- ✓ Storage device forensics
- ✓ Registry parsing
- ✓ Event log analysis
- ✓ Basic GUI

---

## 🤝 Contributing

Want to enhance the tool? You can:
- Add custom device detectors
- Enhance online lookup sources
- Add export formats
- Implement security checks
- Add OS support (Linux, macOS)

---

## 📄 License

[Your License Here]

---

## 🙏 Credits

- Inspired by Wireshark's comprehensive approach
- Built with Python, tkinter, and open-source libraries
- Device database from USB.org and community sources

---

## 📞 Support

For issues or questions:
1. Check documentation
2. Review troubleshooting guide
3. Check Windows Event Viewer
4. Verify dependencies
5. Test with Administrator rights

---

## 🎉 Get Started Now!

```bash
# Launch in 3 seconds!
launch_professional.bat
```

or

```bash
python run_enhanced.py
```

**Welcome to professional USB forensics! 🔍**

---

*Making USB device analysis as comprehensive as network analysis with Wireshark*
