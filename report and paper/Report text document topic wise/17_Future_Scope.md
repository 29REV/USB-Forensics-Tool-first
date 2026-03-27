# Future Scope

## 17.1 GUI Development

Add richer timeline widgets, case management views, and one-click evidence bundles.

Planned GUI enhancements:
- Case profile management (case ID, analyst, notes, evidence tags)
- Better timeline filters (device/type/risk range)
- Built-in screenshot/evidence attachment support
- Report preview before final export

## 17.2 Cross-Platform Support

Expand native collection support for Linux/macOS with equivalent artifact mappings.

Cross-platform roadmap:
- Introduce platform abstraction for parsers
- Implement Linux udev/syslog-style source adapters
- Implement macOS USB/log source adapters
- Maintain common output schema for parity across OS families

## 17.3 Advanced Threat Detection

Introduce model-assisted baselining and stronger behavioral analytics for BadUSB-like threats.

Detection roadmap:
- Device behavior baselines per endpoint/user profile
- Sequence anomaly detection over historical USB timelines
- Better weighting for suspicious communication signatures
- Confidence-level reporting for each risk indicator

## 17.4 Integration with Forensic Suites

Enable export adapters and API connectors for integration into broader DFIR platforms.

Integration roadmap:
- SIEM-friendly JSON export profiles
- Ticket/case tool connectors
- Chain-of-custody metadata packaging
- Interoperability with forensic timeline and evidence management platforms

Phased enhancement plan:

Phase 1: Usability and Reporting
- Add customizable report templates per investigation type.
- Introduce richer GUI filters and in-app evidence bookmarks.
- Add one-click report bundle creation (CSV+JSON+PDF+screenshots).

Phase 2: Analytical Depth
- Introduce confidence scoring per correlated field.
- Add trend and baseline comparison across multiple runs.
- Improve suspicious pattern explainability with rule trace output.

Phase 3: Integration and Automation
- Add scheduler integration for periodic endpoint checks.
- Publish REST-style export adapters for external platforms.
- Add machine-readable metadata manifest for evidence packages.

Phase 4: Enterprise Readiness
- Role-based access controls for case handling.
- Tamper-evident export signature options.
- Centralized evidence index for multi-endpoint investigations.

Expected long-term impact:
These enhancements can transition the project from focused endpoint utility to a broader investigation support platform while retaining the modular architecture established in the current codebase.
