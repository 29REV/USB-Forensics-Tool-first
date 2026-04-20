# Abstract

The USB Forensics Tool is a Windows-focused digital forensics application developed in Python to investigate USB device activity through host artifacts. The solution integrates USB device discovery, registry evidence extraction, event-log parsing, artifact correlation, anomaly detection, and report generation in one workflow. The primary goal is to reduce manual forensic effort while preserving technical transparency and reproducibility.

The system collects evidence from multiple layers: hardware/device metadata, registry traces, event timestamps, and optional low-level communication traces. Correlation logic unifies these records into device-centric timelines, then analysis functions compute risk-oriented indicators such as missing serial behavior, repeated connection patterns, storage-related concerns, and suspicious communication summaries. Reports can be exported in CSV, JSON, XLSX, PDF, and detailed JSON formats for both analyst review and downstream automation.

The project supports two execution styles: a professional GUI for investigators and script-based runs for repeatable evidence generation. Advanced modules support optional Wireshark/tshark USB trace interpretation and URB capture workflows. A practical design feature is graceful degradation: if privileged Windows APIs, administrator permissions, or optional libraries are unavailable, the tool uses controlled fallback paths to remain operational.

In the current validation run, the platform successfully captured runtime screenshots, produced structured report artifacts, and generated a current USB device snapshot. Overall, the implementation demonstrates a modular, extensible, and investigation-ready architecture suitable for academic reporting and applied endpoint forensics.
