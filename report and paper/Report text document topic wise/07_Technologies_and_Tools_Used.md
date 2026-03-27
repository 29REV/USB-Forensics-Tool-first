# Technologies and Tools Used

## 7.1 Hardware Requirements

- Windows-based laptop or desktop system
- CPU: modern multi-core processor (Intel/AMD)
- RAM: minimum 8 GB (16 GB recommended for concurrent analysis and export)
- Storage: minimum 2 GB free for project, logs, traces, and report artifacts
- USB ports for live removable device testing and validation

For advanced workflows (URB/trace processing), higher memory and storage improve performance when handling large capture files.

## 7.2 Software Requirements

- Operating System: Windows (primary target platform)
- Python: 3.9 or above (validated in this workspace with Python 3.13)
- pip and virtual environment support
- Optional administrator privileges for full registry/event and ETW access
- Optional Wireshark/tshark installation for packet-level analysis

On non-Windows or restricted systems, fallback/mock paths allow demonstration but with reduced forensic depth.

## 7.3 Programming Language

Python is used for all core components because it provides:
- Rapid implementation of parser and analysis logic
- Good interoperability with Windows-specific libraries
- Strong ecosystem for report generation and automation
- Clear, maintainable module structure for academic and practical use

## 7.4 Libraries and Frameworks

- tkinter/ttk: GUI
- pywin32: Windows APIs (WMI/Event Log)
- winreg: Registry access
- openpyxl: XLSX reports
- reportlab: PDF reports
- Pillow: image/screenshot handling
- python-docx: document generation utilities

Additional project-relevant packages/tools:
- etl-parser: ETW trace parsing support for URB workflows
- colorama/python-dotenv: optional utility enhancements
- Mermaid syntax (in docs): architecture/data-flow visualization

## 7.5 Development Environment

- VS Code workspace
- Virtual environment (.venv)
- Git-based source control
- Local runtime evidence folders for generated reports and screenshots

Development workflow characteristics:
- Modular code in core/gui/utils/extensions folders
- Test and helper scripts under scripts/
- Report assets managed under report and paper/
- Logging support for traceability during execution and troubleshooting
