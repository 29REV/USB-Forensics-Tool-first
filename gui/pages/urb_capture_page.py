import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import logging
import os
import time

try:
    from core.urb_capture import URBCapture, URBTransfer, parse_etl_file
    URB_CAPTURE_AVAILABLE = True
except ImportError as e:
    URB_CAPTURE_AVAILABLE = False

logger = logging.getLogger(__name__)

class URBCapturePage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style='Main.TFrame')
        self.app = app
        
        self.urb_capture = None
        self.urb_realtime_capture = None
        self.captured_urbs = []
        self.current_etl_file = None
        
        self._create_page()

    def _ui_call(self, callback):
        """Run UI callback on Tk main thread."""
        self.after(0, callback)

    def _ui_showerror(self, title: str, message: str):
        self._ui_call(lambda: messagebox.showerror(title, message))

    def _ui_showinfo(self, title: str, message: str):
        self._ui_call(lambda: messagebox.showinfo(title, message))

    def _create_page(self):
        # Header
        header = ttk.Frame(self, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="🔌 USB Request Block (URB) Capture", style='Header.TLabel').pack(anchor=tk.W)
        
        # Check availability
        if not URB_CAPTURE_AVAILABLE:
            info_frame = ttk.Frame(self, style='Main.TFrame')
            info_frame.pack(fill=tk.X, padx=20, pady=10)
            ttk.Label(
                info_frame, 
                text="⚠️ URB capture requires: pip install etl-parser\nAdministrator privileges required.",
                foreground='#ef4444',
                font=('Segoe UI', 10)
            ).pack()
            return

        # Control panel - Capture
        ctrl_frame = ttk.Frame(self, style='Main.TFrame')
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
        results_frame = ttk.Frame(self, style='Main.TFrame')
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
    
    def _start_urb_capture(self):
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
                    self._ui_showerror(
                        "Error",
                        "URB capture requires:\n"
                        "- Administrator privileges\n"
                        "- Windows system"
                    )
                    return
                
                self._ui_call(lambda: self.urb_start_btn.config(state=tk.DISABLED))
                self._ui_call(lambda: self.urb_stop_btn.config(state=tk.NORMAL))
                self._ui_call(lambda: self.urb_status_label.config(text=f"Status: Capturing... (Duration: {duration}s)"))
                
                # Start capture
                trace_file = self.urb_capture.start_etw_capture(duration_seconds=duration)
                
                if trace_file:
                    self.current_etl_file = trace_file
                    self._ui_call(lambda: self.urb_status_label.config(text=f"Status: Capturing to {trace_file}"))
                    
                    if duration == 0:
                        self._ui_call(lambda: self.urb_status_label.config(text="Status: Capturing... (Click Stop to finish)"))
                    else:
                        time.sleep(duration)
                        self._ui_call(self._stop_urb_capture_internal)
                else:
                    self._ui_showerror("Error", "Failed to start ETW capture")
                    self._ui_call(lambda: self.urb_start_btn.config(state=tk.NORMAL))
                    self._ui_call(lambda: self.urb_stop_btn.config(state=tk.DISABLED))
                    self._ui_call(lambda: self.urb_status_label.config(text="Status: Error starting capture"))
                    
            except Exception as e:
                logger.error(f"Error starting URB capture: {e}", exc_info=True)
                self._ui_showerror("Error", f"Failed to start capture: {e}")
                self._ui_call(lambda: self.urb_start_btn.config(state=tk.NORMAL))
                self._ui_call(lambda: self.urb_stop_btn.config(state=tk.DISABLED))
                self._ui_call(lambda: self.urb_status_label.config(text="Status: Error"))
        
        threading.Thread(target=capture_thread, daemon=True).start()
    
    def _stop_urb_capture(self):
        self._stop_urb_capture_internal()
    
    def _stop_urb_capture_internal(self):
        try:
            if self.urb_capture:
                self.urb_capture.stop_etw_capture()
                
                if self.current_etl_file and os.path.exists(self.current_etl_file):
                    self.urb_status_label.config(
                        text=f"Status: Capture complete. File: {self.current_etl_file}"
                    )
                    self.urb_etl_path_label.config(text=f"Last capture: {self.current_etl_file}")
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
        filename = filedialog.askopenfilename(
            title="Select ETL File",
            filetypes=[("ETL files", "*.etl"), ("All files", "*.*")]
        )
        if filename:
            self.current_etl_file = filename
            self.urb_etl_path_label.config(text=f"Selected: {os.path.basename(filename)}")
    
    def _parse_etl_file(self):
        if not self.current_etl_file:
            messagebox.showwarning("No File", "Please select an ETL file first")
            return
        
        if not os.path.exists(self.current_etl_file):
            messagebox.showerror("Error", "ETL file not found")
            return
        
        self._parse_etl_file_internal(self.current_etl_file)
    
    def _parse_etl_file_internal(self, etl_file: str):
        def parse_thread():
            try:
                self.after(0, lambda: self.urb_status_label.config(text="Status: Parsing ETL file..."))
                
                capture = URBCapture()
                urbs = capture.parse_etl_file(etl_file)
                
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
                self._ui_showerror(
                    "Missing Dependency",
                    f"Failed to parse ETL file: {e}\n\n"
                    "Please install the required library:\n"
                    "  pip install etl-parser"
                )
                self.after(0, lambda: self.urb_status_label.config(text="Status: Parse error - missing etl-parser"))
            except Exception as e:
                logger.error(f"Error parsing ETL file: {e}", exc_info=True)
                self._ui_showerror("Error", f"Failed to parse ETL file:\n{str(e)}")
                self.after(0, lambda: self.urb_status_label.config(text="Status: Parse error"))
        
        threading.Thread(target=parse_thread, daemon=True).start()
    
    def _update_urb_list(self, urbs: list):
        for item in self.urb_tree.get_children():
            self.urb_tree.delete(item)
        
        self.captured_urbs = urbs
        
        for urb in urbs:
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
        
        logger.info(f"Updated URB list with {len(urbs)} URBs")
    
    def _show_urb_details(self, event):
        selection = self.urb_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        index = self.urb_tree.index(item)
        
        if 0 <= index < len(self.captured_urbs):
            urb = self.captured_urbs[index]
            
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
                buffer_hex = urb.transfer_buffer.hex()[:512] 
                details += f"""
TRANSFER BUFFER (first 256 bytes)
{'='*70}
{bytes(urb.transfer_buffer[:256]).hex(' ', 1)}
"""
            
            self.urb_details_text.delete('1.0', tk.END)
            self.urb_details_text.insert('1.0', details)
    
    def _start_realtime_urb(self):
        if not URB_CAPTURE_AVAILABLE:
            messagebox.showerror("Error", "URB capture not available")
            return
        
        def on_urb_captured(urb):
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
        try:
            if self.urb_realtime_capture:
                self.urb_realtime_capture.stop_realtime_capture()
                self.urb_realtime_btn.config(state=tk.NORMAL)
                self.urb_realtime_stop_btn.config(state=tk.DISABLED)
                self.urb_status_label.config(text="Status: Real-time capture stopped")
        except Exception as e:
            logger.error(f"Error stopping real-time capture: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to stop real-time capture: {e}")
    
    def _add_realtime_urb(self, urb):
        self.captured_urbs.append(urb)
        
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
