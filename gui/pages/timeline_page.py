import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import logging
from datetime import datetime, timezone
import os

from core.registry_parser import parse_registry
from core.eventlog_parser import parse_event_logs
from core.correlation import correlate
from core.analysis import summarize
from core.usb_trace_analysis import analyze_usb_trace, match_trace_report
from core.wireshark_bridge import WiresharkBridge
from utils.settings import load_settings

logger = logging.getLogger(__name__)
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TimelinePage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style='Main.TFrame')
        self.app = app
        self.settings = load_settings()
        self.bridge = WiresharkBridge(WORKSPACE_ROOT)
        self._create_page()

    @staticmethod
    def _parse_timestamp(value):
        if not value:
            return None

        text = str(value).strip()
        if not text:
            return None

        normalized = text.replace('Z', '+00:00')
        try:
            dt = datetime.fromisoformat(normalized)
        except ValueError:
            for pattern in (
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%d %H:%M:%S',
                '%b %d, %Y %H:%M:%S.%f',
                '%b %d, %Y %H:%M:%S',
            ):
                try:
                    dt = datetime.strptime(text, pattern)
                    break
                except ValueError:
                    dt = None
            if dt is None:
                return None

        if dt.tzinfo is not None:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt

    @classmethod
    def _timestamp_key(cls, value):
        parsed = cls._parse_timestamp(value)
        if parsed is not None:
            return (0, parsed)
        return (1, str(value or ''))

    @classmethod
    def _resolve_first_seen(cls, summary, trace_report):
        candidates = []
        trace_first_seen = (trace_report or {}).get('first_seen')
        if trace_first_seen:
            candidates.append(('Wireshark Trace', trace_first_seen))

        record_first_seen = summary.get('first_seen')
        if record_first_seen:
            candidates.append(('Registry/Event Logs', record_first_seen))

        if not candidates:
            return 'Unknown', 'Unknown'

        source, value = min(candidates, key=lambda item: cls._timestamp_key(item[1]))
        return value, source

    def _create_page(self):
        # Header
        header = ttk.Frame(self, style='Main.TFrame')
        header.pack(fill=tk.X, padx=20, pady=20)
        ttk.Label(header, text="📊 Timeline Analysis", style='Header.TLabel').pack(anchor=tk.W)
        
        # Control panel
        ctrl_frame = ttk.Frame(self, style='Main.TFrame')
        ctrl_frame.pack(fill=tk.X, padx=20, pady=10)
        
        btn_refresh = tk.Button(
            ctrl_frame, text="🔄 Generate Timeline", command=self._generate_timeline,
            bg='#3b82f6', fg='white', font=('Segoe UI', 10), padx=15, pady=8, relief=tk.FLAT, cursor='hand2'
        )
        btn_refresh.pack(side=tk.LEFT, padx=5)
        
        # Timeline text
        text_frame = ttk.Frame(self, style='Main.TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.timeline_text = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD, font=('Courier New', 9),
            bg='#f9fafb', fg='#1f2937'
        )
        self.timeline_text.pack(fill=tk.BOTH, expand=True)
    
    def _generate_timeline(self):
        def timeline_thread():
            try:
                self.timeline_text.delete('1.0', tk.END)
                self.timeline_text.insert(tk.END, "Generating timeline...\n\n")
                self.timeline_text.update()
                
                regs = parse_registry()
                evs = parse_event_logs()
                devices = correlate(regs, evs)
                summaries = summarize(devices)

                trace_reports_by_device = {}
                if bool(self.settings.get('wireshark_enabled', False)):
                    capture_file = (self.settings.get('wireshark_capture_file', '') or '').strip()
                    if capture_file:
                        try:
                            packets, _ = self.bridge.load_capture(
                                capture_file=capture_file,
                                tshark_override=self.settings.get('wireshark_tshark_path') or None,
                            )
                            trace_result = analyze_usb_trace(packets)
                            for device in summaries:
                                matched_report = match_trace_report(device, trace_result)
                                if matched_report:
                                    trace_reports_by_device[device.get('device_id')] = matched_report
                        except Exception as trace_exc:
                            logger.warning(f"Timeline Wireshark correlation skipped: {trace_exc}")
                
                timeline_rows = []
                for device in summaries:
                    trace_report = trace_reports_by_device.get(device.get('device_id'), {})
                    first_seen, first_source = self._resolve_first_seen(device, trace_report)
                    timeline_rows.append({
                        'device': device,
                        'first_seen': first_seen,
                        'first_source': first_source,
                    })

                sorted_rows = sorted(timeline_rows, key=lambda row: self._timestamp_key(row.get('first_seen')))
                
                self.timeline_text.delete('1.0', tk.END)
                self.timeline_text.insert(tk.END, "USB DEVICE ACTIVITY TIMELINE\n")
                self.timeline_text.insert(tk.END, "="*70 + "\n\n")
                
                for row in sorted_rows:
                    device = row['device']
                    first = row['first_seen']
                    first_source = row['first_source']
                    last = device.get('last_seen', 'Unknown')
                    name = device.get('name', 'Unknown')
                    serial = device.get('serial', 'Unknown')
                    count = device.get('connections', 0)
                    
                    self.timeline_text.insert(tk.END, f"\n{name} ({serial})\n")
                    self.timeline_text.insert(tk.END, f"  First Seen: {first}\n")
                    self.timeline_text.insert(tk.END, f"  First Seen Source: {first_source}\n")
                    self.timeline_text.insert(tk.END, f"  Last Seen:  {last}\n")
                    self.timeline_text.insert(tk.END, f"  Connections:  {count}\n")
                
                logger.info("Timeline generated")
                
            except Exception as e:
                logger.error(f"Timeline generation error: {e}")
                self.timeline_text.insert(tk.END, f"Error: {e}")
        
        thread = threading.Thread(target=timeline_thread, daemon=True)
        thread.start()
