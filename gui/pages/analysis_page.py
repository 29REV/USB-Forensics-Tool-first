import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from dataclasses import asdict, is_dataclass
from datetime import datetime
import threading
import logging

from core.registry_parser import parse_registry
from core.eventlog_parser import parse_event_logs
from core.correlation import correlate
from core.analysis import enrich_summary, merge_trace_analysis
from core.wireshark_bridge import WiresharkBridge
from core.usb_trace_analysis import analyze_usb_trace, match_trace_report
from utils.settings import load_settings

logger = logging.getLogger(__name__)

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _record_to_dict(record):
    if isinstance(record, dict):
        return dict(record)
    if is_dataclass(record):
        return asdict(record)
    return dict(getattr(record, '__dict__', {}))


class AnalysisPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style='Main.TFrame')
        self.app = app
        self.settings = load_settings()
        self.bridge = WiresharkBridge(WORKSPACE_ROOT)
        self.device_map = {}
        self.wireshark_enabled = bool(self.settings.get('wireshark_enabled', False))
        self.include_trace_var = tk.BooleanVar(value=False)
        self.capture_file_var = tk.StringVar(value=self.settings.get('wireshark_capture_file', ''))
        self._create_page()
        self._populate_analysis_devices()

    def _create_page(self):
        header = ttk.Frame(self, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="🔍 Advanced Analysis", style='Header.TLabel').pack(anchor=tk.W)

        sel_frame = ttk.Frame(self, style='Main.TFrame')
        sel_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(sel_frame, text="Select Device:", style='Title.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        self.analysis_combo = ttk.Combobox(sel_frame, width=70, font=('Segoe UI', 9), state='readonly')
        self.analysis_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        btn_analyze = tk.Button(
            sel_frame,
            text="📊 Analyze Device",
            command=self._run_device_analysis,
            bg='#8b5cf6',
            fg='white',
            font=('Segoe UI', 10),
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor='hand2'
        )
        btn_analyze.pack(side=tk.LEFT)

        if self.wireshark_enabled:
            trace_frame = ttk.LabelFrame(self, text="Optional Wireshark Deep USB Behaviour Analysis", padding=10)
            trace_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

            ttk.Checkbutton(
                trace_frame,
                text="Include capture-file analysis for enumeration and suspicious communication patterns",
                variable=self.include_trace_var
            ).pack(anchor=tk.W, pady=(0, 8))

            capture_row = ttk.Frame(trace_frame)
            capture_row.pack(fill=tk.X)
            ttk.Label(capture_row, text="Capture File:", style='Title.TLabel').pack(side=tk.LEFT, padx=(0, 10))
            ttk.Entry(capture_row, textvariable=self.capture_file_var, width=90).pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Button(
                capture_row,
                text="📂 Browse",
                command=self._browse_capture_file,
                bg='#3b82f6',
                fg='white',
                font=('Segoe UI', 10),
                padx=15,
                pady=8,
                relief=tk.FLAT,
                cursor='hand2'
            ).pack(side=tk.LEFT, padx=(10, 0))

            info = self.bridge.runtime_info(self.settings.get('wireshark_tshark_path') or None)
            ttk.Label(
                trace_frame,
                text=f"Runtime status: {info['message']}",
                foreground='#6b7280',
                font=('Segoe UI', 9)
            ).pack(anchor=tk.W, pady=(8, 0))

        text_frame = ttk.Frame(self, style='Main.TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.analysis_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=('Courier New', 9),
            bg='#f9fafb',
            fg='#1f2937'
        )
        self.analysis_text.pack(fill=tk.BOTH, expand=True)

    def _browse_capture_file(self):
        filename = filedialog.askopenfilename(
            title="Select USB Capture File",
            filetypes=[
                ("Capture or JSON Files", "*.pcapng *.pcap *.cap *.json *.ndjson"),
                ("All files", "*.*"),
            ],
        )
        if filename:
            self.capture_file_var.set(filename)

    def _populate_analysis_devices(self):
        try:
            devices = correlate(parse_registry(), parse_event_logs())
            self.device_map = {}
            labels = []
            for device in devices:
                device_dict = _record_to_dict(device)
                label = self._device_label(device_dict)
                self.device_map[label] = device_dict
                labels.append(label)
            self.analysis_combo['values'] = sorted(labels)
            if labels:
                self.analysis_combo.current(0)
        except Exception as e:
            logger.error(f"Error populating devices: {e}")

    def _device_label(self, device):
        identity = device.get('serial') or device.get('device_id') or 'Unknown Device'
        name = device.get('name') or 'Unknown'
        vid = device.get('vid') or '----'
        pid = device.get('pid') or '----'
        return f"{identity} | {name} | {vid}:{pid}"

    def _run_device_analysis(self):
        selected_label = self.analysis_combo.get()
        if not selected_label:
            messagebox.showwarning("No Device", "Please select a device")
            return

        self.analysis_text.delete('1.0', tk.END)
        self.analysis_text.insert(tk.END, "Analyzing device...\n\n")

        def analysis_thread():
            try:
                devices = correlate(parse_registry(), parse_event_logs())
                current_map = {self._device_label(_record_to_dict(device)): _record_to_dict(device) for device in devices}
                selected_device = current_map.get(selected_label) or self.device_map.get(selected_label)
                if not selected_device:
                    raise RuntimeError("Selected device could not be resolved from current device records")

                summary = enrich_summary(selected_device)
                trace_error = ""

                if self.wireshark_enabled and self.include_trace_var.get() and self.capture_file_var.get().strip():
                    try:
                        packets, capture_meta = self.bridge.load_capture(
                            self.capture_file_var.get().strip(),
                            tshark_override=self.settings.get('wireshark_tshark_path') or None,
                        )
                        trace_result = analyze_usb_trace(packets, device_hint=summary)
                        trace_report = match_trace_report(summary, trace_result) or trace_result.get('selected_device', {})
                        if trace_report:
                            trace_report = dict(trace_report)
                            trace_report['capture_file'] = capture_meta.get('capture_file', '')
                            trace_report['capture_source'] = capture_meta.get('capture_source', '')
                            summary = merge_trace_analysis(summary, trace_report)
                        else:
                            trace_error = "Capture loaded, but no matching USB device was identified in the trace."
                    except Exception as trace_exc:
                        trace_error = str(trace_exc)
                        logger.error("Optional Wireshark analysis failed: %s", trace_exc)

                result = self._format_report(summary, trace_error)
                self.after(0, self._show_report, result)
            except Exception as exc:
                logger.error("Device analysis failed: %s", exc, exc_info=True)
                self.after(0, self._show_report, f"Analysis failed:\n\n{exc}")

        threading.Thread(target=analysis_thread, daemon=True).start()

    def _show_report(self, report_text):
        self.analysis_text.delete('1.0', tk.END)
        self.analysis_text.insert(tk.END, report_text)

    def _format_report(self, summary, trace_error):
        lines = [
            "DEVICE ANALYSIS REPORT",
            "=" * 70,
            "",
            f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Device: {summary.get('name', 'Unknown')}",
            f"Device ID: {summary.get('device_id', 'Unknown')}",
            f"VID:PID: {summary.get('vid', '----')}:{summary.get('pid', '----')}",
            f"Serial: {summary.get('serial', 'Unknown')}",
            f"First Seen: {summary.get('first_seen', 'Unknown')}",
            f"Last Seen: {summary.get('last_seen', 'Unknown')}",
            f"Total Connections: {summary.get('total_connections', 0)}",
            f"Anomaly Score: {summary.get('anomaly_score', 0)}",
            "",
            "Base Analysis",
            "-" * 70,
            f"Storage Usage: {summary.get('storage_analysis', {}).get('usage_percentage', 0)}%",
            f"Deleted Files Found: {summary.get('deleted_files_analysis', {}).get('deleted_count', 0)}",
            f"Known Vulnerabilities: {summary.get('reputation_analysis', {}).get('known_vulnerabilities', 0)}",
            "",
        ]

        wireshark_analysis = summary.get('wireshark_analysis', {}) or {}
        if wireshark_analysis:
            lines.extend([
                "Wireshark Deep USB Behaviour Analysis",
                "-" * 70,
                f"Communication Summary: {summary.get('communication_summary', '')}",
                f"Capture Source: {wireshark_analysis.get('capture_source', 'tshark')}",
                f"Capture File: {wireshark_analysis.get('capture_file', '')}",
                f"Enumeration Observed: {'Yes' if wireshark_analysis.get('enumeration_detected') else 'No'}",
                f"Enumeration Steps: {', '.join(wireshark_analysis.get('enumeration_steps', [])) or 'Not fully visible'}",
                f"Interface Classes: {', '.join(wireshark_analysis.get('interface_classes', [])) or 'Unknown'}",
                f"Transfer Breakdown: {wireshark_analysis.get('transfer_breakdown', {})}",
                f"Vendor Requests: {wireshark_analysis.get('vendor_request_count', 0)}",
                f"USB Error Count: {wireshark_analysis.get('error_count', 0)}",
                "",
                "Suspicious USB Activity",
                "-" * 70,
            ])
            patterns = wireshark_analysis.get('suspicious_patterns', []) or []
            if patterns:
                lines.extend([f"- {pattern}" for pattern in patterns])
            else:
                lines.append("- No suspicious packet-level patterns were detected in the optional capture")
            lines.append("")
        elif trace_error:
            lines.extend([
                "Optional Wireshark Analysis",
                "-" * 70,
                trace_error,
                "",
            ])
        else:
            lines.extend([
                "Optional Wireshark Analysis",
                "-" * 70,
                "Not run. Enable the capture-file option above to inspect enumeration and packet-level behavior.",
                "",
            ])

        return "\n".join(lines)
