import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import logging

from core.registry_parser import parse_registry
from core.eventlog_parser import parse_event_logs
from core.correlation import correlate
from core.analysis import summarize, detect_suspicious, merge_trace_analysis
from core.wireshark_bridge import WiresharkBridge
from core.usb_trace_analysis import analyze_usb_trace, match_trace_report
from utils.settings import load_settings

logger = logging.getLogger(__name__)

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SecurityPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style='Main.TFrame')
        self.app = app
        self.settings = load_settings()
        self.bridge = WiresharkBridge(WORKSPACE_ROOT)
        self.wireshark_enabled = bool(self.settings.get('wireshark_enabled', False))
        self.include_trace_var = tk.BooleanVar(value=False)
        self.capture_file_var = tk.StringVar(value=self.settings.get('wireshark_capture_file', ''))
        self._create_page()

    def _create_page(self):
        header = ttk.Frame(self, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="🛡️ Security Advisories", style='Header.TLabel').pack(anchor=tk.W)

        ctrl_frame = ttk.Frame(self, style='Main.TFrame')
        ctrl_frame.pack(fill=tk.X, padx=20, pady=10)

        btn_check = tk.Button(
            ctrl_frame,
            text="🔍 Check Security",
            command=self._check_security,
            bg='#ef4444',
            fg='white',
            font=('Segoe UI', 10),
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor='hand2'
        )
        btn_check.pack(side=tk.LEFT, padx=5)

        if self.wireshark_enabled:
            trace_frame = ttk.LabelFrame(self, text="Optional Capture Correlation", padding=10)
            trace_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
            ttk.Checkbutton(
                trace_frame,
                text="Augment suspicious-device detection with Wireshark/tshark USB trace analysis",
                variable=self.include_trace_var
            ).pack(anchor=tk.W, pady=(0, 8))

            path_row = ttk.Frame(trace_frame)
            path_row.pack(fill=tk.X)
            ttk.Entry(path_row, textvariable=self.capture_file_var, width=90).pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Button(
                path_row,
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

        text_frame = ttk.Frame(self, style='Main.TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.security_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=('Courier New', 9),
            bg='#f9fafb',
            fg='#1f2937'
        )
        self.security_text.pack(fill=tk.BOTH, expand=True)

    def _browse_capture_file(self):
        filename = filedialog.askopenfilename(
            title="Select USB Capture File",
            filetypes=[("Capture or JSON Files", "*.pcapng *.pcap *.cap *.json *.ndjson"), ("All files", "*.*")],
        )
        if filename:
            self.capture_file_var.set(filename)

    def _check_security(self):
        def security_thread():
            try:
                self.security_text.delete('1.0', tk.END)
                self.security_text.insert(tk.END, "Checking security advisories...\n\n")
                self.security_text.update()

                regs = parse_registry()
                evs = parse_event_logs()
                devices = correlate(regs, evs)
                summaries = summarize(devices)
                trace_note = ""

                if self.wireshark_enabled and self.include_trace_var.get() and self.capture_file_var.get().strip():
                    try:
                        packets, capture_meta = self.bridge.load_capture(
                            self.capture_file_var.get().strip(),
                            tshark_override=self.settings.get('wireshark_tshark_path') or None,
                        )
                        trace_result = analyze_usb_trace(packets)
                        enriched = []
                        for summary in summaries:
                            trace_report = match_trace_report(summary, trace_result)
                            if trace_report:
                                trace_report = dict(trace_report)
                                trace_report['capture_file'] = capture_meta.get('capture_file', '')
                                trace_report['capture_source'] = capture_meta.get('capture_source', '')
                                enriched.append(merge_trace_analysis(summary, trace_report))
                            else:
                                enriched.append(summary)
                        summaries = enriched
                        trace_note = (
                            f"Optional capture correlation loaded from {capture_meta.get('capture_file', '')}. "
                            f"Trace-visible devices: {trace_result.get('device_count', 0)}\n\n"
                        )
                    except Exception as trace_exc:
                        trace_note = f"Optional capture correlation was skipped: {trace_exc}\n\n"

                suspicious = detect_suspicious(summaries)

                lines = ["SECURITY ANALYSIS REPORT", "=" * 70, "", trace_note]
                if suspicious:
                    lines.append(f"FOUND {len(suspicious)} SUSPICIOUS DEVICES:\n")
                    for device, reason in suspicious:
                        lines.append(f"Device: {device.get('name', 'Unknown')}")
                        lines.append(f"VID:PID: {device.get('vid', '----')}:{device.get('pid', '----')}")
                        lines.append(f"Serial: {device.get('serial', 'Unknown')}")
                        if device.get('communication_summary'):
                            lines.append(f"Communication Summary: {device.get('communication_summary')}")
                        lines.append(f"Reason: {reason}")
                        lines.append("")
                else:
                    lines.append("No suspicious devices detected")

                self.security_text.delete('1.0', tk.END)
                self.security_text.insert(tk.END, "\n".join(line for line in lines if line is not None))
                logger.info("Security check complete")

            except Exception as e:
                logger.error(f"Security check error: {e}", exc_info=True)
                self.security_text.delete('1.0', tk.END)
                self.security_text.insert(tk.END, f"Error: {e}")

        thread = threading.Thread(target=security_thread, daemon=True)
        thread.start()
