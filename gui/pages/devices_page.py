import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import logging

from core.usb_device_manager import get_all_usb_devices

logger = logging.getLogger(__name__)

class DevicesPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style='Main.TFrame')
        self.app = app
        self.current_devices = []
        self.scanning = False
        self._create_page()
        self._scan_all_devices()

    def _create_page(self):
        # Header
        header = ttk.Frame(self, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(header, text="🔍 All Connected USB Devices", style='Header.TLabel').pack(anchor=tk.W)
        
        # Control panel
        ctrl_frame = ttk.Frame(self, style='Main.TFrame')
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
        search_frame = ttk.Frame(self, style='Main.TFrame')
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(search_frame, text="Search:", style='Title.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        self.device_search = ttk.Entry(search_frame, font=('Segoe UI', 9), width=40)
        self.device_search.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.device_search.bind('<KeyRelease>', lambda e: self._filter_devices())
        
        # Device tree
        tree_frame = ttk.Frame(self, style='Main.TFrame')
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
        detail_frame = ttk.LabelFrame(self, text="📋 Device Details", style='Title.TLabel')
        detail_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.device_details = scrolledtext.ScrolledText(
            detail_frame, height=8, width=80, wrap=tk.WORD,
            font=('Courier New', 9), bg='#f9fafb', fg='#1f2937'
        )
        self.device_details.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _scan_all_devices(self):
        if getattr(self, 'scanning', False):
            return
        self.scanning = True
        try:
            self.btn_refresh.config(state='disabled')
        except Exception:
            pass

        def scan_thread():
            deduped = []
            error_message = ""
            try:
                devices = get_all_usb_devices()
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
                for d in devices:
                    key = ui_key(d)
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)
                    deduped.append(d)

                logger.info(f"Scanned {len(devices)} USB devices")
            except Exception as e:
                logger.error(f"Error scanning devices: {e}")
                error_message = str(e)
            finally:

                def apply_results():
                    try:
                        self.device_tree.delete(*self.device_tree.get_children())
                        self.current_devices = deduped

                        seen_rows = set()
                        for i, device in enumerate(deduped, 1):
                            status = "Connected" if device.connection_status == "Connected" else "Disconnected"

                            if device.serial:
                                serial_display = device.serial
                            elif device.device_type in ('hub', 'unknown'):
                                serial_display = "N/A"
                            else:
                                serial_display = "Unknown"

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

                        if error_message:
                            messagebox.showerror("Error", f"Failed to scan devices: {error_message}")
                    finally:
                        self.scanning = False
                        try:
                            self.btn_refresh.config(state='normal')
                        except Exception:
                            pass

                self.after(0, apply_results)

        thread = threading.Thread(target=scan_thread, daemon=True)
        thread.start()
    
    def _filter_devices(self):
        search_term = self.device_search.get().lower()
        
        for item in self.device_tree.get_children():
            values = self.device_tree.item(item)['values']
            text_repr = ' '.join(str(v).lower() for v in values)
            
            if search_term in text_repr or search_term == '':
                self.device_tree.item(item, tags=())
            else:
                self.device_tree.item(item, tags=('hidden',))
    
    def _on_device_double_click(self, event):
        selection = self.device_tree.selection()
        if selection:
            self._show_device_details()
    
    def _show_device_details(self):
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
        selection = self.device_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a device first")
            return
        
        info = self.device_details.get('1.0', tk.END)
        self.app.clipboard_clear()
        self.app.clipboard_append(info)
        messagebox.showinfo("Copied", "Device information copied to clipboard!")
