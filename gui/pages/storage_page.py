import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import logging

from core.registry_parser import parse_registry
from core.eventlog_parser import parse_event_logs
from core.correlation import correlate
from core.analysis import summarize
from utils.report_generator import write_csv, write_json

logger = logging.getLogger(__name__)

class StoragePage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style='Main.TFrame')
        self.app = app
        self.current_summaries = []
        self._create_page()

    def _create_page(self):
        # Header
        header = ttk.Frame(self, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="💾 Storage Forensics Analysis", style='Header.TLabel').pack(anchor=tk.W)
        
        # Control panel
        ctrl_frame = ttk.Frame(self, style='Main.TFrame')
        ctrl_frame.pack(fill=tk.X, padx=20, pady=10)
        
        btn_analyze = tk.Button(
            ctrl_frame, text="🔄 Analyze Storage", command=self._analyze_storage,
            bg='#3b82f6', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        btn_analyze.pack(side=tk.LEFT, padx=5)
        
        btn_export = tk.Button(
            ctrl_frame, text="💾 Save Report", command=self._export_storage_report,
            bg='#10b981', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        btn_export.pack(side=tk.LEFT, padx=5)
        
        # Analysis text
        text_frame = ttk.Frame(self, style='Main.TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.storage_text = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD, font=('Courier New', 9),
            bg='#f9fafb', fg='#1f2937'
        )
        self.storage_text.pack(fill=tk.BOTH, expand=True)

    def _analyze_storage(self):
        def analyze_thread():
            try:
                self.storage_text.delete('1.0', tk.END)
                self.storage_text.insert(tk.END, "Analyzing storage devices...\n\n")
                self.storage_text.update()
                
                regs = parse_registry()
                evs = parse_event_logs()
                devices = correlate(regs, evs)
                summaries = summarize(devices)
                
                self.current_summaries = summaries
                
                self.storage_text.delete('1.0', tk.END)
                self.storage_text.insert(tk.END, "STORAGE FORENSICS ANALYSIS REPORT\n")
                self.storage_text.insert(tk.END, "="*70 + "\n\n")
                
                for i, summary in enumerate(summaries, 1):
                    self.storage_text.insert(tk.END, f"\n{'─'*70}\n")
                    self.storage_text.insert(tk.END, f"Device #{i}\n")
                    self.storage_text.insert(tk.END, f"{'─'*70}\n")
                    
                    for key, value in summary.items():
                        self.storage_text.insert(tk.END, f"{key:20s}: {value}\n")
                
                logger.info(f"Storage analysis complete: {len(summaries)} devices")
                
            except Exception as e:
                logger.error(f"Storage analysis error: {e}")
                self.storage_text.insert(tk.END, f"Error: {e}")
        
        thread = threading.Thread(target=analyze_thread, daemon=True)
        thread.start()
    
    def _export_storage_report(self):
        if not self.current_summaries:
            messagebox.showwarning("No Data", "Please analyze storage first")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("JSON Files", "*.json")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    write_json(self.current_summaries, file_path)
                else:
                    write_csv(self.current_summaries, file_path)
                messagebox.showinfo("Success", f"Report saved to:\n{file_path}")
                logger.info(f"Report exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
