import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

from core.wireshark_bridge import WiresharkBridge
from utils.admin_elevation import prompt_run_as_administrator
from utils.settings import load_settings, save_settings

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SettingsPage(ttk.Frame):
  def __init__(self, parent, app):
    super().__init__(parent, style='Main.TFrame')
    self.app = app
    self.settings = load_settings()
    self.bridge = WiresharkBridge(WORKSPACE_ROOT)
    self.show_splash_var = tk.BooleanVar(value=bool(self.settings.get('show_splash', True)))
    self.wireshark_option_var = tk.BooleanVar(value=bool(self.settings.get('wireshark_enabled', False)))
    self.tshark_path_var = tk.StringVar(value=self.settings.get('wireshark_tshark_path', ''))
    self.capture_file_var = tk.StringVar(value=self.settings.get('wireshark_capture_file', ''))
    self._create_page()

  def _create_page(self):
    header = ttk.Frame(self, style='Main.TFrame')
    header.pack(fill=tk.X, padx=20, pady=20)
    ttk.Label(header, text="⚙️ Settings & About", style='Header.TLabel').pack(anchor=tk.W)

    settings_notebook = ttk.Notebook(self)
    settings_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    gen_frame = ttk.Frame(settings_notebook)
    settings_notebook.add(gen_frame, text="General")

    ttk.Label(gen_frame, text="Application Settings", font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, padx=20, pady=20)
    ttk.Checkbutton(gen_frame, text="Show splash screen", variable=self.show_splash_var).pack(anchor=tk.W, padx=20, pady=5)
    ttk.Checkbutton(
      gen_frame,
      text="Offer Wireshark capture-analysis option in analysis/export/security pages",
      variable=self.wireshark_option_var,
    ).pack(anchor=tk.W, padx=20, pady=5)

    wireshark_frame = ttk.LabelFrame(gen_frame, text="Optional Wireshark Integration", padding=12)
    wireshark_frame.pack(fill=tk.X, padx=20, pady=15)

    ttk.Label(
      wireshark_frame,
      text="This only enables the option. It does not run capture analysis automatically.",
      foreground='#6b7280',
      font=('Segoe UI', 9)
    ).pack(anchor=tk.W, pady=(0, 10))

    tshark_row = ttk.Frame(wireshark_frame)
    tshark_row.pack(fill=tk.X, pady=5)
    ttk.Label(tshark_row, text="tshark Path:", style='Title.TLabel').pack(side=tk.LEFT, padx=(0, 10))
    ttk.Entry(tshark_row, textvariable=self.tshark_path_var, width=90).pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Button(
      tshark_row,
      text="📂 Browse",
      command=self._browse_tshark,
      bg='#3b82f6',
      fg='white',
      font=('Segoe UI', 10),
      padx=15,
      pady=8,
      relief=tk.FLAT,
      cursor='hand2'
    ).pack(side=tk.LEFT, padx=(10, 0))

    capture_row = ttk.Frame(wireshark_frame)
    capture_row.pack(fill=tk.X, pady=5)
    ttk.Label(capture_row, text="Default Capture:", style='Title.TLabel').pack(side=tk.LEFT, padx=(0, 10))
    ttk.Entry(capture_row, textvariable=self.capture_file_var, width=90).pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Button(
      capture_row,
      text="📂 Browse",
      command=self._browse_capture,
      bg='#3b82f6',
      fg='white',
      font=('Segoe UI', 10),
      padx=15,
      pady=8,
      relief=tk.FLAT,
      cursor='hand2'
    ).pack(side=tk.LEFT, padx=(10, 0))

    runtime = self.bridge.runtime_info(self.tshark_path_var.get().strip() or None)
    ttk.Label(
      wireshark_frame,
      text=f"Detected environment: {runtime['message']}",
      foreground='#6b7280',
      font=('Segoe UI', 9)
    ).pack(anchor=tk.W, pady=(8, 10))

    actions_row = ttk.Frame(wireshark_frame)
    actions_row.pack(fill=tk.X, pady=(0, 6))

    tk.Button(
      actions_row,
      text="▶ Launch Wireshark",
      command=self._launch_wireshark,
      bg='#2563eb',
      fg='white',
      font=('Segoe UI', 10),
      padx=15,
      pady=8,
      relief=tk.FLAT,
      cursor='hand2'
    ).pack(side=tk.LEFT)

    tk.Button(
      actions_row,
      text="🛡 Run as Administrator",
      command=self._run_as_administrator,
      bg='#0f766e',
      fg='white',
      font=('Segoe UI', 10),
      padx=15,
      pady=8,
      relief=tk.FLAT,
      cursor='hand2'
    ).pack(side=tk.LEFT, padx=(10, 0))

    tk.Button(
      gen_frame,
      text="💾 Save Settings",
      command=self._save_settings,
      bg='#10b981',
      fg='white',
      font=('Segoe UI', 10),
      padx=15,
      pady=8,
      relief=tk.FLAT,
      cursor='hand2'
    ).pack(anchor=tk.W, padx=20, pady=(0, 15))

    about_frame = ttk.Frame(settings_notebook)
    settings_notebook.add(about_frame, text="About")

    about_text = """
USB FORENSICS TOOL - PROFESSIONAL EDITION
═════════════════════════════════════════════════════════

Version: 2.0
Release: December 2025

CREATED BY:
  • Srirevanth A
  • Naghul Pranav C B
  • Deeekshitha

FEATURES:
  ✓ Real-time USB device detection and analysis
  ✓ Comprehensive storage forensics
  ✓ Timeline analysis with activity tracking
  ✓ Security advisory checking
  ✓ Optional Wireshark-backed USB behaviour analysis
  ✓ Multi-format report export (CSV, JSON, XLSX, PDF)

This tool can now correlate basic USB connection events with
optional packet-level USB communication behaviour when you
provide a saved capture file.

═════════════════════════════════════════════════════════
"""

    about_display = scrolledtext.ScrolledText(
      about_frame, wrap=tk.WORD, font=('Courier New', 10),
      bg='#f9fafb', fg='#1f2937', height=20
    )
    about_display.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    about_display.insert('1.0', about_text)
    about_display.config(state=tk.DISABLED)

  def _browse_tshark(self):
    filename = filedialog.askopenfilename(
      title="Select tshark executable",
      filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
    )
    if filename:
      self.tshark_path_var.set(filename)

  def _browse_capture(self):
    filename = filedialog.askopenfilename(
      title="Select default USB capture file",
      filetypes=[("Capture or JSON Files", "*.pcapng *.pcap *.cap *.json *.ndjson"), ("All files", "*.*")],
    )
    if filename:
      self.capture_file_var.set(filename)

  def _save_settings(self):
    save_settings({
      'show_splash': self.show_splash_var.get(),
      'reports_dir': self.settings.get('reports_dir', 'reports'),
      'wireshark_enabled': self.wireshark_option_var.get(),
      'wireshark_tshark_path': self.tshark_path_var.get().strip(),
      'wireshark_capture_file': self.capture_file_var.get().strip(),
    })
    self.settings = load_settings()
    messagebox.showinfo("Settings", "Settings saved")

  def _launch_wireshark(self):
    try:
      capture_file = self.capture_file_var.get().strip() or None
      launched_path = self.bridge.launch_wireshark(capture_file=capture_file)
      messagebox.showinfo("Wireshark", f"Started Wireshark from:\n{launched_path}")
    except Exception as exc:
      messagebox.showerror("Wireshark", str(exc))

  def _run_as_administrator(self):
    prompt_run_as_administrator(parent=self, reason="USB registry and event log access works best with elevated permissions.")
