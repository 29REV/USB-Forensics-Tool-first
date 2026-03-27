# System Overview

## 5.1 Existing System

Traditional USB forensic analysis in many organizations is process-driven rather than platform-driven. Analysts typically gather USB evidence through separate utilities and manual checks:
- Device listing through operating system tools
- Registry artifact extraction using scripts or forensic viewers
- Event log review through administrative consoles
- Final consolidation in spreadsheets or manually written notes

This approach can work for small cases but is difficult to scale under incident pressure. Evidence quality depends heavily on analyst experience and documentation discipline.

## 5.2 Limitations of Existing System

- Fragmented data collection and interpretation
- Higher analyst effort and longer turnaround time
- Inconsistent output formats and evidence quality
- Limited built-in anomaly detection logic

Additional limitations include weak extensibility, poor repeatability, and limited integration between technical evidence and final report output.

## 5.3 Proposed System

The proposed system is a modular Python application that:
- Enumerates USB devices and metadata
- Parses USB-related registry and event artifacts
- Correlates evidence into unified device records
- Generates anomaly scores and suspicious indicators
- Exports reports in CSV, JSON, XLSX, and PDF
- Supports optional advanced modules (Wireshark and URB workflows)

The system is organized as a layered workflow with clear module responsibilities. It supports interactive use through a professional GUI and automated use through script/CLI style execution. This dual-mode operation improves adoption across both academic and operational contexts.

## 5.4 Advantages of Proposed System

- Unified investigation workflow in one platform
- Reproducible outputs with structured exports
- Reduced manual interpretation overhead
- Extensible architecture for future forensic capabilities
- GUI + automation compatibility for different analyst preferences

Practical advantages observed in runtime use:
- Faster evidence-to-report cycle
- Consistent schema across generated output formats
- Easier handover between investigators due to standardized summaries
- Better maintainability through modular source design
