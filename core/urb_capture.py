"""USB Request Block (URB) Capture and Parsing Module.

This module provides complete URB capture capabilities:
- Full URB parsing from .etl files
- Real-time event processing via ETW
- Complete URB data extraction with all fields

Requires:
    - Administrator privileges
    - Windows system
    - Optional: etl-parser library (pip install etl-parser) for .etl file parsing
    - Optional: pythonnet (pip install pythonnet) for advanced .NET ETW APIs
"""

import logging
import subprocess
import os
import sys
import platform
import ctypes
import struct
import threading
import queue
import time
import shutil
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timezone
from enum import IntEnum

try:
    import settings as app_settings
    SETTINGS_AVAILABLE = True
except ImportError:
    SETTINGS_AVAILABLE = False

logger = logging.getLogger(__name__)
DEBUG_LOG_PATH = "debug-c4e452.log"

# USB ETW providers used for capture/parsing.
DEFAULT_USB_PROVIDERS = [
    "Microsoft-Windows-USB-USBPORT",
    "Microsoft-Windows-USB-USBXHCI",
    "Microsoft-Windows-USB-UCX",
    "Microsoft-Windows-USB-USBHUB3",
    "Microsoft-Windows-USB-USBHUB",
]


def _coerce_int(value: Any, default: int = 0) -> int:
    """Convert ETW field values to int safely."""
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default
        try:
            if value.lower().startswith("0x"):
                return int(value, 16)
            return int(value)
        except Exception:
            return default
    return default


def _coerce_bytes(value: Any) -> bytes:
    """Convert event payload values to bytes safely."""
    if value is None:
        return b""
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, str):
        cleaned = value.replace(" ", "").replace("-", "")
        try:
            return bytes.fromhex(cleaned)
        except Exception:
            return value.encode("utf-8", errors="ignore")
    return b""


def _first_present(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """Return first available field by key from event data."""
    for key in keys:
        if key in data:
            return data[key]
    return default


# Check for administrator privileges
def _check_admin() -> bool:
    """Check if running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


# USB URB Function Codes (from Windows USB headers)
class URBFunction(IntEnum):
    """URB Function codes from usb.h"""
    URB_FUNCTION_SELECT_CONFIGURATION = 0x0000
    URB_FUNCTION_SELECT_INTERFACE = 0x0001
    URB_FUNCTION_ABORT_PIPE = 0x0002
    URB_FUNCTION_TAKE_FRAME_LENGTH_CONTROL = 0x0003
    URB_FUNCTION_RELEASE_FRAME_LENGTH_CONTROL = 0x0004
    URB_FUNCTION_GET_FRAME_LENGTH = 0x0005
    URB_FUNCTION_SET_FRAME_LENGTH = 0x0006
    URB_FUNCTION_GET_CURRENT_FRAME_NUMBER = 0x0007
    URB_FUNCTION_CONTROL_TRANSFER = 0x0008
    URB_FUNCTION_BULK_OR_INTERRUPT_TRANSFER = 0x0009
    URB_FUNCTION_ISOCH_TRANSFER = 0x000a
    URB_FUNCTION_GET_DESCRIPTOR_FROM_DEVICE = 0x000b
    URB_FUNCTION_SET_DESCRIPTOR_TO_DEVICE = 0x000c
    URB_FUNCTION_SET_FEATURE_TO_DEVICE = 0x000d
    URB_FUNCTION_SET_FEATURE_TO_INTERFACE = 0x000e
    URB_FUNCTION_SET_FEATURE_TO_ENDPOINT = 0x000f
    URB_FUNCTION_CLEAR_FEATURE_TO_DEVICE = 0x0010
    URB_FUNCTION_CLEAR_FEATURE_TO_INTERFACE = 0x0011
    URB_FUNCTION_CLEAR_FEATURE_TO_ENDPOINT = 0x0012
    URB_FUNCTION_GET_STATUS_FROM_DEVICE = 0x0013
    URB_FUNCTION_GET_STATUS_FROM_INTERFACE = 0x0014
    URB_FUNCTION_GET_STATUS_FROM_ENDPOINT = 0x0015
    URB_FUNCTION_RESERVED_0X0016 = 0x0016
    URB_FUNCTION_VENDOR_DEVICE = 0x0017
    URB_FUNCTION_VENDOR_INTERFACE = 0x0018
    URB_FUNCTION_VENDOR_ENDPOINT = 0x0019
    URB_FUNCTION_CLASS_DEVICE = 0x001a
    URB_FUNCTION_CLASS_INTERFACE = 0x001b
    URB_FUNCTION_CLASS_ENDPOINT = 0x001c
    URB_FUNCTION_RESERVE_0X001D = 0x001d
    URB_FUNCTION_SYNC_RESET_PIPE_AND_CLEAR_STALL = 0x001e
    URB_FUNCTION_CLASS_OTHER = 0x001f
    URB_FUNCTION_VENDOR_OTHER = 0x0020
    URB_FUNCTION_GET_STATUS_FROM_OTHER = 0x0021
    URB_FUNCTION_SET_FEATURE_TO_OTHER = 0x0022
    URB_FUNCTION_CLEAR_FEATURE_TO_OTHER = 0x0023
    URB_FUNCTION_GET_INTERFACE = 0x0024
    URB_FUNCTION_SET_INTERFACE = 0x0025
    URB_FUNCTION_GET_CONFIGURATION = 0x0026
    URB_FUNCTION_GET_DESCRIPTOR_FROM_ENDPOINT = 0x0027
    URB_FUNCTION_SET_DESCRIPTOR_TO_ENDPOINT = 0x0028
    URB_FUNCTION_SET_CONFIGURATION = 0x0029
    URB_FUNCTION_GET_DESCRIPTOR_FROM_INTERFACE = 0x002a
    URB_FUNCTION_SET_DESCRIPTOR_TO_INTERFACE = 0x002b
    URB_FUNCTION_GET_MS_FEATURE_DESCRIPTOR = 0x002c


# USB Transfer Status Codes
class URBStatus(IntEnum):
    """URB Status codes"""
    USBD_STATUS_SUCCESS = 0x00000000
    USBD_STATUS_PENDING = 0x40000000
    USBD_STATUS_ERROR = 0xC0000000
    USBD_STATUS_HALTED = 0xC0000001
    USBD_STATUS_INVALID_REQUEST = 0xC0000002
    USBD_STATUS_INVALID_PIPE_HANDLE = 0xC0000003
    USBD_STATUS_NO_BANDWIDTH = 0xC0000004
    USBD_STATUS_INTERNAL_HC_ERROR = 0xC0000005
    USBD_STATUS_ERROR_SHORT_TRANSFER = 0xC0000006
    USBD_STATUS_BAD_START_FRAME = 0xC0000007
    USBD_STATUS_ISOCH_REQUEST_FAILED = 0xC0000008
    USBD_STATUS_FRAME_CONTROL_OWNED = 0xC0000009
    USBD_STATUS_FRAME_CONTROL_NOT_OWNED = 0xC000000a
    USBD_STATUS_NOT_SUPPORTED = 0xC000000b
    USBD_STATUS_INAVLID_URB_FUNCTION = 0xC000000c
    USBD_STATUS_INVALID_PARAMETER = 0xC000000d
    USBD_STATUS_ERROR_BUSY = 0xC000000e


@dataclass
class URBTransfer:
    """Complete URB transfer information."""
    timestamp: str
    urb_function: int
    urb_function_name: str
    status: int
    status_name: str
    device_id: str = ""
    vid: str = ""
    pid: str = ""
    endpoint_address: int = 0
    endpoint_direction: str = ""  # IN, OUT
    transfer_buffer_length: int = 0
    actual_length: int = 0
    transfer_flags: int = 0
    transfer_buffer: bytes = field(default_factory=bytes)
    setup_packet: Dict[str, Any] = field(default_factory=dict)  # For control transfers
    interval: int = 0  # For interrupt/isochronous
    start_frame: int = 0  # For isochronous
    number_of_packets: int = 0  # For isochronous
    error_count: int = 0
    pipe_handle: int = 0
    usbd_status: str = ""
    timeout: int = 0
    request_type: int = 0  # bmRequestType for control transfers
    request: int = 0  # bRequest for control transfers
    value: int = 0  # wValue for control transfers
    index: int = 0  # wIndex for control transfers
    length: int = 0  # wLength for control transfers
    raw_data: Dict[str, Any] = field(default_factory=dict)
    event_id: int = 0
    process_id: int = 0
    thread_id: int = 0


class URBCapture:
    """Complete URB capture and parsing implementation."""
    
    def __init__(self):
        self.is_admin = _check_admin()
        self.is_windows = platform.system() == "Windows"
        self.trace_file: Optional[str] = None
        self.session_name: str = "USB-Forensics-URB-Trace"
        self.realtime_queue: queue.Queue = queue.Queue()
        self.realtime_thread: Optional[threading.Thread] = None
        self.realtime_running: bool = False
        self.realtime_callback: Optional[Callable[[URBTransfer], None]] = None
        self._realtime_lock = threading.Lock()
        self._realtime_stop_event = threading.Event()
        self._logman_available = shutil.which("logman") is not None
        self.session_active = False
        self.last_parse_stats: Dict[str, Any] = {}

    def _get_reports_dir(self) -> str:
        """Get reports directory from settings or fallback."""
        reports_dir = "reports"
        if SETTINGS_AVAILABLE:
            try:
                cfg = app_settings.load_settings()
                reports_dir = cfg.get("reports_directory", "reports")
            except Exception:
                pass
        return reports_dir

    def _debug_log(self, hypothesis_id: str, location: str, message: str, data: Dict[str, Any]):
        """Write NDJSON debug evidence for this session."""
        try:
            payload = {
                "sessionId": "c4e452",
                "runId": "pre-fix-parse",
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(time.time() * 1000),
            }
            with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as fp:
                fp.write(json.dumps(payload, ensure_ascii=True) + "\n")
        except Exception:
            pass

    def _session_exists(self) -> bool:
        """Check whether the ETW session currently exists."""
        if not self._logman_available:
            return False
        try:
            result = subprocess.run(
                ["logman", "query", "-ets"],
                capture_output=True,
                timeout=10,
                text=True
            )
            output = f"{result.stdout}\n{result.stderr}".lower()
            return self.session_name.lower() in output
        except Exception:
            return False

    def _cleanup_existing_session(self):
        """Stop/delete stale session to avoid creation conflicts."""
        if not self._session_exists():
            return
        try:
            subprocess.run(["logman", "stop", self.session_name, "-ets"], capture_output=True, timeout=10, text=True)
        except Exception:
            pass
        try:
            subprocess.run(["logman", "delete", self.session_name, "-ets"], capture_output=True, timeout=10, text=True)
        except Exception:
            pass
        
    def is_available(self) -> bool:
        """Check if URB capture is available."""
        if not self.is_windows:
            logger.warning("URB capture only available on Windows")
            return False
        if not self.is_admin:
            logger.warning("Administrator privileges required for URB capture")
            return False
        if not self._logman_available:
            logger.warning("logman utility not found in PATH - ETW capture unavailable")
            return False
        return True
    
    # ========== .etl FILE PARSING ==========
    
    def parse_etl_file(self, etl_file: str) -> List[URBTransfer]:
        """
        Parse .etl file and extract complete URB data.
        
        Uses etl-parser library for full event extraction.
        Falls back to alternative methods if library not available.
        
        Args:
            etl_file: Path to .etl trace file
            
        Returns:
            List of URBTransfer objects with complete URB data
        """
        if not os.path.exists(etl_file):
            logger.error(f"ETL file not found: {etl_file}")
            return []
        
        urbs = []
        stats = {
            "events_seen": 0,
            "usb_events_seen": 0,
            "urbs_extracted": 0,
            "skipped_missing_fields": 0,
            "extract_errors": 0,
            "provider_names_seen": set(),
        }
        
        # Try using etl-parser library (recommended)
        try:
            from etl.etl import IEtlFileObserver, build_from_stream
            from etl.event import Event
            # region agent log
            self._debug_log(
                "H1",
                "core/urb_capture.py:parse_etl_file",
                "etl parser imported",
                {
                    "observer_abstract_methods": sorted(list(getattr(IEtlFileObserver, "__abstractmethods__", set()))),
                    "etl_file": etl_file,
                },
            )
            # endregion
            
            logger.info(f"Parsing ETL file using etl-parser: {etl_file}")
            
            class URBParserObserver(IEtlFileObserver):
                def __init__(self, urb_list, parse_stats):
                    self.urb_list = urb_list
                    self.parse_stats = parse_stats
                    self.usb_providers = set(DEFAULT_USB_PROVIDERS)
                
                def on_event_record(self, event: Event):
                    """Process each event from ETL file."""
                    try:
                        self.parse_stats["events_seen"] += 1
                        event_data = self._extract_event_data(event)

                        # Some etl-parser versions expose provider names differently (or not at all).
                        # If provider name is unavailable, fall back to USB-field heuristics.
                        provider_name = self._extract_provider_name(event, event_data)
                        if provider_name:
                            self.parse_stats["provider_names_seen"].add(provider_name)

                        provider_match = provider_name and any(
                            provider.lower() in provider_name.lower() for provider in self.usb_providers
                        )
                        if not provider_match and not self._looks_like_usb_event(event_data):
                            return

                        self.parse_stats["usb_events_seen"] += 1
                        
                        # Extract URB information
                        urb = self._extract_urb_from_event(event, event_data)
                        if urb:
                            self.urb_list.append(urb)
                            self.parse_stats["urbs_extracted"] += 1
                    except Exception as e:
                        self.parse_stats["extract_errors"] += 1
                        logger.debug(f"Error processing event: {e}")

                def on_trace_record(self, event):
                    """Compatibility handler for etl-parser interface versions."""
                    return self.on_event_record(event)

                def on_win_trace(self, obj):
                    """Compatibility handler for etl-parser interface versions."""
                    # WinTrace payloads do not always map directly to Event.
                    event = getattr(obj, "event", None) or getattr(obj, "record", None)
                    if event is not None:
                        return self.on_event_record(event)
                    return self.on_event_record(obj)

                def on_system_trace(self, obj):
                    """Required interface method; system traces are ignored for URB parsing."""
                    return None

                def on_perfinfo_trace(self, obj):
                    """Required interface method; perf traces are ignored for URB parsing."""
                    return None

                def _extract_event_data(self, event_obj: Any) -> Dict[str, Any]:
                    """Extract event payload from heterogeneous etl-parser record types."""
                    if event_obj is None:
                        return {}

                    data_candidates = []

                    if hasattr(event_obj, 'parse_etw'):
                        try:
                            parsed = event_obj.parse_etw()
                            if isinstance(parsed, dict):
                                data_candidates.append(parsed)
                        except Exception:
                            pass

                    for attr in ('event_data', 'data', 'payload', 'fields'):
                        value = getattr(event_obj, attr, None)
                        if isinstance(value, dict):
                            data_candidates.append(value)

                    for method_name in ('to_dict', 'as_dict'):
                        method = getattr(event_obj, method_name, None)
                        if callable(method):
                            try:
                                converted = method()
                                if isinstance(converted, dict):
                                    data_candidates.append(converted)
                            except Exception:
                                pass

                    merged: Dict[str, Any] = {}
                    for item in data_candidates:
                        merged.update(item)
                    return merged

                def _extract_provider_name(self, event_obj: Any, event_data: Dict[str, Any]) -> str:
                    """Best-effort provider-name extraction across etl-parser object shapes."""
                    for attr in ('provider_name', 'ProviderName', 'provider'):
                        value = getattr(event_obj, attr, None)
                        if value:
                            return str(value)

                    header = getattr(event_obj, 'header', None)
                    if header is not None:
                        for attr in ('provider_name', 'ProviderName', 'provider'):
                            value = getattr(header, attr, None)
                            if value:
                                return str(value)

                    for key in ('ProviderName', 'provider_name', 'provider', 'Provider'):
                        value = event_data.get(key)
                        if value:
                            return str(value)

                    return ""

                def _looks_like_usb_event(self, event_data: Dict[str, Any]) -> bool:
                    """Heuristic USB-event detector when provider metadata is unavailable."""
                    if not isinstance(event_data, dict) or not event_data:
                        return False

                    keys = {str(k).lower() for k in event_data.keys()}
                    usb_key_hits = {
                        'urbfunction', 'function', 'urb', 'endpointaddress', 'transferbufferlength',
                        'actuallength', 'usbdstatus', 'deviceid', 'pnpdeviceid', 'pipehandle'
                    }
                    if keys.intersection(usb_key_hits):
                        return True

                    # Also check values for common USB signatures.
                    joined = " ".join(str(v) for v in event_data.values() if v is not None).lower()
                    return ('vid_' in joined and 'pid_' in joined) or ('usb' in joined and 'endpoint' in joined)

                def _coerce_event_timestamp(self, event_obj: Any, event_data: Dict[str, Any]) -> str:
                    """Normalize timestamp from event object or payload into ISO-8601 UTC."""
                    raw_ts = getattr(event_obj, 'timestamp', None)
                    if raw_ts is None:
                        raw_ts = _first_present(event_data, ['Timestamp', 'TimeStamp', 'SystemTime', 'time'], None)

                    if isinstance(raw_ts, datetime):
                        dt = raw_ts
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        return dt.astimezone(timezone.utc).isoformat()

                    if isinstance(raw_ts, (int, float)):
                        # ETW timestamps can appear as either Unix seconds or FILETIME ticks.
                        value = float(raw_ts)
                        if value > 1e12:
                            filetime_epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)
                            dt = filetime_epoch + timedelta(microseconds=value / 10.0)
                        else:
                            dt = datetime.fromtimestamp(value, tz=timezone.utc)
                        return dt.isoformat()

                    if isinstance(raw_ts, str) and raw_ts.strip():
                        text = raw_ts.strip().replace('Z', '+00:00')
                        try:
                            dt = datetime.fromisoformat(text)
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            return dt.astimezone(timezone.utc).isoformat()
                        except Exception:
                            pass

                    return datetime.now(timezone.utc).isoformat()

                def _coerce_event_id(self, event_obj: Any, event_data: Dict[str, Any]) -> int:
                    return _coerce_int(
                        getattr(event_obj, 'event_id', None)
                        or _first_present(event_data, ['EventID', 'EventId', 'Id'], 0)
                    )

                def _coerce_process_id(self, event_obj: Any, event_data: Dict[str, Any]) -> int:
                    return _coerce_int(
                        getattr(event_obj, 'process_id', None)
                        or _first_present(event_data, ['ProcessID', 'ProcessId'], 0)
                    )

                def _coerce_thread_id(self, event_obj: Any, event_data: Dict[str, Any]) -> int:
                    return _coerce_int(
                        getattr(event_obj, 'thread_id', None)
                        or _first_present(event_data, ['ThreadID', 'ThreadId'], 0)
                    )
                
                def _extract_urb_from_event(self, event: Event, event_data: Dict) -> Optional[URBTransfer]:
                    """Extract URB data from ETW event."""
                    try:
                        event_data = event_data if isinstance(event_data, dict) else {}

                        # Get event properties
                        timestamp = self._coerce_event_timestamp(event, event_data)
                        event_id = self._coerce_event_id(event, event_data)
                        process_id = self._coerce_process_id(event, event_data)
                        thread_id = self._coerce_thread_id(event, event_data)
                        
                        # Extract USB-specific fields from event data (provider/version dependent).
                        urb_function = _coerce_int(_first_present(event_data, ['Function', 'URBFunction', 'UrbFunction', 'FunctionType'], 0))
                        status = _coerce_int(_first_present(event_data, ['Status', 'USBDStatus', 'NtStatus'], 0))
                        device_id = str(_first_present(event_data, ['DeviceId', 'DeviceID', 'DevicePath', 'PnpDeviceId'], ''))
                        endpoint = _coerce_int(_first_present(event_data, ['EndpointAddress', 'Endpoint', 'PipeEndpoint'], 0))
                        transfer_length = _coerce_int(_first_present(event_data, ['TransferBufferLength', 'TransferLength', 'Length', 'DataLength', 'BufferLength'], 0))
                        actual_length = _coerce_int(_first_present(event_data, ['ActualLength', 'ActualTransferLength', 'Actual'], 0))

                        has_setup_fields = any(k in event_data for k in ('bmRequestType', 'bRequest', 'wValue', 'wIndex', 'wLength'))
                        if urb_function == 0 and transfer_length == 0 and actual_length == 0 and endpoint == 0 and not has_setup_fields:
                            self.parse_stats["skipped_missing_fields"] += 1
                            return None
                        
                        # Extract VID/PID from device_id
                        vid, pid = self._extract_vid_pid(device_id)
                        
                        # Determine endpoint direction
                        endpoint_dir = "IN" if (endpoint & 0x80) else "OUT"
                        
                        # Extract transfer buffer data if available
                        transfer_buffer = _coerce_bytes(_first_present(event_data, ['TransferBuffer', 'Data', 'Payload'], b''))
                        
                        # Extract setup packet for control transfers
                        setup_packet = {}
                        if urb_function == URBFunction.URB_FUNCTION_CONTROL_TRANSFER:
                            setup_packet = {
                                'bmRequestType': _coerce_int(_first_present(event_data, ['bmRequestType', 'RequestType'], 0)),
                                'bRequest': _coerce_int(_first_present(event_data, ['bRequest', 'Request'], 0)),
                                'wValue': _coerce_int(_first_present(event_data, ['wValue', 'Value'], 0)),
                                'wIndex': _coerce_int(_first_present(event_data, ['wIndex', 'Index'], 0)),
                                'wLength': _coerce_int(_first_present(event_data, ['wLength', 'Length'], 0))
                            }
                        
                        # Create URB transfer object
                        urb = URBTransfer(
                            timestamp=timestamp,
                            urb_function=urb_function,
                            urb_function_name=self._get_urb_function_name(urb_function),
                            status=status,
                            status_name=self._get_status_name(status),
                            device_id=device_id,
                            vid=vid,
                            pid=pid,
                            endpoint_address=endpoint,
                            endpoint_direction=endpoint_dir,
                            transfer_buffer_length=transfer_length,
                            actual_length=actual_length,
                            transfer_buffer=transfer_buffer[:1024],  # Limit to 1KB for storage
                            setup_packet=setup_packet,
                            interval=_coerce_int(event_data.get('Interval', 0)),
                            start_frame=_coerce_int(event_data.get('StartFrame', 0)),
                            number_of_packets=_coerce_int(event_data.get('NumberOfPackets', 0)),
                            error_count=_coerce_int(event_data.get('ErrorCount', 0)),
                            pipe_handle=_coerce_int(event_data.get('PipeHandle', 0)),
                            timeout=_coerce_int(event_data.get('Timeout', 0)),
                            request_type=setup_packet.get('bmRequestType', 0),
                            request=setup_packet.get('bRequest', 0),
                            value=setup_packet.get('wValue', 0),
                            index=setup_packet.get('wIndex', 0),
                            length=setup_packet.get('wLength', 0),
                            raw_data=event_data,
                            event_id=event_id,
                            process_id=process_id,
                            thread_id=thread_id
                        )
                        
                        return urb
                    except Exception as e:
                        self.parse_stats["extract_errors"] += 1
                        logger.debug(f"Error extracting URB: {e}")
                        return None
                
                def _extract_vid_pid(self, device_id: str) -> tuple:
                    """Extract VID and PID from device ID string."""
                    vid, pid = "", ""
                    if 'VID_' in device_id:
                        try:
                            vid_start = device_id.index('VID_') + 4
                            vid = device_id[vid_start:vid_start+4]
                        except:
                            pass
                    if 'PID_' in device_id:
                        try:
                            pid_start = device_id.index('PID_') + 4
                            pid = device_id[pid_start:pid_start+4]
                        except:
                            pass
                    return vid, pid
                
                def _get_urb_function_name(self, func_code: int) -> str:
                    """Get human-readable URB function name."""
                    try:
                        return URBFunction(func_code).name
                    except:
                        return f"UNKNOWN_0x{func_code:04X}"
                
                def _get_status_name(self, status: int) -> str:
                    """Get human-readable status name."""
                    try:
                        return URBStatus(status & 0xFFFFFFFF).name
                    except:
                        return f"STATUS_0x{status:08X}"
            
            # region agent log
            self._debug_log(
                "H2",
                "core/urb_capture.py:parse_etl_file",
                "observer class methods",
                {
                    "implemented_methods": sorted(
                        [name for name in dir(URBParserObserver) if callable(getattr(URBParserObserver, name)) and not name.startswith("__")]
                    ),
                    "remaining_abstract_methods": sorted(list(getattr(URBParserObserver, "__abstractmethods__", set()))),
                },
            )
            # endregion
            
            # Parse the ETL file
            with open(etl_file, "rb") as f:
                etl_data = f.read()
                etl_reader = build_from_stream(etl_data)
                # region agent log
                self._debug_log(
                    "H3",
                    "core/urb_capture.py:parse_etl_file",
                    "before observer instantiate",
                    {"etl_bytes": len(etl_data)},
                )
                # endregion
                observer = URBParserObserver(urbs, stats)
                etl_reader.parse(observer)
            
            stats["provider_names_seen"] = sorted(stats["provider_names_seen"])
            self.last_parse_stats = stats
            logger.info(f"Parsed {len(urbs)} URBs from ETL file")
            logger.info(f"Parse stats: {self.last_parse_stats}")

            # If parser callbacks ran but no USB payload was decoded, attempt XML fallback.
            if len(urbs) == 0 and stats.get("events_seen", 0) > 0:
                logger.warning(
                    "etl-parser observed %s events but decoded no URBs; falling back to tracerpt XML parsing",
                    stats.get("events_seen", 0),
                )
                fallback_urbs = self._parse_etl_alternative(etl_file)
                if fallback_urbs:
                    self.last_parse_stats.update(
                        {
                            "primary_mode": "etl-parser",
                            "fallback_mode": "tracerpt_xml",
                            "primary_events_seen": stats.get("events_seen", 0),
                            "primary_usb_events_seen": stats.get("usb_events_seen", 0),
                        }
                    )
                    return fallback_urbs

            return urbs
            
        except ImportError:
            logger.warning("etl-parser not installed. Install with: pip install etl-parser")
            logger.info("Falling back to alternative parsing method...")
            return self._parse_etl_alternative(etl_file)
        except Exception as e:
            # region agent log
            self._debug_log(
                "H4",
                "core/urb_capture.py:parse_etl_file",
                "etl parser exception",
                {"exc_type": type(e).__name__, "error": str(e)},
            )
            # endregion
            logger.error(f"Error parsing ETL file: {e}", exc_info=True)
            stats["provider_names_seen"] = sorted(stats["provider_names_seen"])
            self.last_parse_stats = stats
            return []
    
    def _parse_etl_alternative(self, etl_file: str) -> List[URBTransfer]:
        """Alternative ETL parsing using Windows SDK tools (tracerpt).
        
        Note: This is a limited fallback. For full URB parsing, install etl-parser:
            pip install etl-parser
        """
        logger.info("Using alternative parsing method (tracerpt)")
        logger.warning("Alternative parsing has limited functionality and is being used as a compatibility fallback.")
        
        xml_file = etl_file.replace('.etl', '_temp.xml')
        urbs = []
        
        try:
            result = subprocess.run(
                ["tracerpt", etl_file, "-o", xml_file, "-of", "XML", "-lr"],
                capture_output=True,
                timeout=120,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"tracerpt failed: {result.stderr}")
                return []
            
            if not os.path.exists(xml_file):
                logger.error(f"tracerpt did not create output file: {xml_file}")
                return []
            
            tree = ET.parse(xml_file)
            root = tree.getroot()

            def _local_name(tag: str) -> str:
                if not isinstance(tag, str):
                    return ""
                return tag.split("}", 1)[-1]

            def _find_child(node: ET.Element, local: str) -> Optional[ET.Element]:
                for child in list(node):
                    if _local_name(child.tag) == local:
                        return child
                return None

            events = [node for node in root.iter() if _local_name(node.tag) == "Event"]
            parsed_events = 0
            for event in events:
                system_node = _find_child(event, "System")
                if system_node is None:
                    continue
                provider_name = ""
                provider_node = _find_child(system_node, "Provider")
                if provider_node is not None:
                    provider_name = provider_node.attrib.get("Name", "") or provider_node.attrib.get("Guid", "")
                if "USB" not in provider_name.upper():
                    continue
                event_data = {}
                for data_node in event.iter():
                    if _local_name(data_node.tag) != "Data":
                        continue
                    field_name = data_node.attrib.get("Name", "")
                    if not field_name:
                        continue
                    field_val = (data_node.text or "").strip()
                    event_data[field_name] = field_val
                timestamp = datetime.now(timezone.utc).isoformat()
                time_created = _find_child(system_node, "TimeCreated")
                if time_created is not None:
                    timestamp = time_created.attrib.get("SystemTime", timestamp)

                urb_function = _coerce_int(
                    _first_present(event_data, ["Function", "URBFunction", "UrbFunction", "fid_TransferType"], 0)
                )
                status = _coerce_int(
                    _first_present(event_data, ["Status", "USBDStatus", "fid_LastConfigureEndpointStatus", "fid_Status"], 0)
                )
                device_id = str(
                    _first_present(event_data, ["DeviceId", "DeviceID", "DevicePath", "PnpDeviceId", "fid_UsbDevice"], "")
                )
                endpoint = _coerce_int(
                    _first_present(event_data, ["EndpointAddress", "Endpoint", "fid_bEndpointAddress", "fid_Endpoint"], 0)
                )
                transfer_length = _coerce_int(
                    _first_present(event_data, ["TransferBufferLength", "TransferLength", "Length", "DataLength", "fid_TransferBufferLength", "fid_TransferLength", "fid_DataLength"], 0)
                )
                actual_length = _coerce_int(
                    _first_present(event_data, ["ActualLength", "Actual", "ActualTransferLength", "fid_ActualLength"], 0)
                )

                if urb_function == 0 and transfer_length == 0 and actual_length == 0 and endpoint == 0 and not device_id:
                    continue

                vid, pid = self._extract_vid_pid(device_id)
                execution_node = _find_child(system_node, "Execution")
                process_id = _coerce_int(execution_node.attrib.get("ProcessID", 0)) if execution_node is not None else 0
                thread_id = _coerce_int(execution_node.attrib.get("ThreadID", 0)) if execution_node is not None else 0

                event_id_text = "0"
                event_id_node = _find_child(system_node, "EventID")
                if event_id_node is not None and event_id_node.text:
                    event_id_text = event_id_node.text

                urbs.append(
                    URBTransfer(
                        timestamp=timestamp,
                        urb_function=urb_function,
                        urb_function_name=self._get_urb_function_name(urb_function),
                        status=status,
                        status_name=self._get_status_name(status),
                        device_id=device_id,
                        vid=vid,
                        pid=pid,
                        endpoint_address=endpoint,
                        endpoint_direction="IN" if (endpoint & 0x80) else "OUT",
                        transfer_buffer_length=transfer_length,
                        actual_length=actual_length,
                        event_id=_coerce_int(event_id_text),
                        process_id=process_id,
                        thread_id=thread_id,
                        raw_data=event_data,
                    )
                )
                parsed_events += 1
            self.last_parse_stats = {
                "events_seen": len(events),
                "usb_events_seen": parsed_events,
                "urbs_extracted": len(urbs),
                "mode": "fallback_tracerpt_xml",
            }
            logger.info(f"Fallback parser extracted {len(urbs)} URBs from {len(events)} events")
            
            return urbs
            
        except FileNotFoundError:
            logger.error("tracerpt not found. Please install Windows SDK tools or use etl-parser library.")
            return []
        except Exception as e:
            logger.error(f"Alternative parsing failed: {e}")
            return []
        finally:
            try:
                if os.path.exists(xml_file):
                    os.remove(xml_file)
            except Exception:
                pass
    
    # ========== CREATE .etl FILES ==========
    
    def start_etw_capture(self, duration_seconds: int = 60, 
                         output_file: str = None) -> Optional[str]:
        """
        Start ETW trace session to capture USB URBs to .etl file.
        
        Args:
            duration_seconds: How long to capture (0 = manual stop)
            output_file: Output .etl file path (optional)
            
        Returns:
            Path to trace file if successful, None otherwise
        """
        if not self.is_available():
            return None
            
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            reports_dir = self._get_reports_dir()
            output_file = os.path.join(reports_dir, f"usb_trace_{timestamp}.etl")
        
        # Ensure reports directory exists
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create reports directory: {e}")
            return None
        
        self.trace_file = output_file
        
        try:
            self._cleanup_existing_session()
            
            # Start ETW trace session for USB - register ALL providers
            providers = DEFAULT_USB_PROVIDERS
            primary_provider = providers[0]
            cmd = [
                "logman", "create", "trace", self.session_name,
                "-o", output_file,
                "-ets",
                "-p", primary_provider,
            ]
            
            logger.debug(f"Running logman: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, timeout=10, text=True)
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else (result.stdout.strip() if result.stdout else "Unknown error")
                logger.error(f"logman failed ({result.returncode}): {error_msg}")
                self._cleanup_existing_session()
                return None

            # Add additional providers with update trace (Windows logman can reject multiple -p in create).
            for provider in providers[1:]:
                update_cmd = ["logman", "update", "trace", self.session_name, "-p", provider, "-ets"]
                update_result = subprocess.run(update_cmd, capture_output=True, timeout=10, text=True)
                if update_result.returncode != 0:
                    logger.warning(
                        "Could not add provider '%s' to ETW session: %s",
                        provider,
                        update_result.stderr.strip() or update_result.stdout.strip() or "Unknown error",
                    )
            
            logger.info(f"ETW trace started. Output: {output_file}")
            logger.info(f"Capturing USB providers: {', '.join(providers)}")
            self.session_active = self._session_exists()
            if not self.session_active:
                logger.error("ETW trace command succeeded but session is not active")
                return None
            if duration_seconds > 0:
                logger.info(f"Capturing for {duration_seconds} seconds...")
                # Schedule stop after duration
                threading.Timer(duration_seconds, self.stop_etw_capture).start()
            
            return output_file
            
        except subprocess.TimeoutExpired:
            logger.error("logman command timed out")
            return None
        except FileNotFoundError:
            logger.error("logman utility not found in PATH")
            return None
        except Exception as e:
            logger.error(f"Error starting ETW capture: {e}")
            return None
    
    def stop_etw_capture(self) -> bool:
        """Stop active ETW trace session."""
        if not self.session_active and not self._session_exists():
            logger.info("No active ETW trace session to stop")
            return False
        try:
            result = subprocess.run(
                ["logman", "stop", self.session_name, "-ets"],
                capture_output=True,
                timeout=10,
                text=True
            )
            if result.returncode == 0:
                logger.info(f"ETW trace session '{self.session_name}' stopped")
                self.session_active = False
                return True
            else:
                logger.warning(f"Failed to stop session (may not exist): {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error stopping ETW capture: {e}")
            return False
    
    # ========== REAL-TIME EVENT PROCESSING ==========
    
    def start_realtime_capture(self, callback: Callable[[URBTransfer], None],
                              providers: Optional[List[str]] = None) -> bool:
        """
        Start real-time URB capture via ETW.
        
        Args:
            callback: Function to call for each captured URB
            providers: List of ETW provider names (optional)
            
        Returns:
            True if started successfully
        """
        if not self.is_available():
            return False
        
        with self._realtime_lock:
            if self.realtime_running:
                logger.warning("Real-time capture already running")
                return False
            
            self.realtime_callback = callback
            self.realtime_running = True
            self._realtime_stop_event.clear()
        
        # Default USB providers
        if not providers:
            providers = [
                "Microsoft-Windows-USB-USBPORT",
                "Microsoft-Windows-USB-USBXHCI",
                "Microsoft-Windows-USB-UCX"
            ]
        
        # Start real-time processing thread
        self.realtime_thread = threading.Thread(
            target=self._realtime_worker,
            args=(providers,),
            daemon=True
        )
        self.realtime_thread.start()
        
        logger.info("Real-time URB capture started")
        return True
    
    def stop_realtime_capture(self) -> bool:
        """Stop real-time URB capture."""
        with self._realtime_lock:
            if not self.realtime_running:
                return False
            
            self.realtime_running = False
            self._realtime_stop_event.set()
        
        if self.realtime_thread:
            self.realtime_thread.join(timeout=5.0)
        
        logger.info("Real-time URB capture stopped")
        return True
    
    def _realtime_worker(self, providers: List[str]):
        """Worker thread for real-time ETW event processing."""
        try:
            reports_dir = self._get_reports_dir()
            temp_trace = os.path.join(reports_dir, f"realtime_urb_{int(time.time())}.etl")
            os.makedirs(os.path.dirname(temp_trace), exist_ok=True)
            
            try:
                # Start ETW session to file
                if not self._start_etw_session(temp_trace, providers):
                    logger.error("Real-time ETW session failed to start")
                    return
                
                last_size = 0
                last_parse_time = time.time()
                processed_urb_ids = set()  # Track processed URBs to avoid duplicates
                
                while self.realtime_running and not self._realtime_stop_event.is_set():
                    time.sleep(2)  # Poll every 2 seconds
                    
                    if os.path.exists(temp_trace):
                        current_size = os.path.getsize(temp_trace)
                        if current_size > last_size:
                            # New data available, parse incrementally
                            current_time = time.time()
                            if current_time - last_parse_time > 5:  # Parse every 5 seconds
                                urbs = self.parse_etl_file(temp_trace)
                                # Filter to new URBs - use timestamp + device + endpoint as unique key
                                for urb in urbs:
                                    # Create unique identifier from URB properties
                                    urb_id = f"{urb.timestamp}|{urb.device_id}|{urb.endpoint_address}|{urb.transfer_buffer_length}"
                                    if urb_id not in processed_urb_ids:
                                        processed_urb_ids.add(urb_id)
                                        if self.realtime_callback:
                                            self.realtime_callback(urb)
                                last_parse_time = current_time
                                last_size = current_size
                
            finally:
                self._stop_etw_session()
                try:
                    if os.path.exists(temp_trace):
                        os.remove(temp_trace)
                except:
                    pass
                
        except Exception as e:
            logger.error(f"Real-time worker error: {e}", exc_info=True)
            with self._realtime_lock:
                self.realtime_running = False
    
    def _start_etw_session(self, output_file: str, providers: List[str]) -> bool:
        """Start ETW trace session with USB providers."""
        try:
            self._cleanup_existing_session()

            cmd = [
                "logman", "create", "trace", self.session_name,
                "-o", output_file,
                "-ets"
            ]
            active_providers = providers or DEFAULT_USB_PROVIDERS
            cmd.extend(["-p", active_providers[0]])
            
            result = subprocess.run(cmd, capture_output=True, timeout=10, text=True)
            if result.returncode == 0:
                logger.info("ETW session started successfully")
            else:
                logger.error(f"ETW session failed: {result.stderr.strip() if result.stderr else 'Unknown'}")
                return False

            for provider in active_providers[1:]:
                update_cmd = ["logman", "update", "trace", self.session_name, "-p", provider, "-ets"]
                update_result = subprocess.run(update_cmd, capture_output=True, timeout=10, text=True)
                if update_result.returncode != 0:
                    logger.warning(
                        "Could not add provider '%s' to real-time ETW session: %s",
                        provider,
                        update_result.stderr.strip() or update_result.stdout.strip() or "Unknown error",
                    )
            self.session_active = result.returncode == 0 and self._session_exists()
            return self.session_active
            
        except Exception as e:
            logger.error(f"Failed to start ETW session: {e}")
            return False
    
    def _stop_etw_session(self) -> bool:
        """Stop ETW trace session."""
        try:
            if not self.session_active and not self._session_exists():
                return False
            result = subprocess.run(
                ["logman", "stop", self.session_name, "-ets"],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                self.session_active = False
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to stop ETW session: {e}")
            return False
    
    def _get_urb_function_name(self, func_code: int) -> str:
        """Get human-readable URB function name."""
        try:
            return URBFunction(func_code).name
        except:
            return f"UNKNOWN_0x{func_code:04X}"

    def _extract_vid_pid(self, device_id: str) -> tuple[str, str]:
        """Extract VID/PID from PnP-like identifiers when present."""
        vid, pid = "", ""
        if not device_id:
            return vid, pid

        text = str(device_id)
        if "VID_" in text:
            try:
                vid_start = text.index("VID_") + 4
                vid = text[vid_start:vid_start + 4]
            except Exception:
                pass
        if "PID_" in text:
            try:
                pid_start = text.index("PID_") + 4
                pid = text[pid_start:pid_start + 4]
            except Exception:
                pass
        return vid, pid
    
    def _get_status_name(self, status: int) -> str:
        """Get human-readable status name."""
        try:
            return URBStatus(status & 0xFFFFFFFF).name
        except:
            return f"STATUS_0x{status:08X}"


# ========== CONVENIENCE FUNCTIONS ==========

def parse_etl_file(etl_file: str) -> List[URBTransfer]:
    """Parse .etl file and return list of URBs."""
    capture = URBCapture()
    return capture.parse_etl_file(etl_file)


def start_realtime_urb_capture(callback: Callable[[URBTransfer], None]) -> Optional[URBCapture]:
    """Start real-time URB capture with callback."""
    capture = URBCapture()
    if capture.start_realtime_capture(callback):
        return capture
    return None


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example: Parse ETL file
    if len(sys.argv) > 1:
        etl_file = sys.argv[1]
        print(f"Parsing ETL file: {etl_file}")
        urbs = parse_etl_file(etl_file)
        print(f"Found {len(urbs)} URBs")
        for urb in urbs[:10]:  # Print first 10
            print(f"\nURB: {urb.urb_function_name}")
            print(f"  Device: {urb.vid}:{urb.pid}")
            print(f"  Endpoint: {urb.endpoint_address} ({urb.endpoint_direction})")
            print(f"  Length: {urb.transfer_buffer_length} bytes")
            print(f"  Status: {urb.status_name}")
    else:
        print("Usage: urb_capture.py <etl_file>")
        print("\nFor real-time capture, use the URBCapture class programmatically.")