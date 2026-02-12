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
import time
import os
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

# URB capture imports (may fail if dependencies not installed)
try:
    from urb_capture import URBCapture, URBTransfer, parse_etl_file
    URB_CAPTURE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"URB capture not available: {e}")
    URB_CAPTURE_AVAILABLE = False

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
        self._create_urb_capture_page()
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
            ('urb', '🔌 URB Capture', self._on_nav_urb),
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
    
    def _on_nav_urb(self):
        self.show_page('urb')
    
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
        
        self.btn_refresh = tk.Button(
            ctrl_frame, text="🔄 Scan Devices", command=self._scan_all_devices,
            bg='#3b82f6', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        self.btn_refresh.pack(side=tk.LEFT, padx=5)
        
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
        
        # Highlight portable devices (phones/tablets over MTP/WPD)
        self.device_tree.tag_configure('portable', background='#fef3c7', foreground='#92400e')
        
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
        if getattr(self, 'scanning', False):
            return
        # mark scanning and disable refresh button to prevent concurrent scans
        self.scanning = True
        try:
            self.btn_refresh.config(state='disabled')
        except Exception:
            pass
        def scan_thread():
            try:
                self.device_tree.delete(*self.device_tree.get_children())
                devices = get_all_usb_devices()
                # Strong dedupe at UI level (use same heuristics as device manager)
                import re
                def ui_key(d):
                    try:
                        vid = (d.vid or "").strip().lower()
                        pid = (d.pid or "").strip().lower()
                        serial = (d.serial or "").strip().lower()
                        if serial:
                            manu = (d.manufacturer or "").strip().lower()
                            return f"serial:{serial}:{manu}"
                        if getattr(d, 'hardware_ids', None):
                            hids = ",".join(sorted(h.strip().lower() for h in d.hardware_ids if h))
                            if hids:
                                return f"hid:{vid}:{pid}:{hids}"
                        devid = (d.device_id or "").strip().lower()
                        if devid:
                            m = re.search(r"(vid_[0-9a-f]{4}[^\\]*pid_[0-9a-f]{4})", devid)
                            if m:
                                base = m.group(1)
                                parts = devid.split('\\')
                                if len(parts) >= 3:
                                    tail = parts[-1]
                                    tail_clean = tail.split('&')[0] if '&' in tail else tail
                                    tail_clean = tail_clean.strip()
                                    if tail_clean:
                                        return f"dev:{base}:{tail_clean}"
                                return f"dev:{base}"
                        return "|".join([
                            (d.name or "").strip().lower(),
                            (d.manufacturer or "").strip().lower(),
                            (d.device_type or "").strip().lower(),
                        ])
                    except Exception:
                        return (d.device_id or "").strip().lower() or f"{d.name}:{d.manufacturer}:{d.device_type}"

                seen_keys = set()
                deduped = []
                for d in devices:
                    key = ui_key(d)
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)
                    deduped.append(d)

                self.current_devices = deduped
                seen_rows = set()
                
                for i, device in enumerate(deduped, 1):
                    status = "Connected" if device.connection_status == "Connected" else "Disconnected"
                    
                    # Format serial number display
                    # Empty string = not available, show "N/A" for hubs/some devices, "Unknown" if we should have found it
                    if device.serial:
                        serial_display = device.serial
                    elif device.device_type in ('hub', 'unknown'):
                        serial_display = "N/A"  # Hubs and unknown devices typically don't have serials
                    else:
                        serial_display = "Unknown"  # For devices that should have serials but we couldn't find them
                    
                    row_values = (
                        device.device_type or 'Unknown',
                        device.manufacturer or 'Unknown',
                        device.name or 'Unknown',
                        serial_display,
                        status
                    )
                    row_key = tuple(str(v).strip().lower() for v in row_values)
                    if row_key in seen_rows:
                        continue
                    seen_rows.add(row_key)
                    
                    self.device_tree.insert(
                        '', 'end', text=str(i),
                        values=row_values,
                        tags=('portable',) if device.device_type == 'portable' else ()
                    )
                
                logger.info(f"Scanned {len(devices)} USB devices")
                
            except Exception as e:
                logger.error(f"Error scanning devices: {e}")
                messagebox.showerror("Error", f"Failed to scan devices: {e}")
            finally:
                # allow subsequent scans
                self.scanning = False
                try:
                    self.btn_refresh.config(state='normal')
                except Exception:
                    pass

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
Serial Number:      {device.serial if device.serial else ('N/A' if device.device_type in ('hub', 'unknown') else 'Unknown')}
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
    
    def _create_urb_capture_page(self):
        """Create URB capture page."""
        page = ttk.Frame(self.content_area, style='Main.TFrame')
        self.pages['urb'] = page
        
        # Header
        header = ttk.Frame(page, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="🔌 USB Request Block (URB) Capture", style='Header.TLabel').pack(anchor=tk.W)
        
        # Check availability
        if not URB_CAPTURE_AVAILABLE:
            info_frame = ttk.Frame(page, style='Main.TFrame')
            info_frame.pack(fill=tk.X, padx=20, pady=10)
            ttk.Label(
                info_frame, 
                text="⚠️ URB capture requires: pip install etl-parser\nAdministrator privileges required.",
                foreground='#ef4444',
                font=('Segoe UI', 10)
            ).pack()
            return
        
        # Control panel - Capture
        ctrl_frame = ttk.Frame(page, style='Main.TFrame')
        ctrl_frame.pack(fill=tk.X, padx=20, pady=10)
        
        capture_frame = ttk.LabelFrame(ctrl_frame, text="ETW Capture (Requires Admin Privileges)", padding=10)
        capture_frame.pack(fill=tk.X, pady=5)
        
        admin_warning = ttk.Label(
            capture_frame, 
            text="⚠️ Creating new .etl files requires administrator privileges.",
            font=('Segoe UI', 8),
            foreground='#dc2626'
        )
        admin_warning.pack(anchor=tk.W, pady=(0, 5))
        
        duration_frame = ttk.Frame(capture_frame)
        duration_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(duration_frame, text="Duration (seconds):", font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 10))
        self.urb_duration_var = tk.StringVar(value="60")
        duration_entry = ttk.Entry(duration_frame, textvariable=self.urb_duration_var, width=10)
        duration_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(duration_frame, text="(0 = manual stop)", font=('Segoe UI', 8), foreground='#6b7280').pack(side=tk.LEFT)
        
        btn_frame = ttk.Frame(capture_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.urb_start_btn = tk.Button(
            btn_frame, text="▶️ Start Capture", command=self._start_urb_capture,
            bg='#10b981', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        self.urb_start_btn.pack(side=tk.LEFT, padx=5)
        
        self.urb_stop_btn = tk.Button(
            btn_frame, text="⏹️ Stop Capture", command=self._stop_urb_capture,
            bg='#ef4444', fg='white', font=('Segoe UI', 10), padx=15, pady=8, 
            relief=tk.FLAT, cursor='hand2', state=tk.DISABLED
        )
        self.urb_stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.urb_status_label = ttk.Label(
            capture_frame, text="Status: Ready", font=('Segoe UI', 9)
        )
        self.urb_status_label.pack(anchor=tk.W, pady=5)
        
        # Control panel - Parse ETL
        parse_frame = ttk.LabelFrame(ctrl_frame, text="Parse Existing ETL File (No Admin Required)", padding=10)
        parse_frame.pack(fill=tk.X, pady=5)
        
        info_label = ttk.Label(
            parse_frame, 
            text="ℹ️ You can parse existing .etl files without administrator privileges.",
            font=('Segoe UI', 8),
            foreground='#059669'
        )
        info_label.pack(anchor=tk.W, pady=(0, 5))
        
        parse_btn_frame = ttk.Frame(parse_frame)
        parse_btn_frame.pack(fill=tk.X, pady=5)
        
        btn_browse = tk.Button(
            parse_btn_frame, text="📂 Browse ETL File", command=self._browse_etl_file,
            bg='#3b82f6', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        btn_browse.pack(side=tk.LEFT, padx=5)
        
        btn_parse = tk.Button(
            parse_btn_frame, text="🔍 Parse ETL", command=self._parse_etl_file,
            bg='#8b5cf6', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        btn_parse.pack(side=tk.LEFT, padx=5)
        
        self.urb_etl_path_label = ttk.Label(
            parse_frame, text="No file selected", font=('Segoe UI', 9), foreground='#6b7280'
        )
        self.urb_etl_path_label.pack(anchor=tk.W, pady=5)
        
        # Real-time capture option
        realtime_frame = ttk.LabelFrame(ctrl_frame, text="Real-time Capture", padding=10)
        realtime_frame.pack(fill=tk.X, pady=5)
        
        self.urb_realtime_btn = tk.Button(
            realtime_frame, text="🔄 Start Real-time", command=self._start_realtime_urb,
            bg='#f59e0b', fg='white', font=('Segoe UI', 10), padx=15, pady=8, 
            relief=tk.FLAT, cursor='hand2'
        )
        self.urb_realtime_btn.pack(side=tk.LEFT, padx=5)
        
        self.urb_realtime_stop_btn = tk.Button(
            realtime_frame, text="⏹️ Stop Real-time", command=self._stop_realtime_urb,
            bg='#ef4444', fg='white', font=('Segoe UI', 10), padx=15, pady=8, 
            relief=tk.FLAT, cursor='hand2', state=tk.DISABLED
        )
        self.urb_realtime_stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Results display
        results_frame = ttk.Frame(page, style='Main.TFrame')
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # URB list with treeview
        list_frame = ttk.LabelFrame(results_frame, text="Captured URBs", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for URBs
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.urb_tree = ttk.Treeview(
            tree_frame,
            columns=('timestamp', 'function', 'device', 'endpoint', 'length', 'status'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.urb_tree.yview)
        
        # Configure columns
        self.urb_tree.heading('timestamp', text='Timestamp')
        self.urb_tree.heading('function', text='Function')
        self.urb_tree.heading('device', text='Device (VID:PID)')
        self.urb_tree.heading('endpoint', text='Endpoint')
        self.urb_tree.heading('length', text='Length')
        self.urb_tree.heading('status', text='Status')
        
        self.urb_tree.column('timestamp', width=150)
        self.urb_tree.column('function', width=250)
        self.urb_tree.column('device', width=120)
        self.urb_tree.column('endpoint', width=100)
        self.urb_tree.column('length', width=80)
        self.urb_tree.column('status', width=150)
        
        self.urb_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click to show details
        self.urb_tree.bind('<Double-1>', self._show_urb_details)
        
        # Details text area
        details_frame = ttk.LabelFrame(results_frame, text="URB Details", padding=5)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.urb_details_text = scrolledtext.ScrolledText(
            details_frame, wrap=tk.WORD, font=('Courier New', 9),
            bg='#f9fafb', fg='#1f2937', height=10
        )
        self.urb_details_text.pack(fill=tk.BOTH, expand=True)
        
        # Initialize URB capture instance
        self.urb_capture = None
        self.urb_realtime_capture = None
        self.captured_urbs = []
        self.current_etl_file = None
    
    def _start_urb_capture(self):
        """Start ETW capture to create .etl file."""
        if not URB_CAPTURE_AVAILABLE:
            messagebox.showerror("Error", "URB capture not available. Install etl-parser.")
            return
        
        try:
            duration = int(self.urb_duration_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid duration. Please enter a number.")
            return
        
        def capture_thread():
            try:
                self.urb_capture = URBCapture()
                
                if not self.urb_capture.is_available():
                    messagebox.showerror(
                        "Error", 
                        "URB capture requires:\n"
                        "- Administrator privileges\n"
                        "- Windows system"
                    )
                    return
                
                self.urb_start_btn.config(state=tk.DISABLED)
                self.urb_stop_btn.config(state=tk.NORMAL)
                self.urb_status_label.config(text=f"Status: Capturing... (Duration: {duration}s)")
                
                # Start capture
                trace_file = self.urb_capture.start_etw_capture(duration_seconds=duration)
                
                if trace_file:
                    self.current_etl_file = trace_file
                    self.urb_status_label.config(text=f"Status: Capturing to {trace_file}")
                    
                    if duration == 0:
                        # Manual stop mode
                        self.urb_status_label.config(text="Status: Capturing... (Click Stop to finish)")
                    else:
                        # Wait for duration
                        time.sleep(duration)
                        self._stop_urb_capture_internal()
                else:
                    messagebox.showerror("Error", "Failed to start ETW capture")
                    self.urb_start_btn.config(state=tk.NORMAL)
                    self.urb_stop_btn.config(state=tk.DISABLED)
                    self.urb_status_label.config(text="Status: Error starting capture")
                    
            except Exception as e:
                logger.error(f"Error starting URB capture: {e}", exc_info=True)
                messagebox.showerror("Error", f"Failed to start capture: {e}")
                self.urb_start_btn.config(state=tk.NORMAL)
                self.urb_stop_btn.config(state=tk.DISABLED)
                self.urb_status_label.config(text="Status: Error")
        
        threading.Thread(target=capture_thread, daemon=True).start()
    
    def _stop_urb_capture(self):
        """Stop ETW capture."""
        self._stop_urb_capture_internal()
    
    def _stop_urb_capture_internal(self):
        """Internal method to stop capture."""
        try:
            if self.urb_capture:
                self.urb_capture.stop_etw_capture()
                
                if self.current_etl_file and os.path.exists(self.current_etl_file):
                    self.urb_status_label.config(
                        text=f"Status: Capture complete. File: {self.current_etl_file}"
                    )
                    self.urb_etl_path_label.config(text=f"Last capture: {self.current_etl_file}")
                    # Auto-parse the captured file
                    self._parse_etl_file_internal(self.current_etl_file)
                else:
                    self.urb_status_label.config(text="Status: Capture stopped")
            else:
                self.urb_status_label.config(text="Status: No active capture")
                
            self.urb_start_btn.config(state=tk.NORMAL)
            self.urb_stop_btn.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Error stopping URB capture: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to stop capture: {e}")
    
    def _browse_etl_file(self):
        """Browse for ETL file to parse."""
        filename = filedialog.askopenfilename(
            title="Select ETL File",
            filetypes=[("ETL files", "*.etl"), ("All files", "*.*")]
        )
        if filename:
            self.current_etl_file = filename
            self.urb_etl_path_label.config(text=f"Selected: {os.path.basename(filename)}")
    
    def _parse_etl_file(self):
        """Parse selected ETL file."""
        if not self.current_etl_file:
            messagebox.showwarning("No File", "Please select an ETL file first")
            return
        
        if not os.path.exists(self.current_etl_file):
            messagebox.showerror("Error", "ETL file not found")
            return
        
        self._parse_etl_file_internal(self.current_etl_file)
    
    def _parse_etl_file_internal(self, etl_file: str):
        """Internal method to parse ETL file."""
        def parse_thread():
            try:
                self.after(0, lambda: self.urb_status_label.config(text="Status: Parsing ETL file..."))
                
                # Parsing doesn't require admin privileges - only creating .etl files does
                # Create a URBCapture instance just for parsing (no admin check needed)
                capture = URBCapture()
                urbs = capture.parse_etl_file(etl_file)
                
                # Update UI with parsed URBs
                self.after(0, self._update_urb_list, urbs)
                
                if urbs:
                    self.after(0, lambda: self.urb_status_label.config(text=f"Status: Successfully parsed {len(urbs)} URBs"))
                else:
                    self.after(0, lambda: self.urb_status_label.config(text="Status: No URBs found in file (may need etl-parser library)"))
                    self.after(0, lambda: messagebox.showinfo(
                        "Parse Complete", 
                        "Parsed the ETL file but found 0 URBs.\n\n"
                        "This could mean:\n"
                        "- The file doesn't contain USB events\n"
                        "- etl-parser library may need to be installed: pip install etl-parser\n"
                        "- The ETW trace was not captured with USB providers"
                    ))
                
            except ImportError as e:
                logger.error(f"Missing dependency for parsing: {e}", exc_info=True)
                self.after(0, lambda: messagebox.showerror(
                    "Missing Dependency", 
                    f"Failed to parse ETL file: {e}\n\n"
                    "Please install the required library:\n"
                    "  pip install etl-parser"
                ))
                self.after(0, lambda: self.urb_status_label.config(text="Status: Parse error - missing etl-parser"))
            except Exception as e:
                logger.error(f"Error parsing ETL file: {e}", exc_info=True)
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to parse ETL file:\n{str(e)}"))
                self.after(0, lambda: self.urb_status_label.config(text="Status: Parse error"))
        
        threading.Thread(target=parse_thread, daemon=True).start()
    
    def _update_urb_list(self, urbs: list):
        """Update the URB treeview with parsed URBs."""
        # Clear existing items
        for item in self.urb_tree.get_children():
            self.urb_tree.delete(item)
        
        self.captured_urbs = urbs
        
        # Add URBs to treeview
        for urb in urbs:
            timestamp = urb.timestamp.split('T')[0] if 'T' in urb.timestamp else urb.timestamp[:10]
            device_str = f"{urb.vid}:{urb.pid}" if urb.vid and urb.pid else "Unknown"
            endpoint_str = f"{urb.endpoint_address:02X} ({urb.endpoint_direction})"
            length_str = f"{urb.transfer_buffer_length} bytes"
            
            item_id = self.urb_tree.insert(
                '', tk.END,
                values=(
                    timestamp,
                    urb.urb_function_name,
                    device_str,
                    endpoint_str,
                    length_str,
                    urb.status_name
                )
            )
            # Store URB object in item (using tags or keep reference by index)
        
        logger.info(f"Updated URB list with {len(urbs)} URBs")
    
    def _show_urb_details(self, event):
        """Show detailed URB information."""
        selection = self.urb_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = self.urb_tree.index(item)
        
        if 0 <= index < len(self.captured_urbs):
            urb = self.captured_urbs[index]
            
            # Format detailed information
            details = f"""
URB DETAILS
{'='*70}

Timestamp:        {urb.timestamp}
Function:         {urb.urb_function_name} (0x{urb.urb_function:04X})
Status:           {urb.status_name} (0x{urb.status:08X})
Device ID:        {urb.device_id}
VID:PID:          {urb.vid}:{urb.pid}
Endpoint:         {urb.endpoint_address:02X} ({urb.endpoint_direction})
Transfer Length:  {urb.transfer_buffer_length} bytes
Actual Length:    {urb.actual_length} bytes
Interval:         {urb.interval}
Start Frame:      {urb.start_frame}
Packets:          {urb.number_of_packets}
Error Count:      {urb.error_count}
Timeout:          {urb.timeout} ms
Process ID:       {urb.process_id}
Thread ID:        {urb.thread_id}

"""
            if urb.setup_packet:
                details += f"""
SETUP PACKET (Control Transfer)
{'='*70}
Request Type:     0x{urb.request_type:02X}
Request:          0x{urb.request:02X}
Value:            0x{urb.value:04X}
Index:            0x{urb.index:04X}
Length:           0x{urb.length:04X}
"""
            
            if urb.transfer_buffer:
                buffer_hex = urb.transfer_buffer.hex()[:512]  # Limit display
                details += f"""
TRANSFER BUFFER (first 256 bytes)
{'='*70}
{bytes(urb.transfer_buffer[:256]).hex(' ', 1)}
"""
            
            self.urb_details_text.delete('1.0', tk.END)
            self.urb_details_text.insert('1.0', details)
    
    def _start_realtime_urb(self):
        """Start real-time URB capture."""
        if not URB_CAPTURE_AVAILABLE:
            messagebox.showerror("Error", "URB capture not available")
            return
        
        def on_urb_captured(urb: URBTransfer):
            """Callback for real-time URB capture."""
            self.after(0, self._add_realtime_urb, urb)
        
        try:
            self.urb_realtime_capture = URBCapture()
            
            if not self.urb_realtime_capture.is_available():
                messagebox.showerror("Error", "Real-time capture requires administrator privileges")
                return
            
            if self.urb_realtime_capture.start_realtime_capture(on_urb_captured):
                self.urb_realtime_btn.config(state=tk.DISABLED)
                self.urb_realtime_stop_btn.config(state=tk.NORMAL)
                self.urb_status_label.config(text="Status: Real-time capture active")
            else:
                messagebox.showerror("Error", "Failed to start real-time capture")
                
        except Exception as e:
            logger.error(f"Error starting real-time capture: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to start real-time capture: {e}")
    
    def _stop_realtime_urb(self):
        """Stop real-time URB capture."""
        try:
            if self.urb_realtime_capture:
                self.urb_realtime_capture.stop_realtime_capture()
                self.urb_realtime_btn.config(state=tk.NORMAL)
                self.urb_realtime_stop_btn.config(state=tk.DISABLED)
                self.urb_status_label.config(text="Status: Real-time capture stopped")
        except Exception as e:
            logger.error(f"Error stopping real-time capture: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to stop real-time capture: {e}")
    
    def _add_realtime_urb(self, urb: URBTransfer):
        """Add URB from real-time capture to the list."""
        self.captured_urbs.append(urb)
        
        # Add to treeview
        timestamp = urb.timestamp.split('T')[0] if 'T' in urb.timestamp else urb.timestamp[:10]
        device_str = f"{urb.vid}:{urb.pid}" if urb.vid and urb.pid else "Unknown"
        endpoint_str = f"{urb.endpoint_address:02X} ({urb.endpoint_direction})"
        length_str = f"{urb.transfer_buffer_length} bytes"
        
        self.urb_tree.insert(
            '', tk.END,
            values=(
                timestamp,
                urb.urb_function_name,
                device_str,
                endpoint_str,
                length_str,
                urb.status_name
            )
        )
    
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
