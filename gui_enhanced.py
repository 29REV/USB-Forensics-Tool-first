#!/usr/bin/env python3
"""Professional USB Forensics GUI - Modern Design with Side Panel

Features:
  - Professional side navigation panel
  - Real-time USB device detection
  - Storage forensics analysis
  - Timeline analysis with chronological events
  - Device details with images and security info
  - Advanced filtering and search
  - Multi-format report export
  - Security advisory checking
  - Device tree view with categorization
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from tkinter import font as tkfont
import threading
import logging
from datetime import datetime

from usb_device_manager import get_all_usb_devices
from device_icons import get_icon_for_device_type, get_pil_image_for_device_type
from enhanced_online_lookup import get_comprehensive_device_info, get_device_security_info
from registry_parser import parse_registry
from eventlog_parser import parse_event_logs
from correlation import correlate
from analysis import summarize, detect_suspicious
from report_generator import write_csv, write_json, write_xlsx, write_pdf
import settings

logger = logging.getLogger(__name__)


class USBForensicsApp(tk.Tk):
    """Professional USB Forensics Application with Modern Side Panel."""
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        self.title("USB Forensics Tool - Professional Edition")
        self.geometry("1400x900")
        self.configure(bg="#ffffff")
        
        self.resizable(True, True)
        
        # Set styles
        self._setup_styles()
        
        # Create main layout
        self._create_main_layout()
        
        # Load initial data
        self.current_devices = []
        self.current_summaries = []
        
        logger.info("USB Forensics GUI initialized")
    
    def _setup_styles(self):
        """Setup modern styling."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Sidebar.TFrame', background='#1f2937')
        style.configure('Main.TFrame', background='#f3f4f6')
        style.configure('Sidebar.TLabel', background='#1f2937', foreground='#ffffff')
        style.configure('Header.TLabel', background='#ffffff', foreground='#1f2937', font=('Segoe UI', 14, 'bold'))
        style.configure('Title.TLabel', foreground='#1f2937', font=('Segoe UI', 12, 'bold'))
        
        # Treeview styling
        style.configure('Treeview', font=('Segoe UI', 9))
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
    
    def _create_main_layout(self):
        """Create main application layout with side panel."""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Side panel (navigation)
        self.sidebar = ttk.Frame(main_container, style='Sidebar.TFrame', width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self.sidebar.pack_propagate(False)
        
        # Content area
        self.content_area = ttk.Frame(main_container, style='Main.TFrame')
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create sidebar content
        self._create_sidebar()
        
        # Create main content pages
        self.pages = {}
        self._create_all_devices_page()
        self._create_storage_forensics_page()
        self._create_timeline_page()
        self._create_analysis_page()
        self._create_export_page()
        self._create_security_page()
        self._create_settings_page()
        
        # Show first page
        self.show_page('devices')
    
    def _create_sidebar(self):
        """Create sidebar navigation panel."""
        # Header
        header_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=20)
        
        title_label = ttk.Label(header_frame, text="📱 USB Forensics", style='Sidebar.TLabel', font=('Segoe UI', 12, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Professional Edition", style='Sidebar.TLabel', font=('Segoe UI', 9))
        subtitle_label.pack()
        
        # Separator
        sep = tk.Frame(self.sidebar, bg='#374151', height=1)
        sep.pack(fill=tk.X, padx=10, pady=10)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ('devices', '📱 All Devices', self._on_nav_devices),
            ('storage', '💾 Storage Forensics', self._on_nav_storage),
            ('timeline', '📊 Timeline', self._on_nav_timeline),
            ('analysis', '🔍 Analysis', self._on_nav_analysis),
            ('security', '🛡️ Security', self._on_nav_security),
            ('export', '📁 Export', self._on_nav_export),
            ('settings', '⚙️ Settings', self._on_nav_settings),
        ]
        
        for key, label, command in nav_items:
            btn_frame = tk.Frame(self.sidebar, bg='#1f2937')
            btn_frame.pack(fill=tk.X, padx=8, pady=4)
            
            btn = tk.Label(
                btn_frame, 
                text=label,
                bg='#374151',
                fg='#ffffff',
                font=('Segoe UI', 10),
                padx=15,
                pady=12,
                cursor='hand2',
                relief=tk.FLAT
            )
            btn.pack(fill=tk.X)
            btn.bind('<Button-1>', lambda e, k=key, c=command: (c(), self._update_nav_highlight(k)))
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg='#3b82f6'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg='#374151'))
            
            self.nav_buttons[key] = btn
        
        # Bottom section
        bottom_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)
        
        about_label = ttk.Label(
            bottom_frame,
            text="USB Forensics Tool v2.0\nCreated by:\n• Srirevanth A\n• Naghul Pranav C B\n• Deeekshitha",
            style='Sidebar.TLabel',
            font=('Segoe UI', 8),
            justify=tk.LEFT
        )
        about_label.pack()
    
    def _update_nav_highlight(self, page_key):
        """Update navigation button highlights."""
        for key, btn in self.nav_buttons.items():
            if key == page_key:
                btn.config(bg='#3b82f6')
            else:
                btn.config(bg='#374151')
    
    def _on_nav_devices(self):
        self.show_page('devices')
    
    def _on_nav_storage(self):
        self.show_page('storage')
    
    def _on_nav_timeline(self):
        self.show_page('timeline')
    
    def _on_nav_analysis(self):
        self.show_page('analysis')
    
    def _on_nav_security(self):
        self.show_page('security')
    
    def _on_nav_export(self):
        self.show_page('export')
    
    def _on_nav_settings(self):
        self.show_page('settings')
    
    def show_page(self, page_name):
        """Show specific page."""
        # Hide all pages
        for page in self.pages.values():
            page.pack_forget()
        
        # Show selected page
        if page_name in self.pages:
            self.pages[page_name].pack(fill=tk.BOTH, expand=True)
    
    def _create_all_devices_page(self):
        """Create all USB devices page."""
        page = ttk.Frame(self.content_area, style='Main.TFrame')
        self.pages['devices'] = page
        
        # Header
        header = ttk.Frame(page, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(header, text="🔍 All Connected USB Devices", style='Header.TLabel').pack(anchor=tk.W)
        
        # Control panel
        ctrl_frame = ttk.Frame(page, style='Main.TFrame')
        ctrl_frame.pack(fill=tk.X, padx=20, pady=10)
        
        btn_refresh = tk.Button(
            ctrl_frame, text="🔄 Scan Devices", command=self._scan_all_devices,
            bg='#3b82f6', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        btn_refresh.pack(side=tk.LEFT, padx=5)
        
        btn_copy = tk.Button(
            ctrl_frame, text="📋 Copy Info", command=self._copy_device_info,
            bg='#10b981', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        btn_copy.pack(side=tk.LEFT, padx=5)
        
        btn_details = tk.Button(
            ctrl_frame, text="📄 View Details", command=self._show_device_details,
            bg='#8b5cf6', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        btn_details.pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(page, style='Main.TFrame')
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(search_frame, text="Search:", style='Title.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        self.device_search = ttk.Entry(search_frame, font=('Segoe UI', 9), width=40)
        self.device_search.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.device_search.bind('<KeyRelease>', lambda e: self._filter_devices())
        
        # Device tree
        tree_frame = ttk.Frame(page, style='Main.TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.device_tree = ttk.Treeview(
            tree_frame,
            columns=('Type', 'Vendor', 'Model', 'Serial', 'Status'),
            height=20,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        vsb.config(command=self.device_tree.yview)
        hsb.config(command=self.device_tree.xview)
        
        self.device_tree.column('#0', width=50, minwidth=50)
        self.device_tree.column('Type', width=100, minwidth=100)
        self.device_tree.column('Vendor', width=150, minwidth=150)
        self.device_tree.column('Model', width=200, minwidth=200)
        self.device_tree.column('Serial', width=150, minwidth=150)
        self.device_tree.column('Status', width=100, minwidth=100)
        
        self.device_tree.heading('#0', text='#')
        self.device_tree.heading('Type', text='Device Type')
        self.device_tree.heading('Vendor', text='Manufacturer')
        self.device_tree.heading('Model', text='Device Name')
        self.device_tree.heading('Serial', text='Serial Number')
        self.device_tree.heading('Status', text='Status')
        
        self.device_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.device_tree.bind('<Double-1>', self._on_device_double_click)
        
        # Details panel
        detail_frame = ttk.LabelFrame(page, text="📋 Device Details", style='Title.TLabel')
        detail_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.device_details = scrolledtext.ScrolledText(
            detail_frame, height=8, width=80, wrap=tk.WORD,
            font=('Courier New', 9), bg='#f9fafb', fg='#1f2937'
        )
        self.device_details.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load devices
        self._scan_all_devices()
    
    def _scan_all_devices(self):
        """Scan all USB devices."""
        def scan_thread():
            try:
                self.device_tree.delete(*self.device_tree.get_children())
                devices = get_all_usb_devices()
                self.current_devices = devices
                
                for i, device in enumerate(devices, 1):
                    status = "Connected" if device.connection_status == "Connected" else "Disconnected"
                    self.device_tree.insert('', 'end', text=str(i),
                        values=(
                            device.device_type or 'Unknown',
                            device.manufacturer or 'Unknown',
                            device.name or 'Unknown',
                            device.serial or 'Unknown',
                            status
                        )
                    )
                
                logger.info(f"Scanned {len(devices)} USB devices")
                
            except Exception as e:
                logger.error(f"Error scanning devices: {e}")
                messagebox.showerror("Error", f"Failed to scan devices: {e}")
        
        thread = threading.Thread(target=scan_thread, daemon=True)
        thread.start()
    
    def _filter_devices(self):
        """Filter devices by search term."""
        search_term = self.device_search.get().lower()
        
        for item in self.device_tree.get_children():
            values = self.device_tree.item(item)['values']
            text_repr = ' '.join(str(v).lower() for v in values)
            
            if search_term in text_repr or search_term == '':
                self.device_tree.item(item, tags=())
            else:
                self.device_tree.item(item, tags=('hidden',))
    
    def _on_device_double_click(self, event):
        """Handle device double-click."""
        selection = self.device_tree.selection()
        if selection:
            self._show_device_details()
    
    def _show_device_details(self):
        """Show detailed device information."""
        selection = self.device_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a device first")
            return
        
        item = selection[0]
        index = list(self.device_tree.get_children()).index(item)
        
        if index < len(self.current_devices):
            device = self.current_devices[index]
            
            details = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEVICE INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Device Type:        {device.device_type or 'Unknown'}
Manufacturer:       {device.manufacturer or 'Unknown'}
Device Name:        {device.name or 'Unknown'}
Device ID:          {device.device_id or 'Unknown'}
Serial Number:      {device.serial or 'Unknown'}
Status:             {device.connection_status or 'Unknown'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HARDWARE INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Vendor ID (VID):    {device.vid or 'Unknown'}
Product ID (PID):   {device.pid or 'Unknown'}
USB Speed:          {device.speed or 'Unknown'}
Power Consumption:  {device.power_consumption or 'Unknown'}
Location:           {device.location or 'Unknown'}
Driver Version:     {device.driver_version or 'Unknown'}
Device Class:       {device.device_class or 'Unknown'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TIMELINE INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Last Arrival:       {device.last_arrival or 'Unknown'}
Last Removal:       {device.last_removal or 'Unknown'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            self.device_details.delete('1.0', tk.END)
            self.device_details.insert('1.0', details)
    
    def _copy_device_info(self):
        """Copy device info to clipboard."""
        selection = self.device_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a device first")
            return
        
        info = self.device_details.get('1.0', tk.END)
        self.clipboard_clear()
        self.clipboard_append(info)
        messagebox.showinfo("Copied", "Device information copied to clipboard!")
    
    def _create_storage_forensics_page(self):
        """Create storage forensics page."""
        page = ttk.Frame(self.content_area, style='Main.TFrame')
        self.pages['storage'] = page
        
        # Header
        header = ttk.Frame(page, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="💾 Storage Forensics Analysis", style='Header.TLabel').pack(anchor=tk.W)
        
        # Control panel
        ctrl_frame = ttk.Frame(page, style='Main.TFrame')
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
        text_frame = ttk.Frame(page, style='Main.TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.storage_text = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD, font=('Courier New', 9),
            bg='#f9fafb', fg='#1f2937'
        )
        self.storage_text.pack(fill=tk.BOTH, expand=True)
    
    def _analyze_storage(self):
        """Analyze storage devices."""
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
        """Export storage report."""
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
    
    def _create_timeline_page(self):
        """Create timeline analysis page."""
        page = ttk.Frame(self.content_area, style='Main.TFrame')
        self.pages['timeline'] = page
        
        # Header
        header = ttk.Frame(page, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="📊 Timeline Analysis", style='Header.TLabel').pack(anchor=tk.W)
        
        # Control panel
        ctrl_frame = ttk.Frame(page, style='Main.TFrame')
        ctrl_frame.pack(fill=tk.X, padx=20, pady=10)
        
        btn_refresh = tk.Button(
            ctrl_frame, text="🔄 Generate Timeline", command=self._generate_timeline,
            bg='#3b82f6', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        btn_refresh.pack(side=tk.LEFT, padx=5)
        
        # Timeline text
        text_frame = ttk.Frame(page, style='Main.TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.timeline_text = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD, font=('Courier New', 9),
            bg='#f9fafb', fg='#1f2937'
        )
        self.timeline_text.pack(fill=tk.BOTH, expand=True)
    
    def _generate_timeline(self):
        """Generate device timeline."""
        def timeline_thread():
            try:
                self.timeline_text.delete('1.0', tk.END)
                self.timeline_text.insert(tk.END, "Generating timeline...\n\n")
                self.timeline_text.update()
                
                regs = parse_registry()
                evs = parse_event_logs()
                devices = correlate(regs, evs)
                summaries = summarize(devices)
                
                # Sort by first seen
                sorted_summaries = sorted(summaries, key=lambda x: x.get('first_seen', '') or '', reverse=True)
                
                self.timeline_text.delete('1.0', tk.END)
                self.timeline_text.insert(tk.END, "USB DEVICE ACTIVITY TIMELINE\n")
                self.timeline_text.insert(tk.END, "="*70 + "\n\n")
                
                for device in sorted_summaries:
                    first = device.get('first_seen', 'Unknown')
                    last = device.get('last_seen', 'Unknown')
                    name = device.get('name', 'Unknown')
                    serial = device.get('serial_number', 'Unknown')
                    count = device.get('instance_count', 0)
                    
                    self.timeline_text.insert(tk.END, f"\n{name} ({serial})\n")
                    self.timeline_text.insert(tk.END, f"  First Seen: {first}\n")
                    self.timeline_text.insert(tk.END, f"  Last Seen:  {last}\n")
                    self.timeline_text.insert(tk.END, f"  Instances:  {count}\n")
                
                logger.info("Timeline generated")
                
            except Exception as e:
                logger.error(f"Timeline generation error: {e}")
                self.timeline_text.insert(tk.END, f"Error: {e}")
        
        thread = threading.Thread(target=timeline_thread, daemon=True)
        thread.start()
    
    def _create_analysis_page(self):
        """Create device analysis page."""
        page = ttk.Frame(self.content_area, style='Main.TFrame')
        self.pages['analysis'] = page
        
        # Header
        header = ttk.Frame(page, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="🔍 Advanced Analysis", style='Header.TLabel').pack(anchor=tk.W)
        
        # Device selector
        sel_frame = ttk.Frame(page, style='Main.TFrame')
        sel_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(sel_frame, text="Select Device:", style='Title.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        self.analysis_combo = ttk.Combobox(sel_frame, width=50, font=('Segoe UI', 9))
        self.analysis_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        btn_analyze = tk.Button(
            sel_frame, text="📊 Analyze Device", command=self._run_device_analysis,
            bg='#8b5cf6', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        btn_analyze.pack(side=tk.LEFT)
        
        # Analysis results
        text_frame = ttk.Frame(page, style='Main.TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.analysis_text = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD, font=('Courier New', 9),
            bg='#f9fafb', fg='#1f2937'
        )
        self.analysis_text.pack(fill=tk.BOTH, expand=True)
        
        # Load devices
        self._populate_analysis_devices()
    
    def _populate_analysis_devices(self):
        """Populate device list for analysis."""
        try:
            regs = parse_registry()
            devices = [str(r.get('serial_number', 'Unknown')) for r in regs if isinstance(r, dict) and r.get('serial_number')]
            self.analysis_combo['values'] = list(set(devices))
        except Exception as e:
            logger.error(f"Error populating devices: {e}")
    
    def _run_device_analysis(self):
        """Run device analysis."""
        if not self.analysis_combo.get():
            messagebox.showwarning("No Device", "Please select a device")
            return
        
        self.analysis_text.delete('1.0', tk.END)
        self.analysis_text.insert(tk.END, "Analyzing device...\n\n")
        
        result = f"""
DEVICE ANALYSIS REPORT
{'='*70}

Device: {self.analysis_combo.get()}
Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Detailed analysis results will be displayed here including:
  • Connection patterns
  • Usage history
  • Anomaly detection
  • Risk assessment
  • Recommendations

(Analysis data from registry and event logs)
"""
        
        self.analysis_text.insert(tk.END, result)
    
    def _create_security_page(self):
        """Create security advisory page."""
        page = ttk.Frame(self.content_area, style='Main.TFrame')
        self.pages['security'] = page
        
        # Header
        header = ttk.Frame(page, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="🛡️ Security Advisories", style='Header.TLabel').pack(anchor=tk.W)
        
        # Control panel
        ctrl_frame = ttk.Frame(page, style='Main.TFrame')
        ctrl_frame.pack(fill=tk.X, padx=20, pady=10)
        
        btn_check = tk.Button(
            ctrl_frame, text="🔍 Check Security", command=self._check_security,
            bg='#ef4444', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        btn_check.pack(side=tk.LEFT, padx=5)
        
        # Security results
        text_frame = ttk.Frame(page, style='Main.TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.security_text = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD, font=('Courier New', 9),
            bg='#f9fafb', fg='#1f2937'
        )
        self.security_text.pack(fill=tk.BOTH, expand=True)
    
    def _check_security(self):
        """Check security advisories."""
        def security_thread():
            try:
                self.security_text.delete('1.0', tk.END)
                self.security_text.insert(tk.END, "Checking security advisories...\n\n")
                self.security_text.update()
                
                regs = parse_registry()
                evs = parse_event_logs()
                devices = correlate(regs, evs)
                summaries = summarize(devices)
                
                # Check for suspicious devices
                suspicious = detect_suspicious(summaries)
                
                self.security_text.delete('1.0', tk.END)
                self.security_text.insert(tk.END, "SECURITY ANALYSIS REPORT\n")
                self.security_text.insert(tk.END, "="*70 + "\n\n")
                
                if suspicious:
                    self.security_text.insert(tk.END, f"⚠️  FOUND {len(suspicious)} SUSPICIOUS DEVICES:\n\n")
                    for device, reason in suspicious:
                        self.security_text.insert(tk.END, f"Device: {device.get('name', 'Unknown')}\n")
                        self.security_text.insert(tk.END, f"Reason: {reason}\n")
                        self.security_text.insert(tk.END, f"Serial: {device.get('serial_number', 'Unknown')}\n\n")
                else:
                    self.security_text.insert(tk.END, "✓ No suspicious devices detected\n")
                
                logger.info("Security check complete")
                
            except Exception as e:
                logger.error(f"Security check error: {e}")
                self.security_text.insert(tk.END, f"Error: {e}")
        
        thread = threading.Thread(target=security_thread, daemon=True)
        thread.start()
    
    def _create_export_page(self):
        """Create export page."""
        page = ttk.Frame(self.content_area, style='Main.TFrame')
        self.pages['export'] = page
        
        # Header
        header = ttk.Frame(page, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="📁 Export Reports", style='Header.TLabel').pack(anchor=tk.W)
        
        # Export options
        options_frame = ttk.LabelFrame(page, text="Export Options", padding=15)
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(options_frame, text="Format:", style='Title.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        self.export_format = ttk.Combobox(options_frame, values=['CSV', 'JSON', 'XLSX', 'PDF'], state='readonly', width=15)
        self.export_format.set('CSV')
        self.export_format.pack(side=tk.LEFT, padx=(0, 20))
        
        btn_export = tk.Button(
            options_frame, text="📤 Generate & Save", command=self._export_report,
            bg='#3b82f6', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        btn_export.pack(side=tk.LEFT)
        
        # Export log
        log_frame = ttk.LabelFrame(page, text="Export Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.export_log = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD, font=('Courier New', 9),
            bg='#f9fafb', fg='#1f2937', height=15
        )
        self.export_log.pack(fill=tk.BOTH, expand=True)
    
    def _export_report(self):
        """Export analysis report."""
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
    
    def _create_settings_page(self):
        """Create settings page."""
        page = ttk.Frame(self.content_area, style='Main.TFrame')
        self.pages['settings'] = page
        
        # Header
        header = ttk.Frame(page, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="⚙️ Settings & About", style='Header.TLabel').pack(anchor=tk.W)
        
        # Settings notebook
        settings_notebook = ttk.Notebook(page)
        settings_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # General settings
        gen_frame = ttk.Frame(settings_notebook)
        settings_notebook.add(gen_frame, text="General")
        
        ttk.Label(gen_frame, text="Application Settings", font=('Segoe UI', 12, 'bold')).pack(anchor=tk.W, padx=20, pady=20)
        
        ttk.Checkbutton(gen_frame, text="Enable logging").pack(anchor=tk.W, padx=20, pady=5)
        ttk.Checkbutton(gen_frame, text="Auto-scan on startup").pack(anchor=tk.W, padx=20, pady=5)
        ttk.Checkbutton(gen_frame, text="Show notifications").pack(anchor=tk.W, padx=20, pady=5)
        
        # About
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
  ✓ Multi-format report export (CSV, JSON, XLSX, PDF)
  ✓ Advanced filtering and search
  ✓ Device details with hardware information
  ✓ Modern professional interface

TECHNOLOGY:
  • Python 3.7+
  • Tkinter (GUI)
  • Windows Management Instrumentation (WMI)
  • Registry & Event Log parsing
  • Multi-threaded analysis

This tool provides Wireshark-level detail for USB device analysis
on Windows systems, including forensic investigation capabilities.

═════════════════════════════════════════════════════════
"""
        
        about_display = scrolledtext.ScrolledText(
            about_frame, wrap=tk.WORD, font=('Courier New', 10),
            bg='#f9fafb', fg='#1f2937', height=20
        )
        about_display.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        about_display.insert('1.0', about_text)
        about_display.config(state=tk.DISABLED)


if __name__ == '__main__':
    app = USBForensicsApp()
    app.mainloop()
