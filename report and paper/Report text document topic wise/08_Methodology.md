# Methodology

## 8.1 Data Collection

The methodology begins with structured data acquisition from multiple endpoint artifact sources. Rather than relying on one evidence stream, the tool gathers complementary records that describe device identity, activity timing, and behavior. Collection is modular, so each source can succeed or fail independently without blocking the entire pipeline.

Collected source categories:
- Device inventory and metadata from USB/PnP enumeration
- Registry artifacts for persistent historical traces
- Event logs for temporal connection/disconnection evidence
- Optional trace artifacts for deeper protocol-level interpretation

## 8.2 Registry Analysis

Registry analysis focuses on USB-relevant keys and subkeys to extract:
- Device IDs and instance identifiers
- Vendor and Product IDs (VID/PID)
- Serial-like values and device signatures
- Last write or observation context

Registry artifacts are valuable because they can remain after active sessions end, helping investigators establish historical USB presence.

## 8.3 Event Log Analysis

Event log analysis extracts USB connect/disconnect style records and converts them into normalized timestamped entries. These records provide temporal context that registry-only analysis cannot fully represent.

Processing steps include:
- Reading relevant event channels/sources
- Filtering by USB-relevant event IDs used in project logic
- Converting to normalized UTC-style timestamps
- Packaging events into correlation-ready structures

## 8.4 File System Artifact Analysis

Where available, enrichment functions produce file-system-adjacent summaries such as storage capacity metrics, folder structure indicators, and deleted-file counters. These are not direct disk-forensic reconstructions but analyst-friendly indicators to prioritize deeper review.

This stage supports quick triage by highlighting unusual patterns (for example, high usage, deletion-heavy context, or abrupt structure changes).

## 8.5 Data Correlation Technique

Correlation merges heterogeneous source records into single device-centric entities. Matching relies on serial fields, device IDs, and name-pattern heuristics. Because source quality may vary, the logic allows partial matching and preserves unmatched evidence as separate records rather than discarding it.

Correlation goals:
- Maximize evidence retention
- Reduce duplicate device representations
- Build consistent first_seen/last_seen timelines
- Support downstream scoring and reporting

## 8.6 Timeline Reconstruction

Timeline reconstruction computes chronological views per device from event and artifact timestamps. The process identifies earliest and latest known activity windows and aggregates intermediate event records.

The resulting timeline supports:
- Incident scoping (when activity likely started/ended)
- Device reuse pattern interpretation
- Report narratives and case communication
