# Unified USB Forensics Framework for Host-Level and Packet-Level Investigation

Srirevanth A, Naghul Pranav C B, Deeekshitha  
Dr.N.G.P. Institute of Technology

## Abstract

USB devices continue to be a major source of forensic complexity because evidence is distributed across host metadata, communication traces, and analyst interpretation workflows. This paper presents a unified USB forensics framework that combines host-level artifacts, timeline correlation, packet-informed behavior interpretation, and investigator-centered reporting into one consistent investigative model. The framework integrates registry and event history, Wireshark-assisted communication evidence, URB-oriented transfer behavior, and structured risk reasoning to improve the reliability of conclusions under incomplete visibility. In addition to technical analysis, the framework emphasizes practical deployment through interface design and engineering traceability, allowing investigations to remain reproducible as the tool evolves. A modular architecture supports extension of advanced analyses while preserving the stability of core evidence processing. The resulting approach is designed for both academic and operational digital forensics, where explainability, defensibility, and workflow efficiency are equally important.

Index Terms: USB forensics, digital investigation, timeline correlation, URB behavior, packet analysis, forensic reporting, software traceability

## I. Introduction

Removable USB media remains widely used in enterprise and personal systems for portability and rapid data exchange. The same convenience makes USB an important attack and exfiltration vector in modern incident response. Investigators frequently face a fragmented evidence landscape in which host records, low-level transfer signals, and contextual activity are analyzed separately. This separation increases interpretation time and can reduce evidentiary confidence.

A robust USB investigation requires answers to three connected questions: which device interacted with the system, what sequence of actions occurred, and how defensible the interpretation is under forensic scrutiny. Existing practice often addresses these questions with disconnected tools, producing gaps between acquisition, analysis, and reporting.

This work proposes a unified framework that treats USB forensics as a layered evidence-correlation and reasoning problem. The framework connects user interface workflow, host artifact analysis, Wireshark-level communication interpretation, URB-level transfer behavior, and Git-centered engineering traceability into a single research and operational model.

The major contributions are as follows:

1. A consolidated investigation model linking host and packet-level USB evidence.
2. A correlation approach that reconstructs coherent timelines from heterogeneous records.
3. A theory-driven risk assessment method based on explainable forensic indicators.
4. A workflow design that combines analyst usability with reproducible engineering governance.

## II. Problem Definition and Threat Perspective

### A. Evidence Fragmentation Problem

USB evidence is distributed across multiple system layers. Registry and event traces are typically high-availability but limited in behavioral depth. Communication traces provide richer semantics but are harder to interpret at scale. Without correlation, each source yields partial truth and can produce conflicting narratives.

### B. Threat Perspective

The framework addresses common investigation scenarios including:

1. Unauthorized removable media usage.
2. Data exfiltration through storage-class devices.
3. Device impersonation and role-shifting behavior.
4. BadUSB-style behavior involving suspicious interface patterns.
5. Anti-forensic patterns such as abrupt deletion after transfer.

### C. Forensic Goals

The investigation model is designed to maximize:

1. Temporal coherence of events.
2. Explainability of suspiciousness scoring.
3. Analyst efficiency in triage and deep analysis.
4. Reproducibility of conclusions across tool versions.

## III. Related Work Overview

Host-artifact USB forensics is well established in digital investigation literature and is valued for speed and availability. However, host-only approaches may miss communication behavior and intent-level indicators.

Packet-centered approaches, especially those using Wireshark, provide protocol semantics and richer interaction context. Their limitations are operational cost and analyst complexity when used without host correlation.

Behavioral and anomaly-oriented studies have shown that weighted forensic indicators can improve triage quality, but black-box scoring models are often difficult to justify in legal or audit settings.

This framework builds on these strands by combining host, transfer, and workflow evidence into an explainable and reproducible analysis model.

## IV. Proposed Unified Framework

### A. Layer 1: Evidence Acquisition

The acquisition layer gathers USB-relevant evidence from host and communication perspectives. Host artifacts provide identity and timing signals. Wireshark-oriented traces provide protocol-level context. URB-oriented observations provide request and transfer behavior cues that help bridge high-level and low-level interpretation.

A platform-aware strategy is applied: full-fidelity extraction is prioritized where available, while constrained environments are handled with explicit confidence awareness to avoid hidden assumptions.

### B. Layer 2: Correlation and Timeline Reconstruction

This layer transforms heterogeneous evidence into device-centric records. Correlation is treated as confidence-weighted matching across identifiers, timing, and behavioral consistency. The output is a normalized timeline describing first appearance, activity windows, role continuity, and transition behavior.

The central objective is not simple aggregation; it is reconstruction of coherent forensic narratives with explicit uncertainty boundaries.

### C. Layer 3: Behavioral Interpretation and Risk Reasoning

Risk reasoning uses interpretable forensic indicators rather than opaque classification. Representative indicators include abnormal connection bursts, suspicious role transitions, deletion patterns near transfer windows, and request-level irregularities.

The model produces explainable risk outcomes where each escalation is linked to visible evidence factors. This is intended to support defensibility in both academic validation and operational reporting.

### D. Layer 4: Investigator Interaction and Reporting

The interaction layer supports two complementary modes:

1. Graphical exploration for analyst-driven triage and timeline interpretation.
2. Command-oriented operation for repeatable, scriptable workflows.

Report outputs are structured around identity, chronology, behavior, and confidence. This uniform structure improves communication between technical investigators, management stakeholders, and case documentation processes.

### E. Layer 5: Extensibility and Governance

The framework adopts modular extension principles to isolate advanced analysis from core evidence processing. This reduces regression risk in forensic-critical paths and supports controlled analytical evolution.

To preserve reproducibility, development governance is aligned with Git-based practices including branch isolation, commit traceability, and release tagging. This ensures that investigative conclusions can be mapped to specific tool states.

## V. Wireshark and URB in the Analytical Pipeline

Wireshark-centered analysis contributes protocol semantics and helps validate or challenge host-level timelines. It is especially valuable for understanding enumeration behavior, transfer context, and communication irregularities.

URB-centered interpretation provides transfer-behavior granularity, including control, interrupt, and bulk dynamics. In the unified pipeline, URB evidence acts as a bridge between host metadata and packet-level traces, improving interpretation in ambiguous cases.

The framework intentionally treats deep communication analysis as investigator-directed rather than always-on, balancing analytical depth with operational practicality.

## VI. Interface-Centered Forensic Workflow

The user interface is treated as a methodological component, not only a display layer. A strong forensic interface should reduce cognitive overload, foreground high-value evidence, and preserve narrative continuity from discovery to reporting.

Three design principles guide this layer:

1. Evidence clarity through device-centric grouping and timeline ordering.
2. Decision support through filters, prioritization cues, and suspiciousness explanations.
3. Narrative continuity through report-ready evidence structuring.

By integrating these principles, the framework supports both rapid triage and defensible final analysis.

## VII. Evaluation Methodology and Observations

The framework is evaluated using four practical dimensions.

### A. Functional Coverage

The model spans host artifacts, interface-guided investigation, Wireshark-informed communication analysis, URB-oriented transfer interpretation, and extensible advanced analytics.

### B. Correlation Quality

The primary quality target is temporal and logical consistency across evidence sources. Better cross-source consistency improves confidence and reduces isolated false interpretations.

### C. Analyst Usability

Dual interaction paths enable adoption by both exploratory analysts and automation-focused operators. This increases practical utility across different investigation contexts.

### D. Reproducibility and Maintainability

Modular architecture with Git-centered governance improves maintainability and allows repeatable validation as the framework evolves.

## VIII. Discussion

A key insight from this work is that USB forensics quality depends as much on integration strategy as on individual evidence sources. Registry, event history, packet traces, and transfer signals each provide limited truth when isolated; combined interpretation produces stronger investigative confidence.

Another insight is that explainability is central to forensic adoption. Risk results are more actionable when investigators can trace each conclusion back to observable evidence factors.

Finally, reproducibility should be considered part of forensic rigor. Without version-traceable engineering workflow, analytical results are harder to validate over time.

## IX. Limitations

The framework has practical limitations:

1. Full host-fidelity evidence is strongest on supported Windows environments.
2. Wireshark and URB interpretation depends on trace availability and capture conditions.
3. Suspicious behavior indicators are probabilistic and should not be treated as direct attribution.
4. Final conclusions may require corroboration from non-USB telemetry.

These limits are explicitly acknowledged to avoid overclaiming.

## X. Conclusion and Future Scope

This paper presented a theory-oriented USB forensic framework that unifies host artifacts, communication interpretation, behavioral reasoning, interface workflow, modular analytics, and Git-based reproducibility. The integrated model strengthens evidence coherence and improves the path from raw observations to defensible conclusions.

Future work includes probabilistic confidence modeling, broader cross-host federation, and deeper integration with enterprise DFIR telemetry for stronger contextual attribution.

## References

[1] E. Casey, Digital Evidence and Computer Crime, Academic Press.  
[2] K. Kent, S. Chevalier, T. Grance, and H. Dang, Guide to Integrating Forensic Techniques into Incident Response, NIST SP 800-86.  
[3] Microsoft, Windows Event Logging and Diagnostics Documentation.  
[4] Wireshark Foundation, Wireshark User Documentation.  
[5] N. L. Beebe, Digital forensic research trends and challenges, Digital Investigation.  
[6] S. Liu, J. Slay, and S. Furnell, USB forensic analysis on modern operating systems, Journal of Digital Forensics Research.  
[7] B. Beveridge et al., Device-level trace interpretation in endpoint investigation, Digital Investigation.  
[8] A. T. Sherman and J. Dykstra, Reproducibility in evolving forensic software environments, Journal of Cyber Forensics.  
