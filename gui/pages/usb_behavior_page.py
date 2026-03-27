import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import logging

from core.wireshark_bridge import WiresharkBridge
from core.usb_trace_analysis import analyze_usb_trace
from utils.settings import load_settings

logger = logging.getLogger(__name__)

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class USBBehaviorPage(ttk.Frame):
    """Dedicated optional page for packet-level USB behavior analysis."""

    def __init__(self, parent, app):
        super().__init__(parent, style='Main.TFrame')
        self.app = app
        self.settings = load_settings()
        self.bridge = WiresharkBridge(WORKSPACE_ROOT)
        self.capture_file_var = tk.StringVar(value=self.settings.get('wireshark_capture_file', ''))
        self._create_page()

    def _create_page(self):
        header = ttk.Frame(self, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="🧬 USB Behavior Analysis", style='Header.TLabel').pack(anchor=tk.W)

        control_frame = ttk.LabelFrame(self, text="Capture Input (Optional, Manual)", padding=10)
        control_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        row = ttk.Frame(control_frame)
        row.pack(fill=tk.X)
        ttk.Label(row, text="Capture File:", style='Title.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(row, textvariable=self.capture_file_var, width=90).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(
            row,
            text="📂 Browse",
            command=self._browse_capture_file,
            bg='#3b82f6',
            fg='white',
            font=('Segoe UI', 10),
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor='hand2',
        ).pack(side=tk.LEFT, padx=(10, 0))

        tk.Button(
            control_frame,
            text="🔍 Analyze USB Behavior",
            command=self._analyze_behavior,
            bg='#8b5cf6',
            fg='white',
            font=('Segoe UI', 10),
            padx=15,
            pady=8,
            relief=tk.FLAT,
            cursor='hand2',
        ).pack(anchor=tk.W, pady=(10, 0))

        runtime = self.bridge.runtime_info(self.settings.get('wireshark_tshark_path') or None)
        ttk.Label(
            control_frame,
            text=f"Runtime status: {runtime['message']}",
            foreground='#6b7280',
            font=('Segoe UI', 9),
        ).pack(anchor=tk.W, pady=(8, 0))

        text_frame = ttk.Frame(self, style='Main.TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.output_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=('Courier New', 9),
            bg='#f9fafb',
            fg='#1f2937',
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def _browse_capture_file(self):
        filename = filedialog.askopenfilename(
            title="Select USB Capture File",
            filetypes=[("Capture or JSON Files", "*.pcapng *.pcap *.cap *.json *.ndjson"), ("All files", "*.*")],
        )
        if filename:
            self.capture_file_var.set(filename)

    def _analyze_behavior(self):
        capture_file = self.capture_file_var.get().strip()
        if not capture_file:
            messagebox.showwarning("Missing Capture", "Please select a capture file")
            return

        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, "Analyzing USB communication behavior...\n\n")

        def worker():
            try:
                packets, capture_meta = self.bridge.load_capture(
                    capture_file,
                    tshark_override=self.settings.get('wireshark_tshark_path') or None,
                )
                trace_result = analyze_usb_trace(packets)

                lines = [
                    "USB BEHAVIOR ANALYSIS",
                    "=" * 70,
                    "",
                    f"Capture File: {capture_meta.get('capture_file', '')}",
                    f"Capture Source: {capture_meta.get('capture_source', '')}",
                    f"USB Packets Parsed: {trace_result.get('packet_count', 0)}",
                    f"Trace-visible Devices: {trace_result.get('device_count', 0)}",
                    f"Suspicious Device Count: {trace_result.get('suspicious_device_count', 0)}",
                    "",
                ]

                selected = trace_result.get('selected_device', {}) or {}
                if selected:
                    lines.extend([
                        "Primary Device Communication Summary",
                        "-" * 70,
                        selected.get('next_level_summary', 'No summary available'),
                        f"VID:PID: {selected.get('vendor_id', '')}:{selected.get('product_id', '')}",
                        f"Enumeration Observed: {'Yes' if selected.get('enumeration_detected') else 'No'}",
                        f"Enumeration Steps: {', '.join(selected.get('enumeration_steps', [])) or 'Not fully visible'}",
                        f"Interface Classes: {', '.join(selected.get('interface_classes', [])) or 'Unknown'}",
                        f"Transfer Breakdown: {selected.get('transfer_breakdown', {})}",
                        "",
                    ])

                    patterns = selected.get('suspicious_patterns', []) or []
                    lines.append("Suspicious USB Activity")
                    lines.append("-" * 70)
                    if patterns:
                        lines.extend([f"- {pattern}" for pattern in patterns])
                    else:
                        lines.append("- No suspicious packet-level patterns detected for the primary device")
                    lines.append("")

                devices = trace_result.get('devices', []) or []
                if devices:
                    lines.append("All Devices in Trace")
                    lines.append("-" * 70)
                    for index, device in enumerate(devices, 1):
                        lines.append(
                            f"{index}. {device.get('device_key', 'unknown')} | "
                            f"packets={device.get('packet_count', 0)} | "
                            f"score={device.get('suspicious_score', 0)}"
                        )

                self.after(0, self._set_output, "\n".join(lines))
            except Exception as exc:
                logger.error("USB behavior analysis failed: %s", exc, exc_info=True)
                self.after(0, self._set_output, f"USB behavior analysis failed:\n\n{exc}")

        threading.Thread(target=worker, daemon=True).start()

    def _set_output(self, text):
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, text)
