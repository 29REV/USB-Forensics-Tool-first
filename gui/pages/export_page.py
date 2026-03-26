import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import logging
import os

from core.registry_parser import parse_registry
from core.eventlog_parser import parse_event_logs
from core.correlation import correlate
from core.analysis import summarize, merge_trace_analysis
from core.wireshark_bridge import WiresharkBridge
from core.usb_trace_analysis import analyze_usb_trace, match_trace_report
from utils.report_generator import write_csv, write_json, write_xlsx, write_pdf
from utils.settings import load_settings

logger = logging.getLogger(__name__)

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ExportPage(ttk.Frame):
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
        # Header
        header = ttk.Frame(self, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="📁 Export Reports", style='Header.TLabel').pack(anchor=tk.W)
        
        # Export options
        options_frame = ttk.LabelFrame(self, text="Export Options", padding=15)
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(options_frame, text="Format:", style='Title.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        self.export_format = ttk.Combobox(options_frame, values=['CSV', 'JSON', 'XLSX', 'PDF'], state='readonly', width=15)
        self.export_format.set('CSV')
        self.export_format.pack(side=tk.LEFT, padx=(0, 20))

        if self.wireshark_enabled:
            ttk.Checkbutton(
                options_frame,
                text="Include optional Wireshark USB behavior analysis",
                variable=self.include_trace_var
            ).pack(side=tk.LEFT, padx=(0, 20))
        
        btn_export = tk.Button(
            options_frame, text="📤 Generate & Save", command=self._export_report,
            bg='#3b82f6', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        btn_export.pack(side=tk.LEFT)

        if self.wireshark_enabled:
            trace_frame = ttk.LabelFrame(self, text="Optional Capture File", padding=10)
            trace_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
            ttk.Entry(trace_frame, textvariable=self.capture_file_var, width=100).pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Button(
                trace_frame, text="📂 Browse", command=self._browse_capture_file,
                bg='#3b82f6', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
            ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Export log
        log_frame = ttk.LabelFrame(self, text="Export Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.export_log = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD, font=('Courier New', 9),
            bg='#f9fafb', fg='#1f2937', height=15
        )
        self.export_log.pack(fill=tk.BOTH, expand=True)

    def _browse_capture_file(self):
        filename = filedialog.askopenfilename(
            title="Select USB Capture File",
            filetypes=[("Capture or JSON Files", "*.pcapng *.pcap *.cap *.json *.ndjson"), ("All files", "*.*")]
        )
        if filename:
            self.capture_file_var.set(filename)

    def _augment_with_trace_analysis(self, summaries):
        if not self.wireshark_enabled:
            return summaries
        if not self.include_trace_var.get() or not self.capture_file_var.get().strip():
            return summaries

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
        return enriched

    def _export_report(self):
        fmt = self.export_format.get().lower()
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{fmt}",
            filetypes=[(f"{fmt.upper()} Files", f"*.{fmt}")]
        )
        
        if not file_path:
            return
        
        def export_thread():
            try:
                self.export_log.insert(tk.END, f"\n{'='*70}\n")
                self.export_log.insert(tk.END, f"Exporting {fmt.upper()} to: {file_path}\n")
                self.export_log.update()
                
                regs = parse_registry()
                evs = parse_event_logs()
                devices = correlate(regs, evs)
                summaries = summarize(devices)
                summaries = self._augment_with_trace_analysis(summaries)
                
                if fmt == 'csv':
                    write_csv(summaries, file_path)
                elif fmt == 'json':
                    write_json(summaries, file_path)
                elif fmt == 'xlsx':
                    write_xlsx(summaries, file_path)
                elif fmt == 'pdf':
                    write_pdf(summaries, file_path)
                
                self.export_log.insert(tk.END, f"✓ Successfully exported to {file_path}\n")
                messagebox.showinfo("Success", f"Report exported to:\n{file_path}")
                logger.info(f"Report exported to {file_path}")
                
            except Exception as e:
                self.export_log.insert(tk.END, f"✗ Error: {e}\n")
                messagebox.showerror("Error", f"Export failed: {e}")
                logger.error(f"Export failed: {e}")
        
        thread = threading.Thread(target=export_thread, daemon=True)
        thread.start()
