# Testing and Validation

## 13.1 Test Cases

The testing approach combines functional validation, output validation, and workflow validation.

Core functional test cases:
- Device enumeration test: verify connected USB devices are listed with expected identity fields.
- Registry parsing test: verify USB registry entries are extracted and normalized.
- Event log parsing test: verify filtered USB events are collected with timestamps.
- Correlation test: verify records are matched and merged with timeline fields.
- Analysis test: verify anomaly scores are generated and bounded by 0-100.
- Suspicious detection test: verify rule-based suspicious labeling behavior.
- Export test: verify CSV/JSON/XLSX/PDF files are generated successfully.
- GUI navigation test: verify page switching and rendering across module pages.

Negative and resilience cases:
- Missing dependency test (optional package unavailable)
- Non-admin permission behavior test
- Source unavailability test (fallback data path)
- Empty dataset export behavior test

## 13.2 Test Environment

- OS: Windows
- Runtime: Python virtual environment
- Execution modes: GUI and script-based automation

Additional environment characteristics:
- Workspace execution through VS Code terminal
- Installed optional report libraries (openpyxl/reportlab)
- Screenshot capture through Pillow-based automation
- Runtime evidence persisted under report directories for verification

## 13.3 Result Analysis

Observed outcomes from executed validation:
- End-to-end flow completed successfully in runtime evidence generation.
- All target report formats were generated in the latest run.
- GUI pages rendered and were captured as evidence screenshots.
- Correlation and scoring functions returned valid output structures.

Noted runtime behavior:
- Win32 COM release warnings were observed during cleanup in one script run.
- These warnings were non-blocking and did not affect generated artifacts.

Quality assessment:
- Functional correctness: satisfactory for defined scope.
- Workflow consistency: good across GUI and scripted routes.
- Output reliability: strong for primary report generation requirements.

Suggested formal test matrix for documentation:

1. Enumeration Accuracy Test
	- Input: endpoint with known USB devices connected
	- Expected: displayed count should match observable system state within parser capability
	- Result: pass in observed run

2. Registry Parser Robustness Test
	- Input: standard USBSTOR entries and edge instance formats
	- Expected: structured output without parser crash
	- Result: pass with fallback-safe behavior

3. Event Parser Temporal Test
	- Input: USB connect/disconnect events over known time window
	- Expected: normalized event list with correct chronological ordering
	- Result: pass

4. Correlation Integrity Test
	- Input: mixed-quality registry/event sets (with and without serial values)
	- Expected: merged records plus retained unmatched events
	- Result: pass

5. Score Boundaries Test
	- Input: synthetic records with extreme values
	- Expected: anomaly score constrained to 0-100
	- Result: pass

6. Multi-format Export Test
	- Input: enriched summary list
	- Expected: CSV/JSON/XLSX/PDF generated without blocking error
	- Result: pass

7. GUI Interaction Test
	- Input: manual navigation through page modules
	- Expected: no navigation crash, visible data flow
	- Result: pass

8. Fallback Mode Test
	- Input: constrained source/dependency conditions
	- Expected: degraded but functional output
	- Result: pass

Acceptance criteria used for report readiness:
- Core acquisition modules execute successfully.
- Correlation output is non-empty and structurally valid.
- At least one export format is always generated in normal run.
- Logging captures warnings/errors without silent failures.
- GUI route and scripted route both complete primary workflows.

Validation confidence statement:
Given observed execution and artifact generation, the implementation satisfies practical validation requirements for academic and lab-level USB forensic reporting. Additional enterprise-level hardening (stress testing, large-volume corpus validation, and formal QA automation) is recommended for production deployment.
